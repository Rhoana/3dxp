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

from common import semver
from common import parser
from common import linker
from common import pather
from common import sizer

from common import err
from common import log

def color_label(label):
    red = ((107 * int(label)) % 700) % 256
    green = ((509 * int(label)) % 900) % 256
    blue = ((200 * int(label)) % 777) % 256
    return red/256, green/256, blue/256

def read_id(_path, idFinder, _groups):
    ext = _path.split(".")[-1] 
    tmp_root = _groups['VOL'].tmp
    attributes = {
        '3ds': 'autodesk_3ds',
    }
    ext = attributes.get(ext,ext)
    # Need to know name
    if ext in ['stl', 'ply']:
        try:
            name = next(idFinder(_path))
        except StopIteration:
            raise err.MeshLabelError('', _path)
        log.yaml('Importing {}'.format(name), _path)
        importer =  getattr(bpy.ops.import_mesh, ext)
        # Create a symbolic link to change path name
        tmp_link = pather.link(_path, tmp_root, name, ext)
        status = importer(filepath = tmp_link)
        if 'FINISHED' in status:
            # Set color for new object
            new_obj = bpy.context.active_object
            mat = bpy.data.materials.new(name=name)
            mat.diffuse_color = color_label(name) 
            new_obj.data.materials.append(mat) 
        return status

    # Names and details in file
    if ext in ['autodesk_3ds', 'obj', 'x3d']:
        log.yaml('Importing Scene', _path)
        importer =  getattr(bpy.ops.import_scene, ext)
        return importer(filepath=_path)

    # Cannot import
    log.yaml('Warning, unknown extension', _path)
    return {'CANCELLED'}

def import_id(_glob, _groups, *_ids):
    status = set()
    globber = pather.format_glob(_glob, *_ids)
    idFinder = lambda x: map(str, _ids)
    # Test if any files exist
    if not _ids:
        matcher = fnmatch.translate(globber) 
        grouper = matcher.replace('.*','(.*)')
        rematch = re.compile(grouper).match
        def idFinder(x):
            m = rematch(x)
            g = m.groups('') if m else ()
            return (i for i in g if i.isdigit())
    # For all files that match
    for ifile in glob.iglob(globber):
        try:
            status |= read_id(ifile, idFinder, _groups)
        except err.MeshLabelError:
            raise err.MeshLabelError(globber, ifile)
        # Set scale for newly imported mesh
        new_obj = bpy.context.active_object
        new_obj.scale = _groups['SRC'].from_mesh
        # Translate mesh by origin and offset
        vol_origin = Vector(_groups['VOL'].origin)
        sub_offset = Vector(_groups['SUB'].offset)
        new_obj.location = vol_origin + sub_offset
        # add to all groups
        for g in _groups.values(): 
            bpy.ops.object.group_link(group=g.name)
    if not status:
        log.yaml('Warning, No files match', globber)
        return {'CANCELLED'}
    log.yaml('Imported', globber)
    return status

def import_all(versions, arg):

    _groups = {}
    # Get group matching arguments
    for s,n in linker.groups(versions, arg):
        _groups[s] = bpy.data.groups[n]

    # Set default mesh paths
    _glob = os.path.join(arg.folder, arg.file)
    status = set()
    if arg.list:
        # Try to import all given IDs
        for _id in sizer.parse_list(arg.list):
            status |= import_id(_glob, _groups, _id)
    else:
        # Try to import all IDs in folder
        status |= import_id(_glob, _groups)

    # Warn if any imports did not finish
    unfinished = status - set(['FINISHED'])
    if len(unfinished):
        log.yaml('Warning, some meshes', unfinished)

def main(arg, versions):
    # Open the scene
    bpy.ops.common.start(blend=arg.blend)

    # Import the meshes
    pather.unlink(arg)
    import_all(versions, arg)
    pather.unlink(arg)

    # Stop the scene
    bpy.ops.common.stop(blend=arg.blend, output=arg.output)

if __name__ == "__main__":
    describe = 'Import mesh files.'
    filename = os.path.basename(__file__)
    # Get argument parser
    cmd = parser.setup(filename, describe)
    parser.add_argument(cmd, 'tmp')
    # Get most recent version
    versions = semver.all()
    semver.setup(versions)
    # Run everything safely
    err.wrap(cmd, main, versions)
