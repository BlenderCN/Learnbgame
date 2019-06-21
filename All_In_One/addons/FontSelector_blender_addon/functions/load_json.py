import bpy

from .json_functions import read_json

# get element
def item_name_getter(elem):
    return elem[0]

def load_json_font_file(json_file, font_collection, subdir_collection) :
    datas = read_json(json_file)
    fontlist = []

    # load fonts
    for font in datas['fonts'] :
        fontlist.append([font['name'], font['filepath'], font['subdirectory']])

    fontlist.sort(key=item_name_getter)
    idx = 0
    for font in fontlist :
        newfont = font_collection.add()
        newfont.name = font[0]
        newfont.filepath = font[1]
        newfont.subdirectory = font[2]
        newfont.index = idx
        idx += 1

    # load subdirs
    for subdir in datas['subdirectories'] : 
        newsubdir = subdir_collection.add()
        newsubdir.name = subdir['name']
        newsubdir.filepath = subdir['filepath']    