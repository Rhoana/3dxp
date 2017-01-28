import sys
import simple3d
tile_size = 256
index = 'index.html'
n_ids = int(sys.argv[1])
input_h5 = '~/2017/data/seg_100x4x4/stitched_seg.h5'
output_www = '~/2017/winter/3dxp1338/X3DOM/seg_100x4x4/'
simple3d.main(input_h5, output_www, n_ids, tile_size, index)
