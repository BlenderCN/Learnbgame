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
    for x in [common, base]:
        imp.reload(x)
else:
    from . import common
    from . import base
from .common import safe_name, Teardrop
from .base import bpy, BPY, root_dot, database, Entity, SelectedObjects
import bmesh, mathutils, math

klass_list = list()

class Sandbox(Entity):
    def write(self, f):
        f.write(
        "\tuser defined: " + self.safe_name() + ", sandbox")
        f.write(";\n")

class Constitutive:
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

class SandboxOperator:
    bl_label = "Sandbox"
    @classmethod
    def poll(cls, context):
        return super().poll(context) and "libmodule-sandbox" in [x.value_type for x in database.input_card.filter("Module load")]
    def create_entity(self):
        return Sandbox(self.name)

klass_list.append((Sandbox, SandboxOperator))

class CollisionWorld(Entity):
    file_ext = "usr"
    labels = "Node1 Node2 f1x f1y f1z f2x f2y f2z Ftx Fty Ftz Fn".split()
    def write(self, f):
        f.write("\tuser defined: " + self.safe_name() + ", collision world,\n\t\tmaterial pairs, " + str(len(self.first)))
        for i, x in enumerate(self.first):
            f.write(",\n\t\t\t" + ", ".join([BPY.FORMAT(x), BPY.FORMAT(self.second[i]), "reference, " + self.constitutive[i].safe_name()]))
            f.write((",\n\t\t\t\tfriction function, \"" + self.function[i].name + "\",\n\t\t\t\tpenetration ratio, " + BPY.FORMAT(self.penetration[i])) if self.function[i] else "")
        f.write(",\n\t\tcollision objects, " + str(len(self.collision_objects)))
        for co in self.collision_objects:
            f.write(",\n\t\t\t" + BPY.FORMAT(co))
        f.write(";\n")

class CollisionWorldOperator:
    bl_label = "Collision world"
    exclusive = True
    N_objects = 0
    first = bpy.props.CollectionProperty(type=BPY.Str)
    second = bpy.props.CollectionProperty(type=BPY.Str)
    constitutive = bpy.props.CollectionProperty(type=BPY.Constitutive)
    penetration = bpy.props.CollectionProperty(type=BPY.Float)
    function = bpy.props.CollectionProperty(type=BPY.Function)
    N_pairs = bpy.props.IntProperty(min=1, max=50, name="Material pairs", default=1)
    @classmethod
    def poll(cls, context):
        ob_set = set([e.objects[0] for e in database.element.filter(["Box", "Capsule", "Cone", "Plane", "Sphere"])])
        return set([o for o in context.selected_objects if o.type == 'MESH']) <= ob_set
    def prereqs(self, context):
        super().prereqs(context)
        for collection in [self.first, self.second, self.penetration]:
            collection.clear()
            for i in range(50):
                c = collection.add()
                c.mandatory = True
        self.constitutive.clear()
        self.function.clear()
        for i in range(50):
            c = self.constitutive.add()
            c.mandatory = True
            c.dimension = "1D"
            self.function.add()
    def assign(self, context):
        super().assign(context)
        self.N_pairs = len(self.entity.first)
        for i, value in enumerate(self.entity.first):
            self.first[i].assign(value)
        for i, value in enumerate(self.entity.second):
            self.second[i].assign(value)
        for i, value in enumerate(self.entity.constitutive):
            self.constitutive[i].assign(value)
        if hasattr(self.entity, "penetration"):
            for i, value in enumerate(self.entity.penetration):
                self.penetration[i].assign(value)
        for i, value in enumerate(self.entity.function):
            self.function[i].assign(value)
    def store(self, context):
        self.entity.first = [x.store() for x in self.first][:self.N_pairs]
        self.entity.second = [x.store() for x in self.second][:self.N_pairs]
        self.entity.constitutive = [x.store() for x in self.constitutive][:self.N_pairs]
        self.entity.penetration = [x.store() for x in self.penetration][:self.N_pairs]
        self.entity.function = [x.store() for x in self.function][:self.N_pairs]
        self.entity.collision_objects = [e for e in database.element.filter(["Box", "Capsule", "Cone", "Plane", "Sphere"])
            if e.objects[0] in [o for o in context.selected_objects if o.type == 'MESH']]
        self.entity.objects = [e.objects[0] for e in self.entity.collision_objects]
        self.entity.labels = list()
        for i in range(4 * int(((len(self.entity.objects) - 1) * len(self.entity.objects)) / 2)):
            for x in CollisionWorld.labels:
                self.entity.labels.append("_".join([x, str(i + 1)]))
    def draw(self, context):
        super().draw(context)
        self.basis = self.N_pairs
        layout = self.layout
        layout.prop(self, "N_pairs")
        for i in range(self.N_pairs):
            layout.label("Pair-" + str(i + 1) + ":")
            self.first[i].draw(layout, "")
            self.second[i].draw(layout, "")
            self.constitutive[i].draw(layout, "")
            self.function[i].draw(layout, "Friction")
            if self.function[i].select:
                self.penetration[i].draw(layout, "Penetration ratio")
    def check(self, context):
        return (self.basis != self.N_pairs) or True in [(True in [x.check(context) for x in X]) for X in [self.first, self.second, self.constitutive, self.penetration, self.function]]
    def create_entity(self):
        return CollisionWorld(self.name)

klass_list.append((CollisionWorld, CollisionWorldOperator))

class CollisionObject(Entity):
    group = "Collision object"
    def write(self, f):
        f.write("\tuser defined: " + self.safe_name() + ", collision object")
        self.write_node(f, 0, node=True, position=True, orientation=True)
        f.write(",\n\t\t" + BPY.FORMAT(self.material))

class Collision:
    material = bpy.props.PointerProperty(type=BPY.Str)
    @classmethod
    def poll(cls, context):
        return super().poll(context) and "libmodule-collision" in [x.value_type for x in database.input_card.filter("Module load")]
    def prereqs(self, context):
        self.material.mandatory = True
        self.material.is_card = True
    def assign(self, context):
        self.material.assign(self.entity.material)
    def store(self, context):
        super().store(context)
        self.entity.objects[0].parent = self.entity.objects[1]
        self.entity.objects[0].matrix_parent_inverse = self.entity.objects[1].matrix_basis.inverted()
        self.entity.material = self.material.store()
        self.entity.objects = self.sufficient_objects(context)
    def draw(self, context):
        self.material.draw(self.layout, "Material", "Set")
    def check(self, context):
        return self.material.check(context)

class Box(CollisionObject):
    def write(self, f):
        super().write(f)
        f.write(", box, " + ", ".join([BPY.FORMAT(x) for x in [self.x, self.y, self.z,]]) + ";\n")
    def remesh(self):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=2.0*self.x)
        for v in bm.verts:
            v.co[1] = math.copysign(self.y, v.co[1])
            v.co[2] = math.copysign(self.z, v.co[2])
        bm.to_mesh(self.objects[0].data)
        bm.free()

class BoxOperator(Collision):
    bl_label = "Box"
    x = bpy.props.FloatProperty(precision=6, min=0.0, default=1.0, name="x")
    y = bpy.props.FloatProperty(precision=6, min=0.0, default=1.0, name="y")
    z = bpy.props.FloatProperty(precision=6, min=0.0, default=1.0, name="z")
    def assign(self, context):
        self.x = self.entity.x
        self.y = self.entity.y
        self.z = self.entity.z
        super().assign(context)
    def store(self, context):
        self.entity.x = self.x
        self.entity.y = self.y
        self.entity.z = self.z
        super().store(context)
    def draw(self, context):
        layout = self.layout
        layout.label("Half extents:")
        layout.prop(self, "x")
        layout.prop(self, "y")
        layout.prop(self, "z")
        super().draw(context)
    def create_entity(self):
        return Box(self.name)

#klass_list.append((Box, BoxOperator))

class Capsule(CollisionObject):
    def write(self, f):
        super().write(f)
        f.write(", capsule, " + ", ".join([BPY.FORMAT(x) for x in [self.radius, self.height]]) + ";\n")
    def remesh(self):
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=32, diameter=self.radius)
        for v in bm.verts:
            if 0.0 < v.co[2]:
                bm.verts.remove(v)
        hold = bm.verts[:] + bm.edges[:] + bm.faces[:]
        loop = list()
        for e in bm.edges:
            if not [v for v in e.verts if v.co[2] < -1e-5*self.radius]:
                loop.append(e)
        geom = bmesh.ops.extrude_edge_only(bm, edges=loop)["geom"]
        verts = [ele for ele in geom if isinstance(ele, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=verts, vec=(0.0, 0.0, self.height))
        geom = bmesh.ops.duplicate(bm, geom=hold)["geom"]
        verts = [ele for ele in geom if isinstance(ele, bmesh.types.BMVert)]
        bmesh.ops.rotate(bm, verts=verts, cent=(0.0, 0.0, 0.0), matrix=mathutils.Matrix.Rotation(math.radians(180.0), 3, 'X'))
        bmesh.ops.translate(bm, verts=verts, vec=(0.0, 0.0, self.height))
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5*self.radius)
        bmesh.ops.translate(bm, verts=bm.verts, vec=(0.0, 0.0, -0.5*self.height))
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0.0, 0.0, 0.0), matrix=mathutils.Matrix.Rotation(math.radians(-90.0), 3, 'X'))
        bm.to_mesh(self.objects[0].data)
        bm.free()

class CapsuleOperator(Collision):
    bl_label = "Capsule"
    radius = bpy.props.FloatProperty(precision=6, min=0.0, default=1.0, name="Radius")
    height = bpy.props.FloatProperty(precision=6, min=0.0, default=1.0, name="Height")
    def assign(self, context):
        self.radius = self.entity.radius
        self.height = self.entity.height
        super().assign(context)
    def store(self, context):
        self.entity.radius = self.radius
        self.entity.height = self.height
        super().store(context)
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "radius")
        layout.prop(self, "height")
        super().draw(context)
    def create_entity(self):
        return Capsule(self.name)

#klass_list.append((Capsule, CapsuleOperator))

class Cone(CollisionObject):
    def write(self, f):
        super().write(f)
        f.write(", cone, " + ", ".join([BPY.FORMAT(x) for x in [self.radius, self.height]]) + ";\n")
    def remesh(self):
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, diameter1=self.radius, diameter2=0, segments=32, depth=self.height)
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        geom = bmesh.ops.duplicate(bm, geom=geom)["geom"]
        verts = [ele for ele in geom if isinstance(ele, bmesh.types.BMVert)]
        bmesh.ops.rotate(bm, verts=verts, cent=(0.0, 0.0, 0.0), matrix=mathutils.Matrix.Rotation(math.radians(180.0), 3, 'X'))
        for v in verts:
            v.co[2] = -0.5*self.height
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5*self.height)
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0.0, 0.0, 0.0), matrix=mathutils.Matrix.Rotation(math.radians(-90.0), 3, 'X'))
        bm.to_mesh(self.objects[0].data)
        bm.free()

class ConeOperator(CapsuleOperator):
    bl_label = "Cone"
    def create_entity(self):
        return Cone(self.name)

#klass_list.append((Cone, ConeOperator))

class Sphere(CollisionObject):
    def write(self, f):
        super().write(f)
        f.write(", sphere, " + BPY.FORMAT(self.radius) +";\n")
    def remesh(self):
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=3, diameter=self.radius)
        bm.to_mesh(self.objects[0].data)
        bm.free()

class SphereOperator(Collision):
    bl_label = "Sphere"
    radius = bpy.props.FloatProperty(precision=6, min=0.0, default=1.0, name="Radius")
    def assign(self, context):
        self.radius = self.entity.radius
        super().assign(context)
    def store(self, context):
        self.entity.radius = self.radius
        super().store(context)
    def draw(self, context):
        self.layout.prop(self, "radius")
        super().draw(context)
    def create_entity(self):
        return Sphere(self.name)

klass_list.append((Sphere, SphereOperator))

class Plane(CollisionObject):
    def write(self, f):
        super().write(f)
        f.write(", plane;\n")
    def remesh(self):
        bm = bmesh.new()
        for v in [(10.,10.,0.),(-10.,10.,0.),(-10.,-10.,0.),(10.,-10.,0.)]:
            bm.verts.new(v)
        if hasattr(bm.verts, "ensure_lookup_table"):
            bm.verts.ensure_lookup_table()
        bm.faces.new(bm.verts)
        bm.to_mesh(self.objects[0].data)
        bm.free()

class PlaneOperator(Collision):
    bl_label = "Plane"
    def create_entity(self):
        return Plane(self.name)

klass_list.append((Plane, PlaneOperator))
