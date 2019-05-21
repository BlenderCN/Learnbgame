# --------------------------------------------------------------------------
# Mesh Modifiers Utilities (author Guillaume Darier)
# - Copy the modifiers from a mesh to another
# - Remove all modifiers from a mesh
# - Toggle on/off all modifiers
# - Toggle on/off specified modifiers (in a custom property named Modifiers)
# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
# --------------------------------------------------------------------------

bl_info = {
    "name": "Modifier utilities",
    "author": "Guillaume Darier",
    "version": (1, 0),
    "blender": (2, 57, 0),
    "location": "Tools > Modifier utilities",
    "description": "Provides utilities for modifiers",
    "warning": "",
    "wiki_url": ""
                "",
    "category": "Mesh",
}

"""
Usage:

Launch from "Tools -> Modifier utilities"


Additional links:
    Author Site:
    e-mail: guillaumed00 {at} gmail {dot} com
"""


import bpy
import bmesh
from bpy.props import IntProperty
from bpy.types import Operator, Panel

# The following function is adapted from 
# Nick Keeline "Cloud Generator" addNewObject 
# from object_cloud_gen.py (an addon that comes with the Blender 2.6 package)
#
def duplicateObject(scene, name, copyobj):
 
    # Create new mesh
    # mesh = bpy.data.meshes.new(name)
 
    # Create new object associated with the mesh
    # ob_new = bpy.data.objects.new(name, mesh)
    ob_new = copyobj.copy()
 
    # Copy data block from the old object into the new object
    # ob_new.data = copyobj.data.copy()
    ob_new.data = bpy.data.meshes.new(name)
    ob_new.scale = copyobj.scale
    ob_new.location = copyobj.location
    ob_new.rotation_euler = copyobj.rotation_euler
 
    # Link new object to the given scene and select it
    scene.objects.link(ob_new)
    ob_new.select = True
 
    # for mod in copyobj.modifiers:
    #     ob_new.modifiers.append(mod)

    return ob_new

def mesh_copy_modifiers(self, context):
    source = None

    # deselect everything that's not related
    # for obj in context.selected_objects:
    source = context.selected_objects[0]

    if source is None:
        self.report({'WARNING'}, "You must select a source object")
        return {'CANCELLED'}

    # get active object
    target = context.active_object

    if target is None:
        self.report({'WARNING'}, "No active object...")
        return {'CANCELLED'}

    if target == source:
        # self.report({'WARNING'}, "Source and target is same object...")
        # return {'CANCELLED'}
        source = context.selected_objects[1]

    # copy the source object
    name = target.name
    source = duplicateObject(context.scene, name, source)
    target.name = target.name + "_old"
    source.name = name

    # remove all materials from source object
    while source.data.materials:
        source.data.materials.pop(0, update_data=True)

    # remove all modifiers from target object
    while target.modifiers:
        target.modifiers.remove(target.modifiers[0])

    bpy.ops.object.select_all(action='DESELECT')
    target.select = True
    context.scene.objects.active = source
    source.select = True
    bpy.ops.object.join()

    return {'FINISHED'}

class MeshCopyModifiers(bpy.types.Operator):
    """Copies modifiers from a mesh to another """
    bl_idname = 'mesh.mesh_copy_modifiers'
    bl_label = 'Copy mesh modifiers'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return mesh_copy_modifiers(self, context)

class MeshRemoveModifiers(bpy.types.Operator):
    """Removes all modifiers from selected object"""
    bl_idname = 'mesh.mesh_remove_modifiers'
    bl_label = 'Remove modifiers'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for target in context.selected_objects:
            for idx, const in enumerate(target.modifiers):
                target.modifiers.remove(const)
        return {'FINISHED'}

class MeshToggleSpecifiedModifiers(bpy.types.Operator):
    """Toggles 3d view display of modifiers specified in object's custom property Modifiers. Write comma-separated names of modifiers to toggle"""
    bl_idname = 'mesh.mesh_toggle_specified_modifiers'
    bl_label = 'Toggle specified modifiers'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for target in context.selected_objects:
            text = target["Modifiers"]
            if text:
                for name in text.split(','):
                    for idx, const in enumerate(target.modifiers):
                        if const.name == name:
                            const.show_viewport = not const.show_viewport
        return {'FINISHED'}

class MeshToggleAllModifiers(bpy.types.Operator):
    """Toggles 3d view display of all modifiers."""
    bl_idname = 'mesh.mesh_toggle_all_modifiers'
    bl_label = 'Toggle all modifiers'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for target in context.selected_objects:
            for idx, const in enumerate(target.modifiers):
                const.show_viewport = not const.show_viewport
        return {'FINISHED'}

class c_mesh_modifiers_utilities(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Tools'
    bl_label = "Modifier utilities"
    bl_context = "objectmode"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.operator(MeshCopyModifiers.bl_idname, text="Copy mesh modifiers")
        layout.operator(MeshRemoveModifiers.bl_idname, text="Remove all modifiers")
        layout.operator(MeshToggleAllModifiers.bl_idname, text="Toggle all modifiers")
        layout.operator(MeshToggleSpecifiedModifiers.bl_idname, text="Toggle specified modifiers")

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
