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

if "user_defined_common" in locals():
    import imp
    for x in [user_defined_common, common]:
        imp.reload(x)
else:
    from . import user_defined_common
    from .common import Tree
from collections import OrderedDict

def default_klasses(tree, base_klass):
    klasses = dict()
    def find_leaves(tree):
        for key, value in [kv for kv in tree.items()]:
            if isinstance(value, OrderedDict):
                find_leaves(value)
            else:
                class Default(base_klass):
                    bl_label = key
                    @classmethod
                    def poll(cls, context):
                        return False
                    def create_entity(self):
                        return Entity(self.name)
                klasses[key] = Default
    find_leaves(tree)
    return klasses

constitutive = Tree((t, None) for t in [
    "Linear elastic",
    "Linear elastic generic",
    "Linear elastic generic axial torsion coupling",
    "Cubic elastic generic",
    "Inverse square elastic",
    "Log elastic",
    "Linear elastic bistop",
    "Double linear elastic",
    "Isotropic hardening elastic",
    "Scalar function elastic isotropic",
    "Scalar function elastic orthotropic",
    "Linear viscous",
    "Linear viscous generic",
    "Linear viscoelastic",
    "Linear viscoelastic generic",
    "Linear time variant viscoelastic generic",
    "Linear viscoelastic generic axial torsion couple",
    "Cubic viscoelastic generic",
    "Double linear viscoelastic",
    "Turbulent viscoelastic",
    "Linear viscoelastic bistop",
    "Shock absorber",
    "Symbolic elastic",
    "Symbolic viscous",
    "Symbolic viscoelastic",
    "ann elastic",
    "ann viscoelastic",
    "nlsf elastic",
    "nlsf viscous",
    "nlsf viscoelastic",
    "nlp elastic",
    "nlp viscous",
    "nlp viscoelastic",
    ])

constitutive_tree = Tree([("Constitutive", constitutive)])

method = Tree((t, None) for t in [
    "Crank Nicolson",
    "ms",
    "Hope",
    "Third order",
    "bdf",
    "Implicit Euler"])

nonlinear_solver = Tree((t, None) for t in [
    "Newton Raphston",
    "Line search",
    "Matrix free"])

problem = Tree((t, None) for t in [
    "General data",
    "Method",
    "Nonlinear solver",
    "Eigenanalysis",
    "Abort after",
    "Linear solver",
    "Dummy steps",
    "Output data",
    "Real time"])
problem["Method"] = method
problem["Nonlinear solver"] = nonlinear_solver

control = Tree((t, None) for t in [
    "Assembly",
    "Job control",
    "Default output",
    "Default aerodynamic output",
    "Default beam output",
    "Default scale",
    "Rigid body kinematics"])

definition = Tree((t, None) for t in [
    "Problem",
    "Control"])
definition["Problem"] = problem
definition["Control"] = control

definition_tree = Tree([("Definition", definition)])

scalar_drive = Tree((t, None) for t in [
    "Array of scalar drives",
    "Constant drive",
    "Cosine drive",
    "Cubic drive",
    "Direct drive",
    "Dof drive",
    "Double ramp drive",
    "Double step drive",
    "Drive drive",
    "Element drive",
    "Event drive",
    "Exponential drive",
    "File drive",
    "Fourier series drive",
    "Frequency sweep drive",
    "Hints",
    "Linear drive",
    "Meter drive",
    "Mult drive",
    "Node drive",
    "Null drive",
    "Parabolic drive",
    "Piecewise linear drive",
    "Ramp drive",
    "Random drive",
    "Sine drive",
    "Step drive",
    "String drive",
    "Tanh drive",
    "Time drive",
    "Unit drive"])

matrix_3x1_drive = Tree((t, None) for t in [
    "Array of 3D drives",
    "Template 3D drive"])
matrix_6x1_drive = Tree((t, None) for t in [
    "Array of 6D drives",
    "Template 6D drive"])
matrix_3x3_drive = Tree((t, None) for t in [
    "Array of 3x3 drives",
    "Template 3x3 drive"])
matrix_6x6_drive = Tree((t, None) for t in [
    "Array of 6x6 drives",
    "Template 6x6 drive"])

drive = Tree([
    ("Scalar drive", scalar_drive),
    ("3D drive", matrix_3x1_drive),
    ("6D drive", matrix_6x1_drive),
    ("3x3 drive", matrix_3x3_drive),
    ("6x6 drive", matrix_6x6_drive)])

drive_tree = Tree([("Drive", drive)])

file_driver = Tree((t, None) for t in [
    "Fixed step",
    "Variable step",
    "Socket",
    "RTAI input",
    "Stream",
    "Event stream"])

driver = Tree([("File driver", file_driver)])

driver_tree = Tree([("Driver", driver)])

aerodynamic = Tree([
    ("Aerodynamic body", 1),
    ("Aerodynamic beam2", 2),
    ("Aerodynamic beam3", None),
    ("Generic aerodynamic force", None),
    ("Induced velocity", None)])

beam = Tree([
    ("Beam segment", 2),
    ("Three node beam", None)])

force = Tree([
    ("Abstract force", None),
    ("Structural force", 1),
    ("Structural internal force", 2),
    ("Structural couple", 1),
    ("Structural internal couple", 2)])

genel = Tree([
    ("Swashplate", None)])

joint = Tree([
    ("Axial rotation", 2),
    ("Clamp", 1),
    ("Distance", 2),
    ("Deformable displacement joint", 2),
    ("Deformable hinge", 2),
    ("Deformable joint", 2),
    ("In line", 2),
    ("In plane", 2),
    ("Revolute hinge", 2),
    ("Rod", 2),
    ("Spherical hinge", 2),
    ("Total joint", 2),
    ("Viscous body", 1)])

output = Tree([
    ("Stream animation", None),
    ("Stream output", None)])

environment = Tree([
    ("Air properties", None),
    ("Gravity", None)])

node = Tree([
    ("Rigid offset", 2),
    ("Dummy node", 2),
    ("Feedback node", 2)])

element = Tree([
    ("Aerodynamic", aerodynamic),
    ("Beam", beam),
    ("Body", 1),
    ("Force", force),
    ("GENEL", genel),
    ("Joint", joint),
    ("User defined", user_defined_common.tree),
    ("Output", output),
    ("Environment", environment),
    ("Driven", None),
    ("Node", node)])

element_tree = Tree([("Element", element)])

friction = Tree((t, None) for t in [
    "Modlugre", "Discrete Coulomb"])

friction_tree = Tree([("Friction", friction)])

function = Tree((t, None) for t in [
    "Const",
    "Exp",
    "Log",
    "Pow",
    "Linear",
    "Cubic natural spline",
    "Multilinear",
    "Chebychev",
    "Sum",
    "Sub",
    "Mul",
    "Div"])

function_tree = Tree([("Function", function)])

input_card = Tree((t, None) for t in [
    "c81 data",
    "Hydraulic fluid",
    "Include",
    "Module load",
    "Print symbol table",
    "Reference frame",
    "Remark",
    "Set",
    "Setenv"])

input_card_tree = Tree([("Input Card", input_card)])

matrix = Tree((t, None) for t in [
    "3x1",
    "6x1",
    "3x3",
    "6x6",
    "6xN"])

matrix_tree = Tree([("Matrix", matrix)])

shape = Tree((t, None) for t in [
    "Const shape",
    "Piecewise const shape",
    "Linear shape",
    "Piecewise linear shape",
    "Parabolic shape"])

shape_tree = Tree([("Shape", shape)])

simulator = Tree((t, None) for t in [
    "Initial value"])

simulator_tree = Tree([("Simulator", simulator)])


