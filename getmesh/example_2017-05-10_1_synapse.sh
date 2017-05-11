#!/bin/bash

# Starting from step 0
EXAMPLE="2017_05_10_844z"
ROOT_IN="/n/coxfs01/thejohnhoffer/R0/$EXAMPLE/images"
WORKING_DIR="/n/coxfs01/thejohnhoffer/2017/3dxp/getmesh"
IDS_JSON="/n/coxfs01/leek/results/2017-05-05_R0/boss/boss.json"
RAW_JSON="/n/coxfs01/leek/dropbox/25k_201610_dataset_em.json"
IDS_TIF=$ROOT_IN"/3200_3200_ids"
RAW_PNG=$ROOT_IN"/1600_1600_raw"
IDS_DOWNSAMPLE_XY=3
IDS_DOWNSAMPLE_Z=2
RAW_DOWNSAMPLE_XY=4
RAW_DOWNSAMPLE_Z=2
RUNS=80

# Starting from step 1
IDS_H5=$ROOT_IN"/3200_3200_ids.h5"
RAW_H5=$ROOT_IN"/1600_1600_raw.h5"

# Starting from step 2
BLOCK_COUNTS="8"
BLOCK_RUNS=$((BLOCK_COUNTS**3))
ROOT_OUT="/n/coxfs01/thejohnhoffer/R0/$EXAMPLE/meshes"

# Starting from step 3
ID_LIST="3497592 3497541"
# The number of the ids in the list
NUMBER_TOP=`wc -w <<< $ID_LIST`
ID_LIST=${ID_LIST// /:}

# Starting from step 4
WWW_IN="/n/coxfs01/thejohnhoffer/2017/3dxp/X3DOM/www"

# Starting from step 5
INDEX_NAME="1_synapse.html"

# Load the virtual environment
source new-modules.sh
module load python/2.7.11-fasrc01
conda create -n h5_tile --clone="$PYTHON_HOME"
source activate h5_tile
# Build the virtual environment
conda remove scikit-image
pip install scikit-image
pip install --upgrade h5py
pip install --upgrade numpy
pip install --upgrade scipy
pip install --upgrade mahotas
pip install --upgrade tifffile
pip install --upgrade numpy-stl
pip install --upgrade opencv-python

# Make important directories
mkdir -p $ROOT_IN
mkdir -p $ROOT_OUT

# Run one of the steps
case "$1" in

0) sbatch -o /n/coxfs01/thejohnhoffer/tiff_lists/ids_%a.out -e /n/coxfs01/thejohnhoffer/tiff_lists/ids_%a.err --export=WORKING_DIR=$WORKING_DIR,N_DOWNSAMPLE_XY=$IDS_DOWNSAMPLE_XY,N_DOWNSAMPLE_Z=$IDS_DOWNSAMPLE_Z,RUNS=$RUNS,IN_JSON=$IDS_JSON,OUT_TIF=$IDS_TIF --array=0-$((RUNS - 1)) scale_tif.sbatch
   sbatch -o /n/coxfs01/thejohnhoffer/tiff_lists/raw_%a.out -e /n/coxfs01/thejohnhoffer/tiff_lists/raw_%a.err --export=WORKING_DIR=$WORKING_DIR,N_DOWNSAMPLE_XY=$RAW_DOWNSAMPLE_XY,N_DOWNSAMPLE_Z=$RAW_DOWNSAMPLE_Z,RUNS=$RUNS,IN_JSON=$RAW_JSON,OUT_PNG=$RAW_PNG --array=0-$((RUNS - 1)) scale_png.sbatch
   ;;

1) python png2hd.py $RAW_PNG $RAW_H5
   python tif2hd.py $IDS_TIF $IDS_H5
   ;;

2) python all_counts.py -b $BLOCK_COUNTS $IDS_H5 $ROOT_OUT
   ;;

3) sbatch --export=WORKING_DIR=$WORKING_DIR,ID_LIST=$ID_LIST,BLOCK_COUNTS=$BLOCK_COUNTS,IDS_H5=$IDS_H5,ROOT_OUT=$ROOT_OUT --array=0-$((BLOCK_RUNS - 1)) multi_stl.sbatch
   ;;

4) sbatch --export=WORKING_DIR=$WORKING_DIR,ID_LIST=$ID_LIST,WWW_IN=$WWW_IN,RAW_H5=$RAW_H5,RAW_PNG=$RAW_PNG,ROOT_OUT=$ROOT_OUT --array=0-$((NUMBER_TOP - 1)) multi_x3d.sbatch
   ;;

*) python all_index.py -f $INDEX_NAME -l $ID_LIST $ROOT_OUT
   ;;

esac

