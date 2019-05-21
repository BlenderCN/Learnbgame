import bpy,os
import copy
from .properties import CustomizeUIPrefs,CustomPanels
from .functions import get_panel_classes,get_panel_id

addon = os.path.basename(os.path.dirname(__file__))

class CustomizeUI(bpy.types.Operator) :
    bl_idname = "customizeui.customize_ui"
    bl_label = "Customize UI"

    panels_header = {}
    def execute(self,context) :

        customize_UI_prefs = context.user_preferences.addons[addon].preferences

        for pt in get_panel_classes() :
            pt_id = get_panel_id(pt)

            setattr(pt,'draw_header',eval("lambda s, c: (s.layout.prop(c.user_preferences.addons[addon].preferences.panels, '%s', text=''))"%pt_id))
            if "bl_rna" in pt.__dict__:
                bpy.utils.unregister_class(pt)
            bpy.utils.register_class(pt)

        customize_UI_prefs.customize = not customize_UI_prefs.customize
        return {'FINISHED'}
    def invoke(self,context,event) :
        customize_UI_prefs = context.user_preferences.addons[addon].preferences

        for pt in get_panel_classes() :
            pt_id = get_panel_id(pt)

            #Display all classes
            if "bl_rna" not in pt.__dict__:
                bpy.utils.register_class(pt)

            if hasattr(pt,'draw_header') :
                self.panels_header[pt_id] = pt.draw_header

            if not hasattr(CustomPanels,pt_id) :
                setattr(CustomPanels,pt_id,bpy.props.BoolProperty(default = True))

        self.execute(context)
        return {'FINISHED'}

class ApplyUI(bpy.types.Operator) :
    bl_idname = "customizeui.apply_ui"
    bl_label = "Apply UI"

    def execute(self,context) :
        customize_UI_prefs = context.user_preferences.addons[addon].preferences
        for pt in get_panel_classes() :
            pt_id = get_panel_id(pt)

            if pt_id in CustomizeUI.panels_header :

                setattr(pt,'draw_header',CustomizeUI.panels_header[pt_id])

            else :
                if hasattr(pt,'draw_header') :
                    delattr(pt,'draw_header')

            if "bl_rna" in pt.__dict__:
                bpy.utils.unregister_class(pt)
            bpy.utils.register_class(pt)

            if not getattr(customize_UI_prefs.panels,pt_id) :
                if "bl_rna" in pt.__dict__:
                    bpy.utils.unregister_class(pt)
        customize_UI_prefs.customize = not customize_UI_prefs.customize
        return {'FINISHED'}
