import bpy

from .mesh import Mesh
from .shaders.meshtriangle.shader import MeshTriangleShader

import numpy as np

from gpu_extras.presets import draw_circle_2d
import random
from mathutils import Matrix, Vector

class ManifoldRenderEngine(bpy.types.RenderEngine):
    bl_idname = "MANIFOLD"
    bl_label = "Manifold"

    # Request a GPU context to be created and activated for the render method.
    # This may be used either to perform the rendering itself, or to allocate
    # and fill a texture for more efficient drawing.
    bl_use_gpu_context = True


    def __init__(self):
        self.mesh = Mesh("test")
        self.meshtriangle_shader = MeshTriangleShader()
        self.light = None

    def __del__(self):
        pass


    def view_update(self, context, depsgraph):
        scene = depsgraph.scene

        for obj in scene.objects:
            if not obj.visible_get():
                continue

            if obj.type in ('MESH', 'CURVE'):
                if obj.display_type in ('SOLID', 'TEXTURED'):
                    self.update_mesh(obj, depsgraph)        
            elif obj.type == 'LIGHT':
                self.update_light(obj)


    def update_mesh(self, obj, depsgraph):
        evaluated_obj = obj.evaluated_get(depsgraph)

        self.mesh.update(obj)
        self.mesh.rebuild(evaluated_obj)

    def update_light(self, obj):
        self.light = obj


    def render(self, depsgraph):

        def get_camera_matrices(camera, depsgraph, resolution_x, resolution_y):
            modelview_matrix = camera.matrix_world.inverted()
            window_matrix = camera.calc_matrix_camera(
                depsgraph,
                x = resolution_x,
                y = resolution_y,
                scale_x = 1,
                scale_y = 1,
            )     

            return modelview_matrix, window_matrix      

        ctx = bpy.context
        scene = depsgraph.scene
        
        scale = scene.render.resolution_percentage / 100.0
        self.size_x = int(scene.render.resolution_x * scale)
        self.size_y = int(scene.render.resolution_y * scale)

        # Lazily import GPU module, since GPU context is only created on demand
        # for rendering and does not exist on register.
        import gpu

        IMAGE_NAME = "Manifold_Render_Output"

        depsgraph.update()
        self.view_update(ctx, depsgraph)

        # Perform rendering task.
        offscreen = gpu.types.GPUOffScreen(self.size_x, self.size_y)

        with offscreen.bind():
            fb = gpu.state.active_framebuffer_get()
            fb.clear(color=(0.0, 0.0, 0.0, 0.0), depth=1.0)
            with gpu.matrix.push_pop():
            # reset matrices -> use normalized device coordinates [-1, 1]
                gpu.matrix.load_matrix(Matrix.Identity(4))
                gpu.matrix.load_projection_matrix(Matrix.Identity(4))

                gpu.state.depth_test_set('LESS_EQUAL')
                gpu.state.depth_mask_set(True)

                shader = self.meshtriangle_shader
                shader.bind()

                self.mesh.rebuild_batch_buffers(shader)

                camera = bpy.data.objects['Camera']
                mv, mw = get_camera_matrices(camera, depsgraph, self.size_x, self.size_y)
                mvp = mw @ mv

                shader.set_mat4('ModelViewProjectionMatrix', mvp.transposed())
                shader.set_mat4('ModelMatrix', self.mesh.matrix_world.transposed())

                camera_loc = camera.location

                shader.set_vec3('viewPos',  camera_loc)
                shader.set_vec3('lightPos', self.light.location)

                self.mesh.draw(shader)

                gpu.state.depth_mask_set(False)
                shader.unbind()

            buffer = fb.read_color(0,0, self.size_x, self.size_y, 4, 0, 'FLOAT')

        offscreen.free()

        # if IMAGE_NAME not in bpy.data.images:
        #     bpy.data.images.new(IMAGE_NAME, self.size_x, self.size_y)
        # image = bpy.data.images[IMAGE_NAME]
        # image.scale(self.size_x, self.size_y)

        buffer_list = []

        for line in buffer:
            line_list = line.to_list()
            buffer_list += line_list

        buffer_list = np.reshape(buffer_list, (1, -1))[0]

        GAMMA = 1.0 / 2.4
        linearrgb_to_srgb = lambda c: (c * 12.92 if c > 0.0 else 0.0) if c < 0.0031306684425 else 1.055 * c**GAMMA - 0.055

        # when rendering to a separate image texture you DO have to do this. but NOT when rendering directly into a pass        
        # image.pixels = [linearrgb_to_srgb(v) for v in buffer_list]

        result = self.begin_result(0, 0, self.size_x, self.size_y)
        layer = result.layers[0].passes["Combined"]
        layer.rect.foreach_set(np.array(buffer_list, np.float32))
        self.end_result(result)



    def view_draw(self, context, depsgraph):
        # Lazily import GPU module, so that the render engine works in
        # background mode where the GPU module can't be imported by default.
        import gpu

        scene = depsgraph.scene
        region = context.region
        region3d = context.region_data

        gpu.state.depth_test_set('LESS_EQUAL')
        gpu.state.depth_mask_set(True)


        self.bind_display_space_shader(scene)

        shader = self.meshtriangle_shader

        shader.bind()

        self.mesh.rebuild_batch_buffers(shader)

        mv = region3d.view_matrix @ self.mesh.matrix_world
        mvp = region3d.window_matrix @ mv

        shader.set_mat4('ModelViewProjectionMatrix', mvp.transposed())
        shader.set_mat4('ModelMatrix', self.mesh.matrix_world.transposed())

        shader.set_vec3('viewPos', region3d.view_matrix.inverted().translation)
        shader.set_vec3('lightPos', self.light.location)

        self.mesh.draw(shader)

        gpu.state.depth_mask_set(False)

        shader.unbind()

        self.unbind_display_space_shader()
