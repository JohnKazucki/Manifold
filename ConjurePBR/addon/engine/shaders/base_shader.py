import gpu

import numpy as np


class BaseShader:

    def __init__(self):
        self.program = None
        self.needs_recompile = True

        self.vs_src = """
void main()
{
    gl_Position = ModelViewProjectionMatrix * vec4(pos, 1.0);
    gl_Position.z = gl_Position.z - 0.000001 * gl_Position.w;
}
"""

        self.fs_src = """
void main()
{
    FragColor = vec4(0.5, 1.0, 0.1, 1.0);
}
"""


    def recompile(self):

        self.program = self.compile_program()
        

    def compile_program(self):
        shader_info = gpu.types.GPUShaderCreateInfo()

        shader_info.vertex_source(self.vs_src)
        shader_info.fragment_source(self.fs_src)

        shader_info.push_constant('MAT4', "ModelViewProjectionMatrix")
        # shader_info.push_constant('MAT4', "ModelMatrix")
        shader_info.vertex_in(0, 'VEC3', "pos")
        shader_info.fragment_out(0, 'VEC4', "FragColor")

        program = gpu.shader.create_from_info(shader_info)

        return program
    
    def set_mat4(self, name, matrix):
        matrix_list = np.reshape(matrix, (16, ))
        self.program.uniform_float(name, matrix_list)

    def bind(self) -> bool:
        if self.needs_recompile:
            self.recompile()
            self.needs_recompile = False

        if not self.program:
            return False
        
        self.program.bind()
        return True


    def unbind(self):
        pass
