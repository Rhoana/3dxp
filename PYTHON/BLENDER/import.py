import bpy
import sys
import argparse
from mathutils import Vector
import fnmatch
import glob
import re
import os

DIRNAME = os.path.dirname(__file__)
if not DIRNAME in sys.path:
    sys.path.append(DIRNAME)

from common import semver
from common import linker
from common import pather
from common import sizer

from common import err
from common import log

def color_label(label):
    red = ((107 * int(label)) % 700) / 700.0
    green = ((509 * int(label)) % 900) / 600.0
    blue = ((200 * int(label)) % 777) / 777.0
    return red, green, blue

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
        # Replicate bpy.ops.import_mesh.stl
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
        # Import and set mesh name based on id
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

def remove_mesh(scene, k, v):
    obj = scene.objects[k]
    scene.objects.unlink(obj)
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(v)

def import_all(versions, arg):
    # Open if blend given
    if arg.blend and os.path.exists(arg.blend):
        log.yaml('Loading blend file', arg.blend)
        bpy.ops.wm.open_mainfile(filepath=arg.blend)

    # Get group matching arg
    bpy.ops.object.mode_set(mode='OBJECT')
    _groups = linker.get_groups(versions, arg)

    # Remove the default cube mesh
    for k,v in bpy.data.meshes.items():
        if k in ['Cube']:
            remove_mesh(bpy.context.scene, k, v)
            log.yaml('Removed', k)

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
        log.yaml('Warning, some imports', unfinished)

    # Render if file given
    if arg.output:
        outdir = os.path.dirname(arg.output)
        pather.make(outdir)
        # Path as the output of the scene
        bpy.context.scene.render.filepath = arg.output
        log.yaml('Rendering', arg.output)
        # Write a single image to the output
        bpy.ops.render.render(write_still=True)

    # Save if blend given
    if arg.blend:
        outdir = os.path.dirname(arg.blend)
        pather.make(outdir)
        log.yaml('Saving blend file', arg.blend)
        bpy.ops.wm.save_as_mainfile(**{
            'filepath': arg.blend,
            'check_existing': False,
        })

def main(parsed, versions):
    # Clear before and after import
    pather.unlink(parsed)
    import_all(versions, parsed)
    pather.unlink(parsed)

if __name__ == "__main__":
    FILENAME = os.path.basename(__file__)
    COMMAND = 'blender -P '+FILENAME+' --'

    helps = {
        'import': 'Import STL files.\n'
'The "folder" and "file" can take %%d from --list %%d:%%d:%%d. At least one *'
' wildcard must find only digits if no --list is given. --VOL and --ZYX set'
' the scene in physical micrometers. The other spatial keywords simply allow'
' consistency between sources.',
        'folder': '/folder/ or /id_%%d/folder/',
        'file': '*_segmentation_%%d.stl (default *.stl)',
        'list': '%%d:%%d:%%d... list for %%d in folder and file', 
        'output': 'Output folder to render scene images',
        'blend': 'Blender file to save output',
        'tmp': 'Temporary folder (default ./tmp)',
        'um/VOL': 'Set D:H:W size of volume measured in μm (default 50:50:50)',
        'um/ZYX': 'Set Z:Y:X origin of full volume in microns (default 0:0:0)',
        'vol/VOL': 'Zn:Yn:Xn subvolumes in full volume (default 1:1:1)',
        'vol/zyx': 'Zi:Yi:Xi # subvolumes offset from origin (default 0:0:0)',
        'vox/mesh': 'd:h:w of voxels per mesh unit (default 1:1:1)',
        'nm/vox': 'd:h:w of nm per voxel (default 30:4:4)',
    }
    # Parse with defaults
    parser = argparse.ArgumentParser(**{
        'prog': COMMAND,
        'description': helps['import'],
        'formatter_class': argparse.RawTextHelpFormatter,
    })
    parser.add_argument('folder', help=helps['folder'])
    parser.add_argument('-f','--file', default='*.stl', help=helps['file'])
    parser.add_argument('-l','--list', help=helps['list'])
    parser.add_argument('-b', '--blend', help=helps['blend'])
    parser.add_argument('-o', '--output', help=helps['output'])
    parser.add_argument('--tmp', default='tmp', help=helps['tmp'])
    parser.add_argument('--ZYX', default='0:0:0', help=helps['um/ZYX'])
    parser.add_argument('--VOL', default='50:50:50', help=helps['um/VOL'])
    parser.add_argument('--zyx', default='0:0:0', help=helps['vol/zyx'])
    parser.add_argument('--vol', default='1:1:1', help=helps['vol/VOL'])
    parser.add_argument('--vox', default='1:1:1', help=helps['vox/mesh'])
    parser.add_argument('--nm', default='30:4:4', help=helps['nm/vox'])
    # Get most recent version
    versions = semver.all()
    semver.setup(versions)
    # Run everything safely
    err.wrap(parser, main, versions)
