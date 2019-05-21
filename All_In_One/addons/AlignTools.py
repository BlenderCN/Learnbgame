"""
AlignTools
==========

A set of tools to easily align meshes to world axis or local object axis to mesh

Usage
-----

Select exactly one edge, then run the script.

History
-------

This add-on was originally written for my fellow students at "Arts et
Technologies de l'Image" (ATI, Universite Paris 8) when we had to struggle with
a scene made of blocks but where all the rotations had been applied.

Though less advanced, a version exists for Maya as well:
https://gist.github.com/eliemichel/db86f7a3ebd9f871628af4baf4dc2675

License
-------

Copyright (c) 2017-2018 Elie Michel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

bl_info = {
    "name": "AlignTools",
    "author": "Elie Michel",
    "version": (1, 1),
    "blender": (2, 79, 0),
    "location": "View3D > Mesh > AutoAlign",
    "description": "Tools for automatic object alignment",
    "warning": "",
    "wiki_url": "",
    "category": "Mesh",
    }


import bpy
from bpy.props import FloatVectorProperty, EnumProperty
from mathutils import Vector, Matrix
import bmesh

########################## Utility functions ##########################

class ContextError(Exception):
    def __init__(self, message):
        self.message = message

def getEdgePoints(context):
    """Get the  position of the vertices of the selected edge in world space"""
    obj = context.object
    # Get editmode changes
    obj.update_from_editmode()
    mesh = obj.data

    selected_edges = [e for e in mesh.edges if e.select]

    if len(selected_edges) != 1:
        raise ContextError('You must select exactly one edge')

    edge = selected_edges[0]
    p = [mesh.vertices[v].co for v in edge.vertices]
    p = [obj.matrix_world * u for u in p]
    return p

def applyAlignmentMatrix(context, p, mat):
    obj = context.object
    c = (p[0] + p[1]) / 2.0

    # Translation matrices, in order to rotate around the center of the edge instead of the origin point
    t1 = Matrix.Translation(c)
    t2 = Matrix.Translation(-c)

    obj.matrix_world = t1 * mat * t2 * obj.matrix_world

def getMeanFaceNormal(context):
    """Get the normal of the selected face in world space"""
    obj = context.object
    # Get editmode changes
    obj.update_from_editmode()
    mesh = obj.data
    #bm = bmesh.from_edit_mesh(mesh)

    selected_polygons = [poly for poly in mesh.polygons if poly.select]

    if len(selected_polygons) == 0:
        raise ContextError('You must select at least one face')

    n = sum([Vector(poly.normal) for poly in selected_polygons], Vector([0, 0, 0]))
    n.normalize()
    n = obj.matrix_world.to_3x3() * n
    return n

def setAxis(context, mat):
    """Set selected object local axis orientation to match mat"""
    # Prevent origin from changing
    origin = context.object.matrix_world * Vector([0, 0, 0])
    mat = Matrix.Translation(origin) * mat
    
    # Apply the compensating transform to the mesh data
    bpy.ops.object.mode_set(mode='OBJECT')
    obj = context.object
    mesh = obj.data
    mesh.transform(obj.matrix_world)  # reset
    mesh.transform(mat.inverted())  # compensate
    mesh.update()
    # Set new object matrix
    obj.matrix_world = mat
    bpy.ops.object.mode_set(mode='EDIT')

########################## Operators ##########################

## A. Ops that rotate mesh

class AlignEdgeOp(bpy.types.Operator):
    """Base class for operators that rotates the whole mesh to align the
    selected edge one of the world axis."""

    @classmethod
    def poll(cls, context):
        return context.active_object.mode == 'EDIT' and context.object.type == 'MESH'
    

class AlignEdgeToXOperator(AlignEdgeOp, bpy.types.Operator):
    """Align the selected edge to the world X axis of
    the scene by rotating the whole mesh."""
    bl_idname = "transform.align_edge_to_x"
    bl_label = "Align Edge to X Axis"

    def execute(self, context):
        try:
            p = getEdgePoints(context)
        except ContextError as e:
            self.report({'ERROR_INVALID_CONTEXT'}, e.message)
            return {'CANCELLED'}

        # Reconstruct rotation matrix from the target X vector
        z = Vector((0, 0, 1))
        x = (p[1] - p[0]).normalized()
        y = z.cross(x).normalized()
        z = x.cross(y).normalized()
        mat = Matrix((x, y, z)).to_4x4()

        applyAlignmentMatrix(context, p, mat)
        return {'FINISHED'}

class AlignEdgeToYOperator(AlignEdgeOp, bpy.types.Operator):
    """Align the selected edge to the world Y axis of
    the scene by rotating the whole mesh."""
    bl_idname = "transform.align_edge_to_y"
    bl_label = "Align Edge to Y Axis"

    def execute(self, context):
        try:
            p = getEdgePoints(context)
        except ContextError as e:
            self.report({'ERROR_INVALID_CONTEXT'}, e.message)
            return {'CANCELLED'}

        # Reconstruct rotation matrix from the target X vector
        z = Vector((0, 0, 1))
        y = (p[1] - p[0]).normalized()
        x = y.cross(z).normalized()
        z = x.cross(y).normalized()
        mat = Matrix((x, y, z)).to_4x4()
        
        applyAlignmentMatrix(context, p, mat)
        return {'FINISHED'}

class AlignEdgeToZOperator(AlignEdgeOp, bpy.types.Operator):
    """Align the selected edge to the world Z axis of
    the scene by rotating the whole mesh.
    Try to rotate around X as much as possible"""
    bl_idname = "transform.align_edge_to_z"
    bl_label = "Align Edge to Z Axis"

    def execute(self, context):
        try:
            p = getEdgePoints(context)
        except ContextError as e:
            self.report({'ERROR_INVALID_CONTEXT'}, e.message)
            return {'CANCELLED'}

        # Reconstruct rotation matrix from the target X vector
        x = Vector((1, 0, 0))
        z = (p[1] - p[0]).normalized()
        y = z.cross(x).normalized()
        x = y.cross(z).normalized()
        mat = Matrix((x, y, z)).to_4x4()
        
        applyAlignmentMatrix(context, p, mat)
        return {'FINISHED'}

## B. Ops that rotate local object axis

class AlignObjectOp(bpy.types.Operator):
    """Align the current object's local axis to the selected face. If several
    faces are selected, their mean normal is used.
    The X/Y/Z axis will be the normal of the face and other axis are reconstructed
    from it."""

    @classmethod
    def poll(cls, context):
        return context.active_object.mode == 'EDIT' and context.object.type == 'MESH'

class AlignObjectXToFace(AlignObjectOp):
    bl_idname = "transform.align_object_x_to_face"
    bl_label = "Align Object X Axis to Face"

    def execute(self, context):
        try:
            n = getMeanFaceNormal(context)
        except ContextError as e:
            self.report({'ERROR_INVALID_CONTEXT'}, e.message)
            return {'CANCELLED'}

        # Reconstruct rotation matrix
        y = Vector([1, 0, 0])
        x = n.normalized()
        z = x.cross(y).normalized()
        y = z.cross(x).normalized()
        mat = Matrix((x, y, z)).to_4x4().inverted()

        setAxis(context, mat)
        return {'FINISHED'}

class AlignObjectYToFace(AlignObjectOp):
    bl_idname = "transform.align_object_y_to_face"
    bl_label = "Align Object Y Axis to Face"

    def execute(self, context):
        try:
            n = getMeanFaceNormal(context)
        except ContextError as e:
            self.report({'ERROR_INVALID_CONTEXT'}, e.message)
            return {'CANCELLED'}

        # Reconstruct rotation matrix
        z = Vector([1, 0, 0])
        y = n.normalized()
        x = y.cross(z).normalized()
        z = x.cross(y).normalized()
        mat = Matrix((x, y, z)).to_4x4().inverted()

        setAxis(context, mat)
        return {'FINISHED'}

class AlignObjectZToFace(AlignObjectOp):
    bl_idname = "transform.align_object_z_to_face"
    bl_label = "Align Object Z Axis to Face"

    def execute(self, context):
        try:
            n = getMeanFaceNormal(context)
        except ContextError as e:
            self.report({'ERROR_INVALID_CONTEXT'}, e.message)
            return {'CANCELLED'}

        # Reconstruct rotation matrix
        x = Vector([1, 0, 0])
        z = n.normalized()
        y = z.cross(x).normalized()
        x = y.cross(z).normalized()
        mat = Matrix((x, y, z)).to_4x4().inverted()

        setAxis(context, mat)
        return {'FINISHED'}

########################## Panel ##########################

class AutoAlignPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Tools"
    bl_context = "mesh_edit"
    bl_label = "Auto Align"

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("transform.align_edge_to_x")
        col.operator("transform.align_edge_to_y")
        col.operator("transform.align_edge_to_z")
        col.operator("transform.align_object_x_to_face")
        col.operator("transform.align_object_y_to_face")
        col.operator("transform.align_object_z_to_face")

########################## Registering ##########################


def register():
    bpy.utils.register_class(AlignEdgeToXOperator)
    bpy.utils.register_class(AlignEdgeToYOperator)
    bpy.utils.register_class(AlignEdgeToZOperator)
    bpy.utils.register_class(AlignObjectXToFace)
    bpy.utils.register_class(AlignObjectYToFace)
    bpy.utils.register_class(AlignObjectZToFace)
    bpy.utils.register_class(AutoAlignPanel)

def unregister():
    bpy.utils.unregister_class(AlignEdgeToXOperator)
    bpy.utils.unregister_class(AlignEdgeToYOperator)
    bpy.utils.unregister_class(AlignEdgeToZOperator)
    bpy.utils.unregister_class(AlignObjectXToFace)
    bpy.utils.unregister_class(AlignObjectYToFace)
    bpy.utils.unregister_class(AlignObjectZToFace)
    bpy.utils.unregister_class(AutoAlignPanel)

if __name__ == "__main__":
    register()

