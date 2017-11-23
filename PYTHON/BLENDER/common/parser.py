import argparse

def key(k):
    helps = {
        'folder': '/folder/ or /id_%%d/folder/',
        'file': '*_segmentation_%%d.stl (default {})',
        'list': '%%d:%%d:%%d... list for %%d in folder and file', 
        'output': 'Output folder to render scene images',
        'blend': 'Blender file to save output',
        'tmp': 'Temporary folder (default {})',
        'um/VOL': 'Set D:H:W size of volume measured in μm (default {})',
        'um/XYZ': 'Set X:Y:Z origin of full volume in microns (default {})',
        'vol/VOL': 'Xn:Yn:Zn subvolumes in full volume (default {})',
        'vol/xyz': 'Xi:Yi:Zi # subvolumes offset from origin (default {})',
        'vox/mesh': 'w:h:d of voxels per mesh unit (default {})',
        'nm/vox': 'w:h:d of nm per voxel (default {})',
    }
    defaults = {
        'tmp': 'tmp',
        'file': '*.stl',
        'um/VOL': '50:50:50',
        'um/XYZ': '0:0:0',
        'vol/VOL': '1:1:1',
        'vol/xyz': '0:0:0',
        'vox/mesh': '1:1:1',
        'nm/vox': '4:4:30',           
    }
    keys = {
        'help': helps.get(k, '???'),
    }
    if k in defaults:
        v = defaults[k]
        keys['default'] = v
        keys['help'] = keys['help'].format(v)

    return keys

def setup(_filename, _describe):
    COMMAND = 'blender -P '+_filename+' --'
    DETAILS = _describe + '\n'
    'The "folder" and "file" can take %%d'
    ' from --list %%d:%%d:%%d. At least one *'
    ' wildcard must find only digits if no'
    ' --list is given. --VOL and --XYZ set'
    ' the scene in physical micrometers.'
    ' The other spatial keywords simply'
    ' allow consistency between sources.'

    # Parse with defaults
    cmd = argparse.ArgumentParser(**{
        'prog': COMMAND,
        'description': DETAILS,
        'formatter_class': argparse.RawTextHelpFormatter,
    })
    cmd.add_argument('folder', **key('folder'))
    cmd.add_argument('-f','--file', **key('file'))
    cmd.add_argument('-l','--list', **key('list'))
    cmd.add_argument('-b', '--blend', **key('blend'))
    cmd.add_argument('-o', '--output', **key('output'))
    cmd.add_argument('--XYZ', **key('um/XYZ'))
    cmd.add_argument('--VOL', **key('um/VOL'))
    cmd.add_argument('--xyz', **key('vol/xyz'))
    cmd.add_argument('--vol', **key('vol/VOL'))
    cmd.add_argument('--vox', **key('vox/mesh'))
    cmd.add_argument('--nm', **key('nm/vox'))

    return cmd
