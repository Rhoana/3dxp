#!/bin/bash
#
# add all other SBATCH directives here...
#
#SBATCH -p cox
#SBATCH -n 1 # Number of cores
#SBATCH -N 1 # Ensure that all cores are on one machine #SBITCH --gres=gpu
#SBATCH --mem=10000#6720
#SBATCH -t 10-12:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=haehn@seas.harvard.edu
#SBATCH -o /n/home05/haehn/SLURM/out-mesh-2-11-24.txt
#SBATCH -e /n/home05/haehn/SLURM/err-mesh-2-11-24.txt

source new-modules.sh
module load Anaconda/2.5.0-fasrc01
module load gcc/4.9.0-fasrc01

# custom HDF5 lib
export LIBRARY_PATH=/n/home05/haehn/nolearncox/src/hdf5-1.8.17/hdf5/lib:$LIBRARY_PATH
export LD_LIBRARY_PATH=/n/home05/haehn/nolearncox/src/hdf5-1.8.17/hdf5/lib:$LD_LIBRARY_PATH
export CPATH=/n/home05/haehn/nolearncox/src/hdf5-1.8.17/hdf5/include:$CPATH
export FPATH=/n/home05/haehn/nolearncox/src/hdf5-1.8.17/hdf5/include:$FPATH

source /n/home05/haehn/nolearncox/bin/activate


cd /n/home05/haehn/Projects/3dxp/
python threed.py /n/coxfs01/leek/results/ECS_iarpa_20u_cube/segmentation.h5 2 11 24 /n/coxfs01/haehn/STLs/

# end of program
exit 0;
