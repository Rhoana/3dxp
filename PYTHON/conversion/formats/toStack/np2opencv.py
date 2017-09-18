import os
import cv2
import numpy as np

def np2opencv(path_out, a): 
    """
    Arguments
    ----------
    path_out: str
        Output image file
    a: np.ndarray
        The image to write
    """
    # Make the image color if needed
    color_shape = a.shape + (-1,)
    a = a.view(np.uint8).reshape(color_shape)
    # Check the file extension
    image_fmt = os.path.splitext(path_out)[1]
    if image_fmt in ['jpeg','jpg']:
        # Write to a jpeg with a given image quality
        jpeg_qual = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
        cv2.imwrite(path_out, a[:,:,:3], jpeg_qual)
    else:
        # Write to a color or grayscale png
        cv2.imwrite(path_out, a[:,:,:3])
