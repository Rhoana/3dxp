import numpy as np

from BossGrid import BossGrid
from QueryLayer import BossQuery
from QueryLayer.UtilityLayer import OUTPUT
from QueryLayer.UtilityLayer import RUNTIME

class Boss2np():

    OUTPUT = OUTPUT()
    RUNTIME = RUNTIME()

    def __init__(self, in_path):
        """ Load the json file
        
        Arguments
        ----------
        in_path : str
            The path to the json file
        """
        any_zyx = np.uint32([0,0,0])
        query_0 = BossQuery(in_path, any_zyx)
        # Bootstrap keywords from dummy query
        keywords = BossGrid.preload_source(query_0)
        # Get keyword constants
        k_size = self.OUTPUT.INFO.SIZE.NAME
        k_type = self.OUTPUT.INFO.TYPE.NAME
        k_block = self.RUNTIME.IMAGE.BLOCK.NAME
        # Get variables from keywords
        full_shape = keywords[k_size]
        block_shapes = keywords[k_block] 
        # Store the shape of one block and slice
        self.block_shape = block_shapes[0]
        slice_shape = [1,]+list(full_shape[1:])
        self.slice_shape = np.uint32(slice_shape)
        # Store all the block offsets
        n_zyx = self.slice_shape // self.block_shape
        self.all_yx = zip(*np.where(np.ones(n_zyx[1:])))
        # Store keywords
        self.dtype = keywords[k_type]
        self.full_shape = full_shape
        self.keywords = keywords
        self.in_path = in_path

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
        scale_tile = (self.block_shape // scale)[1:] # for 1 file
        msg = "Reading {}:{}, {}:{} from a {} section"
        print(msg.format( s_y0, s_y1, s_x0, s_x1, scale_slice ))

        # Create the slice image
        a = np.zeros(scale_slice, dtype=self.dtype)
        # Get attributes from self
        keywords = self.keywords
        in_path = self.in_path

        # Open all tiff files in the stack
        for _y, _x in self.all_yx:
            # Get tiff file path and offset
            f_offset = np.uint32([_z, _y, _x])
            # Read the file to a numpy volume
            args = (in_path, f_offset, keywords)
            f_vol = BossGrid.load_tile(BossQuery(*args))
            scale_vol = f_vol[0, ::scale[1], ::scale[2]]
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
