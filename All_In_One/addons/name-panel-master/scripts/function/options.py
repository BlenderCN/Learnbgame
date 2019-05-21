
# imports
import bpy
from .. import storage
from ..defaults import defaults

# reset
def reset(context, panel, auto, names, name, copy):
  '''
    Resets the property values for the name panel add-on.
  '''

  # panel
  if panel:

    # defaults
    default = defaults['name panel']

    # name panel option
    option = context.scene.NamePanel

    # pin active object
    option.pinActiveObject = default['pin active object']

    # pin active bone
    option.pinActiveBone = default['pin active bone']

    # hide find & replace
    option.hideFindReplace = default['hide find & replace']

    # filters
    option.filters = default['filters']

    # shortcuts
    option.shortcuts = default['shortcuts']

    # display names
    option.displayNames = default['display names']

    # mode
    option.mode = default['mode']

    # search
    option.search = default['search']

    # clear search
    option.clearSearch = default['clear search']

    # regex
    option.regex = default['regex']

    # groups
    option.groups = default['groups']

    # action
    option.action = default['action']

    # grease pencil
    option.greasePencil = default['grease pencil']

    # constraints
    option.constraints = default['constraints']

    # modifiers
    option.modifiers = default['modifiers']

    # bone groups
    option.boneGroups = default['bone groups']

    # bone constraints
    option.boneConstraints = default['bone constraints']

    # vertex groups
    option.vertexGroups = default['vertex groups']

    # shapekeys
    option.shapekeys = default['shapekeys']

    # uvs
    option.uvs = default['uvs']

    # vertex colors
    option.vertexColors = default['vertex colors']

    # materials
    option.materials = default['materials']

    # textures
    option.textures = default['textures']

    # particle systems
    option.particleSystems = default['particle systems']

    # display bones
    option.displayBones = default['display bones']

    # bone mode
    option.boneMode = default['bone mode']

  # auto
  if auto:

    # default
    default = defaults['auto name']

    # auto name option
    option = context.window_manager.AutoName

    # mode
    option.mode = default['mode']

    # objects
    option.objects = default['objects']

    # constraints
    option.constraints = default['constraints']

    # modifiers
    option.modifiers = default['modifiers']

    # object data
    option.objectData = default['object data']

    # bone constraints
    option.boneConstraints = default['bone constraints']

    # object type
    option.objectType = default['object type']

    # constraint type
    option.constraintType = default['constraint type']

    # modifier type
    option.modifierType = default['modifier type']

    # option
    option = context.window_manager.BatchShared

    default = defaults['shared']

    # sort
    option.sort = default['sort']

    # type
    option.type = default['type']

    # axis
    option.axis = default['axis']

    # invert
    option.invert = default['invert']

    # count
    option.count = default['count']

    # link
    option.link = default['link']

    # padding
    option.pad = default['pad']

    # start
    option.start = default['start']

    # step
    option.step = default['step']

    # separator
    option.separator = default['separator']

    # ignore
    option.ignore = default['ignore']

  # names
  if names:

    # default
    default = defaults['auto name']['object names']

    # object name
    option = context.scene.ObjectNames

    # prefix
    option.prefix = default['prefix']

    # mesh
    option.mesh = default['mesh']

    # curve
    option.curve = default['curve']

    # surface
    option.surface = default['surface']

    # meta
    option.meta = default['meta']

    # font
    option.font = default['font']

    # armature
    option.armature = default['armature']

    # lattice
    option.lattice = default['lattice']

    # empty
    option.empty = default['empty']

    # speaker
    option.speaker = default['speaker']

    # camera
    option.camera = default['camera']

    # lamp
    option.lamp = default['lamp']

    # default
    default = defaults['auto name']['constraint names']

    # constraint name
    option = context.scene.ConstraintNames

    # prefix
    option.prefix = default['prefix']

    # camera solver
    option.cameraSolver = default['camera solver']

    # follow track
    option.followTrack = default['follow track']

    # object solver
    option.objectSolver = default['object solver']

    # copy location
    option.copyLocation = default['copy location']

    # copy rotation
    option.copyRotation = default['copy rotation']

    # copy scale
    option.copyScale = default['copy scale']

    # copy transforms
    option.copyTransforms = default['copy transforms']

    # limit distance
    option.limitDistance = default['limit distance']

    # limit location
    option.limitLocation = default['limit location']

    # limit rotation
    option.limitRotation = default['limit rotation']

    # limit scale
    option.limitScale = default['limit scale']

    # maintain volume
    option.maintainVolume = default['maintain volume']

    # transform
    option.transform = default['transform']

    # clamp to
    option.clampTo = default['clamp to']

    # damped track
    option.dampedTrack = default['damped track']

    # inverse kinematics
    option.inverseKinematics = default['inverse kinematics']

    # locked track
    option.lockedTrack = default['locked track']

    # spline inverse kinematics
    option.splineInverseKinematics = default['spline inverse kinematics']

    # stretch to
    option.stretchTo = default['stretch to']

    # track to
    option.trackTo = default['track to']

    # action
    option.action = default['action']

    # child of
    option.childOf = default['child of']

    # floor
    option.floor = default['floor']

    # follow path
    option.followPath = default['follow path']

    # pivot
    option.pivot = default['pivot']

    # rigid body joint
    option.rigidBodyJoint = default['rigid body joint']

    # shrinkwrap
    option.shrinkwrap = default['shrinkwrap']

    # default
    default = defaults['auto name']['modifier names']

    # modifier name
    option = context.scene.ModifierNames

    # prefix
    option.prefix = default['prefix']

    # data transfer
    option.dataTransfer = default['data transfer']

    # mesh cache
    option.meshCache = default['mesh cache']

    # normal edit
    option.normalEdit = default['normal edit']

    # uv project
    option.uvProject = default['uv project']

    # uv warp
    option.uvWarp = default['uv warp']

    # vertex weight edit
    option.vertexWeightEdit = default['vertex weight edit']

    # vertex weight mix
    option.vertexWeightMix = default['vertex weight mix']

    # vertex weight proximity
    option.vertexWeightProximity = default['vertex weight proximity']

    # array
    option.array = default['array']

    # bevel
    option.bevel = default['bevel']

    # boolean
    option.boolean = default['boolean']

    # build
    option.build = default['build']

    # decimate
    option.decimate = default['decimate']

    # edge split
    option.edgeSplit = default['edge split']

    # mask
    option.mask = default['mask']

    # mirror
    option.mirror = default['mirror']

    # multiresolution
    option.multiresolution = default['multiresolution']

    # remesh
    option.remesh = default['remesh']

    # screw
    option.screw = default['screw']

    # skin
    option.skin = default['skin']

    # solidify
    option.solidify = default['solidify']

    # subdivision surface
    option.subdivisionSurface = default['subdivision surface']

    # triangulate
    option.triangulate = default['triangulate']

    # wireframe
    option.wireframe = default['wireframe']

    # armature
    option.armature = default['armature']

    # cast
    option.cast = default['cast']

    # corrective smooth
    option.correctiveSmooth = default['corrective smooth']

    # curve
    option.curve = default['curve']

    # displace
    option.displace = default['displace']

    # hook
    option.hook = default['hook']

    # laplacian smooth
    option.laplacianSmooth = default['laplacian smooth']

    # laplacian deform
    option.laplacianDeform = default['laplacian deform']

    # lattice
    option.lattice = default['lattice']

    # mesh deform
    option.meshDeform = default['mesh deform']

    # shrinkwrap
    option.shrinkwrap = default['shrinkwrap']

    # simple deform
    option.simpleDeform = default['simple deform']

    # smooth
    option.smooth = default['smooth']

    # warp
    option.warp = default['warp']

    # wave
    option.wave = default['wave']

    # cloth
    option.cloth = default['cloth']

    # collision
    option.collision = default['collision']

    # dynamic paint
    option.dynamicPaint = default['dynamic paint']

    # explode
    option.explode = default['explode']

    # fluid simulation
    option.fluidSimulation = default['fluid simulation']

    # ocean
    option.ocean = default['ocean']

    # particle instance
    option.particleInstance = default['particle instance']

    # particle system
    option.particleSystem = default['particle system']

    # smoke
    option.smoke = default['smoke']

    # soft body
    option.softBody = default['soft body']

    # default
    default = defaults['auto name']['object data names']

    # object data name
    option = context.scene.ObjectDataNames

    # prefix
    option.prefix = default['prefix']

    # mesh
    option.mesh = default['mesh']

    # curve
    option.curve = default['curve']

    # surface
    option.surface = default['surface']

    # meta
    option.meta = default['meta']

    # font
    option.font = default['font']

    # armature
    option.armature = default['armature']

    # lattice
    option.lattice = default['lattice']

    # speaker
    option.speaker = default['speaker']

    # camera
    option.camera = default['camera']

    # lamp
    option.lamp = default['lamp']

  # name
  if name:

    # default
    default = defaults['batch name']

    # name option
    option = context.window_manager.BatchName

    # mode
    option.mode = default['mode']

    # actions
    option.actions = default['actions']

    # action groups
    option.actionGroups = default['action groups']

    # grease pencil
    option.greasePencil = default['grease pencil']

    # pencil layers
    option.pencilLayers = default['pencil layers']

    # objects
    option.objects = default['objects']

    # groups
    option.groups = default['groups']

    # constraints
    option.constraints = default['constraints']

    # modifiers
    option.modifiers = default['modifiers']

    # object data
    option.objectData = default['object data']

    # bone groups
    option.boneGroups = default['bone groups']

    # bones
    option.bones = default['bones']

    # bone constraints
    option.boneConstraints = default['bone constraints']

    # vertex groups
    option.vertexGroups = default['vertex groups']

    # shapekeys
    option.shapekeys = default['shapekeys']

    # uvs
    option.uvs = default['uvs']

    # vertex colors
    option.vertexColors = default['vertex colors']

    # materials
    option.materials = default['materials']

    # textures
    option.textures = default['textures']

    # particle systems
    option.particleSystems = default['particle systems']

    # particle settings
    option.particleSettings = default['particle settings']

    # object type
    option.objectType = default['object type']

    # constraint type
    option.constraintType = default['constraint type']

    # modifier type
    option.modifierType = default['modifier type']

    # sensors
    option.sensors = default['sensors']

    # controllers
    option.controllers = default['controllers']

    # actuators
    option.actuators = default['actuators']

    # line sets
    option.lineSets = default['line sets']

    # linestyles
    option.linestyles = default['linestyles']

    # linestyle modifiers
    option.linestyleModifiers = default['linestyle modifiers']

    # linestyle modifier type
    option.linestyleModifierType = default['linestyle modifier type']

    # scenes
    option.scenes = default['scenes']

    # render layers
    option.renderLayers = default['render layers']

    # worlds
    option.worlds = default['worlds']

    # libraries
    option.libraries = default['libraries']

    # images
    option.images = default['images']

    # masks
    option.masks = default['masks']

    # sequences
    option.sequences = default['sequences']

    # movie clips
    option.movieClips = default['movie clips']

    # sounds
    option.sounds = default['sounds']

    # screens
    option.screens = default['screens']

    # keying sets
    option.keyingSets = default['keying sets']

    # palettes
    option.palettes = default['palettes']

    # brushes
    option.brushes = default['brushes']

    # nodes
    option.nodes = default['nodes']

    # node labels
    option.nodeLabels = default['node labels']

    # frame nodes
    option.frameNodes = default['frame nodes']

    # node groups
    option.nodeGroups = default['node groups']

    # texts
    option.texts = default['texts']

    # ignore action
    option.ignoreAction = default['ignore action']

    # ignore grease pencil
    option.ignoreGreasePencil = default['ignore grease pencil']

    # ignore object
    option.ignoreObject = default['ignore object']

    # ignore group
    option.ignoreGroup = default['ignore group']

    # ignore constraint
    option.ignoreConstraint = default['ignore constraint']

    # ignore modifier
    option.ignoreModifier = default['ignore modifier']

    # ignore bone
    option.ignoreBone = default['ignore bone']

    # ignore bone group
    option.ignoreBoneGroup = default['ignore bone group']

    # ignore bone constraint
    option.ignoreBoneConstraint = default['ignore bone constraint']

    # ignore object data
    option.ignoreObjectData = default['ignore object data']

    # ignore vertex group
    option.ignoreVertexGroup = default['ignore vertex group']

    # ignore shapekey
    option.ignoreShapekey = default['ignore shapekey']

    # ignore uv
    option.ignoreUV = default['ignore uv']

    # ignore vertex color
    option.ignoreVertexColor = default['ignore vertex color']

    # ignore material
    option.ignoreMaterial = default['ignore material']

    # ignore texture
    option.ignoreTexture = default['ignore texture']

    # ignore particle system
    option.ignoreParticleSystem = default['ignore particle system']

    # ignore particle setting
    option.ignoreParticleSetting = default['ignore particle setting']

    # custom
    option.custom = default['custom']

    # insert
    option.insert = default['insert']

    # insert at
    option.insertAt = default['insert at']

    # find
    option.find = default['find']

    # regex
    option.regex = default['regex']

    # replace
    option.replace = default['replace']

    # prefix
    option.prefix = default['prefix']

    # suffix
    option.suffix = default['suffix']

    # suffix last
    option.suffixLast = default['suffix last']

    # trim start
    option.trimStart = default['trim start']

    # trim end
    option.trimEnd = default['trim end']

    # start
    option.cutStart = default['cut start']

    # end
    option.cutAmount = default['cut amount']

    # default
    default = defaults['shared']

    # option
    option = context.window_manager.BatchShared

    # sort
    option.sort = default['sort']

    # type
    option.type = default['type']

    # axis
    option.axis = default['axis']

    # invert
    option.invert = default['invert']

    # count
    option.count = default['count']

    # link
    option.link = default['link']

    # padding
    option.pad = default['pad']

    # start
    option.start = default['start']

    # step
    option.step = default['step']

    # separator
    option.separator = default['separator']

    # ignore
    option.ignore = default['ignore']

  # copy
  if copy:

    # default
    default = defaults['copy name']

    # copy option
    option = context.window_manager.CopyName

    # mode
    option.mode = default['mode']

    # source
    option.source = default['source']

    # objects
    option.objects = default['objects']

    # object data
    option.objectData = default['object data']

    # materials
    option.materials = default['materials']

    # textures
    option.textures = default['textures']

    # particle systems
    option.particleSystems = default['particle systems']

    # particle settings
    option.particleSettings = default['particle settings']

    # use active object
    option.useActiveObject = default['use active object']
