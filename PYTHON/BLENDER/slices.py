import bpy
import addon_utils
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

addon_utils.enable('io_import_images_as_planes')

from common import semver
from common import parser
from common import linker
from common import pather
from common import cycler
from common import mover
from common import sizer

from common import err
from common import log

def add_plane(_groups, zname, ifile):

    # Temp material on plane
    bpy.ops.import_image.to_plane(files=[{
        'name': ifile,
    }])
    g_plane = bpy.context.active_object

    # Overwrite old material
    c_mat = cycler.mat()
    c_tex = cycler.tex(c_mat, zname, ifile)
    g_plane.data.materials[0] = c_mat

    # add to all groups
    for g in _groups.values(): 
        g.objects.link(g_plane)

    # Flip texture UV map
    for uv_map in g_plane.data.uv_layers:
        for k in uv_map.data:
            k.uv = k.uv[0], 1-k.uv[1]

    # dimensions from subvolume
    sub = Vector(_groups['SUB'].subvolume)
    vol = Vector(_groups['VOL'].volume)
    g_plane.dimensions = sub

    # Set scale based on size of image
    pixels = tuple(c_tex.image.size) + (0,)
    scale = Vector(_groups['SRC'].from_mesh)
    scale_pixels = Vector(pixels)
    scale_pixels.x *= scale.x
    scale_pixels.y *= scale.y
    g_plane.scale = scale_pixels

    # Translate image by origin and offset
    vol_origin = Vector(_groups['VOL'].origin)
    sub_offset = Vector(_groups['SUB'].offset)
    sub_origin = vol_origin + sub_offset
    # Origin of plane represents center
    sub_center = sub_origin + sub/2
    sub_center.z = sub_origin.z
    g_plane.location = sub_center

    # new plane
    return g_plane

def add_slice(_glob, _groups, *_zs):
    globber = pather.format_glob(_glob, *_zs)
    zFinder = lambda x: map(str, _zs)
    # Test if any files exist
    if not _zs:
        matcher = fnmatch.translate(globber) 
        grouper = matcher.replace('.*','(.*)')
        rematch = re.compile(grouper).match
        def zFinder(x):
            m = rematch(x)
            g = m.groups('') if m else ()
            return (i for i in g if i.isdigit())
    # For all files that match
    for ifile in glob.iglob(globber):
        # Look for Plane in SUB and VOL GROUPS
        sub_vol = [_groups['SUB'], _groups['VOL']]
        g_planes = mover.in_groups(sub_vol, 'Plane*')
        g_plane = next(g_planes, None)
        # Format name of z slice
        znum = int(next(zFinder(ifile)))
        zname = '{:d}'.format(znum)
        # Add plane if needed
        if not g_plane:
            g_plane = add_plane(_groups, zname, ifile)
        else:
            c_mat = g_plane.active_material
            cycler.tex(c_mat, zname, ifile)

        # Scale to current Z
        mover.move_z(g_plane, znum)

    log.yaml('Imported', globber)
    return {'FINISHED'}

def add_slices(versions, arg):

    _groups = {}
    # Get group matching arguments
    for s,n in linker.groups(versions, arg):
        _groups[s] = bpy.data.groups[n]

    # Set default image paths
    _glob = os.path.join(arg.folder, arg.file)
    status = set()
    if arg.list:
        # Try to add all given slices
        for _z in sizer.parse_list(arg.list):
            status |= add_slice(_glob, _groups, _z)
    else:
        # Try to import all slices in folder
        status |= add_slice(_glob, _groups)

    # Warn if any imports did not finish
    unfinished = status - set(['FINISHED'])
    if len(unfinished):
        log.yaml('Warning, some slices', unfinished)

def main(arg, versions):
    # Open the scene
    bpy.ops.common.start(blend=arg.blend)

    # Add the slices
    add_slices(versions, arg)

    # Stop the scene
    bpy.ops.common.stop(blend=arg.blend, output=arg.output)

if __name__ == "__main__":
    describe = 'Import slice images.'
    filename = os.path.basename(__file__)
    # Get argument parser
    cmd = parser.setup(filename, describe)
    # Get most recent version
    versions = semver.all()
    semver.setup(versions)
    # Run everything safely
    err.wrap(cmd, main, versions)
