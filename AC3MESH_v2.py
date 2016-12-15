
# coding: utf-8

# In[6]:

import os
import h5py
import mahotas as mh
import numpy as np

from skimage import measure
from stl import mesh



import matplotlib.pyplot as plt
from matplotlib.pyplot import imshow
get_ipython().magic(u'matplotlib inline')

NEURON_ID = 3036
X_SHAPE=1024
Y_SHAPE=1024
Z_SHAPE = (0,75)
SPLINE_RESOLUTION = 1/16.
OUT_FOLDER = '/home/harvard/2017/winter/3dxp/3dxp_data/'
DATA = '/home/d/data/ac3x75/mojo/ids/tiles/w=00000000/'

def threshold(arr, val):
    out = np.zeros((arr.shape[0], arr.shape[1]), dtype=np.bool)
    out[arr == val] = 1
    return out


def store_mesh(arr, filename):
    
    verts, faces = measure.marching_cubes(arr, 0, spacing=(1.,1.,1.),gradient_direction='ascent')
    applied_verts = verts[faces]
    
    mesh_data = np.zeros(applied_verts.shape[0], dtype=mesh.Mesh.dtype)
    
    print 'Converting', applied_verts.shape[0], 'vertices'
    for i, v in enumerate(applied_verts):
        mesh_data[i][1][0] = v[0]
        mesh_data[i][1][1] = v[1]
        mesh_data[i][1][2] = v[2]
        
    m = mesh.Mesh(mesh_data)
    with open(filename, 'w') as f:
        m.save(filename, f)
        
    print 'Saved.'
    
    return m


thresholded_3d = np.zeros((Z_SHAPE[1], Y_SHAPE, X_SHAPE), dtype=np.bool)

for SLICE in range(Z_SHAPE[0], Z_SHAPE[1]):

    img = np.zeros((Y_SHAPE,X_SHAPE), dtype=np.uint64)
    tiles = sorted(os.listdir(os.path.join(DATA, 'z='+str(SLICE).zfill(8))))
    
    
    for t in tiles:
        
        if t.startswith('.'):
            continue
        
        filepath = os.path.join(DATA, 'z='+str(SLICE).zfill(8), t)
        y = int(t.split(',')[0].split('=')[1])
        x = int(t.split(',')[1].split('=')[1].split('.')[0])
        with h5py.File(filepath, 'r') as f:
            data = f.get('IdMap')
            img[y*512:y*512+512, x*512:x*512+512] = data

    # now threshold this bad boy
    thresholded_slice = threshold(img, NEURON_ID)
    thresholded_3d[SLICE] = thresholded_slice
#     threed[SLICE] = img
    
    print 'loaded', SLICE
            


# In[11]:

import math
import scipy
from skimage import measure

def relabel(array):
    return measure.label(array+1).astype(np.uint64)-1

def borderer(relabeled):
    big_spot = np.zeros(relabeled.shape, dtype=np.bool)
    return mh.labeled.borders(big_spot, edge)

def ploty(fun,*args,**kwargs):
    ax = plt.figure(figsize=(1,1)).add_subplot(111)
    getattr(ax, fun)(*args,**kwargs)

class Edger:
    def __init__(self,spots):
        
        # Generate edge_image output and edges input 
        self.edge_image = np.zeros(spots.shape,dtype=int)
        self.max_shape = np.array(self.edge_image.shape)-1
        self.edges = measure.find_contours(spots, 0) 
        self.edges.sort(self.sortAll)
        self.runAll()
        
    def run(self, edgen):
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
        
        print 'fit ', [max(iy), max(ix)], ' in ', self.edge_image.shape
        
        for j in range(1, len(interp)):
            mh.polygon.line(interp[j-1], interp[j], self.edge_image)

    def sortAll(self,a,b):
        xylists = [zip(*a),zip(*b)]
        da,db = [np.array([max(v)-min(v) for v in l]) for l in xylists]
        return 2*int((da-db < 0).all())-1
        
    def runAll(self):
#         ploty('plot',*zip(*self.edges[0]))
        self.run(self.edges[0])
        return
        for edge in self.edges:
            ploty('plot',*zip(*edge))
            self.run(edge)
            
class Mesher:
    def __init__(self,volume):
        self.volume = volume
        self.slices = range(self.volume.shape[0])
        self.edge_vol = np.zeros(volume.shape)
        self.runAll()
    def run(self,k):
#         ploty('imshow',self.volume[k])
        self.edge_vol[k] = Edger(self.volume[k]).edge_image
        print 'k ',k
    def runAll(self):
#         self.run(self.slices[146])
#         return
        for sliced in self.slices:
            self.run(sliced)


# In[12]:

upsampled = thresholded_3d.repeat(10, axis=0)
volume = upsampled.swapaxes(0,1)
meshed = Mesher(volume).edge_vol


all_borders = 0

for z in range(meshed.shape[0]):

    all_borders += meshed[z]
    
plt.figure(figsize=(10,10))
imshow(all_borders)


m1 = store_mesh(meshed, OUT_FOLDER+str(NEURON_ID)+'_smooth.stl')

