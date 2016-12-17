#!/bin/bash
#
# add all other SBATCH directives here...
#
#SBATCH -p cox
#SBATCH -n 1 # Number of cores
#SBATCH -N 1 # Ensure that all cores are on one machine #SBITCH --gres=gpu
#SBATCH --mem=100000
#SBATCH -t 10-12:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=john@hoff.in
#SBATCH -o /n/home08/thejohnhoffer/SLURM/out-mesh-h5.txt
#SBATCH -e /n/home08/thejohnhoffer/SLURM/err-mesh-h5.txt

source new-modules.sh
module load Anaconda/2.5.0-fasrc01
module load gcc/4.9.0-fasrc01

#module load cuda/7.5-fasrc01
#module load cudnn/7.0-fasrc01

#module load opencv/3.0.0-fasrc04

# custom HDF5 lib
#export LIBRARY_PATH=/n/home05/haehn/nolearncox/src/hdf5-1.8.17/hdf5/lib:$LIBRARY_PATH
#export LD_LIBRARY_PATH=/n/home05/haehn/nolearncox/src/hdf5-1.8.17/hdf5/lib:$LD_LIBRARY_PATH
#export CPATH=/n/home05/haehn/nolearncox/src/hdf5-1.8.17/hdf5/include:$CPATH
#export FPATH=/n/home05/haehn/nolearncox/src/hdf5-1.8.17/hdf5/include:$FPATH

source /n/home08/thejohnhoffer/venv/mesh/bin/activate


# we are working in TEMP
cd /n/home08/thejohnhoffer/2017/winter/3dxp/
python mesh_h5.py 18915 /n/home08/thejohnhoffer/2017/data/stl/

# end of program
exit 0;

