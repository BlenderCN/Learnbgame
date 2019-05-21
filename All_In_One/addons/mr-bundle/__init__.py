# __init__.py
# date  : 2017/07/14
# author: Laurent Boiron
#
# Bundler point cloud and camera importer
#

bl_info = {
    "name": "Mr. Bundle",
    "description" : "Import Visual Structure From Motion (vsfm) bundle.out",
    "author"  : "Laurent Boiron",
    "version" : (0, 1),
    "blender" : (2, 78, 0),
    "wiki_url": "",
    "category": "Import",
    }

from . import importer

def register():
    importer.register()

def unregister():
    importer.unregister()

if __name__== "__main__":
    register()


