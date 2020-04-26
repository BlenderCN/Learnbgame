
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
from bpy.types import Operator
from ..text import cheatsheet

# generate cheatsheet
class generate(Operator):
  '''
    Generate regular expression cheatsheet.
  '''
  bl_idname = 'wm.regular_expression_cheatsheet'
  bl_label = 'Generate Cheatsheet'
  bl_description = 'Generate a text reference for regular expressions.'
  bl_options = {'UNDO'}

  # execute
  def execute(self, context):
    '''
      Execute the operator.
    '''

    # cheatsheet
    if not 'Regular Expressions Cheatsheet' in bpy.data.texts:

      # write
      bpy.data.texts.new('Regular Expressions Cheatsheet').write(cheatsheet)

      # place cursor
      bpy.data.texts['Regular Expressions Cheatsheet'].current_line_index = 0

      # info messege
      self.report({'INFO'}, 'See \'Regular Expressions Cheatsheet\' in text editor')
    return {'FINISHED'}
