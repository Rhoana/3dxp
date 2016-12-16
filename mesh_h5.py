#!/home/john/venv/mesh/bin/python

import os
import sys
import h5py
import math
import scipy
import numpy as np
from stl import mesh
import mahotas as mh
from skimage import measure

MAX_Z = 10
NEURON_ID = 18915
NEURON_ID = sys.argv[1]
SPLINE_RESOLUTION = 1/16.
OUT_FOLDER = '/home/john/2017/winter/3dxp/3dxp_data/hohoho/'
DATA = '/home/john/2017/jan/ecs20/dec/segmentation.h5'


def threshold(arr, val):
    out = np.zeros(arr.shape, dtype=np.bool)
    out[arr == val] = 1
    return out

with h5py.File(DATA,'r') as f:
    upsamp = 10
    volstack = f[f.keys()[0]]
    z,y,x = volstack.shape
    z = min(z,MAX_Z)
    thresholded_3d = np.zeros([upsamp*z,y,x], dtype=np.bool)
    #img = f[key0][:,:,:]
    for SLICE in range(z):
        print SLICE , '/', z
        za,zb = [upsamp*i for i in [SLICE,SLICE+1]]
        thresholded_3d[za:zb] = threshold(volstack[SLICE], NEURON_ID)

class Edger:
    def __init__(self,spots):

        # Generate edge_image output and edges input 
        self.edge_image = np.zeros(spots.shape,dtype=np.bool)
        self.max_shape = np.array(self.edge_image.shape)-1
        self.edges = measure.find_contours(spots, 0)
        self.edges.sort(self.sortAll)

    def run(self, edgen,old_interp):
        y,x = zip(*edgen)
        # get the cumulative distance along the contour
        dist = np.sqrt((np.diff(x))**2 + (np.diff(y))**2).cumsum()[-1]
        # build a spline representation of the contour
        spline, u = scipy.interpolate.splprep([x, y])
        res =  int(SPLINE_RESOLUTION*dist)
        print 'res', res
        sampler = np.linspace(0, u[-1], res)

        # resample it at smaller distance intervals
        interp_x, interp_y = scipy.interpolate.splev(sampler, spline)
        iy,ix = [[int(math.floor(ii)) for ii in i] for i in [interp_x,interp_y]]
        interp = [np.clip(point,[0,0],self.max_shape) for point in zip(ix,iy)]

        for j in range(1, len(interp)):
            mh.polygon.line(interp[j-1], interp[j], self.edge_image)

        if len(old_interp):
            # Option 1
            polygo = old_interp[::-1]+interp
            mh.polygon.fill_polygon(polygo,self.edge_image)

        return interp

    def sortAll(self,a,b):
        xylists = [zip(*a),zip(*b)]
        da,db = [np.array([max(v)-min(v) for v in l]) for l in xylists]
        return 2*int((da-db < 0).all())-1

    def runAll(self,old_interp):
        if len(self.edges):
            new_interp = self.run(self.edges[0], old_interp)
            return new_interp
        return old_interp

class Mesher:
    old_interp = []
    def __init__(self,volume):
        self.volume = volume
        self.slices = range(self.volume.shape[0])
        self.edge_vol = np.zeros(volume.shape, dtype=np.bool)
        self.runAll()
    def run(self,k):
        edgy = Edger(self.volume[k])
        self.old_interp = edgy.runAll(self.old_interp)
        self.edge_vol[k] = edgy.edge_image
        print 'k ',k
    def runAll(self):
        for sliced in self.slices:
            self.run(sliced)

def store_mesh(arr, filename):

    verts, faces = measure.marching_cubes(arr, 0, spacing=(1.,1.,1.),gradient_direction='ascent')
    applied_verts = verts[faces]

    mesh_data = np.zeros(applied_verts.shape[0], dtype=mesh.Mesh.dtype)

    for i, v in enumerate(applied_verts):
        mesh_data[i][1][0] = v[0]
        mesh_data[i][1][1] = v[1]
        mesh_data[i][1][2] = v[2]

    m = mesh.Mesh(mesh_data)
    with open(filename, 'w') as f:
        m.save(filename, f)

    return m

volume = thresholded_3d.swapaxes(0,1)
meshed = Mesher(volume).edge_vol
print 'check one'

m1 = store_mesh(meshed, OUT_FOLDER+str(NEURON_ID)+'_smooth1.stl')
