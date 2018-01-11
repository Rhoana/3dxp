import json
import os, glob
import sys, argparse

def write_json(parent, fold, fold_files):

    index_file = os.path.basename(fold)
    index_path = os.path.join(parent, index_file)
    www_file = lambda x: os.path.relpath(x, parent)
    with open(index_path, 'w') as wf:
        mesh_info = {
            'fragments': list(map(www_file, fold_files))
        }
        json.dump(mesh_info, wf)

def start(_argv):

    args = parseArgv(_argv)
    # expand all system paths
    homepath = lambda pathy: os.path.expanduser(pathy)
    realpath = lambda pathy: os.path.realpath(homepath(pathy))
    
    FOLD_GREP = args['grep']
    FILE_GREP = args['files']
    ROOT = realpath(args['root'])
 
    # Assert root is a folder
    if not os.path.isdir(ROOT):
        err = 'Error, need folder @ {}'.format(ROOT)
        sys.stderr.write(err)
        return

    # Find all folders in root
    parent = os.path.dirname(ROOT)
    fold_search = os.path.join(ROOT, FOLD_GREP)
    for fold in glob.glob(fold_search):
        # Find all files in folder
        file_search = os.path.join(fold, FILE_GREP)
        fold_files = list(glob.glob(file_search))
        # Write the index to json file
        if len(fold_files):
            write_json(parent, fold, fold_files)

def parseArgv(argv):
    sys.argv = argv

    help = {
        'root': 'Root path',
        'grep': 'grep pattern of folders to index',
        'f': 'grep pattern of files in folders',
        'help': 'Make an hdf5 file into html meshes!',
    }

    parser = argparse.ArgumentParser(description=help['help'])
    parser.add_argument('root', help=help['root'])
    parser.add_argument('grep', default='*', nargs='?', help=help['grep'])
    parser.add_argument('-f','--files', default='*', help=help['f'])

    # Get all arguments
    return vars(parser.parse_args())

def main(*_args, **_flags):
    return start(toArgv(*_args, **_flags))

if __name__ == "__main__":
    print start(sys.argv)

