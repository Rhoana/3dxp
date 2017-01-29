import sys
import getmesh

if __name__ == "__main__":
    #tile_size = 256
    #index = 'index.html'
    n_ids = int(sys.argv[1])
    input_h5 = '~/2017/data/seg_100x4x4/stitched_seg.h5'
    output_www = '~/2017/winter/3dxp1338/X3DOM/seg_100x4x4/'
    getmesh.main([input_h5, output_www], n=n_ids)
