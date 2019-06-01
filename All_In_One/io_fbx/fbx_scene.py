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


            
class CScene(CModel):

    def __init__(self, subtype='Null'):
        CModel.__init__(self, subtype, 'SCENE')
        self.objects = []


    def make(self, scn):
        CModel.make(self, scn)
        for ob in scn.objects:            
            try:
                node = fbx.nodes.objects[ob.name]
            except KeyError:
                continue
            node.makeOOLink(self)
            self.objects.append(ob)
        return self


    def build3(self):
        scn = fbx.data[self.id]
        return scn
        links = self.getBChildLinks('OBJECT')
        for link in links:
            ob = fbx.data[link.child.id]
            scn.objects.link(ob)
            scn.objects.active = ob
        return scn
        

