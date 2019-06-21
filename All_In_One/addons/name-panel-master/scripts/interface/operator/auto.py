
# imports
import bpy
from bpy.props import IntProperty
from bpy.types import Operator
from . import shared
from ...function import auto

# addon
addon = bpy.context.user_preferences.addons.get(__name__.partition('.')[0])

# name
class name(Operator):
  '''
    Automatically name datablocks based on type.
  '''
  bl_idname = 'view3d.auto_name'
  bl_label = 'Auto Name'
  bl_description = 'Automatically name datablocks based on type.'
  bl_options = {'UNDO'}

  # count
  count = IntProperty(
    name = 'Total named',
    description = 'Total number of names changed during the batch auto name process',
    default = 0
  )

  # object
  objects = []

  # constraints
  constraints = []

  # modifiers
  modifiers = []

  # cameras
  cameras = []

  # meshes
  meshes = []

  # curves
  curves = []

  # lamps
  lamps = []

  # lattices
  lattices = []

  # metaballs
  metaballs = []

  # speakers
  speakers = []

  # armatures
  armatures = []

  # poll
  @classmethod
  def poll(cls, context):
    '''
      Space data type must be in 3D view.
    '''
    return context.space_data.type in 'VIEW_3D'

  # check
  def check(self, context):
    return True

  # draw
  def draw(self, context):
    '''
      Draw the operator panel/menu.
    '''

    # layout
    layout = self.layout

    # option
    option = context.window_manager.AutoName

    # label
    layout.label(text='Targets:')

    # row
    row = layout.row(align=True)

    # mode
    row.prop(option, 'mode', expand=True)

    # op: reset name panel settings
    op = row.operator('wm.reset_name_panel_settings', text='', icon='LOAD_FACTORY')
    op.panel = False
    op.auto = True
    op.names = True
    op.name = False
    op.copy = False

    # column
    column = layout.column(align=True)

    # split
    split = column.split(align=True)

    # objects
    split.prop(option, 'objects', text='', icon='OBJECT_DATA')

    # constraints
    split.prop(option, 'constraints', text='', icon='CONSTRAINT')

    # modifiers
    split.prop(option, 'modifiers', text='', icon='MODIFIER')

    # object data
    split.prop(option, 'objectData', text='', icon='MESH_DATA')

    # bone constraints
    split.prop(option, 'boneConstraints', text='', icon='CONSTRAINT_BONE')

    # column
    column = layout.column()

    # object type
    column.prop(option, 'objectType', text='')

    # constraint type
    column.prop(option, 'constraintType', text='')

    # modifier type
    column.prop(option, 'modifierType', text='')

    # column
    column = layout.column()

    # label
    column.label(text='Name Settings:')

    # split
    split = column.split(align=True)

    # batch auto name object names
    split.operator('view3d.auto_name_object_names', text='Objects')

    # batch auto name constraint names
    split.operator('view3d.auto_name_constraint_names', text='Constraints')

    # batch auto name modifier names
    split.operator('view3d.auto_name_modifier_names', text='Modifiers')

    # batch auto name object data names
    split.operator('view3d.auto_name_object_data_names', text='Object Data')

    # column
    column = layout.column(align=True)

    # sort
    shared.sort(column, context.window_manager.BatchShared)

    # count
    shared.count(column, context.window_manager.BatchShared)

  # execute
  def execute(self, context):
    '''
      Execute the operator.
    '''

    # main
    auto.main(self, context)

    # report
    self.report({'INFO'}, 'Datablocks named: ' + str(self.count))

    # count
    self.count = 0

    return {'FINISHED'}

  # invoke
  def invoke(self, context, event):
    '''
      Invoke the operator panel/menu, control its width.
    '''
    size = 330 if not context.window_manager.BatchShared.largePopups else 460
    context.window_manager.invoke_props_dialog(self, width=size)
    return {'RUNNING_MODAL'}

# objects
class objects(Operator):
  '''
    Invoke the auto name object names dialogue.
  '''
  bl_idname = 'view3d.auto_name_object_names'
  bl_label = 'Object Names:'
  bl_description = 'Change the names used for objects.'
  bl_options = {'UNDO'}

  # draw
  def draw(self, context):
    '''
      Draw the operator panel/menu.
    '''

    # layout
    layout = self.layout

    # option
    option = context.scene.ObjectNames

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
    size = 150 if not context.window_manager.BatchShared.largePopups else 225
    context.window_manager.invoke_props_dialog(self, width=size)
    return {'RUNNING_MODAL'}

# constraints
class constraints(Operator):
  '''
    Invoke the auto name constraint names dialogue.
  '''
  bl_idname = 'view3d.auto_name_constraint_names'
  bl_label = 'Constraint Names:'
  bl_description = 'Change the names used for constraints.'
  bl_options = {'UNDO'}

  # draw
  def draw(self, context):
    '''
      Draw the operator panel/menu.
    '''

    # layout
    layout = self.layout

    # option
    option = context.scene.ConstraintNames

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
    size = 600 if not context.window_manager.BatchShared.largePopups else 900
    context.window_manager.invoke_props_dialog(self, width=size)
    return {'RUNNING_MODAL'}

# modifiers
class modifiers(Operator):
  '''
    Invoke the auto name modifier names dialogue.
  '''
  bl_idname = 'view3d.auto_name_modifier_names'
  bl_label = 'Modifier Names:'
  bl_description = 'Change the names used for modifiers.'
  bl_options = {'UNDO'}

  # draw
  def draw(self, context):
    '''
      Draw the operator panel/menu.
    '''

    # layout
    layout = self.layout

    # option
    option = context.scene.ModifierNames

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
    size = 600 if not context.window_manager.BatchShared.largePopups else 900
    context.window_manager.invoke_props_dialog(self, width=size)
    return {'RUNNING_MODAL'}

# objects
class objectData(Operator):
  '''
    Invoke the auto name object data names dialogue.
  '''
  bl_idname = 'view3d.auto_name_object_data_names'
  bl_label = 'Object Data Names:'
  bl_description = 'Change the names used for objects data.'
  bl_options = {'UNDO'}

  # draw
  def draw(self, context):
    '''
      Draw the operator panel/menu.
    '''

    # layout
    layout = self.layout

    # option
    option = context.scene.ObjectDataNames

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
    size = 150 if not context.window_manager.BatchShared.largePopups else 225
    context.window_manager.invoke_props_dialog(self, width=size)
    return {'RUNNING_MODAL'}
