#!/usr/bin/python
import os
import cv2
import h5py
import glob
import argparse
import numpy as np
import tifffile as tiff

help = {
    'out': 'output file (default out.h5)',
    'tif2hd': 'Stack all tifs into a hdf5 file!',
    'd': 'force specific datatype for output file (e.g. uint8, uint32)',
    'tifs': 'input folder with all tifs (default tifs)',
}
paths = {}

parser = argparse.ArgumentParser(description=help['tif2hd'])
parser.add_argument('tifs', default='tifs', nargs='?', help=help['tifs'])
parser.add_argument('out', default='out.h5', nargs='?', help=help['out'])
parser.add_argument('-d', metavar='string', default='', help=help['d'])

# attain all arguments 
args = vars(parser.parse_args())
for key in ['tifs', 'out']:
    paths[key] = os.path.realpath(os.path.expanduser(args[key]))

# read all tifs in tifs folder
search = os.path.join(paths['tifs'],'*.tif')
stack = sorted(glob.glob(search))

# Size input files
ex_img = tiff.imread(stack[0])
sliceShape = ex_img.shape

# Get info from the tif file
shape = (len(stack),) + sliceShape
dtype = ex_img.dtype
# Use specific dtype if given
force_dtype = args['d']
if force_dtype != '':
    # Read dtype from d argument or np.uint32
    dtype = getattr(np, force_dtype, np.uint32)

# open an output file
with h5py.File(paths['out'], 'w') as hf:
    written = hf.create_dataset("main", shape, dtype=dtype)
    # Add each tif file as a slice
    for zi, file in enumerate(stack):

        # pixel to integer
        _slice = tiff.imread(file)

        # Write as a segmented image
        written[zi, :, :] = _slice

        # simple progress indicator
        if zi % (shape[0] / 10) == 1:
            print str(100 * zi / shape[0]) + '%'
