import tifffile as tiff

def np2tif(path_out, a):
    """
    Arguments
    ----------
    path_out: str
        Output tiff file
    a: np.ndarray
        The image to write
    """
    tiff.imsave(path_out, a)
