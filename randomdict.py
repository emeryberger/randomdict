# From https://stackoverflow.com/a/70870131

try:
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping

import random

__version__ = '0.2.1'

class RandomDict(MutableMapping):
    def __init__(self, *args, **kwargs):
        self._keys = {}
        self._values = []
        self.last_index = -1
        # Populate the RandomDict with any items passed in *args or **kwargs
        self.update(*args, **kwargs)

    def copy(self):
        """ Return a shallow copy of the RandomDict """
        new_rd = RandomDict()
        new_rd._keys = self._keys.copy()          
        new_rd._values = self._values[:]         
        new_rd.last_index = self.last_index
        return new_rd

    @classmethod
    def fromkeys(cls, keys, value=None):
        """Create a RandomDict from an iterable of keys, all mapped to the same value."""
        rd = cls()
        for key in keys:
            rd[key] = value
        return rd

    def __setitem__(self, key, val):
        i = self._keys.get(key, -1)                
        if i > -1:
            self._values[i] = (key, val)          
        else:
            self.last_index += 1
            i = self.last_index
            self._values.append((key, val))       
            self._keys[key] = i                   
    
    def __delitem__(self, key):
        # index of item to delete is i
        i = self._keys[key]                        
        # last item in values array is
        move_key, move_val = self._values.pop()    

        if i != self.last_index:
            # we move the last item into its location
            self._values[i] = (move_key, move_val)  
            self._keys[move_key] = i                
        # else it was the last item and we just throw
        # it away

        # shorten array of values
        self.last_index -= 1
        # remove deleted key
        del self._keys[key]                        
    
    def __getitem__(self, key):
        if key not in self._keys:                   
            raise KeyError(key)
        i = self._keys[key]                         
        return self._values[i][1]                   

    def __iter__(self):
        return iter(self._keys)                     

    def __len__(self):
        return self.last_index + 1

    def random_key(self):
        """ Return a random key from this dictionary in O(1) time """
        if len(self) == 0:
            raise KeyError("RandomDict is empty")
        
        i = random.randint(0, self.last_index)
        return self._values[i][0]                   

    def random_value(self):
        """ Return a random value from this dictionary in O(1) time """
        return self[self.random_key()]

    def random_item(self):
        """ Return a random key-value pair from this dictionary in O(1) time """
        k = self.random_key()
        return k, self[k]
    

def replace_dicts():
    # Replace dict with RandomDict
    import builtins
    builtins.dict = RandomDict

    # Replace defaultdict with RandomDict

    # stash the original import for use in a custom importer
    _original_import = builtins.__import__

    def _custom_import(name, globals=None, locals=None, fromlist=(), level=0):
        """Intercept imports of defaultdict to route to RandomDict"""
        module = _original_import(name, globals, locals, fromlist, level)
        if name == "collections" or (fromlist and "defaultdict" in fromlist):
            module.__dict__['defaultdict'] = RandomDict
        return module

    # Monkey-patch __import__
    builtins.__import__ = _custom_import
