import os
import cv2
import json
import h5py
import time
import argparse
import numpy as np
import tifffile as tiff

class Boss2np():
    ALL = 'tiles'
    PATH = 'location'
    ZYX = ['z','row','column']

    def __init__(self, in_path):
        """ Load the json file
        
        Arguments
        ----------
        in_path : str
            The path to the json file
        """
        with open(in_path, 'r') as jd:
            # Get all the filenames
            boss_file = json.load(jd)
            all = boss_file.get(self.ALL, []) 
            # Get all the paths
            def get_path(d):
                return d.get(self.PATH, '')
            all_path = map(get_path, all)
            # Get all the offsets
            def get_offset(d):
                return map(d.get, self.ZYX)
            # Get the offsets and the max offset
            all_off = np.uint32(map(get_offset, all))
            self.size = np.amax(all_off, 0) + 1
            # Get the xy dimensions and product
            self.size_xy = np.uint32(self.size[1:])
            self.n_xy = np.prod(self.size_xy)
            # Get the tile size from first tile
            tile0 = self.imread(all_path[0])
            self.tile_shape = np.uint32((1,) + tile0.shape)
            # The size and datatype of the full volume
            self.full_shape = self.tile_shape * self.size
            self.slice_shape = np.r_[1, self.full_shape[1:]]
            self.dtype = tile0.dtype
            # Sort all paths by ordered offsets
            def make_flat(pair):
                return np.ravel_multi_index(pair[0], self.size)
            # Sort paths by ordered offsets
            pairs = sorted(zip(all_off, all_path), key=make_flat)
            self.all_off, self.all_path = zip(*pairs)
            self.all_off = np.uint32(self.all_off)

    def scale_image(self, _z, _res, _spans=[[],[],[]], _list=[]):
        """ Downsample some tifs to a numpy array
        
        Arguments
        ----------
        _z: int
            The current full-resolution section
        _res : (int,int,int)
            Number of times to downsample by _res in Z,Y,X
        _spans: list
            3x2 z,y,x start and upper limit (default none)
        """
        # Get the full spans as default
        spans = np.c_[[0,0,0], self.slice_shape].astype(np.uint64)
        # Set the spans if not default
        for i, pair in enumerate(_spans):
            if len(pair) == 2:
                spans[i] = pair

        # Downsampling constant
        scale = 2 ** np.uint32(_res)
        # Scale and expand the spans
        s_y0, s_y1 = spans[1] // scale[1]
        s_x0, s_x1 = spans[2] // scale[2]
        # Get the downsampled full / tile shape
        scale_slice = (self.slice_shape // scale)[1:] # per slice
        scale_tile = (self.tile_shape // scale)[1:] # for 1 file
        msg = "Reading {}:{}, {}:{} from a {} section"
        print(msg.format( s_y0, s_y1, s_x0, s_x1, scale_slice ))

        # Create the slice image
        a = np.zeros(scale_slice, dtype=self.dtype)

        # Open all tiff files in the stack
        for f in range(self.n_xy):
            # Get tiff file path and offset
            f_id = int(_z * self.n_xy + f)
            f_path = self.all_path[f_id]
            f_offset = self.all_off[f_id]
            # Read the file to a numpy volume
            f_vol = self.imread(f_path)
            scale_vol = f_vol[::scale[1],::scale[2]]
            # Get coordinates to fill the tile
            y0, x0 = scale_tile * f_offset[1:]
            y1, x1 = [y0, x0] + np.uint32(scale_vol.shape)
            # Fill the tile with scaled volume
            a[y0:y1, x0:x1] = scale_vol

        # Mask data if list
        if len(_list):
            # Make empty uint8 array
            new_a = np.zeros(a.shape, dtype=np.uint8)
            # Add each list id to array
            for lin, liv in enumerate(_list):
                # Add 1 to list index
                list_index = lin + 1
                # Add values to array
                new_a += np.uint8(a == liv)*list_index
            # New a becomes a
            a = new_a

        # Return full section
        return a[s_y0:s_y1,s_x0:s_x1]

    @staticmethod
    def imread(_path):
        if os.path.splitext(_path)[1] in ['.tiff', '.tif']:
            return tiff.imread(_path)
        else:
            return cv2.imread(_path,0)

