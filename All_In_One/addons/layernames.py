# Layer Names makes a nice layer manager for Tube
# Copyright (C) 2012  Bassam Kurdali
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301, USA.
bl_info = {
    "name": "Layer Names",
    "author": "Bassam Kurdali, Pablo Vazquez",
    "version": (2, 7),
    "blender": (2, 6, 9),
    "location": "View3D > Header",
    "description": "Layers for Empathy",
    "warning": "",
    "wiki_url": "http://wiki.urchn.org/wiki/Layer_names",
    "tracker_url": "",
    "category": "Learnbgame",
}

import bpy
import re

icons = [
    ("DOT", "None", "Not any type of layer in particular"),
    ("MONKEY", "Character", "Layer containing character models"),
    ("WORLD", "Environment", "Layer containing environment models"),
    ("POSE_HLT", "Rigs", "Layer containing rigging objects"),
    ("LAMP_SUN", "Lighting", "Layer containing lighting objects"),
    ("CAMERA_DATA", "Cameras", "Layer containing cameras"),
    ("SOLO_ON", "Extras", "Layer with extra objects"),
    ("RESTRICT_RENDER_ON", "Don't Render", "Layer to skip rendering")]

rig_icons = [
    ("DOT", "None", "Not any type of layer in particular"),
    ("OUTLINER_DATA_ARMATURE", "Controls", "Layer containing Controls"),
    ("UI", "Properties", "Layer containing Property Holders"),
    ("ARMATURE_DATA", "Geometry", "Layer containing Geo bones")]


class LayerNamesPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    map_string = bpy.props.StringProperty(default="maps")
    low_string = bpy.props.StringProperty(default="maps_low")
    
    def draw(self, context):
        layout = self.layout
        layout.label("Don't type full paths or seperators, just what to swap:")
        layout.prop(self, "map_string", text="Normal Resolution Subfolder")
        layout.prop(self, "low_string", text="Low Resolution Subfolder")


def get_xor(count):
    def retfunc(self):
        ''' get or init the exlusive value of a bool array'''
        try:
            self['old_value']
        except KeyError:
            self['old_value'] = [False] * count
        return self['old_value']
    return retfunc


def set_xor(self, new_value):
    ''' Set an exlusive value to a bool array '''
    self['old_value'] = [a != b for a, b in zip(self['old_value'], new_value)]    


def layer_index(self):
    ''' compatibility function for old style version with int index '''
    try:
        self_index = list(self.vector).index(True)
        return self_index
    except ValueError:
        self.vector[self.index] = True
        return self.index


class LayerParameters(bpy.types.PropertyGroup):
    ''' Advanced Layer Parameters '''
    index = bpy.props.IntProperty(min=0, max=20,  # compatibility only
        default=0, name="Layer Number",
        description="Layer Number")
    type = bpy.props.EnumProperty(
        name="Layer Type",
        description="Layer Type",
        items=icons,
        default='DOT')
    flag = bpy.props.BoolProperty(default=False, name="")
    vector = bpy.props.BoolVectorProperty(
        size=20, subtype='LAYER',
        get=get_xor(20), set=set_xor,
        description="Layer List",
        name="Layer List")
    layer_index = layer_index


class ArmatureLayerParameters(bpy.types.PropertyGroup):
    ''' Armature Layer Parameters '''
    index = bpy.props.IntProperty(min=0, max=32,  #compatibility only
        default=0, name="Layer Number",
        description="Layer Number")
    type = bpy.props.EnumProperty(
        name="Layer Type",
        description="Layer Type",
        items=rig_icons,
        default='DOT')
    flag = bpy.props.BoolProperty(default=False, name="")
    vector = bpy.props.BoolVectorProperty(
        size=32, subtype='LAYER',
        get=get_xor(32), set=set_xor,
        description="Layer List",
        name="Layer List")
    layer_index = layer_index


class OperatorParameters(bpy.types.PropertyGroup):
    ''' Operator Layer Parameters, not exclusive '''
    index = bpy.props.IntProperty(min=0, max=32,  #compatibility only
        default=0, name="Layer Number",
        description="Layer Number")
    type = bpy.props.EnumProperty(
        name="Layer Type",
        description="Layer Type",
        items=rig_icons + icons,
        default='DOT')
    flag = bpy.props.BoolProperty(default=False, name="")

    
class SceneRenderLayerBackup(bpy.types.PropertyGroup):
    ''' Backup of renderlayer state '''
    use = bpy.props.BoolProperty()


def check_renderlayer_backup(scene):
    ''' return true if backup is good '''
    backup = scene.renderlayers_backup
    current = scene.render.layers
    # first check if all our renderlayers are there
    for layer in current:
        if layer.name not in backup or layer.use != backup[layer.name].use:
            return False
    # now make sure we have no extra layers in backup
    for layer in backup:
        if layer.name not in current:
            return False
    return True


def make_renderlayer_backup(scene):
    ''' backup scene render layers into backup '''
    backup = scene.renderlayers_backup
    current = scene.render.layers
    # first clear the backup
    while len(backup) > 0:
        backup.remove(0)
    # now save into it
    for layer in current:
        backed_layer = backup.add()
        backed_layer.name = layer.name
        backed_layer.use = layer.use


def restore_renderlayer_backup(scene):
    ''' restore a backup to the current renderlayer setup '''
    backup = scene.renderlayers_backup
    current = scene.render.layers
    deleted_layers = []
    unsaved_layers = [
        layer.name for layer in current if not layer.name in backup]
    missing_layers = ''
    if unsaved_layers:
        error_msg = 'Unsaved Layers: {}'.format(','.join(unsaved_layers))
    else:
        error_msg = ''
    for layer in backup:
        try:
            current[layer.name].use = layer.use
        except KeyError:
            missing_layers.append(layer.name)
    if missing_layers:
        error_msg = '{}, Deleted layers: {} '.format(
            error_msg, ','.join(deleted_layers))
    if error_msg:
        return error_msg


class SCENE_OT_save_render_state(bpy.types.Operator):
    ''' used to avoid missing layers on render'''
    bl_idname = 'scene.save_render_state'
    bl_label = 'save render state'

    @classmethod
    def poll(cls, context):
        for scene in bpy.data.scenes:
            if not scene.state_of_render:
                return True
            if scene.scene_to_render != (context.scene == scene):
                return True
            if list(scene.layers_to_render) != list(scene.layers):
                return True
            if not check_renderlayer_backup(scene):
                return True
        return False
    
    def execute(self, context):
        for scene in bpy.data.scenes:
            scene.state_of_render = False # dirty unless successful
            scene.scene_to_render = scene == context.scene
            scene.layers_to_render = list(scene.layers)
            make_renderlayer_backup(scene)
            scene.state_of_render = True
        return {'FINISHED'}


class SCENE_OT_restore_render_state(bpy.types.Operator):
    ''' used to avoid missing layers on render'''
    bl_idname = 'scene.restore_render_state'
    bl_label = 'restore render state'
    
    @classmethod
    def poll(cls, context):
        for scene in bpy.data.scenes:
            if not scene.state_of_render:
                return False
        for scene in bpy.data.scenes:
            if scene.scene_to_render != (context.scene == scene):
                return True
            if list(scene.layers_to_render) != list(scene.layers):
                return True
            if not check_renderlayer_backup(scene):
                return True
        return False

    def execute(self, context):
        for scene in bpy.data.scenes:
            scene.layers = list(scene.layers_to_render)
            error = restore_renderlayer_backup(scene)
            if error:
                print(error)
            if scene.scene_to_render:
                context.screen.scene = scene
            scene.state_of_render = True
        return {'FINISHED'}


class SCENE_OT_active_to_mask(bpy.types.Operator):
    ''' add/del active scene layer to active renderlayer mask layers'''
    bl_idname = 'scene.active_mask'
    bl_label = 'add/del layer to render mask'
    
    def execute(self, context):
        scene = context.scene
        rl = scene.render.layers.active
        al = scene.layer_names[scene.active_layer_name].layer_index()
        rl.layers_zmask[al] = not rl.layers_zmask[al]
        return {'FINISHED'}


class SCENE_OT_active_to_exclude(bpy.types.Operator):
    ''' add/del active scene layer to active renderlayer mask layers'''
    bl_idname = 'scene.active_exclude'
    bl_label = 'add/del layer to render exclude'
    
    def execute(self, context):
        scene = context.scene
        rl = scene.render.layers.active
        al = scene.layer_names[scene.active_layer_name].layer_index()
        rl.layers_exclude[al] = not rl.layers_exclude[al]
        return {'FINISHED'}



class SCENE_OT_active_to_renderlayers(bpy.types.Operator):
    ''' add/del active scene layer to active renderlayer mask layers'''
    bl_idname = 'scene.active_renderlayers'
    bl_label = 'add/del layer to render layer'
    
    def execute(self, context):
        scene = context.scene
        rl = scene.render.layers.active
        al = scene.layer_names[scene.active_layer_name].layer_index()
        rl.layers[al] = not rl.layers[al]
        return {'FINISHED'}


def add_named_layer(self, item):
    ''' add a name for a given layer '''
    layer_name = self.properties.layer_name
    layer_type = self.properties.layer_type
    a = item.layer_names.add()
    try:
        layer_idx = list(self.properties.layer_idx).index(True)
        a.vector[layer_idx] = True
        a.index = layer_idx
    except ValueError:
        pass
    a.name = layer_name
    a.type = layer_type


class SCENE_OT_add_named_layer(bpy.types.Operator):
    '''Add a named Layer to the Scene'''
    bl_idname = "scene.add_named_layer"
    bl_label = "Add Named Layer"
    layer_name = bpy.props.StringProperty(default="Default", name="Name")
    layer_type = bpy.props.EnumProperty(
        name="Type",
        description="Layer Type",
        items=icons,
        default='DOT')
    layer_idx = bpy.props.BoolVectorProperty(
        size=20, subtype='LAYER',
        get=get_xor(20), set=set_xor,
        name="Number")

    def invoke(self, context, event):
        self.properties.layer_idx[context.scene.active_layer] = True
        context.window_manager.invoke_props_dialog(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        print('here')
        add_named_layer(self, context.scene)
        return {'FINISHED'}

    def draw(self, context):
        props = self.properties
        layout = self.layout
        row = layout.row()
        row.prop(props, "layer_name")
        row.prop(props, "layer_type")
        row = layout.row()
        row.prop(props, "layer_idx")



class ARMATURE_OT_add_named_layer(bpy.types.Operator):
    bl_idname = "armature.add_named_layer"
    bl_label = "Add Named Layer"
    layer_name = bpy.props.StringProperty(default="Default", name="Name")
    layer_type = bpy.props.EnumProperty(
        name="Type",
        description="Layer Type",
        items=rig_icons,
        default='DOT')
    layer_idx = bpy.props.BoolVectorProperty(
        size=32, subtype='LAYER',
        get=get_xor(32), set=set_xor,
        name="Number")

    def invoke(self, context, event):
        context.window_manager.invoke_props_dialog(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        add_named_layer(self, context.active_object.data)
        return {'FINISHED'}

    def draw(self, context):
        props = self.properties
        layout = self.layout
        row = layout.row()
        row.prop(props, "layer_name")
        row.prop(props, "layer_type")
        row = layout.row()
        row.prop(props, "layer_idx")

class SCENE_OT_del_named_layer(bpy.types.Operator):
    '''Delete a named Layer from the Scene'''
    bl_idname = "scene.del_named_layer"
    bl_label = "Delete Named Layer"

    name_index = bpy.props.IntProperty(default=0)

    def execute(self, context):
        context.scene.layer_names.remove(self.name_index)
        return {'FINISHED'}


class ARMATURE_OT_del_named_layer(bpy.types.Operator):
    bl_idname = "armature.del_named_layer"
    bl_label = "Delete Named Layer"

    name_index = bpy.props.IntProperty(default=0)

    def execute(self, context):
        context.active_object.data.layer_names.remove(self.name_index)
        return {'FINISHED'}


def delete_all_layers(item):
    ''' delete all named layers in an item '''
    while len(item.layer_names) > 0:
        item.layer_names.remove(0)


class SCENE_OT_del_all_layers(bpy.types.Operator):
    '''Delete all namedLayer from the Scene'''
    bl_idname = "scene.del_all_layers"
    bl_label = "Delete All Named Layers"

    def execute(self, context):
        delete_all_layers(context.scene)
        return {'FINISHED'}


class ARMATURE_OT_del_all_layers(bpy.types.Operator):
    bl_idname = "armature.del_all_layers"
    bl_label = "Delete All Named Layers"

    def execute(self, context):
        delete_all_layers(context.active_object.data)
        return {'FINISHED'}


def swap_layers(self, item):
    '''Swap two things on a thing '''
    name_index = item.active_layer_name
    lower = self.properties.lower


    layers = [
        (layer.name, layer.type, layer.layer_index())
        for layer in item.layer_names]
    other = name_index + 1 if lower else name_index - 1
    if other < 0 or other >= len(item.layer_names):
        return {'FINISHED'}
    else:
        layers[name_index], layers[other] =\
            layers[other], layers[name_index]
        while len(item.layer_names) > 0:
            item.layer_names.remove(0)
        for layer in layers:
            a = item.layer_names.add()
            a.name = layer[0]
            a.type = layer[1]
            a.vector[layer[2]] = True
        item.active_layer_name = other
        return {'FINISHED'}


class SCENE_OT_swap_layers(bpy.types.Operator):
    '''Swap Layer Order'''
    bl_idname = "scene.swap_layers"
    bl_label = "Swap Scene Layers"
    bl_description = "Move the layer up or down"

    lower = bpy.props.BoolProperty(default=True)
    name_index = bpy.props.IntProperty(default=0)

    def execute(self, context):
        return swap_layers(self, context.scene)


class ARMATURE_OT_swap_layers(bpy.types.Operator):
    bl_idname = "armature.swap_layers"
    bl_label = "Swap Armature Layers"
    bl_description = "Move the layer up or down"

    lower = bpy.props.BoolProperty(default=True)
    name_index = bpy.props.IntProperty(default=0)

    def execute(self, context):
        return swap_layers(self, context.active_object.data)


class SCENE_OT_other_scene_layers(bpy.types.Operator):
    '''Import Named Layers From other scene'''
    bl_idname = "scene.other_scene_layers"
    bl_label = "Import Named Layers From a scene"

    scene_name = bpy.props.StringProperty(
        default="")

    def execute(self, context):
        scene = context.scene
        scene_name = self.properties.scene_name
        other_scene = bpy.data.scenes[scene_name]
        for layer in other_scene.layer_names:
            a = scene.layer_names.add()
            old_idx = layer.layer_index()
            a.name = layer.name
            a.type = layer.type
            a.index = old_idx
            a.vector[old_idx] = True
        return {'FINISHED'}


class SCENE_OT_template_layers_import(bpy.types.Operator):
    '''Import Layers From Template'''
    bl_idname = "scene.template_layers"
    bl_label = "Import Layers From Template"

    file_path = bpy.props.StringProperty(
        default="//__layers", subtype='FILE_PATH')

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        scene = context.scene
        filepath = bpy.path.abspath(self.properties.file_path)
        print(filepath)
        try:
            with open(filepath, "r") as layersfile:
                layersdata = layersfile.read()
        except IOError:
            self.report(type={'ERROR'}, message="File Not Found")
            return {'CANCELLED'}
        layerdict = [
            (pair.partition(':')[0],
                int(pair.partition(':')[2])) for pair in re.split(
                    ",",
                    layersdata) if ':' in pair]
        for layer in layerdict:
            a = scene.layer_names.add()
            a.name = layer[0]
            a.index = layer[1]
            a.vector[layer[1]] = True
        return {'FINISHED'}


class ARMATURE_OT_template_layers_import(bpy.types.Operator):
    '''Import Layers From Template'''
    bl_idname = "armature.template_layers"
    bl_label = "Import Layers From Template"

    file_path = bpy.props.StringProperty(
        default="//__arm_layers", subtype='FILE_PATH')

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        armature = context.active_object.data
        filepath = bpy.path.abspath(self.properties.file_path)
        print(filepath)
        try:
            with open(filepath, "r") as layersfile:
                layersdata = layersfile.read()
        except IOError:
            self.report(type={'ERROR'}, message="File Not Found")
            return {'CANCELLED'}
        layerdict = [
            (pair.partition(':')[0],
                int(pair.partition(':')[2])) for pair in re.split(
                    ",",
                    layersdata) if ':' in pair]
        for layer in layerdict:
            a = armature.layer_names.add()
            a.name = layer[0]
            a.index = layer[1]
            a.vector[layer[1]] = True
        return {'FINISHED'}


class SCENE_OT_template_layers_export(bpy.types.Operator):
    '''Export Named Layers From Template'''
    bl_idname = "scene.template_layers_export"
    bl_label = "Export Named Layers To Template"

    file_path = bpy.props.StringProperty(
        default="//__layers", subtype='FILE_PATH')

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        scene = context.scene
        filepath = bpy.path.abspath(self.properties.file_path)
        print(filepath)
        
        layers = ["{}:{}".format(
            layer.name, layer.index) for layer in scene.layer_names]
        layers_string = ",".join(layers)
        with open(filepath, "w") as layersfile:
            layersfile.write(layers_string)
        return {'FINISHED'}


class ARMATURE_OT_template_layers_export(bpy.types.Operator):
    '''Export Named Layers From Template'''
    bl_idname = "armature.template_layers_export"
    bl_label = "Export Named Layers To Template"

    file_path = bpy.props.StringProperty(
        default="//__arm_layers", subtype='FILE_PATH')

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        armature = context.active_object.data
        filepath = bpy.path.abspath(self.properties.file_path)
        print(filepath)
        layers = ["{}:{}".format(
            layer.name, layer.index) for layer in armature.layer_names]
        layers_string = ",".join(layers)
        with open(filepath, "w") as layersfile:
            layersfile.write(layers_string)
        return {'FINISHED'}


def import_old_layers(item):
    try:
        old_layers = item['__layers']
    except KeyError:
        return {'FINISHED'}
    for layer in old_layers:
        a = item.layer_names.add()
        a.name = layer
        a.type = "DOT"
        a.index = old_layers[layer]
        a.vector[old_layers[layer]] = True
    return {'FINISHED'}


class SCENE_OT_import_old_layers(bpy.types.Operator):
    '''Import Old Skool layer names from the id prop'''
    bl_idname = "scene.import_old_layers"
    bl_label = "Import Old Layers"

    def execute(self, context):
        scene = context.scene
        return import_old_layers(scene)


class ARMATURE_OT_import_old_layers(bpy.types.Operator):
    bl_idname = "armature.import_old_layers"
    bl_label = "Import Old Layers"

    def execute(self, context):
        armature = context.active_object.data
        return import_old_layers(armature)


class OBJECT_OT_change_named_layer(bpy.types.Operator):
    '''Change the layer of the selection'''
    bl_idname = "object.change_named_layer"
    bl_label = "Change Layer"
    self_layers = bpy.props.CollectionProperty(
        type=OperatorParameters)
    is_armature = bpy.props.BoolProperty(default=False)

    def invoke(self, context, event):
        self.properties.self_layers.clear()

        active = context.active_object
        if active.type == 'ARMATURE' and context.mode != 'OBJECT':
            if context.mode == 'POSE':
                select = context.selected_pose_bones
            else:
                select = context.selected_editable_bones
            holder = active.data
            self.properties.is_armature = True
        else:
            select = context.selected_objects
            holder = context.scene
            self.properties.is_armature = False

        for layer in holder.layer_names:
            if self.properties.is_armature:
                a = self.properties.self_layers.add()
                a.index = layer.layer_index()
                a.flag = any(
                    [holder.bones[bone.name].layers[a.index] for
                        bone in select])
            else:
                a = self.properties.self_layers.add()
                a.index = layer.layer_index()
                a.flag = any([ob.layers[a.index] for ob in select])
            a.name = layer.name
            a.type = layer.type

        context.window_manager.invoke_props_dialog(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        active = context.active_object
        layer_count = 20
        if self.properties.is_armature:
            layer_count = 32
            if context.mode == 'POSE':
                selected_bones = context.selected_pose_bones
            else:
                selected_bones = context.selected_editable_bones
            select = [active.data.bones[bone.name] for bone in selected_bones]

        else:
            select = context.selected_objects
        operator_layers = self.properties.self_layers

        layers = [
            idx in [
                layer.index for layer in operator_layers if layer.flag] for
            idx in range(layer_count)]

        for itm in select:
            itm.layers = layers
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layers = self.properties.self_layers
        if self.properties.is_armature:
            if context.mode == 'POSE':
                select = context.selected_pose_bones
            else:
                select = context.selected_editable_bones
            holder = context.active_object.data

        else:
            select = context.selected_objects
            holder = context.scene
        for layer in layers:
            layout.prop(layer, "flag", text=layer.name, icon=layer.type)


def common_items(item, layout):
    ''' common layout for scene/armature menus '''
    layout.operator("{}.del_all_layers".format(item))
    layout.operator("{}.import_old_layers".format(item))
    layout.operator("{}.template_layers".format(item))
    layout.operator("{}.template_layers_export".format(item))

class SCENE_MT_layernames_menu(bpy.types.Menu):
    bl_label = "Scene Layer Names"

    def draw(self, context):
        current_scene = context.scene
        layout = self.layout
        item = "scene"
        common_items(item, layout)
        for scene in bpy.data.scenes:
            if scene != current_scene:
                name = scene.name
                layout.operator(
                    "scene.other_scene_layers",
                    text="import layers from {}".format(
                        name)).scene_name = name



class ARMATURE_MT_layernames_menu(bpy.types.Menu):
    bl_label = "Armature Layer Names"

    def draw(self, context):
        layout = self.layout
        common_items("armature", layout)


def simple_draw(layout, item, active, scene_mode, space=None):
    ''' Layer browser thingie '''

    if item.layer_names:
        col = layout.column()
        for layer in item.layer_names:
            try:
                index = list(layer.vector).index(True)
            except:
                index = layer.index
                layer.vector[index] = True
            has_act = False if not active else active.layers[index]

            row = col.row()

            if space and 'lock_camera_and_layers' in dir(space) and\
                    scene_mode and not space.lock_camera_and_layers:
                layer_holder = space
            else:
                layer_holder = item

            if not space:
                row.label(text="", icon=layer.type)
            row.prop(
                layer_holder, "layers", index=index,
                text="{} * ({})".format(
                    layer.name,
                    active.name) if has_act else layer.name)

            if scene_mode and index == item.active_layer and not space:
                row.label(text="", icon="TRIA_LEFT")
    else:
        layout.separator()
        layout.label(text="No Layers", icon="INFO")


def draw_header(layout, item, menu):
    ''' use this to draw the header menus '''
    layout.prop(
        item, 'use_layers_locked', text="",
        icon='LOCKED' if item.use_layers_locked else 'UNLOCKED',
        emboss=False)
    layout.menu(menu, icon='DOWNARROW_HLT', text=" ")


class NAMED_LAYER_UL_list(bpy.types.UIList):
    sort_on = bpy.props.EnumProperty(
        items =[tuple([a] * 3) for a in ['Default', 'Name', 'Type', 'Layer']],
        name = 'sort_order')
    filter_on = bpy.props.EnumProperty(
        items =[tuple([a] * 3) for a in ['None', 'Layer', 'Exclude', 'Mask']],
        name = 'filter_on')        
    def draw_item(
        self, context, layout, data, item, icon,
        active_data, active_propname, index, flt_flag):
        ''' draw each item '''

        scene = data
        active_object = context.active_object
        named_layer = item
        mapping = named_layer.layer_index()  # force conversion of old layers
        layout = layout.row(align=True)
        layer_icon = "BLANK1"
        if active_object and active_object.layers[mapping]:
            layer_icon = "LAYER_ACTIVE"
        else:
            for ob in scene.objects:
                if ob.layers[mapping]:
                    layer_icon = "LAYER_USED"
                    break
        if scene.use_layers_locked:
            layout.label(text="",icon=named_layer.type)            
            layout.label(text=named_layer.name,icon="BLANK1")
            if mapping == data.active_layer:
                layout.label(text="", icon="TRIA_LEFT")
            layout.prop(
                data, "layers", index=named_layer.layer_index(),
                text="",icon=layer_icon)
            layout.label(text="", icon="BLANK1")
            renderlayer = scene.render.layers.active
            for subprop in (
                    ("layers", 'COLLAPSEMENU'), ("layers_exclude", 'X'),
                    ("layers_zmask", 'GHOST_ENABLED')):
                layout.prop(
                    renderlayer, subprop[0], index=named_layer.layer_index(),
                    text="", icon=subprop[1])
            
        else:
            layout.label(text="",icon=named_layer.type)
            layout.prop(named_layer, "type", text="")
            layout.prop(named_layer, "name", text="")
            layout.prop(
                data, "layers", index=named_layer.layer_index(),
                text="",icon=layer_icon)
            layout.prop(named_layer, "vector", text="")
        

    def draw_filter(self, context, layout):

        scene = context.scene
        active_object = context.active_object
        active_layer = scene.active_layer_name
        try:
            nl = scene.layer_names[active_layer]
        except IndexError:
            nl = None
        rl = context.scene.render.layers.active

        #row = layout.row(align=True)
        split = layout.split(.9,align=True)
        
        col = split.column(align=True)
        row = col.row(align=True)
        row.prop(self, 'filter_on', text="", icon='VIEWZOOM')
        row.prop(self, 'sort_on', text="", icon='SORTALPHA')
        row = col.row(align=True)
        row.operator(
            "scene.add_named_layer", icon='ZOOMIN', text="Create New Layer")
        if nl:
            row.operator(
                "scene.del_named_layer", icon="ZOOMOUT",
                text="Delete Active Layer").name_index = active_layer
            row = col.row(align=True)
            row.operator(
                'scene.active_renderlayers',
                icon='MOD_LATTICE',
                text = 'del layer' if rl.layers[nl.layer_index()]
                    else 'add layer' )
            row.operator(
                'scene.active_exclude',
                icon='MOD_BOOLEAN',
                text = 'del exclude' if rl.layers_exclude[nl.layer_index()]
                    else 'add exclude' )
            row.operator(
                'scene.active_mask',
                icon='MOD_MASK',
                text = 'del mask' if rl.layers_zmask[nl.layer_index()]
                    else 'add mask' )

        col = split.column(align=False)
        #col.operator('scene.add_named_layer', icon='ZOOMIN', text="")
        if nl and self.sort_on == 'Default':
            row = col.row(align=True) 
            up = row.operator(
                'scene.swap_layers', icon='TRIA_UP', text="", emboss=False)
            up.name_index, up.lower = active_layer, False
            row = col.row(align=True)
            down = row.operator(
                'scene.swap_layers', icon='TRIA_DOWN', text="", emboss=False)
            down.name_index, down.lower = active_layer, True        

    def filter_items(self, context, data, propname):
        layer_names = getattr(data, propname)
        rl = context.scene.render.layers.active
        if self.filter_on == 'None':
            flt_flags = []
        else:
            filter_prop = {
                'Layer': 'layers',
                'Exclude': 'layers_exclude',
                'Mask': 'layers_zmask'}[self.filter_on]
            filter_list = getattr(rl, filter_prop)
            flt_flags = [
                (0, self.bitflag_filter_item)[filter_list[i.layer_index()]]
                for i in layer_names]
        if self.sort_on == 'Default':
            flt_neworder = []
        else:
            _sort= [(index, l) for index, l in enumerate(layer_names)]
            key = {
                'Layer':lambda x:x[1].layer_index(),
                'Name':lambda x:x[1].name.lower(),
                'Type':lambda x:x[1].type}[self.sort_on]
            #_sort.sort(key=key)
            
            #flt_neworder = [itm[0] for itm in _sort]

            flt_neworder = bpy.types.UI_UL_list.sort_items_helper(
                _sort, key, False)
            #print(flt_neworder)
            #flt_neworder = [i for i in range(len(layer_names))]
            #flt_neworder.sort(reverse=True)
        return flt_flags, flt_neworder 
 

def draw_panel(layout, item, active, swap, delete, add):
    ''' use this to draw the panel body '''
    row = layout.row(align=True)
    col = row.column(align=True)
    if item.use_layers_locked:

        simple_draw(col, item, active, type(item) == bpy.types.Scene)

    else:
        for name_index, layer in enumerate(item.layer_names):
            layer_type = layer.type
            realrow = col.row(align=True)
            boxrow = realrow.box()
            row=boxrow.row(align=True)
            subcol=row.column(align=True)
            subcol.prop(layer, "name", text="", emboss=False)
            subcol = row.column(align=True)
            subcol.prop(layer, "vector", text="")
            subcol=row.column(align=True)
            subrow = subcol.row(align=True)
            subrow.prop(layer, "type", text="", icon=layer_type)
            subrow.prop(item, "layers", index=layer.layer_index(), text="")
            up = subrow.operator(swap, icon='MOVE_UP_VEC', text="")
            up.name_index, up.lower = name_index, False
            down = subrow.operator(swap, icon='MOVE_DOWN_VEC', text="")
            down.name_index, down.lower = name_index, True
            subrow.operator(delete, icon='X', text="").name_index = name_index
        layout.operator(add, icon='ZOOMIN', text="Create New Layer")



class ARMATURE_LAYER_UL_list(bpy.types.UIList):
    sort_on = bpy.props.EnumProperty(
        items =[tuple([a] * 3) for a in ['Default', 'Name', 'Type', 'Layer']],
        name = 'sort_order')
   
    def draw_item(
        self, context, layout, data, item, icon,
        active_data, active_propname, index, flt_flag):
        ''' draw each item '''
        armature = data
        active_bone = context.active_bone
        named_layer = item
        mapping = named_layer.layer_index()  # force conversion of old layers
        layout = layout.row(align=True)
        layer_icon = "BLANK1"
        if active_bone and active_bone.layers[mapping]:
            layer_icon = "LAYER_ACTIVE"
        else:
            for bone in armature.bones:
                if bone.layers[mapping]:
                    layer_icon = "LAYER_USED"
                    break
        if armature.use_layers_locked:
            layout.label(text="",icon=named_layer.type)            
            layout.label(text=named_layer.name,icon="BLANK1")
            layout.prop(
                data, "layers", index=named_layer.layer_index(),
                text="",icon=layer_icon)
        else:
            layout.label(text="",icon=named_layer.type)
            layout.prop(named_layer, "type", text="")
            layout.prop(named_layer, "name", text="")
            layout.prop(
                data, "layers", index=named_layer.layer_index(),
                text="",icon=layer_icon)
            layout.prop(named_layer, "vector", text="")

    def draw_filter(self, context, layout):

        armature = context.object.data
        active_bone = context.active_bone
        active_layer = armature.active_layer_name
        try:
            nl = armature.layer_names[active_layer]
        except IndexError:
            nl = None
        #row = layout.row(align=True)
        split = layout.split(.9,align=True)
        
        col = split.column(align=True)
        row = col.row(align=True)

        row.prop(self, 'sort_on', text="", icon='SORTALPHA')
        row = col.row(align=True)
        row.operator(
            "armature.add_named_layer", icon='ZOOMIN', text="Create New Layer")
        if nl:
            row.operator(
                "armature.del_named_layer", icon="ZOOMOUT",
                text="Delete Active Layer").name_index = active_layer


        col = split.column(align=False)
        if nl and self.sort_on == 'Default':
            row = col.row(align=True) 
            up = row.operator(
                'armature.swap_layers', icon='TRIA_UP', text="", emboss=False)
            up.name_index, up.lower = active_layer, False
            row = col.row(align=True)
            down = row.operator(
                'armature.swap_layers', icon='TRIA_DOWN', text="", emboss=False)
            down.name_index, down.lower = active_layer, True        

    def filter_items(self, context, data, propname):
        layer_names = getattr(data, propname)
        flt_flags =[]
        if self.sort_on == 'Default':
            flt_neworder = []
        else:
            _sort= [(index, l) for index, l in enumerate(layer_names)]
            key = {
                'Layer':lambda x:x[1].layer_index(),
                'Name':lambda x:x[1].name.lower(),
                'Type':lambda x:x[1].type}[self.sort_on]
            #_sort.sort(key=key)
            
            #flt_neworder = [itm[0] for itm in _sort]

            flt_neworder = bpy.types.UI_UL_list.sort_items_helper(
                _sort, key, False)
            #print(flt_neworder)
            #flt_neworder = [i for i in range(len(layer_names))]
            #flt_neworder.sort(reverse=True)
        return flt_flags, flt_neworder


class ArmatureLayerNames(bpy.types.Panel):
    '''Armature Layers'''
    bl_label = 'Armature Layers'
    bl_idname = 'ARMATURE_PT_layers'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'data'

    @classmethod
    def poll(cls, context):
        act = context.active_object
        return act is not None and act.type == 'ARMATURE'

    def draw_header(self, context):
        layout = self.layout
        armature = context.active_object.data
        draw_header(layout, armature, "ARMATURE_MT_layernames_menu")

    def draw(self, context):
        layout = self.layout
        ob = context.active_object
        armature = ob.data
        active = context.active_bone


        row = layout.row()
        row.template_list(
            "ARMATURE_LAYER_UL_list", "", armature, 
            "layer_names", armature, "active_layer_name", type ="DEFAULT")



class SceneLayerNames(bpy.types.Panel):
    '''Amaranth Layers'''
    bl_label = 'Amaranth Layers'
    bl_idname = 'SCENE_PT_layers'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'render_layer'

    def draw_header(self, context):
        layout = self.layout
        scene = context.scene
        draw_header(layout, scene, "SCENE_MT_layernames_menu")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        active_object = context.active_object
        active_layer = scene.active_layer_name
        row = layout.row()
        row.template_list(
            "NAMED_LAYER_UL_list", "", scene, 
            "layer_names", scene, "active_layer_name", type ="DEFAULT")
        row = layout.row(align=True)
        row.operator("scene.save_render_state", icon='FILE_TICK')
        row.operator("scene.restore_render_state", icon='FILESEL')
        # debuging code for restore/save functionality:
        '''
        for scene in bpy.data.scenes:
            row =layout.row(align = True)
            row.prop(scene,'state_of_render', text='')
            row.prop(scene,'layers',text = '')
            row.prop(scene,'layers_to_render', text='')
            row.prop(scene, 'scene_to_render',
                text='',
                icon='FILE_TICK' if scene == context.screen.scene
                    else 'BLANK1')
        '''


class SCENE_MT_layernames_browser(bpy.types.Menu):
    bl_label = "Layer Browser"

    def draw(self, context):
        layout = self.layout
        mode = context.mode

        scene = context.scene
        active = context.active_object
        col = layout.column()
        space = context.space_data
        if mode in ['EDIT_ARMATURE', 'POSE']:
            simple_draw(col, active.data, context.active_bone, False, space)
        else:
            simple_draw(col, scene, active, True, space)


def add_button(self, context):
    row = self.layout.row(align=True)
    mode = context.mode
    row.separator()
    row.menu(
        "SCENE_MT_layernames_browser",
        icon='NONE',
        text="Layers")
    if mode in ['EDIT_ARMATURE', 'POSE']:
        row.operator("armature.add_named_layer", icon='ZOOMIN', text="")
    else:
        row.operator("scene.add_named_layer", icon='ZOOMIN', text="")


def add_props(id_type, prop):
    id_type.layer_names = bpy.props.CollectionProperty(type=prop)
    id_type.active_layer_name = bpy.props.IntProperty(default=0)
    id_type.use_layers_locked = bpy.props.BoolProperty(default=False)

def del_props(id_type):
    ''' delete the properties we once had'''
    del(id_type.layer_names)
    del(id_type.use_layers_locked)
    del(id_type.active_layer_name)


def add_hotkey(kc, mode_name, ot, key, shift=False, ctrl=False, alt=False):
        km = kc.keymaps.new(name=mode_name)
        kmi = km.keymap_items.new(
            ot, key, 'PRESS',
            shift=shift, ctrl=ctrl, alt=alt)


def del_hotkey(kc, mode_name, ot):
    km = kc.keymaps[mode_name]
    for kmi in km.keymap_items:
        if kmi.idname == ot:
            km.keymap_items.remove(kmi)

layer_classes = [
            LayerNamesPreferences,
            NAMED_LAYER_UL_list,
            ARMATURE_LAYER_UL_list,
            SCENE_OT_save_render_state,
            SCENE_OT_restore_render_state,
            SCENE_OT_active_to_mask,
            SCENE_OT_active_to_exclude,
            SCENE_OT_active_to_renderlayers,
            SCENE_OT_other_scene_layers,
            SCENE_OT_template_layers_import,
            SCENE_OT_template_layers_export,
            SCENE_OT_add_named_layer,
            SCENE_OT_del_named_layer,
            SCENE_OT_del_all_layers,
            SCENE_OT_swap_layers,
            SCENE_OT_import_old_layers,
            ARMATURE_OT_template_layers_import,
            ARMATURE_OT_template_layers_export,
            ARMATURE_OT_add_named_layer,
            ARMATURE_OT_del_named_layer,
            ARMATURE_OT_del_all_layers,
            ARMATURE_OT_swap_layers,
            ARMATURE_OT_import_old_layers,
            OBJECT_OT_change_named_layer,
            SCENE_MT_layernames_menu,
            ARMATURE_MT_layernames_menu,
            SCENE_MT_layernames_browser]

layer_panels = [SceneLayerNames, ArmatureLayerNames]
custom_layer_parameters = [
    LayerParameters, ArmatureLayerParameters,
    OperatorParameters, SceneRenderLayerBackup]
hotkey_modes = ['Object Mode', 'Pose', 'Armature']

layer_options_panels = [
    "RENDERLAYER_PT_layer_options", "CyclesRender_PT_layer_options"]


def register():
    for itm in custom_layer_parameters:
        bpy.utils.register_class(itm)

    add_props(bpy.types.Scene, LayerParameters)
    add_props(bpy.types.Armature, ArmatureLayerParameters)
    bpy.types.Scene.layers_to_render = bpy.props.BoolVectorProperty(
        size=20, subtype='LAYER')
    bpy.types.Scene.scene_to_render = bpy.props.BoolProperty()
    bpy.types.Scene.state_of_render = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.renderlayers_backup = bpy.props.CollectionProperty(
        type=SceneRenderLayerBackup)

    for itm in layer_classes:
        bpy.utils.register_class(itm)

    bpy.types.VIEW3D_HT_header.append(add_button)
    for itm in layer_panels:
        bpy.utils.register_class(itm)

    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        for mode in hotkey_modes:
            add_hotkey(
                kc, mode, 'object.change_named_layer',
                "A", shift=True, ctrl=True)

# addon_prefs = user_prefs.addons[__name__].preferences

def unregister():
    kc = bpy.context.window_manager.keyconfigs.addon
    if kc:
        for mode in ['Object Mode', 'Pose', 'Armature']:
            del_hotkey(kc, mode, 'object.change_named_layer')
    for itm in layer_panels:
        bpy.utils.unregister_class(itm)
    bpy.types.VIEW3D_HT_header.remove(add_button)
    layer_classes.reverse()
    for itm in layer_classes:
        bpy.utils.unregister_class(itm)

    del_props(bpy.types.Scene)
    del_props(bpy.types.Armature)
    del(bpy.types.Scene.layers_to_render)
    del(bpy.types.Scene.scene_to_render)
    del(bpy.types.Scene.state_of_render)
    del(bpy.types.Scene.renderlayers_backup)
    for itm in custom_layer_parameters:
        bpy.utils.unregister_class(itm)

if __name__ == '__main__':
    register()
