#!/usr/bin/python
import os
import h5py
import glob
import argparse
import numpy as np
from formats.common import format_path
from formats.common import trial2span
from formats.fromHDF5 import hd2info
from formats.fromHDF5 import hd2np
from formats.toMojo import MojoImg
from formats.toMojo import MojoSeg

help = {
    'hd5': 'input hd5 file',
    'out': 'output mojo parent',
    'runs': 'The total number of runs',
    'trial': 'The number of this trial',
}
fmtc = argparse.ArgumentDefaultsHelpFormatter
desc = "Expand a hd5 File into a mojo folder!"
parser = argparse.ArgumentParser(description=desc, formatter_class=fmtc)
# Get all needed arguments
parser.add_argument('hd5', default='hd5', nargs='?', help=help['hd5'])
parser.add_argument('out', default='mojo', nargs='?', help=help['out'])
parser.add_argument('--trial','-t', default=0, type=int, help=help['trial'])
parser.add_argument('--runs', '-r', default=1, type=int, help=help['runs'])
args = vars(parser.parse_args())

# Format input and output paths
in_path = format_path(args['hd5'])
out_path = format_path(args['out'])
# Get parallelization arguments
trial, runs = args['trial'], args['runs']

# Get the shape and data type
out_shape, out_type = hd2info(in_path)
# Get the bounds over input z slices
z_span = trial2span(trial, runs, 0, out_shape[0])
# Show the current z span
msg = """z:{}
""".format(z_span)
print(msg)

# Select the correct conversion
mojoMaker = MojoImg(out_path)
if np.iinfo(out_type).max is not 255:
    mojoMaker = MojoSeg(out_path)

# Save images for each z slice
for zi, z_slice in hd2np(in_path, z_span):
    mojoMaker.run(z_slice, zi)
    
# Write as image or segmentation
outfile.save(out_shape)

