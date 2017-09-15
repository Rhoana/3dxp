import os
import math
import lxml
import lxml.etree
import numpy as np
from ..common import make_path


class MojoSave(object):
    def __init__(self, mojo_dir, trial=0):

        self.tile_y = 512
        self.tile_x = 512

    def load_tile(self, tile, new_width, new_height, stride):
        """ Subclass must implement
        """
        pass
    
    def save_tile(self, tile_path, tile, index_x, index_y):
        """ Subclass must implement
        """
        msg = """Saving {}
        """.format(tile_path)
        print(msg)

    def save_xml(self, in_shape, dxgi='R8_UNorm', nbytes=1):
        """ Subclass may overwrite
        """
        # Return if file exists
        if os.path.exists(self.output_tile_volume_file):
            return

        # Get the full width, depth, height
        all_shape = self.round(in_shape)
        (depth, width, height) = all_shape
        #Output TiledVolumeDescription xml file
        tiledVolumeDescription = lxml.etree.Element( "tiledVolumeDescription",
            fileExtension = self.output_extension[1:],
            numTilesX = str( int( math.ceil( width / self.tile_x ) ) ),
            numTilesY = str( int( math.ceil( height / self.tile_y ) ) ),
            numTilesZ = str( depth ),
            numTilesW = str( self.tile_index_w ),
            numVoxelsPerTileX = str( self.tile_x ),
            numVoxelsPerTileY = str( self.tile_y ),
            numVoxelsPerTileZ = str( 1 ),
            numVoxelsX = str( width ),
            numVoxelsY = str( height ),
            numVoxelsZ = str( depth ),
            dxgiFormat = str( dxgi ),
            numBytesPerVoxel = str( nbytes ),
            isSigned = str( False ).lower() )

        with open( self.output_tile_volume_file, 'w' ) as file:
            file.write( lxml.etree.tostring( tiledVolumeDescription, pretty_print = True ) )

    def count_ids(self, image):
        """ Subclass may implement
        """
        pass

    def save_db(self):
        """ Subclass may implement
        """
        pass
    
    def round(self,shape):
        logs = np.ceil(np.log2(shape)).astype(np.uint32)
        padshape = tuple(2 ** p for p in logs)
        if len(shape) > 2:
            return (shape[0],)+padshape[1:]
        return padshape

    def run(self,input_image,tile_index_z):
        """ Save file for each z section
        """
        in_shape = input_image.shape
        pad_shape = self.round(in_shape)
        original_image = np.zeros(pad_shape,dtype = input_image.dtype)
        original_image[:in_shape[0],:in_shape[1]] = input_image

        (original_x, original_y) = original_image.shape

        # Count IDs if defined
        self.count_ids(original_image)

        current_image_y = original_y
        current_image_x = original_x
        self.tile_index_z = tile_index_z
        self.tile_index_w = 0
        stride = 1

        while current_image_y > self.tile_y / 2 or current_image_x > self.tile_x / 2:

            current_tile_path    = self.output_tile_path     + os.sep + 'w=' + '%08d' % ( self.tile_index_w ) + os.sep + 'z=' + '%08d' % ( self.tile_index_z )

            make_path( current_tile_path )

            current_image = self.load_tile(original_image, current_image_x, current_image_y, stride)

            num_tiles_y = int( math.ceil( float( current_image_y ) / self.tile_y ) )
            num_tiles_x = int( math.ceil( float( current_image_x ) / self.tile_x ) )

            for tile_index_y in range( num_tiles_y ):
                for tile_index_x in range( num_tiles_x ):

                    y = tile_index_y * self.tile_y
                    x = tile_index_x * self.tile_x

                    current_tile_name = current_tile_path + os.sep + 'y=' + '%08d' % ( tile_index_y ) + ','  + 'x=' + '%08d' % ( tile_index_x ) + self.output_extension

                    tile_image = current_image[y:y + self.tile_y, x:x + self.tile_x]
                    self.save_tile(current_tile_name, tile_image, tile_index_x, tile_index_y)

            current_image_y /= 2
            current_image_x /= 2
            self.tile_index_w += 1
            stride *= 2

    def save(self, in_shape):
        """ Both functions called can be overwritten
        """
        self.save_db()
        self.save_xml(in_shape)
