import bpy, bmesh

# error exception if object not in edit mode..

class Polycount:
    
    ###### VERTICES
    def vert_obj(object):
        return len(self.object.data.vertices)

    def vert_edit(object):
        bm = bmesh.from_edit_mesh(object.data)
        all_verts = len ( [i for i in bm.verts] )
        sel_verts = len ( [i for i in bm.verts if i.select] )        
        return all_verts, sel_verts

    ##### FACES
    def edge_obj(object):
        return len(obj.data.edges)
    
    def edge_edit(object):
        bm = bmesh.from_edit_mesh(object.data)
        all_edges = len( [i for i in bm.edges] )
        sel_edges = len( [i for i in bm.edges if i.select] )
        return all_edges, sel_edges
     
    #### FACES
    
    def face_obj(object):
        return len(obj.data.polygons)
    
    def face_edit(object):
        bm = bmesh.from_edit_mesh(object.data)
        all_faces = len ( [i for i in bm.faces] )
        sel_faces = len ( [i for i in bm.faces if i.select] )
        return all_faces, sel_faces
    
    ##### TRIANGLES
    def tri_obj(object): 
        tri_count = sum ( [ ( len(i.vertices) -2 ) for i in obj.data.polygons] )
        return tri_count
    
    def tri_edit(object):
        bm = bmesh.from_edit_mesh(object.data)
        sel_faces = [face for face in bm.faces if face.select] 
        sel_tris =  sum( [ len(sel_faces[i].verts)-2 for i in range(0,len(sel_faces)) ] )
        return all_tris, sel_tris