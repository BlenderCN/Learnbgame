import bpy
from bpy import context

# creates a menu for edit mode tools         
class QuickMeshTools(bpy.types.Menu):
    bl_label = "Quick Mesh Tools"
    bl_idname = "mesh.tools_menu"
       
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        
        layout.operator("gpencil.surfsk_add_surface", 'Add BSurface', icon='OUTLINER_OB_SURFACE')
        layout.operator("mesh.bridge_edge_loops")
                
        layout.separator()
        
        layout.operator("mesh.bevel")
        layout.operator("mesh.inset").use_boundary=False
        layout.operator("mesh.subdivide")
        
        layout.separator()
        
        layout.operator("mesh.knife_tool", icon='SCULPTMODE_HLT')
        layout.operator("mesh.vert_connect")
        
        layout.separator()
        
        layout.operator("mesh.vertices_smooth")    
        
        layout.separator()

        layout.operator("mesh.set_object_origin", "Origin to Selection")

        layout.operator("object.mesh_halve", "Halve mesh")

        layout.separator()
        
        layout.operator("object.add_mirror", icon='MOD_MIRROR')  
        layout.operator("object.add_subsurf", 'Add Subsurf', icon='MOD_SUBSURF')


### ------------ New hotkeys and registration ------------ ###

def register():
    #register the new menus
    bpy.utils.register_class(QuickMeshTools)

def unregister():
    #unregister the new menus
    bpy.utils.unregister_class(QuickMeshTools)
        

if __name__ == "__main__":
    register()