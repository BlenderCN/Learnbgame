

#    NeuroMorph_Measurements.py (C) 2018,  Anne Jorstad, Biagio Nigro, Diego Marcos
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/

bl_info = {
    "name": "NeuroMorph Measurement Tools:  Submesh Volume, Surface Area, and Length",
    "description": "Calculates the surface area, volume, and length of user-determined subregions of meshes",
    "author": "Anne Jorstad, Biagio Nigro, Diego Marcos",
    "version": (1, 2, 5),
    "blender": (2, 7, 8),
    "location": "View3D > Add > Mesh",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}


import bpy
from bpy.props import *
import math
import mathutils
import os
import re
from os.path import expanduser
#import inspect
import bmesh
    

# get signed volume contribution from single triangle
def get_vol_tri(tri):  
    # tri = [p0, p1, p2],  pn = [x, y, z]
    p0 = tri[0]
    p1 = tri[1]
    p2 = tri[2]
    vcross = cross_product(p1,p2)
    vdot = dot_product(p0, vcross)
    vol = vdot/6
    return vol


def cross_product(v0, v1):
    x =   v0[1]*v1[2] - v0[2]*v1[1]
    y = -(v0[0]*v1[2] - v0[2]*v1[0])
    z =   v0[0]*v1[1] - v0[1]*v1[0]
    return [x,y,z]


def dot_product(v0,v1):
    vec = [v0[n]*v1[n] for n in range(len(v0))]
    return sum(vec)


# get area of single triangle
def get_area_tri(tri):
    # tri = [p0, p1, p2]
    p0 = tri[0]
    p1 = tri[1]
    p2 = tri[2]
    area = mathutils.geometry.area_tri(p0, p1, p2)
    return area

def GetDist(a, b):
    dif = []
    for i in range(0,3):
        dif.append(a.co[i] - b.co[i])
    res = GetNorm(dif)[0]
    return[res]

def GetNorm(a):
    m = 0.0
    for n in a:
        m = m + n**2
    res = math.sqrt(m)
    return[res]




################### length calculation functions ###############################

### All multi-segment distance code commented out in this release

# def MakePolyLine(objname, curvename, cList, obj):  
    
#     scale=obj.scale
#     pos=obj.location
#     rot=obj.rotation_euler
#     w = 1
#     curvedata = bpy.data.curves.new(name=curvename, type='CURVE')    
#     curvedata.dimensions = '3D'    
    
#     objectdata = bpy.data.objects.new(objname, curvedata)    
#     objectdata.location = pos 
#     objectdata.scale = scale 
#     objectdata.rotation_euler = rot
#     bpy.context.scene.objects.link(objectdata)    
    
#     polyline = curvedata.splines.new('POLY')    
#     polyline.points.add(len(cList)-1)    
#     for num in range(len(cList)):    
#         polyline.points[num].co = (cList[num])+(w,)    
    
#     polyline.order_u = len(polyline.points)-1  
#     polyline.use_endpoint_u = True  
#     return objectdata
    
    
# def GetSelVert(obj):
#     sel = []
#     for v in obj.data.vertices:
#         if v.select:
#             sel.append(v)
#     return sel

# class GetVertex(bpy.types.Operator):
#     """Add selected vertex to point list"""
#     bl_idname = "get.vert"
#     bl_label = "Get Vertex"
#     bl_options = {"REGISTER", "UNDO"}
#     def execute(self, context):
#         obj = context.object
#         sel_before = GetSelVert(obj)
        
#         bpy.ops.object.mode_set(mode='OBJECT')
#         bpy.ops.object.mode_set(mode='EDIT')
        
#         sel_after = GetSelVert(obj)        
        
#         if len(sel_after)==1:
#           new_v = sel_after[0].index        
        
#           for v in sel_after:
#             if v not in sel_before:
#                 new_v = v.index
#           obj.vertex_collection.add().index = new_v
        
#           obj.vertex_collection[-1].name = str(new_v)
#         elif len(sel_after)==0:
#            self.report({'INFO'},"No point selected")
#         else:      
#             self.report({'INFO'},"Multiple points selected")
#         return{'FINISHED'}  


# class ClearAllVertices(bpy.types.Operator):
#     """Remove all points from list"""
#     bl_idname = "clear.vert"
#     bl_label = "Clear Vertices"
#     bl_options = {"REGISTER", "UNDO"}
#     def execute(self, context):
#         obj = context.object
#         bpy.ops.object.mode_set(mode='OBJECT')
#         mt=bpy.context.active_object
#         for i in mt.data.vertices:
#            mt.data.vertices[i.index].select=False
#         bpy.ops.object.mode_set(mode='EDIT')   
#         for v in obj.vertex_collection:
#             obj.vertex_collection.remove(0)
            
#         return{'FINISHED'}  

# def SortPath(mt):
# # sort vertices of highlighted edges into ordered list
#           buf_vector = []  # unsorted edges
#           edge_vector=[]   # sorted edges
#           vert_index_vector=[]
#           flag_vector=[]   # mark used edges
#           vert_vector=[]

#           for e in mt.data.edges:  # populate vector with selected edges
#              if e.select==True:
#                buf_vector.append(e)
#                flag_vector.append(0)
             
#           edge_vector.append(buf_vector[0])
#           flag_vector[0]=1       
#           for i in range(len(buf_vector)):  # loop over edges, prepend/append next edge in path
#              start=edge_vector[0].vertices[0]  # first vertex of current path
#              end=edge_vector[len(edge_vector)-1].vertices[1]  # last vertex of current path
             
#              for j in range(len(buf_vector)):  # find next edge
                 
#                  if flag_vector[j]==0 :
                   
#                    if start==buf_vector[j].vertices[1]:  # add to start of list

#                      edge_vector.insert(0,buf_vector[j])
#                      flag_vector[j]=1 
                     
#                    elif start==buf_vector[j].vertices[0]:  # flip and add to start of list
#                      a=buf_vector[j].vertices[0]
#                      buf_vector[j].vertices[0]=buf_vector[j].vertices[1]
#                      buf_vector[j].vertices[1]=a
                      
#                      edge_vector.insert(0,buf_vector[j])
#                      flag_vector[j]=1
                      
                  
#                    elif end==buf_vector[j].vertices[0]:  # add to end of list
#                      edge_vector.append(buf_vector[j])
#                      flag_vector[j]=1
                   
#                    elif end==buf_vector[j].vertices[1]:  # flip and add to end of list
#                      a=buf_vector[j].vertices[0]
#                      buf_vector[j].vertices[0]=buf_vector[j].vertices[1]
#                      buf_vector[j].vertices[1]=a
                    
#                      edge_vector.append(buf_vector[j])
#                      flag_vector[j]=1
                   
#           # fill vertex list with ordered vertices
#           vert_index_vector.append(edge_vector[0].vertices[0])
#           vert_vector.append(mt.data.vertices[edge_vector[0].vertices[0]].co[:])
#           for v in edge_vector:     
#                  vert_index_vector.append(v.vertices[1])
#                  a=v.vertices[1]
#                  vert_vector.append(mt.data.vertices[a].co[:])

#           return vert_vector


# #Define a collection property associated to each object to contain the selected vertices
# class VertexListItem(bpy.types.PropertyGroup):
#     index = bpy.props.IntProperty()
#     #template_list_controls = bpy.props.StringProperty(default="", options={"HIDDEN"})  # for Blender 2.65 only?


# class LengthMultiSegment(bpy.types.Operator):
#     """Length of line segments connecting multiple points"""
#     bl_idname = "object.length_in_space"
#     bl_label = "Create Curve from at least two selected vertices"
#     bl_options = {"REGISTER", "UNDO"}

#     def execute(self, context):
#         obj = context.object
        
#         data = obj.data
#         count = 0
#         vert_vector = []
#         if len(obj.vertex_collection)>=2:
#           for v in obj.vertex_collection:
#             vert_vector.append(data.vertices[v.index].co[:])

#           #vert_vector.sort()    
#           new_name = obj.string_name + "_MS_dist"
#           curve = MakePolyLine(new_name, "length", vert_vector, obj)
#           bpy.ops.object.mode_set(mode='OBJECT')
#           poly=curve
#           poly.select=True             
#           bpy.context.scene.objects.active = poly
#           poly.parent = obj                         
        
#           # show curve on top of mesh for better display
#           poly.show_wire = True

#           poly.hide=True
#           obj.select=True
#           bpy.context.scene.objects.active = obj
#           bpy.ops.object.mode_set(mode='EDIT')
#         else:
#             self.report({'INFO'},"Select and add at least two points")  
#             obj.select=True
#             bpy.context.scene.objects.active = obj
#             bpy.ops.object.mode_set(mode='EDIT')
            
#         return{'FINISHED'}



class Length3D(bpy.types.Operator):
    """Length of line segment connecting two selected points in space"""
    bl_idname = "object.length_in_space"
    bl_label = "Length of line segment connecting two selected points in space"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        obj = bpy.context.object
        vert_inds = [vind for vind, vert in enumerate(obj.data.vertices) if vert.select == True]
        if len(vert_inds) == 2:

            # Calculate distance
            # Convert to global coordinates, just in case this hasn't already been done
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            v1 = obj.data.vertices[vert_inds[0]].co
            v2 = obj.data.vertices[vert_inds[1]].co
            dist = (v1-v2).length
            bpy.context.scene.last_len = dist
            bpy.ops.object.mode_set(mode='EDIT')

            # Create new object from selected points
            if bpy.context.scene.create_length_obj:
                bpy.ops.mesh.edge_face_add()  # add edge between selected vertices

                # Store index of new edge (to delete later)
                bpy.ops.object.mode_set(mode='OBJECT')
                e_ind = [ii for ii,e in enumerate(obj.data.edges) if e.select == True][0]
                bpy.ops.object.mode_set(mode='EDIT')

                # Create the new object
                curve = new_obj_from_selected_verts(obj)
                curve.name = obj.name + "_dist_3D_seg"
                curve.length = dist

                # Delete edge from original object
                bpy.ops.object.mode_set(mode='OBJECT')
                obj.select = True
                bpy.context.scene.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
                obj.data.edges[e_ind].select = True
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.delete(type='EDGE')
                activate_new_curve(curve, obj)

        else:
            self.report({'INFO'},"Select exactly two points on mesh")
            obj.select=True
            bpy.context.scene.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
        return{'FINISHED'}



def add_face_edges(obj, vert_inds):
# add edges to connect vertices on each face across the face:
# for each quadrilateral face, add the two diagonals,
# for each n>4-sided face, add the centroid and edges connecting
# it to each original vertex,
# leave triangular faces as they are

    bpy.ops.object.mode_set(mode='EDIT')
    obj = bpy.context.object
    data = obj.data
    bm = bmesh.new()   # create an empty BMesh
    bm.from_mesh(data)   # fill it in from a Mesh

    # find shortest path using centroids of all faces;
    # only add diagonal edges to quad faces that include
    # vertices from this shortest path
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.poke()  # adds the centroid to each face and radial edges connecting it each vertex
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    for vind in vert_inds:
        data.vertices[vind].select=True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.shortest_path_select()
    bpy.ops.object.mode_set(mode='OBJECT')

    # store the indices of these vertices, then undo, then proceed
    poke_path_inds = []
    for v in data.vertices:
        if v.select:
            poke_path_inds.append(v.index)
    # undo poke
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.ed.undo()
    bpy.ops.object.mode_set(mode='OBJECT')

    # handle quad faces
    bm.verts.ensure_lookup_table()
    for face in data.polygons:
        if len(face.vertices) == 4:
            on_path_flag = 0
            for vert in face.vertices:
                if vert in poke_path_inds:
                    on_path_flag = 1
                    break
            if on_path_flag:
                v0bm = bm.verts[face.vertices[0]]
                v1bm = bm.verts[face.vertices[1]]
                v2bm = bm.verts[face.vertices[2]]
                v3bm = bm.verts[face.vertices[3]]
                e1 = [v0bm, v2bm]
                e2 = [v1bm, v3bm]
                bm.edges.new(e1)
                bm.edges.new(e2)
    bm.edges.index_update()
    bpy.ops.object.mode_set(mode='OBJECT')
    bm.to_mesh(data)
    bpy.ops.object.mode_set(mode='EDIT')

    # handle non-quad faces  (leave triangular faces as they are)
    # if many faces with >4 sides might be slow
    for face in bm.faces:  # use the bmesh data structure: pointers don't go away after context change
        if len(face.verts) > 4:
            bpy.ops.mesh.select_all(action='DESELECT')
            face.select = True
            bpy.ops.object.mode_set(mode='OBJECT')
            bm.to_mesh(data)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.poke()

    bm.edges.index_update()
    bmesh.update_edit_mesh(data, destructive=True)  # to update mesh in scene
    bm.free()



class PathOnMesh(bpy.types.Operator):
    """Shortest path between two points through vertices on the mesh"""
    bl_idname = "object.length_on_mesh"
    bl_label = "Create Shortest Path connecting two selected vertices"
    bl_options = {"REGISTER", "UNDO"}
    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT')
        obj = context.object
        vert_inds = [vind for vind, vert in enumerate(obj.data.vertices) if vert.select == True]
        if len(vert_inds)==2:

            # Temporarily add edges to connect vertices across each face
            add_face_edges(obj, vert_inds)

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            bpy.ops.object.mode_set(mode='OBJECT')

            for vind in vert_inds:
                obj.data.vertices[vind].select = True

            # Calculate the shortest path
            bpy.ops.object.mode_set(mode='EDIT')
            err = bpy.ops.mesh.shortest_path_select()  
            bpy.ops.object.mode_set(mode='OBJECT')

            if "CANCELLED" in err:
                self.report({'INFO'},"Cannot calculate path: points are from disconnected parts of the mesh")
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.ed.undo()
                bpy.ops.object.mode_set(mode='OBJECT')
                obj.select=True
                bpy.context.scene.objects.active = obj
                bpy.ops.object.mode_set(mode='EDIT')
                return{'FINISHED'}

            # shortest_path_select() returns nothing if points are neighbors, so select them again
            verts_out = [v for v in obj.data.vertices if v.select == True]
            if len(verts_out) == 0:
                for vind in vert_inds:
                    obj.data.vertices[vind].select = True

            # Display length
            dist = get_total_length_of_edges(obj)

            # Create new object from selected points
            if bpy.context.scene.create_length_obj:
                curve = new_obj_from_selected_verts(obj)
                curve.name = obj.name + "_dist_on_mesh"
                curve.length = dist

            # Undo the triangulate operation
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.ed.undo()

            if bpy.context.scene.create_length_obj:
                activate_new_curve(curve, obj)

            else:  # Reactivate initial two points
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.ops.object.mode_set(mode='OBJECT')
                for v in vert_inds:
                    obj.data.vertices[v].select = True
                bpy.ops.object.mode_set(mode='EDIT')

        else:
            self.report({'INFO'},"Select exactly two points on mesh")
            obj.select=True
            bpy.context.scene.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
        return{'FINISHED'}


class GetEdgeLengths(bpy.types.Operator):
    """Total length of all selected edges (or points)"""
    bl_idname = "object.length_edges"
    bl_label = "Calculate Length of Selected Edges"
    
    def execute(self, context):
        start_mode = bpy.context.active_object.mode
        obj = bpy.context.object
        dist = get_total_length_of_edges(obj)
        bpy.ops.object.mode_set(mode=start_mode)

        if bpy.context.scene.create_length_obj:
            curve = new_obj_from_selected_verts(obj)
            curve.name = obj.name + "_dist_edges"
            curve.length = dist
            activate_new_curve(curve, obj)

        return {"FINISHED"}


def get_total_length_of_edges(ob):
    # Get length of all elected edges on an object
    # Assign total length to scene variable

    # Convert to global coordinates, just in case this hasn't already been done
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Get length of all edges
    bpy.ops.object.mode_set(mode='EDIT')
    select_as_vert = tuple(bpy.context.scene.tool_settings.mesh_select_mode)[1]
    bpy.ops.mesh.select_mode(type="EDGE")
    bpy.ops.object.mode_set(mode='OBJECT')
    edges = [ed for ed in ob.data.edges if ed.select == True]

    total_len = 0
    for ed in edges:
        v1 = ob.data.vertices[ed.vertices[0]].co
        v2 = ob.data.vertices[ed.vertices[1]].co
        total_len += (v1-v2).length
    bpy.context.scene.last_len = total_len

    if not select_as_vert:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.object.mode_set(mode='OBJECT')

    return(total_len)


def new_obj_from_selected_verts(obj):
    obs0 = [ob.name for ob in bpy.context.scene.objects]

    obj.select = True
    bpy.context.scene.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.duplicate_move()
    bpy.ops.mesh.separate(type='SELECTED')

    # select the newly created object
    obs1 = [ob.name for ob in bpy.context.scene.objects]
    new_ob_name = [o1 for o1 in obs1 if o1 not in obs0][0]  # the newly created object
    new_obj = bpy.context.scene.objects[new_ob_name]
    return (new_obj)

def activate_new_curve(curve, obj):
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    curve.select=True
    bpy.context.scene.objects.active = curve
    curve.show_wire = True  # Show curve on top of mesh for better display
    curve.parent = obj  # Assign curve to be child of parent object
    # curve.hide=True
    # obj.select=True
    # bpy.context.scene.objects.active = obj
    # bpy.ops.object.mode_set(mode='EDIT')



################### end length calculation functions ############################### 

# calculate surface area of mesh
def fget_SA(self):
    obj = self.data
    if hasattr(obj, 'polygons'):
        n_faces = len(obj.polygons)
        SA = 0
        for f in range(0, n_faces):
            n_vertices = len(obj.polygons[f].vertices[:])
            if n_vertices != 3:  # faces must be triangles
                return 'highlight a subregion'
            tri = [0] * n_vertices
            for v in range(0, n_vertices):
                tri[v] = obj.vertices[obj.polygons[f].vertices[v]].co
            SA += get_area_tri(tri)
        return SA
    else:
        return 'property not available'


# calculate volume of mesh (assumed to be closed surface)
# note:  if remove faces from previously closed solids,
#        tool will return incorrect volume
# There is no efficient way from this function 
# to check whether mesh is closed
def fget_vol(self):
    obj = self.data
    if hasattr(obj, 'polygons'):
        # if mesh not closed, don't calculate volume
        if self.is_open:
            return 'open mesh has no volume'
        if not self.has_vol:  
            # only calculate volume of objects created  
            # with volume button in this tool
            return 'volume not calculated'

        n_faces = len(obj.polygons)
        vol = 0
        for f in range(0, n_faces):
            this_face = obj.polygons[f]
            n_vertices = len(this_face.vertices[:])
            if n_vertices != 3:
                for v in range(0, n_vertices):
                    # return 'highlight a subregion'
                    return 'faces must be triangles'
            tri = [0] * n_vertices
            for v in range(0, n_vertices):
                tri[v] = obj.vertices[obj.polygons[f].vertices[v]].co
            vol += get_vol_tri(tri)

        return vol
    else:
        return 'property not available'


# calculate number of vertices in the mesh
def fget_nverts(self):
    if hasattr(self.data, 'vertices'):
        nverts = len(self.data.vertices)
        return nverts
    else:
        return 'property not available'


# calculate length of curve
def fget_curvelength(self): 
    # if hasattr(self.data, 'splines'):
    #     points = self.data.splines[0].points
    #     l = len(points) - 1
    #     d = 0.0
    #     for n in range(0,l):
    #         part = GetDist(points[n],points[n+1])[0]
    #         d = d + part
    #     return d
    if self.length >= 0:
        return self.length
    else:
        return 'property not available'
        


# object panel to display new geometry properties
class PropertyPanel_geometry(bpy.types.Panel):
    bl_idname = "geometrypanel"
    bl_label = "Geometry Properties"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        display_split(layout, 'Object Name:  ', str(bpy.context.active_object.name))
        display_split(layout, 'Surface Area:  ', str(bpy.context.active_object.SA))
        display_split(layout, 'Volume:  ', str(bpy.context.active_object.vol))
        display_split(layout, 'Number of Vertices:  ', str(bpy.context.active_object.nverts))
        display_split(layout, 'Length of Curve:  ', str(bpy.context.active_object.curvelength))

# helper function for PropertyPanel_geometry()
def display_split(layout, str1, str2):
    split = layout.row().split(percentage=0.4)
    colL = split.column()
    colR = split.column()
    colL.label(text=str1)
    colR.label(text=str2)
        

# these functions need to exist but are not used
def fset_vol(self, value):
    self.vol = -1
def fset_SA(self, value):
    self.SA = -1
def fset_nverts(self, value):
    self.nverts = -1
def fset_curvelength(self, value):
    self.curvelength = -1

# return n lists of lists of connected boundary edges
def get_connected_components(edges):  # bpy.context.active_object.data.edges
    nedges = len(edges) 
    c_edges = [[edges[0]]]                                    # connected edges:  [ [ea,eb], [ed], ...]
    c_verts = [[edges[0].vertices[0], edges[0].vertices[1]]]  # connected vertices:  [ [va,vb,vc], [vd,ve], ...]
    n_comps = 1
    for e in range(1, nedges):
        this_edge = edges[e]
        v0 = this_edge.vertices[0]
        v1 = this_edge.vertices[1]
        v0_loc = -1
        v1_loc = -1
        for n in range(0,n_comps):
            if v0 in c_verts[n]:
                v0_loc = n
            if v1 in c_verts[n]:
                v1_loc = n
        if v0_loc >= 0:
            if v1_loc >= 0:  # append list v1_loc to list v0_loc
                c_edges[v0_loc].append(this_edge)
                if v0_loc != v1_loc:
                    for elt in c_verts[v1_loc]:
                        c_verts[v0_loc].append(elt)
                    c_verts.remove(c_verts[v1_loc])
                    for elt in c_edges[v1_loc]:
                        c_edges[v0_loc].append(elt)
                    c_edges.remove(c_edges[v1_loc])
                    n_comps = n_comps - 1
                
            else:  # add to v0_loc
                c_verts[v0_loc].append(v1)
                c_edges[v0_loc].append(this_edge)
                
        elif v1_loc >= 0:  # add to v1_loc
            c_verts[v1_loc].append(v0)
            c_edges[v1_loc].append(this_edge)

        else:  # make new list elt
            c_verts.append([v0,v1])
            c_edges.append([this_edge])
            n_comps = n_comps + 1
            
    return c_edges


# remove edges from bdry_edges list that are part of >1 face:
# after region_to_loop(), if both verts of an edge are contained in the bdry,
# then the edge is contained, even if the edge is actually interior
def remove_false_bdry_edges(bdry_edges):
    extra = []
    for edge in bdry_edges:
        v0 = edge.vertices[0]
        v1 = edge.vertices[1]
        face_count = 0
        for face in bpy.context.active_object.data.polygons:
            f_verts = face.vertices[:]
            if v0 in f_verts and v1 in f_verts:
                face_count += 1
        if face_count > 1:
            extra.append(edge)
    for edge in extra:
        bdry_edges.remove(edge)
    return bdry_edges


# called by Create_Submesh and Create_Closed_Submesh
def create_submesh_code():
        bpy.ops.object.mode_set(mode='OBJECT')
        obj_ptr = bpy.context.active_object
        if obj_ptr.type=="MESH":
          bpy.ops.object.mode_set(mode='EDIT')
        
          obj_data = obj_ptr.data
          verts = [list(v.co) for v in obj_data.vertices]
          faces = [f.vertices[:] for f in obj_data.polygons]

          # extracted selected vertices and their faces
          sel_inds = [vert.index for vert in bpy.context.active_object.data.vertices if vert.select]
          selected_verts = [verts[v] for v in sel_inds]
          selected_faces = []  # require all vertices on a face to be in selected_verts
          for f in faces:
              if all(f[n] in sel_inds for n in range(len(f))):
                  face_new_inds = [sel_inds.index(f[n]) for n in range(len(f))]
                  selected_faces.append(face_new_inds)

          # create a new mesh object and link it to the scene               
          new_name = bpy.context.object.string_name
          new_name1 = new_name + "_surf"
          mesh = bpy.data.meshes.new(new_name1)
          new_obj = bpy.data.objects.new(new_name1, mesh)
          new_obj.location = obj_ptr.location
          new_obj.scale = obj_ptr.scale
        
          new_obj.rotation_euler = obj_ptr.rotation_euler
          bpy.context.scene.objects.link(new_obj)
          mesh.from_pydata(selected_verts, [], selected_faces)
          mesh.update(calc_edges=True)

          # convert to triangles, if not already  (necessary for calculations)
          bpy.ops.object.mode_set(mode='OBJECT')
          bpy.context.scene.objects.active = new_obj
          bpy.ops.object.mode_set(mode='EDIT')
          bpy.ops.mesh.quads_convert_to_tris()
          bpy.ops.object.mode_set(mode='OBJECT')

          return (new_obj, new_name, obj_ptr, sel_inds, selected_verts, selected_faces)
        else:
          return 0

# called by Create_Submesh and Create_Open_Submesh
def make_original_active(obj_ptr, sel_inds):
    bpy.ops.object.mode_set(mode='OBJECT')   # must be in object mode to update active vertices
    bpy.context.scene.objects.active = obj_ptr
    for ind in sel_inds:
        bpy.context.active_object.data.vertices[ind].select = True
    bpy.ops.object.mode_set(mode='EDIT') 
    return


# create a new mesh object defined by the selected vertices;
# the object returned has the correct surface area for exactly the selected region,
# but has a meaningless volume if the mesh is not closed
class Create_Submesh(bpy.types.Operator):
    """Create surface area mesh as child of selected object"""
    bl_idname = "mesh.create_submesh"
    bl_label = "create submesh"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        # construct open submesh
        #if create_submesh_code()!=0:
            
        (new_obj, new_name, obj_ptr, sel_inds, selected_verts, selected_faces) = create_submesh_code()
        if new_obj is not None:
        # make the new object a child of the original mesh
        # this changes the location of the object, so use the ChildOf relation (for bones, not parent)
        # to undo transform from .parent operation (http://www.foro3d.com/archive/index.php/t-102869.html)
          new_obj.parent = obj_ptr
          bpy.context.scene.objects.active = new_obj
          #bpy.ops.object.constraint_add(type='CHILD_OF')  # set new object to move with parent object, Blender vsn <= 2.66
          #new_obj.constraints['Child Of'].target = obj_ptr
          ##bpy.ops.constraint.childof_set_inverse(constraint=new_obj.constraints['Child Of'].name, owner='OBJECT')
          #bpy.ops.object.mode_set(mode='EDIT')
          #bpy.ops.object.mode_set(mode='OBJECT')

          # determine if object is open or closed
          bpy.ops.object.mode_set(mode='EDIT')
          bpy.ops.mesh.region_to_loop()
          bpy.ops.object.mode_set(mode='OBJECT')
          bdry_edges = [edge for edge in bpy.context.active_object.data.edges if edge.select]
          n_bdry_edges = len(bdry_edges)
          if n_bdry_edges > 0:
              new_obj.is_open = 1
          else:
              new_obj.is_open = 0
              new_obj.has_vol = 1

        # return with all vertices highlighted in edit mode
        # return input object as active
          sel_inds2 = [ind for ind in range(len(new_obj.data.vertices[:]))]
          make_original_active(new_obj, sel_inds2)
        
          make_original_active(obj_ptr, sel_inds)
        
          # uncomment the following
          new_obj.hide = True
          # doing anything here gives a context error
        
        return{'FINISHED'}



# create a new mesh object defined by the selected vertices;
# if selected vertices do not form a closed surface, any holes will be closed
# in order to have the correct volume, and the surface area of the new mesh
# includes the area of the extended surface
class Create_Closed_Submesh(bpy.types.Operator):
    """Create volume mesh as child of selected object"""
    bl_idname = "mesh.create_closed_submesh"
    bl_label = "create closed submesh"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        # construct open submesh for use in calculations
        (new_obj, new_name, obj_ptr, sel_inds, selected_verts, selected_faces) = create_submesh_code()
        if new_obj is not None:
            # create a new closed mesh object and link it to the scene
            close_and_add_mesh(new_obj, new_name, obj_ptr, sel_inds, selected_verts, selected_faces)

        return{'FINISHED'}


# this is a separate function so that it can also be called by Create_Whole_Surfaces()
def close_and_add_mesh(new_obj, new_name, obj_ptr, sel_inds, selected_verts, selected_faces):
      selected_verts2 = list(selected_verts)
      selected_faces2 = list(selected_faces)
      new_name2 = new_name + "_vol"
      mesh2 = bpy.data.meshes.new(new_name2)
      new_obj2 = bpy.data.objects.new(new_name2, mesh2)
      new_obj2.location = obj_ptr.location
      new_obj2.scale = obj_ptr.scale
      new_obj2.rotation_euler = obj_ptr.rotation_euler

    # volume calculation needs a closed mesh; edit object to close open end if it exists
    # by adding a point in the middle of an opening and adding faces connecting to that point
      bpy.ops.object.mode_set(mode='EDIT')
      bpy.ops.mesh.region_to_loop()
      bpy.ops.object.mode_set(mode='OBJECT')
      bdry_edges = [edge for edge in bpy.context.active_object.data.edges if edge.select]
      bdry_edges = remove_false_bdry_edges(bdry_edges)
      n_bdry_edges = len(bdry_edges)
      if n_bdry_edges > 0:
        bdry_edge_comps = get_connected_components(bdry_edges)
        ncomps = len(bdry_edge_comps)
        for c in range(0,ncomps):    # fill in each connected bdry separately
            es = bdry_edge_comps[c]  # list of edges
            nes = len(es)
            bdry_sum = [0,0,0]
            for n in range(0,nes):
                v0_ind = es[n].vertices[0]
                v1_ind = es[n].vertices[1]
                v0 = bpy.context.active_object.data.vertices[v0_ind].co
                v1 = bpy.context.active_object.data.vertices[v1_ind].co
                bdry_sum = [sum(pair) for pair in zip(bdry_sum, v0)]
                bdry_sum = [sum(pair) for pair in zip(bdry_sum, v1)]
            bdry_mean = [elt / (2*nes) for elt in bdry_sum]  # counted each vertex twice, so /2
            selected_verts2.append(mathutils.Vector(bdry_mean))
            last_ind = len(selected_verts2) - 1

            for f in range(0,nes):
                face_new_inds = [es[f].vertices[0], es[f].vertices[1], last_ind]   # will fix inconsistent normals below
                selected_faces2.append(face_new_inds)

      bpy.context.scene.objects.link(new_obj2)
      mesh2.from_pydata(selected_verts2, [], selected_faces2)
      mesh2.update(calc_edges=True)
    #new_obj2.location = obj_ptr.location

    # make new solid object the active object, and convert to triangles
      bpy.ops.object.mode_set(mode='OBJECT')
      bpy.context.scene.objects.active = new_obj2
      bpy.ops.object.mode_set(mode='EDIT')
      bpy.ops.mesh.quads_convert_to_tris()
      bpy.ops.object.mode_set(mode='OBJECT')
      bpy.ops.object.mode_set(mode='EDIT')

    # flip any normals that were assigned incorrectly:
    # search through all faces that contain vertex last_ind
    # if a normal is not consistent with the normal of the other face
    # containing the edge that was previously a boundary, flip it
      if n_bdry_edges > 0:
        n_orig = len(selected_faces)
        ind = n_orig
        bpy.ops.mesh.select_all(action='DESELECT')  # unselect everything in the scene
        sf2 = selected_faces2

        for c in range(ncomps):
            len_here = len(bdry_edge_comps[c])
            v_center = selected_verts2[c-ncomps]

            for f_ind in range(ind, ind+len_here):  # loop over new faces
                f = new_obj2.data.polygons[f_ind]
                v0_ind = bdry_edge_comps[c][f_ind-ind].vertices[0]
                v1_ind = bdry_edge_comps[c][f_ind-ind].vertices[1]
                v0 = new_obj2.data.vertices[v0_ind].co
                v1 = new_obj2.data.vertices[v1_ind].co

                # find neighboring face in original mesh
                f1_ind = [i for i in range(0,n_orig) if v0_ind in sf2[i] and v1_ind in sf2[i]]
                f1 = new_obj2.data.polygons[f1_ind[0]]
                verts_f1 = sf2[f1_ind[0]]
                v_out_ind = set(verts_f1) - set([v0_ind, v1_ind])
                v_out = new_obj2.data.vertices[list(v_out_ind)[0]].co

                # calculate the relative directions of the face normals
                edg = [coord[0]-coord[1] for coord in zip(v1, v0)]            # the shared edge
                seg0 = [coord[0]-coord[1] for coord in zip(v_center, v0)]     # shared pt to v_center
                seg1 = [coord[0]-coord[1] for coord in zip(v_out, v0)]        # shared pt to v_out
                n0 = f.normal
                n1 = f1.normal
                c0 = cross_product(seg0, edg)
                c1 = cross_product(edg, seg1)

                d0 = dot_product(n0, c0)
                d1 = dot_product(n1, c1)
                d = d0*d1

                if d < 0:  # this condition is correct
                    bpy.ops.object.mode_set(mode='OBJECT') # must be in object mode to update active vertices
                    f = new_obj2.data.polygons[f_ind]
                    for vert in f.vertices:
                        new_obj2.data.vertices[vert].select = True
                    bpy.ops.object.mode_set(mode='EDIT')
                    f = new_obj2.data.polygons[f_ind]
                    bpy.ops.mesh.flip_normals()
                    bpy.ops.object.mode_set(mode='OBJECT')  # necessary for the flip to take affect
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='DESELECT')

            ind = ind+len_here  # update for next bdry_edge_comp
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.mode_set(mode='EDIT')


    # make the new object a child of the original mesh
      bpy.ops.object.mode_set(mode='OBJECT')
      new_obj2.parent = obj_ptr
      bpy.context.scene.objects.active = new_obj2

    # remove open mesh object that was generated for interal use here
      bpy.context.scene.objects.unlink(new_obj)
      new_obj.user_clear()
      bpy.data.objects.remove(new_obj)

    # set flags
      new_obj2.is_open = 0
      new_obj2.has_vol = 1

    # enforce consistent normals
      sel_inds2 = [ind for ind in range(len(new_obj2.data.vertices[:]))]
      make_original_active(new_obj2, sel_inds2)
      bpy.ops.object.mode_set(mode='EDIT')
      bpy.ops.mesh.select_all(action='SELECT')
      bpy.ops.mesh.normals_make_consistent(inside=False)   
      bpy.ops.object.mode_set(mode='OBJECT')

    # return input object as active
      make_original_active(obj_ptr, sel_inds)

    # uncomment the following
      new_obj2.hide = True
    # doing anything here gives a context error



# call Create_Submesh, Create_Closed_Submesh and 
class Create_Both_Meshes(bpy.types.Operator):
    """Create both surface area and volume meshes as children of selected object"""
    bl_idname = "mesh.create_both_meshes"
    bl_label = "create both new meshes at once"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        Create_Submesh.execute(self, context)
        Create_Closed_Submesh.execute(self, context)
        return{'FINISHED'}


class Create_Whole_Surfaces(bpy.types.Operator):
    """Measure all selected objects (volume and surface area of whole surfaces)"""
    bl_idname = "mesh.create_whole_surfaces"
    bl_label = "create whole surfaces of selected objs (measure volumes and areas)"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        if bpy.context.object.mode == 'EDIT':  # if in edit mode, do nothing
           self.report({'INFO'},"Select multiple objects")
        else:

            if len(bpy.context.selected_objects)!=0:

              objlist = [item for item in bpy.context.selected_objects if item.parent==None and item.type=="MESH"]
              for obj in objlist:

                if bpy.ops.object.mode_set.poll():
                   bpy.ops.object.mode_set(mode='OBJECT')

                bpy.context.scene.objects.active = obj
                mt = bpy.context.active_object
                children=mt.children
                flag=0
                for child in children:
                   if child.name == mt.name+"_vol":
                     flag=1  # skip this object, operation already performed (won't catch _vol.001, etc)

                if flag==0:
                  if bpy.ops.object.mode_set.poll():
                     bpy.ops.object.mode_set(mode='EDIT')

                  bpy.ops.mesh.select_all(action='SELECT')

                  (new_obj, new_name, obj_ptr, sel_inds, selected_verts, selected_faces) = create_submesh_code()
                  close_and_add_mesh(new_obj, new_name, obj_ptr, sel_inds, selected_verts, selected_faces)

                  bpy.ops.object.mode_set(mode='OBJECT')
                  bpy.ops.object.select_all(action='DESELECT')
          
        return{'FINISHED'}


# adjust the scale of every object in the scene
class Adjust_scene_scale(bpy.types.Operator):
    """Rescale all objects in scene"""
    bl_idname = "mesh.adjust_scale"
    bl_label = "adjust scale"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')
        active_in = bpy.context.scene.objects.active
        bpy.ops.object.select_all(action='DESELECT')
        scl = bpy.context.scene.float_scale
        scale_vec = [scl, scl, scl]

        # temporarily undo parenting and make all objects visible,
        # necessary for some commands to function consistently
        parent_list = []
        visibility_list = []
        for this_obj in bpy.data.objects:
            visibility_list.append(this_obj.hide)
            if this_obj.hide:
                this_obj.hide = False
            
            parent_list.append(this_obj.parent)
            if this_obj.parent is not None:
                bpy.context.scene.objects.active = this_obj
                this_obj.select = True
                this_obj.parent = None
                bpy.ops.object.constraints_clear()
                bpy.ops.object.select_all(action='DESELECT')
            
        # loop through all objects in scene, rescale each
        for this_obj in bpy.data.objects:
            if hasattr(this_obj.data, 'vertices') or hasattr(this_obj.data, 'splines'):
                bpy.context.scene.objects.active = this_obj
                this_obj.select = True

                # the following rescales in reference to object's own geometric center,
                # so is inconsistent with parenting structure:
                # don't use if geometry should be kept alligned
                #bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

                # first scale according to the values currently in the object Transform; 
                # might not want this, in which case just comment out the following line
                bpy.ops.object.transform_apply(scale=True, location=False)

                # scale according to the input scale value
                this_obj.scale = scale_vec
                bpy.ops.object.transform_apply(scale=True, location=False)

                bpy.ops.object.select_all(action='DESELECT')

        # add back parenting structure and original visibility
        ind = 0
        for this_obj in bpy.data.objects:
            this_parent = parent_list[ind]
            if this_parent is not None:
                bpy.context.scene.objects.active = this_obj
                this_obj.select = True
                this_obj.parent = this_parent
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')

            this_obj.hide = visibility_list[ind]
            ind += 1            

        bpy.context.scene.objects.active = active_in
        active_in.select = True
        return{'FINISHED'}



# remesh the selected object based on predefined values and the user-defined octree depth
# the rest of the input parameters agree with the Blender default (can modify here)
class Remesh_Object(bpy.types.Operator):
    bl_idname = "mesh.remesh"
    bl_label = "remesh active object"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')
        obj = context.object
        bpy.ops.object.modifier_add(type='REMESH')
        obj.modifiers["Remesh"].name = 'this_remesh'
        obj.modifiers["this_remesh"].mode = 'SHARP'
        obj.modifiers["this_remesh"].octree_depth = bpy.context.scene.remesh_octree_depth
        obj.modifiers["this_remesh"].scale = .9
        obj.modifiers["this_remesh"].sharpness = 1.0
        obj.modifiers["this_remesh"].threshold = 1.0
        bpy.ops.object.modifier_apply(modifier='this_remesh')
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}



# output data for each object in the scene (for each object that has a mesh or splines)
# entries are separated by commas, can be imported into Microsoft Excel

class WriteData(bpy.types.Operator):
    """Write external file containing all measurements in the scene"""
    bl_idname = "file.write_data"
    bl_label = "Write data file"

    directory = bpy.props.StringProperty(subtype="FILE_PATH")
    filename = bpy.props.StringProperty(subtype="FILE_NAME")

    def execute(self, context):
        directory = self.directory
        filename = self.filename
        fname = filename + '.csv'
        the_name=os.path.join(directory,fname)
        f = open(the_name, 'w')
        f.write('Object Name,Parent,Surface Area,Volume,Number of Vertices,Length\n\n')

        for obj in bpy.data.objects:
            write_obj_info(obj, f)
        f.close()

        return {'FINISHED'}

    def invoke(self, context, event):
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        #bpy.ops.buttons.file_browse
        return {"RUNNING_MODAL"}


# output data for each selected object in the scene and their children
class Write_Selected_Data(bpy.types.Operator):
    """Write external file containing measurements of the selected objects"""
    bl_idname = "mesh.write_selected_data"
    bl_label = "Write data file"

    directory = bpy.props.StringProperty(subtype="FILE_PATH")
    filename = bpy.props.StringProperty(subtype="FILE_NAME")
    
    def execute(self, context):
        to_write = set()
        for obj in bpy.data.objects:
            if obj.select:
                add_obj_and_children_to_set(obj, to_write)

        directory = self.directory
        filename = self.filename
        fname = filename + '.csv'
        the_name=os.path.join(directory,fname)
        f = open(the_name, 'w')
        f.write('Object Name,Parent,Surface Area,Volume,Number of Vertices,Length\n\n')

        for obj in to_write:
            write_obj_info(obj, f)
        f.close()
        return{'FINISHED'}

    def invoke(self, context, event):
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}


def add_obj_and_children_to_set(obj, to_write):  # recursive
    to_write.add(obj)
    if obj.children != ():
        for child in obj.children:
            add_obj_and_children_to_set(child, to_write)


# called by Write_Data and Write_Selected_Data
def write_obj_info(obj, f):
    if hasattr(obj.data, 'vertices'):  # mesh objects
        f.write(obj.name + ',')
        if obj.parent is None:
            f.write('none ,')
        else:
            f.write(str(obj.parent.name) + ',')
        if isinstance(obj.SA, str):
            f.write(' ,')
        else:
            f.write(str(obj.SA) + ',')
        if isinstance(obj.vol, str):
            f.write(' ,')
        else:
            f.write(str(obj.vol) + ',')
        f.write(str(obj.nverts) + ',')
        if obj.curvelength != "property not available":
        	f.write(str(obj.curvelength) + ' \n')
        else:
        	f.write(' \n')
    return



# create a button on the left that executes Create_new_obj when clicked
class MeasurementToolsPanel(bpy.types.Panel):
    bl_label = "Measurement Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "NeuroMorph"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        obj = context.object

        if hasattr(obj, 'data'):
            split = layout.row().split(percentage=0.5)
            col1 = split.column()
            col2 = split.column()
            col1.operator("mesh.create_submesh", text = "Surface Area")
            col2.operator("mesh.create_closed_submesh", text = "Volume")
            row = layout.row()
            split = layout.row().split(percentage=0.5)
            col1 = split.column()
            col2 = split.column()
            col1.operator("mesh.create_both_meshes", text = "Both")
            col2.operator("mesh.create_whole_surfaces", text='Multi Object')

            layout.label("-----Lengths-----")
            layout.prop(context.scene , "create_length_obj")
            len_str = "Last calculated length:   " + str(round(bpy.context.scene.last_len, 6))
            self.layout.label(len_str)
            layout.operator("object.length_in_space", text = "Distance Between 2 Points", icon="FORWARD")
            layout.operator("object.length_on_mesh", text = "Shortest Distance on Mesh", icon="CURVE_NCURVE")
            layout.operator("object.length_edges", text="Length of Selected Edges", icon="MESH_DATA")
            

            ## multi-segment distance
            # split = layout.row().split(percentage=0.5)
            # colL = split.column()
            # colR = split.column()
            # colL.operator("get.vert", text = "Add Point")
            # colR.operator("clear.vert", text = "Clear Points")
            # #layout.template_list(obj.data, "vertex_collection", obj.data, "vertex_collection_index", \
            # #                      prop_list = "template_list_controls", rows = 3)  # for Blender <=2.65
            # layout.template_list('UI_UL_list', 'vertex_collection_id', obj, "vertex_collection", \
            #                      obj, "vertex_collection_index", rows = 3)
            

        layout.label("-----Scale-----")
        split = layout.row().split(percentage=0.5)
        colL = split.column()
        colR = split.column()
        colL.prop(scn, 'float_scale')
        colR.operator("mesh.adjust_scale", text = "Apply Scale")

        layout.label("-----Output Data-----")
        # row = layout.row()
        layout.operator("file.write_data", text='Export Measurements', icon='FILESEL')
        # row = layout.row()
        layout.operator("mesh.write_selected_data", text = "Export Selected", icon='FILESEL')



def register():
    bpy.utils.register_module(__name__)

    # define new properties
    bpy.types.Scene.float_scale = FloatProperty(name = "scale", default = 1.0, min = 10**-20)
    bpy.types.Scene.remesh_octree_depth = IntProperty(name = "import octree depth", default = 7)
    bpy.types.Object.string_name = StringProperty(name = "obj name", default="submesh")
    # bpy.types.Object.string_name = StringProperty(name = "obj name", default="submesh", get=get_name, set=set_name)
    bpy.types.Object.SA = property(fget_SA, fset_SA)
    bpy.types.Object.vol = property(fget_vol, fset_vol)
    bpy.types.Object.nverts = property(fget_nverts, fset_nverts)
    bpy.types.Object.curvelength = property(fget_curvelength, fset_curvelength)
    bpy.types.Object.length = FloatProperty(name = "length", default = -1.0)
    
    
    bpy.types.Object.is_open = BoolProperty(name="is_open", default=0)
    bpy.types.Object.has_vol = BoolProperty(name="has_vol", default=0)
    # bpy.types.Object.vertex_collection = CollectionProperty(type=VertexListItem)
    # bpy.types.Object.vertex_collection_index = IntProperty(min= -1,default= -1)

    # handle the keymap
    # km = bpy.context.window_manager.keyconfigs.active.keymaps['3D View']
    # kmi = km.keymap_items.new(GetVertex.bl_idname, 'S', 'PRESS', ctrl=True)

    # Lengths 2.0
    bpy.types.Scene.last_len = bpy.props.FloatProperty(name = "length", default = 0.0, \
                        description = "Last calculated length")
    bpy.types.Scene.create_length_obj = bpy.props.BoolProperty(name = "Create Length Object", default = True, \
                        description = "Create new mesh curve object from points used in length calculation")



def unregister():
    bpy.utils.unregister_module(__name__)

    del bpy.types.Scene.create_length_obj
    del bpy.types.Scene.last_len
    # del bpy.types.Object.vertex_collection
    # del bpy.types.Object.vertex_collection_index
    del bpy.types.Object.has_vol
    del bpy.types.Object.is_open
    del bpy.types.Object.length
    del bpy.types.Object.curvelength
    del bpy.types.Object.nverts
    del bpy.types.Object.vol
    del bpy.types.Object.SA
    del bpy.types.Object.string_name
    del bpy.types.Scene.remesh_octree_depth
    del bpy.types.Scene.float_scale
    

if __name__ == "__main__":
    register()
