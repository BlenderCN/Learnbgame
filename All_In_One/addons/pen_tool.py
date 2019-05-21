# -*- coding: utf-8 -*-

# ***** BEGIN GPL LICENSE BLOCK *****
#
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

# ------ ------
bl_info = {
    'name': 'pen_tool',
    'author': '',
    'version': (0, 1, 5),
    'blender': (2, 6, 3),
    'api': 47770,
    'location': 'View3D > Tool Shelf',
    'description': '',
    'warning': 'Beta',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Mesh' }

# ------ ------
import bpy, blf, bgl
import bmesh
from bpy_extras.view3d_utils import region_2d_to_location_3d
from mathutils import Vector
from math import degrees

# ------ ------
def edit_mode_out():
    bpy.ops.object.mode_set(mode = 'OBJECT')

def edit_mode_in():
    bpy.ops.object.mode_set(mode = 'EDIT')

# ------ ------
def draw_callback_px(self, context):

    font_id = 0
    blf.position(font_id, 150, 10, 0)
    blf.size(font_id, 20, 72)
    blf.draw(font_id, 'Draw')

    n1 = len(pt_buf.list_)
    if n1 != 0:

        bgl.glEnable(bgl.GL_BLEND)
        
        bgl.glColor4f(0.0, 1.0, 0.0, 1.0)

        bgl.glPointSize(4.0)
        bgl.glBegin(bgl.GL_POINTS)
        for j in pt_buf.list_:
            bgl.glVertex2f(j[0], j[1])
        bgl.glEnd()

        bgl.glLineStipple(4, 0x5555)
        bgl.glEnable(bgl.GL_LINE_STIPPLE)
        
        # -- -- -- --
        #bgl.glLineWidth(1)
        bgl.glBegin(bgl.GL_LINES)
        bgl.glVertex2f(pt_buf.list_[-1][0], pt_buf.list_[-1][1])
        bgl.glVertex2f(pt_buf.x, pt_buf.y)
        bgl.glEnd()

        pos = (pt_buf.list_[-1] + Vector((pt_buf.x, pt_buf.y))) * 0.5
        vec1_3d = region_2d_to_location_3d(context.region, context.space_data.region_3d, Vector((pt_buf.list_[-1][0], pt_buf.list_[-1][1])), Vector((0.0, 0.0, 0.0)))
        vec2_3d = region_2d_to_location_3d(context.region, context.space_data.region_3d, Vector((pt_buf.x, pt_buf.y)), Vector((0.0, 0.0, 0.0)))

        blf.position(font_id, pos[0] + 10, pos[1] + 10, 0)
        blf.size(font_id, 14, 72)
        blf.draw(font_id, str(round((vec1_3d -vec2_3d).length, 4)))

        if n1 >= 2:
            vec0_3d = region_2d_to_location_3d(context.region, context.space_data.region_3d, Vector((pt_buf.list_[-2][0], pt_buf.list_[-2][1])), Vector((0.0, 0.0, 0.0)))
            vec = vec2_3d - vec1_3d
            if vec.length == 0.0:
                pass
            else:
                ang = (vec).angle(vec0_3d - vec1_3d)
                if round(degrees(ang)) == 0.0:
                    pass
                else:
                    bgl.glColor4f(0.027, 0.663, 1.0, 1.0)
                    blf.position(font_id, pt_buf.list_[-1][0] + 10, pt_buf.list_[-1][1] + 10, 0)
                    blf.size(font_id, 14, 72)
                    blf.draw(font_id, str(round(degrees(ang), 2)) + ' Degrees')
                    bgl.glColor4f(0.0, 1.0, 0.0, 1.0)
        
        # -- -- -- --
        bgl.glBegin(bgl.GL_LINE_STRIP)
        for i in range(n1):
            bgl.glVertex2f(pt_buf.list_[i][0], pt_buf.list_[i][1])
        bgl.glEnd()
        bgl.glDisable(bgl.GL_LINE_STIPPLE)

        #bgl.glLineWidth(1)
        bgl.glPointSize(1.0)
        bgl.glColor4f(1.0, 1.0, 1.0, 1.0)
        
        bgl.glDisable(bgl.GL_BLEND)

class pt_buf():
    list_ = []
    list_tmp = []
    x = 0
    y = 0

# ------ panel 0 ------
class pt_p0(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    #bl_idname = 'pt_p0_id'
    bl_label = 'Draw'
    bl_context = 'mesh_edit'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.operator('pt.op0_id', text = 'Draw')

# ------ operator 0 ------
class pt_op0(bpy.types.Operator):
    bl_idname = 'pt.op0_id'
    bl_label = 'Draw'
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        
    def execute(self, context):
        edit_mode_out()
        ob_act = context.active_object
        bme = bmesh.new()
        bme.from_mesh(ob_act.data)

        list_tmp = [region_2d_to_location_3d(context.region, context.space_data.region_3d, k, Vector((0.0, 0.0, 0.0))) for k in pt_buf.list_]

        list_1 = []
        for i in list_tmp:
            bme.verts.new(i)
            bme.verts.index_update()
            list_1.append(bme.verts[-1])

        n = len(list_1)
        for j in range(n - 1):
            bme.edges.new((list_1[j], list_1[(j + 1) % n])              )

        list_tmp[:] = []
        pt_buf.list_[:] = []
        
        bme.to_mesh(ob_act.data)
        edit_mode_in()
        return {'FINISHED'}

    def modal(self, context, event):
        context.area.tag_redraw()
        if event.type == 'MOUSEMOVE':
            pt_buf.x = event.mouse_region_x
            pt_buf.y = event.mouse_region_y
        elif event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                mouse_loc = Vector((event.mouse_region_x, event.mouse_region_y))
                pt_buf.list_.append(mouse_loc)
            elif event.value == 'RELEASE':
                pass
        elif event.type == 'RIGHTMOUSE':
            context.region.callback_remove(self._handle)
            self.execute(context)
            return {'FINISHED'}
        elif event.type == 'ESC':
            context.region.callback_remove(self._handle)
            pt_buf.list_[:] = []
            return {'CANCELLED'}
        return {"PASS_THROUGH"}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            context.window_manager.modal_handler_add(self)
            self._handle = context.region.callback_add(draw_callback_px, (self, context), 'POST_PIXEL')
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

# ------ ------
class_list = [ pt_p0, pt_op0 ]
               
# ------ register ------
def register():
    for c in class_list:
        bpy.utils.register_class(c)
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('pt.op0_id', 'D', 'PRESS')

# ------ unregister ------
def unregister():
    for c in class_list:
        bpy.utils.unregister_class(c)
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps['3D View']
    for kmi in km.keymap_items:
        if kmi.idname == 'pt.op0_id':
            km.keymap_items.remove(kmi)
            break

# ------ ------
if __name__ == "__main__":
    register()