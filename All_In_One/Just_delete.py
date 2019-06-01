bl_info = {
    "name": "Just Delete",
    "author": "Sergey Golubev",
    "version": (0, 1),
    "blender": (2, 80, 0),
    "location": "In delete menus of objects and components. Next to the usual delete button.",
    "description": "Delete objects or components based on selection mode.",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
}

### MAIN PART OF ADDON STARTS HERE

import bpy

def is_updated(cur_sel):
        bpy.context.active_object.update_from_editmode()
        if cur_sel == len([v for v in bpy.context.active_object.data.vertices if v.select]):
            return False
        else:
            return True
        
        
def just_delete():   # check what is selected and start the corresponding function
    bpy.context.active_object.update_from_editmode()
    
    cur_sel = len([v for v in bpy.context.active_object.data.vertices if v.select])
    select_mode = bpy.context.object.mode
    
    if select_mode == "OBJECT":
        bpy.ops.object.delete(use_global=False) 
        
    if select_mode == "EDIT":
        if bpy.context.edit_object.type == 'MESH':      # if mesh is selected

            sel_mode = bpy.context.tool_settings.mesh_select_mode[:] # define active selection modes
    
            if sel_mode[2] == True:                     # if polygon selection mode is on
                bpy.ops.mesh.delete(type='FACE')

            if sel_mode[1] == True:                     # if edge selection mode is on
                bpy.ops.mesh.dissolve_edges()
                bpy.ops.mesh.delete(type='EDGE')
                if is_updated(cur_sel) :
                    bpy.ops.mesh.select_all(action='DESELECT')
                    return

            if sel_mode[0] == True:                     # if vertex selection mode is on
                bpy.ops.mesh.dissolve_verts()
                bpy.ops.mesh.delete(type='VERT')

### MAIN PART OF ADDON ENDS HERE


### ADDON AND INTERFACE PART STARTS HERE

class OBJECT_OT_smart_delete(bpy.types.Operator):
    """Delete objects or components based on selection mode"""
    bl_label = "Just Delete"
    bl_idname = "mesh.just_delete"
    bp_options = {'REGISTER' , "UNDO"}
    
    def execute(self, context):
        
        just_delete()
        
        return {'FINISHED'}


def smart_delete_button_components(self , context): # add separator button in components delete menu
    self.layout.separator()
    self.layout.operator(
            OBJECT_OT_smart_delete.bl_idname
            )

def smart_delete_button_objects(self , context): # add separator button in object delete menu
    self.layout.separator()
    self.layout.operator(
            OBJECT_OT_smart_delete.bl_idname
            )


# Registration

def register():
    bpy.utils.register_class(OBJECT_OT_smart_delete)
    bpy.types.VIEW3D_MT_edit_mesh_delete.append(smart_delete_button_components)
    bpy.types.VIEW3D_MT_object.append(smart_delete_button_objects)




def unregister():
    bpy.utils.unregister_class(OBJECT_OT_smart_delete)
    bpy.types.VIEW3D_MT_edit_mesh_delete.remove(smart_delete_button_components)
    bpy.types.VIEW3D_MT_object.remove(smart_delete_button_objects)



if __name__ == "__main__":
    register()


### ADDON AND INTERFACE PART ENDS HERE
