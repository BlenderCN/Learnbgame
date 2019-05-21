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
    for x in [base, menu]:
        imp.reload(x)
else:
    from . import base
    from . import menu
from .base import bpy, BPY, database, Operator, Entity, Bundle
from .menu import default_klasses, friction_tree

class Base(Operator):
    bl_label = "Frictions"
    bl_options = {'DEFAULT_CLOSED'}
    @classmethod
    def poll(cls, context):
        return True
    @classmethod
    def make_list(self, ListItem):
        bpy.types.Scene.friction_uilist = bpy.props.CollectionProperty(type = ListItem)
        bpy.types.Scene.friction_index = bpy.props.IntProperty(default=-1)
    @classmethod
    def delete_list(self):
        del bpy.types.Scene.friction_uilist
        del bpy.types.Scene.friction_index
    @classmethod
    def get_uilist(self, context):
        return context.scene.friction_index, context.scene.friction_uilist
    def set_index(self, context, value):
        context.scene.friction_index = value
    def prereqs(self, context):
        pass

klasses = default_klasses(friction_tree, Base)

class Modlugre(Entity):
	def string(self):
		string = ("modlugre, " + BPY.FORMAT(self.sigma0) + ", " + BPY.FORMAT(self.sigma1) + ", " + BPY.FORMAT(self.sigma2) + ", " + BPY.FORMAT(self.kappa) + ",\n" +
		"\t\t\t\"" + self.function.name + "\", ")
		if self.radius is not None:
			string += "simple plane hinge, " + BPY.FORMAT(self.radius)
		else:
			string += "simple"
		return string

class ModlugreOperator(Base):
    bl_label = "Modlugre"
    sigma0 = bpy.props.PointerProperty(type = BPY.Float)
    sigma1 = bpy.props.PointerProperty(type = BPY.Float)
    sigma2 = bpy.props.PointerProperty(type = BPY.Float)
    kappa = bpy.props.PointerProperty(type = BPY.Float)
    radius = bpy.props.PointerProperty(type = BPY.Float)
    function = bpy.props.PointerProperty(type = BPY.Function)
    def prereqs(self, context):
        self.sigma0.mandatory = True
        self.sigma1.mandatory = True
        self.sigma2.mandatory = True
        self.kappa.mandatory = True
        self.function.mandatory = True
    def assign(self, context):
        self.sigma0.assign(self.entity.sigma0)
        self.sigma1.assign(self.entity.sigma1)
        self.sigma2.assign(self.entity.sigma2)
        self.kappa.assign(self.entity.kappa)
        self.radius.assign(self.entity.radius)
        self.function.assign(self.entity.function)
    def store(self, context):
        self.entity.sigma0 = self.sigma0.store()
        self.entity.sigma1 = self.sigma1.store()
        self.entity.sigma2 = self.sigma2.store()
        self.entity.kappa = self.kappa.store()
        self.entity.radius = self.radius.store()
        self.entity.function = self.function.store()
    def draw(self, context):
        layout = self.layout
        self.sigma0.draw(layout, "Sigma0")
        self.sigma1.draw(layout, "Sigma1")
        self.sigma2.draw(layout, "Sigma2")
        self.kappa.draw(layout, "Kappa")
        self.radius.draw(layout, "Radius")
        self.function.draw(layout, "function")
    def check(self, context):
        return True in [v.check(context) for v in [self.sigma0, self.sigma1, self.sigma2, self.kappa, self.radius, self.function]]
    def create_entity(self):
        return Modlugre(self.name)

klasses[ModlugreOperator.bl_label] = ModlugreOperator

bundle = Bundle(friction_tree, Base, klasses, database.friction)
