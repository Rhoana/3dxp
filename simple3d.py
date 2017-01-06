import os
import numpy as np
from threed import ThreeD

HOME = os.path.expanduser('~')
DATA = HOME + '/2017/data/bf/jan_push/8x_downsampled_segmentation.h5'
ROOTDIR = HOME + '/2017/data/3dxp/jan_push/'
STLFOLDER = ROOTDIR + 'stl'
X3DFOLDER = ROOTDIR + 'x3d'
ALL_IDS = [1,2,3]
INDEX = '123.html'


subvols = zip(*np.where(np.ones([2]*3)))

#for z,y,x in subvols:
#    ThreeD.run(DATA, z, y, x, STLFOLDER, 200, ALL_IDS)

ThreeD.create_website(STLFOLDER, X3DFOLDER, [1], INDEX)

