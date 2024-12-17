import bpy

from .mesh import Mesh
from .shaders.base_shader import BaseShader


class ConjurePBRRenderEngine(bpy.types.RenderEngine):
    bl_idname = "CONJUREPBR"
    bl_label = "Conjure PBR"

    # Request a GPU context to be created and activated for the render method.
    # This may be used either to perform the rendering itself, or to allocate
    # and fill a texture for more efficient drawing.
    bl_use_gpu_context = True


    def __init__(self):
        self.mesh = Mesh("test")
        self.meshtriangle_shader = BaseShader()

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


    def update_mesh(self, obj, depsgraph):
        evaluated_obj = obj.evaluated_get(depsgraph)

        self.mesh.update(obj)
        self.mesh.rebuild(evaluated_obj)


    def render(self, depsgraph):
        # Lazily import GPU module, since GPU context is only created on demand
        # for rendering and does not exist on register.
        import gpu

        # Perform rendering task.
        pass


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

        self.mesh.draw(shader)

        gpu.state.depth_mask_set(False)

        shader.unbind()

        self.unbind_display_space_shader()
