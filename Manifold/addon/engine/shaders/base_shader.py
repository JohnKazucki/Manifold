import gpu

import numpy as np


class BaseShader:

    def __init__(self):
        self.program = None
        self.needs_recompile = True

    def recompile(self):

        self.program = self.compile_program()
        
    def compile_program(self):
        pass

    def set_float(self, name, value):
        self.program.uniform_float(name, value)

    def set_vec3(self, name, vector):
        self.program.uniform_float(name, vector[:])
    
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
