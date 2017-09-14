import os
import numpy as np
from np2mojo import MojoSave
from ..common import color_ids
import sqlite3
import h5py


class MojoSeg(MojoSave):
    def __init__(self, mojo_dir, trial=0):

        super(MojoSeg, self).__init__(mojo_dir, trial)

        output_path = os.path.join(mojo_dir, 'ids')
        self.output_tile_path = os.path.join(output_path, 'tiles')
        self.output_tile_volume_file = os.path.join(output_path, 'tiledVolumeDescription.xml')

        self.output_extension = '.hdf5'
        n_colors = 1000

        # Make path for colormap and database
        self.output_color_map_file = os.path.join(output_path, 'colorMap.hdf5')
        self.output_db_file = os.path.join(output_path, 'segmentInfo.db')
        # Write new databases for other trials
        if trial:
            trial_db = '{}_segmentInfo.db'.format(trial)
            self.output_db_file = os.path.join(output_path, 'trials', trial_db)

        self.id_max               = 0
        self.id_counts            = np.array([0], dtype=np.int64 )
        self.id_tile_list         = []

        # Make a color map
        self.color_map = color_ids(np.arange(n_colors+1, dtype=np.uint64))

    def load_tile(self, tile, new_width, new_height, stride):
        """ Required method to load tiles
        """
        super(MojoSeg, self).load_tile(tile, new_width, new_height, stride)
        return tile[ ::stride, ::stride ]

    def save_tile(self, tile_path, tile, index_x, index_y):
        """ Required method to save tiles
        """
        super(MojoSeg, self).save_tile(tile_path, tile, index_x, index_y)

        tile_padded = np.zeros( ( self.tile_y, self.tile_x ), np.uint32 )
        tile_padded[ 0:tile.shape[0], 0:tile.shape[1] ] = tile[:,:]
        # Save the hdf5 file
        with h5py.File( tile_path, 'w' ) as hf:
            hf.create_dataset( 'IdMap', data=tile_padded )

        position = (self.tile_index_w, self.tile_index_z, index_y, index_x)
        for unique_id in np.unique( tile_padded ):
            self.id_tile_list.append( (unique_id,) + position  )

    def save_xml(self, in_shape):
        """ Set Segmentation values for saving xml
        """
        super(MojoSeg, self).save_xml(in_shape, 'R32_UInt', 4)

    def count_ids(self, image):
        """ Optional method to count segments
        """
        super(MojoSeg, self).count_ids(image)

        id_counts = np.bincount( image.ravel() )
        nonzero_ids = np.nonzero( id_counts )[0]
        current_max = np.max( nonzero_ids )

        if self.id_max  < current_max:
            self.id_max  = current_max
            self.id_counts.resize( self.id_max  + 1 )

        self.id_counts[ nonzero_ids ] += np.int64( id_counts [ nonzero_ids ] )

    def save_db(self):
        """ Optional method to make a database
        """
        super(MojoSeg, self).save_db()

        ## Sort the tile list so that the same id appears together
        self.id_tile_list = np.array( sorted( self.id_tile_list ), np.uint32 )

        print 'Writing colorMap file (hdf5)'

        if not os.path.exists(self.output_color_map_file):
            with h5py.File( self.output_color_map_file, 'w' ) as hf:
                hf['idColorMap'] = self.color_map

        print 'Writing segmentInfo file (sqlite)'

        # Make folder for database if needed
        db_parent = os.path.dirname(self.output_db_file)
        self.mkdir_safe(db_parent)

        # Remove the database if already there
        if os.path.exists(self.output_db_file):
            os.remove(self.output_db_file)
            print "Deleted existing database file."

        con = sqlite3.connect(self.output_db_file)

        cur = con.cursor()

        cur.execute('PRAGMA main.cache_size=10000;')
        cur.execute('PRAGMA main.locking_mode=EXCLUSIVE;')
        cur.execute('PRAGMA main.synchronous=OFF;')
        cur.execute('PRAGMA main.journal_mode=WAL;')
        cur.execute('PRAGMA count_changes=OFF;')
        cur.execute('PRAGMA main.temp_store=MEMORY;')

        cur.execute('DROP TABLE IF EXISTS idTileIndex;')
        cur.execute('CREATE TABLE idTileIndex (id int, w int, z int, y int, x int);')
        cur.execute('CREATE INDEX I_idTileIndex ON idTileIndex (id);')

        cur.execute('DROP TABLE IF EXISTS segmentInfo;')
        cur.execute('CREATE TABLE segmentInfo (id int, name text, size int, confidence int);')
        cur.execute('CREATE UNIQUE INDEX I_segmentInfo ON segmentInfo (id);')

        cur.execute('DROP TABLE IF EXISTS relabelMap;')
        cur.execute('CREATE TABLE relabelMap ( fromId int PRIMARY KEY, toId int);')

        for entry_index in xrange(0, self.id_tile_list.shape[0]):
            cur.execute("INSERT INTO idTileIndex VALUES({0}, {1}, {2}, {3}, {4});".format( *self.id_tile_list[entry_index, :] ))

        taken_names = {}

        for segment_index in xrange( 1, self.id_max  + 1 ):
            if len( self.id_counts ) > segment_index and self.id_counts[ segment_index ] > 0:
                if segment_index == 0:
                    new_name = '__boundary__'
                else:
                    new_name = "segment{0}".format( segment_index )
                cur.execute('INSERT INTO segmentInfo VALUES({0}, "{1}", {2}, {3});'.format( segment_index, new_name, self.id_counts[ segment_index ], 0 ))

        con.commit()

        con.close()
