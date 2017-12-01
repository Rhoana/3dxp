#!/bin/bash
#
# add all other SBATCH directives here...
#
#SBATCH -p cox
#SBATCH -n 1 # Number of cores
#SBATCH -N 1 # Ensure that all cores are on one machine
#SBATCH --mem=1000
#SBATCH -t 0-12:00

source new-modules.sh
module load blender/2.69-fasrc01
export PYTHONDONTWRITEBYTECODE=1

# we are working
BLEND="blender -noaudio -b"
IN_ARRAY="-t $SLURM_ARRAY_TASK_ID -r $SLURM_ARRAY_TASK_COUNT"
RUNNING="$BLEND -P $python -- $args $IN_ARRAY"
echo $RUNNING
time $RUNNING

# end of program
exit 0;
