import bpy, os
from bpy.types import Menu, Header
from bpy.props import IntProperty, FloatProperty, BoolProperty
import bmesh
from mathutils import *
import math




# misc pie menuz
class misc_pie(Menu):
    bl_idname = "pie.misc_pie"
    bl_label = "Pie Misc"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        #4 - LEFT
        pie.operator("object.modifier_add", text="Bevel" , icon='MOD_BEVEL').type='BEVEL'
        #6 - RIGHT
        pie.operator("object.make_links_data", icon='MATERIAL').type='MATERIAL'
        #2 - BOTTOM
        pie.operator("object.modifier_add", text="Array" , icon='MOD_ARRAY').type='ARRAY'
        # #8 - TOP
        pie.operator("object.freeze_transformation", icon='MANIPUL')
        # #7 - TOP - LEFT
        pie.operator("object.modifier_add", text="Solidify" , icon='MOD_SOLIDIFY').type='SOLIDIFY'
        # #9 - TOP - RIGHT
        pie.operator("btool.auto_union", icon='ROTATECOLLECTION' , text="Union").solver='BMESH'
        # #1 - BOTTOM - LEFT
        pie.operator("object.join", icon='GROUP')
        # #3 - BOTTOM - RIGHT
        pie.operator("btool.auto_difference", icon='ROTACTIVE' , text="Difference").solver='BMESH'






# misc edit pie menu
class misc_edit_pie(Menu):
    bl_idname = "pie.misc_edit_pie"
    bl_label = "Pie Misc Edit"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        #4 - LEFT
        pie.operator("mesh.looptools_bridge", icon='NODE_INSERT_OFF')
        #6 - RIGHT
        pie.operator("mesh.bevel", icon='MOD_BEVEL')
        #2 - BOTTOM
        pie.operator("mesh.extrude_region_shrink_fatten", icon='FACESEL')
        # #8 - TOP
        pie.operator("mesh.looptools_relax", icon='MOD_LATTICE')
        # #7 - TOP - LEFT
        pie.operator("mesh.looptools_circle", icon='MESH_CIRCLE')
        # #9 - TOP - RIGHT
        pie.operator("mesh.remove_doubles", icon='AUTOMERGE_ON').threshold=0.01
        # #1 - BOTTOM - LEFT
        pie.operator("mesh.separate", icon='MOD_UVPROJECT').type='SELECTED'
        # #3 - BOTTOM - RIGHT
        pie.operator("mesh.subdivide", icon='OUTLINER_OB_LATTICE')

        # Menu srt
        ###################################################

        ###################################################
        group = pie.column()
        box = group.box()
        row = box.row()
        box.menu("VIEW3D_MT_edit_mesh_vertices", icon="LOOPSEL")
        box.scale_x = 3

        group.separator()

        box = group.box()
        box.operator("mesh.rip_move", icon="MOD_NORMALEDIT")
        ###################################################

        ###################################################
        box = pie.split().column()
        ###################################################

        ###################################################
        group = pie.column()
        box = group.box()
        row = box.row()

        group.separator()

        ###################################################
        box = group.box()
        box.menu("VIEW3D_MT_edit_mesh_faces", icon="FACESEL")
        box = group.box()
        row = box.row()
        row.operator("mesh.extrude_faces_move", icon="UV_ISLANDSEL")
        row.operator("mesh.flip_normals", icon="UV_ISLANDSEL")
        box.scale_x = 1

        ###################################################
        group = pie.column()
        box = group.box()
        row = box.row()
        box.menu("VIEW3D_MT_edit_mesh_edges", icon="EDGESEL")
        box.scale_x = 3

        group.separator()

        box = group.box()
        ###################################################
        # Menu end




class freeze_transformation(bpy.types.Operator):
    bl_idname = 'object.freeze_transformation'
    bl_label = 'Apply'
    bl_description = 'Freeze Transformation'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        return {'FINISHED'}
