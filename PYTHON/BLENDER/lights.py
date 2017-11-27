import bpy
from mathutils import Vector

import fnmatch
import glob
import sys
import re
import os

DIRNAME = os.path.dirname(__file__)
if not DIRNAME in sys.path:
    sys.path.append(DIRNAME)

COMMON = os.path.join(DIRNAME, 'common', '__init__.py')
bpy.ops.wm.addon_install(filepath=COMMON)
bpy.ops.wm.addon_enable(module='common')
bpy.ops.wm.save_userpref()

from common import parser

from common import err

def main(arg):
    # Open the scene
    bpy.ops.common.start(blend=arg.blend)

    # Stop the scene
    bpy.ops.common.stop(blend=arg.blend, output=arg.output)

if __name__ == "__main__":
    describe = 'Set up the scene.'
    filename = os.path.basename(__file__)
    # Get argument parser
    items = ['blend', 'output']
    cmd = parser.setup(filename, describe, items)
    # Run everything safely
    err.wrap(cmd, main)
