# BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# END GPL LICENSE BLOCK #####


bl_info = {
    "name": "Rename Tools",
    "author": "Julio Iglesias & Luca Scheller ",
    "version": (1,0),
    "blender": (2, 74, 0),
    "location": "",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "User Interface"
}

import bpy
import bgl, blf, bmesh
import math, time, os, re
from bpy.app.handlers import persistent
from math import floor,ceil,log10,radians,degrees
from random import uniform as rand
from mathutils import Vector, Matrix, Color

keyboard_inputs = ['NONE', 'LEFTMOUSE', 'MIDDLEMOUSE', 'RIGHTMOUSE', 'BUTTON4MOUSE', 'BUTTON5MOUSE', 'BUTTON6MOUSE', 'BUTTON7MOUSE', 'ACTIONMOUSE', 'SELECTMOUSE', 'MOUSEMOVE', 'INBETWEEN_MOUSEMOVE', 'TRACKPADPAN', 'TRACKPADZOOM', 'MOUSEROTATE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE', 'WHEELINMOUSE', 'WHEELOUTMOUSE', 'EVT_TWEAK_L', 'EVT_TWEAK_M', 'EVT_TWEAK_R', 'EVT_TWEAK_A', 'EVT_TWEAK_S', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'ZERO', 'ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN', 'EIGHT', 'NINE', 'LEFT_CTRL', 'LEFT_ALT', 'LEFT_SHIFT', 'RIGHT_ALT', 'RIGHT_CTRL', 'RIGHT_SHIFT', 'OSKEY', 'GRLESS', 'TAB', 'SPACE', 'LINE_FEED', 'BACK_SPACE', 'DEL', 'SEMI_COLON', 'PERIOD', 'COMMA', 'QUOTE', 'ACCENT_GRAVE', 'MINUS', 'SLASH', 'BACK_SLASH', 'EQUAL', 'LEFT_BRACKET', 'RIGHT_BRACKET', 'LEFT_ARROW', 'DOWN_ARROW', 'RIGHT_ARROW', 'UP_ARROW', 'NUMPAD_2', 'NUMPAD_4', 'NUMPAD_6', 'NUMPAD_8', 'NUMPAD_1', 'NUMPAD_3', 'NUMPAD_5', 'NUMPAD_7', 'NUMPAD_9', 'NUMPAD_PERIOD', 'NUMPAD_SLASH', 'NUMPAD_ASTERIX', 'NUMPAD_0', 'NUMPAD_MINUS', 'NUMPAD_ENTER', 'NUMPAD_PLUS', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'F13', 'F14', 'F15', 'F16', 'F17', 'F18', 'F19', 'PAUSE', 'INSERT', 'HOME', 'PAGE_UP', 'PAGE_DOWN', 'END', 'MEDIA_PLAY', 'MEDIA_STOP', 'MEDIA_FIRST', 'MEDIA_LAST', 'TEXTINPUT', 'WINDOW_DEACTIVATE', 'TIMER', 'TIMER0', 'TIMER1', 'TIMER2', 'TIMER_JOBS', 'TIMER_AUTOSAVE', 'TIMER_REPORT', 'TIMERREGION', 'NDOF_MOTION', 'NDOF_BUTTON_MENU', 'NDOF_BUTTON_FIT', 'NDOF_BUTTON_TOP', 'NDOF_BUTTON_BOTTOM', 'NDOF_BUTTON_LEFT', 'NDOF_BUTTON_RIGHT', 'NDOF_BUTTON_FRONT', 'NDOF_BUTTON_BACK', 'NDOF_BUTTON_ISO1', 'NDOF_BUTTON_ISO2', 'NDOF_BUTTON_ROLL_CW', 'NDOF_BUTTON_ROLL_CCW', 'NDOF_BUTTON_SPIN_CW', 'NDOF_BUTTON_SPIN_CCW', 'NDOF_BUTTON_TILT_CW', 'NDOF_BUTTON_TILT_CCW', 'NDOF_BUTTON_ROTATE', 'NDOF_BUTTON_PANZOOM', 'NDOF_BUTTON_DOMINANT', 'NDOF_BUTTON_PLUS', 'NDOF_BUTTON_MINUS', 'NDOF_BUTTON_ESC', 'NDOF_BUTTON_ALT', 'NDOF_BUTTON_SHIFT', 'NDOF_BUTTON_CTRL', 'NDOF_BUTTON_1', 'NDOF_BUTTON_2', 'NDOF_BUTTON_3', 'NDOF_BUTTON_4', 'NDOF_BUTTON_5', 'NDOF_BUTTON_6', 'NDOF_BUTTON_7', 'NDOF_BUTTON_8', 'NDOF_BUTTON_9', 'NDOF_BUTTON_10', 'NDOF_BUTTON_A', 'NDOF_BUTTON_B', 'NDOF_BUTTON_C']

##################################################################################################################### Operators

class RT_Rename(bpy.types.Operator):
    bl_idname = "rt.rename"
    bl_label = "Rename Active Object"
    bl_description = "Rename Active Object"
    bl_options = {"REGISTER","BLOCKING","UNDO","INTERNAL"}

    Rename_Name = bpy.props.StringProperty(name="Name",default="")
    Rename_Warning = False
    Rename_ExistingNames = []
    Modal_Timer_Invoke = 0
    Modal_Timer = 0
    Modal_Counter = 0
    KM_Input = {}

    def draw(self, context):
        layout = self.layout
        '''
        col = layout.column()
        row = col.row()
        split = row.split(percentage=0.35)
        col_left = split.column()
        col_left.label(text = "Name")
        col_right = split.column()
        row = col_right.row()
        row.prop(self, 'Rename_Name',text="")
        if self.Rename_Warning == True:
            col.separator()
            row = col.row()
            row.alignment = 'CENTER'
            row.label(text="Name Exists", icon="ERROR")
        '''

    def invoke(self, context, event) :
        active_object = bpy.context.active_object
        self.Rename_Name = active_object.name
        self.Rename_ExistingNames = bpy.data.objects.keys()
        self.Modal_Timer_Invoke = time.time()
        KM = bpy.context.window_manager.keyconfigs['Blender User'].keymaps['3D View'].keymap_items['rt.rename']
        self.KM_Input = {"type":KM.type,"shift":KM.shift,"ctrl":KM.ctrl,"alt":KM.alt}
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        return {"FINISHED"}

    def modal(self,context,event):
        context.area.tag_redraw()
        region = context.region
        rv3d = context.space_data.region_3d
        active_object = bpy.context.active_object
        t = time.time()

        def modal_feedback(self,context):
            default_Prefix = "Rename: "
            Warning_Suffix = ""
            if self.Rename_Name in self.Rename_ExistingNames:
                Warning_Suffix = ""
            context.area.header_text_set(default_Prefix + self.Rename_Name + Warning_Suffix)
        if event.type == "BACK_SPACE" and event.value == "PRESS":
            if t-self.Modal_Timer < 0.04 and self.Modal_Counter > 4:
                self.Modal_Counter = 0
                self.Modal_Timer = 0
                self.Rename_Name = ""
            else:
                if t-self.Modal_Timer > 0.05:
                    self.Modal_Counter = 0
                else:
                    self.Modal_Counter += 1
                self.Modal_Timer = t
                self.Rename_Name = self.Rename_Name[:-1]
            modal_feedback(self,context)
            return {'RUNNING_MODAL'}
        elif event.type == self.KM_Input["type"] and event.value == "RELEASE" and event.shift == self.KM_Input["shift"] and event.ctrl == self.KM_Input["ctrl"] and event.alt == self.KM_Input["alt"]:
            if t-self.Modal_Timer_Invoke > 0.35: # Invoke Delay
                self.Rename_Name = ""
            modal_feedback(self,context)
            return {'RUNNING_MODAL'}
        elif (event.type == "ESC" and event.value == "RELEASE") or (event.type == "RIGHTMOUSE" and event.value == "RELEASE"):
            context.area.header_text_set()
            return {'CANCELLED'}
        elif (event.type == "RET" and event.value == "RELEASE") or (event.type == "LEFTMOUSE" and event.value == "RELEASE"):
            active_object.name = self.Rename_Name
            active_object.data.name = active_object.name
            context.area.header_text_set()
            return {'FINISHED'}
        else:
            self.Rename_Name += event.ascii
            modal_feedback(self,context)
            return {'RUNNING_MODAL'}

    def check(self, context):
        '''
        if self.Rename_Name in bpy.data.objects:
            self.Rename_Warning = True
        else:
            self.Rename_Warning = False
        '''
        return True

    @classmethod
    def poll(cls, context):
        return_value = False
        if bpy.context.active_object != None and bpy.context.mode == 'OBJECT':
            return_value = True
        return return_value

    ############################################################################################################### Main
    ############################################################################################################### LOD

class RT_DuplicateRename(bpy.types.Operator):
    bl_idname = "rt.duplicaterename"
    bl_label = "Duplicate Rename"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    def execute(self, context):
        existing_names = bpy.data.objects.keys()
        selected_objects = bpy.context.selected_objects
        for x in selected_objects:
            rename = None
            LOD_Use = False
            if x.name.rstrip("0123456789.")[-2:] == "HI":
                rename = x.name.rstrip("0123456789.")[:-2] + "LOD0"
                if rename in existing_names:
                    LOD_Use = True
            if x.name.rstrip("0123456789.")[-3:] == "LOD" or LOD_Use == True:
                rename = x.name if LOD_Use == False else rename
                suffix_id = 0
                while rename in existing_names:
                    suffix_id += 1
                    rename = rename.rstrip("0123456789.")
                    rename += str(suffix_id)
            if rename != None:
                x.name = rename
                x.data.name = x.name
                x.data.name = x.name
                existing_names.append(rename)

        return {"FINISHED"}

class RT_DuplicateRename_Macro(bpy.types.Macro):
    bl_idname = "rt.duplicaterename_macro"
    bl_label = "Duplicate Auto Rename"
    bl_description = "Duplicate with Automatic Asset Renaming"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

##################################################################################################################### Operators

##################################################################################################################### Add-on Prefs

def Hotkey_Update(self,context):
    #user_preferences = context.user_preferences
    #addon_prefs = user_preferences.addons[__name__].preferences
    bpy.context.window_manager.keyconfigs['Blender User'].keymaps['3D View'].keymap_items['rt.rename'].type = self.RT_Rename_Hotkey_Ascii[0].upper()
    bpy.context.window_manager.keyconfigs['Blender User'].keymaps['3D View'].keymap_items['rt.rename'].shift = self.RT_Rename_Hotkey_Shift
    bpy.context.window_manager.keyconfigs['Blender User'].keymaps['3D View'].keymap_items['rt.rename'].ctrl = self.RT_Rename_Hotkey_Ctrl
    bpy.context.window_manager.keyconfigs['Blender User'].keymaps['3D View'].keymap_items['rt.rename'].alt = self.RT_Rename_Hotkey_Alt

class RT_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    RT_Rename_Hotkey_Ascii = bpy.props.StringProperty(name="Rename Hotkey",default="R",maxlen=1,update = Hotkey_Update)
    RT_Rename_Hotkey_Shift = bpy.props.BoolProperty(name="Rename Hotkey Shift",default=False,update = Hotkey_Update)
    RT_Rename_Hotkey_Ctrl = bpy.props.BoolProperty(name="Rename Hotkey Ctrl",default=True,update = Hotkey_Update)
    RT_Rename_Hotkey_Alt = bpy.props.BoolProperty(name="Rename Hotkey Alt",default=True,update = Hotkey_Update)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        row = col.row()
        split = row.split(percentage=0.2)
        col_left = split.column()
        col_left.label(text = "Rename Hotkey:")
        col_right = split.column()
        row = col_right.row()
        split = row.split(percentage=0.5)
        col_left = split.row()
        col_left.prop(self, 'RT_Rename_Hotkey_Ascii',text="")
        col_right = split.row()
        col_right.prop(self, 'RT_Rename_Hotkey_Shift',text="Shift")
        col_right.prop(self, 'RT_Rename_Hotkey_Ctrl',text="Ctrl")
        col_right.prop(self, 'RT_Rename_Hotkey_Alt',text="Alt")

##################################################################################################################### Add-on Prefs

##################################################################################################################### Register Functions

# Globals
RT_addon_keymaps = []

def register():

    # Panels, Ops & Vars
    bpy.utils.register_class(RT_AddonPreferences)
    bpy.utils.register_class(RT_Rename)
    bpy.utils.register_class(RT_DuplicateRename)
    bpy.utils.register_class(RT_DuplicateRename_Macro)
    RT_DuplicateRename_Macro.define("OBJECT_OT_duplicate")
    RT_DuplicateRename_Macro.define("RT_OT_duplicaterename")
    RT_DuplicateRename_Macro.define("TRANSFORM_OT_translate")

    # KeyMaps
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons[__name__].preferences
    global RT_addon_keymaps
    km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    kmi = km.keymap_items.new('rt.rename',addon_prefs.RT_Rename_Hotkey_Ascii,'PRESS',ctrl=addon_prefs.RT_Rename_Hotkey_Ctrl,alt=addon_prefs.RT_Rename_Hotkey_Alt,shift=addon_prefs.RT_Rename_Hotkey_Shift)
    RT_addon_keymaps.append(km)
    km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new('rt.duplicaterename_macro','D','PRESS',shift=True)
    RT_addon_keymaps.append(km)

def unregister():

    # Panels, Ops & Vars
    bpy.utils.unregister_class(RT_AddonPreferences)
    bpy.utils.unregister_class(RT_Rename)
    bpy.utils.unregister_class(RT_DuplicateRename)
    bpy.utils.unregister_class(RT_DuplicateRename_Macro)

    # KeyMaps
    global RT_addon_keymaps
    for km in RT_addon_keymaps:
        bpy.context.window_manager.keyconfigs.addon.keymaps.remove(km)
    RT_addon_keymaps.clear()


if __name__ == "__main__":
    register()
