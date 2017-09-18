import numpy as np

def to_scale_spans(_spans, _res):
    """ Return scaled spans
    _spans: [[int,int],[int,int],[int,int]]
        3x2 z,y,x start and upper limit
    _res : (int,int,int)
        Number of times to downsample in Z,Y,X
    """
    scale = 2 ** np.uint64(_res)
    return np.uint64(_spans // np.c_[scale, scale])

def to_scale_zyx(_zyz, _res):
    """ Return scaled zyz

    Arguments
    ----------
    _zyx : (int,int,int)
        full zyz coordinate
    _res : (int,int,int)
        Number of times to downsample in Z,Y,X
    """
    # Scale to smaller z coordinate
    scale = 2 ** np.uint64(_res)
    return np.uint64(_zyz // scale)

def to_scale_z(_z, _res):
    """ Return scaled z

    Arguments
    ----------
    _z : int
        full z coordinate
    _res : (int,int,int)
        Number of times to downsample in Z,Y,X
    """
    # Scale to smaller z coordinate
    z_scale = 2 ** _res[0]
    return _z // z_scale

def from_scale_z(_z, _res):
    """ Return full z

    Arguments
    ----------
    _z : int
        scaled z coordinate
    _res : (int,int,int)
        Number of times to downsample in Z,Y,X
    """
    # Scale to smaller z coordinate
    z_scale = 2 ** _res[0]
    return _z * z_scale
