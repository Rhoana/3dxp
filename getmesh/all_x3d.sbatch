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

# LOAD AOPT
source /n/coxfs01/apps/instantreality/setup.sh

echo "python -u all_x3d.py -t $SLURM_ARRAY_TASK_ID $ARGUMENTS"
python -u all_x3d.py -t $SLURM_ARRAY_TASK_ID $ARGUMENTS

# end of program
exit 0;
