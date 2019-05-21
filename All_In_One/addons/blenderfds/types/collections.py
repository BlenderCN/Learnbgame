"""BlenderFDS, collection types"""

from functools import total_ordering
from blenderfds.lib.utilities import isiterable

class BFList(list):
    """Enhanced list of objects with idname property.
    Get an item by its idname: bf_list["item idname"]
    Get a BFList of items by items idnames: bf_list[("item1 idname", "item2 idname")]
    Get the index of item: bf_list.index["item idname"]
    Check presence of item: "item idname" in bf_list
    Get item by idname with default: bf_list.get("item idname", default)
    """

    def __str__(self):
        return "<{0}: {1}>".format(self.__class__.__name__, list(self))

    def __repr__(self):
        return self.__str__()

    # bf_list.index("item idname"), bf_list.index(item)
    def index(self, item):
        if isinstance(item, str):        
            for i, value in enumerate(self):
                    if getattr(value, "idname", None) == item: return i
        return list.index(self, item)

    # bf_list["item idname"], bf_list[("item1 idname", "item2 idname", ...)], bf_list[3]
    def __getitem__(self, key):
        # Manage: bf_list["key"], return item
        if isinstance(key, str):
            for value in self:
                if getattr(value, "idname", None) == key: return value
            raise KeyError(key)
        # Manage: bf_list[("key1", "key2")], return tuple of items
        if isinstance(key, tuple) or isinstance(key, list):
            return BFList([self[k] for k in key])
        # Manage the rest (eg bf_list[3]), return item
        return list.__getitem__(self, key)

    # "item idname" in bf_list, item in list
    def __contains__(self, key):
        # Manage: "key" in bf_list
        if isinstance(key, str): return self.get(key, False) and True
        # Manage the rest (eg item in bf_list)
        return list.__contains__(self, key)

    # bf_list.get("item idname", default)
    def get(self, key, default=None):
        # Manage: bf_list.get("key", default=None)
        for value in self:
            if getattr(value, "idname", None) == key: return value
        if default is not None: return default
    
@total_ordering
class BFAutoItem():
    """Self-appending item to an internal BFList. Unicity checked at init. Alphabetic ordering by idname."""
    bf_list = BFList() # This is the collection. Don't forget to reinitialize when subclassing

    # Check idname unicity, then append to the class bf_list collection
    def __init__(self, idname):
        if not idname or not isinstance(idname, str): raise ValueError("BFDS: Invalid idname '{}'".format(idname))
        if idname in self.bf_list: raise ValueError("BFDS: Duplicated idname '{}'".format(idname))
        self.idname = idname
        self.bf_list.append(self)

    def __str__(self):
        return "<{0}: {1}>".format(self.__class__.__name__, self.idname)

    def __repr__(self):
        return self.__str__()

    # Allow alphabetic ordering by idname    
    def __lt__(self, other):
        return self.idname < other.idname
