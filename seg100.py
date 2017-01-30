import sys
import getmesh

if __name__ == "__main__":
    flags = {
        #'size': 256,
        #'index': 'index.html',
        'number': int(sys.argv[1]),
        'root': '~/2017/data/seg_100x4x4'
    }
    outpath = '~/2017/winter/3dxp1338/X3DOM/seg_100x4x4/'
    inpaths = ['stitched_seg.h5', 'grayscale.h5']
    getmesh.main(outpath, *inpaths, **flags)
