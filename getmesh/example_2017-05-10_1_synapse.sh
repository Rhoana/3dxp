#!/bin/bash

# Starting from step 0
EXAMPLE="2017_05_10_844z"
ROOT_IN="/n/coxfs01/thejohnhoffer/R0/$EXAMPLE/images"
WORKING_DIR="/n/coxfs01/thejohnhoffer/2017/3dxp/getmesh"
IDS_JSON="/n/coxfs01/leek/results/2017-05-05_R0/boss/boss.json"
RAW_JSON="/n/coxfs01/leek/dropbox/25k_201610_dataset_em.json"
IDS_TIF=$ROOT_IN"/3200_3200_ids"
RAW_JPG=$ROOT_IN"/1600_1600_raw"
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
IDS_LIST="67 151"
# The number of the ids in the list
NUMBER_TOP=`wc -w <<< $IDS_LIST`
IDS_LIST=${IDS_LIST// /:}

# Starting from step 4
WWW_IN="/n/coxfs01/thejohnhoffer/2017/3dxp/X3DOM/www"
RAW_RATIO="$RAW_DOWNSAMPLE_Z:$RAW_DOWNSAMPLE_XY"
IDS_RATIO="$IDS_DOWNSAMPLE_Z:$IDS_DOWNSAMPLE_XY"
VOXEL_RATIO="7.5"

# Starting from step 5
INDEX_NAME="synapse_151-67.html"

# Load the virtual environment
source new-modules.sh
module load python/2.7.11-fasrc01
VENV_NAME="h5_tile"

# Check if the virtual environment exists
VENV_INFO=`conda env list | grep "$VENV_NAME"`
# Make environment if does not exist
if [ -z "$VENV_INFO" ]; then
    echo "Making virtual environment $VENV_NAME"
    conda create -n $VENV_NAME --clone="$PYTHON_HOME"
    source activate $VENV_NAME
    # Build the virtual environment
    conda remove scikit-image
    pip install -r requirements.txt
# Source environment if exists
else
    echo "Loading virtual environment $VENV_NAME"
    source activate $VENV_NAME
fi

# Make important directories
mkdir -p $ROOT_IN
mkdir -p $ROOT_OUT

# Run one of the steps
case "$1" in

0) sbatch -o /n/coxfs01/thejohnhoffer/tiff_lists/ids_%a.out -e /n/coxfs01/thejohnhoffer/tiff_lists/ids_%a.err --export=WORKING_DIR=$WORKING_DIR,N_DOWNSAMPLE_XY=$IDS_DOWNSAMPLE_XY,N_DOWNSAMPLE_Z=$IDS_DOWNSAMPLE_Z,RUNS=$RUNS,IN_JSON=$IDS_JSON,OUT_TIF=$IDS_TIF --array=0-$((RUNS - 1)) scale_tif.sbatch
   sbatch -o /n/coxfs01/thejohnhoffer/tiff_lists/raw_%a.out -e /n/coxfs01/thejohnhoffer/tiff_lists/raw_%a.err --export=WORKING_DIR=$WORKING_DIR,N_DOWNSAMPLE_XY=$RAW_DOWNSAMPLE_XY,N_DOWNSAMPLE_Z=$RAW_DOWNSAMPLE_Z,RUNS=$RUNS,IN_JSON=$RAW_JSON,OUT_JPG=$RAW_JPG --array=0-$((RUNS - 1)) scale_jpg.sbatch
   ;;

1) python h5_writers/jpg2hd.py $RAW_JPG $RAW_H5
   python h5_writers/tif2hd.py $IDS_TIF $IDS_H5
   ;;

2) python all_counts.py -b $BLOCK_COUNTS $IDS_H5 $ROOT_OUT
   ;;

3) sbatch --export=WORKING_DIR=$WORKING_DIR,IDS_LIST=$IDS_LIST,BLOCK_COUNTS=$BLOCK_COUNTS,IDS_H5=$IDS_H5,ROOT_OUT=$ROOT_OUT --array=0-$((BLOCK_RUNS - 1)) multi_stl.sbatch
   ;;

4) sbatch --export=WORKING_DIR=$WORKING_DIR,RAW_RATIO=$RAW_RATIO,IDS_RATIO=$IDS_RATIO,VOXEL_RATIO=$VOXEL_RATIO,IDS_LIST=$IDS_LIST,WWW_IN=$WWW_IN,RAW_H5=$RAW_H5,RAW_JPG=$RAW_JPG,ROOT_OUT=$ROOT_OUT --array=0-$((NUMBER_TOP - 1)) multi_x3d.sbatch
   ;;

*) python all_index.py -f $INDEX_NAME -l $IDS_LIST $ROOT_OUT
   ;;

esac

