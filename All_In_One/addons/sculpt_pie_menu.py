import bpy

from bpy.types import Menu, Operator

bl_info = {
    "name": "Sculpting Brushes",
    "author": "Andrew Merizalde <andrewmerizalde@hotmail.com>",
    "version": (1, 0, 0),
    "blender": (2, 7, 8),
    "location": "Viewport",
    "description": "Spacebar to access sculpting brushes pie menu.",
    "wiki_url": "https://github.com/amerizalde/sculpt_pie_menu",
    "tracker_url": "",
    "category": "Learnbgame"
}

addon_keymaps = []


class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    pie_style = bpy.props.BoolProperty(
        name = "Use Pie Style Menu",
        description = "Toggle between a Pie menu and a 'Standard' popup menu",
        default = True)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "pie_style")


class SculptingBrushSelector(Operator):
    """Update the current sculpting brush with the selected brush"""
    bl_idname = "alm.sculpt_brush_select"
    bl_label = "Select Sculpt Brush"
    bl_options = {"REGISTER", "UNDO"}

    # add enum property
    ### When an item only contains 4 items they define (identifier, name, description, number).
    # Tricky...
    mode_options = [
        ("Clay Strips", "Clay Strips", "Clay Strips", "BRUSH_CLAY", 0),
        ("Crease", "Crease", "Crease", "BRUSH_CREASE", 1),
        ("Grab", "Grab", "Grab", "BRUSH_GRAB", 2),
        ("Draw", "Sculpt Draw", "Sculpt Draw", "BRUSH_SCULPT_DRAW", 3),
        ("Scrape/Peaks", "Scrape/Peaks", "Scrape/Peaks", "BRUSH_SCRAPE", 4),
        ("Clay", "Clay", "Clay", "BRUSH_CLAY", 5),
        ("Flatten/Contrast", "Flatten/Contrast", "Flatten/Contrast", "BRUSH_FLATTEN", 6),
        ("Snake Hook", "Snake Hook", "Snake Hook", "BRUSH_SNAKE_HOOK", 7),
        ("Inflate/Deflate", "Inflate/Deflate", "Inflate/Deflate", "BRUSH_INFLATE", 8),
        ("Mask", "Mask", "Mask", "BRUSH_MASK", 9),
        ("Fill/Deepen", "Fill/Deepen", "Fill/Deepen", "BRUSH_FILL", 10),
        ("Blob", "Blob", "Blob", "BRUSH_BLOB", 11),
        ("Layer", "Layer", "Layer", "BRUSH_LAYER", 12),
        ("Smooth", "Smooth", "Smooth", "BRUSH_SMOOTH", 13),
        ("Thumb", "Thumb", "Thumb", "BRUSH_THUMB", 14),
        ("Nudge", "Nudge", "Nudge", "BRUSH_NUDGE", 15),
        ("Pinch/Magnify", "Pinch/Magnify", "Pinch/Magnify", "BRUSH_PINCH", 16)]

    selected_mode = bpy.props.EnumProperty(
            items=mode_options,
            description="Sculpt Brushes",
            default="Clay Strips")

    def execute(self, context):
        context.tool_settings.sculpt.brush = bpy.data.brushes[self.selected_mode]
        return {"FINISHED"}


class SculptingPieMenu(Menu):
    """Open a pie menu with all the sculpting brushes"""
    bl_idname = "alm.sculpt_pie_menu"
    bl_label = "Select Sculpt Brush"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        pie.operator_enum("alm.sculpt_brush_select", "selected_mode")


class SculptingFloatingMenu(Menu):
    bl_idname = "alm.sculpt_floating_menu"
    bl_label = "Select Sculpt Brush"
    
    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.operator_menu_enum("alm.sculpt_brush_select", "selected_mode")
        

        
class SculptingMenuCaller(Operator):
    """An operator for keymapping the menu"""
    bl_idname = "alm.sculpt_menu_call"
    bl_label = "Open Sculpt Pie Menu"

    def execute(self, context):
        if __name__ != '__main__':
            addon_prefs = context.user_preferences.addons[__name__].preferences
            if addon_prefs.pie_style:
                bpy.ops.wm.call_menu_pie(name="alm.sculpt_pie_menu")
            else:
                bpy.ops.wm.call_menu(name="alm.sculpt_floating_menu")
        return {'FINISHED'}

classes = [AddonPreferences, SculptingBrushSelector, SculptingPieMenu, SculptingFloatingMenu, SculptingMenuCaller]

def register():
    # add operator
    for c in classes:
        bpy.utils.register_class(c)

    # add keymap entry
    kcfg = bpy.context.window_manager.keyconfigs.addon
    if kcfg:
        km = kcfg.keymaps.new(name='Sculpt', space_type='EMPTY')
        kmi = km.keymap_items.new("alm.sculpt_menu_call", 'SPACE', 'PRESS')
        addon_keymaps.append((km, kmi))

def unregister():

    # remove keymap entry
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    for c in reversed(classes):
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()
