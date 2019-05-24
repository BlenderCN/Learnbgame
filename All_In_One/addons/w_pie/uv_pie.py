
import bpy
import mathutils
from mathutils import Vector, Matrix
import bpy, os
from bpy.types import Menu, Header
from bpy.props import IntProperty, FloatProperty, BoolProperty
import bmesh
from mathutils import *
import math


#
# bl_info = {
#     "name": "Jimmy_pie_uv",
#     "description": "Jimmy's UV select mode pie menu",
#     "category": "Learnbgame",
# }


# Operators




#################################################

#################################################
# uv_prj_from_normal
# bl_info = {
#     'name': 'Project From Normal',
#     'author': 'chaosdesk',
#     'version': (0,1),
#     'blender': (2, 6, 9),
#     "location": "View3D > UV Mapping > Project From Normal",
#     'description': 'Project from average normal of all Face',
#     'warning': '',
#     'wiki_url': '',
#     'tracker_url': 'http://chaosdesk.blog123.fc2.com/',
#     "category": "Learnbgame",
}

MAX_LOCATION = 1


class ProjectFromNormal(object):
    def __init__(self):
        bpy.ops.object.mode_set(mode='OBJECT')

        self.current_obj = bpy.context.selected_objects[0]
        self.mesh        = self.current_obj.data
        self.select_poly = []

        # check if more than one face is selected
        self.NoneSelect = True
        for poly in self.mesh.polygons:
            if poly.select == True:
                self.NoneSelect = False
                self.select_poly.append(poly)

        if self.NoneSelect == True:
            return

        if self.mesh.uv_layers.active == None:
            self.mesh.uv_textures.new()

        # translate position that selected polygon's uv
        self.transUvVector()

        bpy.ops.object.mode_set(mode='EDIT')


    def transUvVector(self):
        max_position   = 0.
        min_position_x = 0.
        min_position_y = 0.

        # calculate two rotation matrix from normal vector of selected polygons
        vector_nor = self.averageNormal()

        theta_x  = self.calcRotAngle('X', vector_nor.x, vector_nor.y, vector_nor.z)
        mat_rotx = Matrix.Rotation(theta_x, 3, 'X')
        vector_nor.rotate(mat_rotx)

        theta_y  = self.calcRotAngle('Y', vector_nor.x, vector_nor.y, vector_nor.z)
        mat_roty = Matrix.Rotation(theta_y, 3, 'Y')

        # apply two rotation matrix to vertex
        uv_array = self.mesh.uv_layers.active.data
        for poly in self.select_poly:
            for id in range(poly.loop_start, poly.loop_start + poly.loop_total):
                new_vector = Vector((self.mesh.vertices[self.mesh.loops[id].vertex_index].co[0],
                                     self.mesh.vertices[self.mesh.loops[id].vertex_index].co[1],
                                     self.mesh.vertices[self.mesh.loops[id].vertex_index].co[2]))

                new_vector.rotate(mat_rotx)
                new_vector.rotate(mat_roty)

                uv_array[id].uv = new_vector.to_2d()

                if min_position_x > uv_array[id].uv.x:
                    min_position_x = uv_array[id].uv.x
                if min_position_y > uv_array[id].uv.y:
                    min_position_y = uv_array[id].uv.y

        # recalculate uv position
        for poly in self.select_poly:
            for id in range(poly.loop_start, poly.loop_start + poly.loop_total):
                uv_array[id].uv.x = uv_array[id].uv.x + abs(min_position_x)
                uv_array[id].uv.y = uv_array[id].uv.y + abs(min_position_y)

                if max_position < uv_array[id].uv.x:
                    max_position = uv_array[id].uv.x
                if max_position < uv_array[id].uv.y:
                    max_position = uv_array[id].uv.y

        # scale uv position
        for poly in self.select_poly:
            for id in range(poly.loop_start, poly.loop_start + poly.loop_total):
                uv_array[id].uv.x = uv_array[id].uv.x * MAX_LOCATION / max_position
                uv_array[id].uv.y = uv_array[id].uv.y * MAX_LOCATION / max_position


    def averageNormal(self):
        weight_norx   = 0.
        weight_nory   = 0.
        weight_norz   = 0.
        aver_normal = None

        for poly in self.select_poly:
            weight_norx = weight_norx + (poly.normal.x * poly.area)
            weight_nory = weight_nory + (poly.normal.y * poly.area)
            weight_norz = weight_norz + (poly.normal.z * poly.area)

        aver_normal = Vector((weight_norx, weight_nory, weight_norz))
        aver_normal.normalize()

        return aver_normal


    def calcRotAngle(self, axis, nor_x, nor_y, nor_z):
        theta        = 0
        vector_z     = Vector((0.0, 0.0, 1.0))
        vector_n     = None
        vector_cross = None

        if axis == 'X':
            vector_n     = Vector((0.0, nor_y, nor_z))
            theta        = vector_z.angle(vector_n, 999)
            vector_cross = vector_n.cross(vector_z)
            if vector_cross.x < 0:
                theta = -(theta)
        elif axis == 'Y':
            vector_n     = Vector((nor_x, 0.0, nor_z))
            theta        = vector_z.angle(vector_n, 999)
            vector_cross = vector_n.cross(vector_z)
            if vector_cross.y < 0:
                theta = -(theta)
        else:
            pass

        return theta


class NewUvProjectMenu(bpy.types.Operator):
    """Project From Normal"""
    bl_idname  = "mesh.uv_project_from_normal_vector"
    bl_label   = "Project From Normal Vector"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ProjectFromNormal()
        return {'FINISHED'}


#################################################

#################################################

























class Placeholder(bpy.types.Operator):
    """Placeholder to get pie menu items in arbitrary positions"""
    bl_idname = "ui.placeholder"
    bl_label = ""

    @classmethod
    def poll(cls, context):
        return False

    def execute(self, context):
        return {'FINISHED'}


class SplitAndGrab(bpy.types.Operator):
    """Same as pressing Y, then G in UV editor"""
    bl_idname = "uv.split_and_grab"
    bl_label = "Rip Face"

    def execute(self, context):

        bpy.ops.uv.select_split()
        bpy.ops.transform.translate()

        return {'FINISHED'}


# Menu



class live_unwrap_toggle(bpy.types.Operator):
    bl_idname = "uv.live_unwrap_toggle"
    bl_label = "Live Unwrap"

    def execute(self, context):
        if bpy.context.scene.tool_settings.edge_path_live_unwrap == (False):
           bpy.context.scene.tool_settings.edge_path_live_unwrap = True
        else:
           bpy.context.scene.tool_settings.edge_path_live_unwrap = False
        return {'FINISHED'}



# bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.02)
# bpy.ops.uv.project_from_view(camera_bounds=False, correct_aspect=True, scale_to_bounds=False)

# uv pie menu
class uv_pie(Menu):
    bl_idname = "pie.uv_pie"
    bl_label = "UV"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        #4 - LEFT
        pie.operator("uv.unwrap", icon='LOOPSEL').margin=0.00
        #6 - RIGHT
        pie.operator("uv.smart_project", icon='UV_ISLANDSEL')
        #2 - BOTTOM
        pie.operator("uv.seams_from_islands", icon='MOD_MESHDEFORM')
        # tool_settings = context.tool_settings
        # pie.prop(tool_settings, "edge_path_live_unwrap")
        #8 - TOP
        pie.operator("uv.project_from_view", icon='RENDER_REGION')
        #7 - TOP - LEFT
        pie.operator("uv.pack_islands", icon='MOD_TRIANGULATE').rotate=False
        #9 - TOP - RIGHT
        pie.operator("uv.live_unwrap_toggle", icon='COLOR_RED')
        #1 - BOTTOM - LEFT
        pie.operator("mesh.uv_project_from_normal_vector", icon='VERTEXSEL')
        #3 - BOTTOM - RIGHT
        # pie.operator("uv.paste_uv_map", icon='PASTEDOWN')




class UvSelectMode(bpy.types.Menu):
    bl_label = "UV Select Mode"
    bl_idname = "pie.uv_select_mode"

    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_REGION_WIN'
        toolsettings = context.tool_settings
        pie = layout.menu_pie()

        _ = 0 if toolsettings.use_uv_select_sync else 1

        # Left
        op = pie.operator("wm.context_set_value", text="Vertex",
                          icon=('VERTEXSEL', 'UV_VERTEXSEL')[_])
        op.value = ("(True, False, False)", "'VERTEX'")[_]
        op.data_path = "tool_settings.%s_select_mode" % ('mesh', 'uv')[_]

        # Right
        op = pie.operator("wm.context_set_string",
        text="Island", icon='UV_ISLANDSEL')
        if _:
            op.value = 'ISLAND'
            op.data_path = "tool_settings.uv_select_mode"

        # Bottom
        op = pie.operator("wm.context_set_value", text="Face",
                          icon=('FACESEL', 'UV_FACESEL')[_])
        op.value = ("(False, False, True)", "'FACE'")[_]
        op.data_path = "tool_settings.%s_select_mode" % ('mesh', 'uv')[_]

        # Top
        op = pie.operator("wm.context_set_value", text="Edge",
        icon=('EDGESEL', 'UV_EDGESEL')[_])
        op.value = ("(False, True, False)", "'EDGE'")[_]
        op.data_path = "tool_settings.%s_select_mode" % ('mesh', 'uv')[_]

        # Top-left linked
        op = pie.operator("uv.select_linked", text="Select Linked",
                          icon="OUTLINER_OB_LATTICE")

        # Top-right
        op = pie.operator("wm.context_set_value", text="Sync Selection",
                          icon="UV_SYNC_SELECT")
        op.value = ("False", "True")[_]
        op.data_path = "tool_settings.use_uv_select_sync"

        # Bottom-left
        op = pie.operator("uv.stitch", icon="SNAP_ON")

        # Bottom-right
        op = pie.operator("uv.split_and_grab", text="Rip Face",
                          icon="MOD_MESHDEFORM")


# addon_keymaps = []
#
#
# def register():
#     bpy.utils.register_module(__name__)
#
#     # Keymap Config
#     wm = bpy.context.window_manager
#
#     if wm.keyconfigs.addon:
#         km = wm.keyconfigs.addon.keymaps.new(name='Image',
#                                              space_type='IMAGE_EDITOR')
#         kmi = km.keymap_items.new('wm.call_menu_pie', 'RIGHTMOUSE', 'PRESS')
#         kmi.properties.name = "pie.uv_select_mode"
#
#         addon_keymaps.append(km)
#
#
# def unregister():
#     bpy.utils.unregister_module(__name__)
#
#     wm = bpy.context.window_manager
#
#     if wm.keyconfigs.addon:
#         for km in addon_keymaps:
#             for kmi in km.keymap_items:
#                 km.keymap_items.remove(kmi)
#
#             wm.keyconfigs.addon.keymaps.remove(km)
#
#     del addon_keymaps[:]
#
# if __name__ == "__main__":
#     register()
