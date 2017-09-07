from toArgv import toArgv
import sys, argparse
import os, cv2, h5py
import numpy as np

def start(_argv):
    args = parseArgv(_argv)

    IMG_IN = args['raw']
    PNG_IN = args['png']
    IMG_OUT = args['out']
    PNG_OUT = os.path.join(IMG_OUT,'images')

    if not os.path.exists(IMG_OUT):
        os.makedirs(IMG_OUT)

    all_sides = {
        'z': lambda vol, i: vol[i,:,:],
        'y': lambda vol, i: vol[:,i,:],
        'x': lambda vol, i: vol[:,:,i]
    }
    def get_side(vol, key, i):
        return all_sides[key](vol, i)

    def make_img(vol, key):
        # Give the position and file name
        pos = args[key]
        file_name = '{}_in_{}.png'.format(pos, key)
        sidefile = os.path.join(IMG_OUT, file_name)
        # Write the side file as a png
        if not os.path.exists(sidefile):
            image = get_side(vol, key, pos).astype(np.uint8)
            colorgrey = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            cv2.imwrite(sidefile, colorgrey)
            print 'wrote', sidefile

    # Generate side images
    if os.path.exists(IMG_IN):
        with h5py.File(IMG_IN, 'r') as df:
            vol = df[df.keys()[0]]
            for key in args['a']:
                make_img(vol, key)

    # Link whole image stack
    if os.path.exists(PNG_IN) and not os.path.exists(PNG_OUT):
        os.symlink(PNG_IN, PNG_OUT)

def parseArgv(argv):
    sys.argv = argv

    help = {
       'out': 'output image directory (default .)',
       'raw': 'input raw h5 volume (default raw.h5)',
       'png': 'input raw png folder (default pngs)',
       'help': 'Find the sides of an image volume',
       'x': 'The position of the x slice (default 0)',
       'y': 'The position of the y slice (default 0)',
       'z': 'The position of the z slice (default 0)',
       'a': 'The axes to use (default xy)'
    }

    parser = argparse.ArgumentParser(description=help['help'])
    parser.add_argument('out', default='.', help=help['out'])
    parser.add_argument('raw', default='raw.h5', help=help['raw'])
    parser.add_argument('png', default='pngs', help=help['png'])
    parser.add_argument('-y', type=int, default=0, help=help['y'])
    parser.add_argument('-x', type=int, default=0, help=help['x'])
    parser.add_argument('-z', type=int, default=0, help=help['z'])
    parser.add_argument('-a', default='xy', help=help['a'])

    return vars(parser.parse_args())

def main(*_args, **_flags):
    return start(toArgv(*_args, **_flags))

if __name__ == "__main__":
    print start(sys.argv)

