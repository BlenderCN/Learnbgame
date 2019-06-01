
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
  option = context.scene.BatchCopyName

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

  # generate
  generate.main(defaults)
