'''
Make Cross Section
Copyright (C) 2011  Patrick R, Joar Wandborg

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Make Cross Section",
    "author": "Joar Wandborg, HEAVILY based on Patrick R's \
cross_section_matrix_apply.py from http://goo.gl/xqJ3x",
    "version": (1, 0),
    "blender": (2, 5, 8),
    "api": 31965,
    "location": "Object Properties",
    "description": "Makes a Cross Section",
    "warning": "",
    "wiki_url": "https://github.com/jwandborg/blender-make_cross_section",
    "tracker_url": "https://github.com/jwandborg/blender-make_cross_section/issues",
    "category": "Learnbgame",
}

import bpy
import math
from math import *
from mathutils import *
from mathutils import Vector
from mathutils import Matrix
import time


def section(cut_me, mx, pp, pno, FILL=False):
    '''
    Finds the section between a mesh and a plane mesh
    cut_me: Blender Mesh - the mesh to be cut
    mx: world matrix of mesh
    pp: Vector - a point on the plane
    pno: Vector - The cutting plane normal
    together, pp and pno define the cutting plane
    FILL:  Boolean - check if you want to fill mesh

    Returns: Mesh - the resulting mesh of the cut
    '''

    verts = []
    faces = []
    ed_xsect = {}  # why is this a dictionary? I don't know

    for ed in cut_me.edges:
        # get a vector from each edge to a point on the plane

        v1 = cut_me.vertices[ed.key[0]].co * mx
        co1 = v1 - pp

        v2 = cut_me.vertices[ed.key[1]].co * mx
        co2 = v2 - pp

        # project them onto normal
        proj1 = co1.project(pno).length
        proj2 = co2.project(pno).length

        if (proj1 != 0):
            angle1 = co1.angle(pno)
        else:
            angle1 = 0

        if (proj2 != 0):
            angle2 = co2.angle(pno)
        else:
            angle2 = 0

        # Check to see if edge intersects. Also check if coplanar cutting plane
        if ((proj1 == 0) or (proj2 == 0) or \
            (angle1 > pi / 2) != (angle2 > pi / 2)) and \
                (proj1 + proj2 > 0):

            # edge intersects

            proj1 /= proj1 + proj2
            co = ((v2 - v1) * proj1) + v1
            verts.append(co)

            # store a mapping between the new vertices and the mesh's edges
            ed_xsect[ed.key] = len(ed_xsect)

    edges = []
    for f in cut_me.faces:
        # get the edges that the intersection points form
        ps = [ed_xsect[key] for key in f.edge_keys if key in ed_xsect]
        if len(ps) == 2:
            edges.append(tuple(ps))

    x_me = bpy.data.meshes.new("cross section")
    x_me.from_pydata(verts, edges, faces)

    return x_me


def main():
    dont_delete = list(bpy.data.objects)

    bpy.ops.object.duplicate()
    duplicates = list(bpy.context.selected_objects)

    bpy.context.scene.objects.active = duplicates[len(duplicates) - 1]

    sce = bpy.context.scene

    ob_act = bpy.context.object  # the cutting plane

    print("the active object is" + ob_act.name)

    # bpy.context.scene.objects.active = bpy.context.selected_objects[0]
    # print("now the active object is" + bpy.context.object.name)

    if len(bpy.context.selected_objects) >= 2:
        to_cut = []
        for object in bpy.context.selected_objects:
            if object != duplicates[len(duplicates) - 1]:
                to_cut.append(object)

    print("going ot cut" + str(list(to_cut)))

    bpy.ops.object.select_all(action='DESELECT')
    ob_act.select = True

    bpy.ops.object.transform_apply()
    '''
    Substituted by transform_apply
    bpy.ops.object.location_apply()
    bpy.ops.object.rotation_apply()
    bpy.ops.object.scale_apply()
    '''

    pp = ob_act.data.vertices[0].co
    pno = ob_act.data.faces[0].normal
    bpy.ops.object.select_all(action='DESELECT')

    for o in to_cut:
        o.select = True

        bpy.ops.object.transform_apply()
        '''
        Substituted by transform_apply
        bpy.ops.object.location_apply()
        bpy.ops.object.rotation_apply()
        bpy.ops.object.scale_apply()
        '''

        cut_me = o.data
        mx = o.matrix_world
        x_me = section(cut_me, mx, pp, pno, FILL=False)

        new_ob = bpy.data.objects.new("cross section", x_me)
        sce.objects.link(new_ob)
        dont_delete.append(new_ob)

    bpy.ops.object.select_all(action='SELECT')
    for object in dont_delete:
        object.select = False
    bpy.ops.object.delete()


class MakeCrossSection(bpy.types.Operator):
    '''
    MakeCrossSection Operator class
    '''
    bl_idname = "object.make_cross_section"
    bl_label = "Make Cross Section"

    @classmethod
    def poll(cls, context):
        return context.active_object != None

    def execute(self, context):
        main()
        #Debuging print outs
        return {'FINISHED'}


class OBJECT_PT_cross(bpy.types.Panel):
    bl_label = "Make Cross Section"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        scene = context.scene
        layout = self.layout
        split = layout.split()

        col = split.column()
        col.operator("object.make_cross_section", text="Make Cross Section")

        obj = context.object
        print(obj)

        '''
        Find the other selected objects which are not the active object
        (returns a list)
        '''
        if len(bpy.context.selected_objects) >= 2:
            for object in bpy.context.selected_objects:
                if object != bpy.context.object:
                    obj2 = object
                    print(object)

            row = layout.row()
            row.label(text="Cutting Plane is: " + obj.name)

            row = layout.row()
            row.label(text="To be cut is: " + obj2.name)


def register():
    bpy.utils.register_class(OBJECT_PT_cross)
    bpy.utils.register_class(MakeCrossSection)
    print(__name__ + ' is registered')

def unregister():
    bpy.utils.unregister_class(OBJECT_PT_cross)
    bpy.utils.unregister_class(MakeCrossSection)
    print(__name__ + ' is unregistered')
