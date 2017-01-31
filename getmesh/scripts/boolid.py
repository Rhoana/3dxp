from toArgv import toArgv
import deepest, biggest
import sys, argparse
import os, cv2, h5py
import mahotas as mh
import numpy as np

def start(_argv):
    args = parseArgv(_argv)
    # expand all system paths
    homepath = lambda pathy: os.path.expanduser(pathy)
    realpath = lambda pathy: os.path.realpath(homepath(pathy))
    sharepath = lambda share,pathy: os.path.join(share, homepath(pathy))

    GROWN = args['grow']
    TOP_DEEP = args['deep']
    TILESIZE = args['size']
    N_TOP_IDS = args['number'] + 1
    IDS_IN = realpath(args['ids'])
    IDS_OUT = sharepath(args['out'],args['images'])
    # Count most spread or deep ids 
    BIG_IDS, BIG_COUNTS = biggest.main(IDS_IN, s=TILESIZE)
    DEEP_IDS, DEEP_COUNTS = deepest.main(IDS_IN, s=TILESIZE)
    ALL_IDS = [BIG_IDS, DEEP_IDS][TOP_DEEP][-N_TOP_IDS:-1]

    if not os.path.exists(args['out']):
        print args['out'], 'must exist'
        return -1
    if not os.path.exists(IDS_OUT):
        os.makedirs(IDS_OUT)

    with h5py.File(IDS_IN, 'r') as df:
        vol = df[df.keys()[0]]
        for zed in range(vol.shape[0]):
            zpath = os.path.join(IDS_OUT,str(zed).zfill(5)+'.png')
            if os.path.exists(zpath):
                continue
            plane = vol[zed,:,:]
            black = np.zeros(plane.shape, dtype=np.bool)
            for idy in ALL_IDS:
                black[plane == idy] = True
            for grow in range(GROWN):
                black = mh.dilate(black)
            grey = black.astype(np.uint8)*255

            boolfile = os.path.join(IDS_OUT, zpath)
            colorgrey = cv2.cvtColor(grey, cv2.COLOR_GRAY2RGB)
            cv2.imwrite(boolfile, colorgrey)
            print 'wrote', boolfile

def parseArgv(argv):
    sys.argv = argv

    help = {
        'help': 'Turn h5 into boolean mask pngs for given ids',
        'out': 'output path containing image folder (defalt .)',
        'f': 'output image folder basename (defalt mask)',
        'n': 'Take top n ids from id list (default 1)',
        'g': 'dilate (grow) mask by g px (default 5)',
        's': 'load h5 in s*s*s chunks (default 256)',
        'deep': 'rank top ids by depth (default 0)',
        'ids': 'Full path to segment id hd5 file'
    }

    parser = argparse.ArgumentParser(description=help['help'])
    parser.add_argument('ids', help=help['ids'])
    parser.add_argument('out', default='.', nargs='?', help=help['out'])
    parser.add_argument('-f','--images', default='mask', help=help['f'])
    parser.add_argument('-D','--deep',type=int, default=0, help=help['deep'])
    parser.add_argument('-s','--size', type=int, default=256, help=help['s'])
    parser.add_argument('-n','--number', type=int, default=1, help=help['n'])
    parser.add_argument('-g','--grow', type=int, default=5, help=help['g'])

    return vars(parser.parse_args())

def main(*_args, **_flags):
    return start(toArgv(*_args, **_flags))

if __name__ == "__main__":
    start(sys.argv)


