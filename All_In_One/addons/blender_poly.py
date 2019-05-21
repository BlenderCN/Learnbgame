bl_info = {
    "name": "Blender Poly",
    "category": "Object",
    "author": "Yuichi Sato",
    "version": (1, 5),
    "blender": (2, 79, 0),
    "location": "Object Panel > Poly",
    "wiki_url": "https://github.com/satoyuichi/BlenderPoly",
}

import bpy
import requests
import json
import re
import os
from pathlib import Path

__package__ = "blender_poly"
BLENDER_POLY_PATH = 'BlenderPoly'

preview_collections = {}
blender_poly_json = {}
blender_poly_category_items = [
    ('animals', 'Animals and Creatures', 'animals'),
    ('architecture', 'Architecture', 'architecture'),
    ('art', 'Art', 'art'),
    ('current_events', 'Current events', 'current_events'),
    ('food', 'Food and Drink', 'food'),
    ('furniture_home', 'Furniture and Home', 'furniture_home'),
    ('nature', 'Nature', 'nature'),
    ('objects', 'Objects', 'objects'),
    ('people', 'People and Characters', 'people'),
    ('scenes', 'Places and Scenes', 'scenes'),
    ('sports_fitness', 'Sports and Fitness', 'sports_fitness'),
    ('tech', 'Technology', 'tech'),
    ('transport', 'Transport', 'transport'),
    ('travel', 'Travel', 'travel')
]

def get_temp_path (context):
    props = context.window_manager.poly
    return Path (context.user_preferences.filepaths.temporary_directory).joinpath (BLENDER_POLY_PATH, props.category_type)

def get_element_from_json (id):
    global blender_poly_json

    if not 'assets' in blender_poly_json.keys ():
        return None

    for elem in blender_poly_json['assets']:
        if elem['name'] == id:
            return elem

def enum_previews_from_model_previews(self, context):
    """EnumProperty callback"""
    if context is None:
        return []

    wm = context.window_manager
    preferences = context.user_preferences.addons[__package__].preferences
    props = context.window_manager.poly
    
    enum_items = []
    directory = get_temp_path (context)

    pcoll = preview_collections[props.category_type]
    
    if directory == pcoll.previews_previews_dir:
        return pcoll.previews_previews
        
    filepath_list = list (Path (directory).glob ('**/*'))
    
    # Load JSON file.
    json_path = directory.joinpath (props.category_type + ".json")
    if not json_path.exists ():
        return enum_items
    
    with json_path.open ("r", encoding='utf-8') as f:
        global blender_poly_json
        blender_poly_json = json.loads (f.read ())
    
    for i, filepath in enumerate (filepath_list):
        if filepath.suffix != ".png":
            continue

        # Load image.
        comp_path = str (filepath)
        thumb = pcoll.load (comp_path, comp_path, 'IMAGE')

        # Get asset name from JSON.
        id_name = 'assets/' + filepath.stem
        elem = get_element_from_json (id_name)

        enum_items.append ((id_name, elem['displayName'], comp_path, thumb.icon_id, i))
    
    pcoll.previews_previews = enum_items
    pcoll.previews_previews_dir = directory
    return pcoll.previews_previews

def import_obj_by_url(context, url):
    r = requests.get(url)
    
    print (url)

#    file_path = get_temp_path (context).joinpath (obj_elem['root']['relativePath'])
    file_path = get_temp_path (context).joinpath ('modeldata.obj')
    with file_path.open ("w", encoding='utf-8') as f:
        f.write (r.text)

    bpy.ops.import_scene.obj(filepath=str(file_path), axis_forward='-Z', axis_up='Y', filter_glob="*.obj;*.mtl", use_edges=True, use_smooth_groups=True, use_split_objects=True, use_split_groups=True, use_groups_as_vgroups=False, use_image_search=True, split_mode='ON', global_clamp_size=0)


class BlenderPolyPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    polyApiKey = bpy.props.StringProperty (
        name = "API Key",
        default = "",
        description = "Input the Poly's API Key",
        subtype = 'BYTE_STRING'
        )
           
    def draw(self, context):
        props = context.window_manager.poly
        layout = self.layout
        preferences = context.user_preferences.addons[__package__].preferences
        
        row = layout.row()
        row.prop(preferences, 'polyApiKey')
        
        row = layout.row()
        row.scale_y = 1.25
        row.operator("scene.poly_install_assets", icon='SAVE_PREFS')

class BlenderPolyInstallAssets(bpy.types.Operator):
    """Save the Blender Poly assets filepath"""
    bl_idname = "scene.poly_install_assets"
    bl_label = "Save Settings"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.wm.save_userpref()

        return {'FINISHED'}
    
class BlenderPolyProps(bpy.types.PropertyGroup):
    category_type = bpy.props.EnumProperty(
        items=blender_poly_category_items,
        name="Category Type",
        default="animals")
    maxComplexity = bpy.props.EnumProperty(
        items=[
            ('COMPLEX', 'COMPLEX', 'COMPLEX'),
            ('MEDIUM', 'MEDIUM', 'MEDIUM'),
            ('SIMPLE', 'SIMPLE', 'SIMPLE')
        ],
        name="Max Complexity",
        default="COMPLEX")
    keywords = bpy.props.StringProperty(name='Keywords', description='Keywords')
    curated = bpy.props.BoolProperty(name='Curated', description='Curated')
    pageSize = bpy.props.IntProperty(name='Page size', description='Page size', default=20, min=1, max=100)
    orderBy = bpy.props.EnumProperty(
        items=[('BEST', 'BEST', 'BEST'), ('NEWEST', 'NEWEST', 'NEWEST'), ('OLDEST', 'OLDEST', 'OLDEST')],
        name='Order by',
        default='BEST')
    nextPageToken = bpy.props.StringProperty(name='nextPageToken', default='', description='Token')
    directID = bpy.props.StringProperty(name='ID', description='Import model ID')
        
class BlenderLayoutPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Blender Poly"
    bl_idname = "blender_poly_layout"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Create"
    bl_context = "objectmode"

    def draw(self, context):
        props = context.window_manager.poly
        
        layout = self.layout
        wm = context.window_manager

        scene = context.scene
        
        row = layout.row(align=True)
        row.prop(props, "category_type")
        
        row = layout.row(align=True)
        row.prop(props, "maxComplexity")

        row = layout.row(align=True)
        row.prop(props, "orderBy")

        row = layout.row(align=True)
        row.prop(props, "pageSize")
        
        row = layout.row(align=True)
        row.prop(props, "curated")
        
        row = layout.row(align=True)
        row.prop(props, "keywords")
        
        row = layout.row(align=True)
        col = row.column()
        col.scale_y = 2.0
        if props.nextPageToken:
            col.operator("blender_poly.to_head", text="Head", icon="REW")

            col = row.column()
            col.scale_y = 2.0
            col.operator("blender_poly.load", text="Next", icon="FORWARD")
        else:
            col.operator("blender_poly.load", text="Load", icon="FILE_FOLDER")

        row = layout.row(align=True)
        col = row.column()
        col.scale_y = 1
        col.template_icon_view(wm, "poly_model_previews", show_labels=True)
        elem = get_element_from_json (context.window_manager.poly_model_previews)
        if elem == None:
            col.label('')
        else:
            col.label(elem['displayName'])
        
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("blender_poly.import", text="Import", icon="IMPORT")

        row = layout.row(align=True)
        row.label(text="Direct import:")
        
        row = layout.row(align=True)
        row.prop(props, "directID")
        row = layout.row(align=True)
        row.operator("blender_poly.direct_import", text="Direct Import", icon="IMPORT")

class BlenderPolyToHead(bpy.types.Operator):
    bl_idname = "blender_poly.to_head"
    bl_label = "To Head Operator"

    def execute(self, context):
        props = context.window_manager.poly
        props.nextPageToken = ''
        return {'FINISHED'}
    
class BlenderPolyDirectImport(bpy.types.Operator):
    bl_idname = "blender_poly.direct_import"
    bl_label = "Direct Import Operator"

    def execute(self, context):
        props = context.window_manager.poly
        preferences = context.user_preferences.addons[__package__].preferences
        
        payload = { 'key': preferences.polyApiKey }

        r = requests.get ("https://poly.googleapis.com/v1/assets/" + props.directID, params=payload)
        json = r.json ()
        
        for elem in json['formats']:
            if (elem['formatType']) == 'OBJ':
                url = elem['root']['url']
                import_obj_by_url (context, url)
                break

        return {'FINISHED'}
            
class BlenderPolyAssetsLoader(bpy.types.Operator):
    bl_idname = "blender_poly.load"
    bl_label = "Load Operator"
    
    def getPayload (self, preferences, props):
        return {'key': preferences.polyApiKey, 'format': 'OBJ',
            'category': props.category_type,
            'maxComplexity': props.maxComplexity,
            'curated': props.curated,
            'keywords': props.keywords,
            'pageSize': props.pageSize,
            'orderBy': props.orderBy,
            'pageToken': props.nextPageToken
        }
        
    def writeThumbnails (self, json, thumbnail_path):
        for asset in json['assets']:
            suffix = Path (asset['thumbnail']['relativePath']).suffix
            asset['name'] = re.sub (r'assets/', '', asset['name'])
            filepath = thumbnail_path.joinpath (asset['name']).with_suffix(suffix)

            if not filepath.exists ():
                thumbnail = requests.get (asset['thumbnail']['url'])
                with thumbnail_path.joinpath (filepath).open (mode='wb') as f:
                    f.write (thumbnail.content)

    def recreatePreviews (self, props):
        pcoll = preview_collections[props.category_type]
        bpy.utils.previews.remove(pcoll)
        pcoll = bpy.utils.previews.new ()
        preview_collections[props.category_type] = pcoll
        pcoll.previews_previews = ()
        pcoll.previews_previews_dir = ""

    def execute(self, context):
        if not __package__ in context.user_preferences.addons.keys ():
            return {'FINISHED'}       

        tmp_path = get_temp_path (context)
        if tmp_path.exists ():
            filepath_list = list (tmp_path.glob ('**/*'))
            for path in filepath_list:
                os.remove (str(path))
        else:
            tmp_path.mkdir (parents=True)

        props = context.window_manager.poly
        preferences = context.user_preferences.addons[__package__].preferences
        payload = self.getPayload(preferences, props)

        self.recreatePreviews (props)

        r = requests.get ("https://poly.googleapis.com/v1/assets", params=payload)
        json = r.json()

        if not 'assets' in json.keys ():
            return {'INTERFACE'}

        props.nextPageToken = json['nextPageToken']

        # Save JSON
        json_path = tmp_path.joinpath (props.category_type + ".json")
        with json_path.open ("w", encoding='utf-8') as f:
            f.write (r.text)

        self.writeThumbnails (json, tmp_path)

        return {'FINISHED'}

class BlenderPolyAssetsImporter(bpy.types.Operator):
    bl_idname = "blender_poly.import"
    bl_label = "Import Operator"

    def execute(self, context):
        global blender_poly_json

        elem = get_element_from_json (context.window_manager.poly_model_previews)
        
        obj_elem = ''
        for el in elem['formats']:
            if el['formatType'] == 'OBJ':
                obj_elem = el

        url = obj_elem['root']['url']
        import_obj_by_url (context, url)
        
        return {'FINISHED'}
        
def register():
    bpy.utils.register_class(BlenderPolyProps)
    bpy.utils.register_class(BlenderLayoutPanel)
    bpy.utils.register_class(BlenderPolyDirectImport)
    bpy.utils.register_class(BlenderPolyToHead)
    bpy.utils.register_class(BlenderPolyAssetsLoader)
    bpy.utils.register_class(BlenderPolyAssetsImporter)
    bpy.utils.register_class(BlenderPolyPreferences)
    bpy.utils.register_class(BlenderPolyInstallAssets)
    
    bpy.types.WindowManager.poly = bpy.props.PointerProperty(type=BlenderPolyProps)
    bpy.types.WindowManager.poly_model_previews = bpy.props.EnumProperty(items=enum_previews_from_model_previews)

    for category in blender_poly_category_items:
        pcoll = bpy.utils.previews.new ()
        pcoll.previews_previews = ()
        pcoll.previews_previews_dir = ""
        preview_collections [category[0]] = pcoll

def unregister():
    bpy.utils.unregister_class(BlenderPolyInstallAssets)
    bpy.utils.unregister_class(BlenderPolyPreferences)
    bpy.utils.unregister_class(BlenderPolyAssetsImporter)
    bpy.utils.unregister_class(BlenderPolyAssetsLoader)
    bpy.utils.unregister_class(BlenderPolyToHead)
    bpy.utils.unregister_class(BlenderPolyDirectImport)
    bpy.utils.unregister_class(BlenderLayoutPanel)
    bpy.utils.unregister_class(BlenderPolyProps)

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()
    
    try:
        del bpy.types.WindowManager.poly_model_previews
        del bpy.types.WindowManager.poly
    except:
        pass

if __name__ == "__main__":
    register()
