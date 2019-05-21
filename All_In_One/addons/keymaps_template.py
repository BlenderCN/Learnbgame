import bpy
from bpy.types import Operator, Menu, AddonPreferences
import rna_keymap_ui


bl_info = {
    "name": "custom_keymaps_template",
    "description": "Single Line Explanation",
    "author": "Legigan Jeremy AKA Pistiwique$",
    "version": (0, 0, 1),
    "blender": (2, 78, 0),
    "location": "View3D",
    "warning": "This is an unstable version",
    "wiki_url": "",
    "category": "Learnbgame"
}


class TEST_operator_cube_add(Operator):
    ''' Simple test operator '''
    bl_idname = 'object.cube_add'
    bl_label = "Add Cube"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        bpy.ops.mesh.primitive_cube_add()

        return {'FINISHED'}

class TEST_menu_cube_add(Menu):
    ''' Simple test menu '''
    bl_idname = "menu.cube_add"
    bl_label = "Menu Cube Add"

    def draw(self, context):
        layout = self.layout
        layout.operator('mesh.primitive_cube_add', text = "Add Cube",
                        icon = 'MESH_CUBE')


class TEST_pie_menu_cube_add(Menu):
    ''' Simple test pie menu '''
    bl_idname = "pie.cube_add"
    bl_label = "Pie Cube Add"

    def draw(self, context):
        pie = self.layout.menu_pie()
        pie.operator('mesh.primitive_cube_add', text = "Add Cube",
                        icon = 'MESH_CUBE')

'''
The keymaps_items_dict is the only variable that you have to setup.
All the rest will be done automatically ;)

keymaps_items_dict = {"Name": [kmi_name, kmi_value, km_name, space_type,
                               region_type, event_type, event_value, ctrl, 
                               shift, alt],
                      }

Name: Name that will be displayed in the panel preferences

kmi_name: - bl_idname for the operators (exemple: 'object.cube_add')
          - 'wm.call_menu' for menu
          - 'wm.call_menu_pie' for pie menu

kmi_value: - bl_idname for Menu or Pie Menu
           - None for operators

km_name: keymap name
    exemple: '3D View Generic'

space_type: space type of the keymap, see:
https://docs.blender.org/api/blender_python_api_2_78_release/bpy.types.KeyMap.html?highlight=keymap#bpy.types.KeyMap.space_type

region_type: region type of the keymap, see:
https://docs.blender.org/api/blender_python_api_2_78_release/bpy.types.KeyMap.html?highlight=keymap#bpy.types.KeyMap.region_type

event_type: type of the event, see:
https://docs.blender.org/api/blender_python_api_2_78_release/bpy.types.Event.html?highlight=event#bpy.types.Event.type

event_value: value of the event, see:
https://docs.blender.org/api/blender_python_api_2_78_release/bpy.types.Event.html?highlight=event#bpy.types.Event.value

ctrl: Boolean

shift: Boolean

alt: Boolean

'''
keymaps_items_dict = {"Cube Operator":['object.cube_add', None, '3D View '
                                      'Generic', 'VIEW_3D', 'WINDOW',
                                      'RIGHTMOUSE', 'PRESS', True, False, False
                                      ],

                     "Cube Menu":['wm.call_menu', 'menu.cube_add', '3D View '
                                  'Generic', 'VIEW_3D', 'WINDOW', 'RIGHTMOUSE',
                                  'PRESS', True, True, False
                                  ],

                     "Cube Pie Menu":['wm.call_menu_pie', 'pie.cube_add',
                                      '3D View Generic', 'VIEW_3D', 'WINDOW',
                                       'RIGHTMOUSE', 'PRESS', True, True, True
                                      ]
                     }


class TestAddonPreferences(AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        wm = context.window_manager
        layout = self.layout

        draw_keymap_items(wm, layout)


addon_keymaps = []

def draw_keymap_items(wm, layout):
    kc = wm.keyconfigs.user

    for name, items in keymaps_items_dict.items():
        kmi_name, kmi_value, km_name = items[:3]
        box = layout.box()
        split = box.split()
        col = split.column()
        col.label(name)
        col.separator()
        km = kc.keymaps[km_name]
        get_hotkey_entry_item(kc, km, kmi_name, kmi_value, col)


def get_hotkey_entry_item(kc, km, kmi_name, kmi_value, col):

    # for menus and pie_menu
    if kmi_value:
        for km_item in km.keymap_items:
            if km_item.idname == kmi_name and km_item.properties.name == kmi_value:
                col.context_pointer_set('keymap', km)
                rna_keymap_ui.draw_kmi([], kc, km, km_item, col, 0)
                return

        col.label("No hotkey entry found for {}".format(kmi_value))
        col.operator(Template_Add_Hotkey.bl_idname, icon='ZOOMIN')

    # for operators
    else:
        if km.keymap_items.get(kmi_name):
            col.context_pointer_set('keymap', km)
            rna_keymap_ui.draw_kmi(
                    [], kc, km, km.keymap_items[kmi_name], col, 0)
        else:
            col.label("No hotkey entry found for {}".format(kmi_name))
            col.operator(Template_Add_Hotkey.bl_idname, icon='ZOOMIN')


def add_hotkey():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    # In background mode, there's no such thing has keyconfigs.user,
    # because headless mode doesn't need key combos.
    # So, to avoid error message in background mode, we need to check if
    # keyconfigs is loaded.
    if not kc:
        return

    for items in keymaps_items_dict.values():
        kmi_name, kmi_value, km_name, space_type, region_type = items[:5]
        eventType, eventValue, ctrl, shift, alt = items[5:]
        km = kc.keymaps.new(name = km_name, space_type = space_type,
                            region_type=region_type)

        kmi = km.keymap_items.new(kmi_name, eventType,
                                  eventValue, ctrl = ctrl, shift = shift,
                                  alt = alt

                                  )
        if kmi_value:
            kmi.properties.name = kmi_value

        kmi.active = True

    addon_keymaps.append((km, kmi))

class Template_Add_Hotkey(bpy.types.Operator):
    ''' Add hotkey entry '''
    bl_idname = "template.add_hotkey"
    bl_label = "Add Hotkeys"
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        add_hotkey()

        self.report({'INFO'},
                    "Hotkey added in User Preferences -> Input -> Screen -> Screen (Global)")
        return {'FINISHED'}


def remove_hotkey():
    ''' clears all addon level keymap hotkeys stored in addon_keymaps '''

    kmi_values = [item[1] for item in keymaps_items_dict.values() if item]
    kmi_names = [item[0] for item in keymaps_items_dict.values() if item not in ['wm.call_menu', 'wm.call_menu_pie']]

    for km, kmi in addon_keymaps:
        # remove addon keymap for menu and pie menu
        if hasattr(kmi.properties, 'name'):
            if kmi_values:
                if kmi.properties.name in kmi_values:
                    km.keymap_items.remove(kmi)

        # remove addon_keymap for operators
        else:
            if kmi_names:
                if kmi.name in kmi_names:
                    km.keymap_items.remove(kmi)

    addon_keymaps.clear()


def register():
    bpy.utils.register_module(__name__)
    # hotkey setup
    add_hotkey()

def unregister():
    # hotkey cleanup
    remove_hotkey()

    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()