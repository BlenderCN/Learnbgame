import bpy
import copy, os.path
from ctypes import *

from . import engine

#Manages loading of source code files and path name resolution.
class SourceLoader:
    path_resolver_cb_type = CFUNCTYPE(c_char_p, c_char_p, c_void_p) #char *resolve(const char *name, /* out */ void *status);
    source_loader_cb_type = CFUNCTYPE(c_char_p, c_char_p, c_void_p) #char *load(const char *name, /* out */ void *status);

    def __init__(self, libgideon):
        self.lib = libgideon
        self.resolve_cb = self.path_resolver_cb_type(lambda p, s : self.resolve_pathname(p.decode('ascii'), s))
        self.load_source_cb = self.source_loader_cb_type(lambda fname, s : self.load_source(fname.decode('ascii'), s))
        self.search_paths = []

    def set_search_paths(self, path_list):
        self.search_paths = copy.deepcopy(path_list)
    
    def resolve_pathname(self, path, status_ptr):
        #check gideon source objects
        allow_internal = True
        allow_external = True

        if path in bpy.context.scene.gideon.sources:
            src_obj = bpy.context.scene.gideon.sources[path]
            if src_obj.external:
                allow_internal = False
            else:
                allow_external = False

        #check internal text objects
        if allow_internal:
            if path in bpy.data.texts:
                resolved = "internal:" + path
                engine.set_status(self.lib, status_ptr, 1)
                return engine.string_copy(self.lib, resolved)
        
        #search the file system (using the directories specified)
        if allow_external:
            path_and_ext = os.path.splitext(path)
            if path_and_ext[1] == '':
                path_with_extension = path_and_ext[0] + '.gdl'
            else:
                path_with_extension = path_and_ext[0] + path_and_ext[1]
        
            paths_to_check = [ os.path.abspath(os.path.join(dirpath, path_with_extension)) for dirpath in self.search_paths ]
        
            for p in paths_to_check:
                if os.path.isfile(p):
                    resolved = "external:" + p
                    engine.set_status(self.lib, status_ptr, 1)
                    return engine.string_copy(self.lib, resolved)

        #nothing found
        engine.set_status(self.lib, status_ptr, 0)
        return engine.string_copy(self.lib, "")

    def get_resolve_cb(self):
        return self.resolve_cb

    
    def load_source(self, path, status_ptr):
        try:
            source_info = path.split(':', 1)
            assert len(source_info) == 2
            
            src_type = source_info[0]
            src_path = source_info[1]
            
            if src_type == 'external':
                f = open(src_path, 'r')
                source = f.read()
                f.close()
                
                engine.set_status(self.lib, status_ptr, 1)
                return engine.string_copy(self.lib, source)
            elif src_type == 'internal':
                if src_path in bpy.data.texts:
                    txt_obj = bpy.data.texts[src_path]
                    
                    engine.set_status(self.lib, status_ptr, 1)
                    return engine.string_copy(self.lib, txt_obj.as_string())
            
        except IOError:
            pass

        engine.set_status(self.lib, status_ptr, 0)
        return engine.string_copy(self.lib, "")

    def get_load_cb(self):
        return self.load_source_cb
