import math
import sys
import os

from BLENDER.common import parser
from BLENDER.common import err
from BLENDER.common import log

def main(arg):
    # Add task to path
    task_file = '{:010d}'.format(arg.task)
    task_out = os.path.join(arg.output, task_file)

    print(task_out)

if __name__ == "__main__":
    describe = 'Scale precomputed meshes.'
    filename = os.path.basename(__file__)
    # Get argument parser
    items = [
        'folder', 'file', 'list', 'output',
        'vox/mesh', 'nm/vox',
    ]
    cmd = parser.setup(filename, describe, items, ez=True)
    parser.add_argument(cmd, 'task')
    parser.add_argument(cmd, 'runs')
    # Run everything safely
    err.wrap(cmd, main, ez=True)
