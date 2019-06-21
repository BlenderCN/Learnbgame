
# imports
import bpy
from bpy.types import PropertyGroup
from bpy.props import *
from . import storage
from .defaults import defaults

# name
class name(PropertyGroup):
  '''
    Name panel options.
  '''

  # default
  default = defaults['name panel']

  # owner
  owner = StringProperty(
    name = 'Owner',
    description = 'The owner\'s name of the target datablock.',
    default = ''
  )

  # target
  target = StringProperty(
    name = 'Target',
    description = 'Datablock target\'s name belonging to the owner.',
    default = ''
  )

  # context
  context = EnumProperty(
    name = 'Context',
    description = 'The context the name panel is in based on last icon clicked',
    items = [
      ('OBJECT', 'Object', '', 'OBJECT_DATA', 0),
      ('GROUP', 'Group', '', 'GROUP', 1),
      ('ACTION', 'Action', '', 'ACTION', 2),
      # ('GREASE_PENCIL', 'Grease Pencil', '', 'GREASEPENCIL', 3),
      ('CONSTRAINT', 'Constraint', '', 'CONSTRAINT', 4),
      ('MODIFIER', 'Modifier', '', 'MODIFIER', 5),
      ('OBJECT_DATA', 'Data', '', 'MESH_DATA', 6),
      ('BONE_GROUP', 'Bone Group', '', 'GROUP_BONE', 7),
      ('BONE', 'Bone', '', 'BONE_DATA', 8),
      ('BONE_CONSTRAINT', 'Constraint', '', 'CONSTRAINT_BONE', 9),
      ('VERTEX_GROUP', 'Vertex Group', '', 'GROUP_VERTEX', 10),
      ('SHAPEKEY', 'Shapekey', '', 'SHAPEKEY_DATA', 11),
      ('UV', 'UV Map', '', 'GROUP_UVS', 12),
      ('VERTEX_COLOR', 'Vertex Colors', '', 'GROUP_VCOL', 13),
      # ('MATERIAL', 'Material', '', 'MATERIAL', 14),
      # ('TEXTURE', 'Texture', '', 'TEXTURE', 15),
      # ('PARTICLE_SYSTEM', 'Particle System', '', 'PARTICLES', 16),
      # ('PARTICLE_SETTING', 'Particle Settings', '', 'MOD_PARTICLES', 17)
    ],
    default = 'OBJECT'
  )

  # previous owner
  previousOwner = StringProperty(
    name = 'Previous Owner',
    description = 'The previous owner\'s name of the target datablock.',
    default = ''
  )

  # previous target
  previousTarget = StringProperty(
    name = 'Previous Target',
    description = 'Previous datablock target\'s name belonging to the owner.',
    default = ''
  )

  # previous context
  previousContext = EnumProperty(
    name = 'Previous Context',
    description = 'The previous context the name panel was in.',
    items = [
      ('OBJECT', 'Object', '', 'OBJECT_DATA', 0),
      ('GROUP', 'Group', '', 'GROUP', 1),
      ('ACTION', 'Action', '', 'ACTION', 2),
      # ('GREASE_PENCIL', 'Grease Pencil', '', 'GREASEPENCIL', 3),
      ('CONSTRAINT', 'Constraint', '', 'CONSTRAINT', 4),
      ('MODIFIER', 'Modifier', '', 'MODIFIER', 5),
      ('OBJECT_DATA', 'Object Data', '', 'MESH_DATA', 6),
      ('BONE_GROUP', 'Bone Group', '', 'GROUP_BONE', 7),
      ('BONE', 'Bone', '', 'BONE_DATA', 8),
      ('BONE_CONSTRAINT', 'Bone Constraint', '', 'CONSTRAINT_BONE', 9),
      ('VERTEX_GROUP', 'Vertex Group', '', 'GROUP_VERTEX', 10),
      ('SHAPEKEY', 'Shapekey', '', 'SHAPEKEY_DATA', 11),
      ('UV', 'UV Map', '', 'GROUP_UVS', 12),
      ('VERTEX_COLOR', 'Vertex Colors', '', 'GROUP_VCOL', 13),
      # ('MATERIAL', 'Material', '', 'MATERIAL', 14),
      # ('TEXTURE', 'Texture', '', 'TEXTURE', 15),
      # ('PARTICLE_SYSTEM', 'Particle System', '', 'PARTICLES', 16),
      # ('PARTICLE_SETTING', 'Particle Settings', '', 'MOD_PARTICLES', 17)
    ],
    default = 'OBJECT'
  )

  # location
  location = EnumProperty(
    name = 'Name Panel Location',
    description = 'The 3D view shelf to use for the name panel.',
    items = [
      ('TOOLS', 'Tool Shelf', 'Places the name panel in the tool shelf under the tab labeled \'Name\''),
      ('UI', 'Property Shelf', 'Places the name panel in the property shelf.')
    ],
    default = default['location']
  )

  # pin active object
  pinActiveObject = BoolProperty(
    name = 'Pin Active Object',
    description = 'Keeps the active object at the top of the name stack.',
    default = default['pin active object']
  )


  # pin active bone
  pinActiveBone = BoolProperty(
    name = 'Pin Active Bone',
    description = 'Keeps the active bone at the top of the name stack.',
    default = default['pin active bone']
  )

  # hide find & replace
  hideFindReplace = BoolProperty(
    name = 'Hide Find & Replace',
    description = 'Only display the find & replace fields in the panel when the filters option is toggled on.',
    default = default['hide find & replace']
  )

  # filters
  filters = BoolProperty(
    name = 'Filters',
    description = 'Show options for whether datablock names are displayed.',
    default = default['filters']
  )

  # shortcuts
  shortcuts = BoolProperty(
    name = 'shortcuts',
    description = 'Show shortcuts to settings next to the datablock names.',
    default = default['shortcuts']
  )

  # display names
  displayNames = BoolProperty(
    name = 'Display Names',
    description = 'Display additional object names in the name stack.',
    default = default['display names']
  )

  # search
  search = StringProperty(
    name = 'Search',
    description = 'Find this text in names.',
    default = default['search']
  )

  # clear search
  clearSearch = BoolProperty(
  name = 'Clear Search',
  description = 'Clear search after simple find and replace operations.',
  default = default['clear search']
  )

  # regex
  regex = BoolProperty(
    name = 'Regular Expressions',
    description = 'Enable regular expressions.',
    default = default['regex']
  )

  # mode
  mode = EnumProperty(
    name = 'Mode',
    description = 'Mode option for additional object related names displayed.',
    items = [
      ('SELECTED', 'Selected', 'Display selected objects.'),
      ('LAYERS', 'Layers', 'Display objects in active scene layers.')
    ],
    default = default['mode']
  )

  # groups
  groups = BoolProperty(
    name = 'Groups',
    description = 'Display group name.',
    default = default['groups']
  )

  # action
  action = BoolProperty(
    name = 'Action',
    description = 'Display action name.',
    default = default['action']
  )

  # grease pencil
  greasePencil = BoolProperty(
    name = 'Grease Pencil',
    description = 'Display grease pencil and layer names',
    default = default['grease pencil']
  )

  # constraints
  constraints = BoolProperty(
    name = 'Constraints',
    description = 'Display constraint names.',
    default = default['constraints']
  )

  # modifiers
  modifiers = BoolProperty(
    name = 'Modifiers',
    description = 'Display modifier names.',
    default = default['modifiers']
  )

  # bone groups
  boneGroups = BoolProperty(
    name = 'Bone Groups',
    description = 'Display bone group names.',
    default = default['bone groups']
  )

  # bone constraints
  boneConstraints = BoolProperty(
    name = 'Bone Constraints',
    description = 'Display bone constraint names.',
    default = default['bone constraints']
  )

  # vertex groups
  vertexGroups = BoolProperty(
    name = 'Vertex Groups',
    description = 'Display vertex group names.',
    default = default['vertex groups']
  )

  # shapekeys
  shapekeys = BoolProperty(
    name = 'Shapekeys',
    description = 'Display shapekey names.',
    default = default['shapekeys']
  )

  # uvs
  uvs = BoolProperty(
    name = 'UV\'s',
    description = 'Display uv names.',
    default = default['uvs']
  )

  # vertex colors
  vertexColors = BoolProperty(
    name = 'Vertex Colors',
    description = 'Display vertex color names.',
    default = default['vertex colors']
  )

  # materials
  materials = BoolProperty(
    name = 'Materials',
    description = 'Display material names.',
    default = default['materials']
  )

  # textures
  textures = BoolProperty(
    name = 'Textures.',
    description = 'Display material texture names.',
    default = default['textures']
  )

  # particle systems
  particleSystems = BoolProperty(
    name = 'Particle Systems',
    description = 'Display the particle system and setting names. (Modifier filter must be active)',
    default = default['particle systems']
  )

  # bone mode
  boneMode = EnumProperty(
    name = 'Bone Mode',
    description = 'The display mode for bones.',
    items = [
      ('SELECTED', 'Selected', 'Display the selected bones.'),
      ('LAYERS', 'Layers', 'Display bones in active armature layers.',)
    ],
    default = default['bone mode']
  )

  # display bones
  displayBones = BoolProperty(
    name = 'Display Bones',
    description = 'Display additional bone names.',
    default = default['display bones']
  )

# properties
class properties(PropertyGroup):
  '''
    Properties panel options.
  '''

  # default
  default = defaults['properties panel']

  # location
  location = EnumProperty(
    name = 'Property Panel Location',
    description = 'The 3D view shelf to use for the properties panel.',
    items = [
      ('TOOLS', 'Tool Shelf', 'Places the properties panel in the tool shelf under the tab labeled \'Name\''),
      ('UI', 'Property Shelf', 'Places the properties panel in the property shelf.')
    ],
    default = default['location']
  )

# batch
class batch:
  '''
    Contains Classes;
      auto
      name (PropertyGroup)
      copy (PropertyGroup)
  '''
  # shared
  class shared(PropertyGroup):
    '''
      Shared batch options.
    '''

    # default
    default = defaults['shared']

    # large popups
    largePopups = BoolProperty(
      name = 'Large Pop-ups',
      description = 'Increase the size of pop-ups.',
      default = default['large popups']
    )

    # sort
    sort = BoolProperty(
      name = 'Sort',
      description = 'Sort names before applying any new names.',
      default = default['sort']
    )

    # type
    type = EnumProperty(
      name = 'Type',
      description = 'Sorting method to use.',
      items = [
        ('ALPHABETICAL', 'Alphabetical', 'Sort names alphabetically.'),
        ('POSITIONAL', 'Positional', 'Sort names using position.')
      ],
      default = default['type']
    )

    # axis
    axis = EnumProperty(
      name = 'Axis',
      description = 'The positional axis to use for sorting.',
      items = [
        ('X', 'X', 'Sort from lowest to highest X axis position.'),
        ('Y', 'Y', 'Sort from lowest to highest y axis position.'),
        ('Z', 'Z', 'Sort from lowest to highest z axis position.')
      ],
      default = default['axis']
    )

    # invert
    invert = BoolProperty(
      name = 'Invert',
      description = 'Sort in the opposite direction.',
      default = default['invert']
    )

    # count
    count = BoolProperty(
      name = 'Count',
      description = 'Recount names that are identical with a trailing number.',
      default = default['count']
    )

    # link
    link = BoolProperty(
      name = 'Link Duplicates',
      description = 'When possible link duplicate names to the original datablock.',
      default = default['link']
    )

    # pad
    pad = IntProperty(
      name = 'Pad',
      description = 'Number of zeroes to place before the final incrementing number.',
      min = 0,
      default = default['pad']
    )

    # start
    start = IntProperty(
      name = 'Start',
      description = 'Number to start with.',
      min = 0,
      default = default['start']
    )

    # step
    step = IntProperty(
      name = 'Step',
      description = 'Step factor when counting.',
      min = 1,
      default = default['step']
    )

    # Separator
    separator = StringProperty(
      name = 'Separator',
      description = 'The separator to use between the name and number.',
      default = default['separator']
    )

    # ignore
    ignore = BoolProperty(
      name = 'Ignore Suffixes',
      description = 'Count any number that falls before a suffix.',
      default = default['ignore']
    )

  # auto
  class auto:
    '''
      Contains Classes;
        name (PropertyGroup)
        objects (PropertyGroup)
        constraints (PropertyGroup)
        modifiers (PropertyGroup)
        objectData (PropertyGroup)
    '''
    # name
    class name(PropertyGroup):
      '''
        Auto name options
      '''

      # default
      default = defaults['auto name']

      # mode
      mode = EnumProperty(
        name = 'Mode',
        description = 'How to perform auto naming on datablocks designated below.',
        items = [
          ('SELECTED', 'Selected', 'Effect all objects and object related datablock names in the current 3D view selection.'),
          ('SCENE', 'Scene', 'Effect all objects and object related datablock names in the current scene.'),
          ('OBJECTS', 'All Objects', 'Effect all objects and object related datablock names in the file.')
        ],
        default = default['mode']
      )

      # objects
      objects = BoolProperty(
        name = 'Objects',
        description = 'Name objects.',
        default = default['objects']
      )

      # constraints
      constraints = BoolProperty(
        name = 'Constraints',
        description = 'Name constraints.',
        default = default['constraints']
      )

      # modifiers
      modifiers = BoolProperty(
        name = 'Modifiers',
        description = 'Name modifiers.',
        default = default['modifiers']
      )

      # object data
      objectData = BoolProperty(
        name = 'Object Data',
        description = 'Name object data.',
        default = default['object data']
      )

      # bone constraints
      boneConstraints = BoolProperty(
        name = 'Bone Constraints',
        description = 'Name bone constraints.',
        default = default['bone constraints']
      )

      # object type
      objectType = EnumProperty(
        name = 'Object Type',
        description = 'Type of objects to be effected.',
        items = storage.batch.menu.objects,
        default = default['object type']
      )

      # constraint type
      constraintType = EnumProperty(
        name = 'Constraint Type',
        description = 'Type of constraints to be effected.',
        items = storage.batch.menu.constraints,
        default = default['constraint type']
      )

      # modifier type
      modifierType = EnumProperty(
        name = 'Modifier Type',
        description = 'Type of modifiers to be effected.',
        items = storage.batch.menu.modifiers,
        default = default['modifier type']
      )

    # object
    class objects(PropertyGroup):
      '''
        Object name options
      '''
      # default
      default = defaults['auto name']['object names']

      # prefix
      prefix = BoolProperty(
        name = 'Prefix',
        description = 'Prefix the names of the objects with the values below.',
        default = default['prefix']
      )

      # mesh
      mesh = StringProperty(
        name = 'Mesh',
        description = 'Name used for mesh objects.',
        default = default['mesh']
      )

      # curve
      curve = StringProperty(
        name = 'Curve',
        description = 'Name used for curve objects.',
        default = default['curve']
      )

      # surface
      surface = StringProperty(
        name = 'Surface',
        description = 'Name used for surface objects.',
        default = default['surface']
      )

      # meta
      meta = StringProperty(
        name = 'Meta',
        description = 'Name used for meta objects.',
        default = default['meta']
      )

      # font
      font = StringProperty(
        name = 'Text',
        description = 'Name used for font objects.',
        default = default['font']
      )

      # armature
      armature = StringProperty(
        name = 'Armature',
        description = 'Name used for armature objects.',
        default = default['armature']
      )

      # lattice
      lattice = StringProperty(
        name = 'Lattice',
        description = 'Name used for lattice objects.',
        default = default['lattice']
      )

      # empty
      empty = StringProperty(
        name = 'Empty',
        description = 'Name used for empty objects.',
        default = default['empty']
      )

      # speaker
      speaker = StringProperty(
        name = 'Speaker',
        description = 'Name used for speaker objects.',
        default = default['speaker']
      )

      # camera
      camera = StringProperty(
        name = 'Camera',
        description = 'Name used for camera objects.',
        default = default['camera']
      )

      # lamp
      lamp = StringProperty(
        name = 'Lamp',
        description = 'Name used for lamp objects.',
        default = default['lamp']
      )

    # constraints
    class constraints(PropertyGroup):
      '''
        Constraint name options.
      '''

      # default
      default = defaults['auto name']['constraint names']

      # prefix
      prefix = BoolProperty(
        name = 'Prefix',
        description = 'Prefix the names of the constraints with the values below.',
        default = default['prefix']
      )

      # camera solver
      cameraSolver = StringProperty(
        name = 'Camera Solver',
        description = 'Name used for camera solver constraints.',
        default = default['camera solver']
      )

      # follow track
      followTrack = StringProperty(
        name = 'Follow Track',
        description = 'Name used for follow track constraints.',
        default = default['follow track']
      )

      # object solver
      objectSolver = StringProperty(
        name = 'Object Solver',
        description = 'Name used for object solver constraints.',
        default = default['object solver']
      )

      # copy location
      copyLocation = StringProperty(
        name = 'Copy Location',
        description = 'Name used for copy location constraints.',
        default = default['copy location']
      )

      # copy rotation
      copyRotation = StringProperty(
        name = 'Copy Rotation',
        description = 'Name used for copy rotation constraints.',
        default = default['copy rotation']
      )

      # copy scale
      copyScale = StringProperty(
        name = 'Copy Scale',
        description = 'Name used for copy scale constraints.',
        default = default['copy scale']
      )

      # copy transforms
      copyTransforms = StringProperty(
        name = 'Copy Transforms',
        description = 'Name used for copy transforms constraints.',
        default = default['copy transforms']
      )

      # limit distance
      limitDistance = StringProperty(
        name = 'Limit Distance',
        description = 'Name used for limit distance constraints.',
        default = default['limit distance']
      )

      # limit location
      limitLocation = StringProperty(
        name = 'Limit Location',
        description = 'Name used for limit location constraints.',
        default = default['limit location']
      )

      # limit rotation
      limitRotation = StringProperty(
        name = 'Limit Rotation',
        description = 'Name used for limit rotation constraints.',
        default = default['limit rotation']
      )

      # limit scale
      limitScale = StringProperty(
        name = 'Limit Scale',
        description = 'Name used for limit scale constraints.',
        default = default['limit scale']
      )

      # maintain volume
      maintainVolume = StringProperty(
        name = 'Maintain Volume',
        description = 'Name used for maintain volume constraints.',
        default = default['maintain volume']
      )

      # transform
      transform = StringProperty(
        name = 'Transform',
        description = 'Name used for transform constraints.',
        default = default['transform']
      )

      # clamp to
      clampTo = StringProperty(
        name = 'Clamp To',
        description = 'Name used for clamp to constraints.',
        default = default['clamp to']
      )

      # damped track
      dampedTrack = StringProperty(
        name = 'Damped Track',
        description = 'Name used for damped track constraints.',
        default = default['damped track']
      )

      # inverse kinematics
      inverseKinematics = StringProperty(
        name = 'Inverse Kinematics',
        description = 'Name used for inverse kinematics constraints.',
        default = default['inverse kinematics']
      )

      # locked track
      lockedTrack = StringProperty(
         name = 'Locked Track',
         description = 'Name used for locked track constraints.',
         default = default['locked track']
      )

      # spline inverse kinematics
      splineInverseKinematics = StringProperty(
         name = 'Spline Inverse Kinematics',
         description = 'Name used for spline inverse kinematics constraints.',
         default = default['spline inverse kinematics']
      )

      # stretch to
      stretchTo = StringProperty(
         name = 'Stretch To',
         description = 'Name used for stretch to constraints.',
         default = default['stretch to']
      )

      # track to
      trackTo = StringProperty(
         name = 'Track To',
         description = 'Name used for track to constraints.',
         default = default['track to']
      )

      # action
      action = StringProperty(
         name = 'Action',
         description = 'Name used for action constraints.',
         default = default['action']
      )

      # child of
      childOf = StringProperty(
         name = 'Child Of',
         description = 'Name used for child of constraints.',
         default = default['child of']
      )

      # floor
      floor = StringProperty(
         name = 'Floor',
         description = 'Name used for floor constraints.',
         default = default['floor']
      )

      # follow path
      followPath = StringProperty(
         name = 'Follow Path',
         description = 'Name used for follow path constraints.',
         default = default['follow path']
      )

      # pivot
      pivot = StringProperty(
         name = 'Pivot',
         description = 'Name used for pivot constraints.',
         default = default['pivot']
      )

      # rigid body joint
      rigidBodyJoint = StringProperty(
         name = 'Rigid Body Joint',
         description = 'Name used for rigid body joint constraints.',
         default = default['rigid body joint']
      )

      # shrinkwrap
      shrinkwrap = StringProperty(
         name = 'Shrinkwrap',
         description = 'Name used for shrinkwrap constraints.',
         default = default['shrinkwrap']
      )

    # modifier
    class modifiers(PropertyGroup):
      '''
        Modifier name options.
      '''

      # default
      default = defaults['auto name']['modifier names']

      # prefix
      prefix = BoolProperty(
        name = 'Prefix',
        description = 'Prefix the names of the modifiers with the values below.',
        default = default['prefix']
      )

      # data transfer
      dataTransfer = StringProperty(
        name = 'Data Transfer',
        description = 'Name used for data transfer modifiers.',
        default = default['data transfer']
      )

      # mesh cache
      meshCache = StringProperty(
        name = 'Mesh Cache',
        description = 'Name used for mesh cache modifiers.',
        default = default['mesh cache']
      )

      # normal edit
      normalEdit = StringProperty(
        name = 'Normal Edit',
        description = 'Name used for normal edit modifiers.',
        default = default['normal edit']
      )

      # uv project
      uvProject = StringProperty(
        name = 'UV Project',
        description = 'Name used for uv project modifiers.',
        default = default['uv project']
      )

      # uv warp
      uvWarp = StringProperty(
        name = 'UV Warp',
        description = 'Name used for uv warp modifiers.',
        default = default['uv warp']
      )

      # vertex weight edit
      vertexWeightEdit = StringProperty(
        name = 'Vertex Weight Edit',
        description = 'Name used for vertex weight edit modifiers.',
        default = default['vertex weight edit']
      )

      # vertex weight mix
      vertexWeightMix = StringProperty(
        name = 'Vertex Weight Mix',
        description = 'Name used for vertex weight mix modifiers.',
        default = default['vertex weight mix']
      )

      # vertex weight proximity
      vertexWeightProximity = StringProperty(
        name = 'Vertex Weight Proximity',
        description = 'Name used for vertex weight proximity modifiers.',
        default = default['vertex weight proximity']
      )

      # array
      array = StringProperty(
        name = 'Array',
        description = 'Name used for array modifiers.',
        default = default['array']
      )

      # bevel
      bevel = StringProperty(
        name = 'Bevel',
        description = 'Name used for bevel modifiers.',
        default = default['bevel']
      )

      # boolean
      boolean = StringProperty(
        name = 'Boolean',
        description = 'Name used for boolean modifiers.',
        default = default['boolean']
      )

      # build
      build = StringProperty(
        name = 'Build',
        description = 'Name used for build modifiers.',
        default = default['build']
      )

      # decimate
      decimate = StringProperty(
        name = 'Decimate',
        description = 'Name used for decimate modifiers.',
        default = default['decimate']
      )

      # edge split
      edgeSplit = StringProperty(
        name = 'Edge Split',
        description = 'Name used for edge split modifiers.',
        default = default['edge split']
      )

      # mask
      mask = StringProperty(
        name = 'Mask',
        description = 'Name used for mask modifiers.',
        default = default['mask']
      )

      # mirror
      mirror = StringProperty(
        name = 'Mirror',
        description = 'Name used for mirror modifiers.',
        default = default['mirror']
      )

      # multiresolution
      multiresolution = StringProperty(
        name = 'Multiresolution',
        description = 'Name used for multiresolution modifiers.',
        default = default['multiresolution']
      )

      # remesh
      remesh = StringProperty(
        name = 'Remesh',
        description = 'Name used for remesh modifiers.',
        default = default['remesh']
      )

      # screw
      screw = StringProperty(
        name = 'Screw',
        description = 'Name used for screw modifiers.',
        default = default['screw']
      )

      # skin
      skin = StringProperty(
        name = 'Skin',
        description = 'Name used for skin modifiers.',
        default = default['skin']
      )

      # solidify
      solidify = StringProperty(
        name = 'Solidify',
        description = 'Name used for solidify modifiers.',
        default = default['solidify']
      )

      # subdivision surface
      subdivisionSurface = StringProperty(
        name = 'Subdivision Surface',
        description = 'Name used for subdivision surface modifiers.',
        default = default['subdivision surface']
      )

      # triangulate
      triangulate = StringProperty(
        name = 'Triangulate',
        description = 'Name used for triangulate modifiers.',
        default = default['triangulate']
      )

      # wireframe
      wireframe = StringProperty(
        name = 'Wireframe',
        description = 'Name used for wireframe modifiers.',
        default = default['wireframe']
      )

      # armature
      armature = StringProperty(
        name = 'Armature',
        description = 'Name used for armature modifiers.',
        default = default['armature']
      )

      # cast
      cast = StringProperty(
        name = 'Cast',
        description = 'Name used for cast modifiers.',
        default = default['cast']
      )

      # corrective smooth
      correctiveSmooth = StringProperty(
        name = 'Corrective Smooth',
        description = 'Name used for corrective smooth modifiers.',
        default = default['corrective smooth']
      )

      # curve
      curve = StringProperty(
        name = 'Curve',
        description = 'Name used for curve modifiers.',
        default = default['curve']
      )

      # displace
      displace = StringProperty(
        name = 'Displace',
        description = 'Name used for displace modifiers.',
        default = default['displace']
      )

      # hook
      hook = StringProperty(
        name = 'Hook',
        description = 'Name used for hook modifiers.',
        default = default['hook']
      )

      # laplacian smooth
      laplacianSmooth = StringProperty(
        name = 'Laplacian Smooth',
        description = 'Name used for laplacian smooth modifiers.',
        default = default['laplacian smooth']
      )

      # laplacian deform
      laplacianDeform = StringProperty(
        name = 'Laplacian Deform',
        description = 'Name used for laplacian deform modifiers.',
        default = default['laplacian deform']
      )

      # lattice
      lattice = StringProperty(
        name = 'Lattice',
        description = 'Name used for lattice modifiers.',
        default = default['lattice']
      )

      # mesh deform
      meshDeform = StringProperty(
        name = 'Mesh Deform',
        description = 'Name used for mesh deform modifiers.',
        default = default['mesh deform']
      )

      # shrinkwrap
      shrinkwrap = StringProperty(
        name = 'Shrinkwrap',
        description = 'Name used for shrinkwrap modifiers.',
        default = default['shrinkwrap']
      )

      # simple deform
      simpleDeform = StringProperty(
        name = 'Simple Deform',
        description = 'Name used for simple deform modifiers.',
        default = default['simple deform']
      )

      # smooth
      smooth = StringProperty(
        name = 'Smooth',
        description = 'Name used for smooth modifiers.',
        default = default['smooth']
      )

      # warp
      warp = StringProperty(
        name = 'Warp',
        description = 'Name used for warp modifiers.',
        default = default['warp']
      )

      # wave
      wave = StringProperty(
        name = 'Wave',
        description = 'Name used for wave modifiers.',
        default = default['wave']
      )

      # cloth
      cloth = StringProperty(
        name = 'Cloth',
        description = 'Name used for cloth modifiers.',
        default = default['cloth']
      )

      # collision
      collision = StringProperty(
        name = 'Collision',
        description = 'Name used for collision modifiers.',
        default = default['collision']
      )

      # dynamic paint
      dynamicPaint = StringProperty(
        name = 'Dynamic Paint',
        description = 'Name used for dynamic paint modifiers.',
        default = default['dynamic paint']
      )

      # explode
      explode = StringProperty(
        name = 'Explode',
        description = 'Name used for explode modifiers.',
        default = default['explode']
      )

      # fluid simulation
      fluidSimulation = StringProperty(
        name = 'Fluid Simulation',
        description = 'Name used for fluid simulation modifiers.',
        default = default['fluid simulation']
      )

      # ocean
      ocean = StringProperty(
        name = 'Ocean',
        description = 'Name used for ocean modifiers.',
        default = default['ocean']
      )

      # particle instance
      particleInstance = StringProperty(
        name = 'Particle Instance',
        description = 'Name used for particle instance modifiers.',
        default = default['particle instance']
      )

      # particle system
      particleSystem = StringProperty(
        name = 'Particle System',
        description = 'Name used for particle system modifiers.',
        default = default['particle system']
      )

      # smoke
      smoke = StringProperty(
        name = 'Smoke',
        description = 'Name used for smoke modifiers.',
        default = default['smoke']
      )

      # soft body
      softBody = StringProperty(
        name = 'Soft Body',
        description = 'Name used for soft body modifiers.',
        default = default['soft body']
      )

    # object data
    class objectData(PropertyGroup):
      '''
        Object data name options.
      '''

      # default
      default = defaults['auto name']['object data names']

      # prefix
      prefix = BoolProperty(
        name = 'Prefix',
        description = 'Prefix the names of the object\'s data with the values below.',
        default = default['prefix']
      )

      # mesh
      mesh = StringProperty(
        name = 'Mesh',
        description = 'Name used for mesh objects.',
        default = default['mesh']
      )

      # curve
      curve = StringProperty(
        name = 'Curve',
        description = 'Name used for curve objects.',
        default = default['curve']
      )

      # surface
      surface = StringProperty(
        name = 'Surface',
        description = 'Name used for surface objects.',
        default = default['surface']
      )

      # meta
      meta = StringProperty(
        name = 'Meta',
        description = 'Name used for meta objects.',
        default = default['meta']
      )

      # font
      font = StringProperty(
        name = 'Text',
        description = 'Name used for font objects.',
        default = default['font']
      )

      # armature
      armature = StringProperty(
        name = 'Armature',
        description = 'Name used for armature objects.',
        default = default['armature']
      )

      # lattice
      lattice = StringProperty(
        name = 'Lattice',
        description = 'Name used for lattice objects.',
        default = default['lattice']
      )

      # speaker
      speaker = StringProperty(
        name = 'Speaker',
        description = 'Name used for speaker objects.',
        default = default['speaker']
      )

      # camera
      camera = StringProperty(
        name = 'Camera',
        description = 'Name used for camera objects.',
        default = default['camera']
      )

      # lamp
      lamp = StringProperty(
        name = 'Lamp',
        description = 'Name used for lamp objects.',
        default = default['lamp']
      )

  # name
  class name(PropertyGroup):
    '''
      Batch name options.
    '''

    # default
    default = defaults['batch name']

    # mode
    mode = EnumProperty(
      name = 'Mode',
      description = 'How to perform batch naming on datablocks designated below.',
      items = [
        ('SELECTED', 'Selected', 'Effect all objects and object related datablock names in the current 3D view selection.'),
        ('SCENE', 'Scene', 'Effect all objects and object related datablock names in the current scene.'),
        ('OBJECTS', 'All Objects', 'Effect all objects and object related datablock names in the file.'),
        ('GLOBAL', 'Global', 'Effect all datablocks in the file whether they are attached to an object or not.')
      ],
      default = default['mode']
    )

    # actions
    actions = BoolProperty(
      name = 'Actions',
      description = 'Name object actions. (Use \'Global\' for all)',
      default = default['actions']
    )

    # action groups
    actionGroups = BoolProperty(
      name = 'Action Groups',
      description = 'Name object action groups. (Use \'Global\' for all)',
      default = default['action groups']
    )

    # grease pencil
    greasePencil = BoolProperty(
      name = 'Grease Pencil',
      description = 'Name object grease pencils. (Use \'Global\' for all)',
      default = default['grease pencil']
    )

    # pencil layers
    pencilLayers = BoolProperty(
      name = 'Grease Pencil Layers',
      description = 'Name object grease pencils layers. (Use \'Global\' for all)',
      default = default['pencil layers']
    )

    # objects
    objects = BoolProperty(
      name = 'Objects',
      description = 'Name objects.',
      default = default['objects']
    )

    # groups
    groups = BoolProperty(
      name = 'Groups',
      description = 'Name object groups. (Use \'Global\' for all)',
      default = default['groups']
    )

    # constraints
    constraints = BoolProperty(
      name = 'Object Constraints',
      description = 'Name object constraints.',
      default = default['constraints']
    )

    # modifiers
    modifiers = BoolProperty(
      name = 'Modifiers',
      description = 'Name object modifiers.',
      default = default['modifiers']
    )

    # object data
    objectData = BoolProperty(
      name = 'Object Data',
      description = 'Name object data. (Use \'Global\' for all)',
      default = default['object data']
    )

    # bone groups
    boneGroups = BoolProperty(
      name = 'Bone Groups',
      description = 'Name armature bone groups.',
      default = default['bone groups']
    )

    # bones
    bones = BoolProperty(
      name = 'Bones',
      description = 'Name armature bones.',
      default = default['bones']
    )

    # bone constraints
    boneConstraints = BoolProperty(
      name = 'Bone Constraints',
      description = 'Name armature bone constraints.',
      default = default['bone constraints']
    )

    # vertex groups
    vertexGroups = BoolProperty(
      name = 'Vertex Groups',
      description = 'Name object vertex groups.',
      default = default['vertex groups']
    )

    # shapekeys
    shapekeys = BoolProperty(
      name = 'Shapekeys',
      description = 'Name object shapekeys.',
      default = default['shapekeys']
    )

    # uvs
    uvs = BoolProperty(
      name = 'UV Maps',
      description = 'Name object uv maps.',
      default = default['uvs']
    )

    # vertex colors
    vertexColors = BoolProperty(
      name = 'Vertex Colors',
      description = 'Name object vertex colors.',
      default = default['vertex colors']
    )

    # materials
    materials = BoolProperty(
      name = 'Materials',
      description = 'Name object materials. (Use \'Global\' for all)',
      default = default['materials']
    )

    # textures
    textures = BoolProperty(
      name = 'Textures',
      description = 'Name object material textures. (Use \'Global\' for all)',
      default = default['textures']
    )

    # particle systems
    particleSystems = BoolProperty(
      name = 'Particle Systems',
      description = 'Name object particle systems. (Use \'Global\' for all)',
      default = default['particle systems']
    )

    # particle settings
    particleSettings = BoolProperty(
      name = 'Particle Settings',
      description = 'Name object particle system settings. (Use \'Global\' for all)',
      default = default['particle settings']
    )

    # object type
    objectType = EnumProperty(
      name = 'Object Type',
      description = 'Type of objects to be effected.',
      items = storage.batch.menu.objects,
      default = default['object type']
    )

    # constraint type
    constraintType = EnumProperty(
      name = 'Constraint Type',
      description = 'Type of constraints to be effected.',
      items = storage.batch.menu.constraints,
      default = default['constraint type']
    )

    # modifier type
    modifierType = EnumProperty(
      name = 'Modifier Type',
      description = 'Type of modifiers to be effected.',
      items = storage.batch.menu.modifiers,
      default = default['modifier type']
    )

    # sensors
    sensors = BoolProperty(
      name = 'Sensors',
      description = 'Name object game sensors.',
      default = default['sensors']
    )

    # controllers
    controllers = BoolProperty(
      name = 'Controllers',
      description = 'Name object game controllers',
      default = default['controllers']
    )

    # actuators
    actuators = BoolProperty(
      name = 'Actuators',
      description = 'Name object game actuators',
      default = default['actuators']
    )

    # line sets
    lineSets = BoolProperty(
      name = 'Line Sets',
      description = 'Name line sets.',
      default = default['line sets']
    )

    # linestyles
    linestyles = BoolProperty(
      name = 'Linestyles',
      description = 'Name linestyles.',
      default = default['linestyles']
    )

    # linestyle modifiers
    linestyleModifiers = BoolProperty(
      name = 'Linestyle Modifiers',
      description = 'Name linestyle modifiers.',
      default = default['linestyle modifiers']
    )

    # linestyle modifier type
    linestyleModifierType = EnumProperty(
      name = 'Linestyle Modifier Type',
      description = 'Type of linestyle modifiers to be effected.',
      items = storage.batch.menu.linestyleModifiers,
      default = default['linestyle modifier type']
    )

    # scenes
    scenes = BoolProperty(
      name = 'Scenes',
      description = 'Name scenes.',
      default = default['scenes']
    )

    # render layers
    renderLayers = BoolProperty(
      name = 'Render Layers',
      description = 'Name render layers.',
      default = default['render layers']
    )

    # worlds
    worlds = BoolProperty(
      name = 'Worlds',
      description = 'Name worlds.',
      default = default['worlds']
    )

    # libraries
    libraries = BoolProperty(
      name = 'Libraries',
      description = 'Name libraries.',
      default = default['libraries']
    )

    # images
    images = BoolProperty(
      name = 'Images',
      description = 'Name images.',
      default = default['images']
    )

    # masks
    masks = BoolProperty(
      name = 'Masks',
      description = 'Name masks.',
      default = default['masks']
    )

    # sequences
    sequences = BoolProperty(
      name = 'Sequences',
      description = 'Name sequences.',
      default = default['sequences']
    )

    # movie clips
    movieClips = BoolProperty(
      name = 'Movie Clips',
      description = 'Name movie clips.',
      default = default['movie clips']
    )

    # sounds
    sounds = BoolProperty(
      name = 'Sounds',
      description = 'Name sounds.',
      default = default['sounds']
    )

    # screens
    screens = BoolProperty(
      name = 'Screens',
      description = 'Name screens. (No undo support)',
      default = default['screens']
    )

    # keying sets
    keyingSets = BoolProperty(
      name = 'Keying Sets',
      description = 'Name keying sets.',
      default = default['keying sets']
    )

    # palettes
    palettes = BoolProperty(
      name = 'Palettes',
      description = 'Name color palettes.',
      default = default['palettes']
    )

    # brushes
    brushes = BoolProperty(
      name = 'Brushes',
      description = 'Name brushes.',
      default = default['brushes']
    )

    # nodes
    nodes = BoolProperty(
      name = 'Nodes',
      description = 'Name nodes.',
      default = default['nodes']
    )

    # node labels
    nodeLabels = BoolProperty(
      name = 'Node Labels',
      description = 'Name node labels.',
      default = default['node labels']
    )

    # frame nodes
    frameNodes = BoolProperty(
      name = 'Frame Nodes',
      description = 'Name frame nodes.',
      default = default['frame nodes']
    )

    # node groups
    nodeGroups = BoolProperty(
      name = 'Node Groups',
      description = 'Name node groups.',
      default = default['node groups']
    )

    # texts
    texts = BoolProperty(
      name = 'Texts',
      description = 'Name text documents.',
      default = default['texts']
    )

    # ignore action
    ignoreAction = BoolProperty(
      name = 'Ignore Action',
      description = 'Ignore action names.',
      default = default['ignore action']
    )

    # ignore grease pencil
    ignoreGreasePencil = BoolProperty(
      name = 'Ignore Grease Pencil',
      description = 'Ignore grease pencil names.',
      default = default['ignore grease pencil']
    )

    # ignore object
    ignoreObject = BoolProperty(
      name = 'Ignore Object',
      description = 'Ignore object names.',
      default = default['ignore object']
    )

    # ignore group
    ignoreGroup = BoolProperty(
      name = 'Ignore Oject Group',
      description = 'Ignore object group names.',
      default = default['ignore group']
    )

    # ignore constraint
    ignoreConstraint = BoolProperty(
      name = 'Ignore Constraint',
      description = 'Ignore constraint names.',
      default = default['ignore constraint']
    )

    # ignore modifier
    ignoreModifier = BoolProperty(
      name = 'Ignore Modifier',
      description = 'Ignore modifier names.',
      default = default['ignore modifier']
    )

    # ignore bone
    ignoreBone = BoolProperty(
      name = 'Ignore Bone',
      description = 'Ignore bone names.',
      default = default['ignore bone']
    )

    # ignore bone group
    ignoreBoneGroup = BoolProperty(
      name = 'Ignore Bone Group',
      description = 'Ignore bone group names.',
      default = default['ignore bone group']
    )

    # ignore bone constraint
    ignoreBoneConstraint = BoolProperty(
      name = 'Ignore Bone Constraint',
      description = 'Ignore bone constraint names.',
      default = default['ignore bone constraint']
    )

    # ignore object data
    ignoreObjectData = BoolProperty(
      name = 'Ignore Object Data',
      description = 'Ignore object data names.',
      default = default['ignore object data']
    )

    # ignore vertex group
    ignoreVertexGroup = BoolProperty(
      name = 'Ignore Vertex Group',
      description = 'Ignore vertex group names.',
      default = default['ignore vertex group']
    )

    # ignore shapekey
    ignoreShapekey = BoolProperty(
      name = 'Ignore Shapekey',
      description = 'Ignore shapekey names.',
      default = default['ignore shapekey']
    )

    # ignore uv
    ignoreUV = BoolProperty(
      name = 'Ignore UV',
      description = 'Ignore uv names.',
      default = default['ignore uv']
    )

    # ignore vertex color
    ignoreVertexColor = BoolProperty(
      name = 'Ignore Vertex Color',
      description = 'Ignore vertex color names.',
      default = default['ignore vertex color']
    )

    # ignore material
    ignoreMaterial = BoolProperty(
      name = 'Ignore Material',
      description = 'Ignore material names.',
      default = default['ignore material']
    )

    # ignore texture
    ignoreTexture = BoolProperty(
      name = 'Ignore Texture',
      description = 'Ignore texture names.',
      default = default['ignore texture']
    )

    # ignore particle system
    ignoreParticleSystem = BoolProperty(
      name = 'Ignore Particle System',
      description = 'Ignore particle system names.',
      default = default['ignore particle system']
    )

    # ignore particle setting
    ignoreParticleSetting = BoolProperty(
      name = 'Ignore Particle Setting',
      description = 'Ignore particle setting names.',
      default = default['ignore particle setting']
    )

    # custom
    custom = StringProperty(
      name = 'Custom',
      description = 'Designate a new name.',
      default = default['custom']
    )

    # insert
    insert = BoolProperty(
      name = 'Insert',
      description = 'Insert custom text into the name instead of replacing the name.',
      default = default['insert']
    )

    # insert at
    insertAt = IntProperty(
      name = 'At',
      description = 'Insert custom text at this character.',
      min = -60,
      max = 60,
      default = default['insert at']
    )

    # find
    find = StringProperty(
      name = 'Find',
      description = 'Find this text in the name and remove it.',
      default = default['find']
    )

    # regex
    regex = BoolProperty(
      name = 'Regular Expressions',
      description = 'Enable regular expressions.',
      default = default['regex']
    )

    # replace
    replace = StringProperty(
      name = 'Replace',
      description = 'Replace found text with the text entered here.',
      default = default['replace']
    )

    # prefix
    prefix = StringProperty(
      name = 'Prefix',
      description = 'Place this text at the beginning of the name.',
      default = default['prefix']
    )

    # suffix
    suffix = StringProperty(
      name = 'Suffix',
      description = 'Place this text at the end of the name.',
      default = default['suffix']
    )

    # suffix last
    suffixLast = BoolProperty(
      name = 'Suffix Last',
      description = 'Force the suffix to be placed last when recounting duplicate names.',
      default = default['suffix last']
    )

    # trim start
    trimStart = IntProperty(
      name = 'Trim Start',
      description = 'Remove this many characters from the beginning of the name.',
      min = 0,
      max = 60,
      default = default['trim start']
    )

    # trim end
    trimEnd = IntProperty(
      name = 'Trim End',
      description = 'Remove this many characters from the end of the name.',
      min = 0,
      max = 60,
      default = default['trim end']
    )

    # cut start
    cutStart = IntProperty(
      name = 'Start',
      description = 'Begin the cut at this character.',
      min = 0,
      max = 60,
      default = default['cut start']
    )

    # cut end
    cutAmount = IntProperty(
      name = 'Amount',
      description = 'Number of characters to remove.',
      min = 0,
      max = 60,
      default = default['cut amount']
    )

  # copy
  class copy(PropertyGroup):
    '''
      Batch name copy options.
    '''

    # default
    default = defaults['copy name']

    # mode
    mode = EnumProperty(
      name = 'Mode',
      description = 'How to perform batch name copying on datablocks designated below.',
      items = [
        ('SELECTED', 'Selected', 'Effect all objects and object related datablock names in the current 3D view selection.'),
        ('SCENE', 'Scene', 'Effect all objects and object related datablock names in the current scene.'),
        ('OBJECTS', 'All Objects', 'Effect all objects and object related datablock names in the file.')
      ],
      default = default['mode']
    )

    # source
    source = EnumProperty(
      name = 'Copy',
      description = 'Type of datablock to copy the name from.',
      items = [
        ('OBJECT', 'Object', 'Use the name from the object.', 'OBJECT_DATA', 0),
        ('DATA', 'Object Data', 'Use the name from the object\'s data.', 'MESH_DATA', 1),
        ('MATERIAL', 'Active Material', 'Use the name from the active material of the object.', 'MATERIAL', 2),
        ('TEXTURE', 'Active Texture', 'Use the name from the active material\'s active texture of the object.', 'TEXTURE', 3),
        ('PARTICLE_SYSTEM', 'Active Particle System', 'Use the name from the active particle system of the object.', 'PARTICLES', 4),
        ('PARTICLE_SETTINGS', 'Active Particle Settings', 'Use the name from the active particle system\'s settings of the object.', 'MOD_PARTICLES', 5)
      ],
      default = default['source']
    )

    # objects
    objects = BoolProperty(
      name = 'Object',
      description = 'Paste to objects.',
      default = default['objects']
    )

    # object data
    objectData = BoolProperty(
      name = 'Object Data',
      description = 'Paste to object data.',
      default = default['object data']
    )

    # materials
    materials = BoolProperty(
      name = 'Material',
      description = 'Paste to materials.',
      default = default['materials']
    )

    # textures
    textures = BoolProperty(
      name = 'Texture',
      description = 'Paste to textures.',
      default = default['textures']
    )

    # particle systems
    particleSystems = BoolProperty(
      name = 'Particle System',
      description = 'Paste to particle systems.',
      default = default['particle systems']
    )

    # particle settings
    particleSettings = BoolProperty(
      name = 'Particle Settings',
      description = 'Paste to particle settings.',
      default = default['particle settings']
    )

    # use active object
    useActiveObject = BoolProperty(
      name = 'Use active object',
      description = 'Use the names available from the active object to paste to the other datablock names.',
      default = default['use active object']
    )
