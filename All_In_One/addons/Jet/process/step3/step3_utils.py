import bmesh

def EnableAndConfigAutosmooth(obj, value=3.14159):
    if obj is None or obj.type != "MESH":
        return None
    obj.data.use_auto_smooth = True
    obj.data.auto_smooth_angle = value    # 180 degrees (pi radians)


def ManageSharp(context, mark=True):
    obj = context.active_object
    if obj is None or \
       obj.type != "MESH" or \
       obj.mode != 'EDIT':
        return None

    me = obj.data
    me.show_edge_sharp = True
    bm = bmesh.from_edit_mesh(me)  # Save the mesh of the object in the variable to work with it by code
    bm.edges.ensure_lookup_table()  # It's advisable calling this method in order to work with the different components of an object (verts, edges or faces) using bmesh
    for e in bm.edges:
        if e.select:  # If the edge is selected
            e.smooth = not mark  # Set edge as Seam
    bmesh.update_edit_mesh(me, False)

