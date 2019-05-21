import bpy
import os


def load_element_from_other_file(filepath, collection_name, element_name, link):
    if not os.path.exists(filepath):
        raise OSError()

    with bpy.data.libraries.load(filepath, link=link) as (data_from, data_to):
        if element_name in getattr(data_from, collection_name):
            getattr(data_to, collection_name).append(element_name)
        else:
            raise NameError("The group name does not exist")

    return getattr(data_to, collection_name)[0]


def append_group(filepath, group_name, link=False):
    return load_element_from_other_file(filepath, "groups", group_name, link)


def append_scene(filepath, scene_name, link=False):
    return load_element_from_other_file(filepath, "scenes", scene_name, link)


def append_world(filepath, world_name, link=False):
    return load_element_from_other_file(filepath, "worlds", world_name, link)
