import os
import glob
import h5py
import numpy as np
import common

def hd2info(in_path):
    """
    Arguments
    ----------
    in_path: str
        Input hdf5 file
 
    Returns
    --------
    (np.ndarray, np.dtype)
        The shape and type of the full volume
    """
    with h5py.File(in_path, 'r') as hi:
        # Get the shape and dtype
        group = hi[hi.keys()[0]]
        shape = np.uint64(group.shape)
        dtype = group.dtype
        # Return as specified
        return shape, dtype

def hd2np(in_path, z_span):
    """
    Arguments
    ----------
    in_path: str
        Input hdf5 file
    z_span: np.ndarray
        [The first z slice, the upper limit]

    Yields
    -------
    np.ndarray
        Each 2D slice from a single tif file
    """
    with h5py.File(in_path, 'r') as hi:
        # Get the group in the file
        group = hi[hi.keys()[0]]
        # Yield each slice
        for zi in range(*z_span):
            yield group[zi, :, :]
