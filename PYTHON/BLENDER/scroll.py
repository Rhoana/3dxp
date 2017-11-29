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

def keyframe(vol, planes, w_z):
    scene = bpy.context.scene
    movement = {
        'data_path': 'location',
        'index': -1
    }
    # Set light above volume
    if 'Area' in scene.objects:
        vx, vy, vz = vol.volume
        area = scene.objects['Area']
        off = (0.1*vx, 0.1*vy, 0.1+vz)
        mover.move_w_vol(vol, area, off)
    # Move the light just above slice
    if 'Over' in scene.objects:
        off = (0.0, 0.0, w_z + 2.0)
        over = scene.objects['Over']
        mover.move_w_vol(vol, over, off)
        over.keyframe_insert(**movement)
    # Move the light just below slice
    if 'Under' in scene.objects:
        off = (0.0, 0.0, w_z - 2.0)
        under = scene.objects['Over']
        mover.move_w_vol(vol, under, off)
        under.keyframe_insert(**movement)
    # Move the planes to the z position
    for p in planes:
        mover.move_w_z(p, w_z)
        p.keyframe_insert(**movement)

def animate(arg, versions):
    context = bpy.context
    scene = context.scene
    # Rate must be positive
    if arg.zps <= 0:
        'zps {} must be >0'.format(arg.zps)
        log.yaml('Error', msg)
        return
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
        log.yaml('Error', 'No group')
        return
    # Select all meshes
    for o in scene.objects:
        o.select = False
    for o in group.objects:
        if o.type == 'MESH':
            o.select = True
    # Focus camera on meshes
    bpy.ops.view3d.camera_to_view_selected()

    # Get planes in group
    planes = set(mover.in_groups([group], 'Plane*'))
    if not planes:
        log.yaml('Error', 'No plane')
        return
    # Get sources for planes
    def plane_src(src, x):
        x_g = x.users_group
        x_s = mover.match_name(x_g, 'SRC*')
        return src | set(x_s)
    sources = reduce(plane_src, planes, set())
    if not sources:
        log.yaml('Error', 'No source')
        return
    # Convert between world and voxels
    any_source = next(iter(sources))
    vox_w = list(any_source['to_vox'])
    zvox_w = vox_w[-1]

    # World resolution
    w_min = w_XYZ[-1]
    w_max = w_XYZ[-1] + w_VOL[-1]
    # Voxel resolution
    v_min = int(w_min * zvox_w)
    v_max = int(w_max * zvox_w)
    if arg.zspan:
        def v_clamp(v):
            return sorted([v, v_min, v_max])[1]
        zspan = sizer.parse_list(arg.zspan, 2)
        v_span = [v_clamp(v) for v in zspan]
        w_min, w_max = [v/zvox_w for v in v_span]
        v_min, v_max = v_span
    # World step size and step count
    w_step = arg.zps / zvox_w
    slices = len(range(v_min, v_max, arg.zps))
    slicer = lambda i: w_min + w_step*i

    # Set frames per second
    scene.render.fps = arg.fps
    # Clear all keyframes
    for p in planes:
        p.animation_data_clear()

    # Actually animate
    current_frame = 0
    msg = '{1} seconds × {0} × %dμm' % sizer.UM
    log.yaml('Debug', msg.format(w_step, slices))
    # Use world Z value for all slices
    for world_z in map(slicer, range(slices)):
        # Jump frames per z slice
        current_frame += arg.fps
        scene.frame_set(current_frame)
        # Move slice and change texture
        keyframe(group, planes, world_z)
    # Set first and last frame
    scene.frame_start = arg.fps
    scene.frame_end = current_frame
    # Return planes for callbacks
    return planes

def register(on_frame):
    bpy.app.handlers.frame_change_pre.append(on_frame)

def unregister():
    handlers = bpy.app.handlers.frame_change_pre
    for h in handlers:
        handlers.remove(h)

def main(arg, versions):
    # Open the scene
    bpy.ops.common.start(blend=arg.blend)
    unregister()
    # Animate
    animate(arg, versions)
    def on_frame(scene):
        all_obj = scene.objects
        planes = mover.match_name(all_obj, 'Plane*')
        for p in planes:
            w_z =  p.location[-1]
            mover.slice_w_z(p, w_z, 0)
    register(on_frame)
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
    parser.add_argument(cmd, 'zps')
    parser.add_argument(cmd, 'fps')
    # Get most recent version
    versions = semver.all()
    semver.setup(versions)
    # Run everything safely
    err.wrap(cmd, main, versions)
