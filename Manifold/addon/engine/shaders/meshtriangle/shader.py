import gpu

from ..base_shader import BaseShader

import os.path
from .....get_path import get_path



class MeshTriangleShader(BaseShader):
    def __init__(self):
        super().__init__()

        self.vs_src, self.fs_src, self.typedef_src = self.get_shader_source()

    def get_shader_source(self):
        addon_path = get_path()

        addon_relative_path = os.path.join('addon', 'engine', 'shaders', 'meshtriangle', 'source')
        src_folder = os.path.join(addon_path, addon_relative_path)

        template_src_files = (
        "meshtriangle.vs.glsl",
        "meshtriangle.fs.glsl",
        "typedef.glsl"
        )

        sources = []

        for template in template_src_files:
            src_file = os.path.join(src_folder, template)
            with open(src_file) as f:
                sources.append(f.read())

        return sources[0], sources[1], sources[2]

    def compile_program(self):
        shader_info = gpu.types.GPUShaderCreateInfo()

        shader_info.typedef_source(self.typedef_src)

        shader_info.vertex_source(self.vs_src)
        shader_info.fragment_source(self.fs_src)
        

        shader_info.push_constant('VEC3', "viewPos")

        shader_info.push_constant('MAT4', "ModelViewProjectionMatrix")
        shader_info.push_constant('MAT4', "ModelMatrix")

        shader_info.push_constant('VEC3', "surfaceColor")
        shader_info.push_constant('FLOAT', "surfaceRoughness")

        shader_info.uniform_buf(0, "LightData", "LightBlock[]") 

        shader_info.push_constant('VEC3', "ambientColor")
        
        shader_info.vertex_in(0, 'VEC3', "Position")
        shader_info.vertex_in(1, 'VEC3', "Normal")
        shader_info.fragment_out(0, 'VEC4', "FragColor")

        vert_out = gpu.types.GPUStageInterfaceInfo("VS_OUT")
        vert_out.smooth('VEC3', "positionWS")
        vert_out.smooth('VEC3', "normalWS")

        shader_info.vertex_out(vert_out)

        program = gpu.shader.create_from_info(shader_info)

        return program
