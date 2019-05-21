
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
from ...defaults import defaults

# main
def main(context):

  # option
  option = context.scene.NamePanel

  # default
  default = defaults['name panel']

  # options
  default['pin active object'] = option.pinActiveObject
  default['hide search'] = option.hideSearch
  default['filters'] = option.filters
  default['options'] = option.options
  default['display names'] = option.displayNames
  default['search'] = option.search
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
  default['vertex color'] = option.vertexColors
  default['materials'] = option.materials
  default['textures'] = option.textures
  default['particle systems'] = option.particleSystems
  default['bone mode'] = option.boneMode
  default['display bones'] = option.displayBones

  # generate
  generate.main(defaults)
