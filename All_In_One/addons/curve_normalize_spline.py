'''
BEGIN GPL LICENSE BLOCK

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

END GPL LICENCE BLOCK
'''

bl_info = {
    'name': 'Normalize Spline',
    'author': 'Dealga McArdle (zeffii)',
    'version': (0, 0, 1),
    'blender': (2, 6, 7),
    'location': '3d view > Tool properties > Normalize Spline',
    'description': 'select a spline/curve, drag the slidersit will fillet the edge.',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Mesh'}


import math

import bpy
import bgl
import blf
import mathutils
import bpy_extras

from mathutils import Vector
from mathutils.geometry import interpolate_bezier
from bpy_extras.view3d_utils import location_3d_to_region_2d as loc3d2d
 
def get_points(spline, clean=True, res=False):
    cyclic = True
    knots = spline.bezier_points

    if len(knots) < 2: 
        return

    r = (res if res else spline.resolution_u) + 1
    segments = len(knots)
    
    if not spline.use_cyclic_u:
        cyclic = False
        segments -= 1
 
    master_point_list = []
    for i in range(segments):
        inext = (i + 1) % len(knots)
 
        knot1 = knots[i].co
        handle1 = knots[i].handle_right
        handle2 = knots[inext].handle_left
        knot2 = knots[inext].co
        
        bezier = knot1, handle1, handle2, knot2, r
        points = interpolate_bezier(*bezier)
        master_point_list.extend(points)
 
    # some clean up to remove consecutive doubles, this could be smarter...
    if clean:
        old = master_point_list
        good = [v for i, v in enumerate(old[:-1]) if not old[i] == old[i+1]]
        good.append(old[-1])
        return good, cyclic
            
    return master_point_list, cyclic

def normalized_spline(self, context, spline_config):
    scn = context.scene
    res = scn.SplineResolution

    edge_keys = spline_config.edge_keys
    points = spline_config.points
    num_points = len(points)-1
    total_length = spline_config.total_length
    max_len = total_length / (res - 1)

    # gets coordinates related to the incoming indices
    v = lambda i, j: points[edge_keys[i][j]]

    # returns the length of an edge segment
    d = lambda i: (v(i, 0) - v(i, 1)).length

    # returns the two coordinates of a given edge segment
    e = lambda i: (v(i, 0), v(i,1))

    norm_points = []
    norm_points.append(points[0])

    # this is called recursively
    def consume(p1, p2, cl, idx):
        print(idx, '/', num_points)
        if idx > (num_points - 1):
            norm_points.append(points[-1])
            return

        test_edge = (p1-p2).length

        if test_edge + cl < max_len:
            cl += test_edge
            next_point = points[idx+1]
            consume(p2, next_point, cl, idx+1)

        elif test_edge + cl == max_len:
            norm_points.append(p2)
            next_point = points[idx+1]
            comsume(p2, next_point, 0, idx+1)

        elif test_edge + cl > max_len:
            excess = cl + test_edge - max_len
            num_times = math.floor(test_edge/max_len)

            bit_to_add = test_edge - (num_times * max_len) 
            ratio = bit_to_add / test_edge

            p1 = p1.lerp(p2, ratio)
            norm_points.append(p1)
            consume(p1, p2, 0, idx)
                

    p1, p2 = e(0)
    consume(p1, p2, 0, 1)

    return norm_points


def get_edge_keys(points, cyclic):
    num_points = len(points)
    edges = [[i, i+1] for i in range(num_points-1)]
    if cyclic:
        edges[-1][1] = edges[0][0]

    return edges

def get_total_length(points, edge_keys):
    edge_length = 0
    for edge in edge_keys:
        vert0 = points[edge[0]]
        vert1 = points[edge[1]]
        edge_length += (vert0-vert1).length
    return edge_length


def draw_points(context, points, size, gl_col):
    region = context.region
    rv3d = context.space_data.region_3d
    
    this_object = context.active_object
    matrix_world = this_object.matrix_world  
    
    # needed for adjusting the size of gl_points    
    bgl.glEnable(bgl.GL_POINT_SMOOTH)
    bgl.glPointSize(size)
    bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)
    
    bgl.glBegin(bgl.GL_POINTS)
    bgl.glColor4f(*gl_col)    
    for coord in points:
        # vector3d = matrix_world * (coord.x, coord.y, coord.z)
        vector3d = matrix_world * coord
        vector2d = loc3d2d(region, rv3d, vector3d)
        bgl.glVertex2f(*vector2d)
    bgl.glEnd()
    
    bgl.glDisable(bgl.GL_POINT_SMOOTH)
    bgl.glDisable(bgl.GL_POINTS)
    return

def draw_callback_px(self, context):
    scn = context.scene
    region = context.region
    rv3d = context.space_data.region_3d

    spline = context.active_object.data.splines[0]

    if scn.NumVerts:
        resolution = scn.NumVerts

    if resolution == spline.resolution_u:
        resolution = False

    # get the desired resolution of points, these are used to then
    # evenly space out points for the approximated curve
    points, cyclic = get_points(spline, clean=True, res=resolution)

    edge_keys = get_edge_keys(points, cyclic)
    total_length = get_total_length(points, edge_keys)  # could print to view

    # adjust space between points to equidistant
    spline_config = lambda: None
    spline_config.points = points
    spline_config.edge_keys = edge_keys
    spline_config.total_length = total_length

    # disable this for now.
    #if not resolution:
    points = normalized_spline(self, context, spline_config)

    draw_points(context, points, 4.2, (0.2, 0.9, 0.2, .2))    

    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
    return


  
# create 4 verts, string them together to make 4 edges.  
if False:  
    Verts, Edges = [], []
      
    profile_mesh = bpy.data.meshes.new("Base_Profile_Data")  
    profile_mesh.from_pydata(Verts, Edges, [])  
    profile_mesh.update()  
      
    profile_object = bpy.data.objects.new("Base_Profile", profile_mesh)  
    profile_object.data = profile_mesh  
      
    scene = bpy.context.scene  
    scene.objects.link(profile_object)  
    profile_object.select = True  

# should be toggle on/off 
class OBJECT_OT_draw_fillet(bpy.types.Operator):
    bl_idname = "dynamic.normalize"
    bl_label = "Draw Normalized"
    bl_description = "Allows the user to dynamically set curve resolution"
    bl_options = {'REGISTER', 'UNDO'}
    
    # i understand that a lot of these ifs are redundant, scheduled for
    # deletion. is 'RELEASE' redundant for keys?
   
    def modal(self, context, event):
        context.area.tag_redraw()

        if not context.active_object.type == 'CURVE':
            return {'CANCELLED'}
        return {'PASS_THROUGH'}
    
    def invoke(self, context, event):

        if context.area.type == 'VIEW_3D':
            context.area.tag_redraw()
            context.window_manager.modal_handler_add(self)
                    
            # Add the region OpenGL drawing callback
            # draw in view space with 'POST_VIEW' and 'PRE_VIEW'
            self._handle = context.region.callback_add(
                            draw_callback_px, 
                            (self, context), 
                            'POST_PIXEL')
            
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, 
            "View3D not found, cannot run operator")
            context.area.tag_redraw()            
            return {'CANCELLED'}
    


class UIPanel(bpy.types.Panel):
    bl_label = "Spline Normalize"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOL_PROPS"
 
    scn = bpy.types.Scene
    
    scn.SplineResolution = bpy.props.IntProperty(min=2, max=100, default=30,
                                            name="Spline Resolution")

    scn.NumVerts = bpy.props.IntProperty(min=2, max=64, default=12,
                                            name="number of verts")


    
    @classmethod
    def poll(self, context):
        # i don't really care if this is in editmode or object mode
        return context.object.type == 'CURVE'
        
    
    def draw(self, context):
        layout = self.layout
        scn = context.scene


        row1 = layout.row(align=True)
        row1.prop(scn, "SplineResolution", expand = True)

        row2 = layout.row(align=True)
        row2.operator("dynamic.normalize")

        row3 = layout.row(align=True)
        row3.prop(scn, "NumVerts", expand = True)





# boilerplate register stuff

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
 
if __name__ == "__main__":
    register() 
