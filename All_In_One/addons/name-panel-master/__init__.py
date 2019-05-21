
'''
Name Panel Addon
Copyright (C) 2016 Trentin Frederick

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.
'''

# addon info
bl_info = {
  'name': 'Name Panel',
  'author': 'Trentin Frederick (proxe)',
  'version': (1, 6, 72),
  'blender': (2, 68, 0),
  'location': '3D View \N{Rightwards Arrow} Tool or Property Shelf \N{Rightwards Arrow} Name',
  'description': 'In panel datablock name stack with shortcut and batch name tools.',
  'wiki_url': 'https://cgcookiemarkets.com/all-products/name-panel/?view=docs',
  'tracker_url': 'https://github.com/trentinfrederick/name-panel/issues',
  'category': '3D View'
}

# imports
import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import *
from .scripts import options as PropertyGroup
from .scripts.defaults import defaults
from .scripts.interface import button, menu, name, properties
from .scripts.interface.operator import auto, batch, copy, icon, navigate, options
from .scripts.interface.operator.preferences import name as Pname
from .scripts.interface.operator.preferences import auto as Pauto
from .scripts.interface.operator.preferences import batch as Pbatch
from .scripts.interface.operator.preferences import copy as Pcopy

# save
class save(Operator):
  '''
    Save current property positions as the default, update.
  '''
  bl_idname = 'wm.save_name_panel_defaults'
  bl_label = 'Save'
  bl_description = 'Save current addon options as default and update panel locations.'
  bl_options = {'INTERNAL'}

  # execute
  def execute(self, context):
    '''
      Execute the operator.
    '''

    # location
    location = context.scene.NamePanel.location

    # is location tools
    if location == 'TOOLS':

      # doesnt have tools name
      if not hasattr(bpy.types, 'VIEW3D_PT_TOOLS_name'):
        bpy.utils.register_class(name.toolsName)

      # has ui name
      if hasattr(bpy.types, 'VIEW3D_PT_UI_name')  :
        bpy.utils.unregister_class(name.UIName)

    # isnt location tools
    else:

      # doesnt have ui name
      if not hasattr(bpy.types, 'VIEW3D_PT_UI_name'):
        bpy.utils.register_class(name.UIName)

      # has tools name
      if hasattr(bpy.types, 'VIEW3D_PT_TOOLS_name'):
        bpy.utils.unregister_class(name.toolsName)

    # location
    location = context.window_manager.PropertyPanel.location

    # is location tools
    if location == 'TOOLS':

      # doesnt have tools properties
      if not hasattr(bpy.types, 'VIEW3D_PT_TOOLS_properties'):
        bpy.utils.register_class(properties.toolsProperties)

      # has ui properties
      if hasattr(bpy.types, 'VIEW3D_PT_UI_properties'):
        bpy.utils.unregister_class(properties.UIProperties)

    # isnt location tools
    else:

      # doesnt have ui properties
      if not hasattr(bpy.types, 'VIEW3D_PT_UI_properties'):
        bpy.utils.register_class(properties.UIProperties)

      # has tools properties
      if hasattr(bpy.types, 'VIEW3D_PT_TOOLS_properties'):
        bpy.utils.unregister_class(properties.toolsProperties)

    # imports
    from .scripts.function.preferences import options

    # main
    options.main(context)
    return {'FINISHED'}

# preferences
class preferences(AddonPreferences):
  '''
    Add-on user preferences.
  '''
  bl_idname = __name__

  # draw
  def draw(self, context):

    # layout
    layout = self.layout

    # box
    box = layout.box()

    box.label(text='Defaults:')

    # row
    row = box.row(align=True)

    # scale y
    row.scale_y = 1.5

    # operator; name panel
    row.operator('wm.name_panel_defaults', text='Panel')

    # operator; auto name
    row.operator('wm.auto_name_defaults', text='Auto Name')

    # operator; batch name defaults
    op = row.operator('wm.batch_name_defaults', text='Batch Name')
    op.quickBatch = False

    # operator; batch name defaults
    op = row.operator('wm.batch_name_defaults', text='Quick Batch')
    op.quickBatch = True

    # operator; batch name copy
    row.operator('wm.copy_name_defaults', text='Copy Name')

    # label
    box.label(text='Name Panel Location:')

    # row
    row = box.row()

    # location
    row.prop(context.scene.NamePanel, 'location', expand=True)

    # label
    box.label(text='Property Panel Location:')

    # row
    row = box.row()

    # location
    row.prop(context.window_manager.PropertyPanel, 'location', expand=True)
    box.separator()

    # row
    row = box.row()

    # pop ups
    row.prop(context.window_manager.BatchShared, 'largePopups')

    # row
    row = box.row()

    # scale y
    row.scale_y = 1.5

    # alignment right
    row.alignment = 'RIGHT'

    # operator; save name panel defaults
    row.operator('wm.save_name_panel_defaults', text='Save')

    # split
    split = layout.split(align=True)

    # scale y
    split.scale_y = 2

    # operator; url open
    prop = split.operator('wm.url_open', text='Donate')

    # donate
    prop.url = 'https://paypal.me/proxe'

    # operator; url open
    prop = split.operator('wm.url_open', text='Blender Market')

    # blender market
    prop.url = 'https://cgcookiemarkets.com/all-products/name-panel/'

    # operator; url open
    prop = split.operator('wm.url_open', text='Gumroad')

    # gumroad
    prop.url = 'https://gumroad.com/l/UyXd'

    # operator; url open
    prop = split.operator('wm.url_open', text='Blender Artists')

    # blender artists
    prop.url = 'http://blenderartists.org/forum/showthread.php?272086'

    # operator; url open
    prop = split.operator('wm.url_open', text='Github')

    # github
    prop.url = 'https://github.com/trentinfrederick/name-panel'

# register
def register():
  '''
    Register
  '''

  # register module
  bpy.utils.register_module(__name__)

  # batch shared
  bpy.types.WindowManager.BatchShared = PointerProperty(
    type = PropertyGroup.batch.shared,
    name = 'Batch Shared Settings',
    description = 'Storage location for shared settings of batch name operators.'
  )

  # auto name
  bpy.types.WindowManager.AutoName = PointerProperty(
    type = PropertyGroup.batch.auto.name,
    name = 'Batch Auto Name Settings',
    description = 'Storage location for the auto name operator settings.'
  )

  # object names
  bpy.types.Scene.ObjectNames = PointerProperty(
    type = PropertyGroup.batch.auto.objects,
    name = 'Object Name Settings',
    description = 'Storage location for the object names used during the auto name operation.'
  )

  # constraint names
  bpy.types.Scene.ConstraintNames = PointerProperty(
    type = PropertyGroup.batch.auto.constraints,
    name = 'Constraint Name Settings',
    description = 'Storage location for the constraint names used during the auto name operation.'
  )

  # modifier names
  bpy.types.Scene.ModifierNames = PointerProperty(
    type = PropertyGroup.batch.auto.modifiers,
    name = 'Modifier Name Settings',
    description = 'Storage location for the modifier names used during the auto name operation.'
  )

  # object data names
  bpy.types.Scene.ObjectDataNames = PointerProperty(
    type = PropertyGroup.batch.auto.objectData,
    name = 'Object Data Name Settings',
    description = 'Storage location for the object data names used during the auto name operation.'
  )

  # batch name
  bpy.types.WindowManager.BatchName = PointerProperty(
    type = PropertyGroup.batch.name,
    name = 'Batch Name Settings',
    description = 'Storage location for the batch name operator settings.'
  )

  # copy name
  bpy.types.WindowManager.CopyName = PointerProperty(
    type = PropertyGroup.batch.copy,
    name = 'Copy Name Settings',
    description = 'Storage location for the copy name operator settings.'
  )

  # name panel
  bpy.types.Scene.NamePanel = PointerProperty(
    type = PropertyGroup.name,
    name = 'Name Panel Settings',
    description = 'Storage location for the name panel settings.'
  )

  # property panel
  bpy.types.WindowManager.PropertyPanel = PointerProperty(
    type = PropertyGroup.properties,
    name = 'Property Panel Settings',
    description = 'Storage location for the property panel settings.'
  )

  # append
  bpy.types.OUTLINER_HT_header.append(button.batchName)

  # name panel location

  # location
  location = defaults['name panel']['location']

  # is location tools
  if location == 'TOOLS':
    bpy.utils.unregister_class(name.UIName)

  # isnt location tools
  else:
    bpy.utils.unregister_class(name.toolsName)

  # location
  location = defaults['properties panel']['location']

  # is location tools
  if location == 'TOOLS':
    bpy.utils.unregister_class(properties.UIProperties)

  # isnt location tools
  else:
    bpy.utils.unregister_class(properties.toolsProperties)

# unregister
def unregister():
  '''
    Unregister
  '''

  # unregister module
  bpy.utils.unregister_module(__name__)

  # delete pointer properties
  del bpy.types.WindowManager.AutoName
  del bpy.types.Scene.ObjectNames
  del bpy.types.Scene.ConstraintNames
  del bpy.types.Scene.ModifierNames
  del bpy.types.Scene.ObjectDataNames
  del bpy.types.WindowManager.BatchName
  del bpy.types.WindowManager.CopyName
  del bpy.types.Scene.NamePanel
  del bpy.types.WindowManager.PropertyPanel

  # remove batch name button
  bpy.types.OUTLINER_HT_header.remove(button.batchName)

if __name__ == '__main__':
  register()
