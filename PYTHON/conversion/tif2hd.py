#!/usr/bin/python
import os
import cv2
import h5py
import glob
import argparse
import numpy as np
import tifffile as tiff
from formats.fromStack import tif2np
from formats.common import make_path

help = {
    'out': 'output file (default out.h5)',
    'tif2hd': 'Stack all tifs into a hdf5 file!',
    'tifs': 'input folder with all tifs (default tifs)',
    'z': 'The start:stop subregion to crop in Z (default full)',
    'y': 'The start:stop subregion to crop in Y (default full)',
    'x': 'The start:stop Subregion to crop in X (default full)',
}

parser = argparse.ArgumentParser(description=help['tif2hd'])
parser.add_argument('tifs', default='tifs', nargs='?', help=help['tifs'])
parser.add_argument('out', default='out.h5', nargs='?', help=help['out'])
parser.add_argument('-z', default='0', help=help['z']) 
parser.add_argument('-y', default='0', help=help['y']) 
parser.add_argument('-x', default='0', help=help['x']) 

# Get all arguments
args = vars(parser.parse_args())
# Format input and output paths
def fmt_path (k):
    return os.path.realpath(os.path.expanduser(k))
path_args = [args['tifs'], args['out']]
in_path, out_path = map(fmt_path, path_args)

# Format the spans from strings
fmt_span = lambda k: map(int, k.split(':'))
span_args = [args['z'], args['y'], args['x']]
span_pairs = map(fmt_span, span_args)

# Make a tif generator
tif_gen = tif2np(in_path, span_pairs)
# Get the shape and data type
out_shape, out_type = tif_gen.next()

make_path(os.path.dirname(out_path))

# open an output file
with h5py.File(out_path, 'w') as hf:
    written = hf.create_dataset("main", out_shape, dtype=out_type)
    # Add each tif file as a slice
    for zi, z_slice in enumerate(tif_gen):
        # Write as a segmented image
        written[zi, :, :] = z_slice
