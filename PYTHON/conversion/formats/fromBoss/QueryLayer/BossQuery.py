import numpy as np
from UtilityLayer import OUTPUT
from UtilityLayer import RUNTIME

class BossQuery(object):

    def __init__(self, path_name, zyx_index, keywords={}):
        """
        Arguments
        -----------
        path_name: str
            Path to boss.json file
        zyx_index: numpy.ndarray
            3x1 tile offset of the given tile
        keywords: dict
            Boss paths and offset
        """

        self.RUNTIME = RUNTIME()
        self.OUTPUT = OUTPUT()

        # Set the path and zyx index
        self.OUTPUT.INFO.PATH.VALUE = path_name
        self.RUNTIME.TILE.ZYX.VALUE = zyx_index

        # Boss-specific values
        boss_field = self.RUNTIME.IMAGE.SOURCE.BOSS

        # Get all paths for all images
        paths_field = boss_field.PATHS
        paths_field.VALUE = keywords.get(paths_field.NAME, '')

        # Get the offset of all images
        start_field = boss_field.INFO.START
        start_field.VALUE = keywords.get(start_field.NAME, [0,0,0])

    @property
    def index_zyx(self):
        """The tile offsets needed to get the tile

        Returns
        --------
        numpy.ndarray
            3x1 tile offset of the given tile
        """
        return np.uint32(self.RUNTIME.TILE.ZYX.VALUE)
