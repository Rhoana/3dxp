#!/usr/bin/python
import os
import h5py
import glob
import argparse
import numpy as np
from toMojo.np2imgo import Imgo
from toMojo.np2sego import Sego

help = {
    'out': 'output mojo parent (default mojo)',
    'hd2mojo': 'Expand a hd5 File into a mojo folder!',
    'hd5': 'input hd5 file (default hd5)',
}
paths = {}

parser = argparse.ArgumentParser(description=help['hd2mojo'])
parser.add_argument('hd5', default='hd5', nargs='?', help=help['hd5'])
parser.add_argument('out', default='mojo', nargs='?', help=help['out'])

# attain all arguments 
args = vars(parser.parse_args())
for key in ['hd5', 'out']:
    paths[key] = os.path.realpath(os.path.expanduser(args[key]))

# Add each png file as a slice
with h5py.File(paths['hd5'],'r') as hi:

    group = hi[hi.keys()[0]]
    shape = group.shape
    dtype = group.dtype

    outfile = Imgo(paths['out'])
    if np.iinfo(dtype).max is not 255:
        outfile = Sego(paths['out'])

    for zi in range(500, shape[0]):
        outfile.run(group[zi, :, :], zi)
    
    # Write as image or segmentation
    outfile.save(shape)
