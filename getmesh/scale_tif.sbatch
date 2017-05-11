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

source new-modules.sh
module load python/2.7.11-fasrc01
source activate h5_tile

# we are working
cd $WORKING_DIR
python -u tiff_lists/tiff2tiff.py ${IN_JSON} ${SLURM_ARRAY_TASK_ID} -r ${RUNS} -o ${OUT_TIF} -n ${N_DOWNSAMPLE_XY} -z ${N_DOWNSAMPLE_Z}

# end of program
exit 0;
