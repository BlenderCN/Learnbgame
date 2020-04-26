
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

# reset
def reset(context, panel, auto, names, name, copy):
  '''
    Resets the property values for the name panel add-on.
  '''

  # panel
  if panel:

    # name panel option
    namePanelOption = context.scene.NamePanel

    # pin active object
    namePanelOption.pinActiveObject = False

    # hide search
    namePanelOption.hideSearch = True

    # filters
    namePanelOption.filters = False

    # options
    namePanelOption.options = False

    # selected
    namePanelOption.displayNames = False

    # mode
    namePanelOption.mode = 'SELECTED'

    # search
    namePanelOption.search = ''

    # regex
    namePanelOption.regex = False

    # groups
    namePanelOption.groups = False

    # action
    namePanelOption.action = False

    # grease pencil
    namePanelOption.greasePencil = False

    # constraints
    namePanelOption.constraints = False

    # modifiers
    namePanelOption.modifiers = False

    # bone groups
    namePanelOption.boneGroups = False

    # bone constraints
    namePanelOption.boneConstraints = False

    # vertex groups
    namePanelOption.vertexGroups = False

    # shapekeys
    namePanelOption.shapekeys = False

    # uvs
    namePanelOption.uvs = False

    # vertex colors
    namePanelOption.vertexColors = False

    # materials
    namePanelOption.materials = False

    # textures
    namePanelOption.textures = False

    # particle systems
    namePanelOption.particleSystems = False

    # display bones
    namePanelOption.displayBones = False

    # bone mode
    namePanelOption.boneMode = 'SELECTED'

  # auto
  if auto:

    # auto name option
    batchAutoNameOption = context.scene.BatchAutoName

    # type
    batchAutoNameOption.batchType = 'SELECTED'

    # objects
    batchAutoNameOption.objects = False

    # constraints
    batchAutoNameOption.constraints = False

    # modifiers
    batchAutoNameOption.modifiers = False

    # objectData
    batchAutoNameOption.objectData = False

    # bone Constraints
    batchAutoNameOption.boneConstraints = False

    # object type
    batchAutoNameOption.objectType = 'ALL'

    # constraint type
    batchAutoNameOption.constraintType = 'ALL'

    # modifier type
    batchAutoNameOption.modifierType = 'ALL'

  # names
  if names:

    # object name
    objectName = context.scene.BatchAutoName_ObjectNames

    # prefix
    objectName.prefix = False

    # mesh
    objectName.mesh = 'Mesh'

    # curve
    objectName.curve = 'Curve'

    # surface
    objectName.surface = 'Surface'

    # meta
    objectName.meta = 'Meta'

    # font
    objectName.font = 'Text'

    # armature
    objectName.armature = 'Armature'

    # lattice
    objectName.lattice = 'Lattice'

    # empty
    objectName.empty = 'Empty'

    # speaker
    objectName.speaker = 'Speaker'

    # camera
    objectName.camera = 'Camera'

    # lamp
    objectName.lamp = 'Lamp'

    # constraint name
    constraintName = context.scene.BatchAutoName_ConstraintNames

    # prefix
    constraintName.prefix = False

    # camera solver
    constraintName.cameraSolver = 'Camera Solver'

    # follow track
    constraintName.followTrack = 'Follow Track'

    # object solver
    constraintName.objectSolver = 'Object Solver'

    # copy location
    constraintName.copyLocation = 'Copy Location'

    # copy rotation
    constraintName.copyRotation = 'Copy Rotation'

    # copy scale
    constraintName.copyScale = 'Copy Scale'

    # copy transforms
    constraintName.copyTransforms = 'Copy Transforms'

    # limit distance
    constraintName.limitDistance = 'Limit Distance'

    # limit location
    constraintName.limitLocation = 'Limit Location'

    # limit rotation
    constraintName.limitRotation = 'Limit Rotation'

    # limit scale
    constraintName.limitScale = 'Limit Scale'

    # maintain volume
    constraintName.maintainVolume = 'Maintain Volume'

    # transform
    constraintName.transform = 'Transform'

    # clamp to
    constraintName.clampTo = 'Clamp To'

    # damped track
    constraintName.dampedTrack = 'Damped Track'

    # inverse kinematics
    constraintName.inverseKinematics = 'Inverse Kinematics'

    # locked track
    constraintName.lockedTrack = 'Locked Track'

    # spline inverse kinematics
    constraintName.splineInverseKinematics = 'Spline Inverse Kinematics'

    # stretch to
    constraintName.stretchTo = 'Stretch To'

    # track to
    constraintName.trackTo = 'Track To'

    # action
    constraintName.action = 'Action'

    # child of
    constraintName.childOf = 'Child Of'

    # floor
    constraintName.floor = 'Floor'

    # follow path
    constraintName.followPath = 'Follow Path'

    # pivot
    constraintName.pivot = 'Pivot'

    # rigid body joint
    constraintName.rigidBodyJoint = 'Rigid Body Joint'

    # shrinkwrap
    constraintName.shrinkwrap = 'Shrinkwrap'

    # modifier name
    modifierName = context.scene.BatchAutoName_ModifierNames

    # prefix
    modifierName.prefix = False

    # data transfer
    modifierName.dataTransfer = 'Data Transfer'

    # mesh cache
    modifierName.meshCache = 'Mesh Cache'

    # normal edit
    modifierName.normalEdit = 'Normal Edit'

    # uv project
    modifierName.uvProject = 'UV Project'

    # uv warp
    modifierName.uvWarp = 'UV Warp'

    # vertex weight edit
    modifierName.vertexWeightEdit = 'Vertex Weight Edit'

    # vertex weight mix
    modifierName.vertexWeightMix = 'Vertex Weight Mix'

    # vertex weight proximity
    modifierName.vertexWeightProximity = 'Vertex Weight Proximity'

    # array
    modifierName.array = 'Array'

    # bevel
    modifierName.bevel = 'Bevel'

    # boolean
    modifierName.boolean = 'Boolean'

    # build
    modifierName.build = 'Build'

    # decimate
    modifierName.decimate = 'Decimate'

    # edge split
    modifierName.edgeSplit = 'Edge Split'

    # mask
    modifierName.mask = 'Mask'

    # mirror
    modifierName.mirror = 'Mirror'

    # multiresolution
    modifierName.multiresolution = 'Multiresolution'

    # remesh
    modifierName.remesh = 'Remesh'

    # screw
    modifierName.screw = 'Screw'

    # skin
    modifierName.skin = 'Skin'

    # solidify
    modifierName.solidify = 'Solidify'

    # subdivision surface
    modifierName.subdivisionSurface = 'Subdivision Surface'

    # triangulate
    modifierName.triangulate = 'Triangulate'

    # wireframe
    modifierName.wireframe = 'Wireframe'

    # armature
    modifierName.armature = 'Armature'

    # cast
    modifierName.cast = 'Cast'

    # corrective smooth
    modifierName.correctiveSmooth = 'Corrective Smooth'

    # curve
    modifierName.curve = 'Curve'

    # displace
    modifierName.displace = 'Displace'

    # hook
    modifierName.hook = 'Hook'

    # laplacian smooth
    modifierName.laplacianSmooth = 'Laplacian Smooth'

    # laplacian deform
    modifierName.laplacianDeform = 'Laplacian Deform'

    # lattice
    modifierName.lattice = 'Lattice'

    # mesh deform
    modifierName.meshDeform = 'Mesh Deform'

    # shrinkwrap
    modifierName.shrinkwrap = 'Shrinkwrap'

    # simple deform
    modifierName.simpleDeform = 'Simple Deform'

    # smooth
    modifierName.smooth = 'Smooth'

    # warp
    modifierName.warp = 'Warp'

    # wave
    modifierName.wave = 'Wave'

    # cloth
    modifierName.cloth = 'Cloth'

    # collision
    modifierName.collision = 'Collision'

    # dynamic paint
    modifierName.dynamicPaint = 'Dynamic Paint'

    # explode
    modifierName.explode = 'Explode'

    # fluid simulation
    modifierName.fluidSimulation = 'Fluid Simulation'

    # ocean
    modifierName.ocean = 'Ocean'

    # particle instance
    modifierName.particleInstance = 'Particle Instance'

    # particle system
    modifierName.particleSystem = 'Particle System'

    # smoke
    modifierName.smoke = 'Smoke'

    # soft body
    modifierName.softBody = 'Soft Body'

    # object data names

    # mesh
    modifierName.mesh = 'Mesh'

    # curve
    modifierName.curve = 'Curve'

    # surface
    modifierName.surface = 'Surface'

    # meta
    modifierName.meta = 'Meta'

    # font
    modifierName.font = 'Text'

    # armature
    modifierName.armature = 'Armature'

    # lattice
    modifierName.lattice = 'Lattice'

    # empty
    modifierName.empty = 'Empty'

    # speaker
    modifierName.speaker = 'Speaker'

    # camera
    modifierName.camera = 'Camera'

    # lamp
    modifierName.lamp = 'Lamp'

    # object data name
    objectDataName = context.scene.BatchAutoName_ObjectDataNames

    # prefix
    objectDataName.prefix = False

    # mesh
    objectDataName.mesh = 'Mesh'

    # curve
    objectDataName.curve = 'Curve'

    # surface
    objectDataName.surface = 'Surface'

    # meta
    objectDataName.meta = 'Meta'

    # font
    objectDataName.font = 'Text'

    # armature
    objectDataName.armature = 'Armature'

    # lattice
    objectDataName.lattice = 'Lattice'

    # speaker
    objectDataName.speaker = 'Speaker'

    # camera
    objectDataName.camera = 'Camera'

    # lamp
    objectDataName.lamp = 'Lamp'

  # name
  if name:

    # name option
    batchNameOption = context.scene.BatchName

    # type
    batchNameOption.batchType = 'SELECTED'

    # actions
    batchNameOption.actions = False

    # action groups
    batchNameOption.actionGroups = False

    # grease pencil
    batchNameOption.greasePencil = False

    # pencil layers
    batchNameOption.pencilLayers = False

    # objects
    batchNameOption.objects = False

    # groups
    batchNameOption.groups = False

    # constraints
    batchNameOption.constraints = False

    # modifiers
    batchNameOption.modifiers = False

    # object data
    batchNameOption.objectData = False

    # bone groups
    batchNameOption.boneGroups = False

    # bones
    batchNameOption.bones = False

    # bone constraints
    batchNameOption.boneConstraints = False

    # vertex groups
    batchNameOption.vertexGroups = False

    # shapekeys
    batchNameOption.shapekeys = False

    # uvs
    batchNameOption.uvs = False

    # vertex colors
    batchNameOption.vertexColors = False

    # materials
    batchNameOption.materials = False

    # textures
    batchNameOption.textures = False

    # particle systems
    batchNameOption.particleSystems = False

    # particle settings
    batchNameOption.particleSettings = False

    # object type
    batchNameOption.objectType = 'ALL'

    # constraint type
    batchNameOption.constraintType = 'ALL'

    # modifier type
    batchNameOption.modifierType = 'ALL'

    # sensors
    batchNameOption.sensors = False

    # controllers
    batchNameOption.controllers = False

    # actuators
    batchNameOption.actuators = False

    # line sets
    batchNameOption.lineSets = False

    # linestyles
    batchNameOption.linestyles = False

    # linestyle modifiers
    batchNameOption.linestyleModifiers = False

    # linestyle modifier type
    batchNameOption.linestyleModifierType = 'ALL'

    # scenes
    batchNameOption.scenes = False

    # render layers
    batchNameOption.renderLayers = False

    # worlds
    batchNameOption.worlds = False

    # libraries
    batchNameOption.libraries = False

    # images
    batchNameOption.images = False

    # masks
    batchNameOption.masks = False

    # sequences
    batchNameOption.sequences = False

    # movie clips
    batchNameOption.movieClips = False

    # sounds
    batchNameOption.sounds = False

    # screens
    batchNameOption.screens = False

    # keying sets
    batchNameOption.keyingSets = False

    # palettes
    batchNameOption.palettes = False

    # brushes
    batchNameOption.brushes = False

    # nodes
    batchNameOption.nodes = False

    # node labels
    batchNameOption.nodeLabels = False

    # node groups
    batchNameOption.nodeGroups = False

    # texts
    batchNameOption.texts = False

    # custom name
    batchNameOption.customName = ''

    # find
    batchNameOption.find = ''

    # regex
    batchNameOption.regex = False

    # replace
    batchNameOption.replace = ''

    # prefix
    batchNameOption.prefix = ''

    # suffix
    batchNameOption.suffix = ''

    # suffix last
    batchNameOption.suffixLast = False

    # trim start
    batchNameOption.trimStart = 0

    # trim end
    batchNameOption.trimEnd = 0

    # sort
    batchNameOption.sort = False

    # start
    batchNameOption.start = 1

    # padding
    batchNameOption.padding = 0

    # separator
    batchNameOption.separator = '.'

    # sort only
    batchNameOption.sortOnly = False

  # copy
  if copy:

    # copy option
    batchCopyOption = context.scene.BatchCopyName

    # type
    batchCopyOption.batchType = 'SELECTED'

    # source
    batchCopyOption.source = 'OBJECT'

    # objects
    batchCopyOption.objects = False

    # object data
    batchCopyOption.objectData = False

    # materials
    batchCopyOption.materials = False

    # textures
    batchCopyOption.textures = False

    # particle systems
    batchCopyOption.particleSystems = False

    # particle settings
    batchCopyOption.particleSettings = False

    # use active object
    batchCopyOption.useActiveObject = False

# transfer
def transfer(context, panel, auto, names, name, copy):
  '''
    Resets the property values for the name panel add-on.
  '''

  # panel settings
  if panel:
    for scene in bpy.data.scenes[:]:
      if scene != context.scene:

        # name panel option
        namePanelOption = context.scene.NamePanel

        # pin active object
        scene.NamePanel.pinActiveObject = namePanelOption.pinActiveObject

        # hide search
        scene.NamePanel.hideSearch = namePanelOption.hideSearch

        # filters
        scene.NamePanel.filters = namePanelOption.filters

        # options
        scene.NamePanel.options = namePanelOption.options

        # display names
        scene.NamePanel.displayNames = namePanelOption.displayNames

        # mode
        scene.NamePanel.mode = namePanelOption.mode

        # search
        scene.NamePanel.search = namePanelOption.search

        # regex
        scene.NamePanel.regex = namePanelOption.regex

        # groups
        scene.NamePanel.groups = namePanelOption.groups

        # action
        scene.NamePanel.action = namePanelOption.action

        # grease pencil
        scene.NamePanel.greasePencil = namePanelOption.greasePencil

        # constraint
        scene.NamePanel.constraints = namePanelOption.constraints

        # modifiers
        scene.NamePanel.modifiers = namePanelOption.modifiers

        # bone groups
        scene.NamePanel.boneGroups = namePanelOption.boneGroups

        # bone constraints
        scene.NamePanel.boneConstraints = namePanelOption.boneConstraints

        # vertex groups
        scene.NamePanel.vertexGroups = namePanelOption.vertexGroups

        # shapekeys
        scene.NamePanel.shapekeys = namePanelOption.shapekeys

        # uvs
        scene.NamePanel.uvs = namePanelOption.uvs

        # vertex colors
        scene.NamePanel.vertexColors = namePanelOption.vertexColors

        # materials
        scene.NamePanel.materials = namePanelOption.materials

        # textures
        scene.NamePanel.textures = namePanelOption.textures

        # particels systems
        scene.NamePanel.particleSystems = namePanelOption.particleSystems

        # display bones
        scene.NamePanel.displayBones = namePanelOption.displayBones

        # bone mode
        scene.NamePanel.boneMode = namePanelOption.boneMode

  # auto
  if auto:
    for scene in bpy.data.scenes[:]:
      if scene != context.scene:

        # auto name option
        batchAutoNameOption = context.scene.BatchAutoName

        # type
        scene.BatchAutoName.batchType = batchAutoNameOption.batchType

        # objects
        scene.BatchAutoName.objects = batchAutoNameOption.objects

        # constraints
        scene.BatchAutoName.constraints = batchAutoNameOption.constraints

        # modifiers
        scene.BatchAutoName.modifiers = batchAutoNameOption.modifiers

        # objectData
        scene.BatchAutoName.objectData = batchAutoNameOption.objectData

        # bone Constraints
        scene.BatchAutoName.boneConstraints = batchAutoNameOption.boneConstraints

        # object type
        scene.BatchAutoName.objectType = batchAutoNameOption.objectType

        # constraint type
        scene.BatchAutoName.constraintType = batchAutoNameOption.constraintType

        # modifier type
        scene.BatchAutoName.modifierType = batchAutoNameOption.modifierType

  # names
  if names:
    for scene in bpy.data.scenes[:]:
      if scene != context.scene:

        # object name
        objectName = context.scene.BatchAutoName_ObjectNames

        # prefix
        scene.BatchAutoName_ObjectNames.prefix = objectName.prefix

        # mesh
        scene.BatchAutoName_ObjectNames.mesh = objectName.mesh

        # curve
        scene.BatchAutoName_ObjectNames.curve = objectName.curve

        # surface
        scene.BatchAutoName_ObjectNames.surface = objectName.surface

        # meta
        scene.BatchAutoName_ObjectNames.meta = objectName.meta

        # font
        scene.BatchAutoName_ObjectNames.font = objectName.font

        # armature
        scene.BatchAutoName_ObjectNames.armature = objectName.armature

        # lattice
        scene.BatchAutoName_ObjectNames.lattice = objectName.lattice

        # empty
        scene.BatchAutoName_ObjectNames.empty = objectName.empty

        # speaker
        scene.BatchAutoName_ObjectNames.speaker = objectName.speaker

        # camera
        scene.BatchAutoName_ObjectNames.camera = objectName.camera

        # lamp
        scene.BatchAutoName_ObjectNames.lamp = objectName.lamp

        # constraint name
        constraintName = context.scene.BatchAutoName_ConstraintNames

        # prefix
        scene.BatchAutoName_ConstraintNames.prefix = constraintName.prefix

        # camera solver
        scene.BatchAutoName_ConstraintNames.cameraSolver = constraintName.cameraSolver

        # follow track
        scene.BatchAutoName_ConstraintNames.followTrack = constraintName.followTrack

        # object solver
        scene.BatchAutoName_ConstraintNames.objectSolver = constraintName.objectSolver

        # copy location
        scene.BatchAutoName_ConstraintNames.copyLocation = constraintName.copyLocation

        # copy rotation
        scene.BatchAutoName_ConstraintNames.copyRotation = constraintName.copyRotation

        # copy scale
        scene.BatchAutoName_ConstraintNames.copyScale = constraintName.copyScale

        # copy transforms
        scene.BatchAutoName_ConstraintNames.copyTransforms = constraintName.copyTransforms

        # limit distance
        scene.BatchAutoName_ConstraintNames.limitDistance = constraintName.limitDistance

        # limit location
        scene.BatchAutoName_ConstraintNames.limitLocation = constraintName.limitLocation

        # limit rotation
        scene.BatchAutoName_ConstraintNames.limitRotation = constraintName.limitRotation

        # limit scale
        scene.BatchAutoName_ConstraintNames.limitScale = constraintName.limitScale

        # maintain volume
        scene.BatchAutoName_ConstraintNames.maintainVolume = constraintName.maintainVolume

        # transform
        scene.BatchAutoName_ConstraintNames.transform = constraintName.transform

        # clamp to
        scene.BatchAutoName_ConstraintNames.clampTo = constraintName.clampTo

        # damped track
        scene.BatchAutoName_ConstraintNames.dampedTrack = constraintName.dampedTrack

        # inverse kinematics
        scene.BatchAutoName_ConstraintNames.inverseKinematics = constraintName.inverseKinematics

        # locked track
        scene.BatchAutoName_ConstraintNames.lockedTrack = constraintName.lockedTrack

        # spline inverse kinematics
        scene.BatchAutoName_ConstraintNames.splineInverseKinematics = constraintName.splineInverseKinematics

        # stretch to
        scene.BatchAutoName_ConstraintNames.stretchTo = constraintName.stretchTo

        # track to
        scene.BatchAutoName_ConstraintNames.trackTo = constraintName.trackTo

        # action
        scene.BatchAutoName_ConstraintNames.action = constraintName.action

        # child of
        scene.BatchAutoName_ConstraintNames.childOf = constraintName.childOf

        # floor
        scene.BatchAutoName_ConstraintNames.floor = constraintName.floor

        # follow path
        scene.BatchAutoName_ConstraintNames.followPath = constraintName.followPath

        # pivot
        scene.BatchAutoName_ConstraintNames.pivot = constraintName.pivot

        # rigid body joint
        scene.BatchAutoName_ConstraintNames.rigidBodyJoint = constraintName.rigidBodyJoint

        # shrinkwrap
        scene.BatchAutoName_ConstraintNames.shrinkwrap = constraintName.shrinkwrap

        # modifier name
        modifierName = context.scene.BatchAutoName_ModifierNames

        # prefix
        scene.BatchAutoName_ModifierNames.prefix = modifierName.prefix

        # data transfer
        scene.BatchAutoName_ModifierNames.dataTransfer = modifierName.dataTransfer

        # mesh cache
        scene.BatchAutoName_ModifierNames.meshCache = modifierName.meshCache

        # normal edit
        scene.BatchAutoName_ModifierNames.normalEdit = modifierName.normalEdit

        # uv project
        scene.BatchAutoName_ModifierNames.uvProject = modifierName.uvProject

        # uv warp
        scene.BatchAutoName_ModifierNames.uvWarp = modifierName.uvWarp

        # vertex weight edit
        scene.BatchAutoName_ModifierNames.vertexWeightEdit = modifierName.vertexWeightEdit

        # vertex weight mix
        scene.BatchAutoName_ModifierNames.vertexWeightMix = modifierName.vertexWeightMix

        # vertex weight proximity
        scene.BatchAutoName_ModifierNames.vertexWeightProximity = modifierName.vertexWeightProximity

        # array
        scene.BatchAutoName_ModifierNames.array = modifierName.array

        # bevel
        scene.BatchAutoName_ModifierNames.bevel = modifierName.bevel

        # boolean
        scene.BatchAutoName_ModifierNames.boolean = modifierName.boolean

        # build
        scene.BatchAutoName_ModifierNames.build = modifierName.build

        # decimate
        scene.BatchAutoName_ModifierNames.decimate = modifierName.decimate

        # edge split
        scene.BatchAutoName_ModifierNames.edgeSplit = modifierName.edgeSplit

        # mask
        scene.BatchAutoName_ModifierNames.mask = modifierName.mask

        # mirror
        scene.BatchAutoName_ModifierNames.mirror = modifierName.mirror

        # multiresolution
        scene.BatchAutoName_ModifierNames.multiresolution = modifierName.multiresolution

        # remesh
        scene.BatchAutoName_ModifierNames.remesh = modifierName.remesh

        # screw
        scene.BatchAutoName_ModifierNames.screw = modifierName.screw

        # skin
        scene.BatchAutoName_ModifierNames.skin = modifierName.skin

        # solidify
        scene.BatchAutoName_ModifierNames.solidify = modifierName.solidify

        # subdivision surface
        scene.BatchAutoName_ModifierNames.subdivisionSurface = modifierName.subdivisionSurface

        # triangulate
        scene.BatchAutoName_ModifierNames.triangulate = modifierName.triangulate

        # wireframe
        scene.BatchAutoName_ModifierNames.wireframe = modifierName.wireframe

        # armature
        scene.BatchAutoName_ModifierNames.armature = modifierName.armature

        # cast
        scene.BatchAutoName_ModifierNames.cast = modifierName.cast

        # corrective smooth
        scene.BatchAutoName_ModifierNames.correctiveSmooth = modifierName.correctiveSmooth

        # curve
        scene.BatchAutoName_ModifierNames.curve = modifierName.curve

        # displace
        scene.BatchAutoName_ModifierNames.displace = modifierName.displace

        # hook
        scene.BatchAutoName_ModifierNames.hook = modifierName.hook

        # laplacian smooth
        scene.BatchAutoName_ModifierNames.laplacianSmooth = modifierName.laplacianSmooth

        # laplacian deform
        scene.BatchAutoName_ModifierNames.laplacianDeform = modifierName.laplacianDeform

        # lattice
        scene.BatchAutoName_ModifierNames.lattice = modifierName.lattice

        # mesh deform
        scene.BatchAutoName_ModifierNames.meshDeform = modifierName.meshDeform

        # shrinkwrap
        scene.BatchAutoName_ModifierNames.shrinkwrap = modifierName.shrinkwrap

        # simple deform
        scene.BatchAutoName_ModifierNames.simpleDeform = modifierName.simpleDeform

        # smooth
        scene.BatchAutoName_ModifierNames.smooth = modifierName.smooth

        # warp
        scene.BatchAutoName_ModifierNames.warp = modifierName.warp

        # wave
        scene.BatchAutoName_ModifierNames.wave = modifierName.wave

        # cloth
        scene.BatchAutoName_ModifierNames.cloth = modifierName.cloth

        # collision
        scene.BatchAutoName_ModifierNames.collision = modifierName.collision

        # dynamic paint
        scene.BatchAutoName_ModifierNames.dynamicPaint = modifierName.dynamicPaint

        # explode
        scene.BatchAutoName_ModifierNames.explode = modifierName.explode

        # fluid simulation
        scene.BatchAutoName_ModifierNames.fluidSimulation = modifierName.fluidSimulation

        # ocean
        scene.BatchAutoName_ModifierNames.ocean = modifierName.ocean

        # particle instance
        scene.BatchAutoName_ModifierNames.particleInstance = modifierName.particleInstance

        # particle system
        scene.BatchAutoName_ModifierNames.particleSystem = modifierName.particleSystem

        # smoke
        scene.BatchAutoName_ModifierNames.smoke = modifierName.smoke

        # soft body
        scene.BatchAutoName_ModifierNames.softBody = modifierName.softBody

        # object data name
        objectDataName = context.scene.BatchAutoName_ObjectDataNames

        # prefix
        scene.BatchAutoName_ObjectDataNames.prefix = objectDataName.prefix

        # mesh
        scene.BatchAutoName_ObjectDataNames.mesh = objectDataName.mesh

        # curve
        scene.BatchAutoName_ObjectDataNames.curve = objectDataName.curve

        # surface
        scene.BatchAutoName_ObjectDataNames.surface = objectDataName.surface

        # meta
        scene.BatchAutoName_ObjectDataNames.meta = objectDataName.meta

        # font
        scene.BatchAutoName_ObjectDataNames.font = objectDataName.font

        # armature
        scene.BatchAutoName_ObjectDataNames.armature = objectDataName.armature

        # lattice
        scene.BatchAutoName_ObjectDataNames.lattice = objectDataName.lattice

        # speaker
        scene.BatchAutoName_ObjectDataNames.speaker = objectDataName.speaker

        # camera
        scene.BatchAutoName_ObjectDataNames.camera = objectDataName.camera

        # lamp
        scene.BatchAutoName_ObjectDataNames.lamp = objectDataName.lamp

  # name
  if name:
    for scene in bpy.data.scenes:
      if scene != context.scene:

        # name option
        batchNameOption = context.scene.BatchName

        # batch type
        scene.BatchName.batchType = batchNameOption.batchType

        # actions
        scene.BatchName.actions = batchNameOption.actions

        # action groups
        scene.BatchName.actionGroups = batchNameOption.actionGroups

        # grease pencil
        scene.BatchName.greasePencil = batchNameOption.greasePencil

        # pencil layers
        scene.BatchName.pencilLayers = batchNameOption.pencilLayers

        # objects
        scene.BatchName.objects = batchNameOption.objects

        # groups
        scene.BatchName.groups = batchNameOption.groups

        # constraints
        scene.BatchName.constraints = batchNameOption.constraints

        # modifiers
        scene.BatchName.modifiers = batchNameOption.modifiers

        # object data
        scene.BatchName.objectData = batchNameOption.objectData

        # bone groups
        scene.BatchName.boneGroups = batchNameOption.boneGroups

        # bones
        scene.BatchName.bones = batchNameOption.bones

        # bone constraints
        scene.BatchName.boneConstraints = batchNameOption.boneConstraints

        # vertex groups
        scene.BatchName.vertexGroups = batchNameOption.vertexGroups

        # shapekeys
        scene.BatchName.shapekeys = batchNameOption.shapekeys

        # uvs
        scene.BatchName.uvs = batchNameOption.uvs

        # vertex colors
        scene.BatchName.vertexColors = batchNameOption.vertexColors

        # materials
        scene.BatchName.materials = batchNameOption.materials

        # textures
        scene.BatchName.textures = batchNameOption.textures

        # particle systems
        scene.BatchName.particleSystems = batchNameOption.particleSystems

        # particle settings
        scene.BatchName.particleSettings = batchNameOption.particleSettings

        # object type
        scene.BatchName.objectType = batchNameOption.objectType

        # constraint type
        scene.BatchName.constraintType = batchNameOption.constraintType

        # modifier type
        scene.BatchName.modifierType = batchNameOption.modifierType

        # sensors
        scene.BatchName.sensors = batchNameOption.sensors

        # controllers
        scene.BatchName.controllers = batchNameOption.controllers

        # actuators
        scene.BatchName.actuators = batchNameOption.actuators

        # line sets
        scene.BatchName.lineSets = batchNameOption.lineSets

        # linestyles
        scene.BatchName.linestyles = batchNameOption.linestyles

        # linestyle modifiers
        scene.BatchName.linestyleModifiers = batchNameOption.linestyleModifiers

        # linestyle modifier type
        scene.BatchName.linestyleModifierType = batchNameOption.linestyleModifierType

        # scenes
        scene.BatchName.scenes = batchNameOption.scenes

        # render layers
        scene.BatchName.renderLayers = batchNameOption.renderLayers

        # worlds
        scene.BatchName.worlds = batchNameOption.worlds

        # libraries
        scene.BatchName.libraries = batchNameOption.libraries

        # images
        scene.BatchName.images = batchNameOption.images

        # masks
        scene.BatchName.masks = batchNameOption.masks

        # sequences
        scene.BatchName.sequences = batchNameOption.sequences

        # movie clips
        scene.BatchName.movieClips = batchNameOption.movieClips

        # sounds
        scene.BatchName.sounds = batchNameOption.sounds

        # screens
        scene.BatchName.screens = batchNameOption.screens

        # keying sets
        scene.BatchName.keyingSets = batchNameOption.keyingSets

        # palettes
        scene.BatchName.palettes = batchNameOption.palettes

        # brushes
        scene.BatchName.brushes = batchNameOption.brushes

        # linestyles
        scene.BatchName.linestyles = batchNameOption.linestyles

        # nodes
        scene.BatchName.nodes = batchNameOption.nodes

        # node labels
        scene.BatchName.nodeLabels = batchNameOption.nodeLabels

        # node groups
        scene.BatchName.nodeGroups = batchNameOption.nodeGroups

        # texts
        scene.BatchName.texts = batchNameOption.texts

        # custom name
        scene.BatchName.customName = batchNameOption.customName

        # find
        scene.BatchName.find = batchNameOption.find

        # regex
        scene.BatchName.regex = batchNameOption.regex

        # replace
        scene.BatchName.replace = batchNameOption.replace

        # prefix
        scene.BatchName.prefix = batchNameOption.prefix

        # suffix
        scene.BatchName.suffix = batchNameOption.suffix

        # suffix last
        scene.BatchName.suffixLast = batchNameOption.suffixLast

        # trim start
        scene.BatchName.trimStart = batchNameOption.trimStart

        # trim end
        scene.BatchName.trimEnd = batchNameOption.trimEnd

        # sort
        scene.BatchName.sort = batchNameOption.sort

        # start
        scene.BatchName.start = batchNameOption.start

        # padding
        scene.BatchName.padding = batchNameOption.padding

        # separator
        scene.BatchName.separator = batchNameOption.separator

        # sort only
        scene.BatchName.sortOnly = batchNameOption.sortOnly

  # copy
  if copy:
    for scene in bpy.data.scenes[:]:
      if scene != context.scene:

        # copy option
        batchCopyOption = context.scene.BatchCopyName

        # type
        scene.BatchCopyName.batchType = batchCopyOption.batchType

        # source
        scene.BatchCopyName.source = batchCopyOption.source

        # objects
        scene.BatchCopyName.objects = batchCopyOption.objects

        # object datas
        scene.BatchCopyName.objectData = batchCopyOption.objectData

        # materials
        scene.BatchCopyName.materials = batchCopyOption.materials

        # textures
        scene.BatchCopyName.textures = batchCopyOption.textures

        # particle systems
        scene.BatchCopyName.particleSystems = batchCopyOption.particleSystems

        # particle settings
        scene.BatchCopyName.particleSettings = batchCopyOption.particleSettings

        # use active object
        scene.BatchCopyName.useActiveObject = batchCopyOption.useActiveObject
