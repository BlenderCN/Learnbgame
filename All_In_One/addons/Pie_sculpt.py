bl_info = {
    "name": "Pinceles_Pie_Menus",
    "author": "Jose Ant. Garcia",
    "version": (0, 1, 4),
    "description": "Custom Pie Menus",
    "category": "Learnbgame",
}

import bpy
from bpy.types import Menu
from bpy.props import *

class FloodOperator(bpy.types.Operator):
    '''dynto flood fill a sculpt'''
    bl_idname = "dynto.retopo"
    bl_label = "Sculpt Dynto Flood"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        ob = context.active_object
        wm = context.window_manager
        oldMode = ob.mode

        ob.select = True

        bpy.ops.object.mode_set(mode='SCULPT')
        bpy.ops.sculpt.dynamic_topology_toggle()
        wm.flood_meshsculpt = bpy.data.scenes[bpy.data.scenes[0].name].tool_settings.sculpt.constant_detail_resolution
        bpy.ops.sculpt.detail_flood_fill()
        bpy.ops.sculpt.dynamic_topology_toggle()

        return {'FINISHED'}


class Espejo(bpy.types.Operator):
    bl_idname = "symetri.retopo"
    bl_label = "Symmetry"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        bpy.ops.sculpt.dynamic_topology_toggle()
        bpy.ops.sculpt.symmetrize()
        bpy.ops.sculpt.dynamic_topology_toggle()

        return {'FINISHED'}


class PieSculptPie(Menu):
    bl_idname = "pie.pinceles"
    bl_label = "Brochas Sculpt"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        box = pie.split().column()
        row = box.row(align=True)
        box.scale_x=0.5
        box.operator("paint.brush_select", text='Fill/Deepen', icon='BRUSH_FILL').sculpt_tool= 'FILL'
        box.operator("paint.brush_select", text='Flatten', icon='BRUSH_FLATTEN').sculpt_tool= 'FLATTEN'
        box.operator("paint.brush_select", text='Pinch', icon='BRUSH_PINCH').sculpt_tool= 'PINCH'
        box.operator("paint.brush_select", text='Scrape', icon='BRUSH_SCRAPE').sculpt_tool='SCRAPE'

        box = pie.split().column()
        row = box.row(align=True)
        box.scale_x=0.5
        box.operator("paint.brush_select", text='Grab', icon='BRUSH_GRAB').sculpt_tool= 'GRAB'
        box.operator("paint.brush_select", text='Twist', icon='BRUSH_ROTATE').sculpt_tool= 'ROTATE'
        box.operator("paint.brush_select", text='Snakehook', icon='BRUSH_SNAKE_HOOK').sculpt_tool= 'SNAKE_HOOK'
        box.operator("paint.brush_select", text='Nudge', icon='BRUSH_NUDGE').sculpt_tool='NUDGE'

        box = pie.split().column()
        row = box.row(align=True)
        box.scale_x=0.5
        box.operator("paint.brush_select", text='Mask', icon='BRUSH_MASK').sculpt_tool= 'MASK'
        box.operator("paint.brush_select", text='Smooth', icon='BRUSH_SMOOTH').sculpt_tool= 'SMOOTH'

        box = pie.split().column()
        row = box.row(align=True)
        box.scale_x=0.5
        box.operator("paint.brush_select", text='Blob', icon='BRUSH_BLOB').sculpt_tool= 'BLOB'
        box.operator("paint.brush_select", text='Layer', icon='BRUSH_LAYER').sculpt_tool= 'LAYER'
        box.operator("paint.brush_select", text='Draw', icon='BRUSH_SCULPT_DRAW').sculpt_tool= 'DRAW'

        pie.operator("paint.brush_select", text='Inflate/Deflate', icon='BRUSH_INFLATE').sculpt_tool='INFLATE'

        pie.operator("paint.brush_select", text='Clay Strips', icon='BRUSH_CLAY_STRIPS').sculpt_tool='CLAY_STRIPS'

        pie.operator("paint.brush_select", text='Crease', icon='BRUSH_CREASE').sculpt_tool='CREASE'


        pie.operator("paint.brush_select", text="Clay", icon='BRUSH_CLAY').sculpt_tool='CLAY'



class PieSculpttres(Menu):
    bl_idname = "pie.opciones"
    bl_label = "Options Sculpt"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        sculpt = context.tool_settings.sculpt
        box = pie.split().box().column()

        row = box.row(align=True)
        row.label(text="Symmetry:")
        row.prop(sculpt, "use_symmetry_x", text="x", toggle=True)
        row.prop(sculpt, "use_symmetry_y", text="y", toggle=True)
        row.prop(sculpt, "use_symmetry_z", text="z", toggle=True)
        row = box.row(align=True)
        row.label(text="Lock:    ")

        row.prop(sculpt, "lock_x", text="x", toggle=True)
        row.prop(sculpt, "lock_y", text="y", toggle=True)
        row.prop(sculpt, "lock_z", text="z", toggle=True)


        box = pie.split().box().column()
        row = box.split(align=True)

        row.label(text="Curves:")
        row = box.row(align=True)
        row = box.split(align=True)
        row.operator("brush.curve_preset", icon='SMOOTHCURVE', text="").shape = 'SMOOTH'
        row.operator("brush.curve_preset", icon='SPHERECURVE', text="").shape = 'ROUND'
        row.operator("brush.curve_preset", icon='ROOTCURVE', text="").shape = 'ROOT'
        row.operator("brush.curve_preset", icon='SHARPCURVE', text="").shape = 'SHARP'
        row.operator("brush.curve_preset", icon='LINCURVE', text="").shape = 'LINE'
        row.operator("brush.curve_preset", icon='NOCURVE', text="").shape = 'MAX'

        box = pie.split().box().column()
        row = box.split(align=True)

        row.label(text="Sculpt Tools:")
        row = box.row(align=True)
        row.scale_x=0.9
        row.operator("boolean.mask_extract", text="Extract Mask")
        row = box.row(align=True)
        row.operator("boolean.mod_xmirror", text="X-mirror")


        sculpt = context.tool_settings.sculpt
        box = pie.split().box().column()

        row = box.row(align=False)
        row.scale_x=0.5

        if context.sculpt_object.use_dynamic_topology_sculpting:
            row.operator("sculpt.dynamic_topology_toggle", icon='X', text="Disable Dyntopo")
        else:
            row.operator("sculpt.dynamic_topology_toggle", icon='SCULPT_DYNTOPO', text="Enable Dyntopo")
        row = box.row(align=True)

        if (sculpt.detail_type_method == 'CONSTANT'):
            row.prop(sculpt, "constant_detail_resolution")
            row.operator("sculpt.sample_detail_size", text="", icon='EYEDROPPER')
        else:
            row.prop(sculpt, "detail_size")
        row = box.row(align=True)
        row.scale_x=0.6
        row.prop(sculpt, "detail_refine_method", text="")

        row.prop(sculpt, "detail_type_method", text="")


        brush = context.tool_settings.sculpt.brush
        capabilities = brush.sculpt_capabilities
        box = pie.split().box().column()
        row = box.row(align=True)
        row.prop(brush, "use_frontface", text="Front Faces Only")
        row = box.row(align=True)

        row.prop(brush, "use_accumulate", text="Accumulate")

        sculpt = context.tool_settings.sculpt
        box = pie.split().box().column()

        row = box.row(align=True)
        row.operator("symetri.retopo", text="Symmetrize", icon='MOD_MIRROR')
        row = box.row(align=True)
        row.prop(sculpt,"symmetrize_direction",text="")

        box = pie.split().box().column()
        row = box.row(align=True)
        wm = context.scene.tool_settings.sculpt
        row.prop(wm, "constant_detail_resolution", "Resolution")

        box = pie.split().box().column()
        row = box.row(align=True)

        ups = context.tool_settings.unified_paint_settings

        row.scale_x = 1.3
        row.prop(brush, "use_original_normal", toggle=True, icon_only=True)
        row.prop(brush, "sculpt_plane", text="")
        row = box.row(align=True)
        row.prop(ups, "size", text="Radius", slider=False)
        row.scale_x = 1.3
        row.prop(ups, "use_pressure_size", text="")
        row = box.row(align=True)
        row.prop(ups, "strength",  slider=False)
        row.scale_x = 1.3
        row.prop(ups, "use_pressure_strength", text="")


addon_keymaps = []

def register():
    bpy.utils.register_module(__name__)

    bpy.types.WindowManager.flood_meshsculpt = FloatProperty(min = 0.10, max = 100, default = 30)


    wm = bpy.context.window_manager

    if wm.keyconfigs.addon:


        km = wm.keyconfigs.addon.keymaps.new(name='Sculpt')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'W', 'PRESS')
        kmi.properties.name = "pie.pinceles"


        km = wm.keyconfigs.addon.keymaps.new(name='Sculpt')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'W', 'PRESS', alt=True)
        kmi.properties.name = "pie.opciones"


def unregister():
    bpy.utils.unregister_module(__name__)


    wm = bpy.context.window_manager

    if wm.keyconfigs.addon:
        for km in addon_keymaps:
            for kmi in km.keymap_items:
                km.keymap_items.remove(kmi)

            wm.keyconfigs.addon.keymaps.remove(km)


    del addon_keymaps[:]

if __name__ == "__main__":
    register()
