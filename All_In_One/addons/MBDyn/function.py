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
    for x in [base, common, menu]:
        imp.reload(x)
else:
    from . import base
    from . import common
    from . import menu
from .base import bpy, database, Operator, Entity, Bundle, BPY
from .common import FORMAT
from .menu import default_klasses, function_tree

class Base(Operator):
    bl_label = "Functions"
    bl_options = {'DEFAULT_CLOSED'}
    @classmethod
    def poll(cls, context):
        return True
    @classmethod
    def make_list(self, ListItem):
        bpy.types.Scene.function_uilist = bpy.props.CollectionProperty(type = ListItem)
        bpy.types.Scene.function_index = bpy.props.IntProperty(default=-1)
    @classmethod
    def delete_list(self):
        del bpy.types.Scene.function_uilist
        del bpy.types.Scene.function_index
    @classmethod
    def get_uilist(self, context):
        return context.scene.function_index, context.scene.function_uilist
    def set_index(self, context, value):
        context.scene.function_index = value

klasses = default_klasses(function_tree, Base)

class Const(Entity):
    def write(self, f):
        f.write("scalar function: \"" + self.name + "\", const, " + BPY.FORMAT(self.constant) + ";\n")

class ConstOperator(Base):
    bl_label = "Const"
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
        return Const(self.name)

klasses[ConstOperator.bl_label] = ConstOperator

class Exp(Entity):
    def write(self, f):
        f.write("scalar function: \"" + self.name + "\", exp")
        if self.base is not None:
            f.write(", base, " + BPY.FORMAT(self.base))
        if self.coefficient is not None:
            f.write(", coefficient, " + BPYFORMAT(self.coefficient))
        f.write(", " + BPY.FORMAT(self.multiplier) + ";\n")

class ExpLog(Base):
    base = bpy.props.PointerProperty(type = BPY.Float)
    coefficient = bpy.props.PointerProperty(type = BPY.Float)
    multiplier = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.multiplier.mandatory = True
    def assign(self, context):
        self.base.assign(self.entity.base)
        self.coefficient.assign(self.entity.coefficient)
        self.multiplier.assign(self.entity.multiplier)
    def store(self, context):
        self.entity.base = self.base.store()
        self.entity.coefficient = self.coefficient.store()
        self.entity.multiplier = self.multiplier.store()
    def draw(self, context):
        self.base.draw(self.layout, "Base (else e)")
        self.coefficient.draw(self.layout, "Coefficient (else 1)")
        self.multiplier.draw(self.layout, "Multiplier")
    def check(self, context):
        return self.base.check(context) or self.coefficient.check(context) or self.multiplier.check(context)

class ExpOperator(ExpLog):
    bl_label = "Exp"
    def create_entity(self):
        return Exp(self.name)

klasses[ExpOperator.bl_label] = ExpOperator

class Log(Entity):
    def write(self, f):
        f.write("scalar function: \"" + self.name + "\", log")
        if self.base is not None:
            f.write(", base, " + BPY.FORMAT(self.base))
        if self.coefficient is not None:
            f.write(", coefficient, " + BPY.FORMAT(self.coefficient))
        f.write(", " + FORMAT(self.multiplier) + ";\n")

class LogOperator(ExpLog):
    bl_label = "Log"
    def create_entity(self):
        return Log(self.name)

klasses[LogOperator.bl_label] = LogOperator

class Pow(Entity):
    def write(self, f):
        f.write("scalar function: \"" + self.name + "\", pow, " + BPY.FORMAT(self.power) + ";\n")

class PowOperator(Base):
    bl_label = "Pow"
    power = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.power.mandatory = True
    def assign(self, context):
        self.power.assign(self.entity.power)
    def store(self, context):
        self.entity.power = self.power.store()
    def draw(self, context):
        self.power.draw(self.layout, "Power")
    def check(self, context):
        return self.power.check(context)
    def create_entity(self):
        return Pow(self.name)

klasses[PowOperator.bl_label] = PowOperator

class Linear(Entity):
    def write(self, f):
        f.write("scalar function: \"" + self.name + "\", linear")
        f.write(",\n\t\t" + ", ".join([BPY.FORMAT(x) for x in self.X]))
        f.write(", " + ", ".join([BPY.FORMAT(x) for x in self.X]) + ";\n")

class LinearOperator(Base):
    bl_label = "Linear"
    X = bpy.props.CollectionProperty(type = BPY.Float)
    Y = bpy.props.CollectionProperty(type = BPY.Float)
    def prereqs(self, context):
        self.X.clear()
        self.Y.clear()
        for i in range(2):
            x = self.X.add()
            x.mandatory = True
            y = self.Y.add()
            y.mandatory = True
    def assign(self, context):
        for i, x in enumerate(self.entity.X):
            self.X[i].assign(x)
        for i, y in enumerate(self.entity.Y):
            self.Y[i].assign(y)
    def store(self, context):
        self.entity.X = [x.store() for x in self.X]
        self.entity.Y = [y.store() for y in self.Y]
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label("X")
        row.label("Y")
        for i in range(2):
            row = layout.row()
            self.X[i].draw(row, "")
            self.Y[i].draw(row, "")
    def check(self, context):
        return True in [x.check(context) for x in self.X] + [y.check(context) for y in self.Y]
    def create_entity(self):
        return Linear(self.name)

klasses[LinearOperator.bl_label] = LinearOperator

class CubicNaturalSpline(Entity):
    def write(self, f):
        f.write("scalar function: \"" + self.name + "\", cubicspline")
        if not self.extrapolate:
            f.write(", do not extrapolate")
        for i in range(self.N):
            f.write(",\n\t\t" + BPY.FORMAT(self.X[i]) + ", " + BPY.FORMAT(self.Y[i]))
        f.write(";\n")

class Multiple(Base):
    extrapolate = bpy.props.BoolProperty(name="Extrapolate", default=True)
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
        self.extrapolate = self.entity.extrapolate
        self.N = self.entity.N
        for i, x in enumerate(self.entity.X):
            self.X[i].assign(x)
        for i, y in enumerate(self.entity.Y):
            self.Y[i].assign(y)
    def store(self, context):
        self.entity.extrapolate = self.extrapolate
        self.entity.N = self.N
        self.entity.X = [x.store() for x in self.X][:self.entity.N]
        self.entity.Y = [y.store() for y in self.Y][:self.entity.N]
    def draw(self, context):
        self.basis = self.N
        layout = self.layout
        layout.prop(self, "extrapolate")
        layout.prop(self, "N")
        row = layout.row()
        row.label("X")
        row.label("Y")
        for i in range(self.N):
            row = layout.row()
            self.X[i].draw(row, "")
            self.Y[i].draw(row, "")
    def check(self, context):
        return (self.basis != self.N) or True in [x.check(context) for x in self.X] + [y.check(context) for y in self.Y]

class CubicNaturalSplineOperator(Multiple):
    bl_label = "Cubic natural spline"
    def create_entity(self):
        return CubicNaturalSpline(self.name)

#klasses[CubicNaturalSplineOperator.bl_label] = CubicNaturalSplineOperator

class Multilinear(Entity):
    def write(self, f):
        f.write("scalar function: \"" + self.name + "\", multilinear")
        if not self.extrapolate:
            f.write(", do not extrapolate")
        for i in range(self.N):
            f.write(",\n\t\t" + BPY.FORMAT(self.X[i]) + ", " + BPY.FORMAT(self.Y[i]))
        f.write(";\n")

class MultilinearOperator(Multiple):
    bl_label = "Multilinear"
    def create_entity(self):
        return Multilinear(self.name)

klasses[MultilinearOperator.bl_label] = MultilinearOperator

class Chebychev(Entity):
    def write(self, f):
        f.write("scalar function: \"" + self.name + "\", chebychev")
        f.write(",\n\t\t" + BPY.FORMAT(self.lower_bound) + ", " + BPY.FORMAT(self.upper_bound))
        if not self.extrapolate:
            f.write(", do not extrapolate")
        N = int(self.N/4)
        for i in range(N):
            f.write(",\n\t\t" + ", ".join([BPY.FORMAT(c) for c in self.C[4*i:4*(i+1)]]))
        if 4*N == self.N:
            f.write(";\n")
        else:
            f.write(",\n\t\t" + ", ".join([BPY.FORMAT(c) for c in self.C[4*N:self.N]]) + ";\n")

class ChebychevOperator(Base):
    bl_label = "Chebychev"
    lower_bound = bpy.props.PointerProperty(type = BPY.Float)
    upper_bound = bpy.props.PointerProperty(type = BPY.Float)
    extrapolate = bpy.props.BoolProperty(name="Extrapolate", default=True)
    N = bpy.props.IntProperty(name="Number of points", min=2, max=50, description="", default=2)
    C = bpy.props.CollectionProperty(type = BPY.Float)
    def prereqs(self, context):
        self.lower_bound.mandatory = True
        self.upper_bound.mandatory = True
        self.C.clear()
        for i in range(50):
            c = self.C.add()
            c.mandatory = True
    def assign(self, context):
        self.lower_bound.assign(self.entity.lower_bound)
        self.upper_bound.assign(self.entity.upper_bound)
        self.extrapolate = self.entity.extrapolate
        self.N = len(self.entity.C)
        for i, value in enumerate(self.entity.C):
            self.C[i].assign(value)
    def store(self, context):
        self.entity.lower_bound = self.lower_bound.store()
        self.entity.upper_bound = self.upper_bound.store()
        self.entity.extrapolate = self.extrapolate
        self.entity.C = [c.store() for c in self.C][:self.N]
    def draw(self, context):
        self.basis = self.N
        layout = self.layout
        self.lower_bound.draw(layout, "Lower bound")
        self.upper_bound.draw(layout, "Upper bound")
        layout.prop(self, "extrapolate")
        layout.prop(self, "N")
        layout.label("Coefficients")
        for i in range(self.N):
            self.C[i].draw(layout, "")
    def check(self, context):
        return (self.basis != self.N) or self.lower_bound.check(context) or self.upper_bound.check(context) or True in [c.check(context) for c in self.C]
    def create_entity(self):
        return Chebychev(self.name)

klasses[ChebychevOperator.bl_label] = ChebychevOperator

class Sum(Entity):
    def write(self, f):
        f.write("scalar function: \"" + self.name + "\", sum")
        f.write(",\n\t\t\"" + self.functions[0].name + "\", \"" + self.functions[1].name + "\";\n")

class Binary(Base):
    functions = bpy.props.CollectionProperty(type = BPY.Function)
    def prereqs(self, context):
        self.functions.clear()
        for i in range(2):
            f = self.functions.add()
            f.mandatory = True
    def assign(self, context):
        for i, f in enumerate(self.entity.functions):
            self.functions[i].assign(f)
    def store(self, context):
        self.entity.functions = [f.store() for f in self.functions]
    def draw(self, context):
        layout = self.layout
        for i in range(2):
            self.functions[i].draw(layout, "Function " + str(i+1))
    def check(self, context):
        return True in [f.check(context) for f in self.functions]

class SumOperator(Binary):
    bl_label = "Sum"
    def create_entity(self):
        return Sum(self.name)

klasses[SumOperator.bl_label] = SumOperator

class Sub(Entity):
    def write(self, f):
        f.write("scalar function: \"" + self.name + "\", sub")
        f.write(",\n\t\t\"" + self.functions[0].name + "\", \"" + self.functions[1].name + "\";\n")

class SubOperator(Binary):
    bl_label = "Sub"
    def create_entity(self):
        return Sub(self.name)

klasses[SubOperator.bl_label] = SubOperator

class Mul(Entity):
    def write(self, f):
        f.write("scalar function: \"" + self.name + "\", mul")
        f.write(",\n\t\t\"" + self.functions[0].name + "\", \"" + self.functions[1].name + "\";\n")

class MulOperator(Binary):
    bl_label = "Mul"
    def create_entity(self):
        return Mul(self.name)

klasses[MulOperator.bl_label] = MulOperator

class Div(Entity):
    def write(self, f):
        f.write("scalar function: \"" + self.name + "\", div")
        f.write(",\n\t\t\"" + self.functions[0].name + "\", \"" + self.functions[1].name + "\";\n")

class DivOperator(Binary):
    bl_label = "Div"
    def create_entity(self):
        return Div(self.name)

klasses[DivOperator.bl_label] = DivOperator

bundle = Bundle(function_tree, Base, klasses, database.function)
