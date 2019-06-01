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
    for x in [base, menu, common]:
        imp.reload(x)
else:
    from . import base
    from . import menu
    from . import common
from .base import bpy, BPY, database, Operator, Entity, Bundle
from .common import FORMAT
from .menu import default_klasses, shape_tree

class Base(Operator):
    bl_label = "Shapes"
    bl_options = {'DEFAULT_CLOSED'}
    @classmethod
    def poll(cls, context):
        return True
    @classmethod
    def make_list(self, ListItem):
        bpy.types.Scene.shape_uilist = bpy.props.CollectionProperty(type = ListItem)
        bpy.types.Scene.shape_index = bpy.props.IntProperty(default=-1)
    @classmethod
    def delete_list(self):
        del bpy.types.Scene.shape_uilist
        del bpy.types.Scene.shape_index
    @classmethod
    def get_uilist(self, context):
        return context.scene.shape_index, context.scene.shape_uilist
    def set_index(self, context, value):
        context.scene.shape_index = value

klasses = default_klasses(shape_tree, Base)

class ConstShape(Entity):
    def string(self):
        return '\t\tconst, '+ BPY.FORMAT(self.constant)

class ConstShapeOperator(Base):
    bl_label = "Const shape"
    constant = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.constant.mandatory = True
    def assign(self, context):
        self.constant.assign(self.entity.constant)
    def store(self, context):
        self.entity.constant = self.constant.store()
    def draw(self, context):
        self.constant.draw(self.layout, "Constant")
    def check(self, context):
        return self.constant.check(context)
    def create_entity(self):
        return ConstShape(self.name)

klasses[ConstShapeOperator.bl_label] = ConstShapeOperator

class PiecewiseConstShape(Entity):
    def string(self):
        ret += "\t\tpiecewise const, " + BPY.FORMAT(self.N)
        for i in range(self.N):
            ret += ",\n\t\t\t" + BPY.FORMAT(self.X[i]) + ", " + BPY.FORMAT(self.Y[i])
        return ret

class Multiple(Base):
    N = bpy.props.IntProperty(name="Number of points", min=2, max=50, description="", default=2)
    X = bpy.props.CollectionProperty(type = BPY.Float)
    Y = bpy.props.CollectionProperty(type = BPY.Float)
    def prereqs(self, context):
        self.X.clear()
        self.Y.clear()
        for i in range(50):
            x = self.X.add()
            x.mandatory = True
            y = self.Y.add()
            y.mandatory = True
    def assign(self, context):
        self.N = self.entity.N
        for i, x in enumerate(self.entity.X):
            self.X[i].assign(x)
        for i, y in enumerate(self.entity.Y):
            self.Y[i].assign(y)
    def store(self, context):
        self.entity.N = self.N
        self.entity.X = [x.store() for x in self.X][:self.entity.N]
        self.entity.Y = [y.store() for y in self.Y][:self.entity.N]
    def draw(self, context):
        self.basis = self.N
        layout = self.layout
        layout.prop(self, "N")
        row = layout.row()
        row.label("Abscissa")
        row.label("Value")
        for i in range(self.N):
            row = layout.row()
            self.X[i].draw(row, "")
            self.Y[i].draw(row, "")
    def check(self, context):
        return (self.basis != self.N) or True in [x.check(context) for x in self.X] + [y.check(context) for y in self.Y]

class PiecewiseConstShapeOperator(Multiple):
    bl_label = "Piecewise const shape"
    def create_entity(self):
        return PiecewiseConstShape(self.name)

klasses[PiecewiseConstShapeOperator.bl_label] = PiecewiseConstShapeOperator

class LinearShape(Entity):
    def string(self):
        return '\t\tlinear, ' + ", ".join([BPY.FORMAT(y) for y in [self.y1, self.y2]])

class LinearShapeOperator(Base):
    bl_label = "Linear shape"
    y1 = bpy.props.PointerProperty(type = BPY.Float)
    y2 = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.y1.mandatory = True
        self.y2.mandatory = True
    def assign(self, context):
        self.y1.assign(self.entity.y1)
        self.y2.assign(self.entity.y2)
    def store(self, context):
        self.entity.y1 = self.y1.store()
        self.entity.y2 = self.y2.store()
    def draw(self, context):
        self.y1.draw(self.layout, "y1")
        self.y2.draw(self.layout, "y2")
    def check(self, context):
        return self.y1.check(context) or self.y2.check(context)
    def create_entity(self):
        return LinearShape(self.name)

klasses[LinearShapeOperator.bl_label] = LinearShapeOperator

class PiecewiseLinearShape(Entity):
    def string(self):
        ret += "\t\tpiecewise linear, " + BPY.FORMAT(self.N)
        for i in range(self.N):
            ret += ",\n\t\t\t" + BPY.FORMAT(self.X[i]) + ", " + BPY.FORMAT(self.Y[i])
        return ret

class PiecewiseLinearShapeOperator(Multiple):
    bl_label = "Piecewise linear shape"
    def create_entity(self):
        return PiecewiseLinearShape(self.name)

klasses[PiecewiseLinearShapeOperator.bl_label] = PiecewiseLinearShapeOperator

class ParabolicShape(Entity):
    def string(self):
        return '\t\tparabolic' + ", ".join([BPY.FORMAT(y) for y in [self.y1, self.y2, self.y3]])

class ParabolicShapeOperator(Base):
    bl_label = "Parabolic shape"
    y1 = bpy.props.PointerProperty(type = BPY.Float)
    y2 = bpy.props.PointerProperty(type = BPY.Float)
    y3 = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.y1.mandatory = True
        self.y2.mandatory = True
        self.y3.mandatory = True
    def assign(self, context):
        self.y1.assign(self.entity.y1)
        self.y2.assign(self.entity.y2)
        self.y3.assign(self.entity.y3)
    def store(self, context):
        self.entity.y1 = self.y1.store()
        self.entity.y2 = self.y2.store()
        self.entity.y3 = self.y3.store()
    def draw(self, context):
        self.y1.draw(self.layout, "y1 (at x=-1)")
        self.y2.draw(self.layout, "y2 (at x=0)")
        self.y3.draw(self.layout, "y3 (at x=1)")
    def check(self, context):
        return self.y1.check(context) or self.y2.check(context) or self.y3.check(context)
    def create_entity(self):
        return ParabolicShape(self.name)

klasses[ParabolicShapeOperator.bl_label] = ParabolicShapeOperator

bundle = Bundle(shape_tree, Base, klasses, database.shape)
