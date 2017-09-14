#!/usr/bin/python
import os
import argparse
import numpy as np
from formats.common import format_path
from formats.toMojo import merge_db

help = {
    'out': 'mojo parent with database',
}
fmtc = argparse.ArgumentDefaultsHelpFormatter
desc = "Merge all databases in a mojo folder!"
parser = argparse.ArgumentParser(description=desc, formatter_class=fmtc)
# Get all needed arguments
parser.add_argument('out', default='mojo', nargs='?', help=help['out'])
args = vars(parser.parse_args())

# Format input and output paths
out_path = format_path(args['out'])
# Merge all databases
merge_db(out_path)
