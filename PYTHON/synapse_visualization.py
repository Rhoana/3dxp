
# coding: utf-8

# In[2]:

import json
import sys

sys.path.append('PYTHON')

from threed import ThreeD


# In[ ]:

X3DFOLDER = '/media/SPEED/X3D/ids-2017-05-11/ids-2z-3xy/mesh-8xyz/x3d/'


# In[4]:

with open('/tmp/syn.json', 'r') as f:
    pairs = json.load(f)


# In[6]:

for p in pairs:
    
    n1 = p[0]
    n2 = p[1]
    
    index_file = 'synapse_'+str(n1)+'x'+str(n2)+'.html'
    
    ThreeD.merge_website(X3DFOLDER, index_file, p)
    


# In[ ]:



