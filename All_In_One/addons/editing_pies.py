
bl_info = {
  "name": "Editing Pies",
  "author": "Sebastian Koenig",
  "version": (0, 1),
  "blender": (2, 7, 2),
  "location": "3dView",
  "description": "Add pie menus, R for mesh and C for origin",
  "warning": "",
  "wiki_url": "https://github.com/sebastian-k/scripts",
  "tracker_url": "https://github.com/sebastian-k/scripts/issues",
  "category": "3D View"
  }

import bpy
from bpy.types import Menu


############### FUNCTIONS ##########################







class VIEW3D_PIE_mesh_menu(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "Mesh Operators"
    bl_idname = "mesh.mesh_operators"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()


        pie.operator("mesh.unsubdivide")
        pie.operator("mesh.subdivide").smoothness=0
        pie.operator("mesh.subdivide", text="Subdivide Smooth").smoothness=1
        pie.operator("mesh.loopcut_slide")
        pie.operator("screen.repeat_last")
        props = pie.operator("mesh.knife_tool", text="Knife")
        props.use_occlude_geometry = True
        props.only_selected = False

        pie.operator("mesh.bevel")
        pie.operator("mesh.bridge_edge_loops")


class VIEW3D_PIE_origin(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "Origin"
    bl_idname = "object.origin_pie"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()


        pie.operator("view3d.snap_cursor_to_selected", icon="CURSOR")
        pie.operator("view3d.snap_selected_to_cursor", icon="CURSOR")
        pie.operator("view3d.snap_cursor_to_center", icon="CURSOR")
        pie.operator("view3d.snap_cursor_to_active", icon="CURSOR")
        pie.operator("object.origin_set",icon="EMPTY_DATA", text="Origin to Geometry").type="ORIGIN_GEOMETRY"
        pie.operator("object.origin_set",icon="EMPTY_DATA", text="Origin to Cursor").type="ORIGIN_CURSOR"
        pie.operator("object.origin_set",icon="EMPTY_DATA", text="Geometry to Origin").type="GEOMETRY_ORIGIN"
        pie.operator("object.origin_set",icon="EMPTY_DATA", text="Origin to Center of Mass").type="ORIGIN_CENTER_OF_MASS"




########## register ############






def register():
    bpy.utils.register_class(VIEW3D_PIE_mesh_menu)
    bpy.utils.register_class(VIEW3D_PIE_origin)


    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Mesh')

    kmi = km.keymap_items.new('wm.call_menu_pie', 'R', 'PRESS').properties.name = "mesh.mesh_operators"
    km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type="VIEW_3D")
    kmi = km.keymap_items.new('wm.call_menu_pie', 'C', 'PRESS').properties.name = "object.origin_pie"





def unregister():

    bpy.utils.unregister_class(VIEW3D_PIE_mesh_menu)
    bpy.utils.unregister_class(VIEW3D_PIE_origin)


if __name__ == "__main__":
    register()
    #bpy.ops.wm.call_menu_pie(name="mesh.mesh_operators")
