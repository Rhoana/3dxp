import os
import sys
from toMesh import smoothmesh
from toMesh import threshbound
from toMesh import countlabels

OUT_FOLDER = sys.argv[1]
#DATA_C = '/n/coxfs01/leek/results/ECS_iarpa_20u_cube/segmentation.h5'
#DATA_J = '/home/harvard/2017/data/bf/1017/synapse.h5'
DATA_J = '/home/d/data/toufiq/segmentation.h5'
MAX_COUNT = 10

VOL = {
    'maxz': 10,
    'given': DATA_J
}
id_set = countlabels(**VOL) - set([0])
max_id = min(MAX_COUNT or len(id_set), len(id_set))

for labid in sorted(id_set)[:max_id]:
    OUTNAME = os.path.join(OUT_FOLDER,str(labid)+'_mesh.stl')
    volume, offset = threshbound(id=labid, **VOL)
    smoothmesh(volume, OUTNAME, offset)
    print('Saved id '+str(labid)+'\n')
