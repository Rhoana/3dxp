#!/bin/bash
#
# add all other SBATCH directives here...
#
#SBATCH -p cox
#SBATCH -n 1 # Number of cores
#SBATCH -N 1 # Ensure that all cores are on one machine
#SBATCH --mem=16000
#SBATCH -t 3-12:00

source new-modules.sh
module load python/2.7.11-fasrc01
source activate 3DXP

if [ -z "$z_start" ]; then
    z_start="0"
fi
# we are working
z_slice=$((z_start + SLURM_ARRAY_TASK_ID))
RUNNING="python -u $python $args -z $z_slice"
echo $RUNNING
time $RUNNING

# end of program
exit 0;
