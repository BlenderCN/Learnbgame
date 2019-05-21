import os

import bpy

from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import *

from . utility import addon, update

class Folder(PropertyGroup):
    icon = StringProperty(default='FILE_FOLDER')

    name = StringProperty(
        name = 'Path Name',
        default = '')

    location = StringProperty(
        name = 'Path',
        description = 'Path to KIT OPS library',
        update = update.libpath,
        subtype = 'DIR_PATH',
        default = '')

class KitOps(AddonPreferences):
    bl_idname = addon.name

    #TODO: options/folders modes
    context = EnumProperty(
        name = 'Context',
        description = 'KIT OPS preference settings context',
        items = [
            ('GENERAL', 'General', ''),
            ('THEME', 'Theme', ''),
            ('FILEPATHS', 'File Paths', '')],
        default = 'GENERAL')

    folders = CollectionProperty(type=Folder)

    author = StringProperty(
        name = 'Author',
        description = 'Name that will be used when creating INSERTS',
        default = '')

    category = StringProperty(
        name = 'Toolshelf Category',
        description = 'Category in the tool shelf to place KIT OPS panel under',
        update = update.category,
        default = 'KIT OPS')

    popup_location = EnumProperty(
        name = 'Popup location',
        description = 'Location to put the thumbnail popups in the category row',
        items = [
            ('LEFT', 'Left', 'Replaces file folder icons with the popup'),
            ('RIGHT', 'Right', '')],
        default = 'RIGHT')

    insert_offset_x = IntProperty(
        name = 'INSERT offset X',
        description = 'Offset used when adding the INSERT from the mouse cursor',
        soft_min = -40,
        soft_max = 40,
        subtype = 'PIXEL',
        default = 0)

    insert_offset_y = IntProperty(
        name = 'INSERT offset Y',
        description = 'Offset used when adding the INSERT from the mouse cursor',
        soft_min = -40,
        soft_max = 40,
        subtype = 'PIXEL',
        default = 20)

    clean_names = BoolProperty(
        name = 'Clean names',
        description = 'Capatilize and clean up the names used in the UI from the KPACKS',
        update = update.kpack,
        default = True)

    thumbnail_labels = BoolProperty(
        name = 'Thumbnail labels',
        description = 'Displays names of INSERTS under the thumbnails in the preview popup',
        default = True)

    thumbnails_in_list = BoolProperty(
        name = 'Thumbnails in list',
        description = 'Displays individual thumbnails for the list of INSERTS',
        default = False)

    enable_auto_select = BoolProperty(
        name = 'Enable auto select',
        description = 'Enable auto select in regular mode',
        default = True)

    border_color = FloatVectorProperty(
        name = 'Border color',
        description = 'Color used for the border',
        min = 0,
        max = 1,
        size = 4,
        precision = 3,
        subtype = 'COLOR',
        default = (1.0, 0.030, 0.0, 0.9))

    border_size = IntProperty(
        name = 'Border size',
        description = 'Border size in pixels\n  Note: DPI factored',
        min = 1,
        soft_max = 6,
        subtype = 'PIXEL',
        default = 1)

    border_offset = IntProperty(
        name = 'Border size',
        description = 'Border size in pixels\n  Note: DPI factored',
        min = 1,
        soft_max = 16,
        subtype = 'PIXEL',
        default = 8)

    logo_color = FloatVectorProperty(
        name = 'Logo color',
        description = 'Color used for the KIT OPS logo',
        min = 0,
        max = 1,
        size = 4,
        precision = 3,
        subtype = 'COLOR',
        default = (1.0, 0.030, 0.0, 0.9))

    off_color = FloatVectorProperty(
        name = 'Off color',
        description = 'Color used for the KIT OPS logo when there is not an active insert with an insert target',
        min = 0,
        max = 1,
        size = 4,
        precision = 3,
        subtype = 'COLOR',
        default = (0.448, 0.448, 0.448, 0.1))

    logo_size = IntProperty(
        name = 'Logo size',
        description = 'Logo size in the 3d view\n  Note: DPI factored',
        min = 1,
        soft_max = 500,
        subtype = 'PIXEL',
        default = 10)

    logo_padding_x = IntProperty(
        name = 'Logo padding x',
        description = 'Logo padding in the 3d view from the border corner\n  Note: DPI factored',
        subtype = 'PIXEL',
        default = 18)

    logo_padding_y = IntProperty(
        name = 'Logo padding y',
        description = 'Logo padding in the 3d view from the border corner\n  Note: DPI factored',
        subtype = 'PIXEL',
        default = 12)

    logo_auto_offset = BoolProperty(
        name = 'Logo auto offset',
        description = 'Offset the logo automatically for HardOps and BoxCutter',
        default = True)

    text_color = FloatVectorProperty(
        name = 'Text color',
        description = 'Color used for the KIT OPS help text',
        min = 0,
        max = 1,
        size = 4,
        precision = 3,
        subtype = 'COLOR',
        default = (1.0, 0.030, 0.0, 0.9))

    # displayed in panel
    mode = EnumProperty(
        name = 'Mode',
        description = 'Insert mode',
        items = [
            ('REGULAR', 'Regular', 'Stop creating modifiers for all INSERT objects except for new INSERTS\n  Note: Removes all insert targets'),
            ('SMART', 'Smart', 'Create modifiers as you work with an INSERT on the target object')],
        update = update.mode,
        default = 'SMART')

    insert_scale = EnumProperty(
        name = 'Insert Scale',
        description = 'Insert scale mode based on the active object when adding an INSERT',
        items = [
            ('LARGE', 'Large', ''),
            ('MEDIUM', 'Medium', ''),
            ('SMALL', 'Small', '')],
        update = update.insert_scale,
        default = 'LARGE')

    large_scale = IntProperty(
        name = 'Primary Scale',
        description = 'Percentage of object size when adding an INSERT for primary',
        min = 0,
        soft_max = 200,
        subtype = 'PERCENTAGE',
        update = update.insert_scale,
        default = 100)

    medium_scale = IntProperty(
        name = 'Secondary Scale',
        description = 'Percentage of object size when adding an INSERT for secondary',
        min = 0,
        soft_max = 200,
        subtype = 'PERCENTAGE',
        update = update.insert_scale,
        default = 50)

    small_scale = IntProperty(
        name = 'Tertiary Scale',
        description = 'Percentage of object size when adding an INSERT for tertiary',
        min = 0,
        soft_max = 200,
        subtype = 'PERCENTAGE',
        update = update.insert_scale,
        default = 25)

    def draw(self, context):
        layout = self.layout

        column = layout.column(align=True)

        row = column.row(align=True)
        row.prop(self, 'context', expand=True)

        box = column.box()

        box.separator()
        getattr(self, self.context.lower())(context, box)
        box.separator()

    def general(self, context, layout):
        row = layout.row()
        row.label(text='Author:')
        row.prop(self, 'author', text='')

        row = layout.row()
        row.label(text='Toolshelf category:')
        row.prop(self, 'category', text='')

        split = layout.split()
        split.label(text='Popup location:')

        sub = split.row()
        sub.prop(self, 'popup_location', expand=True)

        row = layout.row()
        row.label(text='INSERT offset X:')
        row.prop(self, 'insert_offset_x', text='')

        row = layout.row()
        row.label(text='INSERT offset Y:')
        row.prop(self, 'insert_offset_y', text='')

        row = layout.row()
        row.label(text='Clean list names:')
        row.prop(self, 'clean_names', text='')

        row = layout.row()
        row.label(text='Thumbnail labels:')
        row.prop(self, 'thumbnail_labels', text='')

        row = layout.row()
        row.label(text='Thumbnails in list:')
        row.prop(self, 'thumbnails_in_list', text='')

        row = layout.row()
        row.label(text='Enable auto select in regular mode:')
        row.prop(self, 'enable_auto_select', text='')

    def theme(self, context, layout):
        row = layout.row()
        row.label(text='Border color:')
        row.prop(self, 'border_color', text='')

        row = layout.row()
        row.label(text='Border size:')
        row.prop(self, 'border_size', text='')

        row = layout.row()
        row.label(text='Border offset:')
        row.prop(self, 'border_offset', text='')

        row = layout.row()
        row.label(text='Logo color:')
        row.prop(self, 'logo_color', text='')

        row = layout.row()
        row.label(text='Off color:')
        row.prop(self, 'off_color', text='')

        row = layout.row()
        row.label(text='Logo size:')
        row.prop(self, 'logo_size', text='')

        row = layout.row()
        row.label(text='Logo padding x:')
        row.prop(self, 'logo_padding_x', text='')

        row = layout.row()
        row.label(text='Logo padding y:')
        row.prop(self, 'logo_padding_y', text='')

        row = layout.row()
        row.label(text='Logo auto offset:')
        row.prop(self, 'logo_auto_offset', text='')

        row = layout.row()
        row.label(text='Text color:')
        row.prop(self, 'text_color', text='')

    def filepaths(self, context, layout):

        for index, folder in enumerate(self.folders):
            row = layout.row()
            split = row.split(percentage=0.2)
            split.prop(folder, 'name', text='', emboss=False)

            split.prop(folder, 'location', text='')

            op = row.operator('kitops.remove_kpack_path', text='', emboss=False, icon='PANEL_CLOSE')
            op.index = index

        row = layout.row()
        split = row.split(percentage=0.2)

        split.separator()
        split.operator('kitops.add_kpack_path', text='', icon='ZOOMIN')

        sub = row.row()
        sub.operator('kitops.refresh_kpacks', text='', emboss=False, icon='FILE_REFRESH')
