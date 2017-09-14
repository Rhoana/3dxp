import os
import numpy as np
from np2mojo import MojoSave
import cv2


class MojoImg(MojoSave):
    def __init__(self, mojo_dir, trial=0):

        super(MojoImg, self).__init__(mojo_dir, trial)

        output_path = os.path.join(mojo_dir, 'images')
        self.output_tile_path = os.path.join(output_path, 'tiles')
        self.output_tile_volume_file = os.path.join(output_path, 'tiledVolumeDescription.xml')

        self.output_extension     = '.tif'

    def load_tile(self, tile, new_width, new_height, stride):
        """ Required method to load tiles
        """
        super(MojoImg, self).load_tile(tile, new_width, new_height, stride)
        return cv2.resize(tile, ( new_width, new_height ))

    def save_tile(self, tile_path, tile, index_x, index_y):
        """ Required method to save tiles
        """
        super(MojoImg, self).save_tile(tile_path, tile, index_x, index_y)
        cv2.imwrite(tile_path, tile)
