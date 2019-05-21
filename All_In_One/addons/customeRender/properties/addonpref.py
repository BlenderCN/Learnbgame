import bpy
from .. import CustomeRenderAddon

from extensions_framework import declarative_property_group
from extensions_framework import util as efutil


@CustomeRenderAddon.addon_register_class
class custome_addon_pref(declarative_property_group):
    """             
    """

    ef_attach_to = ['AddonPreferences']
    controls = ['myPathToExec']
    visibility = {}
    enabled = {}
    alert = {}
    

    
    properties = [
        {            
            'type': 'bool',
            'attr': 'justSomethingToTestWith',
            'name': 'Just Something To TestWith',
            'description': 'If every thing works fine a check box should appear in th UI addons pannel under CustomeRender enabler.',
            'default': False,
            'save_in_preset': True
        },
#        {
#            'type': 'string',
#            'subtype': 'FILE_PATH',
#            'attr': 'myPathToExec',
#            'name': 'Exec Path',
#            'description': 'The path to my executable.',            
#            'default': '',
#            'save_in_preset': True
#        },
                  ]
    