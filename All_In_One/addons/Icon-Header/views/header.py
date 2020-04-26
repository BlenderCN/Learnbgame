import bpy

# -----------------------------------------------------------------------------
# Draw UI, use an function to be append into 3D View Header
# -----------------------------------------------------------------------------
def ui_3D(self, context):
    layout = self.layout
    row = layout.row(align=True)

    row.operator("view.grid_control", text='', icon='GRID')
    icon = 'CURSOR'
    row.operator("object.center_pivot_mesh_obj", text='', icon=icon)
    icon = 'SMOOTH'
    row.operator("object.smooth_shading", text='', icon=icon)

    row = layout.row(align=True)
    icon = 'FORCE_TEXTURE'
    row.operator("unwrap.uv_checker", text='', icon=icon)
    icon = 'EDITMODE_HLT'
    row.operator("object.retopo_shading", text='', icon=icon)


# -----------------------------------------------------------------------------
# Draw UI, use an function to be append into UV/Image Editor View Header
# -----------------------------------------------------------------------------
def ui_UV(self, context):
    layout = self.layout
    row = layout.row(align=True)

    icon = 'CURSOR'
    row.operator("unwrap.reset_cursor", text='', icon=icon)
    icon = 'FORCE_TEXTURE'
    row.operator("unwrap.uv_checker", text='', icon=icon)

def register():
    bpy.types.VIEW3D_HT_header.append(ui_3D)
    bpy.types.IMAGE_HT_header.append(ui_UV)

def unregister():
    bpy.types.VIEW3D_HT_header.remove(ui_3D)
    bpy.types.IMAGE_HT_header.remove(ui_UV)
