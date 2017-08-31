import numpy as np

def color2gray(image, out_type=np.uint32, order='bgr'):
    """
    Arguments
    ----------
    image : np.ndarray
        The color NxMx3 or NxMx4 image to make grayscale NxM
    out_type : np.dtype
        The desired type for the output array
    order : str
        The byte order for colors with biggest byte last ('bgr')
    """
    # Assume 3rd axis has red, green, blue, (and alpha)
    rgba = dict(zip('rgba', range(4)))
    # Output array is NxM
    output = np.zeros(image.shape[:2], dtype=out_type) 
    # Add all the color channels to the output array
    for ci, char in enumerate(order):
        output += image[:, :, rgba[char]] * (256 ** ci)
    # Return grayscale
    return output
