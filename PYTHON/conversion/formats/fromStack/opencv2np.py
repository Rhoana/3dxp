import os
import glob
import cv2
import numpy as np
from ..common import progress
from color2gray import color2gray

def opencv2np(path_in, ext_list, out_type, order='', span_pairs=[[],[],[]]):
    """
    Arguments
    ----------
    path_in: str
        Input folder with all tiff files
    ext_list: list
        List of valid file extensions
    out_type: np.dtype
        The type for the output volume
    order : str
        The byte order for colors with biggest byte last ('')
    span_pairs: list
        3x2 z,y,x start and upper limit (default none)

    Yields
    -------
    (np.ndarray)
        The shape of the full volume
    np.ndarray
        Each 2D slice from a single tif file
    """
    # read all images in folder
    def read_all(ext):
        search = os.path.join(path_in, '*.'+ext)
        return glob.glob(search)
    # Get all sorted images
    stack = [i for e in ext_list for i in read_all(e)]
    stack.sort()

    # Size input files
    ex_img = cv2.imread(stack[0], 0)
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
    # First yield the spans and dtype
    yield out_shape

    # Then yield each section from a file
    for zi, zfile in enumerate(stack[z0:z1]):
        progress(zi, z1-z0)
        if not order:
            # Yield as a plain image
            image = cv2.imread(zfile, 0)[y0:y1,x0:x1]
            yield image.astype(out_type)
        else:
            # Convert color image to grayscale
            image = cv2.imread(zfile)[y0:y1, x0:x1, :]
            yield color2gray(image, out_type, order)
