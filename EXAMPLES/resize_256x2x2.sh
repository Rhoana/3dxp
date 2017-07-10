#!/bin/bash

# Number of jobs at once
SYNC=32

# Starting from step 0
ROOT_IN="/n/coxfs01/thejohnhoffer/R0/images"
LOG_OUT="/n/coxfs01/thejohnhoffer/logging"
WORKING_DIR="/n/coxfs01/thejohnhoffer/2017/3dxp/PYTHON"
RAW_JSON="/n/coxfs01/leek/dropbox/25k_201610_dataset_em.json"
RAW_JPG=$ROOT_IN"/256_2_2_raw"
RAW_DOWNSAMPLE_XY=1
RAW_DOWNSAMPLE_Z=8
RUNS=8

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

# Make log directories
KLOG="scale"
mkdir -p "$LOG_OUT/scale_img"

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
        echo "0B) Will downsample original png raw images to a jpg stack..." 

        LOGS_0B="-o $LOG_OUT/scale_img/${KLOG}_raw_%a.out -e $LOG_OUT/scale_img/${KLOG}_raw_%a.err"
        ARGS_0B="-f jpg -r $RUNS -n $RAW_DOWNSAMPLE_XY -z $RAW_DOWNSAMPLE_Z -o $RAW_JPG $RAW_JSON"
        J0B=$(sbatch $LOGS_0B -D $WORKING_DIR --export="ARGUMENTS=$ARGS_0B" --array=0-$((RUNS - 1))%$SYNC scale_img.sbatch)
        
        echo "... $J0B ..."
        J0B=${J0B//[^0-9]}
        ;;

    esac
done

