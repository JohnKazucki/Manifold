import gpu

class BaseShader:

    def __init__(self):
        self.program = None
        self.needs_recompile = True

        self.vs_src = """
in vec3 pos;

void main()
{
    gl_Position = vec4(pos, 1.0);
}
"""

        self.fs_src = """
out vec4 FragColor;

void main()
{
    FragColor = vec4(0.5, 1.0, 0.1, 1.0);
}
"""


    def recompile(self):

        self.program = self.compile_program()
        

    def compile_program(self):

        program = gpu.types.GPUShader(self.vs_src, self.fs_src)

        return program


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
