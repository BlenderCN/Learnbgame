print("Executing init src")
"""from os.path import dirname, basename, isfile
import glob
modules = glob.glob(dirname(__file__)+"/*.py")
#__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
print(__all__)
"""
__all__ = [
	'geometry', 
	'pose', 
	'config', 
	'csvfile', 
	'BlenderManager', 
	'wops',
	'training', 
	'utils', 
	'DataManager', 
]
