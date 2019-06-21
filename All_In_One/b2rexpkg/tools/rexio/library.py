import os
import shutil
from collections import defaultdict
from os.path import dirname

class LibraryComponent(object):
    """
    A component found inside  a library.
    """
    def __init__(self, name, path, component_type, dependencies,
                 comp_dependencies, attrs):
        self.name = name
        self.path = path
        self._type = component_type
        self._file_dependencies = dependencies
        self.dependencies = comp_dependencies
        self.attributes = attrs

    def pack(self, dest_dir):
        """
        Pack the component and all its dependencies into the destination
        directory.
        """
        # XXX should create a subdirectory to avoid possible conflicts?
        shutil.copy(self.path, dest_dir)
        for dep in self._file_dependencies:
            shutil.copy(dep, dest_dir)

    def __repr__(self):
        return "LibraryComponent(%s, %s, %s)"%(self.name, self.path, self._type)

class Library(object):
    """
    A component library.
    """
    def __init__(self):
        self._paths = []
        self._components = defaultdict(dict)

    def add_path(self, path, refresh=False):
        """
        Add the given path into the library. The path will be scanned for
        known component types.
        """
        if not os.path.exists(path):
            # to allow for test paths that dont exist for other ppl
            return
        if not path in self._paths or refresh:
            self._paths.append(path)
            self.scan_path(path)

    def scan_path(self, path):
        """
        Scan the given path for known component types.
        """
        for f in os.listdir(path):
            if f.endswith(".js"):
                name = f[:-3]
                f_path = os.path.join(path, f)
                self.add_js_component(name, f_path)

    def find_paths(self, path, delim):
        """
        Find paths inside the given file.
        """
        f = open(path, 'r')
        data = f.read()
        f.close()
        paths = set()
        found = data.find(delim)
        while not found == -1:
            delimiter = data[found-1]
            if delimiter in ['"', "'"]:
                end = data.find(delimiter, found)
                paths.add(data[found:end].strip())
            else:
                end = found+1
            found = data.find(delim, end)
        return list(paths)

    def dereference_paths(self, paths, basepath):
        """
        Dereference the given paths from local:// or file:// style
        into filesystem.
        """
        new_paths = []
        for path in paths:
            if path.startswith('local://'):
                new_paths.append(os.path.join(basepath, path[8:]))
            elif path.startswith('file://'):
                new_paths.append(os.path.join(basepath, path[7:]))
        return new_paths

    def add_js_component(self, name, path):
        """
        Add the given js component into the library.
        """
        paths = self.find_paths(path, 'local://')
        paths += self.find_paths(path, 'file://')
        paths = self.dereference_paths(paths, os.path.dirname(path))
        deps, attrs = self.find_component_deps_fromjs(path)
        self._components['jsscript'][name] = LibraryComponent(name,
                                                             path, 'js', paths,
                                                             deps, attrs)
    def find_component_deps_fromjs(self, path):
        """
        Find the component dependencies by scanning a javascript file.
        """
        f = open(path, 'r')
        data = f.read()
        f.close()
        deps = set()
        attrs = set()
        if 'me.dynamiccomponent' in data:
            deps.add('EC_DynamicComponent')
            pos = data.find('me.dynamiccomponent')
            linepos = data[:pos].rfind('\n')
            name = data[linepos: pos].split('=')[0].strip()
            key = name + '.GetAttribute('
            attrs = attrs.union(self.find_from_function(data, key))

        if 'me.animationcontroller' in data:
            deps.add('EC_AnimationController')

        key = 'me.GetComponentRaw('
        deps = deps.union(self.find_from_function(data, key))

        return list(deps), list(attrs)

    def find_from_function(self, data, key):
        """
        Search for a given key in the given data.
        """
        all_found = set()
        found = data.find(key)
        while not found == -1:
            delim = data[found+len(key)]
            end = data.find(delim, found+len(key)+2)
            all_found.add(data[found+len(key)+1:end])
            found = data.find(key, end)
        return list(all_found)

    def get_component(self, component_type, name):
        """
        Get the component with the given type and name.
        """
        return self._components[component_type][name]

    def get_components(self, component_type):
        """
        Get all components with the given type.
        """
        return self._components[component_type]

# hardcoded path, would be nice to do it later and also to allow the user to
# add his own paths.
library = Library()
library.add_path(os.path.join(dirname(dirname(dirname(__file__))),
                              'data',
                              'rexjs'))
if __name__ == '__main__':
    l = Library()
    l.add_path('/home/caedes/SVN/REALXTEND/tundra/bin/scenes/Door')
    l.add_path('/home/caedes/SVN/REALXTEND/tundra/bin/scenes/Avatar')
    print(l.get_components('jsscript'))

