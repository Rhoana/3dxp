#!/usr/bin/python
import os
import cv2
import h5py
import glob
import argparse
import numpy as np
from formats.fromStack import opencv2np

help = {
    'out': 'output file (default out.h5)',
    'png2hd': 'Stack all pngs into a hdf5 file!',
    'pngs': 'input folder with all pngs (default pngs)',
    't': 'datatype for output file (default uint8)',
    'c': '-c enables -t uint32 (and default -o bgr)',
    'o': 'Little Endian channel order as rgba,bgr (default none)',
    'z': 'The start:stop subregion to crop in Z (default full)',
    'y': 'The start:stop subregion to crop in Y (default full)',
    'x': 'The start:stop Subregion to crop in X (default full)',
}
parser = argparse.ArgumentParser(description=help['png2hd'])
parser.add_argument('-t', metavar='string', default='uint8', help=help['t'])
parser.add_argument('-o', metavar='string', default='', help=help['o'])
parser.add_argument('pngs', default='pngs', nargs='?', help=help['pngs'])
parser.add_argument('out', default='out.h5', nargs='?', help=help['out'])
parser.add_argument('-c', help=help['c'], action='store_true')
parser.add_argument('-z', default='0', help=help['z']) 
parser.add_argument('-y', default='0', help=help['y']) 
parser.add_argument('-x', default='0', help=help['x']) 

# Get all arguments
args = vars(parser.parse_args())
# Format input and output paths
def fmt_path (k):
    return os.path.realpath(os.path.expanduser(k))
path_args = [args['pngs'], args['out']]
in_path, out_path = map(fmt_path, path_args)

# Label the order, color, and type arguments
[order, color, dtype] = [args['o'], args['c'], args['t']]
# Set color datatype
if color:
    dtype = 'uint32'
    order = order or 'bgr'
# Get the real data type
out_type = getattr(np, dtype)

# Format the spans from strings
fmt_span = lambda k: map(int, k.split(':'))
span_args = [args['z'], args['y'], args['x']]
span_pairs = map(fmt_span, span_args)

# Make a png generator
k_png = ['png', 'PNG']
png_gen = opencv2np(in_path, k_png, out_type, order, span_pairs)
# Get the shape for the volume
out_shape = png_gen.next()

# open an output file
with h5py.File(out_path, 'w') as hf:
    written = hf.create_dataset("main", out_shape, dtype=out_type)
    # Add each png file as a slice
    for zi, z_slice in enumerate(png_gen):
        # Write as a segmented image
        written[zi, :, :] = z_slice
