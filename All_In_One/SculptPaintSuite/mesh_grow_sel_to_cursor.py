#  ***** BEGIN GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  ***** END GPL LICENSE BLOCK *****

bl_info = {
    "name": "Grow Selection to 3D Cursor",
    "description": "Adds an operator that grows mesh selection towards the 3D cursor.",
    "author": "Jean Ayer (vrav)", # legal / tracker name: Cody Burrow
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "Preferences > Keymap > assign mesh.grow_sel_to_cursor",
    "category": "Mesh"
}

import bpy
import bmesh
from math import isclose
from mathutils import Vector

def vec3_dist_sq(v1, v2):
    vd = v1 - v2
    return (vd.x**2 + vd.y**2 + vd.z**2)

def get_end_vert(bm, cl):
    closest_to_end = None
    closest_dist = float("inf")
    for vert in bm.verts:
        dist = vec3_dist_sq(cl, vert.co)
        if abs(dist) < closest_dist:
            closest_dist = dist
            closest_to_end = vert
    return closest_to_end

def find_next_in_path(path):
    vert = path[-1]
    for edge in vert.link_edges:
        for n in edge.verts:
            if n.select and n not in path:
                return n

def get_neighboring_verts(vert):
    neighbors = []
    [neighbors.extend(edge.verts) for edge in vert.link_edges]
    neighbors = list(set(neighbors))
    neighbors.remove(vert)
    return neighbors

def get_path(start, end):
    if start == end:
        # print("end vert same as start")
        return {"path": [start], "dist": 0.0}
    
    # also need to check if start and end are connected
    # shortest_path_select() deselects them if so, which is bad
    neighbors = get_neighboring_verts(start)
    if end in neighbors:
        # print("adjacent verts")
        return {
            "path": [start, end],
            "dist":vec3_dist_sq(start.co, end.co)
        }
    
    bpy.ops.mesh.select_all(action='DESELECT')
    start.select_set(True)
    end.select_set(True)
    bpy.ops.mesh.shortest_path_select()
    
    path = [start]
    while path[-1]:
        path.append(find_next_in_path(path))
    
    dist = 0.0
    if len(path) > 1:
        for i in range(len(path)-1):
            if path[i+1]:
                dist += vec3_dist_sq(path[i].co, path[i+1].co)
    
    bpy.ops.mesh.select_all(action='DESELECT')
    return {
        "path": path[0:-1],
        "dist": dist,
        }

def select_bmesh_elems_if_verts(bm, elems):
    for elem in elems:
        all_selected = True
        for vert in elem.verts:
            if not vert.select:
                all_selected = False
        if all_selected:
            elem.select_set(True)

class EDIT_OT_grow_sel_to_cursor(bpy.types.Operator):
    bl_idname = "mesh.grow_sel_to_cursor"
    bl_options = {'REGISTER', 'UNDO'}
    bl_label = "Grow Selection to 3D Cursor"
    bl_description = "Grows selection towards the 3D cursor."
    
    @classmethod
    def poll(cls, context):
        return (context.area.type == 'VIEW_3D'
                and context.mode in {'EDIT_MESH'})
    
    def execute(self, context):
        cl = bpy.context.scene.cursor_location
        ob = bpy.context.active_object
        bm = bmesh.from_edit_mesh(ob.data)
        
        end_vert = get_end_vert(bm, cl)

        start_verts = []
        for vert in bm.verts:
            if vert.select:
                start_verts.append(vert)
        
        previous_select_mode = [
            bpy.context.tool_settings.mesh_select_mode[0],
            bpy.context.tool_settings.mesh_select_mode[1],
            bpy.context.tool_settings.mesh_select_mode[2]
        ]
        # disable face and edge selections, only need vertex selections
        bpy.context.tool_settings.mesh_select_mode[0] = True
        bpy.context.tool_settings.mesh_select_mode[1] = False
        bpy.context.tool_settings.mesh_select_mode[2] = False
        
        # print()
        # print("new run")
        to_select = []
        to_select.extend(start_verts)

        for vert in start_verts:
            # print(vert.index)
            # grow selection from selected verts
            
            v2s = get_neighboring_verts(vert)
            for v2 in v2s:
                # v2 == 'next' vert to potentially select
                if v2 in start_verts or v2 in to_select:
                    continue
                
                # if single vert surrounded by selected verts, select it
                neighbors = get_neighboring_verts(v2)
                all_selected = True
                for n in neighbors:
                    if not n in to_select:
                        all_selected = False
                if all_selected:
                    # print("single vert surrounded")
                    to_select.append(v2)
                    continue
                
                # compare path from selected vert to end, and 'next' vert to end
                vpath = get_path(vert, end_vert)
                v2path = get_path(v2, end_vert)
                # print(v2path["dist"], vpath["dist"])
                if v2path["dist"] < vpath["dist"] or v2path["dist"] == 0.0:
                    to_select.append(v2)

        # print("selecting", len(to_select))
        for vert in to_select:
            vert.select_set(True)
            
        # cascade selection upward to edges and faces
        select_bmesh_elems_if_verts(bm, bm.edges)
        select_bmesh_elems_if_verts(bm, bm.faces)
        
        # return to previous selection mode(s)
        # reverse order because vertex can't be set to false if it's the only one set to true
        bpy.context.tool_settings.mesh_select_mode[2] = previous_select_mode[2]
        bpy.context.tool_settings.mesh_select_mode[1] = previous_select_mode[1]
        bpy.context.tool_settings.mesh_select_mode[0] = previous_select_mode[0]
        
        bmesh.update_edit_mesh(ob.data)
        return {'FINISHED'}

classes = (
    EDIT_OT_grow_sel_to_cursor,
)
register, unregister = bpy.utils.register_classes_factory(classes)
