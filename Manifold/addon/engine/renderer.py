import bpy
from mathutils import Matrix

from .mesh import Mesh
from .shaders.meshtriangle.shader import MeshTriangleShader

import numpy as np



class ManifoldRenderEngine(bpy.types.RenderEngine):
    bl_idname = "MANIFOLD"
    bl_label = "Manifold"

    # Request a GPU context to be created and activated for the render method.
    # This may be used either to perform the rendering itself, or to allocate
    # and fill a texture for more efficient drawing.
    bl_use_gpu_context = True


    def __init__(self):

        self.meshes = dict()
        self.lights = dict()

        self.meshtriangle_shader = MeshTriangleShader()

    def __del__(self):
        pass


    def view_update(self, context, depsgraph):
        scene = depsgraph.scene

        updated_meshes = dict()
        updated_lights = dict()
        meshes_to_rebuild = []

        # Check for any updated mesh geometry to rebuild GPU buffers
        for update in depsgraph.updates:
            name = update.id.name
            if type(update.id) == bpy.types.Object:
                if update.is_updated_geometry and name in self.meshes:
                    meshes_to_rebuild.append(name)

        # Aggregate everything visible in the scene that we care about
        for obj in scene.objects:
            if not obj.visible_get():
                continue

            if obj.type in ('MESH', 'CURVE'):
                if obj.display_type in ('SOLID', 'TEXTURED'):
                    self.update_mesh(obj, depsgraph, updated_meshes, meshes_to_rebuild)        
            elif obj.type == 'LIGHT':
                self.update_light(obj, updated_lights)

        self.meshes = updated_meshes
        self.lights = updated_lights


    def update_mesh(self, obj, depsgraph, updated_meshes, meshes_to_rebuild):
        evaluated_obj = obj.evaluated_get(depsgraph)

        mesh = evaluated_obj.to_mesh()
        if len(mesh.loops) == 0:
            return

        rebuild_geometry = obj.name in meshes_to_rebuild
        if obj.name not in self.meshes:
            mesh = Mesh(obj.name)
            rebuild_geometry = True
        else:
            mesh = self.meshes[obj.name]

        mesh.update(obj)

        if rebuild_geometry:
            mesh.rebuild(evaluated_obj)

        updated_meshes[obj.name] = mesh


    def update_light(self, obj, updated_lights):    
        updated_lights[obj.name] = obj


    def render(self, depsgraph):
        # This is F12 render

        def get_camera_matrices(camera, depsgraph, resolution_x, resolution_y):
            view_matrix = camera.matrix_world.inverted()
            window_matrix = camera.calc_matrix_camera(
                depsgraph,
                x = resolution_x,
                y = resolution_y,
                scale_x = 1,
                scale_y = 1,
            )     
            return view_matrix, window_matrix      

        ctx = bpy.context
        scene = depsgraph.scene
        
        scale = scene.render.resolution_percentage / 100.0
        self.size_x = int(scene.render.resolution_x * scale)
        self.size_y = int(scene.render.resolution_y * scale)

        camera = scene.camera
        view_matrix, window_matrix = get_camera_matrices(camera, depsgraph, self.size_x, self.size_y)

        # Lazily import GPU module, since GPU context is only created on demand
        # for rendering and does not exist on register.
        import gpu

        depsgraph.update()
        self.view_update(ctx, depsgraph)

        # Perform rendering task.
        offscreen = gpu.types.GPUOffScreen(self.size_x, self.size_y)

        with offscreen.bind():
            fb = gpu.state.active_framebuffer_get()
            self.draw_background(fb, scene)
            with gpu.matrix.push_pop():
                # reset matrices -> use normalized device coordinates [-1, 1]
                gpu.matrix.load_matrix(Matrix.Identity(4))
                gpu.matrix.load_projection_matrix(Matrix.Identity(4))

                self.draw_meshes(scene, view_matrix, window_matrix, camera.location, is_viewport=False)

            buffer = fb.read_color(0,0, self.size_x, self.size_y, 4, 0, 'FLOAT')

        offscreen.free()

        buffer_list = []
        for line in buffer:
            line_list = line.to_list()
            buffer_list += line_list

        buffer_list = np.reshape(buffer_list, (1, -1))[0]

        result = self.begin_result(0, 0, self.size_x, self.size_y)
        layer = result.layers[0].passes["Combined"]
        layer.rect.foreach_set(np.array(buffer_list, np.float32))
        self.end_result(result)

        # when rendering to a separate image texture you have to do this. but NOT when rendering directly into a render layer
        # IMAGE_NAME = "Manifold_Image_Output"
        # if IMAGE_NAME not in bpy.data.images:
        #     bpy.data.images.new(IMAGE_NAME, self.size_x, self.size_y)
        # image = bpy.data.images[IMAGE_NAME]
        # image.scale(self.size_x, self.size_y)
        
        # GAMMA = 1.0 / 2.4
        # linearrgb_to_srgb = lambda c: (c * 12.92 if c > 0.0 else 0.0) if c < 0.0031306684425 else 1.055 * c**GAMMA - 0.055
        # image.pixels = [linearrgb_to_srgb(v) for v in buffer_list]



    def view_draw(self, context, depsgraph):
        # Lazily import GPU module, so that the render engine works in
        # background mode where the GPU module can't be imported by default.
        import gpu

        scene = depsgraph.scene
        region = context.region
        region3d = context.region_data

        view_matrix = region3d.view_matrix
        window_matrix = region3d.window_matrix
        camera_location = region3d.view_matrix.inverted().translation

        fb = gpu.state.active_framebuffer_get()
        self.draw_background(fb, scene)
        self.draw_meshes(scene, view_matrix, window_matrix, camera_location, is_viewport=True)


    def get_background_color(self, scene):
        world = scene.world

        if world:
            return world.color
        else:
            return (0.0, 0.0, 0.0, 0.0)

    def draw_background(self, fb, scene):
        background_color = self.get_background_color(scene)
        fb.clear(color=background_color, depth=1.0)


    def draw_meshes(self, scene, view_matrix, window_matrix, camera_location, is_viewport=False):
        import gpu

        gpu.state.depth_test_set('LESS_EQUAL')
        gpu.state.depth_mask_set(True)

        if is_viewport:
            self.bind_display_space_shader(scene)

        shader = self.meshtriangle_shader
        shader.bind()

        lights_data = []

        for light in self.lights.values():
            lights_data += light.location[:]
            lights_data.append(light.data.energy/10)
            lights_data += light.data.color[:]
            lights_data += [0.0]

        lights_data += [0.0]*8*(100-len(self.lights))

        lights_uniform_data = gpu.types.Buffer('FLOAT', 8*100, lights_data)
        lights_uniform_buf = gpu.types.GPUUniformBuf(lights_uniform_data)

        shader.set_uniform_buffer("LightBlock", lights_uniform_buf)

        shader.set_vec3('viewPos', camera_location)

        background_color = self.get_background_color(scene)
        shader.set_vec3('ambientColor', background_color[:3])

        for mesh in self.meshes.values():

            modelviewprojection_matrix = window_matrix @ view_matrix @ mesh.matrix_world
            shader.set_mat4('ModelViewProjectionMatrix', modelviewprojection_matrix.transposed())

            mesh.rebuild_batch_buffers(shader)

            shader.set_mat4('ModelMatrix', mesh.matrix_world.transposed())
            shader.set_vec3('surfaceColor', mesh.material.diffuse_color[:3])
            shader.set_float('surfaceRoughness', mesh.material.roughness)

            mesh.draw(shader)
        
        gpu.state.depth_mask_set(False)
        shader.unbind()

        if is_viewport:
            self.unbind_display_space_shader()
