import os, cv2, h5py
import mahotas as mh
import numpy as np

HOME = os.path.expanduser('~')

IMG_IN = HOME + '/2017/data/seg_100x4x4/grayscale.h5'
IMG_OUT = HOME + '/2017/winter/3dxp1338/X3DOM/seg_100x4x4/x3d/images'

def left(vol):
    return vol[:,0,:]
def front(vol):
    return vol[:,:,0]

all_sides = {
    'y': left,
    'x': front
}

with h5py.File(IMG_IN, 'r') as df:
    vol = df[df.keys()[0]]
    for key in all_sides:
        image = all_sides[key](vol)
        sidefile = os.path.join(IMG_OUT, '0_in_'+key+'.png')
        colorgrey = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        cv2.imwrite(sidefile, colorgrey)
        print 'wrote', sidefile
