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
from .base import bpy, root_dot, database, Operator, Entity, Bundle, BPY
from .menu import default_klasses, constitutive_tree

class Base(Operator):
    bl_label = "Constitutives"
    bl_options = {'DEFAULT_CLOSED'}
    dimension_items = [("1D", "1D", ""), ("3D", "3D", ""), ("6D", "6D", "")]
    dimension = bpy.props.EnumProperty(items=dimension_items, name="Dimension")
    @classmethod
    def poll(cls, context):
        return True
    @classmethod
    def make_list(self, ListItem):
        bpy.types.Scene.constitutive_uilist = bpy.props.CollectionProperty(type = ListItem)
        bpy.types.Scene.constitutive_index = bpy.props.IntProperty(default=-1)
    @classmethod
    def delete_list(self):
        del bpy.types.Scene.constitutive_uilist
        del bpy.types.Scene.constitutive_index
    @classmethod
    def get_uilist(self, context):
        return context.scene.constitutive_index, context.scene.constitutive_uilist
    def set_index(self, context, value):
        context.scene.constitutive_index = value
    def draw_dimension(self, layout):
        if self.bl_idname.endswith("c_" + "_".join(self.name.lower().split())):
            layout.prop(self, "dimension")
        else:
            row = layout.row()
            row.label("Dimension:")
            row.label(self.dimension)
            row.label()

klasses = default_klasses(constitutive_tree, Base)

class Stiffness(Base):
    stiffness = bpy.props.PointerProperty(type = BPY.MatrixFloat)
    def prereqs(self, context):
        self.stiffness.mandatory = True
    def assign(self, context):
        self.dimension = self.entity.dimension
        self.stiffness.assign(self.entity.stiffness)
    def store(self, context):
        self.entity.dimension = self.dimension
        self.entity.stiffness = self.stiffness.store()
    def draw(self, context):
        self.basis = self.dimension
        layout = self.layout
        self.draw_dimension(layout)
        self.stiffness.draw(layout, "Stiffness")
    def check(self, context):
        return (self.basis != self.dimension) or self.stiffness.check(context)

class StiffnessN(Base):
    N = 3
    stiffness = bpy.props.CollectionProperty(type = BPY.MatrixFloat)
    def prereqs(self, context):
        self.stiffness.clear()
        for i in range(self.N):
            s = self.stiffness.add()
            s.mandatory = True
    def assign(self, context):
        self.dimension = self.entity.dimension
        for i, s in enumerate(self.entity.stiffness):
            self.stiffness[i].assign(s)
    def store(self, context):
        self.entity.dimension = self.dimension
        self.entity.stiffness = [s.store() for s in self.stiffness]
    def draw(self, context):
        self.basis = self.dimension
        layout = self.layout
        self.draw_dimension(layout)
        for i in range(self.N):
            self.stiffness[i].draw(layout, "Stiffness " + str(i+1))
    def check(self, context):
        return (self.basis != self.dimension) or True in [s.check(context) for s in self.stiffness]

class Viscosity(Base):
    viscosity = bpy.props.PointerProperty(type = BPY.MatrixFloat)
    def prereqs(self, context):
        self.viscosity.mandatory = True
    def assign(self, context):
        self.dimension = self.entity.dimension
        self.viscosity.assign(self.entity.viscosity)
    def store(self, context):
        self.entity.dimension = self.dimension
        self.entity.viscosity = self.viscosity.store()
    def draw(self, context):
        self.basis = self.dimension
        layout = self.layout
        self.draw_dimension(layout)
        self.viscosity.draw(layout, "Viscosity")
    def check(self, context):
        return (self.basis != self.dimension) or self.viscosity.check(context)

class StiffnessViscosity(Base):
    stiffness = bpy.props.PointerProperty(type = BPY.MatrixFloat)
    proportional = bpy.props.PointerProperty(type = BPY.Float)
    viscosity = bpy.props.PointerProperty(type = BPY.MatrixFloat)
    def prereqs(self, context):
        self.stiffness.mandatory = True
        self.viscosity.mandatory = True
    def assign(self, context):
        self.dimension = self.entity.dimension
        self.stiffness.assign(self.entity.stiffness)
        self.proportional.assign(self.entity.proportional)
        self.viscosity.assign(self.entity.viscosity)
    def store(self, context):
        self.entity.dimension = self.dimension
        self.entity.stiffness = self.stiffness.store()
        self.entity.proportional = self.proportional.store()
        self.entity.viscosity = self.viscosity.store() if self.entity.proportional is None else None
    def draw(self, context):
        self.basis = self.dimension
        layout = self.layout
        self.draw_dimension(layout)
        self.stiffness.draw(layout, "Stiffness")
        self.proportional.draw(layout, "Proportional")
        if not self.proportional.select:
            self.viscosity.draw(layout, "Viscosity")
    def check(self, context):
        return (self.basis != self.dimension) or self.stiffness.check(context) or self.proportional.check(context) or self.viscosity.check(context)

class LinearElastic(Entity):
    def string(self):
        if self.dimension == "1D":
            return "linear elastic, " + BPY.FORMAT(self.stiffness)
        else:
            return "linear elastic isotropic, " + BPY.FORMAT(self.stiffness)

class LinearElasticOperator(Stiffness):
    bl_label = "Linear elastic"
    def draw(self, context):
        self.stiffness.type = {"1D": "float", "3D": "float", "6D": "float"}[self.dimension]
        super().draw(context)
    def create_entity(self):
        return LinearElastic(self.name)

klasses[LinearElasticOperator.bl_label] = LinearElasticOperator

class LinearElasticGeneric(Entity):
    def string(self):
        if self.dimension == "1D":
            return "linear elastic generic, " + BPY.FORMAT(self.stiffness)
        else:
            return "linear elastic generic, " + self.stiffness.string()

class LinearElasticGenericOperator(Stiffness):
    bl_label = "Linear elastic generic"
    def draw(self, context):
        self.stiffness.type = {"1D": "float", "3D": "3x3", "6D": "6x6"}[self.dimension]
        super().draw(context)
    def create_entity(self):
        return LinearElasticGeneric(self.name)

klasses[LinearElasticGenericOperator.bl_label] = LinearElasticGenericOperator

class LinearElasticGenericAxialTorsionCoupling(Entity):
    def string(self):
        return "linear elastic generic axial torsion coupling," + self.stiffness.string() + ",\n\t\t" + BPY.FORMAT(self.coupling_coefficient)
                
class LinearElasticGenericAxialTorsionCouplingOperator(Stiffness):
    bl_label = "Linear elastic generic axial torsion coupling"
    dimension_items = [("6D", "6D", "")]
    dimension = bpy.props.EnumProperty(items=dimension_items, name="Dimension")
    coupling_coefficient = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.coupling_coefficient.mandatory = True
        self.coupling_coefficient.assign(1.0)
        super().prereqs(context)
    def assign(self, context):
        self.coupling_coefficient.assign(self.entity.coupling_coefficient)
        super().assign(context)
    def store(self, context):
        self.entity.coupling_coefficient = self.coupling_coefficient.store()
        super().store(context)
    def draw(self, context):
        self.stiffness.type = {"6D": "6x1"}[self.dimension]
        super().draw(context)
        self.coupling_coefficient.draw(self.layout, "Coupling Coefficient")
    def check(self, context):
        return self.coupling_coefficient.check(context) or super().check(context)
    def create_entity(self):
        return LinearElasticGenericAxialTorsionCoupling(self.name)

#klasses[LinearElasticGenericAxialTorsionCouplingOperator.bl_label] = LinearElasticGenericAxialTorsionCouplingOperator

class CubicElasticGeneric(Entity):
    def string(self):
        ret = "cubic elastic generic, "
        if self.dimension == "1D":
            ret += ", ".join([BPY.FORMAT(s) for s in self.stiffness])
        else:
            ret += ", ".join([s.string() for s in self.stiffness])
        return ret

class CubicElasticGenericOperator(StiffnessN):
    bl_label = "Cubic elastic generic"
    dimension_items = [("1D", "1D", ""), ("3D", "3D", "")]
    dimension = bpy.props.EnumProperty(items=dimension_items, name="Dimension")
    def draw(self, context):
        for s in self.stiffness:
            s.type = {"1D": "float", "3D": "3x1"}[self.dimension]
        super().draw(context)
    def create_entity(self):
        return CubicElasticGeneric(self.name)

klasses[CubicElasticGenericOperator.bl_label] = CubicElasticGenericOperator

class InverseSquareElastic(Entity):
    def string(self):
        return "inverse square elastic, " + BPY.FORMAT(self.stiffness) + ", " + BPY.FORMAT(self.reference_length)

class InverseSquareElasticOperator(Stiffness):
    bl_label = "Inverse square elastic"
    dimension_items = [("1D", "1D", ""), ]
    dimension = bpy.props.EnumProperty(items=dimension_items, name="Dimension")
    reference_length = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.reference_length.mandatory = True
        super().prereqs(context)
    def assign(self, context):
        self.reference_length.assign(self.entity.ref_length)
        super().assign(context)
    def store(self, context):
        self.entity.reference_length = self.reference_length.store()
        super().store(context)
    def draw(self, context):
        self.stiffness.type = {"1D": "float"}[self.dimension]
        super().draw(context)
        self.reference_length.draw(self.layout, "Reference lendth")
    def check(self, context):
        return self.reference_length.check(context) or super().check(context)
    def create_entity(self):
        return InverseSquareElastic(self.name)

klasses[InverseSquareElasticOperator.bl_label] = InverseSquareElasticOperator

class LogElastic(Entity):
    def string(self):
        return "log elastic, " + BPY.FORMAT(self.stiffness)

class LogElasticOperator(Stiffness):
    bl_label = "Log elastic"
    dimension_items = [("1D", "1D", ""), ]
    dimension = bpy.props.EnumProperty(items=dimension_items, name="Dimension")
    def draw(self, context):
        self.stiffness.type = {"1D": "float"}[self.dimension]
        super().draw(context)
    def create_entity(self):
        return LogElastic(self.name)

klasses[LogElasticOperator.bl_label] = LogElasticOperator

class LinearElasticBistop(Entity):
    def string(self):
        ret = "linear elastic bistop"
        if self.dimension == "1D":
            ret += ",\n\t\t" + BPY.FORMAT(self.stiffness)
        else:
            ret += ", " + self.stiffness.string()
        ret += ",\n\t\tinitial status, " + self.initial_status
        for drive in [self.activating_condition, self.activating_condition]:
            ret += ",\n\t\t" + drive.string()
        return ret

class LinearElasticBistopOperator(Stiffness):
    bl_label = "Linear elastic bistop"
    initial_status = bpy.props.EnumProperty(items=[("active", "Active", ""), ("inactive", "Inactive", "")], name="Initial status")
    activating_condition = bpy.props.PointerProperty(type = BPY.Drive)
    deactivating_condition = bpy.props.PointerProperty(type = BPY.Drive)
    def prereqs(self, context):
        self.activating_condition.mandatory = True
        self.deactivating_condition.mandatory = True
        super().prereqs(context)
    def assign(self, context):
        self.initial_status = self.entity.initial_status
        self.activating_condition.assign(self.entity.activating_condition)
        self.deactivating_condition.assign(self.entity.deactivating_condition)
        super().assign(context)
    def store(self, context):
        self.entity.initial_status = self.initial_status
        self.entity.activating_condition = self.activating_condition.store()
        self.entity.deactivating_condition = self.deactivating_condition.store()
        super().store(context)
    def draw(self, context):
        self.stiffness.type = {"1D": "float", "3D": "3x3", "6D": "6x6"}[self.dimension]
        super().draw(context)
        layout = self.layout
        layout.prop(self, "initial_status")
        self.activating_condition.draw(layout, "Activating condition")
        self.deactivating_condition.draw(layout, "Deactivatating condition")
    def check(self, context):
        return super().check(context) or self.activating_condition.check(context) or self.deactivating_condition.check(context)
    def create_entity(self):
        return LinearElasticBistop(self.name)

#klasses[LinearElasticBistopOperator.bl_label] = LinearElasticBistopOperator

class DoubleLinearElastic(Entity):
    def string(self):
        ret = "double linear elastic"
        if self.dimension == "1D":
            ret += ", " + BPY.FORMAT(self.stiffness[0])
            ret += ", " + BPY.FORMAT(self.upper_strain) + ", " + BPY.FORMAT(self.lower_strain)
            ret += ", " + BPY.FORMAT(self.stiffness[1])
        else:
            ret += "," + self.stiffness[0].string()
            ret += ",\n\t\t" + BPY.FORMAT(self.upper_strain) + ", " + BPY.FORMAT(self.lower_strain)
            ret += "," + self.stiffness[1].string()
        return ret

class DoubleLinearElasticOperator(StiffnessN):
    N = 2
    bl_label = "Double linear elastic"
    dimension_items = [("1D", "1D", ""), ("3D", "3D", "")]
    dimension = bpy.props.EnumProperty(items=dimension_items, name="Dimension")
    upper_strain = bpy.props.PointerProperty(type = BPY.Float)
    lower_strain = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.upper_strain.mandatory = True
        self.lower_strain.mandatory = True
        super().prereqs(context)
    def assign(self, context):
        self.upper_strain.assign(self.entity.upper_strain)
        self.lower_strain.assign(self.entity.lower_strain)
        super().assign(context)
    def store(self, context):
        self.entity.upper_strain = self.upper_strain.store()
        self.entity.lower_strain = self.lower_strain.store()
        super().store(context)
    def draw(self, context):
        for s in self.stiffness:
            s.type = {"1D": "float", "3D": "3x1"}[self.dimension]
        super().draw(context)
        layout = self.layout
        self.upper_strain.draw(layout, "Upper strain")
        self.lower_strain.draw(layout, "Lower strain")
    def check(self, context):
        return super().check(context) or self.upper_strain.check(context) or self.lower_strain.check(context)
    def create_entity(self):
        return DoubleLinearElastic(self.name)

#klasses[DoubleLinearElasticOperator.bl_label] = DoubleLinearElasticOperator

class IsotropicHardeningElastic(Entity):
    def string(self):
        ret = "isotropic hardening elastic"
        if self.dimension == "1D":
            ret += ",\n\t\t" + BPY.FORMAT(self.stiffness)
        else:
            ret += ", " + self.stiffness.string()
        ret += ",\n\t\t" + BPY.FORMAT(self.reference_strain)
        if self.linear_stiffness is not None:
            ret += ", linear stiffness, " + BPY.FORMAT(self.linear_stiffness)
        return ret

class IsotropicHardeningElasticOperator(Stiffness):
    bl_label = "Isotropic hardening elastic"
    reference_strain = bpy.props.PointerProperty(type = BPY.Float)
    linear_stiffness = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.reference_strain.mandatory = True
        super().prereqs(context)
    def assign(self, context):
        self.reference_strain.assign(self.entity.reference_strain)
        self.linear_stiffness.assign(self.entity.linear_stiffness)
        super().assign(context)
    def store(self, context):
        self.entity.reference_strain = self.reference_strain.store()
        self.entity.linear_stiffness = self.linear_stiffness.store()
        super().store(context)
    def draw(self, context):
        self.stiffness.type = {"1D": "float", "3D": "3x3", "6D": "6x6"}[self.dimension]
        super().draw(context)
        self.reference_strain.draw(self.layout, "Reference strain")
        self.linear_stiffness.draw(self.layout, "Linear stiffness")
    def check(self, context):
        return self.reference_strain.check(context) or self.linear_stiffness.check(context) or super().check(context)
    def create_entity(self):
        return IsotropicHardeningElastic(self.name)

klasses[IsotropicHardeningElasticOperator.bl_label] = IsotropicHardeningElasticOperator

class ScalarFunctionElasticIsotropic(Entity):
    def string(self):
        if self.dimension == "1D":
            return "scalar function elastic, \"" + self.function.name + "\""
        else:
            return "scalar function elastic isotropic, \"" + self.function.name + "\""

class ScalarFunctionElasticIsotropicOperator(Base):
    bl_label = "Scalar function elastic isotropic"
    function = bpy.props.PointerProperty(type = BPY.Function)
    def prereqs(self, context):
        self.function.mandatory = True
    def assign(self, context):
        self.dimension = self.entity.dimension
        self.function.assign(self.entity.function)
    def store(self, context):
        self.entity.dimension = self.dimension
        self.entity.function = self.function.store()
    def draw(self, context):
        self.basis = self.dimension
        layout = self.layout
        self.draw_dimension(layout)
        self.function.draw(layout, "Function")
    def check(self, context):
        return (self.basis != self.dimension) or self.function.check(context)
    def create_entity(self):
        return ScalarFunctionElasticIsotropic(self.name)

klasses[ScalarFunctionElasticIsotropicOperator.bl_label] = ScalarFunctionElasticIsotropicOperator

class ScalarFunctionElasticOrthotropic(Entity):
    def string(self):
        ret = "scalar function elastic"
        if self.dimension != "1D":
            ret += " orthotropic"
        for i in range(int(self.dimension[0])):
            if self.function[i] is None:
                ret += ",\n\t\tnull"
            else:
                ret += ",\n\t\t\"" + self.function[i].name + "\""
        return ret

class ScalarFunctionElasticOrthotropicOperator(Base):
    bl_label = "Scalar function elastic orthotropic"
    N = 6
    function = bpy.props.CollectionProperty(type = BPY.Function)
    def prereqs(self, context):
        self.function.clear()
        for i in range(self.N):
            s = self.function.add()
    def assign(self, context):
        self.dimension = self.entity.dimension
        for i, s in enumerate(self.entity.function):
            self.function[i].assign(s)
    def store(self, context):
        self.entity.dimension = self.dimension
        self.entity.function = [s.store() for s in self.function]
    def draw(self, context):
        self.basis = self.dimension
        layout = self.layout
        self.draw_dimension(layout)
        for i in range(int(self.dimension[0])):
            self.function[i].draw(layout, "Function " + str(i+1))
    def check(self, context):
        return (self.basis != self.dimension) or True in [f.check(context) for f in self.function]
    def create_entity(self):
        return ScalarFunctionElasticOrthotropic(self.name)

klasses[ScalarFunctionElasticOrthotropicOperator.bl_label] = ScalarFunctionElasticOrthotropicOperator

class LinearViscous(Entity):
    def string(self):
        if self.dimension == "1D":
            return "linear viscous, " + BPY.FORMAT(self.viscosity)
        else:
            return "linear viscous isotropic, " + BPY.FORMAT(self.viscosity)

class LinearViscousOperator(Viscosity):
    bl_label = "Linear viscous"
    def draw(self, context):
        self.viscosity.type = {"1D": "float", "3D": "float", "6D": "float"}[self.dimension]
        super().draw(context)
    def create_entity(self):
        return LinearViscous(self.name)

klasses[LinearViscousOperator.bl_label] = LinearViscousOperator

class LinearViscousGeneric(Entity):
    def string(self):
        if self.dimension == "1D":
            return "linear viscous generic, " + BPY.FORMAT(self.viscosity)
        else:
            return "linear viscous generic, " + self.viscosity.string()

class LinearViscousGenericOperator(Viscosity):
    bl_label = "Linear viscous generic"
    def draw(self, context):
        self.viscosity.type = {"1D": "float", "3D": "3x3", "6D": "6x6"}[self.dimension]
        super().draw(context)
    def create_entity(self):
        return LinearViscousGeneric(self.name)

klasses[LinearViscousGenericOperator.bl_label] = LinearViscousGenericOperator

class LinearViscoelastic(Entity):
    def string(self):
        ret = "linear viscoelastic"
        if self.dimension == "1D":
            ret += ", " + BPY.FORMAT(self.stiffness)
        else:
            ret += " isotropic, " + BPY.FORMAT(self.stiffness)
        if self.proportional is not None:
            ret += ", proportional, " + BPY.FORMAT(self.proportional)
        else:
            ret += ", " + BPY.FORMAT(self.viscosity)
        return ret

class LinearViscoelasticOperator(StiffnessViscosity):
    bl_label = "Linear viscoelastic"
    def draw(self, context):
        self.stiffness.type = {"1D": "float", "3D": "float", "6D": "float"}[self.dimension]
        self.viscosity.type = {"1D": "float", "3D": "float", "6D": "float"}[self.dimension]
        super().draw(context)
    def create_entity(self):
        return LinearViscoelastic(self.name)

klasses[LinearViscoelasticOperator.bl_label] = LinearViscoelasticOperator

class LinearViscoelasticGeneric(Entity):
    def string(self):
        ret = "linear viscoelastic generic"
        if self.dimension == "1D":
            ret += ", " + BPY.FORMAT(self.stiffness)
        else:
            ret += ", " + self.stiffness.string()
        if self.proportional is not None:
            ret += ", proportional, " + BPY.FORMAT(self.proportional)
        else:
            if self.dimension == "1D":
                ret += ", " + BPY.FORMAT(self.viscosity)
            else:
                ret += ", " + self.viscosity.string()
        return ret

class LinearViscoelasticGenericOperator(StiffnessViscosity):
    bl_label = "Linear viscoelastic generic"
    def draw(self, context):
        self.stiffness.type = {"1D": "float", "3D": "3x3", "6D": "6x6"}[self.dimension]
        self.viscosity.type = {"1D": "float", "3D": "3x3", "6D": "6x6"}[self.dimension]
        super().draw(context)
    def create_entity(self):
        return LinearViscoelasticGeneric(self.name)

klasses[LinearViscoelasticGenericOperator.bl_label] = LinearViscoelasticGenericOperator

class LinearTimeVariantViscoelasticGeneric(Entity):
    def string(self):
        ret = "linear time variant viscoelastic generic"
        if self.dimension == "1D":
            ret += ", " + BPY.FORMAT(self.stiffness)
        else:
            ret += ", " + self.stiffness.string()
        ret += ", " + self.stiffness_scale.string()
        if self.proportional is not None:
            ret += ", proportional, " + BPY.FORMAT(self.proportional)
        else:
            if self.dimension == "1D":
                ret += ", " + BPY.FORMAT(self.viscosity)
            else:
                ret += ", " + self.viscosity.string()
        ret += ", " + self.viscosity_scale.string()
        return ret

class LinearTimeVariantViscoelasticGenericOperator(StiffnessViscosity):
    bl_label = "Linear time variant viscoelastic generic"
    stiffness_scale = bpy.props.PointerProperty(type = BPY.Drive)
    viscosity_scale = bpy.props.PointerProperty(type = BPY.Drive)
    def prereqs(self, context):
        self.stiffness_scale.mandatory = True
        self.viscosity_scale.mandatory = True
        super().prereqs(context)
    def assign(self, context):
        self.stiffness_scale.assign(self.entity.stiffness_scale)
        self.viscosity_scale.assign(self.entity.viscosity_scale)
        super().assign(context)
    def store(self, context):
        super().store(context)
        self.entity.stiffness_scale = self.stiffness_scale.store() if self.entity.proportional is None else None
        self.entity.viscosity_scale = self.viscosity_scale.store() if self.entity.proportional is None else None
    def draw(self, context):
        self.basis = self.dimension
        self.stiffness.type = {"1D": "float", "3D": "3x3", "6D": "6x6"}[self.dimension]
        self.viscosity.type = {"1D": "float", "3D": "3x3", "6D": "6x6"}[self.dimension]
        layout = self.layout
        self.draw_dimension(layout)
        self.stiffness.draw(layout, "Stiffness")
        self.stiffness_scale.draw(layout, "Stiffness scale")
        self.proportional.draw(layout, "Proportional")
        if not self.proportional.select:
            self.viscosity.draw(layout, "Viscosity")
            self.viscosity_scale.draw(layout, "Viscosity scale")
    def check(self, context):
        return super().check(context) or self.stiffness_scale.check(context) or self.viscosity_scale.check(context)
    def create_entity(self):
        return LinearTimeVariantViscoelasticGeneric(self.name)

klasses[LinearTimeVariantViscoelasticGenericOperator.bl_label] = LinearTimeVariantViscoelasticGenericOperator

class LinearViscoelasticGenericAxialTorsionCoupling(Entity):
    def string(self):
        ret = "linear viscoelastic generic axial torsion coupling"
        ret += "," + self.stiffness.string()
        if self.proportional is not None:
            ret += ",\n\t\tproportional, " + BPY.FORMAT(self.proportional)
        else:
            ret += "," + self.viscosity.string()
        ret += ",\n\t\t" + BPY.FORMAT(self.coupling_coefficient)
        return ret

class LinearViscoelasticGenericAxialTorsionCouplingOperator(StiffnessViscosity):
    bl_label = "Linear viscoelastic generic axial torsion couple"
    dimension_items = [("6D", "6D", ""),]
    dimension = bpy.props.EnumProperty(items=dimension_items, name="Dimension")
    coupling_coefficient = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.coupling_coefficient.mandatory = True
        self.coupling_coefficient.assign(1.0)
        super().prereqs(context)
    def assign(self, context):
        self.coupling_coefficient.assign(self.entity.coupling_coefficient)
        super().assign(context)
    def store(self, context):
        self.entity.coupling_coefficient = self.coupling_coefficient.store()
        super().store(context)
    def draw(self, context):
        self.stiffness.type = {"6D": "6x1"}[self.dimension]
        self.viscosity.type = {"6D": "6x1"}[self.dimension]
        super().draw(context)
        self.coupling_coefficient.draw(self.layout, "Coupling Coefficient")
    def check(self, context):
        return self.coupling_coefficient.check(context) or super().check(context)
    def create_entity(self):
        return LinearViscoelasticGenericAxialTorsionCoupling(self.name)

#klasses[LinearViscoelasticGenericAxialTorsionCouplingOperator.bl_label] = LinearViscoelasticGenericAxialTorsionCouplingOperator

class CubicViscoelasticGeneric(Entity):
    def string(self):
        ret = "cubic viscoelastic generic"
        if self.dimension == "1D":
            for s in self.stiffness:
                ret += ", " + BPY.FORMAT(s)
            ret += ", " + BPY.FORMAT(self.viscosity)
        else:
            for s in self.stiffness:
                ret += ", " + s.string()
            ret += ", " + self.viscosity.string()
        return ret

class CubicViscoelasticGenericOperator(StiffnessN):
    bl_label = "Cubic viscoelastic generic"
    dimension_items = [("1D", "1D", ""), ("3D", "3D", "")]
    dimension = bpy.props.EnumProperty(items=dimension_items, name="Dimension")
    viscosity = bpy.props.PointerProperty(type = BPY.MatrixFloat)
    def prereqs(self, context):
        self.viscosity.mandatory = True
        super().prereqs(context)
    def assign(self, context):
        self.viscosity.assign(self.entity.viscosity)
        super().assign(context)
    def store(self, context):
        self.entity.viscosity = self.viscosity.store()
        super().store(context)
    def draw(self, context):
        for s in self.stiffness:
            s.type = {"1D": "float", "3D": "3x1"}[self.dimension]
        self.viscosity.type = {"1D": "float", "3D": "3x1"}[self.dimension]
        super().draw(context)
        self.viscosity.draw(self.layout, "Viscosity")
    def check(self, context):
        return self.viscosity.check(context) or super().check(context)
    def create_entity(self):
        return CubicViscoelasticGeneric(self.name)

#klasses[CubicViscoelasticGenericOperator.bl_label] = CubicViscoelasticGenericOperator

class DoubleLinearViscoelastic(Entity):
    def string(self):
        ret = "double linear viscoelastic"
        if self.dimension == "1D":
            ret += ", " + BPY.FORMAT(self.stiffness[0])
            ret += ", " + BPY.FORMAT(self.upper_strain) + ", " + BPY.FORMAT(self.lower_strain)
            ret += ", " + BPY.FORMAT(self.stiffness[1])
            ret += ", " + BPY.FORMAT(self.viscosity_1)
            if self.viscosity_2 is not None:
                ret += ", second damping, " + BPY.FORMAT(self.viscosity_2)
        else:
            ret += "," + self.stiffness[0].string()
            ret += ",\n\t\t" + BPY.FORMAT(self.upper_strain) + ", " + BPY.FORMAT(self.lower_strain)
            ret += "," + self.stiffness[1].string()
            ret += "," + self.viscosity_1.string()
            if self.viscosity_2 is not None:
                ret += ", second damping, " + self.viscosity_2.string()
        return ret

class DoubleLinearViscoelasticOperator(StiffnessN):
    N = 2
    bl_label = "Double linear viscoelastic"
    dimension_items = [("1D", "1D", ""), ("3D", "3D", "")]
    dimension = bpy.props.EnumProperty(items=dimension_items, name="Dimension")
    upper_strain = bpy.props.PointerProperty(type = BPY.Float)
    lower_strain = bpy.props.PointerProperty(type = BPY.Float)
    viscosity_1 = bpy.props.PointerProperty(type = BPY.MatrixFloat)
    viscosity_2 = bpy.props.PointerProperty(type = BPY.MatrixFloat)
    def prereqs(self, context):
        self.upper_strain.mandatory = True
        self.lower_strain.mandatory = True
        self.viscosity_1.mandatory = True
        super().prereqs(context)
    def assign(self, context):
        self.upper_strain.assign(self.entity.upper_strain)
        self.lower_strain.assign(self.entity.lower_strain)
        self.viscosity_1.assign(self.entity.viscosity_1)
        self.viscosity_2.assign(self.entity.viscosity_2)
        super().assign(context)
    def store(self, context):
        self.entity.upper_strain = self.upper_strain.store()
        self.entity.lower_strain = self.lower_strain.store()
        self.entity.viscosity_1 = self.viscosity_1.store()
        self.entity.viscosity_2 = self.viscosity_2.store()
        super().store(context)
    def draw(self, context):
        for s in self.stiffness:
            s.type = {"1D": "float", "3D": "3x1"}[self.dimension]
        self.viscosity_1.type = {"1D": "float", "3D": "3x1"}[self.dimension]
        self.viscosity_2.type = {"1D": "float", "3D": "3x1"}[self.dimension]
        super().draw(context)
        self.upper_strain.draw(self.layout, "Upper strain")
        self.lower_strain.draw(self.layout, "Lower strain")
        self.viscosity_1.draw(self.layout, "Viscosity 1")
        self.viscosity_2.draw(self.layout, "Viscosity 2")
    def check(self, context):
        return (self.upper_strain.check(context) or self.lower_strain.check(context)
            or self.viscosity_1.check(context) or self.viscosity_2.check(context) or super().check(context))
    def create_entity(self):
        return DoubleLinearViscoelastic(self.name)

#klasses[DoubleLinearViscoelasticOperator.bl_label] = DoubleLinearViscoelasticOperator

class TurbulentViscoelastic(Entity):
    def string(self):
        ret = "turbulent viscoelastic, " + BPY.FORMAT(self.stiffness) + ", " + BPY.FORMAT(self.parabolic_viscosity)
        if self.threshold is not None:
            ret += ", " + BPY.FORMAT(self.threshold)
            if self.linear_viscosity is not None:
                ret += ", " + BPY.FORMAT(self.linear_viscosity)
        return ret

class TurbulentViscoelasticOperator(Base):
    bl_label = "Turbulent viscoelastic"
    dimension_items = [("1D", "1D", ""), ]
    dimension = bpy.props.EnumProperty(items=dimension_items, name="Dimension")
    stiffness = bpy.props.PointerProperty(type = BPY.Float)
    parabolic_viscosity = bpy.props.PointerProperty(type = BPY.Float)
    threshold = bpy.props.PointerProperty(type = BPY.Float)
    linear_viscosity = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.stiffness.mandatory = True
        self.parabolic_viscosity.mandatory = True
    def assign(self, context):
        self.dimension = self.entity.dimension
        self.stiffness.assign(self.entity.stiffness)
        self.parabolic_viscosity.assign(self.entity.parabolic_viscosity)
        self.threshold.assign(self.entity.threshold)
        self.linear_viscosity.assign(self.entity.linear_viscosity)
    def store(self, context):
        self.entity.dimension = self.dimension
        self.entity.stiffness = self.stiffness.store()
        self.entity.parabolic_viscosity = self.parabolic_viscosity.store()
        self.entity.threshold = self.threshold.store()
        self.entity.linear_viscosity = self.linear_viscosity.store() if self.entity.threshold is not None else None
    def draw(self, context):
        self.basis = self.dimension
        layout = self.layout
        self.draw_dimension(layout)
        self.stiffness.draw(layout, "Stiffness")
        self.parabolic_viscosity.draw(layout, "Parabolic viscosity")
        self.threshold.draw(layout, "Threshold")
        if self.threshold.select:
            self.linear_viscosity.draw(layout, "Linear viscosity")
    def check(self, context):
        return ((self.basis != self.dimension) or self.stiffness.check(context) or self.parabolic_viscosity.check(context)
            or self.threshold.check(context) or self.linear_viscosity.check(context))
    def create_entity(self):
        return TurbulentViscoelastic(self.name)

klasses[TurbulentViscoelasticOperator.bl_label] = TurbulentViscoelasticOperator

class LinearViscoelasticBistop(Entity):
    def string(self):
        ret = "linear viscoelastic bistop"
        if self.dimension == "1D":
            ret += ",\n\t\t" + BPY.FORMAT(self.stiffness) + ", " + BPY.FORMAT(self.viscosity)
        else:
            ret += ", " + self.stiffness.string() + ", " + self.viscosity.string()
        ret += ",\n\t\tinitial status, " + self.initial_status
        for drive in [self.activating_condition, self.deactivating_condition]:
            ret += ",\n\t\t" + drive.string()
        return ret

class LinearViscoelasticBistopOperator(Base):
    bl_label = "Linear viscoelastic bistop"
    stiffness = bpy.props.PointerProperty(type = BPY.MatrixFloat)
    viscosity = bpy.props.PointerProperty(type = BPY.MatrixFloat)
    initial_status = bpy.props.EnumProperty(items=[("active", "Active", ""), ("inactive", "Inactive", "")], name="Initial status")
    activating_condition = bpy.props.PointerProperty(type = BPY.Drive)
    deactivating_condition = bpy.props.PointerProperty(type = BPY.Drive)
    def prereqs(self, context):
        self.stiffness.mandatory = True
        self.viscosity.mandatory = True
        self.activating_condition.mandatory = True
        self.deactivating_condition.mandatory = True
    def assign(self, context):
        self.dimension = self.entity.dimension
        self.stiffness.assign(self.entity.stiffness)
        self.viscosity.assign(self.entity.viscosity)
        self.initial_status = self.entity.initial_status
        self.activating_condition.assign(self.entity.activating_condition)
        self.deactivating_condition.assign(self.entity.deactivating_condition)
    def store(self, context):
        self.entity.dimension = self.dimension
        self.entity.stiffness = self.stiffness.store()
        self.entity.viscosity = self.viscosity.store()
        self.entity.initial_status = self.initial_status
        self.entity.activating_condition = self.activating_condition.store()
        self.entity.deactivating_condition = self.deactivating_condition.store()
    def draw(self, context):
        self.basis = self.dimension
        self.stiffness.type = {"1D": "float", "3D": "3x3", "6D": "6x6"}[self.dimension]
        self.viscosity.type = {"1D": "float", "3D": "3x3", "6D": "6x6"}[self.dimension]
        layout = self.layout
        self.draw_dimension(layout)
        self.stiffness.draw(layout, "Stiffness")
        self.viscosity.draw(layout, "Viscosity")
        layout.prop(self, "initial_status")
        self.activating_condition.draw(layout, "Activating condition")
        self.deactivating_condition.draw(layout, "Deactivating condition")
    def check(self, context):
        return ((self.basis != self.dimension) or self.stiffness.check(context) or self.viscosity.check(context)
            or self.activating_condition.check(context) or self.deactivating_condition.check(context))
    def create_entity(self):
        return LinearViscoelasticBistop(self.name)

klasses[LinearViscoelasticBistopOperator.bl_label] = LinearViscoelasticBistopOperator

for dimension in "1D 3D 6D".split():
    class Menu(bpy.types.Menu):
        bl_label = "Constitutive " + dimension
        bl_idname = root_dot + "constitutive" + dimension
        dimension = dimension
        def draw(self, context):
            layout = self.layout
            layout.operator_context = 'INVOKE_DEFAULT'
            for bl_label in constitutive_tree.get_leaves():
                if [d for d in klasses[bl_label].dimension_items if self.dimension in d[0]]:
                    op = layout.operator(root_dot + "c_" + "_".join(bl_label.lower().split()))
                    op.dimension = self.dimension
    BPY.klasses.append(Menu)

bundle = Bundle(constitutive_tree, Base, klasses, database.constitutive)
