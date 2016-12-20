import os
import sys
from toMesh import smoothmesh
from toMesh import threshbound

OUT_FOLDER = sys.argv[2]
NEURON_ID = int(sys.argv[1])
OUTNAME = os.path.join(OUT_FOLDER,str(NEURON_ID)+'_mesh.stl')
#DATA_C = '/n/coxfs01/leek/results/ECS_iarpa_20u_cube/segmentation.h5'
#DATA_J = '/home/harvard/2017/data/bf/1017/synapse.h5'
DATA_J = '/home/d/data/toufiq/segmentation.h5'

VOL = {
    'maxz': 10,
    'given': DATA_J,
    'id': NEURON_ID
}

volume, offset = threshbound(**VOL)
smoothmesh(volume, OUTNAME, offset)
print('Saved id '+str(VOL['id'])+'\n')
