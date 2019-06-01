__author__ = 'Eric'


import pkgutil
import importlib
import os
from .RWMaterial import RWMaterial

pkg_dir = os.path.dirname(__file__)

for (module_loader, name, isPKG) in pkgutil.iter_modules([pkg_dir]):
    importlib.import_module('.' + name, __package__)

# material_classes = {cls.__name__: cls for cls in RWMaterial.__subclasses__()}
material_classes = sorted([cls for cls in RWMaterial.__subclasses__()],
    key=lambda x: x.__name__)
