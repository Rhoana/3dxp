#!/bin/bash

# Starting from step 0
EXAMPLE="ids-2017-05-11_ids-2z-3xy_mesh-8xyz"
ROOT_IN="/n/coxfs01/thejohnhoffer/R0/$EXAMPLE/images"
LOG_OUT="/n/coxfs01/thejohnhoffer/logging"
WORKING_DIR="/n/coxfs01/thejohnhoffer/2017/3dxp/PYTHON"
IDS_JSON="/n/coxfs01/leek/results/2017-05-11_R0/boss/boss.json"
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
NUMBER_TOP="20"
RANK_Z="1"

# Starting from step 4
WWW_IN="/n/coxfs01/thejohnhoffer/2017/3dxp/WWW"
RAW_RATIO="$RAW_DOWNSAMPLE_Z:$RAW_DOWNSAMPLE_XY"
IDS_RATIO="$IDS_DOWNSAMPLE_Z:$IDS_DOWNSAMPLE_XY"
VOXEL_RATIO="7.5"

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
    conda remove scikit-image
    pip install -r requirements.txt
fi

# Make main directories
mkdir -p $ROOT_IN
mkdir -p $ROOT_OUT

# Make log directories
mkdir -p "$LOG_OUT/scale_img"
mkdir -p "$LOG_OUT/all_stl"
mkdir -p "$LOG_OUT/all_x3d"
mkdir -p "$LOG_OUT/simple"

# Get start and stop of range
START=${1:-0}
STOP=${2:-5}
# STOP equals start if one argument
if [ ! -z $1 ] && [ -z $2 ]; then
    STOP=$START
fi
echo "Steps from $START through $STOP:"

for STEP in $(seq $START $STOP); do
    # Run one of the steps
    case "$STEP" in

    0) 
        echo "0A) Will downsample original tiff ids to a tiff stack..." 
        echo "0B) Will downsample original png raw images to a jpg stack..." 

        LOGS_0A="-o $LOG_OUT/scale_img/ids_%a.out -e $LOG_OUT/scale_img/ids_%a.err"
        ARGS_0A="-f tif -r $RUNS -n $IDS_DOWNSAMPLE_XY -z $IDS_DOWNSAMPLE_Z -o $IDS_TIF $IDS_JSON"
        J0A=$(sbatch $LOGS_0A -D $WORKING_DIR --export="ARGUMENTS=$ARGS_0A" --array=0-$((RUNS - 1)) scale_img.sbatch)

        LOGS_0B="-o $LOG_OUT/scale_img/raw_%a.out -e $LOG_OUT/scale_img/raw_%a.err"
        ARGS_0B="-f jpg -r $RUNS -n $RAW_DOWNSAMPLE_XY -z $RAW_DOWNSAMPLE_Z -o $RAW_JPG $RAW_JSON"
        J0B=$(sbatch $LOGS_0B -D $WORKING_DIR --export="ARGUMENTS=$ARGS_0B" --array=0-$((RUNS - 1)) scale_img.sbatch)
        
        echo "... $J0A and $J0B ..."
        J0A=${J0A//[^0-9]}
        J0B=${J0B//[^0-9]}
        ;;

    1)  
        echo "1A) Will convert ids tiff stack to an hdf5 file..."
        echo "1B) Will convert raw jpg stack to an hdf5 file..."
        # Calculate dependencies if needed
        if [ "$START" -lt "1" ]; then
            echo "... both after 0A) and 0B) finish."
            DEP_1A="--dependency=afterok:$J0A"
            DEP_1B="--dependency=afterok:$J0B"
        fi

        CALL_1A="python -u h5_writers/tif2hd.py $IDS_TIF $IDS_H5"
        LOGS_1A="-o $LOG_OUT/simple/ids_0.out -e $LOG_OUT/simple/ids_0.err"
        J1A=$(sbatch $LOGS_1A $DEP_1A -D $WORKING_DIR --export="FUNCTION_CALL=$CALL_1A" simple.sbatch)

        CALL_1B="python -u h5_writers/jpg2hd.py $RAW_JPG $RAW_H5"
        LOGS_1B="-o $LOG_OUT/simple/raw_0.out -e $LOG_OUT/simple/raw_0.err"
        J1B=$(sbatch $LOGS_1B $DEP_1B -D $WORKING_DIR --export="FUNCTION_CALL=$CALL_1B" simple.sbatch)

        echo "... $J1A and $J1B ..."
        J1A=${J1A//[^0-9]}
        J1B=${J1B//[^0-9]}
        ;;

    2) 
        echo "2A) Will count the biggest in the ids hdf5 file..."
        echo "2B) Will count the deepest in the ids hdf5 file..."
        # Calculate dependencies if needed
        if [ "$START" -lt "2" ]; then
            echo "... both after 1A) finishes."
            DEP_2A="--dependency=afterok:$J1A"
            DEP_2B="--dependency=afterok:$J1A"
        fi

        CALL_2A="python -u all_counts.py -d 0 -b $BLOCK_COUNTS $IDS_H5 $ROOT_OUT"
        LOGS_2A="-o $LOG_OUT/simple/big_0.out -e $LOG_OUT/simple/big_0.err"
        J2A=$(sbatch $LOGS_2A $DEP_2A -D $WORKING_DIR --export="FUNCTION_CALL=$CALL_2A" simple.sbatch)

        CALL_2B="python -u all_counts.py -d 1 -b $BLOCK_COUNTS $IDS_H5 $ROOT_OUT"
        LOGS_2B="-o $LOG_OUT/simple/deep_0.out -e $LOG_OUT/simple/deep_0.err"
        J2B=$(sbatch $LOGS_2B $DEP_2B -D $WORKING_DIR --export="FUNCTION_CALL=$CALL_2B" simple.sbatch)

        echo "... $J2A and $J2B..."
        J2A=${J2A//[^0-9]}
        J2B=${J2B//[^0-9]}
        ;;

    3) 
        echo "3A) Will convert all top $NUMBER_TOP ids to stl mesh files..."
        # Calculate dependencies if needed
        if [ "$START" -lt "3" ]; then
            echo "... after 2A) and 2B) finish."
            DEP_3A="--dependency=afterok:$J2A:$J2B"
        fi

        ARGS_3A="-d $RANK_Z -b $BLOCK_COUNTS -n $NUMBER_TOP $IDS_H5 $ROOT_OUT"
        LOGS_3A="-o $LOG_OUT/all_stl/top_%a.out -e $LOG_OUT/all_stl/top_%a.err"
        J3A=$(sbatch $LOGS_3A $DEP_3A -D $WORKING_DIR --export="ARGUMENTS=$ARGS_3A" --array=0-$((BLOCK_RUNS - 1)) all_stl.sbatch)

        echo "... $J3A ..."
        J3A=${J3A//[^0-9]}
        ;;

    4) 
        echo "4A) Will convert all top $NUMBER_TOP ids to x3d HTML files..."
        # Calculate dependencies if needed
        if [ "$START" -lt "2" ]; then
            echo "... after 1B) and 3A) finish."
            DEP_4A="--dependency=afterok:$J1B:$J3A"
        elif [ "$START" -lt "4" ]; then
            echo "... after 3A) finishes."
            DEP_4A="--dependency=afterok:$J3A"
        fi

        LOGS_4A="-o $LOG_OUT/all_x3d/top_%a.out -e $LOG_OUT/all_x3d/top_%a.err"
        ARGS_4A="-V $VOXEL_RATIO -R $RAW_RATIO -I $IDS_RATIO -d $RANK_Z -n $NUMBER_TOP -w $WWW_IN $RAW_H5 $RAW_JPG $ROOT_OUT"
        J4A=$(sbatch $LOGS_4A $DEP_4A -D $WORKING_DIR --export="ARGUMENTS=$ARGS_4A" --array=0-$((NUMBER_TOP - 1)) all_x3d.sbatch)

        echo "... $J4A ..."
        J4A=${J4A//[^0-9]}
        ;;

    5) 
        echo "5A) Will merge all top $NUMBER_TOP x3d HTML files..."
        # Calculate dependencies if needed
        if [ "$START" -lt "5" ]; then
            echo "... after 4A) finishes."
            DEP_5A="--dependency=afterok:$J4A"
        fi

        CALL_5A="python all_index.py $ROOT_OUT"
        LOGS_5A="-o $LOG_OUT/simple/merge_0.out -e $LOG_OUT/simple/merge_0.err"
        J5A=$(sbatch $LOGS_5A $DEP_5A -D $WORKING_DIR --export="FUNCTION_CALL=$CALL_5A" simple.sbatch)

        echo "... $J5A ..."
        J5A=${J5A//[^0-9]}
        ;;

    0) echo ""

    esac
done