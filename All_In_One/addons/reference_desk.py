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
    'name': 'Reference Desk',
    'author': 'Chris Webber, Bassam Kurdali',
    'version': '0.96',
    'blender': (2, 7, 7),
    'location': 'View3D > Toolbar > Assets > Reference Desk',
    'description': 'Project Asset Linker',
    'url': 'http://urchn.org',
    'category': 'Asset Management'}

__bpydoc__ = """
A tool for allowing easy linking of commonly used assets.

Load things out of a json database, formatted like:
  name,filepath,datapath
"""

import os
import json
import imp

import bpy

from pprint import pprint


# A global variable to track the "loaded" library data from scene to
# scene.
LIBRARY_DATA = {}


# Extra bpy data we can link over the original design (groups and texts)
# TODO get groups and texts in, cleanup post link options for users and code
LINKABLE_ITEMS = {
    'link_actions': {
        'link_type': 'Action',  # How it is reference from the link
        'bpy_data': 'actions',  # How to get it from bpy.data
        'data_type': 'action',  # Singular data type
        'bl_idname': "scene.add_refdesk_action", # idname for getter operator
        'bl_label': "Add Refdesk Action", # label for getter operator
        'items': ('action', 'action', 'action'), # enum tuple for selection
        'icon': 'POSE_DATA',  # menu icon
        'actions': {},
        },
    'link_materials': {
        'link_type': 'Material',
        'bpy_data': 'materials',
        'data_type': 'material',
        'bl_idname': "scene.add_refdesk_material",
        'bl_label': "Add Refdesk Material",
        'items': ('material', 'material', 'material'),
        'icon': 'MATERIAL',
        'actions': {},
        },
    'link_worlds': {
        'link_type': 'World',
        'bpy_data': 'worlds',
        'data_type': 'world',
        'bl_idname': "scene.add_refdesk_world",
        'bl_label': "Add Refdesk Material",
        'items': ('world', 'world', 'world'),
        'icon': 'WORLD',
        'actions': {},
        },
    'link_objects': {
        'link_type': 'Object',
        'bpy_data': 'objects',
        'data_type': 'object',
        'bl_idname': "scene.add_refdesk_object",
        'bl_label': "Add Refdesk Object",
        'items': ('object', 'object', 'object'),
        'icon': 'OBJECT_DATA',
        'actions': {},
        },
    'link_node_groups': {
        'link_type': 'NodeTree',
        'bpy_data': 'node_groups',
        'data_type': 'node_group',
        'bl_idname': "scene.add_refdesk_node_group",
        'bl_label': "Add Refdesk Node Group",
        'items': ('node_group', 'node_group', 'node_group'),
        'icon': 'NODETREE',
        'actions': {},
        },
}


class LibraryItem(object):
    """
    An item for easy-loading via the ReferenceDesk
    """

    def __init__(self, relative_to, **kwargs):
        """
        Keyword arguments:
        - relative_to: path where all other files are relative to
        - datapath: path within the file to the object
        """
        self.relative_to = relative_to
        self.instance_groups = kwargs.get('instance_groups', [])
        self.noninstance_groups = kwargs.get('noninstance_groups', [])
        self.require_python_texts = kwargs.get('require_python_texts', [])
        self.require_python_files = kwargs.get('require_python_files', [])
        self.exec_python_posthooks = kwargs.get('exec_python_posthooks', [])
        self.item_list = [
            'instance_groups', 'noninstance_groups',
            'require_python_texts', 'require_python_files',
            'exec_python_posthooks']
        for link_items in LINKABLE_ITEMS:
            setattr(self, link_items, kwargs.get(link_items, []))
            self.item_list.append(link_items)

    def to_serial(self):
        return {
            attr: getattr(self, attr)
            for attr in self.item_list if getattr(self, attr)}

    def link_into_scene(self):
        """
        Link this object into the scene
        """
        def _link_in(filepath, dataname, instance_groups, link_type="Group"):
            # Allow user to specify absolute path, but generally we'll
            # use relative paths
            if filepath.startswith('/'):
                full_filepath = filepath
            else:
                full_filepath = os.path.join(
                    self.relative_to, filepath)

            arg_filepath = "//%s\\%s\\%s" % (
                os.path.split(filepath)[-1],
                link_type,
                dataname)
            print(arg_filepath)
            arg_directory = "%s\\%s" % (
                full_filepath,
                link_type)
            print(arg_directory)
            bpy.ops.wm.link(
                filepath=arg_filepath,
                directory=arg_directory,
                filename=dataname,
                filemode=1, relative_path=True, link=True,
                instance_groups=instance_groups, active_layer=True) # XXX api

        # Link in python texts from other files
        for filepath, text in self.require_python_texts:
            print("normaltext: ",text)
            if text not in bpy.data.texts: # XXX Also check on lib filepath
                _link_in(filepath, text, False, link_type="Text")

        # Link in instance groups (or add to scene already linked groups)
        for filepath, group in self.instance_groups:
            if group in bpy.data.groups:  # XXX Also check on lib filepath
                bpy.ops.object.group_instance_add(
                    group=group, view_align=False)
            else:
                _link_in(filepath, group, True)

        # Link in noninstance groups not linked yet
        for filepath, group in self.noninstance_groups:
            # Link it in, if it's not linked already.
            if group not in bpy.data.groups: # XXX Also check on lib filepath
                _link_in(filepath, group, False)

        # Link in and execute (via __import__'ing) python_posthooks
        for filepath, text in self.exec_python_posthooks:
            print("posthook: ",text)
            if text not in bpy.data.texts: # XXX Also check on lib filepath
                print("linking")
                _link_in(filepath, text, False, link_type="Text")
            print("executing:")

            try: # XXX warning! really really gross:
                exec(bpy.data.texts[text].as_string())
            except:
                module_name = text.replace(".py", "")
                __import__(module_name)

        def _link_in_items(link_items):
            for filepath, item in getattr(self, link_items):
                print(LINKABLE_ITEMS[link_items]['link_type'], item)
                # XXX Also check on lib filepath
                if item not in getattr(
                        bpy.data, LINKABLE_ITEMS[link_items]['bpy_data']):
                    print("linking")
                    _link_in(
                        filepath, item, False,
                        link_type=LINKABLE_ITEMS[link_items]['link_type'])

        for link_items in LINKABLE_ITEMS:
            _link_in_items(link_items)


class ReferenceDeskReload(bpy.types.Operator):
    bl_idname = 'object.refdesk_reload'
    bl_label = 'Reload!'

    def execute(self, context):
        LIBRARY_DATA[context.scene.name] = load_database(
            context.scene['refdesk_library'])
        pprint(LIBRARY_DATA[context.scene.name])
        return {'FINISHED'}


class ReferenceDeskMenuItem(bpy.types.Operator):
    """
    A selectable button item from the reference desk
    """
    bl_label = "Menu name goes here ;)"
    bl_idname = 'object.refdesk_menuitem'

    section = bpy.props.StringProperty(
        name="Section", description="Section", default="")
    item_name = bpy.props.StringProperty(
        name="Item name", description="Name of the item", default="")

    def execute(self, context):
        item = LIBRARY_DATA[context.scene.name][self.section][self.item_name]
        item.link_into_scene()

        return {'FINISHED'}


class ReferenceDeskSelectLibrary(bpy.types.Operator):
    """
    Opens a Filebrowser to pick the library file, stores in scene
    """
    bl_label = "Select Library File"
    bl_idname = 'scene.refdesk_select_library'

    filepath = bpy.props.StringProperty(name="filepath", subtype='FILE_PATH')

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        filepath = self.properties.filepath
        bpy.context.scene.refdesk_library = bpy.path.relpath(filepath)[2:]
        return {'FINISHED'}


class AddRefDeskText(bpy.types.Operator):
    '''
    Add a text to the item
    '''
    bl_idname = "scene.add_refdesk_text"
    bl_label = "Add Refdesk Text"

    def execute(self, context):
        scene = context.scene
        a = scene.refdesk_items.add()
        a.path = blend_lib_path(scene)
        a.data_type = 'text'
        return {'FINISHED'}


class AddRefDeskGroup(bpy.types.Operator):
    '''
    Add a group to the item
    '''
    bl_idname = "scene.add_refdesk_group"
    bl_label = "Add Refdesk Group"

    def execute(self, context):
        scene = context.scene
        a = scene.refdesk_items.add()
        a.path = blend_lib_path(scene)
        a.data_type = 'group'
        return {'FINISHED'}



def addrefdeskclass(idname, label, data_type):
    '''
    creates a new add class for reference desk
    '''


    class AddRefDeskThing(bpy.types.Operator):
        bl_idname = idname
        bl_label = label

        def execute(self, context):
            scene = context.scene
            a = scene.refdesk_items.add()
            a.path = blend_lib_path(scene)
            a.data_type = data_type
            return {'FINISHED'}

    return AddRefDeskThing


AddOperators = [
    addrefdeskclass(
        link_items['bl_idname'],
        link_items['bl_label'],
        link_items['data_type'])
    for link_items in LINKABLE_ITEMS.values()]


class DelRefDeskItem(bpy.types.Operator):
    '''
    Remove a group from the item
    '''
    bl_idname = "scene.del_refdesk_item"
    bl_label = "Del Refdesk Item"

    def execute(self, context):
        scene = context.scene
        scene.refdesk_items.remove(scene.active_refdesk_item)
        if scene.active_refdesk_item == len(scene.refdesk_items) and\
                scene.active_refdesk_item > 0:
            scene.active_refdesk_item -= 1
        return {'FINISHED'}


class ReferenceDeskToggleRead(bpy.types.Operator):
    """
    Toggle the Read/Write Mode of reference Desk
    """
    bl_label = "Toggle library write/read"
    bl_idname = 'scene.refdesk_toggle_read'

    unlock = bpy.props.BoolProperty(name='unlock', default=True)

    def execute(self, context):
        context.scene.use_refdesk_locked = not self.properties.unlock
        return {'FINISHED'}


def get_groups(scene, instance):
    """
    return groups from objects starting with prefix
    """
    return [
        [itm.path, itm.selection] for itm in scene.refdesk_items if
        itm.data_type == 'group' and itm.active == instance]


def get_selection(self, context):
    '''
    return a list of datablocks in the scene
    '''
    hard_coded = {
        'text': bpy.data.texts,
        'group': bpy.data.groups}
    derived = {
        link_items['data_type']: getattr(bpy.data, link_items['bpy_data'])
        for link_items in LINKABLE_ITEMS.values()
    }
    derived.update(hard_coded)
    source = derived[self.data_type]
    return [tuple([itm.name] * 3) for itm in source]


def get_texts(scene, execute):
    """
    return texts from objects starting with prefix
    """
    return [
        [itm.path, itm.selection] for itm in scene.refdesk_items if
        itm.data_type == 'text' and itm.active == execute]


def get_getters(data_type):
    """
    generate getter functions for our enums
    """
    def get_linkable_items(scene, link):
        return [
        [itm.path, itm.selection] for itm in scene.refdesk_items if
        itm.data_type == data_type and itm.active == link]
    return get_linkable_items


class RefDeskCollection(bpy.types.PropertyGroup):
    """
    what we need to add groups
    """
    name = bpy.props.StringProperty(name="name", default="first")
    data_type = bpy.props.EnumProperty(
        name="data_type",
        items=[
            ('group', 'group', 'group'),
            ('text', 'text', 'text')] + [
            link_items['items'] for link_items in LINKABLE_ITEMS.values()
            ])
    selection = bpy.props.EnumProperty(name="selection", items=get_selection)
    path = bpy.props.StringProperty(name="path", default="")
    active = bpy.props.BoolProperty(name="active", default=True)


def serialize(library):
    """
    returns serializable version of library
    """
    serial = {}
    for category in library:
        serial[category] = {}
        for asset in library[category]:
            asset_data = library[category][asset]
            serial[category][asset] = asset_data.to_serial()
    return serial


def blend_lib_path(scene):
    full_db_path = generate_full_database_path(scene.refdesk_library)
    db_dir = os.path.abspath(os.path.dirname(full_db_path))

    self_path = os.path.abspath(
        bpy.path.abspath(bpy.context.blend_data.filepath))
    return os.path.relpath(self_path, db_dir)


class ReferenceDeskStoreAsset(bpy.types.Operator):
    """
    Store a new Asset in the JSON file
    """
    bl_label = "Store New Asset"
    bl_idname = 'scene.refdesk_store_asset'

    def execute(self, context):
        scene = context.scene

        full_db_path = generate_full_database_path(scene.refdesk_library)
        db_dir = os.path.abspath(os.path.dirname(full_db_path))

        self_path = os.path.abspath(
            bpy.path.abspath(context.blend_data.filepath))

        # Get Asset Data
        category = scene.refdesk_category
        asset = scene.refdesk_item
        asset_items = {}
        asset_items['noninstance_groups'] = get_groups(scene, instance=False)
        asset_items['instance_groups'] = get_groups(scene, instance=True)
        asset_items['require_python_texts'] = get_texts(scene, execute=False)
        asset_items['exec_python_posthooks'] = get_texts(scene, execute=True)
        for link_items in LINKABLE_ITEMS:
            asset_items[link_items] = get_getters(
                LINKABLE_ITEMS[link_items]['data_type'])(scene, link=True)

        lib_data = LIBRARY_DATA[context.scene.name]
        print('ADDING')
        if not category in lib_data:
            lib_data[category] = {}
        if not asset in lib_data[category]:
            lib_data[category][asset] = LibraryItem(db_dir, **asset_items)

        print(type(lib_data))
        print(full_db_path)
        with open(full_db_path, mode='w') as lib_file:
            lib_file.write(
                json.dumps(serialize(lib_data), sort_keys=True, indent=4))
        return {'FINISHED'}


def panel_draw_loader(layout, context, lib_data):
    """
    draw the panel in the case that we are loading data
    """
    # Give the user the option between list and search mode
    row = layout.row()
    row.prop(
        context.scene, 'refdesk_search',
        text="", icon='VIEWZOOM')

    search_string = context.scene.get('refdesk_search')

    # Insert row after row
    section_names = sorted(lib_data.keys())
    for section_name in section_names:
        section_data = lib_data[section_name]

        # Get all the item names, sort them, and only continue if
        # we have matches
        item_names = [
            item_name
            for item_name in sorted(section_data.keys())
            if not search_string
            or search_string.strip().lower() in item_name.lower()]
        if not item_names:
            continue

        layout.separator()

        box = layout.box()
        row = box.row()
        row.label(text="%s:" % section_name)

        for item_name in item_names:
            item_data = section_data[item_name]

            row = box.row()
            menuitem = row.operator(
                'object.refdesk_menuitem',
                text=item_name)
            menuitem.section = section_name
            menuitem.item_name = item_name


class REFDESK_UL_ItemAdder(bpy.types.UIList):
    bl_idname = "refdesk.add_items_ui"

    def draw_item(
            self, context, layout, data, item,
            icon, active_data, active_property, index):
        icon_dict = {
            link_items['data_type']: link_items['icon']
            for link_items in LINKABLE_ITEMS.values()}
        icon_dict.update({'group': 'GROUP', 'text': 'TEXT'})

        try:
            icon_draw = icon_dict[item.data_type]
        except KeyError:
            icon_draw = 'FILESEL' 
        layout.label(text='', icon=icon_draw)
        layout.prop(item, 'selection', text='')
        layout.prop(item, 'path', text='')
        layout.prop(item, 'active', text='')


def panel_draw_saver(layout, context, lib_data):
    """
    draw the panel in the case that we are saving new data
    """
    scene = context.scene
    row = layout.row()
    row.prop(scene, 'refdesk_category', text="Category")
    row = layout.row()
    row.prop(scene, 'refdesk_item', text="Asset")

    row = layout.row()
    col = row.column()
    col.template_list(
        "refdesk.add_items_ui", "", scene, "refdesk_items",
        scene, "active_refdesk_item")
    col = row.column(align=True)
    col.operator('scene.add_refdesk_text', icon='TEXT', text='')
    col.operator('scene.add_refdesk_group', icon='GROUP', text='')

    for link_items in LINKABLE_ITEMS.values():
        col.operator(link_items['bl_idname'], icon=link_items['icon'], text='')

    col.operator('scene.del_refdesk_item', icon='X', text='')

    row = layout.row()
    row.operator('scene.refdesk_store_asset')


class ReferenceDeskPanel(bpy.types.Panel):
    bl_label = 'Reference Desk'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Assets'

    def draw_header(self, context):
        layout = self.layout
        scene = context.scene
        layout.operator(
            'scene.refdesk_toggle_read', text="",
            icon='LOCKED' if scene.use_refdesk_locked else 'UNLOCKED',
            emboss=False).unlock = scene.use_refdesk_locked

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator(
            'scene.refdesk_select_library', text="Select Library", icon='FILE')
        # Check if it's loaded
        if not context.scene.get('refdesk_library'):
            # No library property; we can't do anything!  Warn the
            # user and return.
            row = layout.row()
            row.label(
                text="Scene has no library property!",
                icon="ERROR")
            return

        elif not (os.path.exists(
                generate_full_database_path(
                    context.scene['refdesk_library']))):
            row = layout.row()
            row.label(
                text="Library file does not exist?!",
                icon="ERROR")
            return

        elif not context.scene.name in LIBRARY_DATA:
            # load the library data, if not loaded yet:
            LIBRARY_DATA[context.scene.name] = load_database(
                context.scene['refdesk_library'])
        else:
            # Add a reload button
            row = layout.row()
            row.operator('object.refdesk_reload', icon="FILE_REFRESH")

        lib_data = LIBRARY_DATA[context.scene.name]

        if context.scene.use_refdesk_locked:
            panel_draw_loader(layout, context, lib_data)
        else:
            panel_draw_saver(layout, context, lib_data)


def generate_full_database_path(database_path):
    """
    Get an "absolute data path", relative to this file anyway.
    """
    if not database_path.startswith('/'):
        # Load a ".blend relative path" database_path
        database_path = os.path.abspath(
            os.path.join(
                os.path.dirname(bpy.data.filepath),
                database_path))

    return os.path.abspath(database_path)


def load_database(database_path):
    """
    Load the database ("shelving") which includes all the references
    to all the objects.

    Keyword arguments:
    - database_path: path to csv file that describes all the objects
    """
    db = {}

    full_db_path = generate_full_database_path(database_path)

    data = json.loads(open(full_db_path).read())
    db_dir = os.path.abspath(
        os.path.dirname(full_db_path))  # changed from database_path

    for section_name, section_data in data.items():
        section = db.setdefault(section_name, {})

        for item_name, item_data in section_data.items():
            section[item_name] = LibraryItem(db_dir, **item_data)
    return db


def register():
    # group properties first...
    bpy.utils.register_class(RefDeskCollection)

    bpy.utils.register_class(REFDESK_UL_ItemAdder)

    # this will be our list of groups
    bpy.types.Scene.refdesk_items = bpy.props.CollectionProperty(
        type=RefDeskCollection)

    bpy.types.Scene.active_refdesk_item = bpy.props.IntProperty(
        name="active_refdesk_item", default=0)

    # Panel properties:
    bpy.types.Scene.use_refdesk_locked = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.refdesk_category = bpy.props.StringProperty(default="")
    bpy.types.Scene.refdesk_item = bpy.props.StringProperty(default="")
    bpy.types.Scene.refdesk_library = bpy.props.StringProperty(default="")
    bpy.types.Scene.refdesk_search = bpy.props.StringProperty(
        name="Refdesk Search",
        description="Limit the objects to ones matching this search")

    # Panel Operators
    bpy.utils.register_class(AddRefDeskGroup)
    bpy.utils.register_class(AddRefDeskText)
    for operator in AddOperators:
        bpy.utils.register_class(operator)
    bpy.utils.register_class(DelRefDeskItem)
    bpy.utils.register_class(ReferenceDeskReload)
    bpy.utils.register_class(ReferenceDeskMenuItem)
    bpy.utils.register_class(ReferenceDeskSelectLibrary)
    bpy.utils.register_class(ReferenceDeskToggleRead)
    bpy.utils.register_class(ReferenceDeskStoreAsset)

    # And the Panel
    bpy.utils.register_class(ReferenceDeskPanel)


def unregister():
    # Remove the Panel
    bpy.utils.unregister_class(ReferenceDeskPanel)

    # Get rid of the operators
    bpy.utils.unregister_class(AddRefDeskGroup)
    bpy.utils.unregister_class(AddRefDeskText)
    for operator in AddOperators:
        bpy.utils.unregister_class(operator)
    bpy.utils.unregister_class(DelRefDeskItem)
    bpy.utils.unregister_class(ReferenceDeskReload)
    bpy.utils.unregister_class(ReferenceDeskMenuItem)
    bpy.utils.unregister_class(ReferenceDeskSelectLibrary)
    bpy.utils.unregister_class(ReferenceDeskToggleRead)
    bpy.utils.unregister_class(ReferenceDeskStoreAsset)

    # Now we don't need those extra scene properties
    del(bpy.types.Scene.use_refdesk_locked)
    del(bpy.types.Scene.refdesk_category)
    del(bpy.types.Scene.refdesk_item)
    del(bpy.types.Scene.refdesk_library)
    del(bpy.types.Scene.refdesk_search)
    del(bpy.types.Scene.refdesk_items)
    del(bpy.types.Scene.active_refdesk_item)

    # An no extra group properties
    bpy.utils.unregister_class(REFDESK_UL_ItemAdder)
    bpy.utils.unregister_class(RefDeskCollection)

if __name__ == "__main__":
    register()
