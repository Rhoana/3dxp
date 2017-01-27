import os, cv2, h5py
import mahotas as mh
import numpy as np

HOME = os.path.expanduser('~')

IMG_IN = HOME + '/2017/data/seg_100x4x4/grayscale.h5'
IMG_OUT = HOME + '/2017/data/bf/seg_100x4x4/sides'

def back(vol):
    return vol[:,:,vol.shape(2)-1]
def right(vol):
    return vol[:,vol.shape(1)-1,:]
def left(vol):
    return vol[:,0,:]
def front(vol):
    return vol[:,:,0]

all_sides = [back,right,left,front]

with h5py.File(IDS_IN, 'r') as df:
    vol = df[df.keys()[0]]
    for side in 4:
        image = all_sides[side]()
        sidefile = os.path.join(IMG_OUT, str(zed)+'.png')
        colorgrey = cv2.cvtColor(grey, cv2.COLOR_GRAY2RGB)
        cv2.imwrite(boolfile, colorgrey)
        print 'wrote', boolfile
