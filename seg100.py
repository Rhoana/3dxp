import sys
import getmesh

if __name__ == "__main__":
    flags = {
        #'size': 256,
        #'index': 'index.html',
        'number': int(sys.argv[1]),
        'ids': '~/2017/data/seg_100x4x4/stitched_seg.h5',
        'raw': '~/2017/data/seg_100x4x4/grayscale.h5'
    }
    output_www = '~/2017/winter/3dxp1338/X3DOM/seg_100x4x4/'
    getmesh.main(output_www, **flags)
