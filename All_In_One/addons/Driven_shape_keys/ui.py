import bpy


help_string = \
    '''

    '''


class DrivenShapes(bpy.types.Panel):
    bl_idname = "driven_shapes"
    bl_label = "Driven Shapes"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Shapes"
    
    def draw(self, context):
        layout = self.layout
        
        bone = None
        # Check if a bone is selected
        if context.active_pose_bone:
            bone = context.active_pose_bone
        mesh = None
        
        # If two objects are selected one of these may be a mesh object
        if len(context.selected_objects) == 2:
            mesh = [ob for ob in context.selected_objects if ob.type == "MESH"]
            if mesh:
                mesh = mesh[0]
        # If not just check if the active object is a mesh
        else:
            if context.active_object.type == "MESH":
                mesh = context.active_object
        
        # If find a mesh.
        # Draw its shape key list
        if mesh:
            layout.label("Shape Keys")
            shapes = mesh.data.shape_keys
            row = layout.row()
            row.template_list("MESH_UL_shape_keys", "", shapes, "key_blocks", mesh, "active_shape_key_index", rows = 5)
            
            # If only the mesh is selected draw some special operators for shape the keys
            if not bone:
                col = row.column()
                col.operator("object.shape_key_add", icon = 'ZOOMIN', text = "").from_mix = False
                col.operator("object.shape_key_remove", icon = 'ZOOMOUT', text = "")
                col.separator()
                col.menu("MESH_MT_shape_key_specials", icon = 'DOWNARROW_HLT', text = "")
                col.separator()
                col.operator("object.shape_key_move", "", icon = "TRIA_UP").type = "UP"
                col.operator("object.shape_key_move", "", icon = "TRIA_DOWN").type = "DOWN"
        
        # Finally draw the addon operators
        if bone and mesh:
            col = layout.column(align = True)
            col.operator("driven.splitshapes", "Splt active shape key")
            col.label("")
            
            col.label("Drivers")
            col.operator("driven.add_driver_to_shape_key", "Add driver to active shape key")
            row = col.row(align = True)
            row.operator("driven.add_driver_to_shape_key", "To X").axis = "LOC_X"
            row.operator("driven.add_driver_to_shape_key", "To Y").axis = "LOC_Y"
            row.operator("driven.add_driver_to_shape_key", "To Z").axis = "LOC_Z"
            col.separator()
            
            col.operator("driven.remove_driver_from_shape_key")
