import bpy

class Sprycle(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Tools"
    bl_label = "Sprycle"
    
    @classmethod    
    def poll(self, context):
        return True

    def draw(self, context):
        layout = self.layout
        
        r = layout.row

        r().operator("object.scale_plane_to_uv", text="Scale to UV")
        

def register():
    bpy.utils.register_class(Sprycle)
    
def unregister():
    bpy.utils.unregister_class(Sprycle)


if __name__ == "__main__":
    register()
