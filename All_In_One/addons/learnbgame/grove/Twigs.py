# coding=utf-8

""" The twig picker lists your library of twigs in a convenient menu.
    Picking a twig from the menu will automatically add the twig to your scene.
    If the twigs are already in the scene, for instance you grew a previous tree,
    it will use those.

    The twigs need to be checked every time, because Blender operators use an undo
    step to clean up after themselves. This means that the twigs disappear every time
    The Grove rebuilds the tree.

    Copyright (c) 2017 - 2018, Wybren van Keulen, The Grove. """


from os import walk
from os.path import join
from operator import itemgetter
from .Translation import t
import bpy
from re import sub
import os


def list_twigs(settings, context, icons):
    """ Fill the twig library menu with twigs found in the twigs folder.
        Display a tip to configure a twigs path if no twigs are found.
        Also add options to pick scene objects, or no twigs at all.

        Some good icons: GROUP, OBJECT_DATA, FILE_BLEND, APPEND_BLEND """

    #twigs_path = context.preferences.addons[__package__].preferences.twigs_path
    twigs_path = context.scene.plants.twigs_folder
    items = [(t('pick_objects'), t('pick_objects'), t('pick_objects_tt'), 'GROUP', 0),
             (t('no_twigs'), t('no_twigs'), t('no_twigs_tt'), 'X', 1)]

    library_items = []
    i = 3
    for root, dirs, files in walk(twigs_path):
        for file_name in files:
            if file_name[-6:] == '.blend':
                display_name = file_name[:-6]
                # Strip the Twig at the end of the name.
                display_name = display_name.split('Twig')[0]
                # Convert CamelCase to spaces.
                display_name = sub('(?!^)([A-Z0-9]+)', r' \1', display_name)
                # Remove any duplicate spaces caused by the previous regex.
                display_name = sub('[ ]+[ ]', ' ', display_name)
                library_items.append((join(root, file_name), display_name, '', 'IMPORT', i))
                i += 1
    library_items.sort(key=itemgetter(1))

    items = items + library_items

    if len(library_items) == 0:
        items.append((t('configure_twigs_path'), t('configure_twigs_path'), t('configure_twigs_path_tt'), 'INFO', i))

    return items


def check_twigs(settings, context, check_vanishing=False):
    if settings.apical_twig != "" and settings.apical_twig not in context.scene.objects:
        settings.apical_twig = ""
        if check_vanishing:
            settings.display_vanishing_twig_warning = True
            print(t('twig_vanished_info'))
    if settings.lateral_twig != "" and settings.lateral_twig not in context.scene.objects:
        settings.lateral_twig = ""
        if check_vanishing:
            settings.display_vanishing_twig_warning = True
            print(t('twig_vanished_info'))


def append_twigs(settings, context):
    """ Append twigs from a twigs file.
        This function is called before everything else.

        The naming convention for object inside twig files is simple. A lateral twig should contain "lateral", an
        apical twig "apical", and if both twigs are the same, the object should be named something with "twig. It is
        case insensitive.

        This is an improved version, the old one used a strict formatting rule, while this one
        offers more freedom for naming twig objects. For reference, this is the old code:
        if name[-11:] == "LateralTwig":
        elif name[-10:] == "ApicalTwig":
        elif name[-4:] == "Twig":
        TODO: Remove this info. """

    if settings.twigs_menu == t('no_twigs'):
        check_twigs(settings, context)
        return

    with bpy.data.libraries.load(settings.twigs_menu) as (data_from, data_to):
        data_to.objects = data_from.objects

    settings.lateral_twig = ""
    settings.apical_twig = ""

    for obj in data_to.objects:
        if obj is not None:
            if obj.name[-4] == ".":
                name = obj.name[:-4]
            else:
                name = obj.name

            if name.lower().find('lateral') != -1:
                if name not in bpy.data.objects:
                    context.scene.objects.link(obj)
                else:
                    if name not in context.scene.objects:
                        context.scene.objects.link(bpy.data.objects[name])
                settings.lateral_twig = name

            elif name.lower().find('apical') != -1:
                if obj.name not in bpy.data.objects:
                    context.scene.objects.link(obj)
                else:
                    if name not in context.scene.objects:
                        context.scene.objects.link(bpy.data.objects[name])
                settings.apical_twig = name

            elif name.lower().find('twig') != -1:
                if name not in bpy.data.objects:
                    context.scene.objects.link(obj)
                else:
                    if name not in context.scene.objects:
                        context.scene.objects.link(bpy.data.objects[name])
                settings.apical_twig = name
                settings.lateral_twig = name
