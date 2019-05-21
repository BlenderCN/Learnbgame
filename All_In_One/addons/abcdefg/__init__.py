#----------------------------------------------------------
# File __init__.py
#----------------------------------------------------------


bl_info = {
    'name': "Anatomic Profile Generator",
    'author': "Patrick R. Moore",
    'version': (1,1,1),
    'blender': (2, 7, 8),
    'api': 59393,
    'location': "3D View -> Tool Shelf",
    'description': "Specialty CAD Package",
    'warning': "",
    'wiki_url': "",
    'tracker_url': "",
    'category': '3D View'}



#http://stackoverflow.com/questions/918154/relative-paths-in-python
import sys, os, platform, inspect, imp


sys.path.append(os.path.join(os.path.dirname(__file__)))
print(os.path.join(os.path.dirname(__file__)))

''' 
if "bpy" in locals():
    import imp
    
    imp.reload(classes)
    imp.reload(odcutils)
    imp.reload(crown)
    imp.reload(margin)
    imp.reload(bridge)
    imp.reload(panel)
    print("Reloaded multifiles")
    
else:
    from . import classes, odcutils, crown, margin, bridge, panel
    print("Imported multifiles")
''' 
import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty, FloatProperty
from bpy.app.handlers import persistent
#from . 

import odcutils

from . import addon_updater_ops

def update_preset(self, context):
    
    if self.heal_tooth_preset == 'ANTERIOR':
        sel = [5,6,7,8,9,10,21,23,24,26] #remember index - 1 
    elif self.heal_tooth_preset == 'ASSORTED':
        sel = [2,3,5,7,8,10,12,13,18,19,21,22,25,26,28,29]
    elif self.heal_tooth_preset == 'POSTERIOR':
        sel = [2,3,12,13,18,19,28,29] 
    else:
        sel = []
        
    for i in range(0,32):
        if i in sel:
            self.heal_teeth[i] = True
        else:
            self.heal_teeth[i] = False

#addon preferences
class UCLAPreferences(AddonPreferences):
    bl_idname = __name__
        
    #UCLA Tempalte properties
    heal_show_prefs = bpy.props.BoolProperty(
            name="Show UCLA Abut Preferences",
            default=True)
    
    items = ['UNIVERSAL','F.D.I.', 'PALMER']
    items_enum = []
    for index, item in enumerate(items):
        items_enum.append((item, item, item))
       
    heal_number_sys = bpy.props.EnumProperty(items = items_enum, name = "Number System", default = 'UNIVERSAL')
    
    
    items2 = ['ANTERIOR','POSTERIOR','ASSORTED','CUSTOM']
    presets_enum = []
    for index, item in enumerate(items2):
        presets_enum.append((item, item, item))
     
    heal_tooth_preset = bpy.props.EnumProperty(items = presets_enum, 
                                               name = "Preset Arrangements", 
                                               default = 'ASSORTED',
                                               update = update_preset)
     

    items3 = ['WIZARD','ADVANCED']
    workflow_enum = []
    for index, item in enumerate(items3):
        workflow_enum.append((item, item, item))
       
    heal_workflow = bpy.props.EnumProperty(items = workflow_enum, name = "Workflow", default = 'WIZARD')
    
    
    items5 = ['SMALL','MEDIUM', 'LARGE']
    scale_enum = []
    for index, item in enumerate(items5):
        scale_enum.append((item, item, item))
       
    profile_scale = bpy.props.EnumProperty(items = scale_enum, name = "Profile Size", default = 'MEDIUM')
    
    items4 = ['CONE','HOURGLASS', 'BOWL','DEEP_BOWL']
    profile_enum = []
    for index, item in enumerate(items4):
        profile_enum.append((item, item, item))
       
    heal_profile = bpy.props.EnumProperty(items = profile_enum, name = "Profile", default = 'BOWL')
    
    items5 = ['DIRECT','INVERTED']
    template_enum = []
    for index, item in enumerate(items5):
        template_enum.append((item, item, item))
       
    heal_print_type = bpy.props.EnumProperty(items = template_enum, 
                                             name = "3D Print Type", 
                                             default = 'DIRECT',
                                             description = 'Choose DIRECT for a template to be used directly, INVERTED for a mould to pour silicone material')
    
     
    heal_show_ob = bpy.props.BoolProperty(
            name="Show CEJ Transforms",
            default=True)
    
    heal_advanced_abutment = bpy.props.BoolProperty(
            name="Show Advanced Abutment Tools",
            default=False)
    
    heal_show_edit = bpy.props.BoolProperty(
            name="Show Profile Editing Options",
            default=True)
        
    heal_abutment_file = bpy.props.StringProperty(
            name="Abutment File",
            default='',
            subtype='FILE_PATH')
        
    heal_abutment_depth = bpy.props.FloatProperty(
            name="Abutment Depth",
            default=5.0, min = 2.0, max = 10.0)
      
    heal_passive_offset = bpy.props.FloatProperty(
            name="Abutment Depth",
            default=.1, min = 0.001, max = 0.3,
            description = "Gap to make abutment seat passively in the well")
    
    heal_abutment_diameter = bpy.props.FloatProperty(
            name="Abutment Collar Diameter",
            description = "The diameter of the collar where material will meet the abutment",
            default=3.5, min = 1.8, max = 7.0)
        
    heal_block_border_x = bpy.props.FloatProperty(
            name="X Border Spacer",
            description = "The spacer between edge of CEJ template at sides of block",
            default=2, min = 1.5, max = 20)
    
    heal_block_border_y = bpy.props.FloatProperty(
            name="Y Border Spacer",
            description = "The spacer between edge of CEJ template at top of block",
            default=5, min = 1.5, max = 20)
        
    heal_inter_space_x = bpy.props.FloatProperty(
            name="X spacing between abutments",
            description = "The spacer between edge of templates",
            default=2.0, min = 1.5, max = 10)
    
    heal_inter_space_y = bpy.props.FloatProperty(
            name="Y spacing between abutments",
            description = "The spacer between edge of templates",
            default=2.0, min = 1.5, max = 10)
    
    heal_middle_space_x= bpy.props.FloatProperty(
            name="Width of middle column",
            description = "The spacer between edge of templates",
            default=4.0, min = 1.5, max = 10)
       
    heal_bevel_width = bpy.props.FloatProperty(
            name="Bevel Width",
            description = "Constant which controls beveling of the block",
            default=3, min = 1, max = 5)
        
    
    mould_wall_thickness = bpy.props.FloatProperty(
            name="Mould Wall Thickness",
            description = "Wall thickness for inverted moutl",
            default=4.2, min = 2, max = 10)
    
    
    default_text_size = bpy.props.FloatProperty(
            name="Default Text Size",
            description = "Size of Labels",
            default=3.0, min = 2, max = 10)
    
    heal_n_cols = bpy.props.IntProperty(
            name = "Wells Per Row",
            default = 6, min = 1, max = 32)
        
    heal_teeth = bpy.props.BoolVectorProperty(
            name = "Teeth",
            size = 32,
            subtype = 'LAYER',
            default = (False, False, True, True, False, True, False, True,
                       True, False, True, False, True, True, False, False,
                       False, False, True, True, False, True, False, False,
                       False, False, True, False, True, True, False, False))
    
    heal_custom_text = bpy.props.StringProperty(
            name = "Custom Text",
            default = "Custom Template Label")
    
    heal_block_label = bpy.props.StringProperty(
            name = "Block Label",
            description = "Needed if your file name doesn't have meaningful name or if you created abutment with APG",
            default = "")
    
    heal_invert_mould = bpy.props.BoolProperty(
            name = "Invert Mould",
            default = False,
            description = "Use this setting to make inverted mould for silicone pouring")
    
    heal_mirror_transform =  bpy.props.BoolProperty(
            name = "Mirror Transforms",
            default = False,
            description = "Use this setting to make opposite side CEJ profiles symmetric when editing them")
    
    dev = bpy.props.BoolProperty(
            name = "Development Mode",
            default = False,
            description = "Use this setting to try stuff out")
    
    auto_check_update = bpy.props.BoolProperty(
        name = "Auto-check for Update",
        description = "If enabled, auto-check for updates using an interval",
        default = False,
        )
    updater_intrval_months = bpy.props.IntProperty(
        name='Months',
        description = "Number of months between checking for updates",
        default=0,
        min=0
        )
    updater_intrval_days = bpy.props.IntProperty(
        name='Days',
        description = "Number of days between checking for updates",
        default=7,
        min=0,
        )
    updater_intrval_hours = bpy.props.IntProperty(
        name='Hours',
        description = "Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
        )
    updater_intrval_minutes = bpy.props.IntProperty(
        name='Minutes',
        description = "Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
        )

    #behavior_mode = EnumProperty(name="How Active Tooth is determined by operator", description="'LIST' is more predictable, 'ACTIVE' more like blender, 'ACTIVE_SELECTED' is for advanced users", items=behavior_enum, default='0')

    def draw(self, context):
        layout = self.layout
        layout.label(text="Anatomic Profile Generator Preferences and Settings")
        
        addon_updater_ops.update_settings_ui(self,context)



                          
def register():
    import odcutils, panel, healing_abutment, tracking, import_export #, crown, margin, bridge, splint, implant, panel, help, flexible_tooth, bracket_placement, denture_base, occlusion, ortho, curve_partition # , odcmenus, bgl_utils
     
    #register them
    odcutils.register()
    healing_abutment.register()
    import_export.register()
    panel.register()
    
    bpy.utils.register_class(UCLAPreferences)

    tracking.register(bl_info)
    addon_updater_ops.register(bl_info)
    
def unregister():
    #if __ in locals etc
    import odcutils, panel, healing_abutment
    bpy.utils.unregister_class(UCLAPreferences)

    odcutils.unregister()
    panel.unregister()
    healing_abutment.unregister()
    
 
if __name__ == "__main__":
    register()