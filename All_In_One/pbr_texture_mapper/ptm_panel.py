import bpy
from bpy.types import Panel

from . ptm_mapping_op   import PTM_MappingOperator

# Add this when icon_value works again in Blender 2.8
# from . ptm_icon_manager import PTM_IconMgr

class PTM_Panel(Panel):
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_label = "PTM"
    bl_category = "PTM"
    
    def draw(self, context):
        
        layout = self.layout
        scene = context.scene      
                            
        # Mapping operator
        row = layout.row()
        row.operator('object.ptm_mapping_op', text="Map textures", icon="NODE")
        
        layout.row().separator()
        
        # Alignment (4 columns)
        row = layout.row()
        split = row.split(factor=0.2)
        
        col = split.column()
        col.operator('object.ptm_align_op', text="←", icon="NODE").align = 0
        
        col = split.column()
        col.operator('object.ptm_align_op', text="→", icon="NODE").align = 1
        
        col = split.column()
        col.operator('object.ptm_align_op', text="↑", icon="NODE").align = 2
        
        col = split.column()
        col.operator('object.ptm_align_op', text="↓", icon="NODE").align = 3
        
        col = split.column()
        col.operator('object.ptm_align_op', text="↔", icon="NODE").align = 4
 