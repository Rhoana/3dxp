
# coding: utf-8

# In[2]:

import json
import sys

from threed import ThreeD

# In[ ]:

X3DFOLDER = '/n/coxfs01/thejohnhoffer/R0/ids-2017-05-11_ids-2z-3xy_mesh-8xyz/meshes/x3d'
SYNFOLDER = '/n/coxfs01/thejohnhoffer/R0/ids-2017-05-11_ids-2z-3xy_mesh-8xyz/meshes/37_synapses.json'

# In[4]:

with open(SYNFOLDER, 'r') as f:
    pairs = json.load(f)


# In[6]:

for p in pairs:
    
    n1 = p[0]
    n2 = p[1]
    
    index_file = 'synapse_'+str(n1)+'x'+str(n2)+'.html'
    
    ThreeD.merge_website(X3DFOLDER, index_file, p)
    

