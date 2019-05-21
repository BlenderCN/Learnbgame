bl_info = {
    "name": "Snapping Pies",
    "author": "Sebastian Koenig, Ivan Santic",
    "version": (0, 2),
    "blender": (2, 7, 2),
    "description": "Custom Pie Menus",
    "category": "Learnbgame"
}



import bpy
from bpy.types import Menu


###### FUNTIONS ##########

def enhanced_snapping_toggle(context):
    settings = context.scene.tool_settings
    ob = context.active_object

    settings.use_mesh_automerge = True
    if settings.snap_element != 'VERTEX':
        settings.snap_element = 'VERTEX'
        if ob and ob.mode == 'EDIT':
            bpy.ops.mesh.select_mode(use_extend=False, type='VERT')
    else:
        settings.snap_element = 'FACE'
        if ob and ob.mode == 'EDIT':
            bpy.ops.mesh.select_mode(use_extend=False, type='VERT')
            bpy.ops.mesh.select_mode(use_extend=True, type='EDGE')
            bpy.ops.mesh.select_mode(use_extend=True, type='FACE')
 


def origin_to_selection(context):
    context = bpy.context

    if context.object.mode == "EDIT":
        saved_location = context.scene.cursor_location.copy()
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        context.scene.cursor_location = saved_location


def origin_to_geometry(context):
    context = bpy.context

    if context.object.mode == "EDIT":
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        bpy.ops.object.mode_set(mode="EDIT")


########### CUSTOM OPERATORS ###############


class VIEW3D_OT_enhanced_snap_toggle(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "scene.enhanced_snap_toggle"
    bl_label = "Toggle Vertex/Face Snapping"
 
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'VIEW_3D'
 
    def execute(self, context):
        enhanced_snapping_toggle(context)
        return {'FINISHED'}
 


class VIEW3D_OT_origin_to_selected(bpy.types.Operator):
    bl_idname="object.origin_to_selected"
    bl_label="Origin to Selection"

    @classmethod
    def poll(cls, context):
        sc = context.space_data
        return (sc.type == 'VIEW_3D')

    def execute(self, context):
        origin_to_selection(context)
        return {'FINISHED'}


class VIEW3D_OT_origin_to_geometry(bpy.types.Operator):
    bl_idname="object.origin_to_geometry"
    bl_label="Origin to Geometry"

    @classmethod
    def poll(cls, context):
        sc = context.space_data
        return (sc.type == 'VIEW_3D')

    def execute(self, context):
        origin_to_geometry(context)
        return {'FINISHED'}


#Menu Snap Target
class VIEW3D_PIE_SnapTarget(Menu):
    bl_label = "Snap Target Menu"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        pie.operator("object.snaptargetvariable", text="Active", icon="SNAP_SURFACE").variable='ACTIVE'
        pie.operator("object.snaptargetvariable", text="Median", icon="SNAP_SURFACE").variable='MEDIAN'
        pie.operator("object.snaptargetvariable", text="Center", icon="SNAP_SURFACE").variable='CENTER'
        pie.operator("object.snaptargetvariable", text="Closest", icon="SNAP_SURFACE").variable='CLOSEST'
        pie.operator("object.snapelementvariable", text="Face", icon="SNAP_FACE").variable='FACE'
        pie.operator("object.snapelementvariable", text="Vertex", icon="SNAP_VERTEX").variable='VERTEX'
        pie.operator("object.snapelementvariable", text="Edge", icon="SNAP_EDGE").variable='EDGE'
        pie.operator("object.snapelementvariable", text="Increment", icon="SNAP_INCREMENT").variable='INCREMENT'



class VIEW3D_OT_SnapTargetVariable(bpy.types.Operator):
    bl_idname = "object.snaptargetvariable"
    bl_label = "Snap Target Variable"
    variable = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.context.scene.tool_settings.snap_target=self.variable
        return {'FINISHED'}





class VIEW3D_OT_SnapElementVariable(bpy.types.Operator):
    bl_idname = "object.snapelementvariable"
    bl_label = "Snap Element Variable"
    variable = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.context.scene.tool_settings.snap_element=self.variable
        return {'FINISHED'}



#Menu Snap Element
class VIEW3D_PIE_SnapElementMenu(Menu):
    bl_label = "Snap Element"

    def draw(self, context):
        settings = bpy.context.scene.tool_settings
        layout = self.layout
        pie = layout.menu_pie()
        pie.prop(settings, "snap_element", expand=True)





################### PIES #####################

class VIEW3D_PIE_origin(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "Origin"
    bl_idname = "object.snapping_pie"

    def draw(self, context):
        context = bpy.context
        layout = self.layout
        tool_settings = context.scene.tool_settings

        pie = layout.menu_pie()

        pie.operator("view3d.snap_selected_to_cursor", icon="CURSOR")
        pie.operator("view3d.snap_cursor_to_selected", icon="CLIPUV_HLT")

        # set origin to selection in Edit Mode, set origin to cursor in Object mode
        if context.object.mode == "EDIT":
            pie.operator("object.origin_to_selected", icon="OUTLINER_OB_EMPTY")
        else:
            pie.operator("object.origin_set",icon="EMPTY_DATA", text="Origin to Cursor").type="ORIGIN_CURSOR"

        if context.object.mode == "OBJECT":
            pie.operator("object.origin_set",icon="MESH_CUBE", text="Origin to Geometry").type="ORIGIN_GEOMETRY"
        else:
            pie.operator("object.origin_to_geometry", icon="MESH_CUBE")

        pie.operator("view3d.snap_cursor_to_center", icon="CURSOR")
        pie.operator("wm.call_menu_pie", text="Element / Target", icon='PLUS').name = "VIEW3D_PIE_SnapTarget"

       
        if tool_settings.use_snap:
            pie.prop(context.scene.tool_settings, "use_snap", text="Use Snap(ON)")
        else:
            pie.prop(context.scene.tool_settings, "use_snap", text="Use Snap(OFF)")
            
        pie.operator("scene.enhanced_snap_toggle", icon="AUTOMERGE_ON")



########## REGISTER ############

def register():
    bpy.utils.register_class(VIEW3D_PIE_origin)
    bpy.utils.register_class(VIEW3D_PIE_SnapElementMenu)
    bpy.utils.register_class(VIEW3D_PIE_SnapTarget)
    bpy.utils.register_class(VIEW3D_OT_origin_to_selected)
    bpy.utils.register_class(VIEW3D_OT_enhanced_snap_toggle)
    bpy.utils.register_class(VIEW3D_OT_origin_to_geometry)
    bpy.utils.register_class(VIEW3D_OT_SnapTargetVariable)
    bpy.utils.register_class(VIEW3D_OT_SnapElementVariable)


    wm = bpy.context.window_manager

    km = wm.keyconfigs.addon.keymaps.new(name = 'Object Mode')
    kmi = km.keymap_items.new('wm.call_menu_pie', 'S', 'PRESS', shift=True).properties.name = "object.snapping_pie"

    km = wm.keyconfigs.addon.keymaps.new(name = 'Mesh')
    kmi = km.keymap_items.new('wm.call_menu_pie', 'S', 'PRESS',shift=True).properties.name = "object.snapping_pie"




def unregister():

    bpy.utils.unregister_class(VIEW3D_PIE_origin)
    bpy.utils.unregister_class(VIEW3D_PIE_SnapElementMenu)
    bpy.utils.unregister_class(VIEW3D_PIE_SnapTarget)
    bpy.utils.unregister_class(VIEW3D_OT_origin_to_selected)
    bpy.utils.unregister_class(VIEW3D_OT_enhanced_snap_toggle)
    bpy.utils.unregister_class(VIEW3D_OT_origin_to_geometry)
    bpy.utils.unregister_class(VIEW3D_OT_SnapTargetVariable)
    bpy.utils.unregister_class(VIEW3D_OT_SnapElementVariable)


if __name__ == "__main__":
    register()
    #bpy.ops.wm.call_menu_pie(name="mesh.mesh_operators")
