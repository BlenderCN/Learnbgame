import bpy
import os


def append_group(filepath, name, link=False):
    return append_element(filepath, "groups", name, link)


def append_object(filepath, name, link=False):
    return append_element(filepath, "objects", name, link)


def append_material(filepath, name, link=False):
    return append_element(filepath, "materials", name, link)


def append_scene(filepath, name, link=False):
    return append_element(filepath, "scenes", name, link)


def append_world(filepath, name, link=False):
    return append_element(filepath, "worlds", name, link)


def append_element(filepath, collection_name, element_name, link):
    if os.path.exists(filepath):

        with bpy.data.libraries.load(filepath, link=link) as (data_from, data_to):
            if element_name in getattr(data_from, collection_name):
                getattr(data_to, collection_name).append(element_name)
            else:
                print("The %s name does not exist" % (collection_name[:-1]))

        return getattr(data_to, collection_name)[0]

    else:
        print("The file path does not exist")
