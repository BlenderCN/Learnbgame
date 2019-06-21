
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
import bpy
from bpy.types import Operator
from ..function import auto

# addon
addon = bpy.context.user_preferences.addons.get(__name__.partition('.')[0])

# name
class name(Operator):
  '''
    Automatically name datablocks based on type.
  '''
  bl_idname = 'view3d.batch_auto_name'
  bl_label = 'Auto Name'
  bl_description = 'Automatically name datablocks based on type.'
  bl_options = {'UNDO'}

  # poll
  @classmethod
  def poll(cls, context):
    '''
      Space data type must be in 3D view.
    '''
    return context.space_data.type in 'VIEW_3D'

  # draw
  def draw(self, context):
    '''
      Draw the operator panel/menu.
    '''

    # layout
    layout = self.layout

    # option
    option = context.scene.BatchAutoName

    # batch type
    layout.prop(option, 'mode', expand=True)

    # column
    column = layout.column(align=True)

    # type row
    split = column.split(align=True)
    split.prop(option, 'objects', text='', icon='OBJECT_DATA')
    split.prop(option, 'constraints', text='', icon='CONSTRAINT')
    split.prop(option, 'modifiers', text='', icon='MODIFIER')
    split.prop(option, 'objectData', text='', icon='MESH_DATA')
    split.prop(option, 'boneConstraints', text='', icon='CONSTRAINT_BONE')

    # type filters
    column = layout.column()
    column.prop(option, 'objectType', text='')
    column.prop(option, 'constraintType', text='')
    column.prop(option, 'modifierType', text='')

    # settings
    column = layout.column()
    column.label(text='Name Settings:')
    split = column.split(align=True)
    split.operator('view3d.batch_auto_name_object_names', text='Objects')
    split.operator('view3d.batch_auto_name_constraint_names', text='Constraints')
    split.operator('view3d.batch_auto_name_modifier_names', text='Modifiers')
    split.operator('view3d.batch_auto_name_object_data_names', text='Object Data')

  # execute
  def execute(self, context):
    '''
      Execute the operator.
    '''
    globalUndo = context.user_preferences.edit.use_global_undo
    context.user_preferences.edit.use_global_undo = False

    # main
    auto.main(context)

    context.user_preferences.edit.use_global_undo = globalUndo
    return {'FINISHED'}

  # invoke
  def invoke(self, context, event):
    '''
      Invoke the operator panel/menu, control its width.
    '''
    try:

      # size
      size = 320 if addon.preferences['largePopups'] == 0 else 450

    except:

      # size
      size = 320

    context.window_manager.invoke_props_dialog(self, width=size)
    return {'RUNNING_MODAL'}

# objects
class objects(Operator):
  '''
    Invoke the auto name object names dialogue.
  '''
  bl_idname = 'view3d.batch_auto_name_object_names'
  bl_label = 'Object Names:'
  bl_description = 'Change the names used for objects.'
  bl_options = {'REGISTER', 'UNDO'}

  # poll
  @classmethod
  def poll(cls, context):
    '''
      Space data type must be in 3D view.
    '''
    return context.space_data.type in 'VIEW_3D'

  # draw
  def draw(self, context):
    '''
      Draw the operator panel/menu.
    '''

    # layout
    layout = self.layout

    # option
    option = context.scene.BatchAutoName_ObjectNames

    # prefix
    layout.prop(option, 'prefix')

    # input fields

    # mesh
    column = layout.column()
    row = column.row()
    row.label(icon='OUTLINER_OB_MESH')
    row.prop(option, 'mesh', text='')

    # curve
    column = layout.column()
    row = column.row()
    row.label(icon='OUTLINER_OB_CURVE')
    row.prop(option, 'curve', text='')

    # surface
    column = layout.column()
    row = column.row()
    row.label(icon='OUTLINER_OB_SURFACE')
    row.prop(option, 'surface', text='')

    # meta
    column = layout.column()
    row = column.row()
    row.label(icon='OUTLINER_OB_META')
    row.prop(option, 'meta', text='')

    # font
    column = layout.column()
    row = column.row()
    row.label(icon='OUTLINER_OB_FONT')
    row.prop(option, 'font', text='')

    # armature
    column = layout.column()
    row = column.row()
    row.label(icon='OUTLINER_OB_ARMATURE')
    row.prop(option, 'armature', text='')

    # lattice
    column = layout.column()
    row = column.row()
    row.label(icon='OUTLINER_OB_LATTICE')
    row.prop(option, 'lattice', text='')

    # empty
    column = layout.column()
    row = column.row()
    row.label(icon='OUTLINER_OB_EMPTY')
    row.prop(option, 'empty', text='')

    # speaker
    column = layout.column()
    row = column.row()
    row.label(icon='OUTLINER_OB_SPEAKER')
    row.prop(option, 'speaker', text='')

    # camera
    column = layout.column()
    row = column.row()
    row.label(icon='OUTLINER_OB_CAMERA')
    row.prop(option, 'camera', text='')

    # lamp
    column = layout.column()
    row = column.row()
    row.label(icon='OUTLINER_OB_LAMP')
    row.prop(option, 'lamp', text='')

  # execute
  def execute(self, context):
    '''
      Execute the operator.
    '''
    # do nothing
    return {'FINISHED'}

  # invoke
  def invoke(self, context, event):
    '''
      Invoke the operator panel/menu, control its width.
    '''
    try:

      # size
      size = 150 if addon.preferences['largePopups'] == 0 else 225

    except:

      # size
      size = 150

    context.window_manager.invoke_props_dialog(self, width=size)
    return {'RUNNING_MODAL'}

# constraints
class constraints(Operator):
  '''
    Invoke the auto name constraint names dialogue.
  '''
  bl_idname = 'view3d.batch_auto_name_constraint_names'
  bl_label = 'Constraint Names:'
  bl_description = 'Change the names used for constraints.'
  bl_options = {'REGISTER', 'UNDO'}

  # poll
  @classmethod
  def poll(cls, context):
    '''
      Space data type must be in 3D view.
    '''
    return context.space_data.type in 'VIEW_3D'

  # draw
  def draw(self, context):
    '''
      Draw the operator panel/menu.
    '''

    # layout
    layout = self.layout

    # option
    option = context.scene.BatchAutoName_ConstraintNames

    # prefix
    layout.prop(option, 'prefix')

    # input fields
    split = layout.split()

    # motion tracking
    column = split.column()
    column.label(text='Motion Tracking')

    # camera solver
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'cameraSolver', text='')

    # follow track
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'followTrack', text='')

    # object solver
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'objectSolver', text='')

    # transform
    column = split.column()
    column.label(text='Transform')

    # copy location
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'copyLocation', text='')

    # copy rotation
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'copyRotation', text='')

    # copy scale
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'copyScale', text='')

    # copy transforms
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'copyTransforms', text='')

    # limit distance
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'limitDistance', text='')

    # limit location
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'limitLocation', text='')

    # limit rotation
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'limitRotation', text='')

    # limit scale
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'limitScale', text='')

    # maintain volume
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'maintainVolume', text='')

    # transform
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'transform', text='')

    # tracking
    column = split.column()
    column.label(text='Tracking')

    # clamp to
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'clampTo', text='')

    # damped track
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'dampedTrack', text='')

    # inverse kinematics
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'inverseKinematics', text='')

    # locked track
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'lockedTrack', text='')

    # spline inverse kinematics
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'splineInverseKinematics', text='')

    # stretch to
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'stretchTo', text='')

    # track to
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'trackTo', text='')

    # relationship
    column = split.column()
    column.label(text='Relationship')

    # action
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'action', text='')

    # child of
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'childOf', text='')

    # floor
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'floor', text='')

    # follow path
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'followPath', text='')

    # pivot
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'pivot', text='')

    # rigid body joint
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'rigidBodyJoint', text='')

    # shrinkwrap
    row = column.row()
    row.label(icon='CONSTRAINT_DATA')
    row.prop(option, 'shrinkwrap', text='')

  # execute
  def execute(self, context):
    '''
      Execute the operator.
    '''
    # do nothing
    return {'FINISHED'}

  # invoke
  def invoke(self, context, event):
    '''
      Invoke the operator panel/menu, control its width.
    '''
    try:

      # size
      size = 600 if addon.preferences['largePopups'] == 0 else 900

    except:

      # size
      size = 600

    context.window_manager.invoke_props_dialog(self, width=size)
    return {'RUNNING_MODAL'}

# modifiers
class modifiers(Operator):
  '''
    Invoke the auto name modifier names dialogue.
  '''
  bl_idname = 'view3d.batch_auto_name_modifier_names'
  bl_label = 'Modifier Names:'
  bl_description = 'Change the names used for modifiers.'
  bl_options = {'REGISTER', 'UNDO'}

  # poll
  @classmethod
  def poll(cls, context):
    '''
      Space data type must be in 3D view.
    '''
    return context.space_data.type in 'VIEW_3D'

  # draw
  def draw(self, context):
    '''
      Draw the operator panel/menu.
    '''

    # layout
    layout = self.layout

    # option
    option = context.scene.BatchAutoName_ModifierNames

    # prefix
    layout.prop(option, 'prefix')

    # input fields
    split = layout.split()

    # modify
    column = split.column()
    column.label(text='Modify')

    # data transfer
    row = column.row()
    row.label(icon='MOD_DATA_TRANSFER')
    row.prop(option, 'dataTransfer', text='')

    # mesh cache
    row = column.row()
    row.label(icon='MOD_MESHDEFORM')
    row.prop(option, 'meshCache', text='')

    # normal edit
    row = column.row()
    row.label(icon='MOD_NORMALEDIT')
    row.prop(option, 'normalEdit', text='')

    # uv project
    row = column.row()
    row.label(icon='MOD_UVPROJECT')
    row.prop(option, 'uvProject', text='')

    # uv warp
    row = column.row()
    row.label(icon='MOD_UVPROJECT')
    row.prop(option, 'uvWarp', text='')

    # vertex weight edit
    row = column.row()
    row.label(icon='MOD_VERTEX_WEIGHT')
    row.prop(option, 'vertexWeightEdit', text='')

    # vertex weight mix
    row = column.row()
    row.label(icon='MOD_VERTEX_WEIGHT')
    row.prop(option, 'vertexWeightMix', text='')

    # vertex weight proximity
    row = column.row()
    row.label(icon='MOD_VERTEX_WEIGHT')
    row.prop(option, 'vertexWeightProximity', text='')

    # generate
    column = split.column()
    column.label(text='Generate')

    # array
    row = column.row()
    row.label(icon='MOD_ARRAY')
    row.prop(option, 'array', text='')

    # bevel
    row = column.row()
    row.label(icon='MOD_BEVEL')
    row.prop(option, 'bevel', text='')

    # boolean
    row = column.row()
    row.label(icon='MOD_BOOLEAN')
    row.prop(option, 'boolean', text='')

    # build
    row = column.row()
    row.label(icon='MOD_BUILD')
    row.prop(option, 'build', text='')

    # decimate
    row = column.row()
    row.label(icon='MOD_DECIM')
    row.prop(option, 'decimate', text='')

    # edge split
    row = column.row()
    row.label(icon='MOD_EDGESPLIT')
    row.prop(option, 'edgeSplit', text='')

    # mask
    row = column.row()
    row.label(icon='MOD_MASK')
    row.prop(option, 'mask', text='')

    # mirror
    row = column.row()
    row.label(icon='MOD_MIRROR')
    row.prop(option, 'mirror', text='')

    # multiresolution
    row = column.row()
    row.label(icon='MOD_MULTIRES')
    row.prop(option, 'multiresolution', text='')

    # remesh
    row = column.row()
    row.label(icon='MOD_REMESH')
    row.prop(option, 'remesh', text='')

    # screw
    row = column.row()
    row.label(icon='MOD_SCREW')
    row.prop(option, 'screw', text='')

    # skin
    row = column.row()
    row.label(icon='MOD_SKIN')
    row.prop(option, 'skin', text='')

    # solidify
    row = column.row()
    row.label(icon='MOD_SOLIDIFY')
    row.prop(option, 'solidify', text='')

    # subdivision surface
    row = column.row()
    row.label(icon='MOD_SUBSURF')
    row.prop(option, 'subdivisionSurface', text='')

    # triangulate
    row = column.row()
    row.label(icon='MOD_TRIANGULATE')
    row.prop(option, 'triangulate', text='')

    # wireframe
    row = column.row()
    row.label(icon='MOD_WIREFRAME')
    row.prop(option, 'wireframe', text='')

    # deform
    column = split.column()
    column.label(text='Deform')

    # armature
    row = column.row()
    row.label(icon='MOD_ARMATURE')
    row.prop(option, 'armature', text='')

    # cast
    row = column.row()
    row.label(icon='MOD_CAST')
    row.prop(option, 'cast', text='')

    # corrective smooth
    row = column.row()
    row.label(icon='MOD_SMOOTH')
    row.prop(option, 'correctiveSmooth', text='')

    # curve
    row = column.row()
    row.label(icon='MOD_CURVE')
    row.prop(option, 'curve', text='')

    # displace
    row = column.row()
    row.label(icon='MOD_DISPLACE')
    row.prop(option, 'displace', text='')

    # hook
    row = column.row()
    row.label(icon='HOOK')
    row.prop(option, 'hook', text='')

    # laplacian smooth
    row = column.row()
    row.label(icon='MOD_SMOOTH')
    row.prop(option, 'laplacianSmooth', text='')

    # laplacian deform
    row = column.row()
    row.label(icon='MOD_MESHDEFORM')
    row.prop(option, 'laplacianDeform', text='')

    # lattice
    row = column.row()
    row.label(icon='MOD_LATTICE')
    row.prop(option, 'lattice', text='')

    # mesh deform
    row = column.row()
    row.label(icon='MOD_MESHDEFORM')
    row.prop(option, 'meshDeform', text='')

    # shrinkwrap
    row = column.row()
    row.label(icon='MOD_SHRINKWRAP')
    row.prop(option, 'shrinkwrap', text='')

    # simple deform
    row = column.row()
    row.label(icon='MOD_SIMPLEDEFORM')
    row.prop(option, 'simpleDeform', text='')

    # smooth
    row = column.row()
    row.label(icon='MOD_SMOOTH')
    row.prop(option, 'smooth', text='')

    # warp
    row = column.row()
    row.label(icon='MOD_WARP')
    row.prop(option, 'warp', text='')

    # wave
    row = column.row()
    row.label(icon='MOD_WAVE')
    row.prop(option, 'wave', text='')

    # simulate
    column = split.column()
    column.label(text='Simulate')

    # cloth
    row = column.row()
    row.label(icon='MOD_CLOTH')
    row.prop(option, 'cloth', text='')

    # collision
    row = column.row()
    row.label(icon='MOD_PHYSICS')
    row.prop(option, 'collision', text='')

    # dynamic paint
    row = column.row()
    row.label(icon='MOD_DYNAMICPAINT')
    row.prop(option, 'dynamicPaint', text='')

    # explode
    row = column.row()
    row.label(icon='MOD_EXPLODE')
    row.prop(option, 'explode', text='')

    # fluid simulation
    row = column.row()
    row.label(icon='MOD_FLUIDSIM')
    row.prop(option, 'fluidSimulation', text='')

    # ocean
    row = column.row()
    row.label(icon='MOD_OCEAN')
    row.prop(option, 'ocean', text='')

    # particle instance
    row = column.row()
    row.label(icon='MOD_PARTICLES')
    row.prop(option, 'particleInstance', text='')

    # particle system
    row = column.row()
    row.label(icon='MOD_PARTICLES')
    row.prop(option, 'particleSystem', text='')

    # smoke
    row = column.row()
    row.label(icon='MOD_SMOKE')
    row.prop(option, 'smoke', text='')

    # soft body
    row = column.row()
    row.label(icon='MOD_SOFT')
    row.prop(option, 'softBody', text='')

  # execute
  def execute(self, context):
    '''
      Execute the operator.
    '''
    # do nothing
    return {'FINISHED'}

  # invoke
  def invoke(self, context, event):
    '''
      Invoke the operator panel/menu, control its width.
    '''
    try:

      # size
      size = 600 if addon.preferences['largePopups'] == 0 else 900

    except:

      # size
      size = 600

    context.window_manager.invoke_props_dialog(self, width=size)
    return {'RUNNING_MODAL'}

# objects
class objectData(Operator):
  '''
    Invoke the auto name object data names dialogue.
  '''
  bl_idname = 'view3d.batch_auto_name_object_data_names'
  bl_label = 'Object Data Names:'
  bl_description = 'Change the names used for objects data.'
  bl_options = {'REGISTER', 'UNDO'}

  # poll
  @classmethod
  def poll(cls, context):
    '''
      Space data type must be in 3D view.
    '''
    return context.space_data.type in 'VIEW_3D'

  # draw
  def draw(self, context):
    '''
      Draw the operator panel/menu.
    '''

    # layout
    layout = self.layout

    # option
    option = context.scene.BatchAutoName_ObjectDataNames


    # prefix
    layout.prop(option, 'prefix')

    # input fields

    # mesh
    column = layout.column()
    row = column.row()
    row.label(icon='MESH_DATA')
    row.prop(option, 'mesh', text='')

    # curve
    column = layout.column()
    row = column.row()
    row.label(icon='CURVE_DATA')
    row.prop(option, 'curve', text='')

    # surface
    column = layout.column()
    row = column.row()
    row.label(icon='SURFACE_DATA')
    row.prop(option, 'surface', text='')

    # meta
    column = layout.column()
    row = column.row()
    row.label(icon='META_DATA')
    row.prop(option, 'meta', text='')

    # font
    column = layout.column()
    row = column.row()
    row.label(icon='FONT_DATA')
    row.prop(option, 'font', text='')

    # armature
    column = layout.column()
    row = column.row()
    row.label(icon='ARMATURE_DATA')
    row.prop(option, 'armature', text='')

    # lattice
    column = layout.column()
    row = column.row()
    row.label(icon='LATTICE_DATA')
    row.prop(option, 'lattice', text='')

    # speaker
    column = layout.column()
    row = column.row()
    row.label(icon='SPEAKER')
    row.prop(option, 'speaker', text='')

    # camera
    column = layout.column()
    row = column.row()
    row.label(icon='CAMERA_DATA')
    row.prop(option, 'camera', text='')

    # lamp
    column = layout.column()
    row = column.row()
    row.label(icon='LAMP_DATA')
    row.prop(option, 'lamp', text='')

  # execute
  def execute(self, context):
    '''
      Execute the operator.
    '''
    # do nothing
    return {'FINISHED'}

  # invoke
  def invoke(self, context, event):
    '''
      Invoke the operator panel/menu, control its width.
    '''
    try:

      # size
      size = 150 if addon.preferences['largePopups'] == 0 else 225

    except:

      # size
      size = 150

    context.window_manager.invoke_props_dialog(self, width=size)
    return {'RUNNING_MODAL'}
