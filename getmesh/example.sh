#!/bin/bash

export ROOT_IN="~/2017/data/3dxp/2017-04-19_R2B1V3"
export ROOT_OUT="~/2017/winter/3dxp/X3DOM/2017-04-19_R2B1V3"
export WORKING_DIR="/n/coxfs01/thejohnhoffer/2017/butterfly/scripts/tiff_lists"
export IDS_IN=$ROOT_IN"/neurons.h5"

export RANK_Z="1"
export NUMBER_TOP="8"
export BLOCK_COUNTS="10"
BLOCK_RUNS=$((BLOCK_COUNTS**3 - 1))

python all_counts.py -b $BLOCK_COUNTS $IDS_IN $ROOT_OUT

sbatch --array=0-$BLOCK_RUNS all_stl.sbatch

WWW_IN="~/2017/winter/3dxp/X3DOM/www"
RAW_H5=$ROOT_IN"/neurons.h5"
RAW_PNG=$ROOT_IN"/neurons"

#python all_x3d.py -d $RANK_Z -n $NUMBER_TOP -w $WWW_IN $RAW_H5 $RAW_PNG $ROOT_OUT


