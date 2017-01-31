SEG=~/2017/data/seg_100x4x4/stitched_seg.h5
SIDES=~/2017/data/seg_100x4x4/grayscale.h5
python getmesh/scripts/boolid.py -n $1 -D 1 $SEG -f mask
python getmesh/main.py -n $1 -D 1 -w ../../www $SEG $SIDES mask
