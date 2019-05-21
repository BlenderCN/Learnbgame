bl_info = {
    "name": "Pie View",
    "description": "View Modes",
    "author": "Vaughan Ling",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
    }


import bpy
from bpy.types import Menu

# View Pie with left meaning left of model vs Blender defaults

class VIEW3D_PIE_View(Menu):
    bl_idname = "pie.view"
    bl_label = "View"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        # left
        pie.operator("view3d.view_axis", text="Left").type = "LEFT"
        # right
        pie.operator("view3d.view_axis", text="Right").type = "RIGHT"
        # bottom
        split = pie.split()
        col = split.column(align=True)
        row = col.row(align=True)
        row.scale_y=1.5
        row.operator("view3d.view_camera", text="Camera")
        col.separator()
        row = col.row(align=True)
        row.scale_y=1.5
        row.operator("view3d.create_camera_at_view", text="Create Camera At View")
        row = col.row(align=True)
        row.scale_y=1.5
        prop = row.operator("wm.context_toggle", text="Lock Camera To View")
        prop.data_path = "space_data.lock_camera"
        row = col.row(align=True)
        row.scale_y=1.5
        prop = row.operator("view3d.object_as_camera", text="Set as Render Camera")

        # top
        pie.operator("view3d.view_axis", text="Top").type = "TOP"
        # topleft
        pie.operator("view3d.view_axis", text="Back").type = "BACK"
        # topright
        pie.operator("view3d.view_axis", text="Front").type = "FRONT"
        # bottomleft

        # bottomright
        pie.operator("view3d.view_axis", text="Bottom").type = "BOTTOM"

        props = pie.operator("view3d.view_axis", text="Align Active")
        props.align_active = True
        props.type = 'TOP'

class Create_Camera_At_View(bpy.types.Operator):
    bl_idname = "view3d.create_camera_at_view"        # unique identifier for buttons and menu items to reference.
    bl_label = ""         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def invoke(self, context, event):
        def create_camera_at_view():
            bpy.ops.object.camera_add()
            bpy.context.object.data.passepartout_alpha = 1
            active_cam = bpy.context.active_object
            bpy.context.scene.camera = active_cam 
            bpy.ops.view3d.camera_to_view()  
        try:
            if context.active_object.mode == 'EDIT':
                active_object = bpy.context.active_object
                bpy.ops.object.editmode_toggle()
                create_camera_at_view()
                bpy.context.view_layer.objects.active = active_object
                bpy.ops.object.editmode_toggle()
            else:
                create_camera_at_view()
        except:
            create_camera_at_view()
        return {'FINISHED'}

def register():
    bpy.utils.register_class(Create_Camera_At_View)
    bpy.utils.register_class(VIEW3D_PIE_View)

def unregister():
    bpy.utils.unregister_class(Create_Camera_At_View)
    bpy.utils.unregister_class(VIEW3D_PIE_View)
	
if __name__ == "__main__":
    register()
