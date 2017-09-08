from toArgv import toArgv
import sys, argparse
import os, cv2, h5py
import numpy as np

def start(_argv):
    args = parseArgv(_argv)

    PNG_IN = args['png']
    IMG_OUT = args['out']
    PNG_OUT = os.path.join(IMG_OUT,'images')

    if not os.path.exists(IMG_OUT):
        os.makedirs(IMG_OUT)

    # Link whole image stack
    if os.path.exists(PNG_IN) and not os.path.exists(PNG_OUT):
        os.symlink(PNG_IN, PNG_OUT)

def parseArgv(argv):
    sys.argv = argv

    help = {
       'png': 'input raw png folder (default pngs)',
       'out': 'output image directory (default .)',
       'help': 'Link a png stack to an output dircetory',
    }

    parser = argparse.ArgumentParser(description=help['help'])
    parser.add_argument('out', default='.', help=help['out'])
    parser.add_argument('png', default='pngs', help=help['png'])

    return vars(parser.parse_args())

def main(*_args, **_flags):
    return start(toArgv(*_args, **_flags))

if __name__ == "__main__":
    print start(sys.argv)

