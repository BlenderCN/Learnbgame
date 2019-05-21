
bl_info = {
    "name": "Petgame Transformation Export",
    "description": "petgame transformation exporter",
    "author": "Joe Harding",
    "version": (1, 0),
    "blender": (2, 69, 0),
    "location": "File > Export",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

import bpy
import bmesh
import io
import os
import pprint
import mathutils

from bpy_extras.io_utils import ExportHelper


class BoneTransformation:

    def __init__(self, bone_name, translation_vector, scale_vector, rotation_euler):
        self.bone_name = bone_name
        self.translation_vector = translation_vector
        self.scale_vector = scale_vector
        self.rotation_euler = rotation_euler
        # calculate the quaternion since that is what we actuall want to export
        self.rotation_quat = self.rotation_euler.to_quaternion()

    def get_name(self):
        return self.bone_name

    def get_trans(self):
        return self.translation_vector

    def get_scale(self):
        return self.scale_vector

    # phi is rotation about the x axis
    def get_phi(self):
        return self.rotation_euler[0]

    # theta is rotation about the y axis
    def get_theta(self):
        return self.rotation_euler[1]
 
    # psi is rotation about the z axis
    def get_psi(self):
        return self.rotation_euler[2]

    def get_q_w(self):
        return self.rotation_quat[0]

    def get_q_x(self):
        return self.rotation_quat[1]

    def get_q_y(self):
        return self.rotation_quat[2]

    def get_q_z(self):
        return self.rotation_quat[3]


class Frame:

    def __init__(self, frame_index):
        self.frame_index = frame_index
        self.bone_transformations = []

    def add_bone_transformation(self, bone_transformation):
        self.bone_transformations.append(bone_transformation)

    def get_bone_transformations(self):
        return self.bone_transformations

    def get_index(self):
        return self.frame_index


class ExportTransformation(bpy.types.Operator, ExportHelper):

    filename_ext = ".xml"

    # unique identifier for buttons and menu items to reference.
    bl_idname = "io.export_petgame_transformation"

    # display name in the interface.
    bl_label = "Petgame Transformation Export"

    # enable undo for the operator.
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self):
        pass

    # execute() is called by blender when running the operator.
    def execute(self, context):
        print("XML Transformation Export Script Start")

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
    
        # assume if there is no filepath that we are exporting all
        if self.filepath == "":
            for action in bpy.data.actions:
                bpy.context.object.animation_data.action = action 
                self.export_action(action)
        else: 
            self.export_action(bpy.context.object.animation_data.action)

        print("XML Transformation Export Script End")
        return {'FINISHED'}

    def export_action(self, action):
        frame_range = action.frame_range
        start_frame = int(frame_range[0])
        end_frame = int(frame_range[1])

        # get the world matrix so we can use it to convert local coords to global coords
        world_matrix = bpy.context.active_object.matrix_world

        bone_starting = []
        for bone in bpy.context.object.data.bones:
            if bone.parent is not None:
                if bone.name == "tail":
                    print("tail head_local: {hl}".format(hl=bone.head_local))
                    print("tail parent tail_local: {ptl}".format(ptl=bone.parent.tail_local))
                bone_starting.append({"name": bone.name, "starting": world_matrix * bone.head_local})

        frames = []
        for frame_index in range(start_frame, end_frame, 1):
            print("frame index: {frame_index}".format(frame_index=frame_index))
            bpy.context.scene.frame_set(frame_index)

            current_frame = Frame(frame_index)

            for bone in bpy.context.object.pose.bones:
                print("****BONE : {bone_name} ****".format(bone_name=bone.name))

                euler_rot = bone.rotation_euler;
                print("euler rotation: {euler_rot}".format(euler_rot=euler_rot))

                # we animate rotations using eulers, but we'll export as quats
                # we calculate in BoneTransformation init
                #quat_rot = bone.rotation_quaternion
                #print("quat rotation: {quat_rot}".format(quat_rot=quat_rot))
                
                # this operation solves our problem of having unified coords but also having
                # our translation be parent relative
                inv = bone.matrix_basis.inverted() * bone.matrix
                t, q, s = inv.decompose()
                q_m = q.to_matrix().to_4x4()

                translation = bone.matrix_basis.translation.copy()
                scale = bone.matrix.to_scale()

                bone_t = BoneTransformation(bone.name, translation, scale, euler_rot.copy())
                current_frame.add_bone_transformation(bone_t)

            frames.append(current_frame)

        filepath = self.filepath
        if filepath == "":
            filepath = "transformation_{f}_{a}"
            filepath = filepath.format(f=bpy.path.basename(bpy.context.blend_data.filepath).split('.')[0], a=action.name)
            print("no filename set, assuming running from command line and setting filename to {name}".format(name=filepath))
        self.printXML(frames, filepath)



    def printXML(self, frames, filepath):

        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)

        print('Exporting to XML file "{path}"...'.format(path=filepath))

        file = open(filepath, "w")
        fw = file.write
        fw('<!-- petgame transformation -->\n')
        fw('<frames>\n')
        for frame in frames:
            fw('<frame index="{frame_index}">\n'.format(frame_index=frame.get_index()))
            for bone_t in frame.get_bone_transformations():

                xml_string = '<bone name="{bone_name}">\n'
                fw(xml_string.format(bone_name=bone_t.get_name()))

                xml_string = '<translation x="{trans_x}" y="{trans_y}" z="{trans_z}"/>\n'
                fw(xml_string.format(trans_x=-bone_t.get_trans().x, trans_y=bone_t.get_trans().y, trans_z=-bone_t.get_trans().z))

                xml_string = '<scale x="{scale_x}" y="{scale_y}" />\n'
                fw(xml_string.format(scale_x=bone_t.get_scale().x, scale_y=bone_t.get_scale().y))

                xml_string = '<rotation w="{w}" x="{x}" y="{y}" z="{z}" />\n'
                fw(xml_string.format(w=bone_t.get_q_w(), x=bone_t.get_q_x(), y=bone_t.get_q_y(), z=-bone_t.get_q_z()))

                fw('</bone>\n')

            fw('</frame>\n')

        fw('</frames>\n')

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
    self.layout.operator(ExportTransformation.bl_idname, text="Petgame Transformation (.xml)")


def register():
    bpy.utils.register_class(ExportTransformation)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportTransformation)

# This allows you to run the script directly from blenders text editor
# to test the addon without having to install it.
if __name__ == '__main__':
    register()
    # while testing the script it's easier to just run from command line:
    # blender ~/assets/blender_source/test.blend --background --python ~/petgame/utils/io_export_petgame_transformation.py
    bpy.ops.io.export_petgame_transformation()
