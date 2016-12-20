import h5py
import numpy as np

class Label:
    labels = set()
    def __init__(self, **words):
        self.maxz = words.get('maxz',0)
        given = words.get('given','in.h5')
        with h5py.File(given,'r') as giv:
            self.load_h5(giv)

    def load_h5(self, f):
        volstack = f[f.keys()[0]]
        z,y,x = volstack.shape
        maxz = self.maxz or z
        z = min(z, maxz)
        self.maxz = z

        for z_slice in range(z):
            self.labels = self.labels | set(np.unique(volstack[z_slice]))

def countlabels(**kwargs):
    print('Counting ids')
    labeled = Label(**kwargs)
    labels = labeled.labels
    count,highest = [len(labels),max(labels)+1]
    print(str(count)+' ids under '+str(highest))
    return labels

