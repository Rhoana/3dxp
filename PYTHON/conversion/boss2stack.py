import os
import json
import argparse
import numpy as np
from formats.common import make_path
from formats.common import format_path
from formats.common import trial2span
from formats.fromBoss import Boss2np
from formats.toStack import np2opencv
from formats.toStack import np2tif

if __name__ == '__main__':

    help = {
        'boss2stack': 'Rescale a grid of tiff files to an image stack',
        'files': 'The path to a json file listing all tiff files',
        'out': 'The directory to save the output images (./out)',
        'fmt': 'The output format as jpg, tif, or png (png)',
        'runs': 'The number of runs for all slices (1)',
        'trial': 'The trial number for this run (0)',
        'z': 'The start and end Z slices to use',
        'y': 'The start and end Y slices to use',
        'x': 'The start and end X slices to use',
        'l': 'Mask for : separated list of values',
        'scale': 'Downsampling times in Z,Y,X (2:3:3)',
    }
    # Read the arguments correctly
    parser = argparse.ArgumentParser(description=help['boss2stack'])
    # Define all the arguments
    parser.add_argument('files', help=help['files'])
    parser.add_argument('--trial','-t', default=0, type=int, help=help['trial'])
    parser.add_argument('--runs', '-r', default=1, type=int, help=help['runs'])
    parser.add_argument('--scale', '-s', default='', help=help['scale'])
    parser.add_argument('--out', '-o', default='out', help=help['out'])
    parser.add_argument('--fmt', '-f', default='png', help=help['fmt'])
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

    # Format colon arguments properly
    def fmt_colon(k, default):
        span = map(int, k.split(':'))
        # Default full span in Z
        if len(span) != len(default):
            return default
        return span
    def fmt_span(k, size):
        return fmt_colon(k, [0, size])
   
    # Create a file manager
    mgmt = Boss2np(in_path)

    # Get the span across Z
    z_span = fmt_span(args['z'], mgmt.full_shape[0])
    y_span = fmt_span(args['y'], mgmt.full_shape[1])
    x_span = fmt_span(args['x'], mgmt.full_shape[2])
    # Get all the spans
    all_spans = [z_span, y_span, x_span]

    # Get the input resolution
    resolution = fmt_colon(args['scale'], [2,3,3])
    z_scale = 2**resolution[0]

    # Get the bounds over input z slices
    trial, runs = args['trial'], args['runs']
    z_bound_full = trial2span(trial, runs, *z_span)
    z_bound_scale = z_bound_full // z_scale
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

    # Go through the scaled bounds
    for scale_z in range(*z_bound_scale):
        # Slice at full resolution 
        full_z = scale_z * z_scale
        # Write the downsampled volume to a tiff stack
        a = mgmt.scale_image(full_z, resolution, all_spans, LIST)

        image_fmt = args['fmt']
        # Create the png file path
        image_path = '{:05d}.{}'.format(scale_z, image_fmt)
        image_path = os.path.join(out_path, image_path)

        if os.path.exists(image_path):
            print('Skipping {}'.format(image_path))
            continue

        # Handle each format
        if image_fmt in ['tif','tiff']:
            np2tif(image_path, a)
        else:
            np2opencv(image_path, a)

        msg = "Wrote layer {} to {}"
        print(msg.format(scale_z, image_path))
