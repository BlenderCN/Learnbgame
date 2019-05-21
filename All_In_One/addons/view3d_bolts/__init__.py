# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you may redistribute it, and/or
# modify it, under the terms of the GNU General Public License
# as published by the Free Software Foundation - either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, write to:
#
#   the Free Software Foundation Inc.
#   51 Franklin Street, Fifth Floor
#   Boston, MA 02110-1301, USA
#
# or go online at: http://www.gnu.org/licenses/ to view license options.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    "name": "conveniences for 3dview",
    "author": "zeffii",
    "version": (0, 1, 0),
    "blender": (2, 6, 1),
    "location": "3d view, N panel",
    "description": "Adds features to various toolbars.",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame"
}

import bpy
import bmesh

def print_details(num_edges, edge_length):
    print("number of edges: {0}".format(num_edges))
    print("combined length: {0:6f}".format(edge_length))


def get_combined_length(object_reference):

    # Get a BMesh representation
    bm = bmesh.from_edit_mesh(object_reference.data)

    selected_edges = [edge for edge in bm.edges if edge.select]
    num_edges = len(selected_edges)

    edge_length = 0
    for edge in selected_edges:
        edge_length += edge.calc_length()
         
    print_details(num_edges, edge_length)
    return round(edge_length, 6)
    

class SumButton(bpy.types.Operator):
    bl_idname = "scene.calculate_length"
    bl_label = "Sometype of operator"
 
    def execute(self, context):
        obj_reference = context.active_object
        length = str(get_combined_length(obj_reference))
        context.scene.my_string = length
        return{'FINISHED'}


def draw_item(self, context):
    layout = self.layout
    obj = context.object
    row = layout.row()
    scn = context.scene

    # display label and button
    if obj:
        row.label(text="summed edge length:")
        row = layout.row()
        
        split = row.split(percentage=0.75)
        col = split.column()
        col.prop(scn, 'my_string')

        split = split.split()
        col = split.column()
        col.operator("scene.calculate_length", text='Sum')


def initSceneProperties(scn):
    bpy.types.Scene.my_string = bpy.props.StringProperty(
        name = "")
    scn['my_string'] = ""
    return

def draw_item_2(self, context):
    layout = self.layout
    obj = context.object
    row = layout.row()

    if obj:
        row.operator("view3d.snap_cursor_to_selected", text='Snap to selected')


def register():
    initSceneProperties(bpy.context.scene)
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_PT_view3d_cursor.append(draw_item_2)
    bpy.types.VIEW3D_PT_view3d_meshdisplay.append(draw_item)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.VIEW3D_PT_view3d_cursor.remove(draw_item_2)
    bpy.types.VIEW3D_PT_view3d_meshdisplay.remove(draw_item)

if __name__ == "__main__":
    register()