import bpy
import json


### MISC - GENERAL ###

# create json file
def create_json_file(datas, path) :
    with open(path, "w") as write_file :
        json.dump(datas, write_file, indent=4, sort_keys=True)

# read json
def read_json(filepath):
    with open(filepath, "r") as read_file:
        datas = json.load(read_file)
    return datas


### MAIN LIST FILE ####

# initialize json datas
def initialize_json_datas () :
    datas = {}
    datas['size'] = []
    datas['fonts'] = []
    datas['subdirectories'] = []
    return datas

# add fonts to json datas
def add_fonts_json(datas, font_list) :
    #datas = {}
    #datas['font'] = []
    for font in font_list :
        datas['fonts'].append({
            "name" : font[0],
            "filepath" : font[1],
            "subdirectory" : font[2]
        })
    return datas

# add subdirectories to json datas
def add_subdirectories_json(datas, subdir_list) :
    for sub in subdir_list :
        datas['subdirectories'].append({
            "name" : sub[0],
            "filepath" : sub[1]
        })
    return datas

# add size to json datas
def add_size_json(datas, size) :
    datas['size'] = size
    return datas


### FONTFOLDER ####

# initialize json fontfolders datas
def initialize_json_fontfolders_datas () :
    datas = {}
    datas['fonfolders'] = []
    return datas

# add fontfolder to json datas
def add_fontfolders_json(datas, fontfolder) :
    datas['fonfolders'].append({
        "folder_path" : fontfolder
    })
    return datas


### FAVORITES ####

# initialize json favorites datas
def initialize_json_favorites_datas () :
    datas = {}
    datas['favorites'] = []
    return datas

# add favorite to json datas
def add_favorite_json(datas, font) :
    datas['favorites'].append({
        "font" : font
    })
    return datas
