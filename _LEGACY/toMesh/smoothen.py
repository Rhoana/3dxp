import numpy as np
from stl import mesh
from skimage import measure
from toMesh import tracefill

class Smoothen:
    def __init__(self,volume):
        self.volume = volume
        all_y = self.volume.shape[0]
        self.smooth_vol = np.zeros(volume.shape, dtype=np.bool)
        for y in range(all_y):
            self.smooth_vol[y] = tracefill(self.volume[y])

    def save_mesh(self, filename, bboff):

        arr = [self.smooth_vol,0]
        params = {
            'spacing': (1., 1., 1.,),
            'gradient_direction':'ascent'
        }
        verts, faces = measure.marching_cubes(*arr,**params)
        applied_verts = verts[faces]
        vert_count = applied_verts.shape[0]

        mesh_data = np.zeros(vert_count, dtype=mesh.Mesh.dtype)

        for i, v in enumerate(applied_verts):
            mesh_data[i][1] = v + bboff

        m = mesh.Mesh(mesh_data)
        with open(filename, 'w') as f:
            m.save(filename, f)
        return m

def savemesh(volume, filename, bboff):

    print ('Storing mesh at '+where[0])
    arr = [volume,0]
    params = {
        'spacing': (1., 1., 1.,),
        'gradient_direction':'ascent'
    }
    verts, faces = measure.marching_cubes(*arr,**params)
    applied_verts = verts[faces]
    vert_count = applied_verts.shape[0]

    mesh_data = np.zeros(vert_count, dtype=mesh.Mesh.dtype)

    for i, v in enumerate(applied_verts):
        mesh_data[i][1] = v + bboff

    m = mesh.Mesh(mesh_data)
    with open(filename, 'w') as f:
        m.save(filename, f)
    return m

def smoothvol(volume):
    print('Smoothening volume of '+str(volume.shape))
    smoothy = Smoothen(volume)
    return smoothy.smooth_vol

def smoothmesh(volume,*where):
    print('Smoothening volume of '+str(volume.shape))
    smoothy = Smoothen(volume)
    print ('Storing mesh at '+where[0])
    return smoothy.save_mesh(*where)
