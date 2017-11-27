from itertools import ifilter

# For all nameless keywords
class NamelessStruct(object):
    """ Provides a dictionary-like class interface

    Arguments
    ----------
    _keywords: dict
        Each keyword becomes an attribute

    Attributes
    -----------
    VALUE : anything
        Any instance has its own mutable VALUE.
    LIST : list
        All unique attributes are given here. \
If 'LIST' is given as a keyword, the order\
of the attributes given in the 'LIST' keyword\
is preserved at the top of the :data:`LIST`.
    """
    VALUE = None
    def __init__(self,**_keywords):
        # Begin a new list of all keyword NAMES
        all_list = _keywords.get('LIST',[])[:]
        # Add other keywords to list
        for key in _keywords:
            keyval = _keywords[key]
            setattr(self,key,keyval)
            # Put all lists into list
            if isinstance(keyval, list):
                all_list += keyval
            # Put all keyword names into list
            if hasattr(keyval, 'NAME'):
                all_list.append(keyval.NAME)
        # If there are named keywords
        if len(all_list):
            all_set = set(all_list)
            all_key = all_list.index
            self.LIST = sorted(all_set, key=all_key)

    def _n_get(self, name):
        """ Get a ``NamedStruct`` attribute by NAME.

        Arguments
        -----------
        name: str
            The NAME attribute of the requested \
:class:`NamedStruct`.
        """
        children = self.__dict__.values()
        # Make sure name is the same
        def is_name(c):
            has_name = hasattr(c,'NAME')
            return has_name and c.NAME == name
        # Return None if no children have name
        return next(ifilter(is_name, children), None)

    def __getitem__(self, key):
        """ Get any attribute as if from a dictionary

        If the attribute is a :class:`NamedStruct`, \
then the `key` can be either the attribute or the NAME of \
the attribute. The key is first used as an attribute and \
then used as a NAME with :meth:`_n_get` if not an attribute.

        Arguments
        ----------
        key: str
            The attribute to get
        """
        return self.__dict__.get(key,self._n_get(key))

    def get(self, key, default=None):
        """ Get any attribute with a default value

        This returns :meth:`__getitem__` or ``default``.

        Arguments
        ----------
        key: str
            The attribute to get
        default: anything
            The value if attribute is not found.
        """

        if default is None:
            default = {}
        found = self.__getitem__(key)
        return found if found else default

    def __contains__(self, key):
        """ Check for names or attributes in instance
        """
        return None is not self.__getitem__(key)

# For all keywords with names
class NamedStruct(NamelessStruct):
    """ It's a NamelessStruct with a NAME attribute.

    Arguments
    ----------
    _name : str
        The name becomes :data:`NAME`
    _keywords: dict
        Each keyword becomes an attribute

    Attributes
    -----------
    NAME : str
        This is a constant used externally whenever \
passing the :data:`VALUE` attribute between \
classes, methods, and external files. \
All ``NamedStruct`` or ``NamelessStruct`` with a \
``NamedStruct`` attribute can access the ``NameStruct`` \
with the NAME as a dictionary key such as parent['a_name'].
    LIST : list
        see :data:`NamelessStruct.LIST`
    VALUE : anything
        see :data:`NamelessStruct.VALUE`
    """
    NAME = None
    def __init__(self,_name,**_keywords):
        NamelessStruct.__init__(self, **_keywords)
        self.NAME = _name

