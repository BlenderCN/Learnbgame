bl_info = {
        "name": "QuadView Menu",
        "category": "3D View",
        "author": "Jesse Doyle Form Affinity"
        }

import bpy
from bpy.types import Menu



class Pie_menu(Menu):
    bl_label = "Quad Menu"
    bl_idname = "view3D.Quad_menu"
    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("view3d.view_axis", text="Left", icon='VIEW_ORTHO').type = 'LEFT'
        pie.operator("view3d.view_axis", text="Right", icon='VIEW_ORTHO').type = 'RIGHT'
        pie.operator("view3d.view_axis", text="Bottom", icon='VIEW_ORTHO').type = 'BOTTOM'
        pie.operator("view3d.view_axis", text="Top", icon='VIEW_ORTHO').type = 'TOP'
        pie.operator("view3d.view_axis", text="Front", icon='VIEW_ORTHO').type = 'FRONT'
        pie.operator("view3d.view_axis", text="Back", icon='VIEW_ORTHO').type = 'BACK'
        pie.operator("view3d.view_persportho", text = "Persp/Ortho", icon ="ARROW_LEFTRIGHT")
        pie.operator("screen.region_quadview", text="QuadView", icon='VIEW_PERSPECTIVE')
        pie.separator()
        pie.separator()
        other = pie.column()
        gap = other.column()
        gap.separator()
        gap.scale_y = 7
        other_menu = other.box().column()
        other_menu.scale_y=1.3
        other_menu.operator("view3d.view_camera", text="Active Cam", icon='CAMERA_DATA')
        other_menu.operator("view3d.camera_to_view", text = "Cam To View", icon ="VIEW_CAMERA")
        other_menu.operator("screen.screen_full_area", text = "Max Screen",icon = "FULLSCREEN_ENTER") 

        
        

def register():
    bpy.utils.register_class(Pie_menu)

def unregister():
    bpy.utils.unregister_class(Pie_menu)

if __name__ == "__main__":
    register()

    bpy.ops.wm.call_menu_pie(name="Pie_menu")