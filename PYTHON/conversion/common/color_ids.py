import numpy as np

def color_ids(vol):
    """ Convert ID values to color values
    Arguments
    ----------
    vol: np.ndarray
        An array of Integer IDs of 1,2,3..N Dimensions
    
    Returns
    --------
    np.ndarray
        A uint8 array with a new dimension for 3 colors
    """
    colors = np.zeros((3,)+ vol.shape).astype(np.uint8)
    colors[0] = np.mod(107 * vol, 700).astype(np.uint8)
    colors[1] = np.mod(509 * vol, 900).astype(np.uint8)
    colors[2] = np.mod(200 * vol, 777).astype(np.uint8)
    return np.moveaxis(colors,0,-1)

def color_id(i):
    """ Convert an ID to a color
    Arguments
    ----------
    i: int
        ID

    Returns
    ---------
    np.ndarray
        A vector of 3 colors
    """
    return color_ids(np.uint64([i]))[0]
