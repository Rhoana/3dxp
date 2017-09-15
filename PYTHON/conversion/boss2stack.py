import os
import json
import argparse
import numpy as np
from formats.common import make_path
from formats.common import format_path
from formats.common import trial2span
from formats.fromBoss import Boss2np

if __name__ == '__main__':

    help = {
        'tiffScale': 'Rescale a grid of tiff files to an image stack',
        'files': 'The path to a json file listing all tiff files',
        'out': 'The directory to save the output images (./out)',
        'fmt': 'The output format as jpg, tif, or png (png)',
        'runs': 'The number of runs for all slices (1)',
        'trial': 'The trial number for this run (0)',
        'span': 'The start and end Z slices to use',
        'l': 'make meshes for : separated list of ids',
        'num': 'Downsampling times in XY (4)',
        'numz': 'Downsampling times in Z (2)'
    }
    # Read the arguments correctly
    parser = argparse.ArgumentParser(description=help['tiffScale'])
    # Define all the arguments
    parser.add_argument('files', help=help['files'])
    parser.add_argument('--trial','-t', default=0, type=int, help=help['trial'])
    parser.add_argument('--runs', '-r', default=1, type=int, help=help['runs'])
    parser.add_argument('--num', '-n', default=4, type=int, help=help['num'])
    parser.add_argument('--numz', '-z', default=2, type=int, help=help['numz'])
    parser.add_argument('--out', '-o', default='out', help=help['out'])
    parser.add_argument('--fmt', '-f', default='png', help=help['fmt'])
    parser.add_argument('--span', '-s', default='0', help=help['span'])
    parser.add_argument('-l','--list', default='', help=help['l'])
    # Read the argumentss into a dictionary
    args = vars(parser.parse_args())

    # Format input and output paths
    in_path = format_path(args['files'])
    out_path = format_path(args['out'])
    make_path(out_path)

    # Format the bound arguments properly
    def fmt_bound(k):
        return map(int, k.split(':'))
    
    # Create a file manager
    mgmt = Boss2np(in_path)

    # Get the span across Z
    z_span = fmt_bound(args['span'])
    # Default full span in Z
    if len(z_span) != 2:
        z_span = [0, mgmt.size[0]]
    # Get the trial and number of runs
    trial, runs = args['trial'], args['runs']

    # Get the bounds over input z slices
    z_bounds = trial2span(trial, runs, *z_span)
    
    resolution = (args['numz'], args['num'], args['num'])

    #
    # IF A LIST OF IDS IS PASSED
    #
    if args['list'] != '':
        # If list is range, actualize it
        if '-' in args['list']:
            LIST = [int(v) for v in args['list'].split('-')]
            LIST = range(*LIST)
        else:
            LIST = [int(v) for v in args['list'].split(':')]

        # Write the downsampled volume to a tiff stack
        mgmt.scale_images(z_bounds, out_path, resolution, args['fmt'], LIST)
    ### 
    # Default
    ###
    else: 
        # Write the downsampled volume to a tiff stack
        mgmt.scale_images(z_bounds, out_path, resolution, args['fmt'])
