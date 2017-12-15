import os
import json
import argparse
import numpy as np
from formats.common import progress
from formats.common import make_path
from formats.common import format_path
from formats.common import trial2span
from formats.common import from_scale_z
from formats.common import to_scale_spans
from formats.common import parse_list
from formats.fromBoss import Boss2np
from formats.toMojo import MojoImg
from formats.toMojo import MojoSeg

if __name__ == '__main__':

    help = {
        'boss2mojo': 'Rescale a grid of tiff files to a mojo directory',
        'files': 'The path to a json file listing all tiff files',
        'out': 'The output mojo directory (./mojo)',
        'runs': 'The number of runs for all slices (1)',
        'trial': 'The trial number for this run (0)',
        'z': 'The start and end full voxel Z span',
        'y': 'The start and end full voxel Y span',
        'x': 'The start and end full voxel X span',
        'l': 'make meshes for : separated list of ids',
        'scale': 'Downsampling times in Z,Y,X (0:0:0)',
        'delta': 'Define full voxel 0,0,0 in data Z,Y,X (0:0:0)',
    }
    # Read the arguments correctly
    parser = argparse.ArgumentParser(description=help['boss2mojo'])
    # Define all the arguments
    parser.add_argument('files', help=help['files'])
    parser.add_argument('--trial','-t', default=0, type=int, help=help['trial'])
    parser.add_argument('--runs', '-r', default=1, type=int, help=help['runs'])
    parser.add_argument('--scale', '-s', default='0:0:0', help=help['scale'])
    parser.add_argument('--delta', '-d', default='0:0:0', help=help['delta'])
    parser.add_argument('--out', '-o', default='mojo', help=help['out'])
    parser.add_argument('-l','--list', default='', help=help['l'])
    parser.add_argument('-z', default='0', help=help['z'])
    parser.add_argument('-y', default='0', help=help['y'])
    parser.add_argument('-x', default='0', help=help['x'])
    # Read the argumentss into a dictionary
    args = vars(parser.parse_args())

    # Format input and output paths
    in_path = format_path(args['files'])
    out_path = format_path(args['out'])
    make_path(out_path)

    def fmt_span(k, size):
        try:
            return parse_list(k, 2)
        except ValueError:
            return [0, size]
   
    # Create a file manager
    mgmt = Boss2np(in_path)

    # Get full shape
    full_shape = mgmt.full_shape
    z_max, y_max, x_max = full_shape
    # Get all the deltas
    z_off, y_off, x_off = parse_list(args['delta'], 3)

    # Get the span across Z
    z_span = np.int64(fmt_span(args['z'], z_max))
    y_span = np.int64(fmt_span(args['y'], y_max))
    x_span = np.int64(fmt_span(args['x'], x_max))
    # Get all the spans
    full_spans = [
        list(np.clip(z_span + z_off, 0, z_max)),
        list(np.clip(y_span + y_off, 0, y_max)),
        list(np.clip(x_span + x_off, 0, x_max)),
    ]

    # Get the input resolution
    resolution = parse_list(args['scale'], 3)
    # Get the scaled spans and shape
    scale_spans = to_scale_spans(full_spans, resolution)
    out_shape = np.squeeze(np.diff(scale_spans))
    # Get the scaled z_span
    scale_z_span = scale_spans[0]
    scale_z0 = scale_z_span[0]

    # Get the bounds over input z slices
    trial, runs = args['trial'], args['runs']
    trial_bounds = trial2span(trial, runs, *scale_z_span)
    trial_range = range(*trial_bounds)

    #
    # IF A LIST OF IDS IS PASSED
    #
    LIST = []
    if args['list'] != '':
        # If list is range, actualize it
        if '-' in args['list']:
            LIST = [int(v) for v in args['list'].split('-')]
            LIST = range(*LIST)
        else:
            LIST = [int(v) for v in args['list'].split(':')]

    # Select the correct conversion
    mojoMaker = MojoImg(out_path, trial)
    if np.iinfo(mgmt.dtype).max is not 255:
        mojoMaker = MojoSeg(out_path, trial)

    # Go through the scaled bounds
    for i, scale_z in enumerate(trial_range):
        # Get the full z coordinates
        full_z = from_scale_z(scale_z, resolution) 
        # Get the output z coordinates
        out_z = scale_z - scale_z0

        # Write the downsampled volume to a tiff stack
        a = mgmt.scale_image(full_z, resolution, full_spans, LIST)
        # Write a layer to mojo
        mojoMaker.run(a, out_z)

        # Write progress
        progress(i, len(trial_range), step='Total Saved')
        print("Wrote z={} as z={}".format(full_z, out_z))

    # Write as image or segmentation
    mojoMaker.save(out_shape)
