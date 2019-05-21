import bpy
import bmesh

# CREATE NEW
class VertexGroupToMask(bpy.types.Operator):
    '''Vertex Group To Mask'''
    bl_idname = "mesh.vgrouptomask"
    bl_label = "Vertex Group To Mask"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod

    def poll(cls, context):

        return context.active_object is not None and context.active_object.mode == 'SCULPT'

    def execute(self, context):

        dynatopoEnabled = False

        if context.active_object.mode == 'SCULPT'and context.active_object.vertex_groups.active is not None :

            vGroupLocked = context.active_object.vertex_groups.active.lock_weight

            if vGroupLocked == False :

               if context.sculpt_object.use_dynamic_topology_sculpting :

                  dynatopoEnabled = True

                  bpy.ops.sculpt.dynamic_topology_toggle()

               bmeshContainer = bmesh.new() # New bmesh container

               bmeshContainer.from_mesh(context.active_object.data) # Fill container with our object

               activeVertexGroup = context.active_object.vertex_groups.active  # Set active vgroup

               mask = bmeshContainer.verts.layers.paint_mask.verify() # get active mask layer

               bmeshContainer.verts.ensure_lookup_table() # Update vertex lookup table

               for x in context.active_object.data.vertices: # For each x vert

                   bmeshContainer.verts[x.index] [mask] = 0.0 # Set mask to 0 weight

                   if len(x.groups) > 0: # if vert is a member of a vgroup

                    for y in x.groups: # For each y vgroup in group list

                       if y.group == activeVertexGroup.index: # if y is active group x belongs to

                          if activeVertexGroup.weight(x.index) > 0 :  # and x vert weight is not zero

                             currVert = bmeshContainer.verts[x.index]  # current vert is x bmesh vert

                             maskWeight = activeVertexGroup.weight(x.index) # set weight from active vgroup

                             currVert[mask] = maskWeight # assign weight to custom data layer


               bmeshContainer.to_mesh(context.active_object.data) # Fill obj data with bmesh data

               bmeshContainer.free() # Release bmesh

               if dynatopoEnabled :

                   bpy.ops.sculpt.dynamic_topology_toggle()

        return {'FINISHED'}

# APPEND
class VertexGroupToMaskAppend(bpy.types.Operator):
    '''Append Vertex Group To Mask'''
    bl_idname = "mesh.vgrouptomask_append"
    bl_label = "Append Vertex Group To Mask"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod

    def poll(cls, context):

        return context.active_object is not None and context.active_object.mode == 'SCULPT'

    def execute(self, context):

        dynatopoEnabled = False

        if context.active_object.mode == 'SCULPT'and context.active_object.vertex_groups.active is not None :

            vGroupLocked = context.active_object.vertex_groups.active.lock_weight

            if vGroupLocked == False :

               if context.sculpt_object.use_dynamic_topology_sculpting :

                    dynatopoEnabled = True

                    bpy.ops.sculpt.dynamic_topology_toggle()

               bmeshContainer = bmesh.new() # New bmesh container

               bmeshContainer.from_mesh(context.active_object.data) # Fill container with our object

               activeVertexGroup = context.active_object.vertex_groups.active  # Set active vgroup

               mask = bmeshContainer.verts.layers.paint_mask.verify() # get active mask layer

               bmeshContainer.verts.ensure_lookup_table() # Update vertex lookup table

               for x in context.active_object.data.vertices: # For each x vert

                   if len(x.groups) > 0: # if vert is a member of a vgroup

                    for y in x.groups: # For each y vgroup in group list

                       if y.group == activeVertexGroup.index: # if y is active group x belongs to

                           if activeVertexGroup.weight(x.index) > 0 :  # and x vert weight is not zero

                             currVert = bmeshContainer.verts[x.index]  # current vert is x bmesh vert

                             maskWeight = activeVertexGroup.weight(x.index) # set weight from active vgroup

                             currVert[mask] = (maskWeight + currVert[mask]) # add current mask weight to maskweight and assign
                             if currVert[mask] > 1.0 : # is current mask weight greater than 0-1 range

                                 currVert[mask] = 1.0 # then Normalize mask weight


               bmeshContainer.to_mesh(context.active_object.data) # Fill obj data with bmesh data

               bmeshContainer.free() # Release bmesh

               if dynatopoEnabled :

                   bpy.ops.sculpt.dynamic_topology_toggle()

        return {'FINISHED'}

#REMOVE
class VertexGroupToMaskRemove(bpy.types.Operator):
    '''Remove Vertex Group From Mask'''
    bl_idname = "mesh.vgrouptomask_remove"
    bl_label = "Remove Vertex Group From Mask"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod

    def poll(cls, context):

        return context.active_object is not None and context.active_object.mode == 'SCULPT'

    def execute(self, context):

        dynatopoEnabled = False

        if context.active_object.mode == 'SCULPT'and context.active_object.vertex_groups.active is not None :

            vGroupLocked = context.active_object.vertex_groups.active.lock_weight

            if vGroupLocked == False :

               if context.sculpt_object.use_dynamic_topology_sculpting :

                    dynatopoEnabled = True

                    bpy.ops.sculpt.dynamic_topology_toggle()

               bmeshContainer = bmesh.new() # New bmesh container

               bmeshContainer.from_mesh(context.active_object.data) # Fill container with our object

               activeVertexGroup = context.active_object.vertex_groups.active  # Set active vgroup

               mask = bmeshContainer.verts.layers.paint_mask.verify()  # get active mask layer

               bmeshContainer.verts.ensure_lookup_table() # Update vertex lookup table

               for x in context.active_object.data.vertices: # For each x vert

                   if len(x.groups) > 0: # if vert is a member of a vgroup

                    for y in x.groups: # For each y vgroup in group list

                       if y.group == activeVertexGroup.index: # if y is active group x belongs to

                           if activeVertexGroup.weight(x.index) > 0 :  # and x vert weight is not zero

                             currVert = bmeshContainer.verts[x.index]  # current vert is x bmesh vert

                             maskWeight = activeVertexGroup.weight(x.index) # set weight from active vgroup

                             currVert[mask] -= (maskWeight * currVert[mask]) # multiply current mask with maskweight and subtract
                             if currVert[mask] < 0 : # is current mask weight less than 0

                                 currVert[mask] = 0 # then Normalize mask weight


               bmeshContainer.to_mesh(context.active_object.data) # Fill obj data with bmesh data

               bmeshContainer.free() # Release bmesh

               if dynatopoEnabled :

                   bpy.ops.sculpt.dynamic_topology_toggle()

        return {'FINISHED'}

#
# def register():
# 	bpy.utils.register_module(__name__)
#
#
#
# def unregister():
# 	bpy.utils.unregister_module(__name__)
#
#
# if __name__ == "__main__":
#     register()
#
#
#
