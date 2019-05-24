bl_info = {
    "name": "BLayers",
    "author": "Christophe Seux",
    "version": (0, 1),
    "blender": (2, 78, 0),
    "category": "Learnbgame",
}

if "bpy" in locals():
    import imp
    imp.reload(properties)
    imp.reload(operators)
    imp.reload(panels)
    imp.reload(utils)
    imp.reload(functions)

else :
    from . import properties
    from . import operators
    from . import panels
    from . import utils
    from . import functions

import os
import bpy
from bpy.app.handlers import persistent


custom_icons = None

addon_keymaps = []


def register():
    utils.get_icons()

    #bpy.app.handlers.load_post.append(change_key_map)
    bpy.utils.register_module(__name__)
    bpy.types.Scene.BLayers = bpy.props.PointerProperty(type = properties.BLayersScene)
    #bpy.types.Scene.BLayers = bpy.props.CollectionProperty(type = properties.LayersSettings)

    bpy.types.Armature.BLayers = bpy.props.PointerProperty(type = properties.BLayersArmature)
    #bpy.types.Armature.BLayers = bpy.props.CollectionProperty(type = properties.LayersSettings)

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi = km.keymap_items.new('blayers.objects_to_layer', 'M', 'PRESS')
    addon_keymaps.append((km, kmi))

    register.render_pass_class =[a for a in bpy.types.Panel.__subclasses__() if a.__name__ == 'CyclesRender_PT_layer_options'][0]
    register.object_relation_class =[a for a in bpy.types.Panel.__subclasses__() if a.__name__ == 'OBJECT_PT_relations'][0]
    register.object_group_class =[a for a in bpy.types.Panel.__subclasses__() if a.__name__ == 'OBJECT_PT_groups'][0]

    register.relations_extras =[a for a in bpy.types.Panel.__subclasses__() if a.__name__ == 'OBJECT_PT_relations_extras'][0]
    #unregister render layer panel
    register.old_render_pass = register.render_pass_class.draw
    register.render_pass_class.draw = panels.render_layer_draw

    #unregister render layer panel
    register.old_object_relation = register.object_relation_class.draw
    register.object_relation_class.draw = panels.object_relation_draw

    #unregister render layer panel
    register.old_object_group = register.object_group_class.draw
    register.object_group_class.draw = panels.object_group_draw

    #unregister relations_extras
    bpy.utils.unregister_class(register.relations_extras)

def unregister():
    wm = bpy.context.window_manager
    keyconfig = wm.keyconfigs.user.keymaps.get('Object Mode')
    #print('check')
    if keyconfig and keyconfig.keymap_items.get('object.move_to_layer'):
        move_to_layer = keyconfig.keymap_items.get('object.move_to_layer')
        move_to_layer.active = True

    bpy.utils.previews.remove(utils.custom_icons)
    register.render_pass_class.draw = register.old_render_pass
    register.object_relation_class.draw = register.old_object_relation
    register.object_group_class.draw = register.old_object_group

    bpy.utils.register_class(register.relations_extras)

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


    #bpy.app.handlers.load_post.remove(change_key_map)
    del bpy.types.Scene.BLayers
    del bpy.types.Armature.BLayers


    bpy.utils.unregister_module(__name__)
