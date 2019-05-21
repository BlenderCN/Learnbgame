# -*- coding: utf-8 -*-

import bpy
import bmesh
from bpy.props import EnumProperty


def setupScene():
    bpy.ops.object.mode_set(mode='OBJECT')
    for slots in bpy.context.active_object.material_slots:
        bpy.ops.object.material_slot_remove()  # remove all materials slots
    bpy.ops.object.mode_set(mode='EDIT')


def createMat():
    m_check = bpy.context.window_manager.m_check
    if bpy.context.space_data.shading.light == 'MATCAP':
        m_check.meshcheck_matcap = True
        bpy.context.space_data.shading.light = 'STUDIO'
        bpy.context.space_data.shading.color_type = 'MATERIAL'

    # create new material
    mat_A = bpy.data.materials.new("Quads")
    mat_A.diffuse_color = (0.865, 0.865, 0.865)

    mat_B = bpy.data.materials.new("Ngons")
    mat_B.diffuse_color = (1, 0, 0)

    mat_C = bpy.data.materials.new("Tris")
    mat_C.diffuse_color = (1, 1, 0)

    ob = bpy.context.active_object
    me = ob.data
    mat_list = [mat_A, mat_B, mat_C]
    for mat in mat_list:
        me.materials.append(mat)  # assign materials


def restoreMat():
    setupScene()
    mat_A = bpy.data.materials['Quads']

    mat_B = bpy.data.materials['Ngons']

    mat_C = bpy.data.materials['Tris']

    ob = bpy.context.active_object
    me = ob.data
    mat_list = [mat_A, mat_B, mat_C]
    for mat in mat_list:
        me.materials.append(mat)


class HOPS_OT_AddMaterials(bpy.types.Operator):
    """
    Display NGONS / TRIS using materials.
    Select a 2nd time to disable.

    """
    bl_idname = "object.add_materials"
    bl_label = "Add materials"

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def execute(sefl, context):
        m_check = context.window_manager.m_check
        m_check.meshcheck_shade = bpy.context.space_data.shading.type
        bpy.context.space_data.shading.type = 'SOLID'

        m_check.meshcheck_color = bpy.context.space_data.shading.color_type
        bpy.context.space_data.shading.color_type = 'MATERIAL'

        m_check.meshcheck_light = bpy.context.space_data.shading.light
        bpy.context.space_data.shading.light = 'STUDIO'

        if not bpy.data.materials:
            if context.object.mode == 'OBJECT':
                bpy.ops.object.mode_set(mode='EDIT')
                createMat()
            elif context.object.mode == 'EDIT':
                createMat()

        else:
            if bpy.context.object.active_material:
                for mat_slots in bpy.context.active_object.material_slots:
                    m_check.meshcheck_save_mat.append(mat_slots.name)

            ref_list = ['Quads', 'Ngons', 'Tris']
            mat_list = []
            for mat in bpy.data.materials:
                mat_list.append(mat.name)
            for ref in ref_list:
                if ref in mat_list:
                    restoreMat()

                else:
                    setupScene()
                    createMat()
        m_check.meshcheck_enabled = True
        meshCheckDisplayColor()
        updateDisplayColor(context.scene)
        return {'FINISHED'}


class HOPS_OT_RemoveMaterials(bpy.types.Operator):
    bl_idname = "object.remove_materials"
    bl_label = "Remove materials"

    @classmethod
    def poll(cls, context):
        return context.active_object.type == 'MESH'

    def execute(self, context):
        m_check = context.window_manager.m_check

        bpy.context.space_data.shading.color_type = m_check.meshcheck_color
        bpy.context.space_data.shading.light = m_check.meshcheck_light
        bpy.context.space_data.shading.type = m_check.meshcheck_shade
        m_check.meshcheck_enabled = False

        if bpy.context.object.mode == 'OBJECT':
            for slots in bpy.context.active_object.material_slots:
                bpy.ops.object.material_slot_remove()
            if len(m_check.meshcheck_save_mat) > 0:
                ob = bpy.context.active_object
                me = ob.data

                for mat in m_check.meshcheck_save_mat:
                    mat_list = bpy.data.materials[mat]
                    me.materials.append(mat_list)

                del(m_check.meshcheck_save_mat[:])  # clean the list

        elif bpy.context.object.mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')
            for slots in bpy.context.active_object.material_slots:
                bpy.ops.object.material_slot_remove()
            if len(m_check.meshcheck_save_mat) > 0:
                ob = bpy.context.active_object
                me = ob.data

                for mat in m_check.meshcheck_save_mat:
                    mat_list = bpy.data.materials[mat]
                    me.materials.append(mat_list)

                del(m_check.meshcheck_save_mat[:])  # clean the list
            bpy.ops.object.mode_set(mode='EDIT')

        updateDisplayColor(context.scene)
        return {'FINISHED'}


def updateDisplayColor(scene):
    obj = bpy.context.active_object
    obj.data.validate()
    if obj and obj.type == 'MESH' and obj.mode == 'EDIT':
        meshCheckDisplayColor()


def meshCheckDisplayColor():
    m_check = bpy.context.window_manager.m_check

    m_check.ngons_count = 0
    m_check.tris_count = 0
    ob = bpy.context.object
    me = ob.data
    bm = bmesh.from_edit_mesh(me)

    tris = ngons = 0

    for f in bm.faces:
        v = len(f.verts)
        if v == 3:  # tris
            f.material_index = 2
            tris += 1
        elif v == 4:  # quads
            f.material_index = 0
        elif v > 4:  # ngons
            f.material_index = 1
            ngons += 1
    m_check.tris_count = tris
    m_check.ngons_count = ngons

    bmesh.update_edit_mesh(me)


class HopsMeshCheckCollectionGroup(bpy.types.PropertyGroup):
    meshcheck_use: bpy.props.BoolProperty(
        name="Mesh check",
        description="Display mesh check tools",
        default=False)
    meshcheck_enabled: bpy.props.BoolProperty(
        name="Mesh check enabled",
        description="Display faces color",
        default=False)
    meshcheck_shade: bpy.props.StringProperty(default='SOLID')
    meshcheck_light: bpy.props.StringProperty(default='STUDIO')
    meshcheck_color: bpy.props.StringProperty(default='MATERIAL')
    meshcheck_save_mat = []
    tris_count: bpy.props.IntProperty(
        name="Tris :")
    ngons_count: bpy.props.IntProperty(
        name="Ngons :")


class HOPS_OT_DataOpFaceTypeSelect(bpy.types.Operator):
    """Select all faces of a certain type"""
    bl_idname = "data.facetype_select"
    bl_label = "Select by face type"
    bl_options = {'REGISTER', 'UNDO'}

    select_mode: bpy.props.StringProperty()
    face_type: EnumProperty(name="Select faces:",
                            items=(("3", "Triangles", "Faces made up of 3 vertices"),
                                   ("5", "Ngons", "Faces made up of 5 and more vertices")),
                            default="5")

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        if tuple(bpy.context.tool_settings.mesh_select_mode) == (True, False, False):
            self.select_mode = "VERT"
        elif tuple(bpy.context.tool_settings.mesh_select_mode) == (False, True, False):
            self.select_mode = "EDGE"
        elif tuple(bpy.context.tool_settings.mesh_select_mode) == (False, False, True):
            self.select_mode = "FACE"
        context.tool_settings.mesh_select_mode = (False, False, True)
        if self.face_type == "3":
            bpy.ops.mesh.select_face_by_sides(number=3, type='EQUAL')
            bpy.ops.mesh.select_mode(type=self.select_mode)
        else:
            bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER')
            bpy.ops.mesh.select_mode(type=self.select_mode)
        return {'FINISHED'}
