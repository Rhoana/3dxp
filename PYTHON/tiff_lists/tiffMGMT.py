import os
import cv2
import json
import h5py
import time
import argparse
import numpy as np
import tifffile as tiff

class TiffMGMT():
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

    def scale_images(self, _bounds, _path, _res, _format='png'):
        """ Downsample the tiffs to a png stack
        
        Arguments
        ----------
        _bounds : numpy.ndarray
            2x1 array of scaled z_arg bounds
        _path : str
            The path to the output h5 file
        _res : (int,int,int)
            Number of times to downsample by _res in Z,Y,X
        """
        # Downsampling constant
        scale = 2 ** np.uint32(_res)
        # Get the downsampled full / tile shape
        scale_bounds = _bounds // scale[0] # only for Z
        scale_slice = self.slice_shape[1:] // scale[1:] # per slice
        scale_tile = self.tile_shape[1:] // scale[1:] # for 1 file
        print("""
Scaled Z Bounds: {}
Writing {} volume to {}
""".format(scale_bounds, scale_slice, _path))
        # Start timing the h5 file writing
        sec_start = time.time()
        # Add to the h5 file for the given stack
        for s_z in range(*scale_bounds):
            # Scale the z bound
            z = s_z * scale[0]
            # Create the slice image
            a = np.zeros(scale_slice, dtype=self.dtype)
            # Create the png file path
            image_path = '{:05d}.{}'.format(s_z, _format)
            image_path = os.path.join(_path, image_path)

            if os.path.exists(image_path):
              print 'was there', image_path
              continue

            # Open all tiff files in the stack
            for f in range(self.n_xy):
                # Get tiff file path and offset
                f_id = int(z * self.n_xy + f)
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

            # Handle each format
            if _format == 'png':
                # Write the layer to a color or grayscale png file
                color_shape = a.shape + (-1,)
                a = a.view(np.uint8).reshape(color_shape)
                cv2.imwrite(image_path, a[:,:,:3])
            elif _format in ['jpeg','jpg']:
                # Write the layer to a color or grayscale png file
                color_shape = a.shape + (-1,)
                a = a.view(np.uint8).reshape(color_shape)
                # Write to a jpeg with a given image quality
                jpeg_qual = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
                cv2.imwrite(image_path, a[:,:,:3], jpeg_qual)
            else:
                print 'MAX',a.max()
                tiff.imsave(image_path, a)

            print("""
            Wrote layer {} to a {} file
            """.format(z, _format))

        # Record total writing time
        sec_diff = time.time() - sec_start
        # Record total slices written
        z_count = scale_bounds[1] - scale_bounds[0]
        print("""
Wrote {} layers to {} in {} seconds
""".format(z_count, _path, sec_diff))

    @staticmethod
    def imread(_path):
        if os.path.splitext(_path)[1] in ['.tiff', '.tif']:
            return tiff.imread(_path)
        else:
            return cv2.imread(_path,0)

