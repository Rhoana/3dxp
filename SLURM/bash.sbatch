#!/bin/bash
#
# add all other SBATCH directives here...
#
#SBATCH -p cox
#SBATCH -n 1 # Number of cores
#SBATCH -N 1 # Ensure that all cores are on one machine
#SBATCH --mem=16000
#SBATCH -t 3-12:00

# we are working
RUNNING="$args"
echo $RUNNING
time $RUNNING

# end of program
exit 0;
