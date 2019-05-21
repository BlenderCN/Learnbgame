# <pep8 compliant>
# Copyright 2011 Jacques Duflos
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
    "name": "Auto Custom Shape",
    "author": "Jacques Duflos",
    "version": (0,1),
    "blender": (2, 5, 8),
    "api": 36826,
    "location": "Properties > Bone > Create a custom shape (visible on pose or edit mode only)",
    "description": "Creates a mesh object at the bone's position and uses it as custom shape",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

"""
Auto Custom Shape
This script creates a mesh object and applies it as the selected bone's
custom shape. The mesh is created with a Copy Location and Copy rotation
and is scaled so it fits exactly to the bone.

Usage:
You have to activated the script in the "Add-Ons" tab (user preferences).
The functionality can then be accessed via
"Properties Panel" -> "Bone Properties" -> "Add custom shape"
The "Add custom shape" panel will only be visible in pose mode or edit mode.

Version history:
v0.1 - Initial revision.

More links:

TODO:

- use a matrix transformation instead of constraints and give the choice
  (constraints or matrix transfomation) to the user as a boolean option
  of the operator
- give the chois as a combo list for which primitive mesh to use
- fix the wired option
"""


import bpy
from bpy.props import FloatProperty, BoolProperty, FloatVectorProperty
from bpy_extras import object_utils
from mathutils import Vector


def add_mesh_bone(context, length=1, head_radius=0.1, tail_radius=0.1, mesh_name="Mesh bone"):
    """
    This function adds a mesh object in the scene
    """
    vertices = [
        Vector((0.10000002384185791, 0.10000002384185791, -0.09999996423721313)),
        Vector((0.10000002384185791, 0.09999996423721313, 0.10000002384185791)),
        Vector((-0.10000002384185791, 0.10000002384185791, 0.10000002384185791)),
        Vector((-0.09999996423721313, 0.10000002384185791, -0.10000002384185791)),
        Vector((0.0, 1.0, 9.536745437799254e-08)),
        Vector((0.0, -5.960462345910855e-09, -1.1920931797249068e-08)),
        Vector((0.01913417875766754, 0.046193987131118774, 0.0)),
        Vector((0.035355329513549805, 0.035355329513549805, 0.0)),
        Vector((0.046193987131118774, -0.01913417875766754, 0.0)),
        Vector((0.035355329513549805, -0.035355329513549805, 0.0)),
        Vector((0.01913417875766754, -0.046193987131118774, 0.0)),
        Vector((7.549793679118011e-09, -0.050000011920928955, 0.0)),
        Vector((-0.019134163856506348, -0.046193987131118774, 0.0)),
        Vector((-0.035355329513549805, -0.03535535931587219, 0.0)),
        Vector((-0.046193987131118774, -0.01913417875766754, 0.0)),
        Vector((-0.050000011920928955, 5.2939571825168255e-24, -4.5015168935135766e-17)),
        Vector((-0.046193987131118774, 0.01913417875766754, 0.0)),
        Vector((-0.035355329513549805, 0.03535535931587219, 0.0)),
        Vector((-0.019134148955345154, 0.046193987131118774, 0.0)),
        Vector((2.1855690590655286e-09, 0.050000011920928955, 2.980232949312267e-09)),
        Vector((1.182821840473025e-09, 0.046193987131118774, -0.019134163856506348)),
        Vector((0.0, 0.03535535931587219, -0.035355329513549805)),
        Vector((-1.182821840473025e-09, 0.01913417875766754, -0.046193987131118774)),
        Vector((-2.1855690590655286e-09, 2.980232949312267e-09, -0.050000011920928955)),
        Vector((-2.855584213534712e-09, -0.01913417875766754, -0.046193987131118774)),
        Vector((-3.0908626769132752e-09, -0.035355329513549805, -0.03535535931587219)),
        Vector((-2.855584213534712e-09, -0.046193987131118774, -0.01913417875766754)),
        Vector((-1.1828227286514448e-09, -0.046193987131118774, 0.019134163856506348)),
        Vector((-9.770253996035233e-16, -0.03535535931587219, 0.035355329513549805)),
        Vector((1.1828209522946054e-09, -0.019134193658828735, 0.046193987131118774)),
        Vector((2.1855690590655286e-09, -2.980232949312267e-09, 0.050000011920928955)),
        Vector((2.855584213534712e-09, 0.01913417875766754, 0.046193987131118774)),
        Vector((3.090860900556436e-09, 0.03535535931587219, 0.035355329513549805)),
        Vector((2.855584213534712e-09, 0.046193987131118774, 0.019134148955345154)),
        Vector((0.01913417875766754, 2.980232949312267e-09, -0.046193987131118774)),
        Vector((0.035355329513549805, 2.980232949312267e-09, -0.035355329513549805)),
        Vector((0.046193987131118774, 1.4901164746561335e-09, -0.01913417875766754)),
        Vector((0.050000011920928955, -1.776357262916724e-16, 2.1855690590655286e-09)),
        Vector((0.046193987131118774, -1.4901164746561335e-09, 0.01913417875766754)),
        Vector((0.035355329513549805, -2.980232949312267e-09, 0.035355329513549805)),
        Vector((0.01913417875766754, -2.980232949312267e-09, 0.046193987131118774)),
        Vector((-0.019134163856506348, -2.980232949312267e-09, 0.046193987131118774)),
        Vector((-0.035355329513549805, -2.980232949312267e-09, 0.03535535931587219)),
        Vector((-0.046193987131118774, -1.4901164746561335e-09, 0.01913417875766754)),
        Vector((-0.046193987131118774, 1.4901164746561335e-09, -0.01913417875766754)),
        Vector((-0.035355329513549805, 2.980232949312267e-09, -0.03535535931587219)),
        Vector((-0.019134148955345154, 2.980232949312267e-09, -0.046193987131118774)),
        Vector((-0.019134148955345154, 1.0, -0.04619389772415161)),
        Vector((-0.035355329513549805, 1.0, -0.03535526990890503)),
        Vector((-0.046193987131118774, 1.0, -0.01913413405418396)),
        Vector((-0.050000011920928955, 1.0, 9.536745437799254e-08)),
        Vector((-0.046193987131118774, 1.0, 0.019134238362312317)),
        Vector((-0.035355329513549805, 1.0, 0.03535547852516174)),
        Vector((-0.019134163856506348, 1.0, 0.04619407653808594)),
        Vector((7.549793679118011e-09, 1.0, 0.05000010132789612)),
        Vector((0.01913417875766754, 1.0, 0.04619407653808594)),
        Vector((0.035355329513549805, 1.0, 0.03535538911819458)),
        Vector((0.046193987131118774, 1.0, 0.019134238362312317)),
        Vector((0.050000011920928955, 1.0, 9.536745437799254e-08)),
        Vector((0.046193987131118774, 1.0, -0.01913413405418396)),
        Vector((0.035355329513549805, 1.0, -0.03535526990890503)),
        Vector((0.01913417875766754, 1.0, -0.04619389772415161)),
        Vector((0.0, 1.0, -0.049999892711639404)),
        Vector((2.855584213534712e-09, 1.046194076538086, 0.019134238362312317)),
        Vector((3.090860900556436e-09, 1.035355567932129, 0.03535538911819458)),
        Vector((2.855584213534712e-09, 1.019134521484375, 0.04619407653808594)),
        Vector((1.1828209522946054e-09, 0.980865478515625, 0.04619407653808594)),
        Vector((-9.770253996035233e-16, 0.9646444320678711, 0.03535538911819458)),
        Vector((-1.1828227286514448e-09, 0.9538059234619141, 0.019134238362312317)),
        Vector((-2.1855690590655286e-09, 0.9499998092651367, 9.536745437799254e-08)),
        Vector((-2.855584213534712e-09, 0.9538059234619141, -0.01913413405418396)),
        Vector((-3.0908626769132752e-09, 0.9646444320678711, -0.03535526990890503)),
        Vector((-2.855584213534712e-09, 0.980865478515625, -0.04619389772415161)),
        Vector((-1.182821840473025e-09, 1.019134521484375, -0.04619389772415161)),
        Vector((0.0, 1.035355567932129, -0.03535526990890503)),
        Vector((1.182821840473025e-09, 1.046194076538086, -0.01913413405418396)),
        Vector((2.1855690590655286e-09, 1.0500001907348633, 9.536745437799254e-08)),
        Vector((-0.019134148955345154, 1.046194076538086, 9.536745437799254e-08)),
        Vector((-0.035355329513549805, 1.035355567932129, 9.536745437799254e-08)),
        Vector((-0.046193987131118774, 1.019134521484375, 9.536745437799254e-08)),
        Vector((-0.046193987131118774, 0.980865478515625, 9.536745437799254e-08)),
        Vector((-0.035355329513549805, 0.9646444320678711, 9.536745437799254e-08)),
        Vector((-0.019134163856506348, 0.9538059234619141, 9.536745437799254e-08)),
        Vector((0.01913417875766754, 0.9538059234619141, 9.536745437799254e-08)),
        Vector((0.035355329513549805, 0.9646444320678711, 9.536745437799254e-08)),
        Vector((0.046193987131118774, 0.980865478515625, 9.536745437799254e-08)),
        Vector((0.046193987131118774, 1.019134521484375, 9.536745437799254e-08)),
        Vector((0.035355329513549805, 1.035355567932129, 9.536745437799254e-08)),
        Vector((0.01913417875766754, 1.046194076538086, 9.536745437799254e-08)),
        Vector((0.04619397595524788, 0.019134171307086945, 0.0))]

    edges = [[1, 2], [0, 1], [0, 3], [2, 3], [3, 4], [1, 4], [0, 4], [2, 4],
        [3, 5], [1, 5], [0, 5], [2, 5], [6, 7], [8, 9], [9, 10], [10, 11],
        [11, 12], [12, 13], [13, 14], [14, 15], [15, 16], [16, 17], [17, 18],
        [19, 20], [20, 21], [21, 22], [22, 23], [23, 24], [24, 25], [25, 26],
        [27, 28], [28, 29], [29, 30], [30, 31], [31, 32], [32, 33], [19, 33],
        [34, 35], [35, 36], [36, 37], [37, 38], [38, 39], [39, 40], [41, 42],
        [42, 43], [44, 45], [45, 46], [47, 62], [47, 48], [48, 49], [49, 50],
        [50, 51], [51, 52], [52, 53], [53, 54], [54, 55], [55, 56], [56, 57],
        [57, 58], [58, 59], [59, 60], [60, 61], [61, 62], [63, 76], [63, 64],
        [64, 65], [66, 67], [67, 68], [68, 69], [69, 70], [70, 71], [71, 72],
        [73, 74], [74, 75], [75, 76], [77, 78], [78, 79], [80, 81], [81, 82],
        [83, 84], [84, 85], [86, 87], [87, 88], [76, 88], [58, 86], [58, 85],
        [69, 83], [69, 82], [50, 80], [50, 79], [76, 77], [62, 73], [62, 72],
        [54, 66], [54, 65], [23, 46], [15, 44], [15, 43], [30, 41], [30, 40],
        [23, 34], [11, 27], [11, 26], [18, 19], [8, 37], [6, 19], [89, 7], [37,89]]
    faces = [[2, 3, 4], [3, 0, 4], [0, 1, 4], [1, 2, 4],
        [3, 2, 5], [0, 3, 5], [1, 0, 5], [2, 1, 5]]

    vertices=[vec*length for vec in vertices]

    mesh = bpy.data.meshes.new(mesh_name)
    mesh.vertices.add(len(vertices))
    mesh.edges.add(len(edges))
    mesh.faces.add(len(faces))
    
    for i in range(len(mesh.vertices)):
        mesh.vertices[i].co = vertices[i]
    for i in range(len(mesh.edges)):
        mesh.edges[i].vertices = edges[i]        
    for i in range(len(mesh.faces)):
        mesh.faces[i].vertices = faces[i]

    mesh.update()

    # add the mesh as an object into the scene with the utility module
    obj=object_utils.object_data_add(context, mesh)
    obj.object.show_wire = True

    return {'FINISHED'}


def main(context, wired=True):
    '''This cript will create a custome shape'''
    #### Check if selection is OK ####
    if context.selected_objects == [] or \
            context.selected_objects[0].type != 'ARMATURE':
        return {'CANCELLED'}, "No bone selected"

    # We need to be in pose mode
    mode_prec = context.object.mode
    bpy.ops.object.mode_set(mode='POSE')

    # Check that a single bone is selected
    nos = len(context.selected_pose_bones)
    if nos != 1 :
        bpy.ops.object.mode_set(mode=mode_prec)
        return {'CANCELLED'}, str(nos) + " bone(s) selected (select 1 only)"
    
    # First, we save the armature and the selected bone
    larma = context.selected_objects[0]
    larma_name = larma.name
    los = context.selected_pose_bones[0]
    los_name = los.name
    shape_name = los_name + "_cs"           # We set the name of the shape
    # Next we get the size
    size = los.length
    #### TODO: Save the matrix as well ####

    # Let's create the custom shape
    bpy.ops.object.mode_set(mode='OBJECT')
    add_mesh_bone(context, mesh_name=shape_name)
    shape = context.selected_objects[0]
    shape.name = shape_name
    
    # Next step : create a copy location+copy rotation constraint
    CopLoc = shape.constraints.new("COPY_LOCATION")
    # WARNING : larma must be a object and not an armature
    CopLoc.target = larma
    # WARNING : los_name must be a string and not a bone
    CopLoc.subtarget = los_name
    
    CopRot = shape.constraints.new("COPY_ROTATION")
    CopRot.target = larma
    CopRot.subtarget = los_name
    
    shape.scale = (size, size, size)                  # We scale the shape
    larma.pose.bones[los_name].custom_shape = shape   # Apply shape to bone
    #### TODO: use the matrix transformation ####
    #(object.data.tranansform(matrix))

    # Display wires operation moved to the operator class definition

    return {'FINISHED'}, shape, los


class BONE_OT_custom_shape(bpy.types.Operator):
    '''Creates a mesh object at the bone's position and uses it as custom shape'''
    bl_idname = "object.auto_custom_shape"
    bl_label = "Auto custom shape"
    bl_options = {'REGISTER', 'UNDO'}
#### TODO: fix that goddamned wired option ####
    #wired = BoolProperty(name="Display wire", default=True)
    
    # bl_context has nothing to do in a Operator class.
    # bl_context = ENUM in (
    #    mesh_edit, curve_edit, surface_edit, text_edit,
    #    armature_edit, mball_edit, lattice_edit, posemode,
    #    weightpaint, vertexpaint, texturepaint, particulemode)

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        issu = main(context)
        if issu[0] == {'CANCELLED'}:
            self.report('WARNING', issu[1])
            return {'CANCELLED'}
        else:
            self.report('INFO', issu[1].name + " has been created")

            # This doesn't work, wating for fixing
            #if self.wired:
            #    issu[1].draw_type = 'WIRE'
            #
            #issu[2].bone.show_wire = self.wired

            return {'FINISHED'}


class BONE_PT_custom_shape(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "bone"
    bl_label = "Create a custom shape"
    # it seams like only the first panel can be head hidden
    #bl_options = {'HIDE_HEADER'}

    @classmethod
    def poll(cls, context):
        if context.edit_bone:
            return True

        ob = context.object
        return ob and ob.mode == 'POSE' and context.bone

    def draw(self, context):
        layout = self.layout
        bone = context.bone
        if not bone:
            bone = context.edit_bone

        row = layout.row()
        row.operator("object.auto_custom_shape", text="Add Shape", icon='BONE_DATA')


def register():
    bpy.utils.register_class(BONE_OT_custom_shape)
    bpy.utils.register_class(BONE_PT_custom_shape)


def unregister():
    bpy.utils.unregister_class(BONE_OT_custom_shape)
    bpy.utils.unregister_class(BONE_PT_custom_shape)


if __name__ == "__main__":
    register()

