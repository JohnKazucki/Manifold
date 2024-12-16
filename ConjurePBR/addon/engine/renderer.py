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

    def render(self, depsgraph):
        # Lazily import GPU module, since GPU context is only created on demand
        # for rendering and does not exist on register.
        import gpu

        # Perform rendering task.
        pass


    def view_update(self, context, depsgraph):
        pass

    def view_draw(self, context, depsgraph):
        # Lazily import GPU module, so that the render engine works in
        # background mode where the GPU module can't be imported by default.
        import gpu

        scene = depsgraph.scene
        region = context.region
        region3d = context.region_data

        self.bind_display_space_shader(scene)

        self.meshtriangle_shader.bind()

        self.mesh.rebuild(None)
        self.mesh.draw(self.meshtriangle_shader)

        self.meshtriangle_shader.unbind()

        self.unbind_display_space_shader()
