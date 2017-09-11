import os

def format_path (in_path):                              
    """ Get the full path
    Arguments
    ---------
    in_path : str
        Path relative to current or home directory
    
    Returns
    --------
    str
        Absolute path from root of filesystem
    """
    return os.path.realpath(os.path.expanduser(in_path))
