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
#
#    You should have received a copy of the GNU General Public License
#    along with BlenderAndMBDyn.  If not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
# -------------------------------------------------------------------------- 

if "bpy" in locals():
    import imp
    for x in [user_defined_element, common, base, menu]:
        imp.reload(x)
else:
    from . import user_defined_element
    from . import common
    from . import base
    from . import menu
from .user_defined_element import klass_list
from .common import (safe_name, Ellipsoid, RhombicPyramid, TriPyramid, Octahedron, Teardrop, Cylinder, Sphere, RectangularCuboid, write_vector, write_orientation)
from .base import bpy, BPY, root_dot, database, Operator, Entity, Bundle, SelectedObjects, SegmentList
from .menu import default_klasses, element_tree
from mathutils import Vector
from copy import copy
import os
import subprocess
from tempfile import TemporaryFile

class Base(Operator):
    bl_label = "Elements"
    exclusive = False
    N_objects = 2
    @classmethod
    def poll(cls, context):
        if cls.N_objects == 0:
            return not cls.exclusive or not database.element.filter(cls.bl_label)
        else:
            obs = SelectedObjects(context)
            return (len(obs) == cls.N_objects - 1
                or (len(obs) == cls.N_objects and not (cls.exclusive and database.element.filter(cls.bl_label, obs[0] if obs else None))))
    def sufficient_objects(self, context):
        objects = SelectedObjects(context)
        if len(objects) == self.N_objects - 1:
            bpy.ops.mesh.primitive_cube_add()
            for obj in objects:
                obj.select = True
            objects.insert(0, context.active_object)
            if 1 < len(objects):
                objects[0].location = objects[1].location
            exec("bpy.ops." + root_dot + "object_specifications('INVOKE_DEFAULT')")
        elif hasattr(self.entity, "objects") and False in [self.entity.objects[i] == ob for i, ob in enumerate(objects)]:
            exec("bpy.ops." + root_dot + "object_specifications('INVOKE_DEFAULT')")
        return objects
    def store(self, context):
        self.entity.objects = self.sufficient_objects(context)
    @classmethod
    def make_list(self, ListItem):
        bpy.types.Scene.element_uilist = bpy.props.CollectionProperty(type = ListItem)
        def select_and_activate(self, context):
            if database.element and self.element_index < len(database.element):
                bpy.ops.object.select_all(action='DESELECT')
                element = database.element[self.element_index]
                if hasattr(element, "objects"):
                    for ob in element.objects:
                        ob.select = True
                    if element.objects and element.objects[0].name in context.scene.objects:
                        context.scene.objects.active = element.objects[0]
                    element.remesh()
        bpy.types.Scene.element_index = bpy.props.IntProperty(default=-1, update=select_and_activate)
    @classmethod
    def delete_list(self):
        del bpy.types.Scene.element_uilist
        del bpy.types.Scene.element_index
    @classmethod
    def get_uilist(self, context):
        return context.scene.element_index, context.scene.element_uilist
    def set_index(self, context, value):
        context.scene.element_index = value
    def draw_panel_post(self, context, layout):
        selected_obs = set(SelectedObjects(context))
        row = layout.row()
        row.operator_context = 'EXEC_DEFAULT'
        if selected_obs:
            used_obs = set()
            for e in database.element + database.drive + database.input_card:
                if hasattr(e, "objects"):
                    used_obs.update(set(e.objects))
            if selected_obs.intersection(used_obs):
                row.menu(root_dot + "selected_objects")
            else:
                row.operator("object.delete")
        row.operator(root_dot + "select_all_filtered")

klasses = default_klasses(element_tree, Base)
for e, o in klass_list:
    class O(o, Base):
        pass
    klasses[O.bl_label] = O

class Constitutive(Base):
    constitutive = bpy.props.PointerProperty(type = BPY.Constitutive)
    def prereqs(self, context):
        self.constitutive.mandatory = True
        self.constitutive.dimension = "3D"
    def assign(self, context):
        self.constitutive.assign(self.entity.constitutive)
    def store(self, context):
        self.entity.constitutive = self.constitutive.store()
        self.entity.objects = self.sufficient_objects(context)
    def draw(self, context):
        self.constitutive.draw(self.layout, text="Constitutive")
    def check(self, context):
        return self.constitutive.check(context)

class Drive(Base):
    drive = bpy.props.PointerProperty(type = BPY.Drive)
    def prereqs(self, context):
        self.drive.mandatory = True
    def assign(self, context):
        self.drive.assign(self.entity.drive)
    def store(self, context):
        self.entity.drive = self.drive.store()
        self.entity.objects = self.sufficient_objects(context)
    def draw(self, context):
        self.drive.draw(self.layout, "Drive")
    def check(self, context):
        return self.drive.check(context)

class Friction(Base):
    friction = bpy.props.PointerProperty(type = BPY.Friction)
    def assign(self, context):
        self.friction.assign(self.entity.friction)
    def store(self, context):
        self.entity.friction = self.friction.store()
        self.entity.objects = self.sufficient_objects(context)
    def draw(self, context):
        self.friction.draw(self.layout, text="Friction")
    def check(self, context):
        return self.friction.check(context)

class StructuralForce(Entity):
    elem_type = "force"
    file_ext = "frc"
    labels = "node Fx Fy Fz X Y Z".split()
    def write(self, f):
        rot_0, globalV_0, Node_0 = self.rigid_offset(0)
        localV_0 = rot_0*globalV_0
        rotT = self.objects[0].matrix_world.to_quaternion().to_matrix()
        f.write("\t" + self.elem_type + ": " + self.safe_name() + ", " + self.force_type +
            ",\n\t\t" + safe_name(Node_0.name) + ", position")
        write_vector(f, localV_0)
        if self.force_type == "follower" and self.orientation:
            f.write(",\n\t\torientation")
            write_orientation(f, rot_0*rotT, "\t\t")
        f.write(",\n\t\t" + self.drive.string() + ";\n")
    def remesh(self):
        if self.force_type == "absolute":
            Octahedron(self.objects[0])
        else:
            TriPyramid(self.objects[0])

class StructuralForceOperator(Drive):
    bl_label = "Structural force"
    N_objects = 1
    force_type = bpy.props.EnumProperty(items=[("follower", "Follower", ""), ("absolute", "Absolute", "")], name="Force type", default="follower")
    orientation = bpy.props.BoolProperty(name="Has orientation patch")
    def prereqs(self, context):
        self.drive.mandatory = True
        self.drive.dimension = "3D"
    def assign(self, context):
        self.force_type = self.entity.force_type
        self.orientation = self.entity.orientation
        super().assign(context)
    def store(self, context):
        self.entity.force_type = self.force_type
        self.entity.orientation = self.orientation
        super().store(context)
    def draw(self, context):
        self.layout.prop(self, "force_type")
        if self.force_type == "follower":
            self.layout.prop(self, "orientation")
        super().draw(context)
    def create_entity(self):
        return StructuralForce(self.name)

klasses[StructuralForceOperator.bl_label] = StructuralForceOperator

class StructuralCouple(StructuralForce):
    elem_type = "couple"
    labels = "node Mx My Mz".split()

class StructuralCoupleOperator(StructuralForceOperator):
    bl_label = "Structural couple"
    def create_entity(self):
        return StructuralCouple(self.name)

klasses[StructuralCoupleOperator.bl_label] = StructuralCoupleOperator

class StructuralInternalForce(Entity):
    elem_type = "force"
    file_ext = "frc"
    labels = "node Fx Fy Fz X Y Z".split()
    def write(self, f):
        rot_0, globalV_0, Node_0 = self.rigid_offset(0)
        localV_0 = rot_0*globalV_0
        rotT = self.objects[0].matrix_world.to_quaternion().to_matrix()
        rot_1, globalV_1, Node_1 = self.rigid_offset(1)
        localV_1 = rot_1*globalV_1
        f.write("\t" + self.elem_type + ": " + self.safe_name() + ", " + self.force_type + " internal" +
            ",\n\t\t" + safe_name(Node_0.name) + ", position")
        write_vector(f, localV_0)
        if self.force_type == "follower" and self.orientation:
            f.write(",\n\t\torientation")
            write_orientation(f, rot_0*rotT, "\t\t")
        f.write(",\n\t\t" + safe_name(Node_1.name) + ", position")
        write_vector(f, localV_1)
        f.write(",\n\t\t" + self.drive.string() + ";\n")
    def remesh(self):
        if self.force_type == "absolute":
            Octahedron(self.objects[0])
        else:
            TriPyramid(self.objects[0])

class StructuralInternalForceOperator(StructuralForceOperator):
    bl_label = "Structural internal force"
    N_objects = 2
    def create_entity(self):
        return StructuralInternalForce(self.name)

klasses[StructuralInternalForceOperator.bl_label] = StructuralInternalForceOperator

class StructuralInternalCouple(StructuralInternalForce):
    elem_type = "couple"
    labels = "node1 M1x M1y M1z node2 M2x M2y M2z".split()

class StructuralInternalCoupleOperator(StructuralInternalForceOperator):
    bl_label = "Structural internal couple"
    def create_entity(self):
        return StructuralInternalCouple(self.name)

klasses[StructuralInternalCoupleOperator.bl_label] = StructuralInternalCoupleOperator

class Joint(Entity):
    elem_type = "joint"
    file_ext = "jnt"
    labels = "Fx Fy Fz Mx My Mz FX FY FZ MX MY MZ".split()

class Hinge(Joint):
    def write_hinge(self, f, name, V1=True, V2=True, M1=True, M2=True):
        rot_0, globalV_0, Node_0 = self.rigid_offset(0)
        localV_0 = rot_0*globalV_0
        rot_1, globalV_1, Node_1 = self.rigid_offset(1)
        to_hinge = rot_1*(globalV_1 + self.objects[0].matrix_world.translation - self.objects[1].matrix_world.translation)
        rotT = self.objects[0].matrix_world.to_quaternion().to_matrix()
        f.write("\tjoint: " + self.safe_name() + ", " + name + ",\n\t\t" + safe_name(Node_0.name))
        if V1:
            write_vector(f, localV_0)
        if M1:
            f.write(",\n\t\t\thinge")
            write_orientation(f, rot_0*rotT, "\t\t\t")
        f.write(", \n\t\t" + safe_name(Node_1.name))
        if V2:
            write_vector(f, to_hinge)
        if M2:
            f.write(",\n\t\t\thinge")
            write_orientation(f, rot_1*rotT, "\t\t\t")

class AxialRotation(Hinge):
    def write(self, f):
        self.write_hinge(f, "axial rotation")
        f.write(",\n\t\treference, " + self.drive.safe_name() + ";\n")
    def remesh(self):
        Cylinder(self.objects[0])

class AxialRotationOperator(Drive):
    bl_label = "Axial rotation"
    def create_entity(self):
        return AxialRotation(self.name)

klasses[AxialRotationOperator.bl_label] = AxialRotationOperator

class Clamp(Joint):
    def write(self, f):
        f.write(
        "\tjoint: " + self.safe_name() + ", clamp,\n" +
        "\t\t" + safe_name(self.objects[0].name) + ", node, node;\n")
    def remesh(self):
        Teardrop(self.objects[0])

class ClampOperator(Base):
    bl_label = "Clamp"
    exclusive = True
    N_objects = 1
    def create_entity(self):
        return Clamp(self.name)

klasses[ClampOperator.bl_label] = ClampOperator

class DeformableDisplacementJoint(Hinge):
    labels = "Fx Fy Fz Mx My Mz FX FY FZ MX MY MZ ex ey ez ex_dot ey_dot ez_dot".split()
    def write(self, f):
        self.write_hinge(f, "deformable displacement joint")
        f.write(",\n\t\treference, " + self.constitutive.safe_name() + ";\n")
    def remesh(self):
        Cylinder(self.objects[0])

class DeformableDisplacementJointOperator(Constitutive):
    bl_label = "Deformable displacement joint"
    def create_entity(self):
        return DeformableDisplacementJoint(self.name)

klasses[DeformableDisplacementJointOperator.bl_label] = DeformableDisplacementJointOperator

class DeformableHinge(Hinge):
    def write(self, f):
        self.write_hinge(f, "deformable hinge", V1=False, V2=False)
        f.write(",\n\t\treference, " + self.constitutive.safe_name() + ";\n")
    def remesh(self):
        Sphere(self.objects[0])

class DeformableHingeOperator(Constitutive):
    bl_label = "Deformable hinge"
    def create_entity(self):
        return DeformableJoint(self.name)

klasses[DeformableHingeOperator.bl_label] = DeformableHingeOperator

class DeformableJoint(Hinge):
    labels = "Fx Fy Fz Mx My Mz FX FY FZ MX MY MZ ex ey ez".split()
    def write(self, f):
        self.write_hinge(f, "deformable joint")
        f.write(",\n\t\treference, " + self.constitutive.safe_name() + ";\n")
    def remesh(self):
        Sphere(self.objects[0])

class DeformableJointOperator(Constitutive):
    bl_label = "Deformable joint"
    def prereqs(self, context):
        self.constitutive.mandatory = True
        self.constitutive.dimension = "6D"
    def create_entity(self):
        return DeformableJoint(self.name)

klasses[DeformableJointOperator.bl_label] = DeformableJointOperator

class Distance(Joint):
    def write(self, f):
        f.write("\tjoint: " + self.safe_name() + ", distance")
        for i in range(2):
            self.write_node(f, i, node=True, position=True, p_label="position")
        if self.drive is None:
            f.write(",\n\t\tfrom nodes;\n")
        else:
            f.write(",\n\t\treference, " + self.drive.safe_name() + ";\n")

class DistanceOperator(Drive):
    bl_label = "Distance"
    exclusive = True
    def prereqs(self, context):
        self.drive.mandatory = False
    def create_entity(self):
        return Distance(self.name)

klasses[DistanceOperator.bl_label] = DistanceOperator

class InLine(Joint):
    def write(self, f):
        rot_1, globalV_1, Node_1 = self.rigid_offset(1)
        localV_1 = rot_1*globalV_1
        f.write("\tjoint: " + self.safe_name() + ", in line")
        self.write_node(f, 0, node=True, position=True, orientation=True)
        f.write(",\n\t\t" + safe_name(Node_1.name) + ",\n\t\t\toffset")
        write_vector(f, localV_1)
        f.write(";\n")
    def remesh(self):
        RhombicPyramid(self.objects[0])

class InLineOperator(Base):
    bl_label = "In line"
    def create_entity(self):
        return InLine(self.name)

klasses[InLineOperator.bl_label] = InLineOperator

class InPlane(Joint):
    def write(self, f):
        rot_0, globalV_0, Node_0 = self.rigid_offset(0)
        localV_0 = rot_0*globalV_0
        rot_1, globalV_1, Node_1 = self.rigid_offset(1)
        localV_1 = rot_1*globalV_1

        rot = self.objects[0].matrix_world.to_quaternion().to_matrix()
        normal = rot*rot_0*Vector((0., 0., 1.))
        f.write(
        "\tjoint: " + self.safe_name() + ", in plane" +
        ",\n\t\t" + safe_name(Node_0.name) + ",\n\t\t\t")
        write_vector(f, localV_0, prepend=False)
        f.write(",\n\t\t\t")
        write_vector(f, normal, prepend=False)
        f.write(",\n\t\t" + safe_name(Node_1.name) + ",\n\t\t\toffset")
        write_vector(f, localV_1)
        f.write(";\n")
    def remesh(self):
        RhombicPyramid(self.objects[0])

class InPlaneOperator(Base):
    bl_label = "In plane"
    def create_entity(self):
        return InPlane(self.name)

klasses[InPlaneOperator.bl_label] = InPlaneOperator

class RevoluteHinge(Hinge):
    labels = "Fx Fy Fz Mx My Mz FX FY FZ MX MY MZ ex ey ez Ax Ay Az Ax_dot Ay_dot Az_dot".split()
    def write(self, f):
        self.write_hinge(f, "revolute hinge")
        if self.theta is not None:
            f.write(",\n\t\tinitial theta, " + BPY.FORMAT(self.theta))
        if self.average_radius is not None:
            f.write(",\n\t\tfriction, " + BPY.FORMAT(self.average_radius))
            if self.preload is not None:
                f.write(",\n\t\t\tpreload, " + BPY.FORMAT(self.preload))
            f.write(",\n\t\t\t" + self.friction.string())
        f.write(";\n")
    def remesh(self):
        Cylinder(self.objects[0])

class RevoluteHingeOperator(Friction):
    bl_label = "Revolute hinge"
    theta = bpy.props.PointerProperty(type = BPY.Float)
    average_radius = bpy.props.PointerProperty(type = BPY.Float)
    preload = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.friction.mandatory = True
    def assign(self, context):
        self.theta.assign(self.entity.theta)
        self.average_radius.assign(self.entity.average_radius)
        self.preload.assign(self.entity.preload)
        super().assign(context)
    def store(self, context):
        self.entity.theta = self.theta.store()
        self.entity.average_radius = self.average_radius.store()
        self.entity.preload = self.preload.store()
        if self.entity.average_radius is None:
            self.friction.mandatory = False
        super().store(context)
    def draw(self, context):
        self.theta.draw(self.layout, text="Theta")
        self.average_radius.draw(self.layout, text="Average radius")
        if self.average_radius.select:
            self.preload.draw(self.layout, text="Preload")
            self.friction.draw(self.layout, text="Friction")
    def check(self, context):
        return self.theta.check(context) or self.average_radius.check(context) or self.preload.check(context) or self.friction.check(context)
    def create_entity(self):
        return RevoluteHinge(self.name)

klasses[RevoluteHingeOperator.bl_label] = RevoluteHingeOperator

class Rod(Joint):
    labels = "Fx Fy Fz Mx My Mz FX FY FZ MX MY MZ l ux uy uz l_dot".split()
    def write(self, f):
        f.write("\tjoint: " + self.safe_name() + ", rod")
        for i in range(2):
            self.write_node(f, i, node=True, position=True, p_label="position")
        if self.length is not None:
            f.write(",\n\t\t" + BPY.FORMAT(self.length))
        else:
            f.write(",\n\t\tfrom nodes")
        f.write(",\n\t\treference, " + self.constitutive.safe_name() + ";\n")

class RodOperator(Constitutive):
    bl_label = "Rod"
    length = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.constitutive.mandatory = True
        self.constitutive.dimension = "1D"
    def assign(self, context):
        self.length.assign(self.entity.length)
        super().assign(context)
    def store(self, context):
        self.entity.length = self.length.store()
        super().store(context)
    def draw(self, context):
        super().draw(context)
        self.length.draw(self.layout, text="Length")
    def check(self, context):
        return self.length.check(context) or super().check(context)
    def create_entity(self):
        return Rod(self.name)

klasses[RodOperator.bl_label] = RodOperator

class SphericalHinge(Hinge):
    def write(self, f):
        self.write_hinge(f, "spherical hinge")
        f.write(";\n")
    def remesh(self):
        Sphere(self.objects[0])

class SphericalHingeOperator(Base):
    bl_label = "Spherical hinge"
    def create_entity(self):
        return SphericalHinge(self.name)

klasses[SphericalHingeOperator.bl_label] = SphericalHingeOperator

class TotalJoint(Joint):
    labels = "Fx Fy Fz Mx My Mz FX FY FZ MX MY MZ dx dy dz dAx dAy dAz u v w dAx_dor dAy_dot dAz_dot".split()
    def write(self, f):
        rot_0, globalV_0, Node_0 = self.rigid_offset(0)
        localV_0 = rot_0*globalV_0
        rot_1, globalV_1, Node_1 = self.rigid_offset(1)
        to_joint = rot_1*(globalV_1 + self.objects[0].matrix_world.translation - self.objects[1].matrix_world.translation)
        rot = self.objects[0].matrix_world.to_quaternion().to_matrix()
        if Node_1 == self.objects[1]:
            rot_position = rot
        else:
            rot_position = self.objects[1].matrix_world.to_quaternion().to_matrix()
        f.write("\tjoint: " + self.safe_name() + ", total joint")
        if self.first == "rotate":
            f.write(",\n\t\t" + safe_name(Node_0.name) + ", position")
            write_vector(f, localV_0)
            f.write(",\n\t\t\tposition orientation")
            write_orientation(f, rot_0*rot_position, "\t\t\t")
            f.write(",\n\t\t\trotation orientation")
            write_orientation(f, rot_0*rot, "\t\t\t")
        f.write(",\n\t\t" + safe_name(Node_1.name) + ", position")
        write_vector(f, to_joint)
        f.write(",\n\t\t\tposition orientation")
        write_orientation(f, rot_1*rot_position, "\t\t\t")
        f.write(",\n\t\t\trotation orientation")
        write_orientation(f, rot_1*rot, "\t\t\t")
        if self.first == "displace":
            f.write(",\n\t\t" + safe_name(Node_0.name) + ", position")
            write_vector(f, localV_0)
            f.write(",\n\t\t\tposition orientation")
            write_orientation(f, rot_0*rot_position, "\t\t\t")
            f.write(",\n\t\t\trotation orientation")
            write_orientation(f, rot_0*rot, "\t\t\t")
        f.write(",\n\t\t\tposition constraint")
        for d in self.drives[:3]: 
            if d:
                f.write(", active")
            else:
                f.write(", inactive")
        f.write(", component")
        for d in self.drives[:3]:
            if d:
                f.write(",\n\t\treference, " + d.safe_name())
            else:
                f.write(",\n\t\t\t\tinactive")
        f.write(",\n\t\t\torientation constraint")
        for d in self.drives[3:6]: 
            if d:
                f.write(", active")
            else:
                f.write(", inactive")
        f.write(", component")
        for d in self.drives[3:6]:
            if d:
                f.write(",\n\t\treference, " + d.safe_name())
            else:
                f.write(",\n\t\t\t\tinactive")
        f.write(";\n")
    def remesh(self):
        Sphere(self.objects[0])

class TotalJointOperator(Base):
    bl_label = "Total joint"
    first = bpy.props.EnumProperty(items=[("displace", "Displacement", ""), ("rotate", "Angular Displacement", "")], default="displace")
    drives = bpy.props.CollectionProperty(type = BPY.Drive)
    def prereqs(self, context):
        for i in range(6):
            self.drives.add()
        self.titles = list()
        for t1 in ["Displacement-", "Angular Displacement-"]:
            for t2 in "XYZ":
                self.titles.append(t1 + t2)
    def assign(self, context):
        self.first = self.entity.first
        for i, d in enumerate(self.entity.drives):
            self.drives[i].assign(d)
    def store(self, context):
        self.entity.first = self.first
        self.entity.drives = [d.store() for d in self.drives]
        self.entity.objects = self.sufficient_objects(context)
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "first", text="Driven first")
        for d, t in zip(self.drives, self.titles):
            d.draw(layout, text = t)
    def check(self, context):
        return True in [d.check(context) for d in self.drives]
    def create_entity(self):
        return TotalJoint(self.name)

klasses[TotalJointOperator.bl_label] = TotalJointOperator

class ViscousBody(Joint):
    def write(self, f):
        f.write(
        "\tjoint: " + self.safe_name() + ", viscous body,\n\t\t" +
        safe_name(self.objects[0].name) +
        ",\n\t\tposition, reference, node, null" +
        ",\n\t\treference, " + self.constitutive.safe_name() + ";\n")
    def remesh(self):
        Sphere(self.objects[0])

class ViscousBodyOperator(Constitutive):
    bl_label = "Viscous body"
    N_objects = 1
    def prereqs(self, context):
        self.constitutive.mandatory = True
        self.constitutive.dimension = "6D"
    def create_entity(self):
        return ViscousBody(self.name)

klasses[ViscousBodyOperator.bl_label] = ViscousBodyOperator

class StreamOutput(Entity):
    elem_type = "stream output"
    def write(self, f):
        f.write("\tstream output: " + self.safe_name() +
            ",\n\t\tstream name, " + BPY.FORMAT(self.stream_name) +
            ",\n\t\tcreate, " + ("yes" if self.create else "no"))
        if self.socket_name is not None:
            f.write(",\n\t\tlocal, ", BPY.FORMAT(self.socket_name))
        else:
            f.write((",\n\t\tport, " + BPY.FORMAT(self.port_number) if self.port_number is not None else "") +
                (",\n\t\thost, " + BPY.FORMAT(self.host_name) if self.host_name is not None else ""))
        f.write(",\n\t\t" + ("" if self.signal else "no ") + "signal"
            + ",\n\t\t" + ("" if self.blocking else "non ") + "blocking"
            + ",\n\t\t" + ("" if self.send_first else "no ") + "send first"
            + ",\n\t\t" + ("" if self.abort_if_broken else "do not ") + "abort if broken")
        f.write(",\n\t\toutput every, " + BPY.FORMAT(self.steps) if self.steps is not None else "")
        if self.file_name is not None:
            f.write(",\n\t\techo, " + BPY.FORMAT(self.file_name) +
                (",\n\t\tprecision, " + BPY.FORMAT(self.precision) if self.precision is not None else "") +
                (",\n\t\tshift, " + BPY.FORMAT(self.shift) if self.shift is not None else ""))
        if self.values_motion == "values":
            f.write(",\n\t\tvalues, " + str(len(self.nodedofs) + len(self.drives)))
            for nodedof in self.nodedofs:
                f.write(",\n\t\t\tnodedof, " + BPY.FORMAT(nodedof))
            for drive in self.drives:
                f.write(",\n\t\t\tdrive, reference, " + drive.safe_name())
        else:
            f.write(",\n\t\tmotion")
            if self.position or self.orientation_matrix or self.orientation_matrix_transpose or self.velocity or self.angular_velocity:
                f.write(", output flags")
                f.write((", position" if self.position else "") +
                    (", orientation matrix" if self.orientation_matrix else "") +
                    (", orientation matrix transpose" if self.orientation_matrix_transpose else "") +
                    (", velocity" if self.velocity else "") +
                    (", angular velocity" if self.angular_velocity else ""))
                if hasattr(self, "objects"):
                    for ob in self.objects:
                        assert ob in database.node, repr(ob) + "is not a node"
                        f.write(",\n\t\t\t" + safe_name(ob.name))
                else:
                    for ob in database.node:
                        f.write(",\n\t\t\t" + safe_name(ob.name))
        f.write(";\n")

class StreamOutputOperator(Base):
    bl_label = "Stream output"
    N_objects = 0
    stream_name = bpy.props.PointerProperty(type = BPY.Str)
    create = bpy.props.BoolProperty(name="Create")
    socket_name = bpy.props.PointerProperty(type = BPY.Str)
    port_number = bpy.props.PointerProperty(type = BPY.Int)
    host_name = bpy.props.PointerProperty(type = BPY.Str)
    signal = bpy.props.BoolProperty(name="Signal")
    blocking = bpy.props.BoolProperty(name="Blocking")
    send_first = bpy.props.BoolProperty(name="Send first")
    abort_if_broken = bpy.props.BoolProperty(name="Abort if broken")
    steps = bpy.props.PointerProperty(type = BPY.Int)
    file_name = bpy.props.PointerProperty(type = BPY.Str)
    precision = bpy.props.PointerProperty(type = BPY.Int)
    shift = bpy.props.PointerProperty(type = BPY.Float)
    values_motion = bpy.props.EnumProperty(items=[("values", "Values", ""), ("motion", "Motion", "")], default="motion")
    N_nodedofs = bpy.props.IntProperty(name="Number of nodedofs", min=0)
    nodedofs = bpy.props.CollectionProperty(type=BPY.Str)
    N_drives = bpy.props.IntProperty(name="Number of drives", min=0)
    drives = bpy.props.CollectionProperty(type=BPY.Drive)
    position = bpy.props.BoolProperty(name="Position", default=True)
    orientation_matrix = bpy.props.BoolProperty(name="Orientation matrix")
    orientation_matrix_transpose = bpy.props.BoolProperty(name="Orientation matrix transpose")
    velocity = bpy.props.BoolProperty(name="Velocity")
    angular_velocity = bpy.props.BoolProperty(name="Angular velocity")
    def prereqs(self, context):
        self.stream_name.mandatory = True
        self.stream_name.value = "MAILBX"
        self.port_number.value = 9011
        self.port_number.select = True
        self.host_name.value = "127.0.0.1"
        self.host_name.select = True
        self.signal = True
        self.blocking = True
        self.send_first = True
        self.abort_if_broken = False
        self.steps.value = 1
        for i in range(20):
            n = self.nodedofs.add()
            n.mandatory = True
            d = self.drives.add()
            d.mandatory = True
    def assign(self, context):
        self.stream_name.assign(self.entity.stream_name)
        self.create = self.entity.create
        self.socket_name.assign(self.entity.socket_name)
        self.port_number.assign(self.entity.port_number)
        self.host_name.assign(self.entity.host_name)
        self.signal = self.entity.signal
        self.blocking = self.entity.blocking
        self.send_first = self.entity.send_first
        self.abort_if_broken = self.entity.abort_if_broken
        self.steps.assign(self.entity.steps)
        self.file_name.assign(self.entity.file_name)
        self.precision.assign(self.entity.precision)
        self.shift.assign(self.entity.shift)
        self.values_motion = self.entity.values_motion
        self.N_nodedofs = self.entity.N_nodedofs
        for i, v in enumerate(self.entity.nodedofs):
            self.nodedofs[i].assign(v)
        self.N_drives = self.entity.N_drives
        for i, d in enumerate(self.entity.drives):
            self.drives[i].assign(d)
        self.position = self.entity.position
        self.orientation_matrix = self.entity.orientation_matrix
        self.orientation_matrix_transpose = self.entity.orientation_matrix_transpose
        self.velocity = self.entity.velocity
        self.angular_velocity = self.entity.angular_velocity
    def store(self, context):
        self.entity.stream_name = self.stream_name.store()
        self.entity.create = self.create
        self.entity.socket_name = self.socket_name.store() if not (self.port_number.select or self.host_name.select) else None
        self.entity.port_number = self.port_number.store() if not self.socket_name.select else None
        self.entity.host_name = self.host_name.store() if not self.socket_name.select else None
        self.entity.signal = self.signal
        self.entity.blocking = self.blocking
        self.entity.send_first = self.send_first
        self.entity.abort_if_broken = self.abort_if_broken
        self.entity.steps = self.steps.store()
        self.entity.file_name = self.file_name.store()
        self.entity.precision = self.precision.store() if self.file_name.select else None
        self.entity.shift = self.shift.store() if self.file_name.select else None
        self.entity.values_motion = self.values_motion
        self.entity.N_nodedofs = self.N_nodedofs if self.values_motion == "values" else 0
        self.entity.nodedofs = [v.store() for v in self.nodedofs][:self.entity.N_nodedofs] if self.values_motion == "values" else list()
        self.entity.N_drives = self.N_drives if self.values_motion == "values" else 0
        self.entity.drives = [d.store() for d in self.drives][:self.entity.N_drives] if self.values_motion == "values" else list()
        self.entity.position = self.position
        self.entity.orientation_matrix = self.orientation_matrix
        self.entity.orientation_matrix_transpose = self.orientation_matrix_transpose
        self.entity.velocity = self.velocity
        self.entity.angular_velocity = self.angular_velocity
        self.entity.objects = self.sufficient_objects(context) if self.values_motion == "motion" else list()
        if not self.entity.objects:
            del self.entity.objects
    def draw(self, context):
        self.basis = (self.values_motion, self.N_nodedofs, self.N_drives)
        layout = self.layout
        self.stream_name.draw(layout, "Stream name")
        layout.prop(self, "create")
        if not (self.port_number.select or self.host_name.select):
            self.socket_name.draw(layout, "Socket name")
        if not self.socket_name.select:
            self.port_number.draw(layout, "Port number")
            self.host_name.draw(layout, "Host name")
        layout.prop(self, "signal")
        layout.prop(self, "blocking")
        layout.prop(self, "send_first")
        layout.prop(self, "abort_if_broken")
        self.steps.draw(layout, "Steps")
        self.file_name.draw(layout, "File name")
        if self.file_name.select:
            self.precision.draw(layout, "Precision")
            self.shift.draw(layout, "Shift")
        layout.prop(self, "values_motion")
        if self.values_motion == "values":
            row = layout.row()
            row.prop(self, "N_nodedofs")
            row.prop(self, "N_drives")
            for i in range(self.N_nodedofs):
                self.nodedofs[i].draw(layout, "Nodedof-" + str(i+1))
            for i in range(self.N_drives):
                self.drives[i].draw(layout, "Drive-" + str(i+1))
        else:
            layout.prop(self, "position")
            layout.prop(self, "orientation_matrix")
            layout.prop(self, "orientation_matrix_transpose")
            layout.prop(self, "velocity")
            layout.prop(self, "angular_velocity")
    def check(self, context):
        return True in [x.check(context) for x in (self.stream_name, self.socket_name, self.port_number, self.host_name, self.steps, self.file_name, self.precision, self.shift)] + [v.check(context) for v in self.nodedofs] + [d.check(context) for d in self.drives] or self.basis != (self.values_motion, self.N_nodedofs, self.N_drives)
    def create_entity(self):
        return StreamOutput(self.name)

klasses[StreamOutputOperator.bl_label] = StreamOutputOperator

class StreamAnimation(StreamOutput):
    pass

class StreamAnimationOperator(StreamOutputOperator):
    bl_label = "Stream animation"
    exclusive = True
    def prereqs(self, context):
        self.abort_if_broken = True
        self.position = True
        self.orientation_matrix = True
        super().prereqs(context)
    def draw(self, context):
        layout = self.layout
        self.stream_name.draw(layout, "Stream name")
        self.port_number.draw(layout, "Port number")
        self.host_name.draw(layout, "Host name")
    def create_entity(self):
        return StreamAnimation(self.name)

klasses[StreamAnimationOperator.bl_label] = StreamAnimationOperator

class Body(Entity):
    elem_type = "body"
    def write(self, f):
        f.write("\tbody: " + self.safe_name())
        self.write_node(f, 0, node=True)
        f.write(",\n\t\t\t" + BPY.FORMAT(self.mass))
        self.write_node(f, 0, position=True)
        if self.inertial_matrix is not None:
            f.write(", " + self.inertial_matrix.string())
            self.write_node(f, 0, orientation=True, o_label="inertial")
        f.write(";\n")
    def remesh(self):
        Ellipsoid(self.objects[0], self.mass, self.inertial_matrix)

class BodyMass(bpy.types.PropertyGroup, BPY.ValueMode):
    value = bpy.props.FloatProperty(min=-9.9e10, max=9.9e10, step=100, precision=6, description="Mass of the body")
BPY.klasses.append(BodyMass)    

class BodyOperator(Base):
    bl_label = "Body"
    N_objects = 1
    mass = bpy.props.PointerProperty(type = BodyMass)
    inertial_matrix = bpy.props.PointerProperty(type = BPY.MatrixFloat)
    def prereqs(self, context):
        self.mass.mandatory = True
        self.mass.assign(1.0)
        self.inertial_matrix.mandatory = True
        self.inertial_matrix.type = "3x3"
    def assign(self, context):
        self.mass.assign(self.entity.mass)
        self.inertial_matrix.assign(self.entity.inertial_matrix)
    def store(self, context):
        self.entity.mass = self.mass.store()
        self.entity.inertial_matrix = self.inertial_matrix.store()
        self.entity.objects = self.sufficient_objects(context)
    def draw(self, context):
        layout = self.layout
        self.mass.draw(layout, "Mass")
        self.inertial_matrix.draw(layout, "Inertial matrix")
    def check(self, context):
        return self.mass.check(context) or self.inertial_matrix.check(context)
    def create_entity(self):
        return Body(self.name)

klasses[BodyOperator.bl_label] = BodyOperator

class RigidOffset(Entity):
    def remesh(self):
        RhombicPyramid(self.objects[0])

class RigidOffsetOperator(Base):
    bl_label = "Rigid offset"
    exclusive = True
    def store(self, context):
        self.entity.objects = self.sufficient_objects(context)
        self.entity.objects[0].parent = self.entity.objects[1]
        self.entity.objects[0].matrix_parent_inverse = self.entity.objects[1].matrix_basis.inverted()
    def create_entity(self):
        return RigidOffset(self.name)

klasses[RigidOffsetOperator.bl_label] = RigidOffsetOperator

class DummyNode(Entity):
    def remesh(self):
        RhombicPyramid(self.objects[0])

class DummyNodeOperator(Base):
    bl_label = "Dummy node"
    exclusive = True
    def create_entity(self):
        return DummyNode(self.name)

klasses[DummyNodeOperator.bl_label] = DummyNodeOperator

class BeamSegment(Entity):
    elem_type = "beam2"
    file_ext = "act"
    labels = "Fx Fy Fz Mx My Mz".split()
    def write(self, f):
        if hasattr(self, "consumer"):
            return
        f.write("\tbeam2: " + self.safe_name())
        for i in range(len(self.objects)):
            self.write_node(f, i, node=True, position=True, orientation=True, p_label="position", o_label="orientation")
        f.write("\t\tfrom nodes, reference, " + self.constitutive.safe_name() + ";\n")
    def remesh(self):
        for obj in self.objects:
            RectangularCuboid(obj)

class BeamSegmentOperator(Constitutive):
    bl_label = "Beam segment"
    def prereqs(self, context):
        self.constitutive.mandatory = True
        self.constitutive.dimension = "6D"
    def create_entity(self):
        return BeamSegment(self.name)

klasses[BeamSegmentOperator.bl_label] = BeamSegmentOperator

class SegmentPair:
    N_objects = 0
    segments = bpy.props.CollectionProperty(type=BPY.Segment)
    in_process = False
    @classmethod
    def begin_process(cls):
        cls.in_process = True
    @classmethod
    def end_process(cls):
        cls.in_process = False
    @classmethod
    def selected_pair(cls, context, segment_type="Beam segment"):
        obs = SelectedObjects(context)
        if len(obs) != 3:
            return list()
        selected_pair = list()
        for ob in obs:
            selected_pair.extend(database.element.filter(segment_type, ob))
        if len(selected_pair) == 2 and not selected_pair[0].objects[1] == selected_pair[1].objects[0]:
            selected_pair.reverse()
        if len(selected_pair) != 2 or not selected_pair[0].objects[1] == selected_pair[1].objects[0]:
            return list()
        for ob in obs:
            if ob not in selected_pair[0].objects + selected_pair[1].objects:
                return list()
        return selected_pair
    @classmethod
    def poll(cls, context):
        if cls.in_process:
            return True
        selected_pair = cls.selected_pair(context, cls.segment_type)
        if not selected_pair:
            return False
        entity = database.element[context.scene.element_index]
        for s in selected_pair:
            if hasattr(s, "consumer") and (not hasattr(entity, "segments") or not s in entity.segments):
                return False
        return True
    def prereqs(self, context):
        self.begin_process()
        self.segments.clear()
        for segment in self.selected_pair(context, self.segment_type):
            s = self.segments.add()
            s.assign(segment)
    def store(self, context):
        if not hasattr(self.entity, "segments"):
            self.entity.segments = SegmentList()
        self.entity.segments.clear()
        for segment in self.segments:
            self.entity.segments.append(segment.store())
        self.entity.objects = self.entity.segments[0].objects + self.entity.segments[1].objects[1:]
        self.end_process()
    def draw(self, context):
        layout = self.layout
        for i, s in enumerate(self.segments):
            row = layout.row()
            row.label("Segment-" + str(i + 1) + ":")
            row.prop(s, "edit", toggle=True, text=s.name)

class ThreeNodeBeam(Entity):
    elem_type = "beam3"
    file_ext = "act"
    labels = "F1x F1y F1z M1x M1y M1z F2x F2y F2z M2x M2y M2z".split()
    def write(self, f):
        f.write("\tbeam3: " + self.safe_name())
        self.objects = self.segments[0].objects + self.segments[1].objects[1:]
        for i in range(3):
            self.write_node(f, i, node=True, position=True, orientation=True, p_label="position", o_label="orientation")
        f.write("\t\tfrom nodes, reference, " + self.segments[0].constitutive.safe_name())
        f.write(",\n\t\tfrom nodes, reference, " + self.segments[1].constitutive.safe_name() + ";\n")
        del self.objects
    def remesh(self):
        for s in self.segments:
            s.remesh()

class ThreeNodeBeamOperator(SegmentPair, Base):
    bl_label = "Three node beam"
    segment_type = "Beam segment"
    def create_entity(self):
        return ThreeNodeBeam(self.name)

klasses[ThreeNodeBeamOperator.bl_label] = ThreeNodeBeamOperator

class Gravity(Entity):
    elem_type = "gravity"
    file_ext = "grv"
    labels = "X_dotdot Y_dotdot Z_dotdot".split()
    def write(self, f):
        f.write("\tgravity: uniform, " + self.drive.string() + ";\n")

class GravityOperator(Drive):
    bl_label = "Gravity"
    @classmethod
    def poll(cls, context):
        return cls.bl_idname.startswith(root_dot+"e_") or not database.element.filter("Gravity")
    def prereqs(self, context):
        super().prereqs(context)
        self.drive.dimension = "3D"
    def store(self, context):
        self.entity.drive = self.drive.store()
    def create_entity(self):
        return Gravity(self.name)

klasses[GravityOperator.bl_label] = GravityOperator

class Driven(Entity):
    elem_type = "driven"
    def write(self, f):
        f.write("\tdriven: " + self.element.safe_name() + ",\n\t\treference, " +
        self.drive.safe_name() + ",\n\t\texisting: " + self.element.elem_type + ", " + self.element.safe_name() + ";\n")

class DrivenOperator(Drive):
    bl_label = "Driven"
    element = bpy.props.PointerProperty(type = BPY.Element)
    @classmethod
    def poll(cls, context):
        return context.scene.element_uilist
    def prereqs(self, context):
        self.element.mandatory = True
        self.element.assign(database.element[context.scene.element_index])
        super().prereqs(context)
    def assign(self, context):
        self.element.assign(self.entity.element)
        super().assign(context)
    def store(self, context):
        self.entity.element = self.element.store()
        self.entity.drive = self.drive.store()
    def draw(self, context):
        layout = self.layout
        self.drive.draw(layout, "Drive")
        self.element.draw(layout, "Element")
    def check(self, context):
        return self.element.check(context) or super().check(context)
    def create_entity(self):
        return Driven(self.name)

klasses[DrivenOperator.bl_label] = DrivenOperator

class Plot:
    bl_options = {'REGISTER', 'INTERNAL'}
    label_names = bpy.props.CollectionProperty(type=BPY.Str)
    def load(self, context, exts, pd):
        self.base = os.path.join(os.path.splitext(context.blend_data.filepath)[0], context.scene.name)
        if 'frequency' not in BPY.plot_data:
            with open(".".join((self.base, "log")), 'r') as f:
                for line in f:
                    if line.startswith("output frequency:"):
                        BPY.plot_data['frequency'] = int(line.split()[-1])
                        break
        if 'out' not in BPY.plot_data:
            BPY.plot_data['out'] = pd.read_table(".".join((self.base, 'out')), sep=" ", skiprows=2, usecols=[i for i in range(2, 9)])
            BPY.plot_data['timeseries'] = BPY.plot_data['out']['Time'][::BPY.plot_data['frequency']]
        for ext in exts:
            if ext not in BPY.plot_data:
                df = pd.read_csv(".".join((self.base, ext)), sep=" ", header=None, skipinitialspace=True, names=[i for i in range(1000)], lineterminator="\n")
                value_counts = df[0].value_counts()
                p = dict()
                for node_label in df[0].unique():
                    p[str(int(node_label))] = df.ix[df[0]==node_label, 1:].dropna(1, 'all')
                    p[str(int(node_label))].index = [i for i in range(value_counts[node_label])]
                BPY.plot_data[ext] = pd.Panel(p)
    def execute(self, context):
        select = [name.select for name in self.label_names]
        if True in select:
            dataframe = self.dataframe.T[select].T.rename(BPY.plot_data['timeseries'])
            dataframe.columns = [name.value for name in self.label_names if name.select]
            plot_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plot.py")
            with TemporaryFile('w') as f:
                f.write(self.entity.name + "\n")
                dataframe.to_csv(f)
                f.seek(0)
                subprocess.Popen(("python3", plot_script), stdin=f)
        elif self.label_names:
            self.report({'ERROR'}, "None selected.")
        return{'FINISHED'}
    def draw(self, context):
        layout = self.layout
        for name in self.label_names:
            row = layout.row()
            row.prop(name, "select", text="")
            row.label(name.value)

class PlotElement(bpy.types.Operator, Plot):
    bl_label = "Plot output"
    bl_description = "Plot the simulated output for the selected element"
    bl_idname = root_dot + "plot_element"
    @classmethod
    def poll(cls, context):
        return context.scene.clean_log and hasattr(database.element[context.scene.element_index], "file_ext")
    def invoke(self, context, event):
        self.entity = database.element[context.scene.element_index]
        import pandas as pd
        self.load(context, [self.entity.file_ext], pd)
        self.label_names.clear()
        key = "1" if self.entity.file_ext == "grv" else str(sorted(database.element, key=lambda x: x.name).index(self.entity))    
        self.dataframe = BPY.plot_data[self.entity.file_ext][key].dropna(1, 'all')
        for i in range(self.dataframe.shape[1]):
            name = self.label_names.add()
            name.value = self.entity.labels[i] if i < len(self.entity.labels) else str(i + 2)
            name.select = False
        return context.window_manager.invoke_props_dialog(self)
BPY.klasses.append(PlotElement)

class PlotNode(bpy.types.Operator, Plot):
    bl_label = "Plot the node"
    bl_description = "Plot the simulated trajectory of a selected node"
    bl_idname = root_dot + "plot_node"
    @classmethod
    def poll(cls, context):
        obs = SelectedObjects(context)
        return context.scene.clean_log and len(obs) == 1 and obs[0] in database.node
    def invoke(self, context, event):
        self.entity = SelectedObjects(context)[0]
        import pandas as pd
        self.load(context, "ine mov".split(), pd)
        node_label = str(database.node.index(SelectedObjects(context)[0]))
        self.dataframe = BPY.plot_data['mov'][node_label].dropna(1, 'all')
        columns = "X Y Z".split() + {
            "orientation matrix": ["R" + str(1 + int(i/3)) + str(1 + int(i%3)) for i in range(9)],
            "orientation vector": "v1 v2 v3".split(),
            "euler123": "e1 e2 e3".split(),
            "euler321": "e3 e2 e1".split(),
            "euler313": "e3 e1 e3".split()}[context.scene.mbdyn_default_orientation]
        self.dataframe.columns = columns + ["u v w omega-1 omega-2 omega-3 u_dot v_dot w_dot omega-1_dot omega-2_dot omega-3_dot".split()[i] for i in range(self.dataframe.shape[1] - len(columns))]
        if node_label in BPY.plot_data['ine']:
            df = BPY.plot_data['ine'][node_label].dropna(1, 'all')
            df.columns = "px py pz Lx Ly Lz dpx/dt dpy/dt dpz/dt dLx/dt dLy/dt dLz/dt".split()
            self.dataframe = self.dataframe.join(df)
        self.label_names.clear()
        for label in self.dataframe.columns:
            name = self.label_names.add()
            name.value = label
            name.select = False
        return context.window_manager.invoke_props_dialog(self)
BPY.klasses.append(PlotNode)

class DuplicateFromObjects(bpy.types.Operator):
    bl_label = "Duplicate"
    bl_description = "Duplicate the selected objects along with some or all of the entities using them"
    bl_idname = root_dot + "duplicate_from_objects"
    bl_options = {'REGISTER', 'INTERNAL'}
    to_scene = bpy.props.PointerProperty(type = BPY.Scene)
    entity_names = bpy.props.CollectionProperty(type=BPY.Str)
    @classmethod
    def poll(cls, context):
        return SelectedObjects(context)
    def invoke(self, context, event):
        self.entity_names.clear()
        self.users = database.entities_originating_from(SelectedObjects(context))
        for user in self.users:
            name = self.entity_names.add()
            name.value = user.name
            name.select = True
        return context.window_manager.invoke_props_dialog(self)
    def execute(self, context):
        entities = [u for u, n in zip(self.users, self.entity_names) if n.select]
        keys = [e for e in entities if e.type != "Reference frame"]
        if self.to_scene.select:
            old_entities = database.all_entities()
            new_entities = dict()
            def duplicate_if_singlet(x, initialize=False):
                if x not in new_entities:
                    database.to_be_duplicated = x
                    exec("bpy.ops." + root_dot + "d_" + "_".join(x.type.lower().split()) + "()")
                    new_entities[x] = database.dup
                    del database.dup
                    if not initialize:
                        keys.append(x)
            while keys:
                key = keys.pop()
                duplicate_if_singlet(key, initialize=True)
                for k, v in vars(key).items():
                    if isinstance(v, Entity):
                        duplicate_if_singlet(v)
                        new_entities[key].__dict__[k] = new_entities[v]
                    elif isinstance(v, list):
                        for i, x in enumerate(v):
                            if isinstance(x, Entity):
                                duplicate_if_singlet(x)
                                new_entities[key].__dict__[k][i] = new_entities[x]
            for frame in [e for e in entities if e.type == "Reference frame"]:
                duplicate_if_singlet(frame, initialize=True)
            new_obs = dict()
            for v in new_entities.values():
                if hasattr(v, "objects"):
                    for i, ob in enumerate(v.objects):
                        if ob not in new_obs:
                            bpy.ops.object.select_all(action='DESELECT')
                            ob.select = True
                            bpy.ops.object.duplicate()
                            new_obs[ob] = context.selected_objects[0]
                        v.objects[i] = new_obs[ob]
            if self.to_scene.name != context.scene.name:
                parent = dict()
                for v in new_obs.values():
                    context.scene.objects.unlink(v)
                for v in new_entities.values():
                    database.to_be_unlinked = v
                    exec("bpy.ops." + root_dot + "u_" + "_".join(v.type.lower().split()) + "()")
                context.screen.scene = bpy.data.scenes[self.to_scene.name]
                database.pickle()
                for e in old_entities:
                    if e in new_entities:
                        new_entities[e].name = e.name
                        database.to_be_linked = new_entities[e]
                        exec("bpy.ops." + root_dot + "l_" + "_".join(new_entities[e].type.lower().split()) + "()")
                for k, v in new_obs.items():
                    context.scene.objects.link(v)
                    v.parent = new_obs[v.parent] if v.parent in new_obs else None
                    v.matrix_parent_inverse = k.matrix_parent_inverse
        else:
            for e in keys:
                exec("bpy.ops." + root_dot + "d_" + "_".join(e.type.lower().split()) + "()")
        del self.users
        context.scene.dirty_simulator = True
        return {'FINISHED'}
    def draw(self, context):
        layout = self.layout
        self.to_scene.draw(layout, "Full copy")
        for name in self.entity_names:
            row = layout.row()
            row.prop(name, "select", text="", toggle=True)
            row.label(name.value)
    def check(self, context):
        return self.to_scene.check(context)
BPY.klasses.append(DuplicateFromObjects)

class Users(bpy.types.Operator):
    bl_label = "Users"
    bl_description = "Users of the selected objects"
    bl_idname = root_dot + "users"
    bl_options = {'REGISTER', 'INTERNAL'}
    entity_names = bpy.props.CollectionProperty(type=BPY.Str)
    @classmethod
    def poll(cls, context):
        return SelectedObjects(context)
    def invoke(self, context, event):
        self.entity_names.clear()
        self.users = database.entities_using(SelectedObjects(context))
        for user in self.users:
            name = self.entity_names.add()
            name.value = user.name
        return context.window_manager.invoke_props_dialog(self)
    def execute(self, context):
        for name, user in zip(self.entity_names, self.users):
            if name.select:
                module = user.__module__.split(".")[-1]
                entity_list = {"element": database.element, "drive": database.drive, "input_card": database.input_card}[module]
                context.scene[module + "_index"] = entity_list.index(user)
                exec("bpy.ops." + root_dot + "e_" + "_".join(user.type.lower().split()) + "('INVOKE_DEFAULT')")
        return {'FINISHED'}
    def draw(self, context):
        layout = self.layout
        for name in self.entity_names:
            row = layout.row()
            row.prop(name, "select", text="", toggle=True)
            row.label(name.value)
    def check(self, context):
        return False
BPY.klasses.append(Users)

class ObjectSpecifications(bpy.types.Operator):
    bl_label = "Object specifications"
    bl_description = "Name, location, and orientation of the selected objects"
    bl_idname = root_dot + "object_specifications"
    bl_options = {'REGISTER', 'INTERNAL'}
    @classmethod
    def poll(cls, context):
        return SelectedObjects(context)
    def invoke(self, context, event):
        self.objects = SelectedObjects(context)
        return context.window_manager.invoke_props_dialog(self)
    def execute(self, context):
        return {'FINISHED'}
    def draw(self, context):
        self.basis = [obj.rotation_mode for obj in self.objects]
        layout = self.layout
        for i, obj in enumerate(self.objects):
            layout.label("")
            layout.prop(obj, "name", text="")
            layout.prop(obj, "location")
            if obj.rotation_mode == 'QUATERNION':
                layout.prop(obj, "rotation_quaternion")
            elif obj.rotation_mode == 'AXIS_ANGLE':
                layout.prop(obj, "rotation_axis_angle")
            else:
                layout.prop(obj, "rotation_euler")
            layout.prop(obj, "rotation_mode")
    def check(self, context):
        return self.basis != [obj.rotation_mode for obj in self.objects]
BPY.klasses.append(ObjectSpecifications)

class SelecteAllFiltered(bpy.types.Operator):
    bl_label = "Select all filtered"
    bl_description = "Select and remesh all filtered element objects"
    bl_idname = root_dot + "select_all_filtered"
    bl_options = {'REGISTER', 'INTERNAL'}
    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        for i, element in enumerate(database.element):
            if database.element.flags[i] and hasattr(element, "objects"):
                element.remesh()
                element.objects[0].select = True
        return {'FINISHED'}
BPY.klasses.append(SelecteAllFiltered)

class Menu(bpy.types.Menu):
    bl_label = "Selected Objects"
    bl_description = "Actions for the selected object(s)"
    bl_idname = root_dot + "selected_objects"
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator(root_dot + "object_specifications")
        layout.operator(root_dot + "users")
        layout.operator(root_dot + "duplicate_from_objects")
        layout.operator(root_dot + "plot_node")
BPY.klasses.append(Menu)

bundle = Bundle(element_tree, Base, klasses, database.element)
