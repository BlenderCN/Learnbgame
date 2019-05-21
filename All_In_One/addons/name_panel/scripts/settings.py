
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
from bpy.types import PropertyGroup
from bpy.props import *
from . import storage

# name
class name(PropertyGroup):
  '''
    Properties that effect how name panel displays the datablocks within the users current selection.
  '''

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
      ('GREASE_PENCIL', 'Grease Pencil', '', 'GREASEPENCIL', 3),
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
      ('MATERIAL', 'Material', '', 'MATERIAL', 14),
      ('TEXTURE', 'Texture', '', 'TEXTURE', 15),
      ('PARTICLE_SYSTEM', 'Particle System', '', 'PARTICLES', 16),
      ('PARTICLE_SETTING', 'Particle Settings', '', 'MOD_PARTICLES', 17)
    ],
    default = 'OBJECT'
  )

  # pin active object
  pinActiveObject = BoolProperty(
    name = 'Pin Active Object',
    description = 'Keeps the active object at the top of the stack.',
    default = True
  )

  # hide search
  hideSearch = BoolProperty(
    name = 'Hide Search',
    description = 'Only display the search field in the name panel when the filters option is toggled on.',
    default = True
  )

  # filters
  filters = BoolProperty(
    name = 'Filters',
    description = 'Show options for whether datablock names are displayed.',
    default = False
  )

  # options
  options = BoolProperty(
    name = 'Options',
    description = 'Show shortcut options next to datablock names.',
    default = False
  )

  # display names
  displayNames = BoolProperty(
    name = 'Display Names',
    description = 'Display additional object names in the name stack.',
    default = False
  )

  # search
  search = StringProperty(
    name = 'Search',
    description = 'Search filter.',
    default = ''
  )

  # regex
  regex = BoolProperty(
    name = 'Regular Expressions',
    description = 'Enable regular expressions.',
    default = False
  )

  # mode
  mode = EnumProperty(
    name = 'Mode',
    description = 'Mode option for additional object related names displayed.',
    items = [
      ('SELECTED', 'Selected', 'Display selected objects.'),
      ('LAYERS', 'Layers', 'Display objects in active scene layers.')
    ],
    default = 'SELECTED'
  )

  # groups
  groups = BoolProperty(
    name = 'Groups',
    description = 'Display group name.',
    default = False
  )

  # action
  action = BoolProperty(
    name = 'Action',
    description = 'Display action name.',
    default = False
  )

  # grease pencil
  greasePencil = BoolProperty(
    name = 'Grease Pencil',
    description = 'Display grease pencil and layer names',
    default = False
  )

  # constraints
  constraints = BoolProperty(
    name = 'Constraints',
    description = 'Display constraint names.',
    default = False
  )

  # modifiers
  modifiers = BoolProperty(
    name = 'Modifiers',
    description = 'Display modifier names.',
    default = False
  )

  # bone groups
  boneGroups = BoolProperty(
    name = 'Bone Groups',
    description = 'Display bone group names.',
    default = False
  )

  # bone constraints
  boneConstraints = BoolProperty(
    name = 'Bone Constraints',
    description = 'Display bone constraint names.',
    default = False
  )

  # vertex groups
  vertexGroups = BoolProperty(
    name = 'Vertex Groups',
    description = 'Display vertex group names.',
    default = False
  )

  # shapekeys
  shapekeys = BoolProperty(
    name = 'Shapekeys',
    description = 'Display shapekey names.',
    default = False
  )

  # uvs
  uvs = BoolProperty(
    name = 'UV\'s',
    description = 'Display uv names.',
    default = False
  )

  # vertex color
  vertexColors = BoolProperty(
    name = 'Vertex Colors',
    description = 'Display vertex color names.',
    default = False
  )

  # materials
  materials = BoolProperty(
    name = 'Materials',
    description = 'Display material names.',
    default = False
  )

  # textures
  textures = BoolProperty(
    name = 'Textures.',
    description = 'Display material texture names.',
    default = False
  )

  # particle systems
  particleSystems = BoolProperty(
    name = 'Particle Systems',
    description = 'Display the particle system and setting names. (Modifier filter must be active)',
    default = False
  )

  # bone mode
  boneMode = EnumProperty(
    name = 'Bone Mode',
    description = 'The display mode for bones.',
    items = [
      ('SELECTED', 'Selected', 'Display the selected bones.'),
      ('LAYERS', 'Layers', 'Display bones in active armature layers.',)
    ],
    default = 'SELECTED'
  )

  # display bones
  displayBones = BoolProperty(
    name = 'Display Bones',
    description = 'Display additional bone names.',
    default = False
  )

# properties
class properties(PropertyGroup):
  '''
    Properties that effect how properties panel displays the options.
  '''

  # display active
  displayActive = BoolProperty(
    name = 'Display Active',
    description = 'Prefer to display the active objects options instead of the last icon clicked when applicable.',
    default = True
  )

class batch:
  '''
    Contains Classes;
      auto
      name (PropertyGroup)
      copy (PropertyGroup)
  '''
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
    # options
    class name(PropertyGroup):
      '''
        Main properties that effect how the batch auto name operator is performed.
      '''

      # mode
      mode = EnumProperty(
        name = 'Mode',
        description = 'How to perform auto naming on datablocks designated below.',
        items = [
          ('SELECTED', 'Selected', 'Effect all objects and object related datablock names in the current 3D view selection.'),
          ('SCENE', 'Scene', 'Effect all objects and object related datablock names in the current scene.'),
          ('OBJECTS', 'All Objects', 'Effect all objects and object related datablock names in the file.')
        ],
        default = 'SELECTED'
      )

      # objects
      objects = BoolProperty(
        name = 'Objects',
        description = 'Name objects.',
        default = False
      )

      # constraints
      constraints = BoolProperty(
        name = 'Constraints',
        description = 'Name constraints.',
        default = False
      )

      # modifiers
      modifiers = BoolProperty(
        name = 'Modifiers',
        description = 'Name modifiers.',
        default = False
      )

      # objectData
      objectData = BoolProperty(
        name = 'Object Data',
        description = 'Name object data.',
        default = False
      )

      # bone Constraints
      boneConstraints = BoolProperty(
        name = 'Bone Constraints',
        description = 'Name bone constraints.'
      )

      # object type
      objectType = EnumProperty(
        name = 'Object Type',
        description = 'Type of objects to be effected.',
        items = storage.batch.menu.objects,
        default = 'ALL'
      )

      # constraint type
      constraintType = EnumProperty(
        name = 'Constraint Type',
        description = 'Type of constraints to be effected.',
        items = storage.batch.menu.constraints,
        default = 'ALL'
      )

      # modifier type
      modifierType = EnumProperty(
        name = 'Modifier Type',
        description = 'Type of modifiers to be effected.',
        items = storage.batch.menu.modifiers,
        default = 'ALL'
      )

    # object
    class objects(PropertyGroup):
      '''
        Properties that effect the names used when auto naming objects.
      '''

      # prefix
      prefix = BoolProperty(
        name = 'Prefix',
        description = 'Prefix the names of the objects with the values below.'
      )

      # mesh
      mesh = StringProperty(
        name = 'Mesh',
        description = 'Name used for mesh objects.',
        default = 'Mesh'
      )

      # curve
      curve = StringProperty(
        name = 'Curve',
        description = 'Name used for curve objects.',
        default = 'Curve'
      )

      # surface
      surface = StringProperty(
        name = 'Surface',
        description = 'Name used for surface objects.',
        default = 'Surface'
      )

      # meta
      meta = StringProperty(
        name = 'Meta',
        description = 'Name used for meta objects.',
        default = 'Meta'
      )

      # font
      font = StringProperty(
        name = 'Text',
        description = 'Name used for font objects.',
        default = 'Text'
      )

      # armature
      armature = StringProperty(
        name = 'Armature',
        description = 'Name used for armature objects.',
        default = 'Armature'
      )

      # lattice
      lattice = StringProperty(
        name = 'Lattice',
        description = 'Name used for lattice objects.',
        default = 'Lattice'
      )

      # empty
      empty = StringProperty(
        name = 'Empty',
        description = 'Name used for empty objects.',
        default = 'Empty'
      )

      # speaker
      speaker = StringProperty(
        name = 'Speaker',
        description = 'Name used for speaker objects.',
        default = 'Speaker'
      )

      # camera
      camera = StringProperty(
        name = 'Camera',
        description = 'Name used for camera objects.',
        default = 'Camera'
      )

      # lamp
      lamp = StringProperty(
        name = 'Lamp',
        description = 'Name used for lamp objects.',
        default = 'Lamp'
      )

    # constraints
    class constraints(PropertyGroup):
      '''
        Properties that effect the names used when auto naming constraints.
      '''

      # prefix
      prefix = BoolProperty(
        name = 'Prefix',
        description = 'Prefix the names of the constraints with the values below.'
      )

      # camera solver
      cameraSolver = StringProperty(
        name = 'Camera Solver',
        description = 'Name used for camera solver constraints.',
        default = 'Camera Solver'
      )

      # follow track
      followTrack = StringProperty(
        name = 'Follow Track',
        description = 'Name used for follow track constraints.',
        default = 'Follow Track'
      )

      # object solver
      objectSolver = StringProperty(
        name = 'Object Solver',
        description = 'Name used for object solver constraints.',
        default = 'Object Solver'
      )

      # copy location
      copyLocation = StringProperty(
        name = 'Copy Location',
        description = 'Name used for copy location constraints.',
        default = 'Copy Location'
      )

      # copy rotation
      copyRotation = StringProperty(
        name = 'Copy Rotation',
        description = 'Name used for copy rotation constraints.',
        default = 'Copy Rotation'
      )

      # copy scale
      copyScale = StringProperty(
        name = 'Copy Scale',
        description = 'Name used for copy scale constraints.',
        default = 'Copy Scale'
      )

      # copy transforms
      copyTransforms = StringProperty(
        name = 'Copy Transforms',
        description = 'Name used for copy transforms constraints.',
        default = 'Copy Transforms'
      )

      # limit distance
      limitDistance = StringProperty(
        name = 'Limit Distance',
        description = 'Name used for limit distance constraints.',
        default = 'Limit Distance'
      )

      # limit location
      limitLocation = StringProperty(
        name = 'Limit Location',
        description = 'Name used for limit location constraints.',
        default = 'Limit Location'
      )

      # limit rotation
      limitRotation = StringProperty(
        name = 'Limit Rotation',
        description = 'Name used for limit rotation constraints.',
        default = 'Limit Rotation'
      )

      # limit scale
      limitScale = StringProperty(
        name = 'Limit Scale',
        description = 'Name used for limit scale constraints.',
        default = 'Limit Scale'
      )

      # maintain volume
      maintainVolume = StringProperty(
        name = 'Maintain Volume',
        description = 'Name used for maintain volume constraints.',
        default = 'Maintain Volume'
      )

      # transform
      transform = StringProperty(
        name = 'Transform',
        description = 'Name used for transform constraints.',
        default = 'Transform'
      )

      # clamp to
      clampTo = StringProperty(
        name = 'Clamp To',
        description = 'Name used for clamp to constraints.',
        default = 'Clamp To'
      )

      # damped track
      dampedTrack = StringProperty(
        name = 'Damped Track',
        description = 'Name used for damped track constraints.',
        default = 'Damped Track'
      )

      # inverse kinematics
      inverseKinematics = StringProperty(
        name = 'Inverse Kinematics',
        description = 'Name used for inverse kinematics constraints.',
        default = 'Inverse Kinematics'
      )

      # locked track
      lockedTrack = StringProperty(
         name = 'Locked Track',
         description = 'Name used for locked track constraints.',
         default = 'Locked Track'
      )

      # spline inverse kinematics
      splineInverseKinematics = StringProperty(
         name = 'Spline Inverse Kinematics',
         description = 'Name used for spline inverse kinematics constraints.',
         default = 'Spline Inverse Kinematics'
      )

      # stretch to
      stretchTo = StringProperty(
         name = 'Stretch To',
         description = 'Name used for stretch to constraints.',
         default = 'Stretch To'
      )

      # track to
      trackTo = StringProperty(
         name = 'Track To',
         description = 'Name used for track to constraints.',
         default = 'Track To'
      )

      # action
      action = StringProperty(
         name = 'Action',
         description = 'Name used for action constraints.',
         default = 'Action'
      )

      # child of
      childOf = StringProperty(
         name = 'Child Of',
         description = 'Name used for child of constraints.',
         default = 'Child Of'
      )

      # floor
      floor = StringProperty(
         name = 'Floor',
         description = 'Name used for floor constraints.',
         default = 'Floor'
      )

      # follow path
      followPath = StringProperty(
         name = 'Follow Path',
         description = 'Name used for follow path constraints.',
         default = 'Follow Path'
      )

      # pivot
      pivot = StringProperty(
         name = 'Pivot',
         description = 'Name used for pivot constraints.',
         default = 'Pivot'
      )

      # rigid body joint
      rigidBodyJoint = StringProperty(
         name = 'Rigid Body Joint',
         description = 'Name used for rigid body joint constraints.',
         default = 'Rigid Body Joint'
      )

      # shrinkwrap
      shrinkwrap = StringProperty(
         name = 'Shrinkwrap',
         description = 'Name used for shrinkwrap constraints.',
         default = 'Shrinkwrap'
      )

    # modifier
    class modifiers(PropertyGroup):
      '''
        Properties that effect the names used when auto naming modifiers.
      '''

      # prefix
      prefix = BoolProperty(
        name = 'Prefix',
        description = 'Prefix the names of the modifiers with the values below.'
      )

      # data transfer
      dataTransfer = StringProperty(
        name = 'Data Transfer',
        description = 'Name used for data transfer modifiers.',
        default = 'Data Transfer'
      )

      # mesh cache
      meshCache = StringProperty(
        name = 'Mesh Cache',
        description = 'Name used for mesh cache modifiers.',
        default = 'Mesh Cache'
      )

      # normal edit
      normalEdit = StringProperty(
        name = 'Normal Edit',
        description = 'Name used for normal edit modifiers.',
        default = 'Normal Edit'
      )

      # uv project
      uvProject = StringProperty(
        name = 'UV Project',
        description = 'Name used for uv project modifiers.',
        default = 'UV Project'
      )

      # uv warp
      uvWarp = StringProperty(
        name = 'UV Warp',
        description = 'Name used for uv warp modifiers.',
        default = 'UV Warp'
      )

      # vertex weight edit
      vertexWeightEdit = StringProperty(
        name = 'Vertex Weight Edit',
        description = 'Name used for vertex weight edit modifiers.',
        default = 'Vertex Weight Edit'
      )

      # vertex weight mix
      vertexWeightMix = StringProperty(
        name = 'Vertex Weight Mix',
        description = 'Name used for vertex weight mix modifiers.',
        default = 'Vertex Weight Mix'
      )

      # vertex weight proximity
      vertexWeightProximity = StringProperty(
        name = 'Vertex Weight Proximity',
        description = 'Name used for vertex weight proximity modifiers.',
        default = 'Vertex Weight Proximity'
      )

      # array
      array = StringProperty(
        name = 'Array',
        description = 'Name used for array modifiers.',
        default = 'Array'
      )

      # bevel
      bevel = StringProperty(
        name = 'Bevel',
        description = 'Name used for bevel modifiers.',
        default = 'Bevel'
      )

      # boolean
      boolean = StringProperty(
        name = 'Boolean',
        description = 'Name used for boolean modifiers.',
        default = 'Boolean'
      )

      # build
      build = StringProperty(
        name = 'Build',
        description = 'Name used for build modifiers.',
        default = 'Build'
      )

      # decimate
      decimate = StringProperty(
        name = 'Decimate',
        description = 'Name used for decimate modifiers.',
        default = 'Decimate'
      )

      # edge split
      edgeSplit = StringProperty(
        name = 'Edge Split',
        description = 'Name used for edge split modifiers.',
        default = 'Edge Split'
      )

      # mask
      mask = StringProperty(
        name = 'Mask',
        description = 'Name used for mask modifiers.',
        default = 'Mask'
      )

      # mirror
      mirror = StringProperty(
        name = 'Mirror',
        description = 'Name used for mirror modifiers.',
        default = 'Mirror'
      )

      # multiresolution
      multiresolution = StringProperty(
        name = 'Multiresolution',
        description = 'Name used for multiresolution modifiers.',
        default = 'Multiresolution'
      )

      # remesh
      remesh = StringProperty(
        name = 'Remesh',
        description = 'Name used for remesh modifiers.',
        default = 'Remesh'
      )

      # screw
      screw = StringProperty(
        name = 'Screw',
        description = 'Name used for screw modifiers.',
        default = 'Screw'
      )

      # skin
      skin = StringProperty(
        name = 'Skin',
        description = 'Name used for skin modifiers.',
        default = 'Skin'
      )

      # solidify
      solidify = StringProperty(
        name = 'Solidify',
        description = 'Name used for solidify modifiers.',
        default = 'Solidify'
      )

      # subdivision surface
      subdivisionSurface = StringProperty(
        name = 'Subdivision Surface',
        description = 'Name used for subdivision surface modifiers.',
        default = 'Subdivision Surface'
      )

      # triangulate
      triangulate = StringProperty(
        name = 'Triangulate',
        description = 'Name used for triangulate modifiers.',
        default = 'Triangulate'
      )

      # wireframe
      wireframe = StringProperty(
        name = 'Wireframe',
        description = 'Name used for wireframe modifiers.',
        default = 'Wireframe'
      )

      # armature
      armature = StringProperty(
        name = 'Armature',
        description = 'Name used for armature modifiers.',
        default = 'Armature'
      )

      # cast
      cast = StringProperty(
        name = 'Cast',
        description = 'Name used for cast modifiers.',
        default = 'Cast'
      )

      # corrective smooth
      correctiveSmooth = StringProperty(
        name = 'Corrective Smooth',
        description = 'Name used for corrective smooth modifiers.',
        default = 'Corrective Smooth'
      )

      # curve
      curve = StringProperty(
        name = 'Curve',
        description = 'Name used for curve modifiers.',
        default = 'Curve'
      )

      # displace
      displace = StringProperty(
        name = 'Displace',
        description = 'Name used for displace modifiers.',
        default = 'Displace'
      )

      # hook
      hook = StringProperty(
        name = 'Hook',
        description = 'Name used for hook modifiers.',
        default = 'Hook'
      )

      # laplacian smooth
      laplacianSmooth = StringProperty(
        name = 'Laplacian Smooth',
        description = 'Name used for laplacian smooth modifiers.',
        default = 'Laplacian Smooth'
      )

      # laplacian deform
      laplacianDeform = StringProperty(
        name = 'Laplacian Deform',
        description = 'Name used for laplacian deform modifiers.',
        default = 'Laplacian Deform'
      )

      # lattice
      lattice = StringProperty(
        name = 'Lattice',
        description = 'Name used for lattice modifiers.',
        default = 'Lattice'
      )

      # mesh deform
      meshDeform = StringProperty(
        name = 'Mesh Deform',
        description = 'Name used for mesh deform modifiers.',
        default = 'Mesh Deform'
      )

      # shrinkwrap
      shrinkwrap = StringProperty(
        name = 'Shrinkwrap',
        description = 'Name used for shrinkwrap modifiers.',
        default = 'Shrinkwrap'
      )

      # simple deform
      simpleDeform = StringProperty(
        name = 'Simple Deform',
        description = 'Name used for simple deform modifiers.',
        default = 'Simple Deform'
      )

      # smooth
      smooth = StringProperty(
        name = 'Smooth',
        description = 'Name used for smooth modifiers.',
        default = 'Smooth'
      )

      # warp
      warp = StringProperty(
        name = 'Warp',
        description = 'Name used for warp modifiers.',
        default = 'Warp'
      )

      # wave
      wave = StringProperty(
        name = 'Wave',
        description = 'Name used for wave modifiers.',
        default = 'Wave'
      )

      # cloth
      cloth = StringProperty(
        name = 'Cloth',
        description = 'Name used for cloth modifiers.',
        default = 'Cloth'
      )

      # collision
      collision = StringProperty(
        name = 'Collision',
        description = 'Name used for collision modifiers.',
        default = 'Collision'
      )

      # dynamic paint
      dynamicPaint = StringProperty(
        name = 'Dynamic Paint',
        description = 'Name used for dynamic paint modifiers.',
        default = 'Dynamic Paint'
      )

      # explode
      explode = StringProperty(
        name = 'Explode',
        description = 'Name used for explode modifiers.',
        default = 'Explode'
      )

      # fluid simulation
      fluidSimulation = StringProperty(
        name = 'Fluid Simulation',
        description = 'Name used for fluid simulation modifiers.',
        default = 'Fluid Simulation'
      )

      # ocean
      ocean = StringProperty(
        name = 'Ocean',
        description = 'Name used for ocean modifiers.',
        default = 'Ocean'
      )

      # particle instance
      particleInstance = StringProperty(
        name = 'Particle Instance',
        description = 'Name used for particle instance modifiers.',
        default = 'Particle Instance'
      )

      # particle system
      particleSystem = StringProperty(
        name = 'Particle System',
        description = 'Name used for particle system modifiers.',
        default = 'Particle System'
      )

      # smoke
      smoke = StringProperty(
        name = 'Smoke',
        description = 'Name used for smoke modifiers.',
        default = 'Smoke'
      )

      # soft body
      softBody = StringProperty(
        name = 'Soft Body',
        description = 'Name used for soft body modifiers.',
        default = 'Soft Body'
      )

    # object data
    class objectData(PropertyGroup):
      '''
        Properties that effect the names used when auto naming objects.
      '''

      # prefix
      prefix = BoolProperty(
        name = 'Prefix',
        description = 'Prefix the names of the object\'s data with the values below.'
      )

      # mesh
      mesh = StringProperty(
        name = 'Mesh',
        description = 'Name used for mesh objects.',
        default = 'Mesh'
      )

      # curve
      curve = StringProperty(
        name = 'Curve',
        description = 'Name used for curve objects.',
        default = 'Curve'
      )

      # surface
      surface = StringProperty(
        name = 'Surface',
        description = 'Name used for surface objects.',
        default = 'Surface'
      )

      # meta
      meta = StringProperty(
        name = 'Meta',
        description = 'Name used for meta objects.',
        default = 'Meta'
      )

      # font
      font = StringProperty(
        name = 'Text',
        description = 'Name used for font objects.',
        default = 'Text'
      )

      # armature
      armature = StringProperty(
        name = 'Armature',
        description = 'Name used for armature objects.',
        default = 'Armature'
      )

      # lattice
      lattice = StringProperty(
        name = 'Lattice',
        description = 'Name used for lattice objects.',
        default = 'Lattice'
      )

      # empty
      empty = StringProperty(
        name = 'Empty',
        description = 'Name used for empty objects.',
        default = 'Empty'
      )

      # speaker
      speaker = StringProperty(
        name = 'Speaker',
        description = 'Name used for speaker objects.',
        default = 'Speaker'
      )

      # camera
      camera = StringProperty(
        name = 'Camera',
        description = 'Name used for camera objects.',
        default = 'Camera'
      )

      # lamp
      lamp = StringProperty(
        name = 'Lamp',
        description = 'Name used for lamp objects.',
        default = 'Lamp'
      )

  # name
  class name(PropertyGroup):
    '''
      Properties that effect how the batch name operation is performed.
    '''

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
      default = 'SELECTED'
    )

    # actions
    actions = BoolProperty(
      name = 'Actions',
      description = 'Name object actions. (Use \'Global\' for all)',
      default = False
    )

    # action groups
    actionGroups = BoolProperty(
      name = 'Action Groups',
      description = 'Name object action groups. (Use \'Global\' for all)',
      default = False
    )

    # grease pencil
    greasePencil = BoolProperty(
      name = 'Grease Pencil',
      description = 'Name object grease pencils. (Use \'Global\' for all)',
      default = False
    )

    # pencil layers
    pencilLayers = BoolProperty(
      name = 'Grease Pencil Layers',
      description = 'Name object grease pencils layers. (Use \'Global\' for all)',
      default = False
    )

    # objects
    objects = BoolProperty(
      name = 'Objects',
      description = 'Name objects.',
      default = False
    )

    # groups
    groups = BoolProperty(
      name = 'Groups',
      description = 'Name object groups. (Use \'Global\' for all)',
      default = False
    )

    # constraints
    constraints = BoolProperty(
      name = 'Object Constraints',
      description = 'Name object constraints.',
      default = False
    )

    # modifiers
    modifiers = BoolProperty(
      name = 'Modifiers',
      description = 'Name object modifiers.',
      default = False
    )

    # object data
    objectData = BoolProperty(
      name = 'Object Data',
      description = 'Name object data. (Use \'Global\' for all)',
      default = False
    )

    # bone groups
    boneGroups = BoolProperty(
      name = 'Bone Groups',
      description = 'Name armature bone groups.',
      default = False
    )

    # bones
    bones = BoolProperty(
      name = 'Bones',
      description = 'Name armature bones.',
      default = False
    )

    # bone constraints
    boneConstraints = BoolProperty(
      name = 'Bone Constraints',
      description = 'Name armature bone constraints.',
      default = False
    )

    # vertex groups
    vertexGroups = BoolProperty(
      name = 'Vertex Groups',
      description = 'Name object vertex groups.',
      default = False
    )

    # shapekeys
    shapekeys = BoolProperty(
      name = 'Shapekeys',
      description = 'Name object shapekeys.',
      default = False
    )

    # uvs
    uvs = BoolProperty(
      name = 'UV Maps',
      description = 'Name object uv maps.',
      default = False
    )

    # vertex colors
    vertexColors = BoolProperty(
      name = 'Vertex Colors',
      description = 'Name object vertex colors.',
      default = False
    )

    # materials
    materials = BoolProperty(
      name = 'Materials',
      description = 'Name object materials. (Use \'Global\' for all)',
      default = False
    )

    # textures
    textures = BoolProperty(
      name = 'Textures',
      description = 'Name object material textures. (Use \'Global\' for all)',
      default = False
    )

    # particle systems
    particleSystems = BoolProperty(
      name = 'Particle Systems',
      description = 'Name object particle systems. (Use \'Global\' for all)',
      default = False
    )

    # particle settings
    particleSettings = BoolProperty(
      name = 'Particle Settings',
      description = 'Name object particle system settings. (Use \'Global\' for all)',
      default = False
    )

    # object type
    objectType = EnumProperty(
      name = 'Object Type',
      description = 'Type of objects to be effected.',
      items = storage.batch.menu.objects,
      default = 'ALL'
    )

    # constraint type
    constraintType = EnumProperty(
      name = 'Constraint Type',
      description = 'Type of constraints to be effected.',
      items = storage.batch.menu.constraints,
      default = 'ALL'
    )

    # modifier type
    modifierType = EnumProperty(
      name = 'Modifier Type',
      description = 'Type of modifiers to be effected.',
      items = storage.batch.menu.modifiers,
      default = 'ALL'
    )

    # sensors
    sensors = BoolProperty(
      name = 'Sensors',
      description = 'Name object game sensors.',
      default = False
    )

    # controllers
    controllers = BoolProperty(
      name = 'Controllers',
      description = 'Name object game controllers',
      default = False
    )

    # actuators
    actuators = BoolProperty(
      name = 'Actuators',
      description = 'Name object game actuators',
      default = False
    )

    # line sets
    lineSets = BoolProperty(
      name = 'Line Sets',
      description = 'Name line sets.',
      default = False
    )

    # linestyles
    linestyles = BoolProperty(
      name = 'Linestyles',
      description = 'Name linestyles.',
      default = False
    )

    # linestyle modifiers
    linestyleModifiers = BoolProperty(
    name = 'Linestyle Modifiers',
    description = 'Name linestyle modifiers.',
    default = False
    )

    # linestyle modifier type
    linestyleModifierType = EnumProperty(
      name = 'Linestyle Modifier Type',
      description = 'Type of linestyle modifiers to be effected.',
      items = storage.batch.menu.linestyleModifiers,
      default = 'ALL'
    )

    # scenes
    scenes = BoolProperty(
      name = 'Scenes',
      description = 'Name scenes.',
      default = False
    )

    # render layers
    renderLayers = BoolProperty(
      name = 'Render Layers',
      description = 'Name render layers.',
      default = False
    )

    # worlds
    worlds = BoolProperty(
      name = 'Worlds',
      description = 'Name worlds.',
      default = False
    )

    # libraries
    libraries = BoolProperty(
      name = 'Libraries',
      description = 'Name libraries.',
      default = False
    )

    # images
    images = BoolProperty(
      name = 'Images',
      description = 'Name images.',
      default = False
    )

    # masks
    masks = BoolProperty(
      name = 'Masks',
      description = 'Name masks.',
      default = False
    )

    # sequences
    sequences = BoolProperty(
      name = 'Sequences',
      description = 'Name sequences.',
      default = False
    )

    # movie clips
    movieClips = BoolProperty(
      name = 'Movie Clips',
      description = 'Name movie clips.',
      default = False
    )

    # sounds
    sounds = BoolProperty(
      name = 'Sounds',
      description = 'Name sounds.',
      default = False
    )

    # screens
    screens = BoolProperty(
      name = 'Screens',
      description = 'Name screens. (No undo support)',
      default = False
    )

    # keying sets
    keyingSets = BoolProperty(
      name = 'Keying Sets',
      description = 'Name keying sets.',
      default = False
    )

    # palettes
    palettes = BoolProperty(
      name = 'Palettes',
      description = 'Name color palettes.',
      default = False
    )

    # brushes
    brushes = BoolProperty(
      name = 'Brushes',
      description = 'Name brushes.',
      default = False
    )

    # nodes
    nodes = BoolProperty(
      name = 'Nodes',
      description = 'Name nodes.',
      default = False
    )

    # node labels
    nodeLabels = BoolProperty(
      name = 'Node Labels',
      description = 'Name node labels.',
      default = False
    )

    # frame nodes
    frameNodes = BoolProperty(
      name = 'Frame Nodes',
      description = 'Name frame nodes.',
      default = False
    )

    # node groups
    nodeGroups = BoolProperty(
      name = 'Node Groups',
      description = 'Name node groups.',
      default = False
    )

    # texts
    texts = BoolProperty(
      name = 'Texts',
      description = 'Name text documents.',
      default = False
    )

    # ignore action
    ignoreAction = BoolProperty(
      name = 'Ignore Action',
      description = 'Ignore action names.',
      default = False
    )

    # ignore grease pencil
    ignoreGreasePencil = BoolProperty(
      name = 'Ignore Grease Pencil',
      description = 'Ignore grease pencil names.',
      default = False
    )

    # ignore object
    ignoreObject = BoolProperty(
      name = 'Ignore Object',
      description = 'Ignore object names.',
      default = False
    )

    # ignore group
    ignoreGroup  = BoolProperty(
      name = 'Ignore Oject Group',
      description = 'Ignore object group names.',
      default = False
    )

    # ignore constraint
    ignoreConstraint = BoolProperty(
      name = 'Ignore Constraint',
      description = 'Ignore constraint names.',
      default = False
    )

    # ignore modifier
    ignoreModifier = BoolProperty(
      name = 'Ignore Modifier',
      description = 'Ignore modifier names.',
      default = False
    )

    # ignore bone
    ignoreBone = BoolProperty(
      name = 'Ignore Bone',
      description = 'Ignore bone names.',
      default = False
    )

    # ignore bone group
    ignoreBoneGroup  = BoolProperty(
      name = 'Ignore Bone Group',
      description = 'Ignore bone group names.',
      default = False
    )

    # ignore bone constraint
    ignoreBoneConstraint = BoolProperty(
      name = 'Ignore Bone Constraint',
      description = 'Ignore bone constraint names.',
      default = False
    )

    # ignore object data
    ignoreObjectData = BoolProperty(
      name = 'Ignore Object Data',
      description = 'Ignore object data names.',
      default = False
    )

    # ignore vertex group
    ignoreVertexGroup = BoolProperty(
      name = 'Ignore Vertex Group',
      description = 'Ignore vertex group names.',
      default = False
    )

    # ignore shapekey
    ignoreShapekey = BoolProperty(
      name = 'Ignore Shapekey',
      description = 'Ignore shapekey names.',
      default = False
    )

    # ignore uv
    ignoreUV = BoolProperty(
      name = 'Ignore UV',
      description = 'Ignore uv names.',
      default = False
    )

    # ignore vertex color
    ignoreVertexColor = BoolProperty(
      name = 'Ignore Vertex Color',
      description = 'Ignore vertex color names.',
      default = False
    )

    # ignore material
    ignoreMaterial = BoolProperty(
      name = 'Ignore Material',
      description = 'Ignore material names.',
      default = False
    )

    # ignore texture
    ignoreTexture = BoolProperty(
      name = 'Ignore Texture',
      description = 'Ignore texture names.',
      default = False
    )

    # ignore particle system
    ignoreParticleSystem = BoolProperty(
      name = 'Ignore Particle System',
      description = 'Ignore particle system names.',
      default = False
    )

    # ignore particle setting
    ignoreParticleSetting = BoolProperty(
      name = 'Ignore Particle Setting',
      description = 'Ignore particle setting names.',
      default = False
    )

    # custom name
    customName = StringProperty(
      name = 'Custom Name',
      description = 'Designate a new name.'
    )

    # find
    find = StringProperty(
      name = 'Find',
      description = 'Find this text in the name and remove it.'
    )

    # regex
    regex = BoolProperty(
      name = 'Regular Expressions',
      description = 'Enable regular expressions.',
      default = False
    )

    # replace
    replace = StringProperty(
      name = 'Replace',
      description = 'Replace found text with the text entered here.'
    )

    # prefix
    prefix = StringProperty(
      name = 'Prefix',
      description = 'Place this text at the beginning of the name.'
    )

    # suffix
    suffix = StringProperty(
      name = 'Suffix',
      description = 'Place this text at the end of the name.'
    )

    # suffix last
    suffixLast = BoolProperty(
      name = 'Suffix Last',
      description = 'Force the suffix to be placed last when recounting duplicate names.',
      default = False
    )

    # trim start
    trimStart = IntProperty(
      name = 'Trim Start',
      description = 'Remove this many characters from the beginning of the name.',
      min = 0,
      max = 63,
      default = 0
    )

    # trim end
    trimEnd = IntProperty(
      name = 'Trim End',
      description = 'Remove this many characters from the end of the name.',
      min = 0,
      max = 63,
      default = 0
    )

    # sort
    sort = BoolProperty(
      name = 'Sort Duplicates',
      description = 'Recount names that are identical with a trailing number.',
      default = False
    )

    # start
    start = IntProperty(
      name = 'Start',
      description = 'Number to start with.',
      min = 0,
      default = 1
    )

    # padding
    padding = IntProperty(
      name = 'Padding',
      description = 'Number of zeroes to place before the final incrementing number.',
      min = 0,
      default = 0
    )

    # separator
    separator = StringProperty(
      name = 'Separator',
      description = 'The separator to use between the name and number.',
      default = '.'
    )

    # sort only
    sortOnly = BoolProperty(
     name = 'Only Sort Duplicates',
     description = 'Only effect names during the naming process that need to be numbered.',
     default = False
    )

    # link
    link = BoolProperty(
      name = 'Link Duplicates',
      description = 'If possible link the original duplicate name to the other duplicates location.',
      default = False
    )

  # copy
  class copy(PropertyGroup):
    '''
      Properties that effect how the batch copy name operation is performed.
    '''

    # mode
    mode = EnumProperty(
      name = 'Mode',
      description = 'How to perform batch name copying on datablocks designated below.',
      items = [
        ('SELECTED', 'Selected', 'Effect all objects and object related datablock names in the current 3D view selection.'),
        ('SCENE', 'Scene', 'Effect all objects and object related datablock names in the current scene.'),
        ('OBJECTS', 'All Objects', 'Effect all objects and object related datablock names in the file.')
      ],
      default = 'SELECTED'
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
      default = 'OBJECT'
    )

    # objects
    objects = BoolProperty(
      name = 'Object',
      description = 'Paste to objects.',
      default = False
    )

    # object data
    objectData = BoolProperty(
      name = 'Object Data',
      description = 'Paste to object data.',
      default = False
    )

    # materials
    materials = BoolProperty(
      name = 'Material',
      description = 'Paste to materials.',
      default = False
    )

    # textures
    textures = BoolProperty(
      name = 'Texture',
      description = 'Paste to textures.',
      default = False
    )

    # particle systems
    particleSystems = BoolProperty(
      name = 'Particle System',
      description = 'Paste to particle systems.',
      default = False
    )

    # particle settings
    particleSettings = BoolProperty(
      name = 'Particle Settings',
      description = 'Paste to particle settings.',
      default = False
    )

    # use active object
    useActiveObject = BoolProperty(
      name = 'Use active object',
      description = 'Use the names available from the active object to paste to the other datablock names.',
      default = False
    )
