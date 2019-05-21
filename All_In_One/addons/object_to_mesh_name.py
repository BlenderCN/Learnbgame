bl_info = {
    "name": "Object to mesh name",
    "category": "Object",
    "blender": (2, 80, 0),
}



import bpy

class ObjectToMeshName(bpy.types.Operator):
    """Object to mesh name"""      
    bl_idname = "object.objecttomeshname"        
    bl_label = "Object to mesh name"         
    bl_options = {'REGISTER', 'UNDO'}  

    def execute(self, context):        

        scene = context.scene
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':            
                obj.data.name = obj.name    
                  
        return {'FINISHED'}            


class CopyMenu(bpy.types.Menu):
    bl_label = "Copy"
    bl_idname = "OBJECT_MT_copyname_menu"

    def draw(self, context):
        layout = self.layout

        layout.operator("object.objecttomeshname", "", icon="PASTEDOWN") 
        #layout.operator("object.meshnametobject", "", icon="PASTEUP") 


def draw_item(self, context):
    layout = self.layout
    layout.menu("OBJECT_MT_copyname_menu")


        
def register():
    bpy.utils.register_module(__name__)
    
    bpy.types.OUTLINER_HT_header.prepend(draw_item)
          
def unregister():
    bpy.utils.unregister_module(__name__)
    
    bpy.types.OUTLINER_HT_header.remove(draw_item)
    
if __name__ == "__main__":
    register()