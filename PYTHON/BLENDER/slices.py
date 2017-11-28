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
from common import mover
from common import sizer

from common import err
from common import log

def remove_obj(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    bpy.ops.object.delete()

def read_z(_path, zFinder, _groups):
    ext = _path.split(".")[-1] 
    try:
        z_name = next(zFinder(_path))
    except StopIteration:
        raise err.MeshLabelError('', _path)
    log.yaml('Adding {}'.format(z_name), _path)
    importer = bpy.ops.import_image.to_plane
    status = importer(**{
        'files': [{'name':_path}]
    })
    if 'FINISHED' in status:
        pass
    return status

def add_slice(_glob, _groups, *_zs):
    status = set()
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
        try:
            status |= read_z(ifile, zFinder, _groups)
            z_name = next(zFinder(ifile))
        except err.MeshLabelError:
            raise err.MeshLabelError(globber, ifile)
        # Properly format zname
        z_num = int(z_name)
        z_name = '{:d}'.format(z_num)
        # Get volume and subvolume sizes
        new_obj = bpy.context.active_object
        # Get source image
        new_material = new_obj.active_material
        new_texture = new_material.active_texture
        new_image = new_texture.image
        # Set names to subvolume z index
        new_material.name = z_name
        new_texture.name = z_name
        # SUB and VOL GROUPS
        sub_vol = [_groups['SUB'], _groups['VOL']]
        g_planes = mover.in_groups(sub_vol, 'Plane*')
        g_plane = next(g_planes, None)
        # Add to existing plane if needed
        if g_plane:
            # Add material to existing Plane
            g_plane.data.materials.append(new_material)
            g_materials = g_plane.material_slots
            remove_obj(new_obj)
            # Scale to current Z
            mover.move_z(g_plane, z_num)
            continue

        # dimensions from subvolume
        sub = Vector(_groups['SUB'].subvolume)
        vol = Vector(_groups['VOL'].volume)
        new_obj.dimensions = sub
        # Set scale based on size of image
        pixels = tuple(new_image.size) + (0,)
        scale = Vector(_groups['SRC'].from_mesh)
        scale_pixels = Vector(pixels)
        scale_pixels.x *= scale.x
        scale_pixels.y *= scale.y
        new_obj.scale = scale_pixels

        # Translate image by origin and offset
        vol_origin = Vector(_groups['VOL'].origin)
        sub_offset = Vector(_groups['SUB'].offset)
        sub_origin = vol_origin + sub_offset
        # Origin of plane represents center
        sub_center = sub_origin + sub/2
        sub_center.z = sub_origin.z
        new_obj.location = sub_center

        # add to all groups
        for g in _groups.values(): 
            g.objects.link(new_obj)

        # Flip texture UV map
        for uv_map in new_obj.data.uv_layers:
            for k in uv_map.data:
                k.uv = k.uv[0], 1-k.uv[1]

        # Scale to current Z
        mover.move_z(new_obj, z_num)

    if not status:
        log.yaml('Warning, No files match', globber)
        return {'CANCELLED'}
    log.yaml('Imported', globber)
    return status

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
