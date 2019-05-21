
import bpy
import bl_ui
from extensions_framework.ui import property_group_renderer
from .. import CustomeRenderAddon




class addon_panel(bl_ui.space_userpref.USERPREF_PT_addons, property_group_renderer):
    COMPAT_ENGINES = 'CUSTOME_RENDER'

@CustomeRenderAddon.addon_register_class
class CustomeRenderAddon_PT_addonpreference(addon_panel):
    bl_label = 'Addon Type'
    #bl_options = {'DEFAULT_CLOSED'}
    
    
    display_property_groups = [
        ( ('user_preferences',), 'custome_addon_pref' )
    ]

    
    """
    Something goes wrong here I don't know what ?
    
    """
    
    def draw(self, context):
#        layout = self.layout
#        layout.prop(context.user_preferences.custome_addon_pref, "justSomethingToTestWith")
        super().draw(context)



