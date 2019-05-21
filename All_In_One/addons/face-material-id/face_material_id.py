"""
This module has functions to save per face material info of a mesh.

# How to

You can store the material slot index of every face of a mesh, and the name of each
material in a JSON file with the functions `dump_material_indices_and_names()` and
`save_material_names_and_indices_to_file()`.

Then you can apply the material info from a file to a mesh with the functions
`load_material_names_and_indices_from_file()` and `apply_material_indices_and_names()`.

You can check if the data loaded from a JSON can be applied on a mesh with the function
`check_material_infos_on_mesh()`.
"""

import bpy
import json


def dump_material_indices_and_names(mesh_object):
    """
    Put per face material indices and material names in a dictionary
    :param mesh_object: Blender Object (of type MESH)
    :return: Python dictionary with indices and names
    """
    dump = {}
    dump["indices"] = [p.material_index for p in mesh_object.data.polygons]
    dump["materials"] = [m.material.name if m.material else None for m in mesh_object.material_slots]
    return dump


def apply_indices(mesh_object, indices):
    """
    Set per face material indices for the mesh object
    :param mesh_object: Blender object (of type MESH)
    :param indices: List of integer (material indices per face)
    """
    for i, p in enumerate(mesh_object.data.polygons):
        p.material_index = indices[i]


def remove_material_slots():
    """
    Removes all the material of the active object.
    """
    while len(bpy.context.object.data.materials):
        bpy.ops.object.material_slot_remove()


def set_material_slots(object, materials):
    """
    Replace the object's materials with the given materials
    :param object: Blender Object to replace materials on
    :param materials: List of string
    """
    # remove old materials
    remove_material_slots()
    # add the new ones
    for m in materials:
        if m is None or m in bpy.data.materials:
            object.data.materials.append(bpy.data.materials[m] if m else None)


def apply_material_indices_and_names(mesh_object, material_indices_and_names):
    """
    Replace materials with the given ones, and change material indices per face with the given ones.
    :param mesh_object: Blender Object (of type MESH)
    :param material_indices_and_names: Python dictionary with material names and indices
    """
    set_material_slots(mesh_object, material_indices_and_names["materials"])
    apply_indices(mesh_object, material_indices_and_names["indices"])


def save_material_names_and_indices_to_file(material_names_and_indices, path):
    """
    Save material info to file
    :param material_names_and_indices: Python dictionary
    :param path: Path of the target file
    """
    dump = json.dumps(material_names_and_indices)
    with open(path, 'w') as file:
        file.write(dump)


def load_material_names_and_indices_from_file(path):
    """
    Loads material info from file
    :param path: Path of the source file
    """
    with open(path, 'r') as file:
        return json.load(file)


def check_material_infos_on_mesh(material_indices_and_names, mesh_object):
    """
    Check if material_indices_and_names is valid to be applied on mesh_object
    :param material_indices_and_names: Python dictionary with material infos
    :param mesh_object: Blender Object
    :return: (Bool, String) : (Test success, possible error message)
    """
    ok = True
    message = ""
    # check if it's a mesh object
    if mesh_object.type == "MESH":
        # check number of faces
        if len(mesh_object.data.polygons) != len(material_indices_and_names["indices"]):
            ok = False
            message += "Face count mismatch ({} on {}) ".format(len(material_indices_and_names["indices"]),
                                                                len(mesh_object.data.polygons))
    else:
        ok = False
        message += "Object is not of type MESH. "
    # check every materials
    for m in material_indices_and_names["materials"]:
        if m and (m not in bpy.data.materials):
            ok = False
            message += "Material missing: " + m + ". "
    return ok, message
