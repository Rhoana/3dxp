import os
import sys
from toMesh import smoothmesh
from toMesh import threshbound
from toMesh import countlabels

OUT_FOLDER = sys.argv[1]
OUTNAME = os.path.join(OUT_FOLDER,str(NEURON_ID)+'_mesh.stl')
DATA_C = '/n/coxfs01/leek/results/ECS_iarpa_20u_cube/segmentation.h5'
DATA_J = '/home/harvard/2017/data/bf/1017/synapse.h5'
MAX_COUNT = 10

VOL = {
    'maxz': False,
    'given': DATA_J,
    'id': NEURON_ID
}
id_set = countlabels(**VOL)
max_id = min(MAX_COUNT or len(id_set), len(id_set))

for labid in sorted(id_set)[:max_id]:
    VOL['id'] = labid
    volume, offset = threshbound(**VOL)
    smoothmesh(volume, OUTNAME, offset)
    print('Saved id '+str(VOL['id'])+'\n')
