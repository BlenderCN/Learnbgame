# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
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

from . import fbx
from .fbx_basic import *
from .fbx_props import *
from .fbx_model import *

#------------------------------------------------------------------
#   
#------------------------------------------------------------------


	ObjectType: "GlobalShading" {
		Count: 1
	}
	ObjectType: "Shader" {
		Count: 2
	}
	ObjectType: "ControlSetPlug" {
		Count: 1
	}
	ObjectType: "GroupExclusive" {
		Count: 1
	}
	ObjectType: "Character" {
		Count: 1
		PropertyTemplate: "FbxCharacter" {
			Properties70:  {
				P: "Active", "bool", "", "",1
				P: "Lock", "bool", "", "",0
				P: "Weight", "Weight", "", "A",100
			}
		}
	}
	ObjectType: "TimelineXTrack" {
		Count: 1
	}
