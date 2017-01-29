from toArgv import toArgv
import sys, argparse
import os, cv2, h5py
import mahotas as mh
import numpy as np

def start(_args):
    args = parseArgv(_args)
    HOME = os.path.expanduser('~')

    IMG_IN = HOME + '/2017/data/seg_100x4x4/grayscale.h5'
    IMG_OUT = HOME + '/2017/winter/3dxp1338/X3DOM/seg_100x4x4/x3d'

    all_sides = {
        'y': lambda vol: vol[:,0,:],
        'x': lambda vol: vol[:,:,0]
    }

    with h5py.File(IMG_IN, 'r') as df:
        vol = df[df.keys()[0]]
        for key in all_sides:
            image = all_sides[key](vol)
            sidefile = os.path.join(IMG_OUT, '0_in_'+key+'.png')
            colorgrey = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            cv2.imwrite(sidefile, colorgrey)
            print 'wrote', sidefile

def parseArgv(argv):
    sys.argv = argv

    help = {
        'help': 'Find thes sides of an image volume'
    }

    parser = argparse.ArgumentParser(description=help['help'])

    return vars(parser.parse_args())

def main(_args, **_flags):
    start(toArgv(_args, **_flags))

if __name__ == "__main__":
    start(sys.argv)

