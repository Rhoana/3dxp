import os
import sys
import h5py
import numpy as np
from hd2stl import Mesher

#import matplotlib.pyplot as plt

MAX_Z = 100
MARGIN = 2
NEURON_ID = 18915
OUT_FOLDER = sys.argv[2]
NEURON_ID = int(sys.argv[1])
OUTNAME = os.path.join(OUT_FOLDER,str(NEURON_ID)+'_mesh.stl')
DATA = '/n/coxfs01/leek/results/ECS_iarpa_20u_cube/segmentation.h5'
DATA = '/home/harvard/2017/data/bf/1017/synapse.h5'

def threshold(arr, val):
    out = np.ones(arr.shape, dtype=arr.dtype)*val
    return np.equal(arr,out)

#
#

with h5py.File(DATA,'r') as f:
    upsamp = 10
    volstack = f[f.keys()[0]]
    z,y,x = volstack.shape
    z = min(z,MAX_Z)

    thresholded_3d = np.zeros([upsamp*z,y,x], dtype=np.bool)
    box_tl,box_br = [[y,x],[0,0]]
    box_up,box_dn = [-1,-1]

    for SLICE in range(z):
        print (SLICE , '/', z)
        za,zb = [upsamp*i for i in [SLICE,SLICE+1]]
        thresholded = threshold(volstack[SLICE], NEURON_ID)
        thresholded_3d[za:zb] = thresholded

        if thresholded.any():
            extent = np.argwhere(thresholded)
            box_tl = np.c_[extent.min(0),box_tl].min(1)
            box_br = np.c_[extent.max(0),box_br].max(1)
            box_dn = za if box_dn < 0 else box_dn
            box_up = zb

zo,ze = [box_dn,box_up]
yo,xo = box_tl
ye,xe = box_br

print ('shape at ',zo,yo,xo)
volume = thresholded_3d[zo:ze, yo:ye, xo:xe].swapaxes(0,1)
vy,vz,vx = volume.shape
z_margin = np.zeros([vy,MARGIN,vx], dtype=bool)
volume = np.concatenate((z_margin,volume,z_margin),axis=1)
x_margin = np.zeros([vy,vz+2*MARGIN,MARGIN], dtype=bool)
volume = np.concatenate((x_margin,volume,x_margin),axis=2)
bb_offset = (yo, zo-MARGIN, xo-MARGIN)

meshy = Mesher(volume)
print ('storing mesh..')
meshy.store_mesh(OUTNAME, bb_offset)
