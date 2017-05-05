import os, h5py
import numpy as np
from threed import ThreeD

HOME = os.path.expanduser('~')
DATA = HOME + '/2017/data/bf/jan_push/8x_downsampled_segmentation.h5'
DATA = '/n/coxfs01/leek/results/ECS_iarpa_20u_cube/segmentation.h5'
ROOTDIR = HOME + '/2017/data/3dxp/jan_push/'
STLFOLDER = ROOTDIR + 'stl'
X3DFOLDER = ROOTDIR + 'x3d'
ALL_IDS = [ 49146, 49266, 50513, 51536, 54306, 68584, 81359, 91293, 114967, 117847, 123959, 151877, 163906]
INDEX = 'toufiq.html'
NTILES = 4

with h5py.File(DATA, 'r') as df:
    MAXSIZE = np.max(df[df.keys()[0]].shape)
    TILESIZE = MAXSIZE // NTILES

subvols = zip(*np.where(np.ones([NTILES]*3)))

for z,y,x in subvols:
    ThreeD.run(DATA, z, y, x, STLFOLDER, TILESIZE, ALL_IDS)

ThreeD.create_website(STLFOLDER, X3DFOLDER, ALL_IDS, INDEX)

LOCAL_DATA = '/home/d/data/toufiq/segmentation.h5'
CLUSTER_DATA = '/n/coxfs01/leek/results/ECS_iarpa_20u_cube/segmentation.h5'
CLUSTER_STL_OUTPUT = '/n/coxfs01/haehn/STLs/'
TILEWIDTH = 200
with h5py.File(LOCAL_DATA, 'r') as f:
    shape = f[f.keys()[0]].shape
# assume X,Y equal right now
tiles_Z = range(int(round(shape[0]) / float(TILEWIDTH)))
tiles_Y = range(int(round(shape[1] / float(TILEWIDTH))))
tiles_X = range(int(round(shape[2] / float(TILEWIDTH))))
# we assume the following memory
bytes = TILEWIDTH * TILEWIDTH * shape[0] * 8
print 'MB', bytes / 1000000
# and we take 4 times as large just to be safe
# OOOPS we need more.. let's try 10*
memory = 30 * bytes / 1000000
# SLURM TEMPLATE
t = '''#!/bin/bash
#
# add all other SBATCH directives here...
#
#SBATCH -p cox
#SBATCH -n 1 # Number of cores
#SBATCH -N 1 # Ensure that all cores are on one machine #SBITCH --gres=gpu
#SBATCH --mem=10000#{MEMORY}
#SBATCH -t 10-12:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=haehn@seas.harvard.edu
#SBATCH -o /n/home05/haehn/SLURM/out-mesh-{Z}-{Y}-{X}.txt
#SBATCH -e /n/home05/haehn/SLURM/err-mesh-{Z}-{Y}-{X}.txt

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
python threed.py {DATAPATH} {Z} {Y} {X} {OUTPUTPATH}

# end of program
exit 0;
'''
for Z in tiles_Z:
    for Y in tiles_Y:
        for X in tiles_X:

            t2 = t.replace('{MEMORY}', str(memory))
            t2 = t2.replace('{DATAPATH}', str(CLUSTER_DATA))
            t2 = t2.replace('{X}', str(X))
            t2 = t2.replace('{Y}', str(Y))
            t2 = t2.replace('{Z}', str(Z))
            t2 = t2.replace('{OUTPUTPATH}', str(CLUSTER_STL_OUTPUT))        

            with open('SLURM/mesh-'+str(Z)+'-'+str(Y)+'-'+str(X)+'.slurm', 'w') as f:
                f.write(t2)
# LAUNCH ALL SLURMS WITH
# for f in *.slurm; do sbatch $f; done
memory
