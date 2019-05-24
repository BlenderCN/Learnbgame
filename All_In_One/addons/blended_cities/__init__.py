# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
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
# ##### END GPL LICENSE BLOCK #####
bl_info = {
    "name": "Blended Cities",
    "description": "A city builder",
    "author": "Jerome Mahieux (Littleneo)",
    "version": (0, 5),
    "blender": (2, 5, 8),
    "api": 37702,
    "location": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}
 
print('\n. %s addon init\n'% __name__)


if __name__ != "__main__" :

    if "bpy" in locals():
        print('\n. reload modules\n')
        import imp
        imp.reload(core.class_main)
        imp.reload(core.class_import)
        imp.reload(core.main)
        print()
    else:
        print('\n. load modules\n')
        import bpy
        ## helpers
        from blended_cities.utils.log_tools import LoggerLogs, Logger, LoggerPopup, LoggerConsole
        from blended_cities.utils.log_tools import register as log_install, unregister as log_uninstall
        import blended_cities.utils.vmodal as modal
        from blended_cities.core.class_main import *
        from blended_cities.core.class_import import *
        from blended_cities.utils.meshes_io import *
        from blended_cities.core.ui import *
        from blended_cities.core.main import *


else :
    print('\n%s init as text\n'% __name__)
    print('\nNOT IMPLEMENTED :\n')
    john_doe()
 
    
def register() :

        # For now they need to be registered first due to: http://wiki.blender.org/index.php/Dev:2.5/Py/API/Overview#Manipulating-Classes
        # Maybe later we find another solution to be able to register builders later too?
        # builders :
        register_default_builders()

        # log_tools module attached to scene.city.log
        log_install()
        BlendedCities.log = bpy.props.PointerProperty(type=Logger)
        bpy.types.Logger.bpy_instance_path.append('scene.city.log')

        # modal module attached to scene.city.modal
        modal.register_modal()
        BlendedCities.modal = bpy.props.PointerProperty(type=modal.ModalState)
        bpy.types.ModalState.bpy_instance_path.append('scene.city.modal')

        #operators :
        bpy.utils.register_class(OP_BC_cityMethods)

        # ui. scene.city.ui as path to modals
        bpy.utils.register_class(WM_OT_Panel_expand)
        bpy.utils.register_class(BC_City_ui)
        bpy.utils.register_class(BC_City_ui_helpers)
        bpy.utils.register_class(OP_BC_Selector)
        bpy.utils.register_class(BC_main_panel)
        bpy.utils.register_class(BC_outlines_panel)
        #BlendedCities.ui = bpy.props.PointerProperty(type=BC_City_ui_helpers)
        BC_City_ui.helpers = bpy.props.PointerProperty(type=BC_City_ui_helpers)

        # class_main
        bpy.utils.register_class(BC_groups)
        bpy.utils.register_class(BC_builders)
        bpy.utils.register_class(BC_outlines)
        bpy.utils.register_class(BC_elements)
        bpy.utils.register_class(BlendedCities)

        bpy.types.Scene.city = bpy.props.PointerProperty(type=BlendedCities)

        #bpy.types.Scene.city.ui = bpy.props.PointerProperty(type=BC_City_ui)
        BlendedCities.builders = bpy.props.PointerProperty(type=BC_builders)
        items=[('niet','niet','')]
        for m in bpy.data.materials :
            items.append( (m.name,m.name,'') )
        BC_City_ui.matmenu = bpy.props.EnumProperty(items=items)


def unregister() :

    print('\n. %s addon unregister\n'% __name__)
    scene = bpy.data.scenes[0]
    module_name = 'blended_cities.builders'
    for m in dict(sys.modules) :
        if module_name + '.' == m[0:len(module_name) +1 ] :
            builder = m[len(module_name) +1:]+'.BC_'+m[len(module_name) +5:]
            exec('bpy.utils.unregister_class(builders.%s)'%builder)
            exec('bpy.utils.unregister_class(builders.%s_panel)'%builder)
            del sys.modules[m]
            print('\t%s unregistered'%builder)
    bpy.utils.unregister_class(BC_nones)
    bpy.utils.unregister_class(BC_objects)
    bpy.utils.unregister_class(BC_groups)
    del bpy.types.Scene.city
    bpy.utils.unregister_class(BlendedCities)
    bpy.utils.unregister_class(BC_elements)
    bpy.utils.unregister_class(BC_outlines)
    bpy.utils.unregister_class(BC_builders)

    # ui
    bpy.utils.unregister_class(OP_BC_Selector)
    bpy.utils.unregister_class(BC_main_panel)
    bpy.utils.unregister_class(BC_outlines_panel)
    #bpy.utils.unregister_class(BC_selector_panel)
    bpy.utils.unregister_class(WM_OT_Panel_expand)
    bpy.utils.unregister_class(BC_City_ui)

    # operators
    bpy.utils.unregister_class(OP_BC_cityMethods)

    log_uninstall()
    '''
    # this permits to work on multifiles addons without having to restarts blender every 3 min.
    # 'the (already registered' bug)
    # not needed if addon dependencies is used
    import addon_utils
    if hasattr(addon_utils,'lnmod') == False :
        module_name = 'blended_cities'
        for m in dict(sys.modules) :
            if module_name + '.' == m[0:len(module_name) +1 ] :
                del sys.modules[m]
        try : del sys.modules[module_name]
        except : pass
    '''

