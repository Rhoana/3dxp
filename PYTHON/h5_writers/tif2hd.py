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
    'tifs': 'input folder with all tifs (default tifs)',
    'z': 'The start:stop subregion to crop in Z (default full)',
    'y': 'The start:stop subregion to crop in Y (default full)',
    'x': 'The start:stop Subregion to crop in X (default full)',
}
paths = {}

parser = argparse.ArgumentParser(description=help['tif2hd'])
parser.add_argument('tifs', default='tifs', nargs='?', help=help['tifs'])
parser.add_argument('out', default='out.h5', nargs='?', help=help['out'])
parser.add_argument('-z', default='0', help=help['z']) 
parser.add_argument('-y', default='0', help=help['y']) 
parser.add_argument('-x', default='0', help=help['x']) 

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
dtype = ex_img.dtype
shape = (len(stack),) + sliceShape

# Get the full spans and arguments
spans = np.uint64([[0,0,0], shape]).T
span_args = [args['z'], args['y'], args['x']]
# Format the spans from strings
fmt_span = lambda k: map(int, k.split(':'))
span_pairs = map(fmt_span, span_args)
# Set the spans if not default
for i, pair in enumerate(span_pairs):
    if len(pair) == 2:
        spans[i] = pair
# Expand the spans
[z0,z1], [y0, y1], [x0, x1] = spans
# Cropped shape
crop_shape = spans[:,1] - spans[:,0]

# open an output file
with h5py.File(paths['out'], 'w') as hf:
    written = hf.create_dataset("main", crop_shape, dtype=dtype)
    # Add each tif file as a slice
    for zi, file in enumerate(stack[z0:z1]):

        # pixel to integer
        _slice = tiff.imread(file)[y0:y1, x0:x1]

        # Write as a segmented image
        written[zi, :, :] = _slice

        # simple progress indicator
        if zi % (crop_shape[0] / 10) == 1:
            print str(100 * zi / crop_shape[0]) + '%'
