#!/bin/bash

# Number of jobs at once
SYNC=32
RUNS=32

# Root level logging and workign path names
LOG_OUT="/n/coxfs01/thejohnhoffer/logging"
WORKING_DIR="/n/coxfs01/thejohnhoffer/2017/3dxp/PYTHON"

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

# Make log directories
KLOG="all"
mkdir -p "$LOG_OUT/move_folders"

echo "0A) Will move stl files to folders..." 

ARGS_0A="-r $RUNS"
LOGS_0A="-o $LOG_OUT/move_folders/${KLOG}_%a.out -e $LOG_OUT/move_folders/${KLOG}_%a.err"
J0A=$(sbatch $LOGS_0A -D $WORKING_DIR --export="ARGUMENTS=$ARGS_0A" --array=0-$((RUNS - 1))%$SYNC move_folders.sbatch)

echo "... $J0A ..."

