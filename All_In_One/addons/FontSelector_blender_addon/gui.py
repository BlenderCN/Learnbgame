import bpy

from bpy.types import Panel

from.preferences import get_addon_preferences

# Properties Panel GUI
class FontSelectorPanel(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_category = "Font Selector"
    bl_context = "data"
    bl_label = "Font Selection"
    
    @classmethod
    def poll(cls, context):
        active=bpy.context.active_object
        if active is not None:
            active_type=active.type
        else:
            active_type=""
        return active_type=='FONT'

    def draw(self, context):
        layout = self.layout
        activedata = context.active_object.data
        draw_general_gui(layout, activedata)

# Sequencer Panel GUI
class SEQUENCER_PT_font_selector(Panel):
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Strip"
    bl_label = "Font Selection"
    #bl_parent_id = "SEQUENCER_PT_effect"
    #bl_options = {'DEFAULT_CLOSED'}

    @staticmethod
    def has_sequencer(context):
        return (context.space_data.view_type in {'SEQUENCER', 'SEQUENCER_PREVIEW'})

    @classmethod
    def poll(cls, context):
        if not cls.has_sequencer(context):
            return False
        try :
            strip = context.scene.sequence_editor.active_strip
            strip.name
        except AttributeError:
            return False

        return strip.type == 'TEXT'


    def draw(self, context):
        layout = self.layout
        activedata = context.scene.sequence_editor.active_strip
        draw_general_gui(layout, activedata)


# general GUI
def draw_general_gui(layout, activedata):
    layout.use_property_split = True # Active single-column layout
    
    #get addon prefs
    addon_preferences = get_addon_preferences()
    debug = addon_preferences.debug_value
    rownumber = addon_preferences.row_number
    fplist = addon_preferences.font_folders
    
    wm = bpy.data.window_managers['WinMan']
    
    # no font folder
    if len(fplist)==0:
        layout.label(text = 'Add Font Folder in Addon Preference', icon = 'INFO')

    else:
        row = layout.row(align = True)
        row.operator("fontselector.modal_refresh", text = "", icon = 'FILE_REFRESH')

        # no list
        if len(wm.fontselector_list) == 0 :
            row = layout.row()
            row.label(text = 'Refresh to get List of available Fonts', icon = 'INFO')

        else: 
            row.operator("fontselector.check_changes", text = '', icon = 'OUTLINER_OB_LIGHT')
            row.separator()
            row.operator("fontselector.remove_unused", text = "", icon = 'UNLINKED')
            if activedata.fontselector_font_missing :
                row.separator()
                row.label(text = "Missing : " + activedata.fontselector_font, icon = "ERROR")
                row.operator("fontselector.open_font_folder", text = "", icon = 'FILE_FOLDER')

            # debug font
            if debug :
                box = layout.box()
                box.label(text = "DEBUG")
                row = box.row()
                row.label(text = "font : " + activedata.fontselector_font)
                row = box.row()
                row.label(text = "index : " + str(activedata.fontselector_index))
                row = box.row()
                row.label(text = "avoid : " + str(activedata.fontselector_avoid_changes))

            row = layout.row()
            row.template_list("FontUIList", "", wm, "fontselector_list", activedata, "fontselector_index", rows = rownumber)