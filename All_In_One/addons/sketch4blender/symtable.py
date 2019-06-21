from copy import deepcopy
from .scene import Tag

class Symbol(object):
    def __init__(self, name, tag, obj, line):
        self.name = name
        self.tag  = tag
        self.obj  = obj
        self.line = line
        self.ref  = 0

    def __repr__(self):
        return "Symbol(" + self.name + "->" + repr(self.obj) + ")"

class SymbolTable(dict):
    def __init__(self, **kwargs):
        super(SymbolTable, self).__init__(**kwargs)
        self.enclosing = None

    def get(self, name, default=None):
        symbol = super(SymbolTable, self).get(name, None)
        if not symbol and self.enclosing:
            return self.enclosing.get(name, None)
        if symbol and isinstance(symbol, Symbol):
            symbol.ref += 1
            return symbol
        return default

    def lookup(self, name, check=tuple(), line=-1):
        """find a symbol with name, with type in check"""
        symbol = self.get(name, None)
        if symbol:
            if symbol.obj:
                if type(symbol.obj) in check or \
                        (type(symbol.obj) == list and \
                         all(type(o) in check for o in symbol.obj)):
                    return symbol.obj
                # else TODO(david): error
            # else TODO(david): error
        # else TODO(david): error
        return None

    def new_symbol(self, name, tag, obj, line):
        if not (name and len(name) > 0):
            return None
        if tag and not self.lookup(tag, (Tag,)):
            return None

        symbol = self.get(name, None)
        if symbol and not (tag and len(symbol.tag) > 0 and symbol.ref == 0):
            # TODO(david): error if defined
            # TODO(david): error if defined with line no
            return None

        # TODO(david): warning if symbol defined

        symbol = Symbol(name, tag if tag else "", obj, line)
        self[name] = symbol
        return symbol

    def push(self):
        new = SymbolTable()
        new.enclosing = self
        return new

    def pop(self):
        # TODO(david): warn about unreferenced symbols
        return self.enclosing

