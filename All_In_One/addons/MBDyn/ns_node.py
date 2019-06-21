# --------------------------------------------------------------------------
# BlenderAndMBDyn
# Copyright (C) 2015 G. Douglas Baldwin - http://www.baldwintechnology.com
# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
#    This file is part of BlenderAndMBDyn.
#
#    BlenderAndMBDyn is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    BlenderAndMBDyn is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with BlenderAndMBDyn.  If not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
# -------------------------------------------------------------------------- 

if "bpy" in locals():
    import imp
    for x in [base]:
        imp.reload(x)
else:
    from . import base
from .base import bpy, database, Operator, Entity, Bundle

types = [
	"Electric",
	"Abstract",
	"Hydraulic",
	"Parameter"]

tree = ["NS Node", types]

klasses = dict()

class Base(Operator):
    bl_label = "NS Nodes"
    bl_options = {'DEFAULT_CLOSED'}
    @classmethod
    def poll(cls, context):
        return True
    @classmethod
    def make_list(self, ListItem):
        bpy.types.Scene.ns_node_uilist = bpy.props.CollectionProperty(type = ListItem)
        bpy.types.Scene.ns_node_index = bpy.props.IntProperty(default=-1)
    @classmethod
    def delete_list(self):
        del bpy.types.Scene.ns_node_uilist
        del bpy.types.Scene.ns_node_index
    @classmethod
    def get_uilist(self, context):
        return context.scene.ns_node_index, context.scene.ns_node_uilist
    def set_index(self, context, value):
        context.scene.ns_node_index = value

for t in types:
    class Tester(Base):
        bl_label = t
        @classmethod
        def poll(cls, context):
            return False
        def create_entity(self):
            return Entity(self.name)
    klasses[t] = Tester

bundle = Bundle(tree, Base, klasses, database.ns_node)
