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
    'name': 'Index Visualiser (BMesh)',
    'author': 'Bartius Crouch, CoDEmanX, zeffii',
    'version': (3, 0, 0),
    'blender': (2, 7, 0),
    'location': 'View3D > Properties panel > Mesh Display tab (edit-mode)',
    'warning': '',
    'description': 'Display indices of verts, edges and faces in the 3d-view',
    'wiki_url': '',
    'tracker_url': '',
    'category': '3D View'}

"""
Display the indices of vertices, edges and faces in the 3d-view.

How to use:
- Select a mesh and go into editmode
- Display the properties panel (N-key)
- Go to the Mesh Display tab, it helps to fold the tabs above it
- Press the 'Visualise indices button'

"""

import bpy
import bgl
import blf
import mathutils
import bmesh
import math
from bpy_extras.view3d_utils import location_3d_to_region_2d as loc3d2d

point_dict = {}


def adjust_list(in_list, x, y):
    return [[old_x + x, old_y + y] for (old_x, old_y) in in_list]


def generate_points(width, height):
    amp = 5  # radius fillet

    width += 2
    height += 4
    width = ((width / 2) - amp) + 2
    height -= (2 * amp)

    pos_list, final_list = [], []

    n_points = 12
    seg_angle = 2 * math.pi / n_points
    for i in range(n_points + 1):
        angle = i * seg_angle
        x = math.cos(angle) * amp
        y = math.sin(angle) * amp
        pos_list.append([x, -y])

    w_list, h_list = [1, -1, -1, 1], [-1, -1, 1, 1]
    slice_list = [[i, i + 4] for i in range(0, n_points, 3)]

    for idx, (start, end) in enumerate(slice_list):
        point_array = pos_list[start:end]
        w = width * w_list[idx]
        h = height * h_list[idx]
        final_list += adjust_list(point_array, w, h)

    return final_list


def get_points(index):
    '''
    index:   string representation of the index number
    returns: rounded rect point_list used for background.

    the neat thing about this is if a width has been calculated once, it
    is stored in a dict and used if another polygon is saught with that width.
    '''
    width, height = blf.dimensions(0, index)
    if not (width in point_dict):
        point_dict[width] = generate_points(width, height)

    return point_dict[width]


# calculate locations and store them as ID property in the mesh
def draw_callback_px(self, context):
    # polling
    if context.mode != "EDIT_MESH":
        return

    # get screen information
    region = context.region
    rv3d = context.space_data.region_3d
    this_object = context.active_object
    matrix_world = this_object.matrix_world

    text_height = 13
    blf.size(0, text_height, 72)

    def draw_index(rgb, index, coord):

        vector3d = matrix_world * coord
        x, y = loc3d2d(region, rv3d, vector3d)

        index = str(index)
        polyline = get_points(index)

        ''' draw polygon '''
        bgl.glColor4f(0.103, 0.2, 0.2, 0.2)
        bgl.glBegin(bgl.GL_POLYGON)
        for pointx, pointy in polyline:
            bgl.glVertex2f(pointx + x, pointy + y)
        bgl.glEnd()

        ''' draw text '''
        txt_width, txt_height = blf.dimensions(0, index)
        bgl.glColor3f(*rgb)
        blf.position(0, x - (txt_width / 2), y - (txt_height / 2), 0)
        blf.draw(0, index)

    vert_idx_color = (1.0, 1.0, 1.0)
    edge_idx_color = (1.0, 1.0, 0.0)
    face_idx_color = (1.0, 0.8, 0.8)

    scene = context.scene
    me = context.active_object.data
    bm = bmesh.from_edit_mesh(me)

    if scene.live_mode:
        me.update()

    if scene.display_vert_index:
        for v in bm.verts:
            if not v.hide and (v.select or not scene.display_sel_only):
                ## CoDEmanx: bm.verts.index_update()?
                draw_index(vert_idx_color, v.index, v.co.to_4d())

    if scene.display_edge_index:
        for e in bm.edges:
            if not e.hide and (e.select or not scene.display_sel_only):
                v1 = e.verts[0].co
                v2 = e.verts[1].co
                loc = v1 + ((v2 - v1) / 2)
                draw_index(edge_idx_color, e.index, loc.to_4d())

    if scene.display_face_index:
        for f in bm.faces:
            if not f.hide and (f.select or not scene.display_sel_only):
                draw_index(
                    face_idx_color, f.index, f.calc_center_median().to_4d())


# operator
class IndexVisualiser(bpy.types.Operator):
    bl_idname = "view3d.index_visualiser"
    bl_label = "Index Visualiser"
    bl_description = "Toggle the visualisation of indices"

    _handle = None

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH"

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()

        # removal of callbacks when operator is called again
        if context.scene.display_indices == -1:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            context.scene.display_indices = 0
            return {"CANCELLED"}

        return {"PASS_THROUGH"}

    def invoke(self, context, event):
        if context.area.type == "VIEW_3D":
            if context.scene.display_indices < 1:
                # operator is called for the first time, start everything
                context.scene.display_indices = 1
                self._handle = bpy.types.SpaceView3D.draw_handler_add(
                    draw_callback_px, (self, context), 'WINDOW', 'POST_PIXEL')
                context.window_manager.modal_handler_add(self)
                return {"RUNNING_MODAL"}
            else:
                # operator is called again, stop displaying
                context.scene.display_indices = -1
                return {'RUNNING_MODAL'}
        else:
            self.report({"WARNING"}, "View3D not found, can't run operator")
            return {"CANCELLED"}


# defining the panel
def menu_func(self, context):
    self.layout.separator()
    scn = context.scene

    col = self.layout.column(align=True)
    col.operator(IndexVisualiser.bl_idname, text="Visualize indices")
    row = col.row(align=True)
    row.active = (context.mode == "EDIT_MESH" and scn.display_indices == 1)

    row.prop(scn, "display_vert_index", toggle=True)
    row.prop(scn, "display_edge_index", toggle=True)
    row.prop(scn, "display_face_index", toggle=True)
    row = col.row(align=True)
    row.active = context.mode == "EDIT_MESH" and scn.display_indices == 1
    row.prop(context.scene, "display_sel_only")
    # row.prop(context.scene, "live_mode")


def register_properties():
    bpy.types.Scene.display_indices = bpy.props.IntProperty(
        name="Display indices",
        default=0)
    # context.scene.display_indices = 0
    bpy.types.Scene.display_sel_only = bpy.props.BoolProperty(
        name="Selected only",
        description="Only display indices of selected vertices/edges/faces",
        default=True)
    bpy.types.Scene.display_vert_index = bpy.props.BoolProperty(
        name="Vertices",
        description="Display vertex indices", default=True)
    bpy.types.Scene.display_edge_index = bpy.props.BoolProperty(
        name="Edges",
        description="Display edge indices")
    bpy.types.Scene.display_face_index = bpy.props.BoolProperty(
        name="Faces",
        description="Display face indices")
    bpy.types.Scene.live_mode = bpy.props.BoolProperty(
        name="Live",
        description="Toggle live update of the selection, can be slow",
        default=False)


def unregister_properties():
    del bpy.types.Scene.display_indices
    del bpy.types.Scene.display_sel_only
    del bpy.types.Scene.display_vert_index
    del bpy.types.Scene.display_edge_index
    del bpy.types.Scene.display_face_index
    del bpy.types.Scene.live_mode


def register():
    register_properties()
    bpy.utils.register_class(IndexVisualiser)
    bpy.types.VIEW3D_PT_view3d_meshdisplay.append(menu_func)


def unregister():
    bpy.utils.unregister_class(IndexVisualiser)
    unregister_properties()
    bpy.types.VIEW3D_PT_view3d_meshdisplay.remove(menu_func)


if __name__ == "__main__":
    register()
