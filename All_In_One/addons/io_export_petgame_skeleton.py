
bl_info = {
    "name": "Petgame Skeleton Export",
    "description": "petgame skeleton exporter",
    "author": "Joe Harding",
    "version": (1, 0),
    "blender": (2, 69, 0),
    "location": "File > Export",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

import bpy
import io
import pprint
import mathutils

from bpy_extras.io_utils import ExportHelper


class BoneTemplate:

    def __init__(self, name):
        self.name = name;
        self.parent_name = "none";

    def get_name(self):
        return self.name

    def get_parent_name(self):
        return self.parent_name

    def get_head_offset(self):
        return self.head_offset

    def get_tail_offset(self):
        return self.tail_offset

    def set_parent(self, parent_name):
        self.parent_name = parent_name

    def set_head_offset(self, offset):
        self.head_offset = offset

    def set_tail_offset(self, offset):
        self.tail_offset = offset


class ExportSkeleton(bpy.types.Operator, ExportHelper):

    filename_ext = ".xml"

    # unique identifier for buttons and menu items to reference.
    bl_idname = "io.export_petgame_skeleton"

    # display name in the interface.
    bl_label = "Petgame Skeleton Export"

    # enable undo for the operator.
    bl_options = {'REGISTER', 'UNDO'}

    # b/c we extend operator, execute is called by blender when running the operator
    def execute(self, context):
        print("### XML Skeleton Export Script Start ###")

        # switch to object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # start off by deselecting everything
        bpy.ops.object.select_all(action='DESELECT')

        # select only the armature
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE':
                print("selecting armature: {name} for export...".format(name=obj.name))
                obj.select = True
                # we have to select the armature AND set it to be active (yellow highlight)
                bpy.context.scene.objects.active = obj

        # switch to edit mode so we can modify the bones
        bpy.ops.object.mode_set(mode='EDIT')

        # make sure that every bone's roll is consistent and aligned on the correct axis
        z_axis_vector = mathutils.Vector()
        z_axis_vector.y = 1.0
        for edit_bone in bpy.context.object.data.edit_bones:
            edit_bone.align_roll(z_axis_vector)

        # return to object mode for consitency
        bpy.ops.object.mode_set(mode='OBJECT')

        # create the bone templates
        bones = []
        for bone in bpy.context.object.data.bones:
            print("***name:")
            print(bone.name)
            bone_template = BoneTemplate(bone.name)

            # get the world matrix so we can use it to convert local coords to global coords
            world_matrix = bpy.context.active_object.matrix_world

            if bone.parent:
                print("parent.tail_local: {p_tail_local}".format(p_tail_local=bone.parent.tail_local))
                bone_template.set_head_offset((bone.head_local - bone.parent.tail_local) * world_matrix)
            else:
                bone_template.set_head_offset(bone.head_local * world_matrix)

            my_tail_offset = ((bone.tail_local - bone.head_local) * world_matrix)
            bone_template.set_tail_offset(my_tail_offset)

            if bone.parent:
                bone_template.set_parent(bone.parent.name)

            bones.append(bone_template)

        self.print_xml(bones)

        print("### XML Skeleton Export Script End ###")
        # this lets blender know the operator finished successfully.
        return {'FINISHED'}


    def print_xml(self, bones):
        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)

        print('Exporting to XML file "{path}"...'.format(path=filepath))

        file = open(filepath, "w")
        fw = file.write
        fw('<!-- petgame skeleton {v} -->\n'.format(v=bl_info["version"]))
        fw('<bones>\n')
        for bone in bones:

            xml_string = '<bone name="{bone_name}" parentName="{parent_bone_name}">\n'
            fw(xml_string.format(bone_name=bone.get_name(), parent_bone_name=bone.get_parent_name()))

            xml_string = '<headOffset x="{head_x}" y="{head_y}" />\n'
            fw(xml_string.format(head_x=bone.get_head_offset().x, head_y=bone.get_head_offset().z))

            xml_string = '<tailOffset x="{tail_x}" y="{tail_y}" />\n'
            fw(xml_string.format(tail_x=bone.get_tail_offset().x, tail_y=bone.get_tail_offset().z))

            fw('</bone>\n')

        fw('</bones>\n')

        file.close()


    def invoke(self, context, event):
        wm = context.window_manager

        if True:
            # File selector
            wm.fileselect_add(self) # will run self.execute()
            return {'RUNNING_MODAL'}
        elif True:
            # search the enum
            wm.invoke_search_popup(self)
            return {'RUNNING_MODAL'}
        elif False:
            # Redo popup
            return wm.invoke_props_popup(self, event)
        elif False:
            return self.execute(context)


def menu_func_export(self, context):
    self.layout.operator(ExportSkeleton.bl_idname, text="Petgame Skeleton (.xml)")


def register():
    bpy.utils.register_class(ExportSkeleton)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportSkeleton)


# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
if __name__ == '__main__':
    register()
