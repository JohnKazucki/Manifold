import gpu

from .shaders.base_shader import BaseShader



class Mesh:
    """Minimal representation needed to render a mesh"""
    def __init__(self, name):
        self.name = name
        self.Batch = None
        self.VBO = None
        self.IBO = None

        self.is_dirty = False
        self.indices_size = 0

    def rebuild(self, eval_obj):
        # mesh = eval_obj.to_mesh()

        # self.indices = []        

        # self.vertices = [0]*len(mesh.vertices)

        self.vertices = [(-0.5,-0.2,0), (0.5,-0.2,0), (0,0.8,0)]
        self.indices = [(0, 1, 2)]

        
    def rebuild_buffers(self):
        fmt = gpu.types.GPUVertFormat()
        fmt.attr_add(id="pos", comp_type='F32', len=3, fetch_mode='FLOAT')
        fmt.attr_add(id="normal", comp_type='F32', len=3, fetch_mode='FLOAT')

        self.VBO = gpu.types.GPUVertBuf(len=len(self.vertices), format=fmt)
        self.VBO.attr_fill(id="pos", data=self.vertices)

        self.IBO = gpu.types.GPUIndexBuf(type='TRIS', seq=self.indices)

        self.Batch = gpu.types.GPUBatch(type='TRIS', buf=self.VBO, elem=self.IBO)

    def draw(self, shader: BaseShader):
        self.rebuild_buffers()
        self.Batch.draw(shader.program)
