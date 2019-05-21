bl_info = {
    "name" : "Svg path exporter",
    "author" : "Hideaki Fukushima",
    "version" : (1, 0),
    "blender" : (2, 7, 9),
    "location" : "File > Export > Export strokes to SVG",
    "description" : "Export mesh edges and curves to svg as strokes",
    "warning" : "",
    "wiki_url" : "",
    "tracker_url" : "",
    "category" : "Import-Export"
}


import bpy

from . import opSVGExport


def regMain(reg):
    opSVGExport.regOps(reg)

def register():
    regMain(True)

def unregister():
    regMain(False)


if __name__ == '__main__':
    register()
