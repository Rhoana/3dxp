#!/usr/bin/python
import os
import cv2
import h5py
import glob
import argparse
import numpy as np

help = {
    'out': 'output file (default out.h5)',
    'png2hd': 'Stack all pngs into a hdf5 file!',
    'pngs': 'input folder with all pngs (default pngs)',
    't': 'datatype for output file (default uint8)',
    'c': '-c enables -t uint32 (and default -o bgr)',
    'o': 'Little Endian channel order as rgba,bgr (default none)',
}
paths = {}
rgba = {
    'r': 0,
    'g': 1,
    'b': 2,
    'a': 3
}
parser = argparse.ArgumentParser(description=help['png2hd'])
parser.add_argument('-t', metavar='string', default='uint8', help=help['t'])
parser.add_argument('-o', metavar='string', default='', help=help['o'])
parser.add_argument('pngs', default='pngs', nargs='?', help=help['pngs'])
parser.add_argument('out', default='out.h5', nargs='?', help=help['out'])
parser.add_argument('-c', help=help['c'], action='store_true')

# attain all arguments 
args = vars(parser.parse_args())
for key in ['pngs', 'out']:
    paths[key] = os.path.realpath(os.path.expanduser(args[key]))
[order, color, dtype] = [args['o'], args['c'], args['t']]

# Set color datatype
if color:
    dtype = 'uint32'
    order = order or 'bgr'
dtype = getattr(np,dtype)

# read all pngs in pngs folder
search = os.path.join(paths['pngs'],'*.png')
stack = sorted(glob.glob(search))

# Size input files
sliceShape = cv2.imread(stack[0], 0).shape
shape = (len(stack),) + sliceShape

# open an output file
with h5py.File(paths['out'], 'w') as hf:
    written = hf.create_dataset("main", shape, dtype=dtype)
    # Add each png file as a slice
    for zi, file in enumerate(stack):
        if not order:
            # Write as a plain image
            written[zi, :, :] = cv2.imread(file, 0)
        else:
            # pixel to integer
            volume = cv2.imread(file)
            slice = np.zeros(volume.shape[:2])
            for ci, char in enumerate(order):
                colorbyte = volume[:, :, rgba[char]] * (256 ** ci)
                slice = slice + colorbyte
            # Write as a segmented image
            written[zi, :, :] = slice

        # simple progress indicator
        if zi % (shape[0] / 10) == 1:
            print str(100 * zi / shape[0]) + '%'
