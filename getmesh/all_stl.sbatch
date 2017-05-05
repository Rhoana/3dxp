#!/bin/bash
#
# add all other SBATCH directives here...
#
#SBATCH -p holyseasgpu
#SBATCH -n 1 # Number of cores
#SBATCH -N 1 # Ensure that all cores are on one machine
#SBATCH --mem=16000
#SBATCH -t 10-12:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=john@hoff.in
#SBATCH -o /n/coxfs01/thejohnhoffer/all_stl/all_stl_%a.out
#SBATCH -e /n/coxfs01/thejohnhoffer/all_stl/all_stl_%a.err

source new-modules.sh
module load python/2.7.11-fasrc01
conda create -n h5_tile --clone="$PYTHON_HOME"
source activate h5_tile
pip install --upgrade numpy
pip install --upgrade h5py
pip install --upgrade scipy
pip install --upgrade mahotas
pip install --upgrade numpy-stl
pip install --upgrade opencv-python
pip install --upgrade scikit-image

# we are working
cd $WORKING_DIR
python all_stl.py -t $SLURM_ARRAY_TASK_ID -d $RANK_Z -b $BLOCK_COUNTS -n $NUMBER_TOP $IDS_IN $ROOT_OUT

# end of program
exit 0;
