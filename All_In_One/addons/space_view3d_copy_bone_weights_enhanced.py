# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****
bl_info = {
    "name": "Copy Bone Weights",
    "author": "Luke Hares, Gaia Clary, IRIE Shinsuke",
    "version": (0, 1),
    "blender": (2, 80, 0),  # or (2, 79, 0)
    "location": "View3D > Tool Shelf > Copy Bone Weights Panel",
    "description": "Copy Bone Weights from Active Object to Selected Objects",
    "tracker_url": "https://github.com/iRi-E/blender_copy_bone_weights/issues",
    "category": "Learnbgame",
    }
    
import bpy
import mathutils
from contextlib import redirect_stdout
import io



blender28 = bpy.app.version[0] == 2 and bpy.app.version[1] >= 80 or bpy.app.version[0] >= 3


def boneWeightCopy(tempObj, targetObject, onlyNamedBones, keepEmptyGroups):
    modifiers = tempObj.modifiers
    mesh = tempObj.data

    boneSet = []
    for modifier in modifiers:
        if modifier.type == 'ARMATURE':
            armature = modifier.object.data
            bones = armature.bones

            for bone in bones:
                boneSet.append(bone.name)

                if keepEmptyGroups:
                    if bone.use_deform and bone.name not in targetObject.vertex_groups:
                        targetObject.vertex_groups.new(bone.name)

    # get active object vertices and transform to world space
    WSTargetVertsCo = [targetObject.matrix_world @ v.co if blender28 else targetObject.matrix_world * v.co
                       for v in targetObject.data.vertices]

    kd = None
    ncopied = 0

    for targetVert, WSTargetVertCo in zip(targetObject.data.vertices, WSTargetVertsCo):
        if targetVert.select:
            try:
                faceFound, nearestCo, normal, faceIndex = tempObj.closest_point_on_mesh(WSTargetVertCo)
            except RuntimeError:  # there is no polygon
                faceFound = False

            if faceFound:
                polygon = mesh.polygons[faceIndex].vertices
                ipWeights = mathutils.interpolate.poly_3d_calc([mesh.vertices[i].co for i in polygon], nearestCo)
            else:
                # fallback
                if not kd:
                    print("falling back to nearest vertex method...")

                    # build kd-tree
                    size = len(mesh.vertices)
                    kd = mathutils.kdtree.KDTree(size)
                    for i, v in enumerate(mesh.vertices):
                        kd.insert(v.co, i)
                    kd.balance()

                nearestCo, activeIndex, minDist = kd.find(WSTargetVertCo)

            copied = False
            for group in tempObj.vertex_groups:
                groupName = group.name

                if (groupName in boneSet or not onlyNamedBones):
                    if faceFound:
                        weight = 0.0

                        for i, w in zip(polygon, ipWeights):
                            try:
                                weight += group.weight(i) * w
                            except RuntimeError:  # vertex doesn't belong to this group
                                pass
                    else:
                        try:
                            weight = group.weight(activeIndex)
                        except RuntimeError:  # nearest vertex doesn't belong to this group
                            weight = 0.0

                    if weight:
                        if groupName not in targetObject.vertex_groups:
                            targetObject.vertex_groups.new(name=groupName)

                        targetObject.vertex_groups[groupName].add([targetVert.index], weight, 'REPLACE')
                        copied = True
                    elif groupName in targetObject.vertex_groups:
                        targetObject.vertex_groups[groupName].remove([targetVert.index])

            if copied:
                ncopied += 1

    return ncopied


def main(context):
    '''Copies the bone weights'''

    if context.active_object.type != 'MESH':
        return

    targetObjects = context.selected_objects
    baseObj = context.active_object

    bpy.ops.object.select_all(action='DESELECT')
    if blender28:
        baseObj.select_set(True)
    else:
        baseObj.select = True

    bpy.ops.object.duplicate()
    tempObj = context.active_object

    # apply mirrors, to process target objects not mirrored
    for modifier in tempObj.modifiers:
        if modifier.type == 'MIRROR':
            if tempObj.data.shape_keys:
                bpy.ops.object.shape_key_remove(all=True)
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier=modifier.name)

    for v in tempObj.data.vertices:
        v.co = baseObj.matrix_world @ v.co if blender28 else baseObj.matrix_world * v.co

    for targetObject in targetObjects:
        if (targetObject.type == 'MESH') & (targetObject != baseObj):
            print("Copy bone weights from '{}' to '{}'".format(baseObj.name, targetObject.name))
            n = boneWeightCopy(tempObj, targetObject,
                               context.scene.copy_bone_weights.named_bones,
                               context.scene.copy_bone_weights.empty_groups)
            print("Transferred weights of {} vertices".format(n))

    with redirect_stdout(io.StringIO()):  # quiet "Info: Deleted 1 object(s)"
        bpy.ops.object.delete()


# Copy Bone Weights Operator
class OBJECT_OT_copy_bone_weights(bpy.types.Operator):
    '''Copy bone weights from active object to selected vertices in other selected objects'''

    bl_idname = "object.copy_bone_weights"
    bl_label = "Copy Bone Weights Active Object to Selected Objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        main(context)
        return {'FINISHED'}


# User interface
class VIEW3D_MT_copy_bone_weights(bpy.types.Menu):
    bl_label = "Copy Bone Weights"

    def draw(self, context):
        layout = self.layout
        cbw = context.scene.copy_bone_weights

        col = layout.column()
        col.operator("object.copy_bone_weights", text="Copy Bone Weights")
        col.prop(cbw, 'named_bones')
        col.prop(cbw, 'empty_groups')


def copy_bone_weights_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.menu("VIEW3D_MT_copy_bone_weights", icon="PLUGIN")


# Properties
class CopyBoneWeightsProps(bpy.types.PropertyGroup):
    named_bones = bpy.props.BoolProperty(
        name="Only Named Bones",
        description="Copy only the bone related weight groups to Target (Skip all other weight groups)",
        default=False)

    empty_groups = bpy.props.BoolProperty(
        name="Copy Empty Groups",
        description="Create bone related weight groups in Target, even if they contain no vertices",
        default=False)


# Register
classes = (
    OBJECT_OT_copy_bone_weights,
    CopyBoneWeightsProps,
    VIEW3D_MT_copy_bone_weights,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_object.append(copy_bone_weights_menu)
    bpy.types.VIEW3D_MT_paint_weight.append(copy_bone_weights_menu)

    bpy.types.Scene.copy_bone_weights = bpy.props.PointerProperty(type=CopyBoneWeightsProps)


def unregister():
    del bpy.types.Scene.copy_bone_weights

    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_object.remove(copy_bone_weights_menu)
    bpy.types.VIEW3D_MT_paint_weight.remove(copy_bone_weights_menu)


if __name__ == "__main__":
    register()
