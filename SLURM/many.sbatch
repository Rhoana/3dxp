#!/bin/bash
#
# add all other SBATCH directives here...
#
#SBATCH -p cox
#SBATCH -n 1 # Number of cores
#SBATCH -N 1 # Ensure that all cores are on one machine
#SBATCH --mem=16000
#SBATCH -t 3-12:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=john@hoff.in

source new-modules.sh
module load python/2.7.11-fasrc01
source activate 3DXP

# we are working
RUNNING="python -u $PYTHON $ARGS -t $SLURM_ARRAY_TASK_ID"
echo $RUNNING
time $RUNNING

# end of program
exit 0;
