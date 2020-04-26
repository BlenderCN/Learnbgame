#==================================
# TODO
#==================================
# Position based on the tools menue toggle 
# 

import bpy, imp, bmesh, blf, bgl

from . import draw_call
from . import operator
from . import properties
from . import tools
  
bl_info = { 
    "name": "Polygon Count Display", 
    "author": "Anomalous Underdog", 
    "version": (0, 0, 1), 
    "blender": (2, 6, 3), 
    "location": "View3D > Properties panel > Poly Count Display", 
    "description": "Shows how many triangles your 3d model would have if its faces were all converted to triangles.", 
    "category": "3D View"
}

#from polycountDisplay import *

class PolyCountPanel(bpy.types.Panel): 
    bl_label = "Poly Count Display"
    bl_idname = "OBJECT_PT_poly_count"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
  
    def draw(self, context): 
        sc = context.scene 
        wm = context.window_manager  
        layout = self.layout 
  
        if not wm.polycount_run: 
            layout.operator("view3d.polycount", text="Start display", 
                icon='PLAY') 
        else: 
            layout.operator("view3d.polycount", text="Stop display", 
                icon='PAUSE') 
  
        col = layout.column(align=True)
        row = col.row(align=True) 
        row.prop(sc, "polycount_pos_x") 
        row.prop(sc, "polycount_pos_y") 
        row = col.row(align=True) 
        row.prop(sc, "polycount_font_size") 
        row.prop(sc, "polycount_font_color", text = "")
        
        col.separator()
        col.label(text="        all     obj    sel")
        
        row = col.row()        
        row.prop(sc, "show_vertex_count", text="", icon='VERTEXSEL')
        row.prop(sc, "vert_count_all", text = "")
        row.prop(sc, "vert_count_obj", text = "")
        row.prop(sc, "vert_count_sel", text = "")
        
        row = col.row()
        row.prop(sc, "show_edge_count", text="", icon='EDGESEL')
        row.prop(sc, "edge_count_all", text = "")
        row.prop(sc, "edge_count_obj", text = "")
        row.prop(sc, "edge_count_sel", text = "")
        
                          
        row = col.row()
        row.prop(sc, "show_face_count", text="", icon='FACESEL')
        row.prop(sc, "face_count_all", text = "")
        row.prop(sc, "face_count_obj", text = "")
        row.prop(sc, "face_count_sel", text = "")
        
        row = col.row()
        row.prop(sc, "show_triangle_count", text="", icon='EDITMODE_VEC_HLT')
        row.prop(sc, "tri_count_all", text = "")
        row.prop(sc, "tri_count_obj", text = "")
        row.prop(sc, "tri_count_sel", text = "")

def register():
    bpy.utils.register_class(PolyCountPanel)
    bpy.utils.register_module(draw_call)
    bpy.utils.register_module(operator)
    bpy.utils.register_module(properties)
    bpy.utils.register_module(tools)

def unregister():
    bpy.utils.unregister_class(PolyCountPanel)
    bpy.utils.unregister_module(tools)
    bpy.utils.unregister_module(properties)
    bpy.utils.unregister_module(operator)
    bpy.utils.unregister_module(draw_call)
        
if __name__ == "__main__":
    register()
        