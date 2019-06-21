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
from .menu import default_klasses, matrix_tree

class Base(Operator):
    bl_label = "Matrices"
    bl_options = {'DEFAULT_CLOSED'}
    @classmethod
    def poll(cls, context):
        return True
    @classmethod
    def make_list(self, ListItem):
        bpy.types.Scene.matrix_uilist = bpy.props.CollectionProperty(type = ListItem)
        bpy.types.Scene.matrix_index = bpy.props.IntProperty(default=-1)
    @classmethod
    def delete_list(self):
        del bpy.types.Scene.matrix_uilist
        del bpy.types.Scene.matrix_index
    @classmethod
    def get_uilist(self, context):
        return context.scene.matrix_index, context.scene.matrix_uilist
    def set_index(self, context, value):
        context.scene.matrix_index = value

klasses = default_klasses(matrix_tree, Base)

class MatrixBase(Base):
    N = None
    subtype = None
    ordinals = {}
    floats = bpy.props.CollectionProperty(type = BPY.Float)
    scale = bpy.props.PointerProperty(type = BPY.Float)
    def prereqs(self, context):
        self.floats.clear()
        for i in range(self.N):
            f = self.floats.add()
            f.mandatory = True
    def assign(self, context):
        self.subtype = self.entity.subtype
        for i, f in enumerate(self.entity.floats):
            self.floats[i].assign(f)
        self.scale.assign(self.entity.scale)
    def store(self, context):
        self.entity.subtype = self.subtype
        self.entity.floats = [f.store() if i in self.ordinals[self.subtype] else 0 for i, f in enumerate(self.floats)]
        self.entity.scale = self.scale.store()
    def check(self, context):
        return (self.basis != self.subtype) or self.scale.check(context) or True in [f.check(context) for f in self.floats]

class Matrix3x1(Entity):
    def string(self):
        if self.subtype == "null":
            ret = "\n\t\t\tnull"
        elif self.subtype == "default":
            ret = "\n\t\t\tdefault"
        else:
            ret = "\n\t\t\t" + ", ".join([BPY.FORMAT(prop) for prop in self.floats])
            if self.scale is not None:
                ret += ", scale, " + BPY.FORMAT(self.scale)
        return ret

class Matrix3x1Operator(MatrixBase):
    N = 3
    bl_label = "3x1"
    subtype = bpy.props.EnumProperty(items=[
        ("matr", "General", ""),
        ("null", "Null", ""),
        ("default", "Default", "")],
        name="Subtype")
    ordinals = {
        "matr": [i for i in range(3)],
        "null": [],
        "default": []}
    def draw(self, context):
        self.basis = self.subtype
        layout = self.layout
        layout.prop(self, "subtype")
        if self.subtype not in "null default".split():
            self.scale.draw(layout, "Scale")
            for i in range(self.N):
                self.floats[i].draw(layout, "x" + str(i+1))
    def create_entity(self):
        return Matrix3x1(self.name)


klasses[Matrix3x1Operator.bl_label] = Matrix3x1Operator

class Matrix6x1(Matrix3x1):
    pass

class Matrix6x1Operator(Matrix3x1Operator):
    N = 6
    bl_label = "6x1"
    ordinals = {
        "matr": [i for i in range(6)],
        "null": [],
        "default": []}
    def create_entity(self):
        return Matrix6x1(self.name)

klasses[Matrix6x1Operator.bl_label] = Matrix6x1Operator

class Matrix3x3(Entity):
    def string(self):
        if self.subtype == "matr":
            ret = ("\n\t\t\tmatr,\n" +
            "\t"*4 + ", ".join([BPY.FORMAT(prop) for prop in self.floats[0:3]]) + ",\n" +
            "\t"*4 + ", ".join([BPY.FORMAT(prop) for prop in self.floats[3:6]]) + ",\n" +
            "\t"*4 + ", ".join([BPY.FORMAT(prop) for prop in self.floats[6:9]]))
        elif self.subtype == "sym":
            ret = ("\n\t\t\tsym,\n" +
            "\t"*4 + ", ".join([BPY.FORMAT(prop) for prop in self.floats[0:3]]) + ",\n" +
            "\t"*5 + ", ".join([BPY.FORMAT(prop) for prop in self.floats[4:6]]) + ",\n" +
            "\t"*6 + BPY.FORMAT(self.floats[8]))
        elif self.subtype == "skew":
            ret = "\n\t\t\tskew, " + ", ".join([BPY.FORMAT(self.floats[i]) for i in [7, 2, 3]])
        elif self.subtype == "diag":
            ret = "\n\t\t\tdiag, " + ", ".join([BPY.FORMAT(self.floats[i]) for i in [0, 4, 8]])
        elif self.subtype == "eye":
            ret = "\n\t\t\teye"
        elif self.subtype == "null":
            ret = "\n\t\t\tnull"
        ret += (", scale, " + BPY.FORMAT(self.scale)) if self.scale is not None else ""
        return ret

class Matrix3x3Operator(MatrixBase):
    N = 9
    bl_label = "3x3"
    subtype = bpy.props.EnumProperty(items=[
        ("matr", "General", "General matrix"),
        ("null", "Null", "Null matrix"),
        ("sym", "Symmetric", "Symmetric matrix"),
        ("skew", "Skew symmetric", "Skew symmetric matrix"),
        ("diag", "Diagonal", "Diagonal matrix"),
        ("eye", "Identity", "Identity matrix"),
        ], name="Subtype", default="eye")
    ordinals = {
        "matr": [i for i in range(9)],
        "null": [],
        "sym": [0,1,2,4,5,8],
        "skew": [2,3,7],
        "diag": [0,4,8],
        "eye": []}
    def draw(self, context):
        self.basis = self.subtype
        layout = self.layout
        layout.prop(self, "subtype")
        if self.subtype != "null":
            self.scale.draw(layout, "Scale")
            if self.subtype != "eye":
                for i in range(3):
                    row = layout.row()
                    for j in range(3):
                        k = 3*i+j
                        if k in self.ordinals[self.subtype]:
                            self.floats[k].draw(row, "")
                        else:
                            row.label()
    def create_entity(self):
        return Matrix3x3(self.name)

klasses[Matrix3x3Operator.bl_label] = Matrix3x3Operator

class Matrix6x6(Entity):
    def string(self):
        if self.subtype == "matr":
            ret = ("\n\t\t\tmatr,\n" +
            "\t"*4 + ", ".join([BPY.FORMAT(prop) for prop in self.floats[0:6]]) + ",\n" +
            "\t"*4 + ", ".join([BPY.FORMAT(prop) for prop in self.floats[6:12]]) + ",\n" +
            "\t"*4 + ", ".join([BPY.FORMAT(prop) for prop in self.floats[12:18]]) + ",\n" +
            "\t"*4 + ", ".join([BPY.FORMAT(prop) for prop in self.floats[18:24]]) + ",\n" +
            "\t"*4 + ", ".join([BPY.FORMAT(prop) for prop in self.floats[24:30]]) + ",\n" +
            "\t"*4 + ", ".join([BPY.FORMAT(prop) for prop in self.floats[30:36]]))
        elif self.subtype == "sym":
            ret = ("\n\t\t\tsym,\n" +
            "\t"*4 + ", ".join([BPY.FORMAT(prop) for prop in self.floats[0:6]]) + ",\n" +
            "\t"*5 + ", ".join([BPY.FORMAT(prop) for prop in self.floats[7:12]]) + ",\n" +
            "\t"*6 + ", ".join([BPY.FORMAT(prop) for prop in self.floats[14:18]]) + ",\n" +
            "\t"*7 + ", ".join([BPY.FORMAT(prop) for prop in self.floats[21:24]]) + ",\n" +
            "\t"*8 + ", ".join([BPY.FORMAT(prop) for prop in self.floats[28:30]]) + ",\n" +
            "\t"*9 + BPY.FORMAT(self.floats[35]))
        elif self.subtype == "diag":
            ret = "\n\t\t\tdiag, " + ", ".join([BPY.FORMAT(self.floats[i]) for i in [0,7,14,21,28,35]])
        elif self.subtype == "eye":
            ret = "\n\t\t\teye"
        elif self.subtype == "null":
            ret = "\n\t\t\tnull"
        if self.scale is not None:
            ret += ", scale, " + BPY.FORMAT(self.scale)
        return ret

class Matrix6x6Operator(MatrixBase):
    N = 36
    bl_label = "6x6"
    subtype = bpy.props.EnumProperty(items=[
        ("matr", "General", "General matrix"),
        ("null", "Null", "Null matrix"),
        ("sym", "Symmetric", "Symmetric matrix"),
        ("diag", "Diagonal", "Diagonal matrix"),
        ("eye", "Identity", "Identity matrix"),
        ], name="Subtype", default="eye")
    ordinals = {
        "matr": [i for i in range(36)],
        "null": [],
        "sym": [0,1,2,3,4,5,7,8,9,10,11,14,15,16,17,21,22,23,28,29,35],
        "diag": [0,7,14,21,28,35],
        "eye": []}
    show_column = bpy.props.IntProperty(min=1, max=4, name="Show column", default=1)
    def draw(self, context):
        self.basis = (self.subtype, self.show_column)
        layout = self.layout
        layout.prop(self, "subtype")
        if self.subtype != "null":
            self.scale.draw(layout, "Scale")
            if self.subtype != "eye":
                row = layout.row()
                row.prop(self, "show_column")
                row.label("to column: " + str(self.show_column +2))
                row = layout.row()
                for i in range(3):
                    row.label(str(self.show_column + i))
                for i in range(6):
                    row = layout.row()
                    for j in range(self.show_column - 1, self.show_column + 2):
                        k = 6*i+j
                        if k in self.ordinals[self.subtype]:
                            self.floats[k].draw(row, "")
                        else:
                            row.label()
    def check(self, context):
        return self.basis != (self.subtype, self.show_column) or self.scale.check(context) or True in [f.check(context) for f in self.floats]
    def create_entity(self):
        return Matrix6x6(self.name)

klasses[Matrix6x6Operator.bl_label] = Matrix6x6Operator

class Matrix6xN(Entity):
    ...

class Matrix6xNOperator(MatrixBase):
    N = 30
    bl_label = "6xN"
    @classmethod
    def poll(cls, context):
        return False

klasses[Matrix6xNOperator.bl_label] = Matrix6xNOperator

bundle = Bundle(matrix_tree, Base, klasses, database.matrix)
