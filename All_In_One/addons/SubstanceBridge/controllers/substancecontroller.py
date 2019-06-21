# -----------------------------------------------------------------------------
# Substance Controller
#
# This file contains many function, name project, add texture set list...
# All function are create in an operator.
# 
# -----------------------------------------------------------------------------

import bpy
from bpy.props import IntProperty


# -----------------------------------------------------------------------------
# Create a News Substance Project
# -----------------------------------------------------------------------------
class CreateSubstanceProject(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "sbs_painter.substance_name"
    bl_label = "Create a new Substance Painter project"

    def execute(self, context):
        scn = context.scene
        slct_obj = bpy.context.selected_objects
        sbs_settings = scn.sbs_project_settings

        # Check if this object can be export for Sbs Painter.
        for obj in slct_obj:
            if obj.type == 'MESH':
                # Add attribute for all mesh selected
                obj['substance_project'] = sbs_settings.prj_name

                # Clear Material slot
                nbr = len(bpy.data.objects[obj.name].material_slots)
                for i in range(nbr):
                    bpy.ops.object.material_slot_remove()

                # Add a materials basic.
                base_mat = bpy.data.materials.get(sbs_settings.prj_name)
                if base_mat is None:
                    base_mat = bpy.data.materials.new(sbs_settings.prj_name)

                # Asign materials to all object selected
                if obj.data.materials:
                    obj.data.materials[0] = base_mat

                else:
                    obj.data.materials.append(base_mat)

            else:
                self.report({'WARNING'}, "This object is not a mesh.")
                return {'CANCELLED'}

        return {'FINISHED'}


# -----------------------------------------------------------------------------
# Function Selected Project
# -----------------------------------------------------------------------------
class SelectedProject(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "sbs_painter.selected_project"
    bl_label = "Selected mesh with this project"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        scn = context.scene
        all_obj = bpy.data.objects
        project_name = scn.sbs_project_settings.prj_name

        for obj in all_obj:
            name_obj = bpy.data.objects[obj.name]
            if obj.get('substance_project') is not None:
                name_prj = bpy.data.objects[obj.name]['substance_project']
                if name_prj == project_name:
                    name_obj.select = True

                else:
                    name_obj.select = False
            else:
                name_obj.select = False

        return {'FINISHED'}


# -----------------------------------------------------------------------------
# Function Remove form an Project
# -----------------------------------------------------------------------------
class RemovefromProject(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "sbs_painter.remove_from_project"
    bl_label = "Selected mesh with this project"

    def execute(self, context):
        obj = context.object

        del obj['substance_project']

        return {'FINISHED'}


# -----------------------------------------------------------------------------
# Function unwrap set list, use multi object uv edit to be functional.
# -----------------------------------------------------------------------------
class TextureSetUnwrap(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "sbs_painter.uv_set"
    bl_label = "Unwrap mode for a texture set list"

    def execute(self, context):
        bpy.ops.sbs_painter.selected_project()
        bpy.ops.object.multi_object_uv_edit('INVOKE_DEFAULT')

        return {'FINISHED'}


# -----------------------------------------------------------------------------
# Function to add a new set list.
# -----------------------------------------------------------------------------
class TextureSetAdd(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "sbs_painter.uv_set_add"
    bl_label = "Add a new texture set list."

    def execute(self, context):
        scn = context.scene
        all_obj = bpy.data.objects
        slc_obj = bpy.context.active_object
        project_name = scn.sbs_project_settings.prj_name
        sbs_settings = scn.sbs_project_settings

        # Create a new material.
        nbr = len(slc_obj.material_slots)
        name_mat = project_name
        name_mat = name_mat + "_set_" + str(nbr)
        new_mat = bpy.data.materials.new(name_mat)

        for obj in all_obj:
            name_obj = bpy.data.objects[obj.name]
            if obj.get('substance_project') is not None:
                name_prj = bpy.data.objects[obj.name]['substance_project']
                if name_prj == project_name:
                    obj.data.materials.append(new_mat)

        return {'FINISHED'}


# -----------------------------------------------------------------------------
# Make a set list as a referential
# -----------------------------------------------------------------------------
class TextureSetOn(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "sbs_painter.uv_set_on"
    bl_label = "Make an set list on first."

    # Generate a index variable, need to count all set list used.
    index = IntProperty(
        name="Index Material",
        default=0,
    )

    def execute(self, context):
        slc_obj = bpy.context.active_object
        # Count a nbr of materials
        nbr = len(slc_obj.material_slots)
        # Select the index material.
        bpy.context.object.active_material_index = self.index

        # Create a loop to move the material on the first positon
        for i in range(nbr):
            bpy.ops.object.material_slot_move(direction='UP')
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='TOGGLE')
            bpy.ops.object.material_slot_assign()
            bpy.ops.object.editmode_toggle()

        return {'FINISHED'}


def register():
    bpy.utils.register_class(CreateSubstanceProject)
    bpy.utils.register_class(SelectedProject)
    bpy.utils.register_class(RemovefromProject)
    # Texture Set Functions
    bpy.utils.register_class(TextureSetUnwrap)
    bpy.utils.register_class(TextureSetAdd)
    bpy.utils.register_class(TextureSetOn)


def unregister():
    bpy.utils.unregister_class(CreateSubstanceProject)
    bpy.utils.unregister_class(SelectedProject)
    bpy.utils.unregister_class(RemovefromProject)
    # Texture Set Functions
    bpy.utils.unregister_class(TextureSetUnwrap)
    bpy.utils.unregister_class(TextureSetAdd)
    bpy.utils.unregister_class(TextureSetOn)
