import os
import sys
import h5py
import numpy as np
from toMesh import Mesher

#import matplotlib.pyplot as plt

MAX_Z = 100
MARGIN = 2
NEURON_ID = 18915
OUT_FOLDER = sys.argv[2]
NEURON_ID = int(sys.argv[1])
OUTNAME = os.path.join(OUT_FOLDER,str(NEURON_ID)+'_mesh.stl')
DATA = '/n/coxfs01/leek/results/ECS_iarpa_20u_cube/segmentation.h5'
DATA = '/home/harvard/2017/data/bf/1017/synapse.h5'

class Thresh:
    upsamp = 10
    def __init__(self):
        self.max_z = MAX_Z
        with h5py.File(DATA,'r') as f:
            self.bitvolume, self.bounds = self.load_h5(f)

    def load_h5(self, f):
        upsamp = self.upsamp
        volstack = f[f.keys()[0]]
        z,y,x = volstack.shape
        z = min(z, self.max_z)

        bitvolume = np.zeros([upsamp*z,y,x], dtype=np.bool)
        box_tl,box_br = [[y,x],[0,0]]
        box_up,box_dn = [-1,-1]

        for SLICE in range(z):
            print (SLICE , '/', z)
            za,zb = [upsamp*i for i in [SLICE,SLICE+1]]
            thresholded = self.threshold(volstack[SLICE], NEURON_ID)
            bitvolume[za:zb] = thresholded

            if thresholded.any():
                extent = np.argwhere(thresholded)
                box_tl = np.c_[extent.min(0),box_tl].min(1)
                box_br = np.c_[extent.max(0),box_br].max(1)
                box_dn = za if box_dn < 0 else box_dn
                box_up = zb

        bounds = [[box_dn,box_up], box_tl, box_br]
        return [bitvolume, bounds]

    def threshold(self, arr, val):
        out = np.ones(arr.shape, dtype=arr.dtype)*val
        return np.equal(arr,out)

    def bound(self):
        bitvolume = self.bitvolume
        box_ud, box_tl, box_br = self.bounds
        zo,ze = box_ud
        yo,xo = box_tl
        ye,xe = box_br
        volume = bitvolume[zo:ze, yo:ye, xo:xe].swapaxes(0,1)
        vy,vz,vx = volume.shape

        bound_offset = (yo, zo-MARGIN, xo-MARGIN)
        z_margin = np.zeros([vy,MARGIN,vx], dtype=bool)
        x_margin = np.zeros([vy,vz+2*MARGIN,MARGIN], dtype=bool)

        volume = np.concatenate((z_margin,volume,z_margin),axis=1)
        volume = np.concatenate((x_margin,volume,x_margin),axis=2)
        return [volume, bound_offset]
#
#

def threshbound():
    threshy = Thresh()
    return threshy.bound()

volume,offset = threshbound()
smooth = Mesher(volume)
print ('storing mesh..')
smooth.store_mesh(OUTNAME, offset)
