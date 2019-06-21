'''
Copyright (C) 2015 Andreas Esau
andreasesau@gmail.com

Created by Andreas Esau

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os    
import sys
import pkgutil
import importlib

reload_event = False

def setup_addon_modules(path, package_name):
    """
    Imports and reloads all modules in this addon. 
    
    path -- __path__ from __init__.py
    package_name -- __name__ from __init__.py
    """
    def get_submodule_names(path = path[0], root = ""):
        module_names = []
        for importer, module_name, is_package in pkgutil.iter_modules([path]):
            if is_package:
                sub_path = os.path.join(path, module_name)
                sub_root = root + module_name + "."
                module_names.extend(get_submodule_names(sub_path, sub_root))
            else: 
                module_names.append(root + module_name)
        return module_names 

    def import_submodules(names):
        modules = []
        for name in names:
            modules.append(importlib.import_module("." + name, package_name))
        return modules
        
    def reload_modules(modules):
        for module in modules:
            importlib.reload(module)
    
    names = get_submodule_names()
    modules = import_submodules(names)        
    if reload_event: 
        reload_modules(modules) 
    return modules
    
reload_event = True
