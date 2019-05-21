import bpy
import bmesh

# CREATE NEW
class MaskToVertexGroup(bpy.types.Operator):
    '''Mask To Vertex Group'''
    bl_idname = "mesh.masktovgroup"
    bl_label = "Mask To Vertex Group"
    bl_options = {'REGISTER'}

    @classmethod

    def poll(cls, context):

        return context.active_object is not None and context.active_object.mode == 'SCULPT'

    def execute(self, context):

        dynatopoEnabled = False

        if context.active_object.mode == 'SCULPT' :

           if context.sculpt_object.use_dynamic_topology_sculpting :

               dynatopoEnabled = True

               bpy.ops.sculpt.dynamic_topology_toggle()

           #print(context.active_object.use_dynamic_topology_sculpting)

           bmeshContainer = bmesh.new() # New bmesh container

           bmeshContainer.from_mesh(context.sculpt_object.data) # Fill container with our object

           mask = bmeshContainer.verts.layers.paint_mask.verify() # Set the active mask layer as custom layer

           newVertexGroup = context.sculpt_object.vertex_groups.new(name = "Mask") # Create an empty vgroup

           bmeshContainer.verts.ensure_lookup_table() # Just incase > Remove if unneccessary

           for x in bmeshContainer.verts:  # itterate from bmesh.verts

               if x[mask] > 0 : # if x BMVert has mask weight

                   maskWeight = x[mask] # assign float variable for weight from mask layer

                   newVertexGroup.add([x.index], maskWeight, "REPLACE") # add it to vgroup, set mask weight
               else :

                   newVertexGroup.add([x.index], 0, "REPLACE")

           bmeshContainer.free()

           if dynatopoEnabled :

               bpy.ops.sculpt.dynamic_topology_toggle()

               #print("Mask Converted to Vertex Group")

        return {'FINISHED'}


# APPEND
class MaskToVertexGroupAppend(bpy.types.Operator):
    '''Append Mask To Vertex Group'''
    bl_idname = "mesh.masktovgroup_append"
    bl_label = "Append Mask To Vertex Group"
    bl_options = {'REGISTER'}

    @classmethod

    def poll(cls, context):

        return context.active_object is not None and context.active_object.mode == 'SCULPT'

    def execute(self, context):

        dynatopoEnabled = False

        if context.active_object.mode == 'SCULPT'and context.active_object.vertex_groups.active is not None :

            vGroupLocked = context.sculpt_object.vertex_groups.active.lock_weight

            if vGroupLocked == False :

               if context.sculpt_object.use_dynamic_topology_sculpting :

                    dynatopoEnabled = True

                    bpy.ops.sculpt.dynamic_topology_toggle()

               bmeshContainer = bmesh.new() # New bmesh container

               bmeshContainer.from_mesh(context.sculpt_object.data) # Fill container with our object

               activeVertexGroup = context.sculpt_object.vertex_groups.active  # Set active vgroup

               mask = bmeshContainer.verts.layers.paint_mask.verify() # Set the active mask layer as custom layer

               bmeshContainer.verts.ensure_lookup_table() # Just incase > Remove if unneccessary

               for x in bmeshContainer.verts:  # itterate from bmesh.verts

                   if x[mask] > 0 : # if x BMVERT has mask weight

                       maskWeight = x[mask] # assign float variable for weight from mask layer

                       activeVertexGroup.add([x.index],maskWeight,"ADD") # add it to vgroup, set mask weight

               bmeshContainer.free()

               if dynatopoEnabled :

                   bpy.ops.sculpt.dynamic_topology_toggle()

                   #print("Mask Added to Vertex Group")

        return {'FINISHED'}

# REMOVE
class MaskToVertexGroupRemove(bpy.types.Operator):
    '''Remove Mask From Vertex Group'''
    bl_idname = "mesh.masktovgroup_remove"
    bl_label = "Remove Mask From Vertex Group"
    bl_options = {'REGISTER'}

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

               bmeshContainer.from_mesh(context.sculpt_object.data) # Fill container with our object

               activeVertexGroup = context.sculpt_object.vertex_groups.active  # Set active vgroup

               mask = bmeshContainer.verts.layers.paint_mask.verify() # Set the active mask layer as custom layer

               bmeshContainer.verts.ensure_lookup_table() # Just incase > Remove if unneccessary

               for x in bmeshContainer.verts:  # itterate from bmesh.verts

                   if x[mask] > 0 : # if x BMVert has mask weight

                       maskWeight = x[mask] # assign float variable for weight from mask layer

                       activeVertexGroup.add([x.index], maskWeight,"SUBTRACT") # add it to vgroup, set mask weight


               bmeshContainer.free()

               if dynatopoEnabled :

                   bpy.ops.sculpt.dynamic_topology_toggle()

                    #print("Mask Removed from Vertex Group")

        return {'FINISHED'}

#
# def register():
#     bpy.utils.register_module(__name__)
#
#
#
# def unregister():
#     bpy.utils.unregister_module(__name__)
#
#
# if __name__ == "__main__":
#     register()
#
#
