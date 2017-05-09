import os
import json
import argparse
import numpy as np
from tiffMGMT import TiffMGMT

if __name__ == '__main__':

    help = {
        'tiff2h5': 'Rescale a list of tiff files to one h5 file',
        'files': 'The path to a json file listing all tiff files',
        'out': 'The directory to save the output pngs (./out)',
        'runs': 'The number of runs for all slices (1)',
        'z0': 'The order of this run (0)',
        'num': 'Downsampling times (4)',
    }
    # Read the arguments correctly
    parser = argparse.ArgumentParser(description=help['tiff2h5'])
    # Define all the arguments
    parser.add_argument('files', help=help['files'])
    parser.add_argument('z0', default=0, type=int, nargs='?', help=help['z0'])
    parser.add_argument('--runs', '-r', default=1, type=int, help=help['runs'])
    parser.add_argument('--num', '-n', default=4, type=int, help=help['num'])
    parser.add_argument('--out', '-o', default='out', help=help['out'])
    # Read the argumentss into a dictionary
    argd = vars(parser.parse_args())
    # Format the path arguments properly
    def fmt_path(k):
        return os.path.abspath(os.path.expanduser(argd[k]))
    in_file, out_folder = map(fmt_path, ['files', 'out'])
    # Make sure the out folder exists
    if not os.path.exists(out_folder):
        try:
            os.mkdir(out_folder)
        except OSError:
            pass

    # Format the bound arguments properly
    def fmt_bound(k):
        return np.uint32(map(int,argd[k].split(':')))
    # Create a file manager
    mgmt = TiffMGMT(in_file)
    # Get the bounds over z
    tiles = np.linspace(0, mgmt.size[0], argd['runs'] + 1)
    z_bounds = np.uint32(tiles[argd['z0']:][:2])
    resolution = argd['num']
    # Write the downsampled volume to a tiff stack
    mgmt.scale_png(z_bounds, out_folder, resolution)
