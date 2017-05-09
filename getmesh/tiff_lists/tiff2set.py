import os
import cv2
import json
import argparse
import numpy as np
from tiffMGMT import TiffMGMT

if __name__ == '__main__':

    help = {
        'tiff2set': 'Get all values in a region a list of tiff files',
        'files': 'The path to a json file listing all tiff files',
        'out': 'The folder to save all lists of ids (./out)',
        'z_arg': 'z_start:z_stop',
        'y_arg': 'y_start:y_stop',
        'x_arg': 'x_start:x_stop',
    }
    # Read the arguments correctly
    parser = argparse.ArgumentParser(description=help['tiff2set'])
    # Define all the arguments
    parser.add_argument('files', help=help['files'])
    parser.add_argument('z_arg', help=help['z_arg'])
    parser.add_argument('y_arg', help=help['y_arg'])
    parser.add_argument('x_arg', help=help['x_arg'])
    parser.add_argument('--out', '-o', default='out', help=help['out'])
    # Read the argumentss into a dictionary
    argd = vars(parser.parse_args())
    # Format the path arguments properly
    def fmt_path(k):
        return os.path.abspath(os.path.expanduser(argd[k]))
    in_file, out_folder = map(fmt_path, ['files', 'out'])
    # Format the bound arguments properly
    def fmt_bound(k):
        return np.uint32(map(int,argd[k].split(':')))
    bounds = np.uint32(map(fmt_bound, ['z_arg','y_arg','x_arg']))
    # Create a file manager
    mgmt = TiffMGMT(in_file)

