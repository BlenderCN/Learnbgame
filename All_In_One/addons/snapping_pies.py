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


class VIEW3D_PIE_Snapping_Extras(Menu):
    bl_label = "Snapping Extras"
    

    def draw(self, context):
        layout = self.layout
        space = context.space_data

        pie = layout.menu_pie()
        pie.operator("view3d.snap_cursor_to_center", icon="MANIPUL")
        pie.operator("view3d.snap_cursor_to_active", icon="CURSOR")
        pie.operator("view3d.snap_selected_to_grid", icon="GRID")
        pie.operator("view3d.snap_cursor_to_grid", icon="GRID")
        
 

class VIEW3D_OT_toggle_pivot(bpy.types.Operator):
    """Toggle between 3D-Cursor and Median pivoting"""
    bl_idname = "scene.toggle_pivot"
    bl_label = "Toggle Pivot"
 
    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'VIEW_3D'
 
    def execute(self, context):
        pivot = context.space_data.pivot_point
        if pivot == "CURSOR":
            context.space_data.pivot_point = "MEDIAN_POINT"
        elif pivot == "INDIVIDUAL_ORIGINS":
            context.space_data.pivot_point = "MEDIAN_POINT"
        else:
            context.space_data.pivot_point = "CURSOR"
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


#Menu Snap Element
class VIEW3D_OT_SetPivotIndividual(bpy.types.Operator):
    bl_label = "Individual Origins"
    bl_idname = "object.setpivotindidual"

    @classmethod
    def poll(cls, context):
        sc = context.space_data
        return (sc.type == 'VIEW_3D')

    def execute(self, context):
        bpy.context.space_data.pivot_point = "INDIVIDUAL_ORIGINS"
        return {'FINISHED'}
        






################### PIES #####################

class VIEW3D_PIE_origin(Menu):
    # label is displayed at the center of the pie menu.
    bl_label = "Snapping and Origin"
    bl_idname = "object.snapping_pie"

    def draw(self, context):
        context = bpy.context
        layout = self.layout
        tool_settings = context.scene.tool_settings

        pie = layout.menu_pie()

        pie.operator("view3d.snap_selected_to_cursor", icon="CLIPUV_HLT")
        pie.operator("view3d.snap_cursor_to_selected", icon="CURSOR")

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

        if context.object.mode == "EDIT":
            if tool_settings.use_mesh_automerge:
                pie.prop(tool_settings, "use_mesh_automerge", text="Automerge (ON)", icon='AUTOMERGE_ON')
            else:
                pie.prop(tool_settings, "use_mesh_automerge", text="Automerge (OFF)", icon='AUTOMERGE_OFF')
        else:
            pie.operator("object.setpivotindidual", icon="ROTATECOLLECTION")

        pie.operator("scene.toggle_pivot", icon="ROTATECENTER")



########## REGISTER ############

def register():
    bpy.utils.register_class(VIEW3D_OT_toggle_pivot)
    bpy.utils.register_class(VIEW3D_OT_origin_to_selected)
    bpy.utils.register_class(VIEW3D_OT_origin_to_geometry)
    bpy.utils.register_class(VIEW3D_OT_SnapTargetVariable)
    bpy.utils.register_class(VIEW3D_OT_SnapElementVariable)
    bpy.utils.register_class(VIEW3D_OT_SetPivotIndividual)
    bpy.utils.register_class(VIEW3D_PIE_origin)
    bpy.utils.register_class(VIEW3D_PIE_SnapElementMenu)
    bpy.utils.register_class(VIEW3D_PIE_SnapTarget)
    bpy.utils.register_class(VIEW3D_PIE_Snapping_Extras)


    wm = bpy.context.window_manager

    km = wm.keyconfigs.addon.keymaps.new(name = 'Object Mode')
    kmi = km.keymap_items.new('wm.call_menu_pie', 'S', 'PRESS', shift=True).properties.name = "object.snapping_pie"

    km = wm.keyconfigs.addon.keymaps.new(name = 'Mesh')
    kmi = km.keymap_items.new('wm.call_menu_pie', 'S', 'PRESS',shift=True).properties.name = "object.snapping_pie"




def unregister():

    bpy.utils.unregister_class(VIEW3D_OT_toggle_pivot)
    bpy.utils.unregister_class(VIEW3D_OT_origin_to_selected)
    bpy.utils.unregister_class(VIEW3D_OT_origin_to_geometry)
    bpy.utils.unregister_class(VIEW3D_OT_SnapTargetVariable)
    bpy.utils.unregister_class(VIEW3D_OT_SnapElementVariable)
    bpy.utils.unregister_class(VIEW3D_OT_SetPivotIndividual)
    bpy.utils.unregister_class(VIEW3D_PIE_origin)
    bpy.utils.unregister_class(VIEW3D_PIE_SnapElementMenu)
    bpy.utils.unregister_class(VIEW3D_PIE_SnapTarget)
    bpy.utils.unregister_class(VIEW3D_PIE_Snapping_Extras)


if __name__ == "__main__":
    register()
    #bpy.ops.wm.call_menu_pie(name="mesh.mesh_operators")
