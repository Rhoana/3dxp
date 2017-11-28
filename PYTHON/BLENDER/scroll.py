import bpy
from mathutils import Vector

from functools import reduce
import fnmatch
import glob
import math
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
from common import semver
from common import linker
from common import sizer
from common import mover
from common import err
from common import log

def keyframe(planes, vox_z):
    for p in planes:
        mover.move_vox_z(p, vox_z)
        p.keyframe_insert(**{
            'data_path': 'location',
            'index': -1
        })

def animate(arg, versions):
    # Convert inputs to world units
    known = {
        'um/w': [sizer.UM,] * 3,
        'um/XYZ': sizer.parse_list(arg.XYZ, 3),
        'um/VOL': sizer.parse_list(arg.VOL, 3),
    }
    w_VOL = sizer.convert(known, ['um/VOL'],['um/w'])
    w_XYZ = sizer.convert(known, ['um/XYZ'],['um/w'])
    # Where to animate (in world units)
    given = {
        'volume': w_VOL,
        'origin': w_XYZ,
    }
    # Select group to animate
    vol_k = list(given.keys())
    vol_v = versions[0]['Items']['VOL']
    groups = linker.match(given, vol_v, vol_k)
    group, likeness = next(groups)
    if not group:
        return
    # Get planes in group
    planes = set(mover.in_groups([group], 'Plane*'))
    if not planes:
        return
    # Get sources for planes
    def plane_src(src, x):
        x_g = x.users_group
        x_s = mover.match_name(x_g, 'SRC*')
        return src | set(x_s)
    sources = reduce(plane_src, planes, set())
    if not sources:
        return

    # World z min and max
    w_min = w_XYZ[-1]
    w_max = w_XYZ[-1] + w_VOL[-1]
    # World z start and stop
    w_span = [w_min, w_max]
    def w_clamp(v):
        return sorted(v/sizer.UM, w_min, w_max)[1]
    if arg.zspan:
        w_span = sizer.parse_list(arg.zspan, 2)
        w_span = [w_clamp(v) for v in w_span]
    # Get voxels per world unit
    all_vox_w = [s['to_vox'] for s in sources]
    vox_w = [sum(v) for v in zip(*all_vox_w)]
    # Voxel z start and stop
    z_span = [int(vox_w[-1]*v) for v in w_span]

    # Get frames per z
    scene = bpy.context.scene
    frame_sec = scene.render.fps
    frame_z = frame_sec / arg.zrate
    frame_z = int(math.ceil(frame_z))

    # Actually animate
    current_frame = 0
    for vox_z in range(*z_span):
        scene.frame_set(current_frame)
        # Move slice and change texture
        keyframe(planes, vox_z)
        # Jump frames per z slice
        current_frame += frame_z

def main(arg, versions):
    # Open the scene
    bpy.ops.common.start(blend=arg.blend)
    # Animate
    animate(arg, versions)
    # Stop the scene
    bpy.ops.common.stop(**{
        'blend': arg.blend,
        'output': arg.output,
        'movie': True,
    })

if __name__ == "__main__":
    describe = 'Set up the scene.'
    filename = os.path.basename(__file__)
    # Get argument parser
    items = [
        'blend', 'output',
        'um/VOL', 'um/XYZ',
    ]
    cmd = parser.setup(filename, describe, items)
    parser.add_argument(cmd, 'zspan')
    parser.add_argument(cmd, 'zrate')
    # Get most recent version
    versions = semver.all()
    semver.setup(versions)
    # Run everything safely
    err.wrap(cmd, main, versions)
