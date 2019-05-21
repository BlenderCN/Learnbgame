from . import raw
import struct

class file_node(object):
    __slots__ = ('name', 'data')
    
    def __init__(self, name, data=None):
        self.name = name
        self.data = data
        
    def size(self):
        return len(self.data)
        
    def total_size(self):
        return self.size() + len(self.name) + 4
        
    def output(self):
        out = struct.pack('>'+str(len(self.name))+'sI', self.name.encode('ascii'), self.size())
        out += self.data
        return out
        
        
    def parent(self, p):
        p.children.append(self)
        return self
        
    def console_print(self, indent=0):
        for i in range(indent):
            print("\t", end="")
        print(self.name)
    
class folder_node(object):
    __slots__ = ('name', 'children')
    def __init__(self, name, *args):
        self.name = name
        self.children = list(args)
    
    def size(self):
        total = 0
        for child in self.children:
            total += child.total_size()
        return total
    
    def total_size(self):
        return self.size() + len(self.name) + 4
    
    def output(self):
        out = struct.pack('>'+str(len(self.name))+'sI', self.name.encode('ascii'), self.size())
        for child in self.children:
            out += child.output()
        return out
        
    def parent(self, p):
        p.children.append(self)
        return self
        
    def console_print(self, indent=0):
        for i in range(indent):
            print("\t", end="")
        print(self.name)
        
        for child in self.children:
            child.console_print(indent+1)
            

class iff_file(object):
    __slots__ = ('data', 'interpreter')
    
    @staticmethod
    def _nodeName(f):
        string = f.read(8)
        length = 0
        
        for c in string:
            if not ((c >= ord('A') and c <= ord('Z')) or (c >= ord('0') and c <= ord('9')) or c == ord(' ')):
                break
            length += 1
        
        if length < 8 and length >= 4:
            string = string[0:4]
            f.seek(-4, 1) #go back 4 bytes
        elif length < 4:
            f.seek(-8, 1)
            return ''
        
        return string.decode('ascii')
    
    def __init__(self, filename, interpreter):
        with open(filename, 'rb') as f:
            while True:
                name = iff_file._nodeName(f)
                if(name != ""):
                    size = raw.read_net_uint32(f)
                    if(name.count("FORM") > 0):
                        interpreter.interpret_folder(name, size)
                    else:
                        interpreter.interpret_file(name, size, f)
                else:
                    break