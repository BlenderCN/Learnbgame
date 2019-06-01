
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

  # option
  option = context.scene.BatchName

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
  default['custom name'] = option.customName
  default['find'] = option.find
  default['regex'] = option.regex
  default['replace'] = option.replace
  default['prefix'] = option.prefix
  default['suffix'] = option.suffix
  default['suffix last'] = option.suffixLast
  default['trim start'] = option.trimStart
  default['trim end'] = option.trimEnd
  shared.main(context, context.scene.BatchShared, defaults['shared'])

  # generate
  generate.main(defaults)
