
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
from . import generate
from . import shared
from ...defaults import defaults

# main
def main(context):

  # name
  name(context)

  # objects
  objects(context)

  # constraints
  constraints(context)

  # modifiers
  modifiers(context)

  # object data
  objectData(context)

  # generate
  generate.main(defaults)

# name
def name(context):

  # option
  option = context.scene.BatchAutoName

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
  shared.main(context, context.scene.BatchShared, defaults['shared'])

# objects
def objects(context):

  # option
  option = context.scene.BatchAutoName_ObjectNames

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

# constraints
def constraints(context):

  # option
  option = context.scene.BatchAutoName_ConstraintNames

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

# modifiers
def modifiers(context):

  # option
  option = context.scene.BatchAutoName_ModifierNames

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

# object data
def objectData(context):

  # option
  option = context.scene.BatchAutoName_ObjectDataNames

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
