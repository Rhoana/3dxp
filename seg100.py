import sys
import getmesh

if __name__ == "__main__":
    flags = {
        #'size': 256,
        #'index': 'index.html',
        'number': int(sys.argv[1]),
        'root': '~/2017/data/seg_100x4x4',
        'www': 'X3DOM/www',
        'deep': 1
    }
    inpaths = ['stitched_seg.h5', 'grayscale.h5', 'grayscale_maps_converted']
    inpaths.extend(['X3DOM/seg_100x4x'])
    getmesh.main(*inpaths, **flags)
