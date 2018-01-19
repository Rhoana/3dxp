import os
import json
import argparse
import numpy as np
from formats.common import progress
from formats.common import make_path
from formats.common import format_path
from formats.common import trial2span
from formats.common import parse_list
from formats.fromStack import tif2np
from formats.toMojo import MojoImg
from formats.toMojo import MojoSeg

if __name__ == '__main__':

    help = {
        'tiff2mojo': 'Send a stack of tiff files to a mojo directory',
        'files': 'The path to a directory of tiff files',
        'out': 'The output mojo directory (./mojo)',
        'runs': 'The number of runs for all slices (1)',
        'trial': 'The trial number for this run (0)',
        'em': 'Force EM stack generation (False)',
        'id': 'Force ID stack generation (False)',
        'z': 'The start and end full voxel Z span',
        'y': 'The start and end full voxel Y span',
        'x': 'The start and end full voxel X span',
        'delta': 'Define full voxel 0,0,0 in data Z,Y,X (0:0:0)',
    }
    # Read the arguments correctly
    parser = argparse.ArgumentParser(description=help['tiff2mojo'])
    # Define all the arguments
    parser.add_argument('files', help=help['files'])
    parser.add_argument('--em', action='store_true', help=help['em'])
    parser.add_argument('--id', action='store_true', help=help['id'])
    parser.add_argument('--trial','-t', default=0, type=int, help=help['trial'])
    parser.add_argument('--runs', '-r', default=1, type=int, help=help['runs'])
    parser.add_argument('--delta', '-d', default='0:0:0', help=help['delta'])
    parser.add_argument('--out', '-o', default='mojo', help=help['out'])
    parser.add_argument('-z', default='0', help=help['z'])
    parser.add_argument('-y', default='0', help=help['y'])
    parser.add_argument('-x', default='0', help=help['x'])
    # Read the argumentss into a dictionary
    args = vars(parser.parse_args())

    # Format input and output paths
    in_path = format_path(args['files'])
    out_path = format_path(args['out'])
    make_path(out_path)

    def fmt_span(k):
        try:
            return parse_list(k, 2)
        except ValueError as e:
            msg = "Using full span because {}"
            print(msg.format(str(e)))
            return [0]

    # Get all the deltas
    z_off, y_off, x_off = parse_list(args['delta'], 3)

    # Get the input spans
    in_spans = [
        list(z_off + np.int64(fmt_span(args['z']))),
        list(y_off + np.int64(fmt_span(args['y']))),
        list(x_off + np.int64(fmt_span(args['x']))),
    ]

    # Create tif generator
    tif_gen = tif2np(in_path, in_spans)
    # Get the shape and data type
    full_shape, input_type = tif_gen.next()

    # Get the full z_span
    full_z0 = in_spans[0][0]
    full_z = [full_z0, full_z0 + full_shape[0]]

    # Get the bounds over input z slices
    trial, runs = args['trial'], args['runs']
    trial_bounds = trial2span(trial, runs, *full_z)
    trial_range = range(*trial_bounds)

    mojo_kind = None
    if args['em']:
        mojo_kind = MojoImg
    if args['id']:
        mojo_kind = MojoSeg

    # Infer option if not given
    if mojo_kind == None:
        mojo_kind = MojoImg
        if np.iinfo(input_type).max is not 255:
            mojo_kind = MojoSeg

    # Get the mojo maker
    mojoMaker = mojo_kind(out_path, trial)

    # Go through the bounds
    for z_i, z_slice in enumerate(tif_gen):
        if z_i not in trial_range:
            continue
        # Get the output z coordinates
        out_z = z_i - full_z0

        # Write a layer to mojo
        mojoMaker.run(z_slice, out_z)

        # Write progress
        progress(z_i, len(trial_range), step='Total Saved')
        print("Wrote z={} as z={}".format(z_i, out_z))

    # Write as image or segmentation
    mojoMaker.save(full_shape)
