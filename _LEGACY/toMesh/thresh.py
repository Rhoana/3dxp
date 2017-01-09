import h5py
import numpy as np

class Thresh:
    def __init__(self, neuro_id, **words):
        self.id = neuro_id
        self.maxz = words.get('maxz',0)
        self.margin = words.get('margin',2)
        self.upsamp = words.get('upsamp',10)
        given = words.get('given','in.h5')
        with h5py.File(given,'r') as giv:
            self.bitvolume, self.bounds = self.load_h5(giv)

    def load_h5(self, f):
        upsamp = self.upsamp
        volstack = f[f.keys()[0]]
        z,y,x = volstack.shape
        maxz = self.maxz or z
        z = min(z, maxz)
        self.maxz = z

        bitvolume = np.zeros([upsamp*z,y,x], dtype=np.bool)
        box_tl,box_br = [[y,x],[0,0]]
        box_up,box_dn = [-1,-1]

        for z_slice in range(z):
            za,zb = [upsamp*i for i in [z_slice,z_slice+1]]
            thresholded = self.threshold(volstack[z_slice], self.id)
            bitvolume[za:zb] = thresholded

            if thresholded.any():
                extent = np.argwhere(thresholded)
                box_tl = np.c_[extent.min(0),box_tl].min(1)
                box_br = np.c_[extent.max(0),box_br].max(1)
                box_dn = za if box_dn < 0 else box_dn
                box_up = zb

        bounds = [[box_dn,box_up], box_tl, box_br]
        return [bitvolume, bounds]

    def threshold(self, arr, val):
        out = np.ones(arr.shape, dtype=arr.dtype)*val
        return np.equal(arr,out)

    def bound(self):
        bitvolume = self.bitvolume
        box_ud, box_tl, box_br = self.bounds
        zo,ze = box_ud
        yo,xo = box_tl
        ye,xe = box_br
        volume = bitvolume[zo:ze, yo:ye, xo:xe].swapaxes(0,1)
        vy,vz,vx = volume.shape

        margin_z = [vy,self.margin,vx]
        margin_x = [vy,vz+2*self.margin,self.margin]
        bound_offset = (yo, zo-self.margin, xo-self.margin)
        z_margin = np.zeros(margin_z, dtype=bool)
        x_margin = np.zeros(margin_x, dtype=bool)

        volume = np.concatenate((z_margin,volume,z_margin),axis=1)
        volume = np.concatenate((x_margin,volume,x_margin),axis=2)
        return [volume, bound_offset]

def threshbound(**kwargs):
    neuro_id = kwargs.get('id',1)
    print('Threshing id '+str(neuro_id))
    threshy = Thresh(neuro_id, **kwargs)
    return threshy.bound()
