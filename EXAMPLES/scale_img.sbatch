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
#SBATCH --mail-user=haehn@seas.harvard.edu

source new-modules.sh
module load python/2.7.11-fasrc01
source activate h5_tile

# we are working
echo "python -u tiff_lists/tiffScale.py -t $SLURM_ARRAY_TASK_ID $ARGUMENTS"
time python -u tiff_lists/tiffScale.py -t $SLURM_ARRAY_TASK_ID $ARGUMENTS

# end of program
exit 0;
