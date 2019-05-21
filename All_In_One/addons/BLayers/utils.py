import bpy
import bpy.utils.previews
from os.path import join,basename,dirname,splitext
from os import listdir


def sort_layer(visible_layer):
    sorted_layer = []

    Column = {}
    for l in visible_layer :
        if not Column.get(l.column) :
            Column[l.column] = []

        Column[l.column].append(l)

    for col,layers in sorted(Column.items()) :
        sorted_layer.append(sorted(layers,key=lambda x : x.row))

    return sorted_layer

def update_col_index(collection) :
    for i,item in enumerate(collection) :
        item.col_index = i

def redraw_areas():
    for area in bpy.context.screen.areas :
        area.tag_redraw()

def get_icons():
    global custom_icons
    custom_icons = bpy.utils.previews.new()
    icons_dir = join(dirname(__file__),'icons')
    for icon in listdir(icons_dir) :
        custom_icons.load(splitext(icon)[0].upper(), join(icons_dir, icon), 'IMAGE',force_reload=True)

    custom_icons.update()

def source_layers():
    scene = bpy.context.scene
    ob = bpy.context.object
    BLayersSettings = scene.BLayers

    if BLayersSettings.layer_type == 'ARMATURE' :
        if ob and ob.type == 'ARMATURE' :
            layer_mode= 'ARMATURE'
        else :
            layer_mode = 'SCENE'

    elif BLayersSettings.layer_type == 'SCENE' :
        layer_mode = 'SCENE'

    else :
        if bpy.context.mode in ['POSE','EDIT_ARMATURE'] :
            layer_mode = 'ARMATURE'
        else :
            layer_mode = 'SCENE'

    if layer_mode == 'SCENE' :
        return scene,scene.BLayers.layers,scene.BLayers,scene.layers,scene.objects,bpy.context.selected_objects
    else :
        selected_bones =[]
        if bpy.context.mode =='POSE':
            selected_bones = [b.bone for b in bpy.context.selected_pose_bones]
        elif bpy.context.mode =='EDIT_ARMATURE' :
            selected_bones = [b for b in bpy.context.selected_editable_bones]

        return ob.data,ob.data.BLayers.layers,ob.data.BLayers,ob.data.layers,ob.data.bones,selected_bones
