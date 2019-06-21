import os
import bpy


def project_files_path():
    ''' Consolidate the creation of the path to the project files'''

    filepath = os.path.dirname(bpy.data.filepath)
    filepath, dot, blend = bpy.data.filepath.rpartition(os.path.extsep)
    filepath = filepath + "_files"
    filepath = os.path.join(filepath, "mcell")
    return filepath


def preserve_selection_use_operator(operator, new_obj):
    """ Preserve current object selection state and use operator.

    It is not uncommon for Blender operators to make use of the current
    selection. This means you first have to save the current selection state,
    deselect everything, select the object you actually want to do the
    operation on, execute the operator, deselect that object, and finally
    reselect the original selection state. This sounds silly but can be quite
    useful. """

    object_list = bpy.context.scene.objects
    selected_objs = [obj for obj in object_list if obj.select]
    # Deselect everything currently selected, so the operator doesn't act on it
    for obj in selected_objs:
        obj.select = False
    # Select the object we actually want the operator to act on, use it, and
    # deselect.
    new_obj.select = True
    operator()
    new_obj.select = False
    # It's annoying if operators change things they shouldn't, so let's restore
    # the originally select objects.
    for obj in selected_objs:
        obj.select = True
