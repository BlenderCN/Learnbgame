
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation; either version 2 of the License, or (at your option)
#  any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# imports
from .constraints import ConstraintButtons
from .modifiers import ModifierButtons

# object
def Object(self, context, layout, datablock):
  '''
    The object properties.
  '''

  # label
  layout.label(text='Display:')

  # split
  split = layout.split()

  # column
  column = split.column()

  # show name
  column.prop(datablock, 'show_name', text='Name')

  # show axis
  column.prop(datablock, 'show_axis', text='Axis')

  # type
  if datablock.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'} or datablock.dupli_type != None:

    # show wire
    column.prop(datablock, 'show_wire', text='Wire')

  # type
  if datablock.type == 'MESH' or datablock.dupli_type != None:

    # show all edges
    column.prop(datablock, 'show_all_edges')

  # column
  column = split.column()

  # row
  row = column.row()

  # show bounds
  row.prop(datablock, 'show_bounds', text='Bounds')

  # sub
  sub = row.row()

  # active
  sub.active = datablock.show_bounds

  # draw bounds type
  sub.prop(datablock, 'draw_bounds_type', text='')

  # type
  if datablock.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'}:

    # show texture space
    column.prop(datablock, 'show_texture_space', text='Texture Space')

  # show xray
  column.prop(datablock, 'show_x_ray', text='X-Ray')

  # type
  if datablock.type == 'MESH' or datablock.type == 'EMPTY' and datablock.empty_draw_type == 'IMAGE':

    # show transparent
    column.prop(datablock, 'show_transparent', text='Transparency')

  # split
  split = layout.split()

  # column
  column = split.column()

  # type
  if datablock.type in {'CAMERA', 'EMPTY'}:

    # active
    column.active = datablock.dupli_type != None

    # label
    column.label(text='Maximum Dupli Draw Type:')

  # type
  else:

    # label
    column.label(text='Maximum Draw Type:')

  # draw type
  column.prop(datablock, 'draw_type', text='')

  # column
  column = split.column()

  # type
  if datablock.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT'} or datablock.type == 'EMPTY' and datablock.empty_draw_type == 'IMAGE':

    # label
    column.label(text='Object Color:')

    # color
    column.prop(datablock, 'color', text='')

  # separator
  layout.separator()

  # label
  layout.label(text='Relations:')

  # split
  split = layout.split()

  # column
  column = split.column()

  # layers
  column.prop(datablock, 'layers')

  # separator
  column.separator()

  # pass index
  column.prop(datablock, 'pass_index')

  # column
  column = split.column()

  # label
  column.label(text='Parent:')

  # parent
  column.prop(datablock, 'parent', text='')

  # sub
  sub = column.column()

  # active
  sub.active = datablock.parent is not None

  # parent type
  sub.prop(datablock, 'parent_type', text='')

  # parent
  if datablock.parent and datablock.parent_type == 'BONE' and datablock.parent.type == 'ARMATURE':

    # parent bone
    sub.prop_search(datablock, 'parent_bone', datablock.parent.data, 'bones', text='')

  # separator
  layout.separator()

  # cycles
  if context.scene.render.engine == 'CYCLES':

    # label
    layout.label(text='Cycles Settings:')

    # label
    layout.label(text='Ray Visibility:')

    # split
    split = layout.split()

    # column
    column = split.column()

    # camera
    column.prop(datablock.cycles_visibility, 'camera')

    # diffuse
    column.prop(datablock.cycles_visibility, 'diffuse')

    # glossy
    column.prop(datablock.cycles_visibility, 'glossy')

    # column
    column = split.column()

    # transmission
    column.prop(datablock.cycles_visibility, 'transmission')

    # scatter
    column.prop(datablock.cycles_visibility, 'scatter')

    # type
    if datablock.type != 'LAMP':

      # shadow
      column.prop(datablock.cycles_visibility, 'shadow')

    # column
    column = layout.column()

    # label
    column.label(text='Performance:')

    # row
    row = column.row()

    # active
    row.active = context.scene.render.use_simplify and context.scene.cycles.use_camera_cull

    # use camera cull
    row.prop(datablock.cycles, 'use_camera_cull')

# group
def Group(self, context, layout, datablock):
  '''
    The group properties.
  '''

  # separator
  layout.separator()

  # column
  column = layout.column()

  # # context
  # column.context_pointer_set('group', datablock)
  #
  # # row
  # row = column.row(align=True)
  #
  # # name
  # row.prop(datablock, 'name', text='')
  #
  # # remove
  # row.operator('object.group_remove', text='', icon='X')
  #
  # # specials
  # row.menu('GROUP_MT_specials', icon='COLLAPSEMENU', text='')

  # split
  split = column.split()

  # column
  column = split.column()

  # layers
  column.prop(datablock, 'layers', text='Dupli Visibility')

  # column
  column = split.column()

  # dulpi offset
  column.prop(datablock, 'dupli_offset', text='')

# action
def Action(self, context, layout, datablock):
  '''
    The action properties.
  '''

  # label
  layout.label(text='Nothing to show')

# grease pencil
def GreasePencil(self, context, layout, datablock):
  '''
  The grease pencil properties.
  '''

  # label
  layout.label(text='Nothing to show')

# constraint
def Constraint(self, context, layout, datablock):
  '''
    The constraint properties.
  '''

  # label
  layout.label(text=datablock.name + ':')

  # constraint buttons
  ConstraintButtons.main(self, context, layout, datablock)

# modifier
def Modifier(self, context, layout, object, datablock):
  '''
    The modifier properties.
  '''

  # label
  layout.label(text=datablock.name + ':')

  # modifier buttons
  ModifierButtons.main(self, context, layout, datablock, object)

# object data
def ObjectData(self, context, layout, datablock):
  '''
    The object data properties.
  '''

  # label
  layout.label(text='Nothing to show')

# bone group
def BoneGroup(self, context, layout, datablock):
  '''
    The bone group properties.
  '''

  # label
  layout.label(text='Nothing to show')

# bone
def Bone(self, context, layout, datablock):
  '''
    The bone properties.
  '''

  # label
  layout.label(text='Nothing to show')

# bone constraint
def BoneConstraint(self, context, layout, datablock):
  '''
    The bone constraints properties.
  '''

  # label
  layout.label(text=datablock.name + ':')

  # constraint buttons
  ConstraintButtons.main(self, context, layout, datablock)

# vertex group
def VertexGroup(self, context, layout, datablock):
  '''
    The vertex group properties.
  '''

  # label
  layout.label(text='Nothing to show')

# uv
def UV(self, context, layout, datablock):
  '''
    The UV properties.
  '''

  # label
  layout.label(text='Nothing to show')

# shapekey
def Shapekey(self, context, layout, datablock):
  '''
    The shapekey properties.
  '''

  # label
  layout.label(text='Nothing to show')

# vertex color
def VertexColor(self, context, layout, datablock):
  '''
    The vertex color properties.
  '''

  # label
  layout.label(text='Nothing to show')

# material
def Material(self, context, layout, datablock):
  '''
    The material properties.
  '''

  # label
  layout.label(text='Nothing to show')

# texture
def Texture(self, context, layout, datablock):
  '''
    The texture properties.
  '''

  # label
  layout.label(text='Nothing to show')

# particle system
def ParticleSystem(self, context, layout, datablock):
  '''
    The particle system properties.
  '''

  # label
  layout.label(text='Nothing to show')

# particle settings
def ParticleSettings(self, context, layout, datablock):
  '''
    The particle settings properties.
  '''

  # label
  layout.label(text='Nothing to show')
