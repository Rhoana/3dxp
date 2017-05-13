from toArgv import toArgv
import sys, argparse
import os, cv2, h5py
import mahotas as mh
import numpy as np

def start(_argv):
    args = parseArgv(_argv)

    IMG_IN = args['raw']
    PNG_IN = args['png']
    IMG_OUT = args['out']
    PNG_OUT = os.path.join(IMG_OUT,'images')

    all_sides = {
        'y': lambda vol: vol[:,0,:],
        'x': lambda vol: vol[:,:,0]
    }

    # Generate side images
    if os.path.exists(IMG_IN):
        with h5py.File(IMG_IN, 'r') as df:
            vol = df[df.keys()[0]]
            for key in all_sides:
                sidefile = os.path.join(IMG_OUT, '0_in_'+key+'.png')
                if not os.path.exists(sidefile):
                    image = np.uint8(all_sides[key](vol))
                    colorgrey = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
                    cv2.imwrite(sidefile, colorgrey)
                    print 'wrote', sidefile

    # Link whole image stack
    if os.path.exists(PNG_IN) and not os.path.exists(PNG_OUT):
        os.symlink(PNG_IN, PNG_OUT)

def parseArgv(argv):
    sys.argv = argv

    help = {
       'out': 'output image directory (default .)',
       'raw': 'input raw h5 volume (default raw.h5)',
       'png': 'input raw png folder (default pngs)',
       'help': 'Find thes sides of an image volume'
    }

    parser = argparse.ArgumentParser(description=help['help'])
    parser.add_argument('out', default='.', help=help['out'])
    parser.add_argument('raw', default='raw.h5', help=help['raw'])
    parser.add_argument('png', default='pngs', help=help['png'])

    return vars(parser.parse_args())

def main(*_args, **_flags):
    return start(toArgv(*_args, **_flags))

if __name__ == "__main__":
    print start(sys.argv)

