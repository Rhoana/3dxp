import bpy
import sys
import shutil
import argparse
from operator import mul
from functools import reduce
import fnmatch
import glob
import re
import os

class MeshPathError(TypeError):
    pass

class MeshLabelError(ValueError):
    pass

class ListParseError(ValueError):
    pass

class TempPathError(OSError):
    pass

def make_path(out_path):
    if not os.path.exists(out_path):
        try:
            os.makedirs(out_path)
        except OSError: 
            pass      

def fake_yaml(i, y):
    vals = str(y)
    indent ="\n  "
    if type(y) is dict:
        vals = ""
        for k,v in y.items():
            vals += fake_yaml(k,v)+'\n'
    out = "{}:\n{}".format(i, vals).rstrip('\n')
    return out.replace('\n',indent)

def log_yaml(i, y, quiet=False):
    if not quiet:
        print(fake_yaml(i,y)+'\n')

def fake_dir(obj):
    logging = {}
    for k in dir(obj):
        if '__' not in k:
            logging[k] = str(getattr(obj,k,'???'))
    return logging

def log_dir(obj):
    obj_n = getattr(obj, 'name', str(obj))
    log_yaml(obj_n, fake_dir(obj))

def log_diff(_a, _b):
    difference = {}
    a_n = getattr(_a, 'name', str(_a))
    b_n = getattr(_b, 'name', str(_b))
    a, b = map(fake_dir, [_a, _b])
   
def color_label(label):
    red = ((107 * int(label)) % 700) / 700.0
    green = ((509 * int(label)) % 900) / 600.0
    blue = ((200 * int(label)) % 777) / 777.0
    return red, green, blue

def parse_list(_list, _len=None, _log=''):
    LIST = []
    for val in _list.split(':'):
        if val.isdigit():
            LIST += [int(val)]
    if _len is not None:
        if _len is not len(LIST):
            msg = 'Must have {} numbers'.format(_len)
            raise(ListParseError(msg, _log, LIST))
    return LIST

def format_path(details, key, *args):
    val = details.get(key) or ''
    try:
        # Allow '/path/*/' % ()
        # Allow '/path/%d' % (id,)
        details[key] = val % args
    except (TypeError, ValueError) as e:
        # Disallow '/path/%d' % ()
        if not len(args):
            raise MeshPathError(e.args[0], key, val)
        # Allow '/path/45' % (id,)
        pass

def format_details(_details, *args):
    details = _details.copy()
    for k in details.keys():
        format_path(details, k, *args)
    return details

def read_id(filepath, idFinder, basic):
    tmp_root = basic.get('tmp','tmp')
    ext = filepath.split(".")[-1] 
    attributes = {
        '3ds': 'autodesk_3ds',
    }
    ext = attributes.get(ext,ext)
    # Need to know name
    if ext in ['stl', 'ply']:
        try:
            name = next(idFinder(filepath))
        except StopIteration:
            raise MeshLabelError('', filepath)
        # Replicate bpy.ops.import_mesh.stl
        log_yaml('Importing {}'.format(name), filepath)
        importer =  getattr(bpy.ops.import_mesh, ext)
        # Create a symbolic link to change path name
        tmp_link = make_link(filepath, tmp_root, name, ext)
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
        log_yaml('Importing Scene', filepath)
        importer =  getattr(bpy.ops.import_scene, ext)
        return importer(filepath=filepath)

    # Cannot import
    log_yaml('Warning, unknown extension', filepath)
    return {'CANCELLED'}

def import_id(_details, basic, *_ids):
    details = format_details(_details, *_ids)
    idFinder = lambda x: map(str, _ids)
    log_yaml('Importing', details)
    # Test if any files exist
    globber = details['filepath']
    status = set()
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
            status |= read_id(ifile, idFinder, basic)
        except MeshLabelError:
            raise MeshLabelError(globber, ifile)
        # Set scale for newly imported mesh
        new_obj = bpy.context.active_object
        new_obj.scale = basic.get('scale', [1,1,1])

    if not status:
        log_yaml('Warning, No files match', details)
    return status

def remove_mesh(scene, k, v):
    obj = scene.objects[k]
    scene.objects.unlink(obj)
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(v)

def get_scale(arg):
    given = { 
        'quad/vol': [2,]*3,
        'um/nm': [0.001,]*3,
        'um/vol': parse_list(arg.vol, 3, 'vol'),
        'nm/vox': parse_list(arg.nm, 3, 'nm'),
        'vox/unit': parse_list(arg.vox, 3, 'vox'),
    }
    # um/unit := vox/unit * nm/vox * um/nm
    # vol/unit := um/unit / um/vol
    # quad/unit := vol/unit * quad/vol
    result = [1, 1, 1]
    denoms = ['um/vol']
    mults = [
        'vox/unit', 'nm/vox', 'um/nm', 'quad/vol',
    ]
    mz, my, mx = zip(*(given[m] for m in mults))
    qz, qy, qx = zip(*(given[d] for d in denoms))
    result[0] = reduce(mul, mz, 1) / reduce(mul, qz, 1)
    result[1] = reduce(mul, my, 1) / reduce(mul, qy, 1)
    result[2] = reduce(mul, mx, 1) / reduce(mul, qx, 1)
    log_yaml('Render units / Mesh unit', result)
    return result

def import_all(arg):
    unused = ['Cube']
    scene = bpy.context.scene
    matte = bpy.data.materials['Material']
    # New mesh defaults
    basic = {
        'material': matte, 
        'scale': get_scale(arg),
        'tmp': arg.tmp,
    }

    # Remove the default cube mesh
    for k,v in bpy.data.meshes.items():
        if k in unused:
            remove_mesh(scene, k, v)
            log_yaml('Removed', k)

    # Set default mesh paths
    glob = os.path.join(arg.folder, arg.file)
    mesh_paths = {
        'filepath': glob,
        'file': arg.file,
    }
    status = set()
    if arg.list:
        # Try to import all given IDs
        for _id in parse_list(arg.list):
            status |= import_id(mesh_paths, basic, _id)
    else:
        # Try to import all IDs in folder
        status |= import_id(mesh_paths, basic)

    # Warn if any imports did not finish
    unfinished = status - set(['FINISHED'])
    if len(unfinished):
        log_yaml('Warning, some imports', unfinished)

    # Render if file given
    if arg.output:
        outdir = os.path.dirname(arg.output)
        make_path(outdir)
        # Path as the output of the scene
        scene.render.filepath = arg.output
        log_yaml('Rendering', arg.output)
        # Write a single image to the output
        bpy.ops.render.render(write_still=True)

    # Save if blend given
    if arg.blend:
        outdir = os.path.dirname(arg.blend)
        make_path(outdir)
        log_yaml('Saving blend file', arg.blend)
        bpy.ops.wm.save_as_mainfile(filepath=arg.blend)

def make_link(filepath, tmp_root, name, ext):
    # Create a temporary folder for this file
    tmp_folders = filepath.replace('.','_').split(os.sep)
    tmp_path = os.path.join(tmp_root, *tmp_folders)
    tmp_link = os.path.join(tmp_path, '{}.{}'.format(name, ext))
    make_path(tmp_path)
    try:
        if os.path.exists(tmp_link):
            if os.path.isdir(tmp_link):
                os.rmdir(tmp_link)
            else:
                os.unlink(tmp_link)
    except OSError as e:
        raise TempPathError(e.args[0], filepath, tmp_link)

    # Link the path temporarily
    os.symlink(filepath, tmp_link)
    return tmp_link

def clear_tmp(arg):
    # Remove tmp directory
    if os.path.exists(arg.tmp):
        shutil.rmtree(arg.tmp)

if __name__ == "__main__":
    COMMAND = 'blender -P '+__file__+' --'

    helps = {
        'import': """Import STL files.
The 'folder' and 'file' can take %d from --list %d:%d:%d. Exactly
one * wildcard must find only digits if no --list is given.
        """, 
        'folder': '/folder/ or /id_%d/folder/',
        'file': '*_segmentation_%d.stl (default *.stl)',
        'list': '%d:%d:%d... list for %d in folder and file', 
        'output': 'Output folder to render scene images',
        'blend': 'Blender file to save output',
        'tmp': 'Temporary folder (default ./tmp)',
        'vol': 'z:y:x of full volume in μm (50:50:50)',
        'vox': 'z:y:x of mesh units in voxels (1:1:1)',
        'nm': 'z:y:z of voxels in nm (30:4:4)',
    }

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
    parser.add_argument('--vol', default='50:50:50', help=helps['vol'])
    parser.add_argument('--vox', default='1:1:1', help=helps['vox'])
    parser.add_argument('--nm', default='30:4:4', help=helps['nm'])
    # Parse all arguments after double dash
    args = []
    try:
        arg0 = sys.argv.index('--')
        args = list(sys.argv)[arg0+1:]
    except ValueError as e:
        log_yaml('Usage Error', {
            'Missing -- in': ' '.join(sys.argv),
            'Usage': parser.format_usage(),
        })
    try:
        parsed = parser.parse_args(args)
        clear_tmp(parsed)

        # Main function
        import_all(parsed)

        clear_tmp(parsed)
        print('Done')
    except SystemExit as e:
        helped = '-h' in args or '--help' in args
        usage = parser.format_usage().split(' ')
        log_yaml('EXIT', {
            'Bad Usage': COMMAND+' '+' '.join(args),
            'Usage': ' '.join(usage[1:]),
        }, helped)
    # Cannot format paths without giving integers
    except MeshPathError as e:
        error, k, v = e.args
        log_yaml('Error', {
            'Error': error,
            'No ID in --list': {
                '--list': helps['list'],
            },
            'Need ID to format "{}" argument'.format(k): v,
        })
    # Cannot infer ID from file path
    except MeshLabelError as e:
        search, path = e.args
        log_yaml('Error', {
            'Error': 'Cannot infer ID label from path',
            'Search Path': search,
            'Real Path': path,
        })
    # Cannot link temp file needed
    except TempPathError as e:
        error, real, symbol = e.args
        log_yaml('Error', {
            'Error': error,
            'Cannot link': {
                'From': real,
                'To': symbol,
            }
        })
    # Cannot read list
    except ListParseError as e:
        error, k, v = e.args
        log_yaml('Error', {
            error: helps.get(k,k),
            k: v,
        })
