import sys, os
import getmesh

if __name__ == "__main__":
    flags = {
        'number': int(sys.argv[1]),
        'deep': 1
    }
    id_path = '~/2017/data/seg_100x4x4/stitched_seg.h5'
    side_path = '~/2017/data/seg_100x4x4/grayscale.h5'
    getmesh.boolid(id_path, images='mask', **flags)

    inpaths = [id_path, side_path, 'mask']
    getmesh.main(*inpaths, www='../../www', **flags)
