import os
import glob
import numpy as np
import tifffile as tiff

def tif2np(path_in, span_pairs=[[],[],[]]):
    """
    Arguments
    ----------
    path_in: str
        Input folder with all tiff files
    span_pairs: list
        3x2 z,y,x start and upper limit (default none)

    Yields
    -------
    (np.ndarray, np.dtype)
        The shapee and type of the full volume
    np.ndarray
        Each 2D slice from a single tif file
    """
    # simple progress indicator
    def progress(part, whole):
        if part % (whole / 100) == 1:
            msg = 'Loaded: {:.2f}%'
            percent = 100.0 * part / whole
            print(msg.format(percent))

    # read all tifs in tifs folder
    search = os.path.join(path_in, '*.tif')
    stack = sorted(glob.glob(search))

    # Size input files
    ex_img = tiff.imread(stack[0])
    shape = (len(stack),) + ex_img.shape

    # Get the full spans as default
    spans = np.uint64([[0,0,0], shape]).T
    # Set the spans if not default
    for i, pair in enumerate(span_pairs):
        if len(pair) == 2:
            spans[i] = pair

    # Expand the spans
    [z0,z1], [y0, y1], [x0, x1] = spans
    out_shape = spans[:,1] - spans[:,0]
    out_type = ex_img.dtype
    # First yield the spans and dtype
    yield (out_shape, out_type)

    # Then yield each section from a file
    for zi, zfile in enumerate(stack[z0:z1]):
        progress(zi, z1-z0)
        yield tiff.imread(zfile)[y0:y1, x0:x1]
