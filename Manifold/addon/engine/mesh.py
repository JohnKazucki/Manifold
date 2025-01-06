import gpu
from gpu_extras.batch import batch_for_shader

from .shaders.base_shader import BaseShader
from .material import BaseMaterial

import numpy as np



class Mesh:
    """Minimal representation needed to render a mesh"""
    def __init__(self, name):
        self.name = name
        self.Batch = None
        self.VBO = None
        self.IBO = None

        self.is_dirty = False
        self.indices_size = 0


    def update(self, obj):
        self.matrix_world = obj.matrix_world

    def rebuild(self, eval_obj):
        mesh = eval_obj.to_mesh()

        mesh.split_faces()
        mesh.calc_loop_triangles()

        self.indices = [0] * 3 * len(mesh.loop_triangles)
        mesh.loop_triangles.foreach_get("vertices", self.indices)
        self.indices = np.reshape(self.indices, (-1, 3)).tolist()

        self.vertices = [0] * 3 * len(mesh.vertices)
        mesh.vertices.foreach_get("co", self.vertices)
        self.vertices = np.reshape(self.vertices, (-1, 3)).tolist()

        self.normals = [0] * 3 * len(mesh.vertices)
        mesh.vertices.foreach_get("normal", self.normals)
        self.normals = np.reshape(self.normals, (-1, 3)).tolist()

        eval_obj.to_mesh_clear()
        
    def rebuild_batch_buffers(self, shader: BaseShader):
        self.Batch = batch_for_shader(shader.program, 'TRIS', {"Position": self.vertices, "Normal": self.normals}, indices=self.indices)

    def draw(self, shader: BaseShader):
        self.Batch.draw(shader.program)
