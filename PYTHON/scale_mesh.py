import numpy as np
import math
import sys
import os

from BLENDER.common import parser
from BLENDER.common import err
from BLENDER.common import log

N_DIM = 3

def parse_list(_list, _len=None, _log='', _neg=False):
    LIST = []
    for val in _list.split(':'):
        pos = val.lstrip('-')
        if pos.isdigit():
            if _neg and '-' in val:
                LIST += [-int(pos)]
                continue
            LIST += [int(pos)]
    if _len is not None:
        if _len is not len(LIST):
            msg = 'Must have {} numbers'.format(_len)
            raise err.ListParseError(msg, _log, LIST)
    return LIST

def import_id(_glob, _src, *_ids):
    status = set()
    globber = pather.format_glob(_glob, *_ids)
    idFinder = lambda x: map(str, _ids)
    # Set scale for newly imported mesh
    vox_mesh = np.float32(_src['vox_mesh'])
    nm_vox = np.float32(_src['nm_vox'])
    nm_mesh = nm_vox * vox_mesh
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
            status |= read_id(ifile, idFinder)
        except err.MeshLabelError:
            raise err.MeshLabelError(globber, ifile)
        print(nm_mesh)
    if not status:
        log.yaml('Warning, No files match', globber)
        return {'CANCELLED'}
    log.yaml('Imported', globber)
    return status

def import_all(arg):

    nm_vox = parse_list(arg.nm, 3, 'nm/vox')
    vox_mesh = parse_list(arg.vox, 3, 'vox/mesh')
    
    _src = {
        'from_mesh': vox_mesh,
        'to_um': nm_vox,
    }

    # Set default mesh paths
    _glob = os.path.join(arg.folder, arg.file)
    status = set()
    if arg.list:
        # Try to import all given IDs
        for _id in sizer.parse_list(arg.list):
            status |= import_id(_glob, _src, _id)
    else:
        # Try to import all IDs in folder
        status |= import_id(_glob, _src)

    log.yaml('Import Status', status)

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
