import numpy as np
from stl import mesh
from skimage import measure
from toMesh import Edger

class Mesher:
    def __init__(self,volume):
        self.volume = volume
        self.slices = range(self.volume.shape[0])
        self.edge_vol = np.zeros(volume.shape, dtype=np.bool)
        self.runAll()
    def run(self,k):
        edgy = Edger(self.volume[k]).runAll(k)
        self.edge_vol[k] = edgy.edge_image
        print ('k ',k)
    def runAll(self):
        for sliced in self.slices:
            self.run(sliced)
        return self
    def store_mesh(self, filename, bboff):

        arr = [self.edge_vol,0]
        params = {
            'spacing': (1., 1., 1.,),
            'gradient_direction':'ascent'
        }
        verts, faces = measure.marching_cubes(*arr,**params)
        applied_verts = verts[faces]

        mesh_data = np.zeros(applied_verts.shape[0], dtype=mesh.Mesh.dtype)

        for i, v in enumerate(applied_verts):
            mesh_data[i][1] = v + bboff

        m = mesh.Mesh(mesh_data)
        with open(filename, 'w') as f:
            m.save(filename, f)
        return m

