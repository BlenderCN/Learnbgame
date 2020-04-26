
# imports
import bpy
from bpy.props import BoolProperty, IntProperty
from bpy.types import Operator
from . import shared
from ...function import batch

# addon
addon = bpy.context.user_preferences.addons.get(__name__.partition('.')[0])

# name
class name(Operator):
  '''
    Batch name datablocks.
  '''
  bl_idname = 'wm.batch_name'
  bl_label = 'Batch Name'
  bl_description = 'Batch name datablocks.'
  bl_options = {'UNDO'}

  # simple
  simple = BoolProperty(
    name = 'Simple Batch',
    description = 'Perform find & replace on names visible in the name panel.',
    default = False
  )

  # quick batch
  quickBatch = BoolProperty(
    name = 'Quick Batch',
    description = 'Quickly batch name datablocks visible in the name panel.',
    default = False
  )

  # tag
  tag = BoolProperty(
    name = 'Tag',
    description = 'Generic tag.',
    default = False
  )

  # count
  count = IntProperty(
    name = 'Total named',
    description = 'Total number of names changed during the batch name process',
    default = 0
  )

  # actions
  actions = []

  # action groups
  actionsGroups = []

  # grease pencils
  greasePencils = []

  # pencil layers
  pencilLayers = []

  # objects
  objects = []

  # groups
  groups = []

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

  # bone groups
  boneGroups = []

  # bones
  bones = []

  # vertex groups
  vertexGroups = []

  # shapekeys
  shapekeys = []

  # uvs
  uvs = []

  # vertex colors
  vertexColors = []

  # materials
  materials = []

  # textures
  textures = []

  # particle systems
  particleSystems = []

  # particle settings
  particleSettings = []

  # linestyles
  linestyles = []

  # sensors
  sensors = []

  # controllers
  controllers = []

  # actuators
  actuators = []

  # scenes
  scenes = []

  # render layers
  renderLayers = []

  # worlds
  worlds = []

  # libraries
  libraries = []

  # images
  images = []

  # masks
  masks = []

  # sequences
  sequences = []

  # movie clips
  movieClips = []

  # sounds
  sounds = []

  # screens
  screens = []

  # keying sets
  keyingSets = []

  # palettes
  palettes = []

  # brushes
  brushes = []

  # nodes
  nodes = []

  # node labels
  nodeLabels = []

  # node groups
  nodeGroups = []

  # texts
  texts = []

  # check
  def check(self, context):
    return True

  # draw
  def draw(self, context):
    '''
      Operator body.
    '''

    # layout
    layout = self.layout

    # option
    option = context.window_manager.BatchName

    # column
    column = layout.column(align=True)

    # is not quick batch
    if not self.quickBatch:

      # label
      column.label(text='Targets:')

      # row
      row = column.row(align=True)

      # batch type
      row.prop(option, 'mode', expand=True)

      # op: reset name panel settings
      op = row.operator('wm.reset_name_panel_settings', text='', icon='LOAD_FACTORY')
      op.panel = False
      op.auto = False
      op.names = False
      op.name = True
      op.copy = False

      # column
      column = layout.column(align=True)

      # row
      row = column.row(align=True)

      # scale x
      row.scale_x = 5

      # actions
      row.prop(option, 'actions', text='', icon='ACTION')

      # grease pencil
      row.prop(option, 'greasePencil', text='', icon='GREASEPENCIL')

      # objects
      row.prop(option, 'objects', text='', icon='OBJECT_DATA')

      # groups
      row.prop(option, 'groups', text='', icon='GROUP')

      # constraints
      row.prop(option, 'constraints', text='', icon='CONSTRAINT')

      # modifiers
      row.prop(option, 'modifiers', text='', icon='MODIFIER')

      # object data
      row.prop(option, 'objectData', text='', icon='MESH_DATA')

      # bones
      row.prop(option, 'bones', text='', icon='BONE_DATA')

      # bone groups
      row.prop(option, 'boneGroups', text='', icon='GROUP_BONE')

      # bone constraints
      row.prop(option, 'boneConstraints', text='', icon='CONSTRAINT_BONE')

      # row
      row = column.row(align=True)

      # scale x
      row.scale_x = 5

      # action groups
      row.prop(option, 'actionGroups', text='', icon='NLA')

      # pencil layers
      row.prop(option, 'pencilLayers', text='', icon='OOPS')

      # vertex groups
      row.prop(option, 'vertexGroups', text='', icon='GROUP_VERTEX')

      # shape keys
      row.prop(option, 'shapekeys', text='', icon='SHAPEKEY_DATA')

      # uvs
      row.prop(option, 'uvs', text='', icon='GROUP_UVS')

      # vertex colors
      row.prop(option, 'vertexColors', text='', icon='GROUP_VCOL')

      # materials
      row.prop(option, 'materials', text='', icon='MATERIAL')

      # textures
      row.prop(option, 'textures', text='', icon='TEXTURE')

      # particles systems
      row.prop(option, 'particleSystems', text='', icon='PARTICLES')

      # particle settings
      row.prop(option, 'particleSettings', text='', icon='MOD_PARTICLES')

      # column
      column = layout.column()

      # object type
      column.prop(option, 'objectType', text='')

      # constraint type
      column.prop(option, 'constraintType', text='')

      # modifier type
      column.prop(option, 'modifierType', text='')

      # column
      column = layout.column(align=True)

      # label
      column.label(text='Game Engine:')

      # row
      row = column.row(align=True)

      # sensors
      row.prop(option, 'sensors', text='Sensors', toggle=True)

      # controllers
      row.prop(option, 'controllers', text='Controllers', toggle=True)

      # actuators
      row.prop(option, 'actuators', text='Actuators', toggle=True)

      # column
      column = layout.column(align=True)

      # label
      column.label(text='Global:')

      # row
      row = column.row(align=True)

      # scale x
      row.scale_x = 5

      # scenes
      row.prop(option, 'scenes', text='', icon='SCENE_DATA')

      # render layers
      row.prop(option, 'renderLayers', text='', icon='RENDERLAYERS')

      # worlds
      row.prop(option, 'worlds', text='', icon='WORLD')

      # libraries
      row.prop(option, 'libraries', text='', icon='LIBRARY_DATA_DIRECT')

      # images
      row.prop(option, 'images', text='', icon='IMAGE_DATA')

      # masks
      row.prop(option, 'masks', text='', icon='MOD_MASK')

      # sequences
      row.prop(option, 'sequences', text='', icon='SEQUENCE')

      # movie clips
      row.prop(option, 'movieClips', text='', icon='CLIP')

      # sounds
      row.prop(option, 'sounds', text='', icon='SOUND')

      # row
      row = column.row(align=True)

      # scale x
      row.scale_x = 5

      # screens
      row.prop(option, 'screens', text='', icon='SPLITSCREEN')

      # keying sets
      row.prop(option, 'keyingSets', text='', icon='KEYINGSET')

      # palettes
      row.prop(option, 'palettes', text='', icon='COLOR')

      # brushes
      row.prop(option, 'brushes', text='', icon='BRUSH_DATA')

      # texts
      row.prop(option, 'texts', text='', icon='TEXT')

      # nodes
      row.prop(option, 'nodes', text='', icon='NODE_SEL')

      # node labels
      row.prop(option, 'nodeLabels', text='', icon='NODE')

      # frame nodes
      row.prop(option, 'frameNodes', text='', icon='FULLSCREEN')

      # node groups
      row.prop(option, 'nodeGroups', text='', icon='NODETREE')

      # column
      column = layout.column(align=True)

      # label
      column.label(text='Freestyle:')

      # row
      row = column.row(align=True)

      # scale x
      row.scale_x = 1.5

      # line sets
      row.prop(option, 'lineSets', text='', icon='BRUSH_TEXDRAW')

      # linestyles
      row.prop(option, 'linestyles', text='', icon='LINE_DATA')

      # linestyle modifiers
      row.prop(option, 'linestyleModifiers', text='', icon='MODIFIER')

      # linestyle modifier type
      row.prop(option, 'linestyleModifierType', text='')

      # separate
      column.separator()
      column.separator()
      column.separator()
      column.separator()

    # quick batch
    else:

      # label
      column.label(text='Ignore:')

      # split
      split = layout.split(align=True, percentage=0.9)

      # column
      column = split.column(align=True)

      # row
      row = column.row(align=True)

      # scale x
      row.scale_x = 5

      # ignore object
      row.prop(option, 'ignoreObject', text='', icon='OBJECT_DATA')

      # ignore action
      row.prop(option, 'ignoreAction', text='', icon='ACTION')

      # ignore grease pencil
      row.prop(option, 'ignoreGreasePencil', text='', icon='GREASEPENCIL')

      # ignore group
      row.prop(option, 'ignoreGroup', text='', icon='GROUP')

      # ignore constraint
      row.prop(option, 'ignoreConstraint', text='', icon='CONSTRAINT')

      # ignore modifier
      row.prop(option, 'ignoreModifier', text='', icon='MODIFIER')

      # ignore bone
      row.prop(option, 'ignoreBone', text='', icon='BONE_DATA')

      # ignore bone group
      row.prop(option, 'ignoreBoneGroup', text='', icon='GROUP_BONE')

      # ignore bone constraint
      row.prop(option, 'ignoreBoneConstraint', text='', icon='CONSTRAINT_BONE')

      # row
      row = column.row(align=True)

      # scale x
      row.scale_x = 5

      # ignore object data
      row.prop(option, 'ignoreObjectData', text='', icon='MESH_DATA')

      # ignore vertex group
      row.prop(option, 'ignoreVertexGroup', text='', icon='GROUP_VERTEX')

      # ignore shape key
      row.prop(option, 'ignoreShapekey', text='', icon='SHAPEKEY_DATA')

      # ignore uv
      row.prop(option, 'ignoreUV', text='', icon='GROUP_UVS')

      # ignore vertex color
      row.prop(option, 'ignoreVertexColor', text='', icon='GROUP_VCOL')

      # ignore material
      row.prop(option, 'ignoreMaterial', text='', icon='MATERIAL')

      # ignore texture
      row.prop(option, 'ignoreTexture', text='', icon='TEXTURE')

      # ignore particle systme
      row.prop(option, 'ignoreParticleSystem', text='', icon='PARTICLES')

      # ignore particle settings
      row.prop(option, 'ignoreParticleSetting', text='', icon='MOD_PARTICLES')

      # column
      column = split.column(align=True)

      # scale y
      column.scale_y = 2

      # op: reset name panel settings
      op = column.operator('wm.reset_name_panel_settings', text='', icon='LOAD_FACTORY')
      op.panel = False
      op.auto = False
      op.names = False
      op.name = True
      op.copy = False

      # separate
      column.separator()
      column.separator()

    # size
    size = 0.3

    # column
    column = layout.column(align=True)

    # split
    split = column.split(align=True, percentage=size)

    # row
    row = split.row(align=True)

    # label
    row.label(text='Custom:')

    # row
    row = split.row(align=True)

    # custom name
    row.prop(option, 'custom', text='')

    # test
    sub = row.row(align=True)

    # scale x
    sub.scale_x = 0.39 if option.insert else 0.25

    # is insert
    if option.insert:

      # sub sub
      subsub = sub.row(align=True)

      # scale x
      subsub.scale_x = 1.5

      # insert at
      subsub.prop(option, 'insertAt')

    # insert
    sub.prop(option, 'insert', toggle=True)

    # separate
    column.separator()
    column.separator()

    # split
    split = column.split(align=True, percentage=size)

    # row
    row = split.row(align=True)

    # label
    row.label(text='Find:')

    # row
    row = split.row(align=True)

    # find
    row.prop(option, 'find', text='', icon='VIEWZOOM')

    # sub
    sub = row.split(align=True)

    # scale x
    sub.scale_x = 0.1

    # regex
    sub.prop(option, 'regex', text='.*', toggle=True)

    # separate
    column.separator()

    # split
    split = column.split(align=True, percentage=size)

    # row
    row = split.row(align=True)

    # label
    row.label('Replace:')

    # row
    row = split.row(align=True)

    # replace
    row.prop(option, 'replace', text='', icon='FILE_REFRESH')

    # separate
    column.separator()
    column.separator()

    # split
    split = column.split(align=True, percentage=size)

    # row
    row = split.row(align=True)

    # label
    row.label(text='Prefix:')

    # row
    row = split.row(align=True)

    # prefix
    row.prop(option, 'prefix', text='', icon='LOOP_BACK')

    # separate
    column.separator()

    # split
    split = column.split(align=True, percentage=size)

    # row
    row = split.row(align=True)

    # label
    row.label('Suffix:')

    # row
    row = split.row(align=True)

    # suffix
    row.prop(option, 'suffix', text='', icon='LOOP_FORWARDS')

    # suffix last
    row.prop(option, 'suffixLast', text='', icon='FORWARD')

    # separate
    column.separator()
    column.separator()

    # row
    row = column.row()

    # label
    row.label(text='Trim Start:')

    # trim start
    row.prop(option, 'trimStart', text='')

    # separate
    column.separator()

    # row
    row = column.row()

    # label
    row.label(text='Trim End:')

    # trim end
    row.prop(option, 'trimEnd', text='')

    # separate
    column.separator()
    column.separator()

    # split
    split = column.split(align=True)

    # row
    row = split.row(align=True)

    # label
    row.label(text='Cut:')

    # row
    row = split.row(align=True)

    # sub
    sub = row.row(align=True)

    # scale x
    sub.scale_x = 0.75

    # cut start
    sub.prop(option, 'cutStart', text='At')

    # cut amount
    row.prop(option, 'cutAmount')

    # separate
    column.separator()

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
    batch.main(self, context)

    # report
    self.report({'INFO'}, 'Datablocks named: ' + str(self.count))

    # tag
    self.tag = False

    # count
    self.count = 0

    return {'FINISHED'}

  # invoke
  def invoke(self, context, event):
    '''
      Invoke the operator panel/menu, control its width.
    '''

    # is alt and isnt simple
    if event.alt and not self.simple:
      self.quickBatch = False

    # isnt simple
    if not self.simple:

      # size
      size = 330 if not context.window_manager.BatchShared.largePopups else 460

      # props dialog
      context.window_manager.invoke_props_dialog(self, width=size)

      # running modal
      return {'RUNNING_MODAL'}

    # is simple
    else:

      # execute
      self.execute(context)

      # is clear search
      if context.scene.NamePanel.clearSearch:

        # clear search
        context.scene.NamePanel.search = ''

      # finished
      return {'FINISHED'}
