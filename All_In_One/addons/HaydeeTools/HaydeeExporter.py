
import bpy
import os
import struct
import math
import io
import re
from .HaydeeUtils import d, find_armature
from .HaydeeUtils import boneRenameHaydee, materials_list, stripName, NAME_LIMIT
from . import HaydeeMenuIcon
from bpy_extras.wm_utils.progress_report import (
    ProgressReport,
    ProgressReportSubstep,
)

# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

from mathutils import *
from math import pi


# ------------------------------------------------------------------------------
#  .dskel exporter
# ------------------------------------------------------------------------------

def write_dskel(operator, context, filepath):
    armature = find_armature(operator, context)
    if armature == None:
        return {'FINISHED'}

    bones = armature.data.bones

    f = open(filepath, 'w', encoding='utf-8')
    f.write("HD_DATA_TXT 300\n\n")
    f.write("skeleton %d\n{\n" % len(bones))
    r = Quaternion([0, 0, 1], -pi/2)
    for bone in bones:
        head = bone.head_local.xzy
        q = bone.matrix_local.to_quaternion()
        q = (q @ r)
        q = Quaternion([-q.w, q.x, q.y, -q.z])

        bone_name = boneRenameHaydee(bone.name)

        bone_side = bone.length / 4
        f.write("\tbone %s\n\t{\n" % bone_name)
        f.write("\t\twidth %s;\n" % d(bone_side))
        f.write("\t\theight %s;\n" % d(bone_side))
        f.write("\t\tlength %s;\n" % d(bone.length))

        if bone.parent:
            parent_name = boneRenameHaydee(bone.parent.name)
            f.write("\t\tparent %s;\n" % parent_name)
            head = bone.head_local
            head = Vector((head.x, head.z, head.y))

        head = Vector((-head.x, head.y, -head.z))
        q = Quaternion([q.x, q.z, q.y, q.w])
        f.write("\t\torigin %s %s %s;\n" % (d(head.x), d(head.y), d(head.z)))
        f.write("\t\taxis %s %s %s %s;\n" % (d(q.w), d(q.x), d(q.y), d(q.z)))
        f.write("\t}\n")

    f.write("}\n")
    f.close();
    return {'FINISHED'}


class ExportHaydeeDSkel(Operator, ExportHelper):
    bl_idname = "haydee_exporter.dskel"
    bl_label = "Export Haydee DSkel (.dskel)"
    bl_options = {'REGISTER'}
    filename_ext = ".dskel"
    filter_glob : StringProperty(
            default="*.dskel",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        return write_dskel(self, context, self.filepath)


# --------------------------------------------------------------------------------
#  .dpose exporter
# --------------------------------------------------------------------------------

def write_dpose(operator, context, filepath):
    armature = find_armature(operator, context)
    if armature == None:
        return {'FINISHED'}

    bones = armature.pose.bones

    f = open(filepath, 'w', encoding='utf-8')
    f.write("HD_DATA_TXT 300\n\n")
    f.write("pose\n{\n\tnumTransforms %d;\n" % len(bones))
    r = Quaternion([0, 0, 1], pi/2)
    for bone in bones:
        head = bone.head.xzy
        q = bone.matrix.to_quaternion()
        q = -(q @ r)
        if bone.parent:
            head = bone.parent.matrix.inverted().to_quaternion() @ (bone.head - bone.parent.head)
            head = Vector((-head.y, head.z, head.x))
            q = (bone.parent.matrix.to_3x3().inverted() @ bone.matrix.to_3x3()).to_quaternion()
            q = Quaternion([q.z, -q.y, q.x, -q.w])

        f.write("\ttransform %s %s %s %s %s %s %s %s;\n" % (
            boneRenameHaydee(bone.name), \
            d(-head.x), d(head.y), d(-head.z),
            d(q.x), d(-q.w), d(q.y), d(q.z)))

    f.write("\t}\n")
    f.close();
    return {'FINISHED'}


class ExportHaydeeDPose(Operator, ExportHelper):
    bl_idname = "haydee_exporter.dpose"
    bl_label = "Export Haydee DPose (.dpose)"
    bl_options = {'REGISTER'}
    filename_ext = ".dpose"
    filter_glob : StringProperty(
            default="*.dpose",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        return write_dpose(self, context, self.filepath)


# --------------------------------------------------------------------------------
#  .dmot exporter
# --------------------------------------------------------------------------------

def write_dmot(operator, context, filepath):
    armature = find_armature(operator, context)
    if armature == None:
        return {'FINISHED'}

    bones = armature.pose.bones
    keyframeCount = bpy.context.scene.frame_end - bpy.context.scene.frame_start + 1
    previousFrame = bpy.context.scene.frame_current
    wm = bpy.context.window_manager

    lines = {}
    for bone in bones:
        name = boneRenameHaydee(bone.name)
        lines[name] = []

    r = Quaternion([0, 0, 1], pi/2)
    wm.progress_begin(0, keyframeCount)
    for frame in range(keyframeCount):
        wm.progress_update(frame)
        context.scene.frame_set(frame + bpy.context.scene.frame_start)
        for bone in bones:

            head = bone.head.xzy
            q = bone.matrix.to_quaternion()
            q = -(q @ r)
            if bone.parent:
                head = bone.parent.matrix.inverted().to_quaternion() @ (bone.head - bone.parent.head)
                head = Vector((-head.y, head.z, head.x))
                q = (bone.parent.matrix.to_3x3().inverted() @ bone.matrix.to_3x3()).to_quaternion()
                q = Quaternion([-q.z, -q.y, q.x, -q.w])

            name = boneRenameHaydee(bone.name)
            lines[name].append("\t\tkey %s %s %s %s %s %s %s;\n" % (
                d(-head.x), d(head.y), d(-head.z),
                d(q.x), d(q.w), d(q.y), d(q.z)))
    wm.progress_end()

    context.scene.frame_set(previousFrame)

    f = open(filepath, 'w', encoding='utf-8')
    f.write("HD_DATA_TXT 300\n\n")
    f.write("motion\n{\n");
    f.write("\tnumTracks %d;\n" % len(bones))
    f.write("\tnumFrames %d;\n" % keyframeCount)
    f.write("\tframeRate %g;\n" % context.scene.render.fps)
    for bone in bones:
        name = boneRenameHaydee(bone.name)
        f.write("\ttrack %s\n\t{\n" % name)
        f.write("".join(lines[name]))
        f.write("\t}\n")
    f.write("}\n")
    f.close();
    return {'FINISHED'}


class ExportHaydeeDMotion(Operator, ExportHelper):
    bl_idname = "haydee_exporter.dmot"
    bl_label = "Export Haydee DMotion (.dmot)"
    bl_options = {'REGISTER'}
    filename_ext = ".dmot"
    filter_glob : StringProperty(
            default="*.dmot",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        return write_dmot(self, context, self.filepath)


# --------------------------------------------------------------------------------
#  .dmesh exporter
# --------------------------------------------------------------------------------

def write_dmesh(operator, context, filepath, export_skeleton, \
        apply_modifiers, selected_only, separate_files, \
        ignore_hidden, SELECTED_MATERIAL):
    print("Exporting mesh, material: %s" % SELECTED_MATERIAL)

    mesh_count = 0
    for ob in context.scene.objects:
        if ob.type == "MESH":
            if SELECTED_MATERIAL == '__ALL__':
                mesh_count += 1
            else:
                for n in range(len(ob.material_slots)):
                    if ob.material_slots[n].name == SELECTED_MATERIAL:
                        mesh_count += 1
                        break

    if selected_only:
        list = context.selected_objects
        if len(list) == 0:
            list = context.scene.objects
    else:
        list = context.scene.objects

    (vertex_output, uvs_output, groups_output, groups_count,
        joints_output, weights_output, weights_count, group_count,
        base_vertex_index, base_uv_index, armature, unique_uvs_pos,
        uvs_dict) = reset_variables()
    group_name = None

    for ob in sorted([x for x in list if x.type=='MESH'], key=lambda ob: ob.name):
        if ob.type == "MESH":
            #TODO ignore hidden objects
            if ignore_hidden and ob.hide_viewport:
                continue

            if separate_files:
                (vertex_output, uvs_output, groups_output, groups_count,
                joints_output, weights_output, weights_count, group_count,
                base_vertex_index, base_uv_index, armature, unique_uvs_pos,
                uvs_dict) = reset_variables()

            settings = 'PREVIEW'
            #//XXX TO MESH
            mesh = ob.to_mesh(context.depsgraph, apply_modifiers)
            mat = ob.matrix_world
            vertices = mesh.vertices
            materials = mesh.materials
            polygons = mesh.polygons
            material_index = -1
            if len(mesh.uv_layers) >= 1:
                uvs_data = mesh.uv_layers[0].data
            else:
                uvs_data = None

            first_uv_index = base_uv_index
            first_vertex_index = base_vertex_index
            vertex_map = {}
            new_mesh_uvs = []
            if SELECTED_MATERIAL == '__ALL__':
                for n in range(len(vertices)):
                    vertex_map[n] = base_vertex_index+n
                if uvs_data != None:
                    for n, uv in enumerate(uvs_data):
                        uv_pos = uv.uv
                        if uv_pos in unique_uvs_pos:
                            idx = unique_uvs_pos.index(uv_pos)
                        else:
                            idx = len(unique_uvs_pos)
                            unique_uvs_pos.append(uv_pos)
                            new_mesh_uvs.append(uv_pos)
                        uvs_dict.append(idx)
                    base_uv_index += len(uvs_data)
                base_vertex_index += len(vertices)
            else:
                for n in range(len(ob.material_slots)):
                    if ob.material_slots[n].name == SELECTED_MATERIAL:
                        material_index = n
                        break
                if material_index == -1:
                    print("Ignoring mesh %s since no material %s found" % (ob.name, SELECTED_MATERIAL))
                    continue
                for polygon in mesh.polygons:
                    if polygon.material_index == material_index:
                        if uvs_data != None:
                            for uvIdx in polygon.loop_indices:
                                uv_pos = uvs_data[uvIdx].uv
                                if uv_pos in unique_uvs_pos:
                                    idx = unique_uvs_pos.index(uv_pos)
                                else:
                                    idx = len(unique_uvs_pos)
                                    unique_uvs_pos.append(uv_pos)
                                    new_mesh_uvs.append(uv_pos)
                                uvs_dict.append(idx)
                                base_uv_index += 1
                        for vertex in polygon.vertices:
                            if not (vertex in vertex_map):
                                vertex_map[vertex] = base_vertex_index
                                base_vertex_index += 1
                if len(vertex_map) == 0:
                    print("Ignoring mesh %s since no vertices found with material %s" % (ob.name, SELECTED_MATERIAL))
                    continue

            if uvs_data == None:
                operator.report({'ERROR'}, "Mesh " + ob.name + " is missing UV information")
                continue
            # Export vertices
            vertex_count = base_vertex_index - first_vertex_index
            print ("Exporting %d vertices" % vertex_count)
            vertex_indexes = [0] * vertex_count
            for key, value in vertex_map.items():
                vertex_indexes[value - first_vertex_index] = key
            for index in vertex_indexes:
                v = vertices[index]
                co = mat @ v.co
                vertex_output.append("\t\tvert %s %s %s;\n" % (d(-co.x), d(co.z), d(-co.y)))

            # Export UV map
            uv_count = base_uv_index - first_uv_index
            print ("Exporting %d uvs" % uv_count)
            uv_indexes = [-1] * uv_count
            if len(mesh.uv_layers) >= 1:
                for uv in new_mesh_uvs:
                    uvs_output.append("\t\tuv %s %s;\n" % (d(uv.x), d(uv.y)))

            EXPORT_SMOOTH_GROUPS = False
            EXPORT_SMOOTH_GROUPS_BITFLAGS = True
            if (EXPORT_SMOOTH_GROUPS or EXPORT_SMOOTH_GROUPS_BITFLAGS):
                smooth_groups, smooth_groups_tot = mesh.calc_smooth_groups(use_bitflags=EXPORT_SMOOTH_GROUPS_BITFLAGS)
                if smooth_groups_tot <= 1:
                    smooth_groups, smooth_groups_tot = (), 0
            else:
                smooth_groups, smooth_groups_tot = (), 0

            # Export faces (by material)
            current_material_index = -1

            if SELECTED_MATERIAL == '__ALL__':
                current_material_index += 1
                if material_index != -1 and material_index != current_material_index:
                    continue
                count = 0
                for polygon in polygons:
                    if polygon.material_index == current_material_index:
                        count += 1
                if count == 0:
                    continue

                if len(materials) > 1:
                    group_name = ob.name + '_' + mat.name
                else:
                    group_name = ob.name
                regex=re.compile('^[0-9]')
                if regex.match(group_name):
                    group_name = 'x' + group_name
                group_name = stripName(group_name)
                group_name = group_name[:NAME_LIMIT]
#                if not group_name:
#                    operator.report({'ERROR'}, "Mesh " + ob.name + ", no group name")
#                    continue
                print(group_name, 'count', count)
                if group_name in groups_output:
                    group_output = groups_output[group_name]
                else:
                    group_output = []
                    groups_count[group_name] = 0

                for polygon in polygons:
                    if polygon.material_index == current_material_index:
                        groups_count[group_name] += 1
                        group_output.append("\t\t\tface\n\t\t\t{\n")
                        group_output.append("\t\t\t\tcount %d;\n" % len(polygon.vertices))
                        group_output.append("\t\t\t\tverts ");
                        for v in tuple(polygon.vertices)[::-1]:
                            group_output.append(" %d" % vertex_map[v]);
                        group_output.append(";\n")
                        if uvs_data != None:
                            group_output.append("\t\t\t\tuvs ");
                            for v in tuple(polygon.loop_indices)[::-1]:
                                group_output.append(" %d" % uvs_dict[v + first_uv_index]);
                            group_output.append(";\n")
                        if smooth_groups_tot:
                            group_output.append("\t\t\t\tsmoothGroup %d;\n\t\t\t}\n" % smooth_groups[polygon.index])
                        else:
                            group_output.append("\t\t\t\tsmoothGroup %d;\n\t\t\t}\n" % 0)
                groups_output[group_name] = group_output

            else:

                for mat in materials:
                    current_material_index += 1
                    if material_index != -1 and material_index != current_material_index:
                        continue
                    count = 0
                    for polygon in polygons:
                        if polygon.material_index == current_material_index:
                            count += 1
                    if count == 0:
                        continue

                    if len(materials) > 1:
                        group_name = ob.name + '_' + mat.name
                    else:
                        group_name = ob.name
                    regex=re.compile('^[0-9]')
                    if regex.match(group_name):
                        group_name = 'x' + group_name
                    group_name = stripName(group_name)
                    group_name = group_name[:NAME_LIMIT]

#                    if not group_name:
#                        operator.report({'ERROR'}, "Mesh " + ob.name + ", no group name")
#                        continue

                    print(group_name, 'count', count)
                    if group_name in groups_output:
                        group_output = groups_output[group_name]
                    else:
                        group_output = []
                        groups_count[group_name] = 0

                    for polygon in polygons:
                        if polygon.material_index == current_material_index:
                            groups_count[group_name] += 1
                            group_output.append("\t\t\tface\n\t\t\t{\n")
                            group_output.append("\t\t\t\tcount %d;\n" % len(polygon.vertices))
                            group_output.append("\t\t\t\tverts ");
                            for v in tuple(polygon.vertices)[::-1]:
                                group_output.append(" %d" % vertex_map[v]);
                            group_output.append(";\n")
                            if uvs_data != None:
                                group_output.append("\t\t\t\tuvs ");
                                for v in tuple(polygon.loop_indices)[::-1]:
                                    group_output.append(" %d" % uvs_dict[v + first_uv_index]);
                                group_output.append(";\n")
                            if smooth_groups_tot:
                                group_output.append("\t\t\t\tsmoothGroup %d;\n\t\t\t}\n" % smooth_groups[polygon.index])
                            else:
                                group_output.append("\t\t\t\tsmoothGroup %d;\n\t\t\t}\n" % 0)
                    groups_output[group_name] = group_output

            # Export skeleton
            if export_skeleton:
                for x in range(1):
                    if ob.find_armature():

                        print("Exporting armature: " + ob.find_armature().name)

                        if armature == None:
                            armature = ob.find_armature()
                            bones = armature.data.bones
                            mat = armature.matrix_world

                            joints_output.append("\tjoints %d\n\t{\n" % len(bones))
                            bone_indexes = {}
                            bone_index = 0
                            r = Quaternion([0, 0, 1], -pi/2)
                            for bone in bones:
                                head = mat @ bone.head.xyz
                                q = bone.matrix_local.to_quaternion()
                                q = q @ r
                                bone_indexes[bone.name[:NAME_LIMIT]] = bone_index
                                bone_index += 1

                                bone_name = boneRenameHaydee(bone.name)

                                #print("Bone %s quaternion: %s" % (bone.name, bone.matrix.to_quaternion() @ r))
                                joints_output.append("\t\tjoint %s\n\t\t{\n" % bone_name)
                                if bone.parent:
                                    parent_name = boneRenameHaydee(bone.parent.name)
                                    joints_output.append("\t\t\tparent %s;\n" % parent_name)
                                    q = (bone.parent.matrix_local.to_3x3().inverted() @ bone.matrix_local.to_3x3()).to_quaternion()
                                    q = Quaternion([q.w, -q.y, q.x, q.z])
                                    print("%s head: %s parent head: %s" % (bone.name[:NAME_LIMIT], bone.head, bone.parent.head_local))
                                    head = (mat @ bone.parent.matrix_local.inverted()).to_quaternion() @ (bone.head_local - bone.parent.head_local)
                                    head = Vector((-head.y, head.x, head.z))

                                head = Vector((-head.x, -head.y, head.z))
                                head = Vector((head.x, head.z, head.y))
                                q = Quaternion([-q.w, q.x, -q.z, q.y])
                                q = Quaternion([q.x, q.y, q.z, q.w])
                                joints_output.append("\t\t\torigin %s %s %s;\n" % (d(head.x), d(head.y), d(head.z)))
                                joints_output.append("\t\t\taxis %s %s %s %s;\n" % (d(q.w), d(q.x), d(q.y), d(q.z)))
                                joints_output.append("\t\t}\n")
                            joints_output.append("\t}\n")

                        elif armature.name != ob.find_armature().name:
                            operator.report({'ERROR'}, "Multiple armatures present, please select only one")
                            continue

                        vertex_weights = {}
                        vertex_groups = ob.vertex_groups
                        invalid_weighting = False
                        for v in mesh.vertices:
                            for g in v.groups:
                                group = vertex_groups[g.group]
                                if not (group.name[:NAME_LIMIT] in bone_indexes):
                                    continue
                                bone = bone_indexes[group.name[:NAME_LIMIT]]
                                if v.index in vertex_map:
                                    if g.weight > 0:
                                        i = vertex_map[v.index]
                                        if not (i in vertex_weights):
                                            vertex_weights[i] = []
                                        vertex_weights[i].append((vertex_map[v.index], bone, g.weight))
                        for i in sorted(vertex_weights.keys()):
                            weight_list = vertex_weights[i]
                            #sort bone names first?
                            #weight_list = sorted(weight_list, key=lambda bw: bw[1], reverse=True)
                            weight_list = sorted(weight_list, key=lambda bw: bw[2], reverse=True)
                            #if len(weight_list) > 4:
                            #    weight_list = weight_list[0:3]
                            sum = 0
                            for w in weight_list:
                                sum += w[2]
                            for w in weight_list:
                                normalized_weight = w[2] / sum
                                weights_output.append("\t\tweight %d %d %s;\n" % (w[0], w[1], d(normalized_weight)))
                                weights_count += 1

        if separate_files:
            to_file(separate_files, filepath, group_name, base_vertex_index, vertex_output,
                    unique_uvs_pos, uvs_output, groups_output, groups_count,
                    joints_output, weights_count, weights_output)

    if not separate_files:
        if base_vertex_index == 0 or not group_name:
            operator.report({'ERROR'}, "Nothing to export")
            return {'FINISHED'}

        to_file(separate_files, filepath, group_name, base_vertex_index, vertex_output,
                unique_uvs_pos, uvs_output, groups_output, groups_count,
                joints_output, weights_count, weights_output)

    return {'FINISHED'}


def reset_variables():
    vertex_output = []
    uvs_output = []
    groups_output = {}
    groups_count = {}
    joints_output = []
    weights_output = []
    weights_count = 0
    group_count = 0
    base_vertex_index = 0
    base_uv_index = 0
    armature = None
    unique_uvs_pos = []
    uvs_dict = []

    return (vertex_output, uvs_output, groups_output, groups_count,
        joints_output, weights_output, weights_count, group_count,
        base_vertex_index, base_uv_index, armature, unique_uvs_pos, uvs_dict)


def to_file(separate_files, filepath, group_name, base_vertex_index,
        vertex_output, unique_uvs_pos, uvs_output, groups_output,
        groups_count, joints_output, weights_count, weights_output):

    if separate_files:
        folder_path, basename = (os.path.split(filepath))
        name, ext = (os.path.splitext(filepath))
        filepath = os.path.join(folder_path, "{}{}".format(group_name, ext))

    # Write file contents
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("HD_DATA_TXT 300\n\n")
        f.write("mesh\n{\n")
        f.write("\tverts %d\n\t{\n" % base_vertex_index)
        f.write("".join(vertex_output))
        f.write("\t}\n")
        f.write("\tuvs %d\n\t{\n" % len(unique_uvs_pos))
        f.write("".join(uvs_output))
        f.write("\t}\n")
        f.write("\tgroups %d\n\t{\n" % len(groups_output))
        for name, contents in groups_output.items():
            f.write("\t\tgroup %s %d\n\t\t{\n" % (name, groups_count[name]))
            f.write("".join(contents))
            f.write("\t\t}\n")
        f.write("\t}\n")
        f.write("".join(joints_output))
        if weights_count > 0:
            f.write("\tweights %d\n\t{\n" % weights_count)
            f.write("".join(weights_output))
            f.write("\t}\n")
        f.write("}\n")


class ExportHaydeeDMesh(Operator, ExportHelper):
    bl_idname = "haydee_exporter.dmesh"
    bl_label = "Export Haydee dmesh"
    bl_options = {'REGISTER'}
    filename_ext = ".dmesh"
    filter_glob : StringProperty(
            default="*.dmesh",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    selected_only : BoolProperty(
            name="Selected only",
            description="Export only selected objects (if nothing is selected, full scene will be exported regardless of this setting)",
            default=True,
            )
    separate_files : BoolProperty(
            name="Export to Separate Files",
            description="Export each object to a separate file",
            default=False,
            )
    ignore_hidden : BoolProperty(
            name="Ignore hidden",
            description="Ignore hidden objects",
            default=True,
            )
    apply_modifiers : BoolProperty(
            name="Apply modifiers",
            description="Apply modifiers before exporting",
            default=True,
            )
    export_skeleton : BoolProperty(
            name="Export skeleton",
            description="Export skeleton and vertex weights",
            default=True,
            )
    material : EnumProperty(
            name="Material",
            description="Material to export",
            items = materials_list
            )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        return write_dmesh(self, context, self.filepath, self.export_skeleton,
                self.apply_modifiers, self.selected_only, self.separate_files,
                self.ignore_hidden, self.material)


# --------------------------------------------------------------------------------
#  Initialization & menu
# --------------------------------------------------------------------------------
class HaydeeExportSubMenu(bpy.types.Menu):
    bl_idname = "OBJECT_MT_haydee_export_submenu"
    bl_label = "Haydee"

    def draw(self, context):
        layout = self.layout
        layout.operator(ExportHaydeeDMesh.bl_idname, text="Haydee DMesh (.dmesh)")
        layout.operator(ExportHaydeeDSkel.bl_idname, text="Haydee DSkel (.dskel)")
        layout.operator(ExportHaydeeDPose.bl_idname, text="Haydee DPose (.dpose)")
        layout.operator(ExportHaydeeDMotion.bl_idname, text="Haydee DMotion (.dmot)")


def menu_func_export(self, context):
    my_icon = HaydeeMenuIcon.custom_icons["main"]["haydee_icon"]
    self.layout.menu(HaydeeExportSubMenu.bl_idname, icon_value=my_icon.icon_id)


# --------------------------------------------------------------------------------
#  Register
# --------------------------------------------------------------------------------
def register():
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
    # bpy.ops.haydee_exporter.motion('INVOKE_DEFAULT')

