import os, cv2, h5py
import mahotas as mh
import numpy as np

HOME = os.path.expanduser('~')

IDS_IN = HOME + '/2017/data/bf/jan_push/8x_downsampled_segmentation.h5'
IDS_OUT = HOME + '/2017/data/bf/jan_push/boolid'

IMG_IN = HOME + '/2017/data/bf/jan_push/images_2kx2k.h5'
IMG_OUT = HOME + '/2017/data/bf/jan_push/aligned'

ALL_IDS = [ 49146, 49266, 50513, 51536, 54306, 68584, 81359, 91293, 114967, 117847, 123959, 151877, 163906]
GROWN = 5

with h5py.File(IDS_IN, 'r') as df:
    vol = df[df.keys()[0]]
    for zed in range(vol.shape[0]):
        plane = vol[zed,:,:]
        black = np.zeros(plane.shape, dtype=np.bool)
        for idy in ALL_IDS:
            black[plane == idy] = True
        for grow in range(GROWN):
            black = mh.dilate(black)
        grey = black.astype(np.uint8)*255

        boolfile = os.path.join(IDS_OUT, str(zed)+'.png')
        colorgrey = cv2.cvtColor(grey, cv2.COLOR_GRAY2RGB)
        cv2.imwrite(boolfile, colorgrey)
        print 'wrote', boolfile


