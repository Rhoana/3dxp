#!/bin/bash
#
# add all other SBATCH directives here...
#
#SBATCH -p holyseasgpu
#SBATCH -n 1 # Number of cores
#SBATCH -N 1 # Ensure that all cores are on one machine
#SBATCH --mem=8000
#SBATCH -t 1-12:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=john@hoff.in
#SBATCH -o /n/coxfs01/thejohnhoffer/all_stl/all_stl_%a.out
#SBATCH -e /n/coxfs01/thejohnhoffer/all_stl/all_stl_%a.err

source new-modules.sh
module load python/2.7.11-fasrc01
source activate h5_tile

# we are working
cd $WORKING_DIR
echo "Working ${WORKING_DIR}"
echo "From ${IDS_H5} to ${ROOT_OUT}"
python -u all_stl.py -t $SLURM_ARRAY_TASK_ID -d $RANK_Z -b $BLOCK_COUNTS -n $NUMBER_TOP $IDS_H5 $ROOT_OUT

# end of program
exit 0;
