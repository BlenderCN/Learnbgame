bl_info = {
        "name": "Marking Menu",
        "category": "3D View",
        "author": "Jesse Doyle of Form Affinity"
        }

import bpy
from bpy.types import Menu

class Submenu(Menu):
    bl_label = 'Submenu'    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Create:")
        layout.separator()
        layout.operator("mesh.primitive_plane_add", text = "Plane", icon = "MESH_PLANE")
        layout.operator("mesh.primitive_cube_add", text = "Cube", icon = "MESH_CUBE")
        layout.operator("mesh.primitive_circle_add", text = "Circle", icon = "MESH_CIRCLE")
        layout.operator("mesh.primitive_uv_sphere_add", text = "UV Sphere", icon = "MESH_UVSPHERE")
        layout.operator("mesh.primitive_ico_sphere_add", text = "Ico Sphere", icon = "MESH_ICOSPHERE")
        layout.operator("mesh.primitive_cylinder_add", text = "Cylinder", icon = "MESH_CYLINDER")
        layout.operator("mesh.primitive_cone_add", text = "Cone", icon = "MESH_CONE")
        layout.operator("mesh.primitive_torus_add", text = "Torus", icon = "MESH_TORUS")
        layout.operator("object.empty_add", text = "Null", icon = "EMPTY_AXIS").type='PLAIN_AXES'
        
        
class Submenu2(Menu):
    bl_label = 'Submenu2'    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Create:")
        layout.separator()
        layout.operator("object.light_add", text = "Point", icon = "LIGHT_POINT").type="POINT"
        layout.operator("object.light_add", text = "Sun", icon = "LIGHT_SUN").type="SUN"
        layout.operator("object.light_add", text = "Spot", icon = "LIGHT_SPOT").type="SPOT"
        layout.operator("object.light_add", text = "Area", icon = "LIGHT_AREA").type="AREA"
        
class Submenu3(Menu):
    bl_label = 'Submenu3'    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Clear Transforms")
        layout.separator()
        layout.operator("object.transforms_to_deltas",text = "Clear All", icon = "EMPTY_AXIS").mode="ALL"
        layout.operator("object.transforms_to_deltas",text = "Location", icon = "NDOF_TRANS").mode="LOC"
        layout.operator("object.transforms_to_deltas",text = "Rotation", icon = "NDOF_TURN").mode="ROT"
        layout.operator("object.transforms_to_deltas",text = "Scale", icon = "FULLSCREEN_ENTER").mode="SCALE"
        layout.separator()
        layout.label(text="Reset Transforms")
        layout.separator()
        layout.operator("object.location_clear",text = "Location", icon = "NDOF_TRANS").clear_delta=False
        layout.operator("object.rotation_clear", text = "Rotation", icon = "NDOF_TURN").clear_delta=False
        layout.operator("object.scale_clear", text = "Scale", icon = "FULLSCREEN_ENTER").clear_delta=False
        


class Pie_menu(Menu):
    bl_label = "Marking Menu"
    bl_idname = "view3D.Pie_menu"  
    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator("object.msm_from_object", text = "Vertex", icon = 'VERTEXSEL').mode = 'vert'
        pie.operator("object.mode_set", text="Edit Mode", icon='EDITMODE_HLT').mode= 'EDIT'
        pie.operator("object.shade_smooth", text = "Smooth", icon = "MOD_SMOOTH")
        pie.operator("object.msm_from_object", text = "Edge", icon = 'EDGESEL').mode = 'edge'
        pie.operator("view3d.localview", text = "Isolate", icon = "BORDERMOVE")
        pie.operator("object.mode_set", text = "Object", icon = "OBJECT_DATA")
        pie.operator("object.shade_flat", text = "Shade Flat", icon = "MOD_WIREFRAME")
        pie.operator("object.msm_from_object", text = "Face", icon = 'FACESEL').mode = 'face'
        pie.separator()
        pie.separator()
        other = pie.column()
        gap = other.column()
        gap.separator()
        gap.scale_y = 7
        other_menu = other.box().column()
        other_menu.scale_y=1.3
        other_menu.operator("mesh.select_all", text = "Invert Selection", icon ="UV_SYNC_SELECT").action="INVERT"
        other_menu.operator("screen.screen_full_area", text = "Max Screen",icon = "FULLSCREEN_ENTER") 
        other_menu.menu('Submenu', icon='RIGHTARROW_THIN',  text='Mesh Objects')
        other_menu.menu('Submenu2', icon='RIGHTARROW_THIN',  text='Lights')
        other_menu.menu('Submenu3', icon='RIGHTARROW_THIN',  text='History')
        


def register():
    bpy.utils.register_class(Submenu)
    bpy.utils.register_class(Submenu2)
    bpy.utils.register_class(Submenu3)
    bpy.utils.register_class(Pie_menu)

def unregister():
    bpy.utils.unregister_class(Submenu)
    bpy.utils.unregister_class(Submenu2)
    bpy.utils.unregister_class(Submenu3)
    bpy.utils.unregister_class(Pie_menu)

if __name__ == "__main__":
    register()

    bpy.ops.wm.call_menu_pie(name="Pie_menu")