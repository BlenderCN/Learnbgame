# coding=utf-8

""" Copyright 2017 - 2018, Wybren van Keulen, The Grove

    WIP: The Grove's very own translation system translates phrases into Blender's current language.

    """


from .Languages.en_US import dictionary


def t(phrase):
    """ Translate the give phrase into Blender's current language. """

    try:
        return dictionary[phrase]
    except KeyError:
        print('Warning - Text missing for: ' + phrase)
        return phrase
