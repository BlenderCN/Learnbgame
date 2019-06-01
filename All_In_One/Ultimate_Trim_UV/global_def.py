# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2
#  of the License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from bpy.props import BoolProperty, EnumProperty

#######################
#   Global variables
#######################

#This variable is accessed by the settings UI and Buttons UI menus for changing the number of trims
trimTotal = 2

#Options for choosing how many trim segments
bpy.types.Scene.numTrims = EnumProperty(
    items = [
        ('2_trims', 'Two Trims', 'Choose the number of segments in your trim sheet'),
        ('3_trims', 'Three Trims', 'Choose the number of segments in your trim sheet'),
        ('4_trims', 'Four Trims', 'Choose the number of segments in your trim sheet'),
        ('5_trims', 'Five Trims', 'Choose the number of segments in your trim sheet'),
        ('6_trims', 'Six Trims', 'Choose the number of segments in your trim sheet'),
        ('7_trims', 'Seven Trims', 'Choose the number of segments in your trim sheet'),
        ('8_trims', 'Eight Trims', 'Choose the number of segments in your trim sheet'),
        ('9_trims', 'Nine Trims', 'Choose the number of segments in your trim sheet'),
        ('10_trims', 'Ten Trims', 'Choose the number of segments in your trim sheet'),
        ('11_trims', 'Eleven Trims', 'Choose the number of segments in your trim sheet'),
        ('12_trims', 'Twelve Trims', 'Choose the number of segments in your trim sheet')],
    name = "Number")

#Options for total resolution of texture image
bpy.types.Scene.trimRes = EnumProperty(
    items = [
        ('256', '256', 'Choose the vertical resolution of your texture file. For a complete trim sheet, adding the pixel height of all trim indexes together should equal this number.'),
        ('512', '512', 'Choose the vertical resolution of your texture file. For a complete trim sheet, adding the pixel height of all trim indexes together should equal this number.'),
        ('1024', '1024','Choose the vertical resolution of your texture file. For a complete trim sheet, adding the pixel height of all trim indexes together should equal this number.'),
        ('2048', '2048','Choose the vertical resolution of your texture file. For a complete trim sheet, adding the pixel height of all trim indexes together should equal this number.'),
        ('4096', '4096','Choose the vertical resolution of your texture file. For a complete trim sheet, adding the pixel height of all trim indexes together should equal this number.'),
        ('8192', '8192','Choose the vertical resolution of your texture file. For a complete trim sheet, adding the pixel height of all trim indexes together should equal this number.')],
    name = "Resolution",
    default = "1024"
)

#For storing the height of each trim as a percentage of 0-1 UV space
trimHeight = {}

#Used by makeislands function
bm = None
uvlayer = None

