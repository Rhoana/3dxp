#!/bin/bash

# Starting from step 0
EXAMPLE="R0_mojo_test"
ROOT_IN="/n/coxfs01/haehn/3D/$EXAMPLE/"
LOG_OUT="/n/coxfs01/haehn/3D/logging"
WORKING_DIR="/n/home05/haehn/Projects/3dxp/PYTHON"
IDS_JSON="/n/coxfs01/leek/results/2017-05-11_R0/boss/boss.json"
RAW_JSON="/n/coxfs01/leek/dropbox/25k_201610_dataset_em.json"
IDS_TIF=$ROOT_IN"/ids"
RAW_JPG=$ROOT_IN"/raw"
IDS_DOWNSAMPLE_XY=1
IDS_DOWNSAMPLE_Z=1
RAW_DOWNSAMPLE_XY=1
RAW_DOWNSAMPLE_Z=1
RUNS=200


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
KLOG="top"
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
        echo "0A) Will downsample original tiff ids to a tiff stack..." 

        LOGS_0A="-o $LOG_OUT/scale_img/${KLOG}_ids_%a.out -e $LOG_OUT/scale_img/${KLOG}_ids_%a.err"
        ARGS_0A="-f tif -r $RUNS -n $IDS_DOWNSAMPLE_XY -z $IDS_DOWNSAMPLE_Z -o $IDS_TIF $IDS_JSON"
        J0A=$(sbatch $LOGS_0A -D $WORKING_DIR --export="ARGUMENTS=$ARGS_0A" --array=0-$((RUNS - 1)) scale_img.sbatch)

        J0A=${J0A//[^0-9]}
        ;;

    *) echo ""

    esac
done
