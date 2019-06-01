
# imports
from . import generate
from ...defaults import defaults

# main
def main(context):

  # name
  name(context)

  # properties
  properties(context)

  # shared
  shared(context)

  # auto
  auto(context)

  # batch
  batch(context)

  # copy
  copy(context)

  # generate
  generate.main(defaults)


# name
def name(context):

  # option
  option = context.scene.NamePanel

  # default
  default = defaults['name panel']

  # options
  default['location'] = option.location
  default['pin active object'] = option.pinActiveObject
  default['pin active bone'] = option.pinActiveObject
  default['hide find & replace'] = option.hideFindReplace
  default['filters'] = option.filters
  default['shortcuts'] = option.shortcuts
  default['display names'] = option.displayNames
  default['search'] = option.search
  default['clear search'] = option.clearSearch
  default['regex'] = option.regex
  default['mode'] = option.mode
  default['groups'] = option.groups
  default['action'] = option.action
  default['grease pencil'] = option.greasePencil
  default['constraints'] = option.constraints
  default['modifiers'] = option.modifiers
  default['bone groups'] = option.boneGroups
  default['bone constraints'] = option.boneConstraints
  default['vertex groups'] = option.vertexGroups
  default['shapekeys'] = option.shapekeys
  default['uvs'] = option.uvs
  default['vertex colors'] = option.vertexColors
  default['materials'] = option.materials
  default['textures'] = option.textures
  default['particle systems'] = option.particleSystems
  default['bone mode'] = option.boneMode
  default['display bones'] = option.displayBones


# properties
def properties(context):

  # option
  option = context.window_manager.PropertyPanel

  # default
  default = defaults['properties panel']

  default['location'] = option.location


# shared
def shared(context):

  # option
  option = context.window_manager.BatchShared

  # default
  default = defaults['shared']

  # options
  default['large popups'] = option.largePopups
  default['sort'] = option.sort
  default['type'] = option.type
  default['axis'] = option.axis
  default['invert'] = option.invert
  default['count'] = option.count
  default['pad'] = option.pad
  default['start'] = option.start
  default['step'] = option.step
  default['separator'] = option.separator
  default['link'] = option.link
  default['ignore'] = option.ignore


# auto
def auto(context):

  # option
  option = context.window_manager.AutoName

  # default
  default = defaults['auto name']

  # options
  default['mode'] = option.mode
  default['objects'] = option.objects
  default['constraints'] = option.constraints
  default['modifiers'] = option.modifiers
  default['object data'] = option.objectData
  default['bone constraints'] = option.boneConstraints
  default['object type'] = option.objectType
  default['constraint type'] = option.constraintType
  default['modifier type'] = option.modifierType


  # option
  option = context.scene.ObjectNames

  # default
  default = defaults['auto name']['object names']

  # options
  default['prefix'] = option.prefix
  default['mesh'] = option.mesh
  default['curve'] = option.curve
  default['surface'] = option.surface
  default['meta'] = option.meta
  default['font'] = option.font
  default['armature'] = option.armature
  default['lattice'] = option.lattice
  default['empty'] = option.empty
  default['speaker'] = option.speaker
  default['camera'] = option.camera
  default['lamp'] = option.lamp


  # option
  option = context.scene.ConstraintNames

  # default
  default = defaults['auto name']['constraint names']

  # options
  default['prefix'] = option.prefix
  default['camera solver'] = option.cameraSolver
  default['follow track'] = option.followTrack
  default['object solver'] = option.objectSolver
  default['copy location'] = option.copyLocation
  default['copy rotation'] = option.copyRotation
  default['copy scale'] = option.copyScale
  default['copy transforms'] = option.copyTransforms
  default['limit distance'] = option.limitDistance
  default['limit location'] = option.limitLocation
  default['limit rotation'] = option.limitRotation
  default['limit scale'] = option.limitScale
  default['maintain volume'] = option.maintainVolume
  default['transform'] = option.transform
  default['clamp to'] = option.clampTo
  default['damped track'] = option.dampedTrack
  default['inverse kinematics'] = option.inverseKinematics
  default['locked track'] = option.lockedTrack
  default['spline inverse kinematics'] = option.splineInverseKinematics
  default['stretch to'] = option.stretchTo
  default['track to'] = option.trackTo
  default['action'] = option.action
  default['child of'] = option.childOf
  default['floor'] = option.floor
  default['follow path'] = option.followPath
  default['pivot'] = option.pivot
  default['rigid body joint'] = option.rigidBodyJoint
  default['shrinkwrap'] = option.shrinkwrap


  # option
  option = context.scene.ModifierNames

  # default
  default = defaults['auto name']['modifier names']

  # options
  default['prefix'] = option.prefix
  default['data transfer'] = option.dataTransfer
  default['mesh cache'] = option.meshCache
  default['normal edit'] = option.normalEdit
  default['uv project'] = option.uvProject
  default['uv warp'] = option.uvWarp
  default['vertex weight edit'] = option.vertexWeightEdit
  default['vertex weight mix'] = option.vertexWeightMix
  default['vertex weight proximity'] = option.vertexWeightProximity
  default['array'] = option.array
  default['bevel'] = option.bevel
  default['boolean'] = option.boolean
  default['build'] = option.build
  default['decimate'] = option.decimate
  default['edge split'] = option.edgeSplit
  default['mask'] = option.mask
  default['mirror'] = option.mirror
  default['multiresolution'] = option.multiresolution
  default['remesh'] = option.remesh
  default['screw'] = option.screw
  default['skin'] = option.skin
  default['solidify'] = option.solidify
  default['subdivision surface'] = option.subdivisionSurface
  default['triangulate'] = option.triangulate
  default['wireframe'] = option.wireframe
  default['armature'] = option.armature
  default['cast'] = option.cast
  default['corrective smooth'] = option.correctiveSmooth
  default['curve'] = option.curve
  default['displace'] = option.displace
  default['hook'] = option.hook
  default['laplacian smooth'] = option.laplacianSmooth
  default['laplacian deform'] = option.laplacianDeform
  default['lattice'] = option.lattice
  default['mesh deform'] = option.meshDeform
  default['shrinkwrap'] = option.shrinkwrap
  default['simple deform'] = option.simpleDeform
  default['smooth'] = option.smooth
  default['warp'] = option.warp
  default['wave'] = option.wave
  default['cloth'] = option.cloth
  default['collision'] = option.collision
  default['dynamic paint'] = option.dynamicPaint
  default['explode'] = option.explode
  default['fluid simulation'] = option.fluidSimulation
  default['ocean'] = option.ocean
  default['particle instance'] = option.particleInstance
  default['particle system'] = option.particleSystem
  default['smoke'] = option.smoke
  default['soft body'] = option.softBody


  # option
  option = context.scene.ObjectDataNames

  # default
  default = defaults['auto name']['object data names']

  # options
  default['prefix'] = option.prefix
  default['mesh'] = option.mesh
  default['curve'] = option.curve
  default['surface'] = option.surface
  default['meta'] = option.meta
  default['font'] = option.font
  default['armature'] = option.armature
  default['lattice'] = option.lattice
  default['speaker'] = option.speaker
  default['camera'] = option.camera
  default['lamp'] = option.lamp


# batch
def batch(context):

  # option
  option = context.window_manager.BatchName

  # default
  default = defaults['batch name']

  # options
  default['mode'] = option.mode
  default['actions'] = option.actions
  default['action groups'] = option.actionGroups
  default['grease pencil'] = option.greasePencil
  default['pencil layers'] = option.pencilLayers
  default['objects'] = option.objects
  default['groups'] = option.groups
  default['constraints'] = option.constraints
  default['modifiers'] = option.modifiers
  default['object data'] = option.objectData
  default['bone groups'] = option.boneGroups
  default['bones'] = option.bones
  default['bone constraints'] = option.boneConstraints
  default['vertex groups'] = option.vertexGroups
  default['shapekeys'] = option.shapekeys
  default['uvs'] = option.uvs
  default['vertex colors'] = option.vertexColors
  default['materials'] = option.materials
  default['textures'] = option.textures
  default['particle systems'] = option.particleSystems
  default['particle settings'] = option.particleSettings
  default['object type'] = option.objectType
  default['constraint type'] = option.constraintType
  default['modifier type'] = option.modifierType
  default['sensors'] = option.sensors
  default['controllers'] = option.controllers
  default['actuators'] = option.actuators
  default['line sets'] = option.lineSets
  default['linestyles'] = option.linestyles
  default['linestyle modifiers'] = option.linestyleModifiers
  default['linestyle modifier type'] = option.linestyleModifierType
  default['scenes'] = option.scenes
  default['render layers'] = option.renderLayers
  default['worlds'] = option.worlds
  default['libraries'] = option.libraries
  default['images'] = option.images
  default['masks'] = option.masks
  default['sequences'] = option.sequences
  default['movie clips'] = option.movieClips
  default['sounds'] = option.sounds
  default['screens'] = option.screens
  default['keying sets'] = option.keyingSets
  default['palettes'] = option.palettes
  default['brushes'] = option.brushes
  default['nodes'] = option.nodes
  default['node labels'] = option.nodeLabels
  default['frame nodes'] = option.frameNodes
  default['node groups'] = option.nodeGroups
  default['texts'] = option.texts
  default['ignore action'] = option.ignoreAction
  default['ignore grease pencil'] = option.ignoreGreasePencil
  default['ignore object'] = option.ignoreObject
  default['ignore group'] = option.ignoreGroup
  default['ignore constraint'] = option.ignoreConstraint
  default['ignore modifier'] = option.ignoreModifier
  default['ignore bone'] = option.ignoreBone
  default['ignore bone group'] = option.ignoreBoneGroup
  default['ignore bone constraint'] = option.ignoreBoneConstraint
  default['ignore object data'] = option.ignoreObjectData
  default['ignore vertex group'] = option.ignoreVertexGroup
  default['ignore shapekey'] = option.ignoreShapekey
  default['ignore uv'] = option.ignoreUV
  default['ignore vertex color'] = option.ignoreVertexColor
  default['ignore material'] = option.ignoreMaterial
  default['ignore texture'] = option.ignoreTexture
  default['ignore particle system'] = option.ignoreParticleSystem
  default['ignore particle setting'] = option.ignoreParticleSetting
  default['custom'] = option.custom
  default['find'] = option.find
  default['regex'] = option.regex
  default['replace'] = option.replace
  default['prefix'] = option.prefix
  default['suffix'] = option.suffix
  default['suffix last'] = option.suffixLast
  default['trim start'] = option.trimStart
  default['trim end'] = option.trimEnd
  default['cut start'] = option.cutStart
  default['cut amount'] = option.cutAmount


# copy
def copy(context):

  # option
  option = context.window_manager.CopyName

  # default
  default = defaults['copy name']

  # options
  default['mode'] = option.mode
  default['source'] = option.source
  default['objects'] = option.objects
  default['object data'] = option.objectData
  default['materials'] = option.materials
  default['textures'] = option.textures
  default['particle systems'] = option.particleSystems
  default['particle settings'] = option.particleSettings
  default['use active object'] = option.useActiveObject
