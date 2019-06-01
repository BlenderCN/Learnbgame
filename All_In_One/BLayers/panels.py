import bpy
from . import utils
from .utils import source_layers,sort_layer





class RigLayerPanel(bpy.types.Panel) :
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Rig Layers"

    @classmethod
    def poll(self,context) :
        ob = context.object
        return ob and ob.type == 'ARMATURE' and len(ob.data.BLayers.layers)


    @staticmethod
    def draw_header(self, context):
        scene = context.scene
        ob = context.object
        if not context.object.data.library :
            self.layout.prop(scene.BLayers, "layers_settings", text="",icon ='SCRIPTWIN' )

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        ob = context.object
        settings = scene.BLayers

        BLayers = ob.data.BLayers

        if settings.layers_settings :
            layout.operator('blayers.add_layer_to_panel',text = 'Add Layers',icon='ZOOMIN')
            #layout.operator('blayers.layer_preset',text = 'Basic').preset = 'BASIC'
            #layout.operator('blayers.layer_preset',text = 'Complet').preset = 'COMPLET'
            row = layout.row(align = True)
            row.operator('blayers.move_rig_layers',icon = 'TRIA_DOWN',text='').operation ='DOWN'
            row.operator('blayers.move_rig_layers',icon = 'TRIA_UP',text='').operation ='UP'
            row.label('')
            row.operator('blayers.move_rig_layers',icon = 'TRIA_DOWN_BAR',text='').operation ='MERGE'
            row.operator('blayers.move_rig_layers',icon = 'TRIA_UP_BAR',text='').operation ='EXTRACT'

            row.separator()
            row.operator('blayers.layer_separator',icon = 'GRIP',text='').operation ='ADD'
            row.operator('blayers.layer_separator',icon = 'PANEL_CLOSE',text='').operation ='REMOVE'

            row.label('')
            row.operator('blayers.move_rig_layers',icon = 'TRIA_LEFT',text='').operation ='LEFT'
            row.operator('blayers.move_rig_layers',icon = 'TRIA_RIGHT',text='').operation ='RIGHT'


        visible_layer = [l for l in BLayers.layers if l.UI_visible]

        col = layout.column(align = True)
        for col_index in sort_layer(visible_layer) :
            col_separator = False
            row = col.row(align = True)
            for l in col_index :
                if l.v_separator :
                    col_separator = True

                if settings.layers_settings and not ob.data.library :
                    row.prop(l,"move",toggle = True,text = l.name)

                else :
                    row.prop(ob.data,"layers",index = l.index,toggle = True,text = l.name)

            if col_separator :
                col.separator()

        row = layout.row(align=True)
        if BLayers.get("presets") :
            for preset in sorted(BLayers["presets"]):
                apply_preset = row.operator('blayers.layer_preset_management',text=preset)
                apply_preset.operation = 'APPLY'
                apply_preset.preset = preset

                if settings.layers_settings :
                    remove = row.operator('blayers.layer_preset_management',icon='ZOOMOUT',text='')
                    remove.operation = 'REMOVE'
                    remove.preset = preset

        if settings.layers_settings :
            row.operator('blayers.layer_preset_management',icon='ZOOMIN',text='').operation = 'ADD'


class CustomizeUIPrefs(bpy.types.AddonPreferences):
    bl_idname = 'BLayers'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator('blayers.change_shorcut')


def object_group_draw(self, context):
    layout = self.layout
    scene = context.scene
    #BLayersSettings = scene.BLayersSettings
    layers = [l for l in scene.BLayers.layers if l.type == 'LAYER']

    obj = context.object

    row = layout.row(align=True)
    if bpy.data.groups:
        row.operator("object.group_link", text="Add to Group")
    else:
        row.operator("object.group_add", text="Add to Group")
    row.operator("object.group_add", text="", icon='ZOOMIN')

    obj_name = obj.name
    for group in bpy.data.groups:
        # XXX this is slow and stupid!, we need 2 checks, one thats fast
        # and another that we can be sure its not a name collision
        # from linked library data
        group_objects = group.objects
        if obj_name in group.objects and obj in group_objects[:]:
            col = layout.column(align=True)

            col.context_pointer_set("group", group)

            row = col.box().row()
            row.prop(group, "name", text="")
            row.operator("object.group_remove", text="", icon='X', emboss=False)
            row.menu("GROUP_MT_specials", icon='DOWNARROW_HLT', text="")

            split = col.box().split()

            col = split.column(align = True)
            for layer in layers :
                col.prop(group,'layers',index = layer.index,toggle = True,text = layer.name)
            #col.prop(group, "layers", text="Dupli Visibility")

            col = split.column()
            col.prop(group, "dupli_offset", text="")


def object_relation_draw(self, context):
    layout = self.layout
    scene = context.scene
    #BLayers = scene.BLayers
    layers = [l for l in scene.BLayers.layers if l.type == 'LAYER']
    ob = context.object

    split = layout.split()

    #col = split.column()
    #col.prop(ob, "layers")
    #col.label('Layer : ')
    #for layer in layers :
    #    col.prop(ob,'layers',index = layer.index,toggle = True,text = layer.name)

    #col = layout.column()
    col = split.column()
    col.label(text="Parent:")
    col.prop(ob, "parent", text="")

    sub = col.column()
    sub.prop(ob, "parent_type", text="")
    parent = ob.parent
    if parent and ob.parent_type == 'BONE' and parent.type == 'ARMATURE':
        sub.prop_search(ob, "parent_bone", parent.data, "bones", text="")
    sub.active = (parent is not None)

    col.prop(ob, "pass_index")

    col = split.column()
    if context.scene.render.engine != 'BLENDER_GAME':
        col.label(text="Tracking Axes:")
        col.prop(ob, "track_axis", text="Axis")
        col.prop(ob, "up_axis", text="Up Axis")


    col.prop(ob, "use_slow_parent")
    row = col.row()
    row.active = ((ob.parent is not None) and (ob.use_slow_parent))
    row.prop(ob, "slow_parent_offset", text="Offset")

    col.prop(ob, "use_extra_recalc_object")
    col.prop(ob, "use_extra_recalc_data")

def render_layer_draw(self, context):
    layout = self.layout
    #main_col = layout.column(align = True)
    scene = context.scene
    BLayers = scene.BLayers
    rd = scene.render
    rl = rd.layers.active

    if BLayers.layers :
        layers = [l for l in scene.BLayers.layers if l.type == 'LAYER']
        row = layout.row()

        col = row.column(align = True)
        col.label('Layer : ')
        for layer in layers :
            col.prop(scene.render.layers.active,'layers',index = layer.index,toggle = True,text = layer.name)

        col = row.column(align = True)
        col.label('Mask Layer: ')
        for layer in layers :
            col.prop(context.scene.render.layers.active,'layers_zmask',index = layer.index,toggle = True,text = layer.name)

        col = row.column(align = True)
        col.label('Exclude : ')
        for layer in layers :
            col.prop(context.scene.render.layers.active,'layers_exclude',index = layer.index,toggle = True,text = layer.name)

        #split = layout.split()
        layout.separator()
    #col = split.column()
    #col.prop(scene, "layers", text="Scene")
    #col.prop(rl, "layers_exclude", text="Exclude")

    #col = split.column()

    split = layout.split()

    col = split.column()
    col.label(text="Material:")
    col.prop(rl, "material_override", text="")
    col.separator()
    col.prop(rl, "samples")

    col = split.column()
    col.prop(rl, "use_sky", "Use Environment")
    col.prop(rl, "use_ao", "Use AO")
    col.prop(rl, "use_solid", "Use Surfaces")
    col.prop(rl, "use_strand", "Use Hair")

class BLayerTypeMenu(bpy.types.Menu):
    """Add Group or Layer"""
    bl_label = "Choose Layer type"

    def draw(self, context):
        layout = self.layout
        layout.operator("blayers.add_layer", icon='NEW',text = 'Add layer').type = 'LAYER'
        icon = utils.custom_icons["NEW_LAYER_OBJECT"].icon_id
        layout.operator("blayers.add_layer", icon_value=icon,text = 'Add layer from object').type = 'LAYER_FROM_SELECTED'
        layout.operator("blayers.add_layer", icon='NEWFOLDER',text = 'Add Group').type = 'GROUP'

class BLayerSpecialMenu(bpy.types.Menu):
    """Special Menu"""
    bl_label = "Special Layer menu"

    def draw(self, context):
        layout = self.layout
        #layout.operator("blayers.select_objects", icon='RESTRICT_SELECT_OFF', text="Select Objects")
        layout.operator("blayers.synchronise_layers", icon='FILE_REFRESH', text="Synchronise Layers")
        layout.prop(context.scene.BLayers,'show_index')

        layout.operator("blayers.copy_layers", icon='COPYDOWN', text="Copy Layers")
        layout.operator("blayers.paste_layers", icon='PASTEDOWN', text="Paste Layers")

        layout.separator()
        layout.operator("blayers.objects_to_layer", icon='HAND', text="Move to Layers")



class BLayersList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        ob = context.object
        scene = context.scene

        layers_from,BLayers,BLayersSettings,layers,objects,selected = source_layers()
        active_ob = objects.active

        view_3d = context.area.spaces.active  # Ensured it is a 'VIEW_3D' in panel's poll(), weak... :/
        use_spacecheck = False if view_3d.lock_camera_and_layers else True

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            if item.lock :
                row.active = False
            else :
                row.active = True

            if item.type == 'GROUP' :
                visibility_icon = 'VISIBLE_IPO_ON' if item.visibility else 'VISIBLE_IPO_OFF'
                expand_icon = utils.custom_icons["GROUP_OPEN"].icon_id if item.expand else utils.custom_icons["GROUP_CLOSED"].icon_id
                row.prop(item,'visibility',icon =visibility_icon ,text='', emboss=False)
                row.prop(item,'expand',icon_value =expand_icon ,text='', emboss=False)
                row.prop(item, "name", text="", emboss=False )
                row.separator()
                row.operator("blayers.move_in_group",icon_value =utils.custom_icons["IN_GROUP"].icon_id ,text='',emboss= False).index = index

                icon = "LOCKED" if item.lock_group else "UNLOCKED"
                op = row.prop(item,"lock_group", text="", emboss=False, icon=icon)

                if layers_from == bpy.context.scene :
                    render_icon =  'RESTRICT_RENDER_ON' if item.hide_group_render else  'RESTRICT_RENDER_OFF'
                    row.prop(item,'hide_group_render',icon =render_icon ,text='', emboss=False)

            else : #item type = LAYER
                layer_used_icon = 'BLANK1'
                layer_on = layers_from.layers[item.index]
                active_ob_on_layer = active_ob and active_ob.layers[item.index]
                ob_on_layer = [o for o in objects if o.layers[item.index]]



                icon = 'RESTRICT_VIEW_OFF' if layer_on else 'RESTRICT_VIEW_ON'
                row.prop(layers_from,"layers",index = item.index, text="", emboss=False, icon=icon)

                if item.id in [l.id for l in BLayers if l.type == 'GROUP'] :
                    row.label(icon_value=utils.custom_icons["GROUP_TREE"].icon_id)

                row.prop(item, "name", text="", emboss=False)

                if active_ob_on_layer :
                    row.label(icon='LAYER_ACTIVE')

                elif ob_on_layer:
                    row.label(icon='LAYER_USED')

                icon = "LOCKED" if item.lock else "UNLOCKED"
                op = row.prop(item,"lock", text="", emboss=False, icon=icon)

                if layers_from == bpy.context.scene :
                    render_icon =  'RESTRICT_RENDER_ON' if item.hide_render else  'RESTRICT_RENDER_OFF'
                    row.prop(item,'hide_render',icon =render_icon ,text='', emboss=False)
                else :
                    pass
                    #row.operator("blayers.objects_to_layer",icon = 'BONE_DATA',text='',emboss=False).layer_index = item.index

            if scene.BLayers.show_index :
                row.prop(item,"index",text = '')


        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'

    def filter_items(self, context, data, propname):
        scene = context.scene
        ob = context.object

        layers_from,BLayers,BLayersSettings,layers,objects,selected = source_layers()

        layers = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list

        # Default return values.
        flt_flags = []
        flt_neworder = []

        # Filtering by name
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(self.filter_name, self.bitflag_filter_item, layers, "name",
                                                          reverse=self.use_filter_name_reverse)
        if not flt_flags:
            flt_flags = [self.bitflag_filter_item] * len(layers)

        #flt_flags = []
        for i,layer in enumerate(layers):
            groups = [l for l in BLayers if l.type=='GROUP' and l.id == layer.id]
            if layer.type == 'LAYER' and groups and not groups[0].expand:
                flt_flags[i] = 0
            #else :
            #    flt_flags.append(self.bitflag_filter_item)
        # Reorder by name or average weight.
        if self.use_filter_sort_alpha:
            flt_neworder = helper_funcs.sort_items_by_name(layers, "name")


        #return flt_flags, flt_neworder
        return flt_flags,[]



class LayerPanel(bpy.types.Panel) :
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Layer Management"
    bl_category = "Layers"

    @staticmethod
    def draw(self, context):
        layout = self.layout

        ob = context.object
        scene = context.scene
        layers_from,BLayers,BLayersSettings,layers,objects,selected = source_layers()

        main_row = layout.row()
        #box_row = box.row(align = True)
        left_col = main_row.column(align = True)
        right_col = main_row.column(align= True)

        #col = row.column(align = False)
        layer_type_row = left_col.row(align=True)
        layer_type_row.prop(scene.BLayers,'layer_type',expand = True)

        layer_type_row.separator()
        layer_type_row.label("")

        layer_type_row.operator("blayers.select_objects", icon='RESTRICT_SELECT_OFF', text="",emboss= False)
        layer_type_row.operator("blayers.toogle_layer_hide", icon='RESTRICT_VIEW_OFF', text="",emboss= False)
        layer_type_row.operator("blayers.toogle_layer", icon='LOCKED', text="",emboss= False).prop = 'lock'

        if layers_from == bpy.context.scene :
            layer_type_row.operator("blayers.toogle_layer", icon='RESTRICT_RENDER_OFF', text="",emboss= False).prop = 'hide_render'



        if BLayers  :
            left_col.template_list("BLayersList", "", BLayersSettings, "layers", BLayersSettings, "active_index", rows=6)
        else :
            left_col.operator("blayers.synchronise_layers", icon='FILE_REFRESH', text="Synchronise Layers")

        for i in range(4) :
            right_col.separator()

        right_col.menu("BLayerTypeMenu", icon="ZOOMIN", text="")
        bin_icon = utils.custom_icons["BIN"].icon_id
        right_col.operator("blayers.remove_layer", icon_value =bin_icon, text="")
        right_col.separator()
        right_col.operator("blayers.layer_move", icon='TRIA_UP', text="").step = -1
        right_col.operator("blayers.layer_move", icon='TRIA_DOWN', text="").step = 1


        right_col.separator()
        right_col.menu("BLayerSpecialMenu", icon="DOWNARROW_HLT", text="")
        right_col.separator()
        if BLayers and BLayersSettings.active_index !=-1:
            right_col.operator("blayers.objects_to_layer", icon='HAND', text="").layer_index = BLayers[BLayersSettings.active_index].index
