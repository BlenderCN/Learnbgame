# coding=utf-8

""" Texture picker menu - lists every texture found in a library folder.
    Select a folder in The Grove's user preferences.

    Copyright (c) 2017 - 2018, Wybren van Keulen, The Grove. """


from os import walk
from os.path import join
from operator import itemgetter
from .Translation import t


def list_textures(settings, context):
    """ List all textures found in the library folder. """

    textures_path = context.user_preferences.addons[__package__].preferences.textures_path
    textures = []

    i = 0
    for root, dirs, files in walk(textures_path):
        for file_name in files:
            if file_name[-4:].lower() in ['.jpg', 'jpeg', '.png', '.tga', '.tif', 'tiff']:
                textures.append((join(root, file_name), file_name[:-4], '', 'IMAGEFILE', i))
                i += 1

    textures.sort(key=itemgetter(1))

    if len(textures) == 0:
        textures.append(('', 'No Textures Found', 'Configure your textures path in the user preferences of the Grove.', 'INFO', i))

    return textures
