""" Provieds Keywords, Logging templates, and an argument handler.

Attributes
-----------
BFLY_CONFIG : dict
   Loads all data from  the rh-config given\
by the :mod:`rh_config` module.

"""
# Get all the classes
from Keywords import INPUT
from Keywords import RUNTIME
from Keywords import OUTPUT

__all__ = ['INPUT','RUNTIME','OUTPUT']
