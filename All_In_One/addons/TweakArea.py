######################################################################################################
# A tool that makes opening/closing window faster and easier                                         #
# Actualy partly uncommented - if you do not understand some parts of the code,                      #
# please see further version or contact me                                                           #
# Author: Lapineige                                                                                  #
# License: GPL v3                                                                                    #
######################################################################################################


############# Add-on description (used by Blender)

bl_info = {
    "name": "Tweak Area",
    "description": 'A tool that makes opening/closing window faster and easier',
    "author": "Lapineige",
    "version": (1, 4),
    "blender": (2, 71, 0),
    "location": "Shortcut (default Mouse Button 5)",
    "warning": "",
    "wiki_url": "https://www.youtube.com/watch?v=CTPsqHxmrgM&list=UUNhIgErK9OY3XzhEoRS_j7Q",
    "tracker_url": "http://le-terrier-de-lapineige.over-blog.com/contact",
    "category": "Learnbgame"
}

##############

import bpy
########################
###### Preferences Panel
class TweakAreaPreferencePanel(bpy.types.AddonPreferences):
    """ Create a configuration panel in the preferences """
    bl_idname = __name__

    TweakArea_map_type = bpy.props.StringProperty(default='')
    TweakArea_type = bpy.props.StringProperty(default='')
    TweakArea_value = bpy.props.StringProperty(default='')
    SwitchArea_type = bpy.props.StringProperty(default='')
    SwitchArea_map_type = bpy.props.StringProperty(default='')
    SwitchArea_value = bpy.props.StringProperty(default='')

    def draw(self, context):
        layout = self.layout
        wm = bpy.context.window_manager

        box = layout.box()
        box.label(text='Tweak Area:')
        row = box.row()
        row.prop(wm.keyconfigs['Blender'].keymaps['Window'].keymap_items[TweakArea.bl_idname], "map_type")
        row.prop(wm.keyconfigs['Blender'].keymaps['Window'].keymap_items[TweakArea.bl_idname], "value")
        row.prop(wm.keyconfigs['Blender'].keymaps['Window'].keymap_items[TweakArea.bl_idname], "type", full_event=True)

        box = layout.box()
        box.label(text='Switch Area:')
        row = box.row()
        row.prop(wm.keyconfigs['Blender'].keymaps['Window'].keymap_items[SwitchArea.bl_idname], "map_type")
        row.prop(wm.keyconfigs['Blender'].keymaps['Window'].keymap_items[SwitchArea.bl_idname], "value")
        row.prop(wm.keyconfigs['Blender'].keymaps['Window'].keymap_items[SwitchArea.bl_idname], "type", full_event=True)

        row = layout.row()
        row.scale_y = 2.0
        row.operator('wm.apply_shorcut_as_default', text='Apply Shortcuts')
        return {'FINISHED'}

class ApplyShorcutsAsDefault(bpy.types.Operator):
    """  """
    bl_idname = "wm.apply_shorcut_as_default"
    bl_label = "Apply Shorcut As Default"
    
    @classmethod
    def poll(cls, context):
        return __name__ in [addon.module for addon in context.user_preferences.addons]

    def execute(self, context):
        wm = bpy.context.window_manager

        for name in (TweakArea.bl_idname,SwitchArea.bl_idname):
            new_value = wm.keyconfigs['Blender'].keymaps['Window'].keymap_items[name].value
            new_type = wm.keyconfigs['Blender'].keymaps['Window'].keymap_items[name].type
            new_map_type = wm.keyconfigs['Blender'].keymaps['Window'].keymap_items[name].map_type
            wm.keyconfigs['Blender'].keymaps['Window'].keymap_items.remove(wm.keyconfigs['Blender'].keymaps['Window'].keymap_items[name])
            wm.keyconfigs['Blender'].keymaps['Window'].keymap_items.new(name, new_type, new_value)
            if name == TweakArea.bl_idname:
                context.user_preferences.addons[__name__].preferences.TweakArea_map_type , context.user_preferences.addons[__name__].preferences.TweakArea_type , context.user_preferences.addons[__name__].preferences.TweakArea_value = (new_map_type, new_type, new_value)
            elif name == SwitchArea.bl_idname:
                context.user_preferences.addons[__name__].preferences.SwitchArea_map_type , context.user_preferences.addons[__name__].preferences.SwitchArea_type , context.user_preferences.addons[__name__].preferences.SwitchArea_value = (new_map_type, new_type, new_value)
        return {'FINISHED'}
    
########################
###### Tweak Area

class TweakArea(bpy.types.Operator):
    """ Join the current area with the selected (by clicking), or divide it """
    bl_idname = "wm.tweak_area"
    bl_label = "Tweak Area"

    @classmethod
    def poll(cls, context):
        if context.screen.show_fullscreen:
                self.report({'INFO'}, "Impossible to do in fullscreen mode")
                return False
        return True

    min_x = bpy.props.IntProperty()
    min_y = bpy.props.IntProperty()

    def modal(self, context, event):
        if event.type == 'LEFTMOUSE':
            self.max_x = event.mouse_x
            self.max_y = event.mouse_y
            if bpy.ops.screen.area_join(min_x=self.min_x, min_y=self.min_y, max_x=self.max_x, max_y=self.max_y) == {'CANCELLED'}:
                if (min(self.min_x,self.max_x) >= context.area.x) and (min(self.min_y,self.max_y) >= context.area.y) and (max(self.min_x,self.max_x) <= (context.area.x + context.area.width)) and (max(self.min_y,self.max_y) <= (context.area.y + context.area.height)):
                    if abs(self.min_x - self.max_x) > abs(self.min_y - self.max_y):
                        bpy.ops.screen.area_split(direction='VERTICAL', factor=(self.max_x - context.area.x)/(context.area.width), mouse_x=self.min_x, mouse_y=self.min_y)
                    elif abs(self.min_x - self.max_x) < abs(self.min_y - self.max_y):
                        bpy.ops.screen.area_split(direction='HORIZONTAL', factor=(self.max_y - context.area.y)/(context.area.height), mouse_x=self.min_x, mouse_y=self.min_y)
                else:
                    self.report({'INFO'}, "Areas selected can't be merged together")
            bpy.ops.screen.header_toggle_menus()
            bpy.ops.screen.header_toggle_menus()
            return {'FINISHED'}
        elif event.type == 'RIGHTMOUSE' or event.type == 'ESC':
            return {'CANCELLED'}
        else:
            return {'PASS_THROUGH'}

    def invoke(self, context, event):
        self.min_x = event.mouse_x
        self.min_y = event.mouse_y
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

class SwitchArea(bpy.types.Operator):
    """ Join the current area with the selected (by clicking), or divide it """
    bl_idname = "wm.switch_area"
    bl_label = "Switch Area"

    @classmethod
    def poll(cls, context):
        if context.screen.show_fullscreen:
                self.report({'INFO'}, "Impossible to do in fullscreen mode")
                return False
        return True

    def modal(self, context, event):
        if event.type == 'LEFTMOUSE':
            area = self.detect_area(event.mouse_x, event.mouse_y, context)
            if not (area is self.invk_area):
                tmp = area.type
                area.type = self.invk_area.type
                self.invk_area.type = tmp
            return {'FINISHED'}
        elif event.type == 'RIGHTMOUSE' or event.type == 'ESC':
            return {'CANCELLED'}
        else:
            return {'PASS_THROUGH'}

    def invoke(self, context, event):
        self.invk_area = context.area
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def detect_area(self, x, y, context):
        for area in context.screen.areas:
            h , w= area.height , area.width
            if (x>=area.x) and (y>=area.y) and (x<=(area.x+w)) and (y<=(area.y+h)):   
                return area


###################### Registration of all Operators, Panels and Shortcuts

def register():
    bpy.utils.register_class(TweakAreaPreferencePanel)
    bpy.utils.register_class(ApplyShorcutsAsDefault)

    bpy.utils.register_class(TweakArea)
    bpy.utils.register_class(SwitchArea)
    # keymap
    wm = bpy.context.window_manager
    if wm.keyconfigs['Blender'].keymaps['Window'].keymap_items.find(TweakArea.bl_idname) == -1:
        if bpy.context.user_preferences.addons[__name__].preferences.TweakArea_type != '': # need to use both properties for a better security
            wm.keyconfigs['Blender'].keymaps['Window'].keymap_items.new(TweakArea.bl_idname, bpy.context.user_preferences.addons[__name__].preferences.TweakArea_type, bpy.context.user_preferences.addons[__name__].preferences.TweakArea_value)
            wm.keyconfigs['Blender'].keymaps['Window'].keymap_items.new(SwitchArea.bl_idname, bpy.context.user_preferences.addons[__name__].preferences.SwitchArea_type, bpy.context.user_preferences.addons[__name__].preferences.SwitchArea_value)
        else:
            wm.keyconfigs['Blender'].keymaps['Window'].keymap_items.new(TweakArea.bl_idname, 'BUTTON5MOUSE', 'PRESS')
            wm.keyconfigs['Blender'].keymaps['Window'].keymap_items.new(SwitchArea.bl_idname, 'BUTTON5MOUSE', 'PRESS', ctrl=True)

###################### Unregistration of all Operators, Panels and Shortcuts
    
def unregister():
    bpy.utils.unregister_class(TweakAreaPreferencePanel)
    bpy.utils.unregister_class(ApplyShorcutsAsDefault)


    # keymap
    wm = bpy.context.window_manager
    wm.keyconfigs['Blender'].keymaps['Window'].keymap_items.remove(wm.keyconfigs['Blender'].keymaps['Window'].keymap_items[TweakArea.bl_idname])
    wm.keyconfigs['Blender'].keymaps['Window'].keymap_items.remove(wm.keyconfigs['Blender'].keymaps['Window'].keymap_items[SwitchArea.bl_idname])
    bpy.utils.unregister_class(TweakArea)
    bpy.utils.unregister_class(SwitchArea)
    
if __name__ == '__main__':
    register()
