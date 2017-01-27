import os, h5py
import numpy as np
from threed import ThreeD

HOME = os.path.expanduser('~')
DATA = HOME + '/2017/data/bf/jan_push/8x_downsampled_segmentation.h5'
ROOTDIR = HOME + '/2017/data/3dxp/jan_push/'
STLFOLDER = ROOTDIR + 'stl'
X3DFOLDER = ROOTDIR + 'x3d'
ALL_IDS = [ 49146, 49266, 50513, 51536, 54306, 68584, 81359, 91293, 114967, 117847, 123959, 151877, 163906]
INDEX = 'toufiq.html'
NTILES = 4

DIMX=1024
DIMY=1024
DIMZ=1024


with h5py.File(DATA, 'r') as df:
    MAXSIZE = np.max(df[df.keys()[0]].shape)
    TILESIZE = MAXSIZE // NTILES

subvols = zip(*np.where(np.ones([NTILES]*3)))

for z,y,x in subvols:
    ThreeD.run(DATA, z, y, x, STLFOLDER, TILESIZE, ALL_IDS)

ThreeD.create_website(STLFOLDER, X3DFOLDER, ALL_IDS, INDEX, DIMX, DIMY, DIMZ)

