import numpy as np
import os, h5py

def sort(counts):
    keysort = np.argsort(counts).astype(np.uint32)
    return [keysort, counts[keysort]]

def main(_data, _out, _block):
    """
    Arguments
    ----------
    _data: str
        Path to the input h5 file
    _out: str
        Path to save output text files
    _block: int
        The number of blocks in each dimension
    """

    COUNTS = np.array([],dtype=np.uint32)

    if os.path.exists(_out):
        print('loading depth count from file')
        COUNTS = np.loadtxt(_out,dtype=np.uint32)
        return sort(COUNTS)

    with h5py.File(_data, 'r') as df:
        vol = df[df.keys()[0]]
        full_shape = np.array(vol.shape)
        # Get number of blocks and block size
        block_size = np.uint32(np.ceil(full_shape/_block))
        ntiles = np.uint32([_block]*3)

        # All below must happen with df open

        subvols = zip(*np.where(np.ones(ntiles[1:])))
        subdepths = np.arange(ntiles[0])

        def even_count(old_c, new_c):
            diff_count = len(new_c) - len(old_c)
            if diff_count > 0:
                old_c = np.r_[old_c, np.zeros(diff_count, dtype=old_c.dtype)]
            if diff_count < 0:
                new_c = np.r_[new_c, np.zeros(-diff_count, dtype=new_c.dtype)]
            return old_c, new_c

        for y in subdepths:
            y_count = np.array([],dtype=np.bool)
            for z,x in subvols:

                zo,ze = np.array([z,z+1])*block_size[0]
                yo,ye = np.array([y,y+1])*block_size[1]
                xo,xe = np.array([x,x+1])*block_size[2]
                in_block = np.unique(vol[zo:ze, yo:ye, xo:xe])

                # Get the max number of ids
                max_ids = int(max(in_block) + 1)
                new_count = np.zeros(max_ids, dtype=np.bool)
                new_count[in_block] = True

                y_count, new_count = even_count(y_count, new_count)
                y_count = np.logical_or(y_count, new_count)

                # Get percentages
                y_base = 1./ntiles[0]
                z_base = y_base/ntiles[1]
                x_base = z_base/ntiles[2]
                z_done = z*z_base + y*y_base + x*x_base
                print("Found {:.1f}% highest ids".format(100*z_done))

            COUNTS, y_count = even_count(COUNTS, y_count)
            COUNTS = COUNTS + y_count.astype(np.uint32)

        np.savetxt(_out, COUNTS, fmt='%i')
        return sort(COUNTS)

