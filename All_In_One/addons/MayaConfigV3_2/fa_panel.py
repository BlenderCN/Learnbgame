import bpy, os

class CustomPanel(bpy.types.Panel):
    """A Custom Panel in the Properties Toolbar"""
    bl_label = "Maya"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'


    def draw(self, context):
        layout = self.layout

        obj = context.object

        path = bpy.utils.user_resource('SCRIPTS', os.path.join("presets", "keyconfig"), create=False)


        row = layout.row()
        row.prop(bpy.context.space_data.overlay, 'show_cursor', text = "3D cursor", toggle = True)
        row = layout.row()
        row.operator('view3d.snap_cursor_to_center', text='Center', icon='PIVOT_CURSOR')
        row = layout.row()
        row.operator('mesh.select_mirror', text='Symmetry', icon='MOD_MIRROR')
        row = layout.row()
        row.operator("render.render", text='Render', icon='RENDER_STILL')
        row = layout.row()
        row.operator("screen.userpref_show", text='Prefs', icon='PREFERENCES')
        row = layout.row()
        row.operator("wm.url_open", text="Tutorials", icon="WORKSPACE").url = "https://www.youtube.com/channel/UCcCo0cPbrsWeoImgs6L7OOA"
        
        row = layout.row()
        row.operator("screen.region_quadview", text="QuadView", icon='VIEW_PERSPECTIVE')
        row = layout.row()
        row.operator("view3d.view_camera", text="Camera", icon='CAMERA_DATA')
        row = layout.row()
        row.label(text="Extras", icon='ADD')
        row = layout.row()
        row.operator('preferences.keyconfig_activate', text='Blender', icon='BLENDER').filepath = path + "/blender.py"
        row = layout.row()
        row.operator('preferences.keyconfig_activate', text='Maya', icon='EVENT_M').filepath = path + "/fa_hotkeys.py"
        row = layout.row()
        row.operator("wm.url_open", text="Donate", icon="FUND").url = "https://www.paypal.me/formaffinity"

def register():
    bpy.utils.register_class(CustomPanel)


def unregister():
    bpy.utils.unregister_class(CustomPanel)
    
if __name__ == "__main__":
    register()