# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Copyright (C) 2017 JOSECONSCO
# Created by JOSECONSCO

import bpy
import bmesh
import math
from mathutils import Vector
from bpy.props import EnumProperty, FloatProperty, BoolProperty, IntProperty, StringProperty
from .helper_functions import calc_power
import numpy as np
# import sys
# dir = 'C:\\Users\\JoseConseco\\AppData\\Local\\Programs\\Python\\Python35\\Lib\\site-packages'
# if not dir in sys.path:
#     sys.path.append(dir )
# import ipdb

#DONE: better deformer handling vs old braid (tag it maybe...)
#TODO: if active obj has multi splines then what...
#DONE: curve len automatic calculation.... from surface to splines.... possibly


class HT_OT_BraidMaker(bpy.types.Operator):
    bl_label = "Generate Braids"
    bl_idname = "object.braid_make"
    bl_description = "Generate braid Curves"
    bl_options = {"REGISTER", "UNDO"}

    hairType: bpy.props.EnumProperty(name="Hair Type", default="NURBS",
                                      items=(("NURBS", "Nurbs", ""),
                                             ("POLY", "Poly", "")))
    points_per_cycle: IntProperty(name="Points per cycles", default=4, min=3, max=10)
    braid_length: FloatProperty(name="Braid length", default=1, min=0.1, max=50)
    braid_freq: FloatProperty(name="Braid Frequency", default=1, min=0.2, max=10)
    Radius: FloatProperty(name="Radius", description="Braid Radius", default=0.1, min=0.01, max=2)
    strand_radius: FloatProperty(name="Strand Radius", description="Strand Radius", default=1, min=0.01, max=2)
    FreqFalloff: FloatProperty(name="Falloff", description="Change braid size over strand length", default=-1,
                                   min=-1, max=1, subtype='PERCENTAGE')

    def generate_braid_points(self, braid_index=1):
        braid_xy_offset = 0.0
        if braid_index == 2:
            braid_xy_offset = -4/3*np.pi
        elif braid_index == 3:
            braid_xy_offset = 4/3*np.pi
        cpow = calc_power(self.FreqFalloff)
        min_dist =2*np.pi / (self.points_per_cycle * self.braid_freq*10) 
        z =  np.arange( 0, self.braid_length , min_dist)
        length = z.size
        freq_multiplier = np.array( [math.pow((i+1) / length, cpow) for i in range(length)])
        arg_z = z * self.braid_freq*10 + braid_xy_offset
        x = 0.5*self.Radius * freq_multiplier * np.sin(arg_z)
        y = self.Radius * freq_multiplier * np.cos(0.5 *arg_z )
        z = z * freq_multiplier - z[-1]  #reduce size and radius
        return np.array([x,y,z]).T  #so we have point1(x,y,z), point2 ...

    def create_new_curve(self, context):
        curveData = bpy.data.curves.new('BraidPolyline', type='CURVE')
        curveData.dimensions = '3D'
        curveData.bevel_resolution = 2
        Curve = bpy.data.objects.new('Braid', curveData)
        context.scene.collection.objects.link(Curve)
        context.view_layer.objects.active = Curve
        Curve.select_set(True)
        # Curve.data.show_normal_face = False
        bpy.context.scene.update()
        return Curve

    @staticmethod
    def get_curve_len(curve):
        backup_bevel_obj = curve.data.bevel_object
        curve.data.bevel_object = None
        backup_bevel_depth = curve.data.bevel_depth
        curve.data.bevel_depth = 0
        me_from_curve = curve.to_mesh(bpy.context.depsgraph, apply_modifiers=False, calc_undeformed=False)
        total_len=0
        bm = bmesh.new()
        bm.from_mesh(me_from_curve)
        for edge in bm.edges:
            total_len+=edge.calc_length()
        curve.data.bevel_object = backup_bevel_obj
        curve.data.bevel_depth = backup_bevel_depth
        return total_len

    def invoke(self, context, event):
        if context.active_object and  context.active_object.type == 'CURVE' and context.active_object.is_braid == False: #assume it is deformer for braid
            self.braid_length = self.get_curve_len(context.active_object)
            self.Radius = self.braid_length/20
            self.braid_freq = 1/(2*np.pi*self.braid_length*self.Radius  )
        return self.execute(context)

    def execute(self, context):
        deform_curve = None
        Curve = None
        if context.active_object and  context.active_object.type == 'CURVE': #if no selection, or selection is not curve
            if context.active_object.is_braid:
                Curve = context.active_object
            else:
                deform_curve = context.active_object
                
        if Curve is None:
            Curve = self.create_new_curve(context)
            Curve.is_braid = True

        # Curve.data.show_normal_face = False
        Curve.data.fill_mode = 'FULL'
        Curve.data.use_uv_as_generated = True
        Curve.data.use_auto_texspace = True
        Curve.data.bevel_depth = self.strand_radius * self.Radius
        Curve.data.splines.clear()

        if deform_curve is not None:
            mod = Curve.modifiers.new("BraidDeform", 'CURVE')
            mod.deform_axis = 'NEG_Z'
            mod.object = deform_curve
            Curve.matrix_world = deform_curve.matrix_world
            # constraint = Curve.constraints.new(type='CHILD_OF')
            # constraint.target = deform_curve
            # constraint.inverse_matrix = deform_curve.matrix_world.inverted()

        cpow = calc_power(self.FreqFalloff)
        for braid_i in range(3):
            braid_points = self.generate_braid_points( braid_index=braid_i+1)
            curve_length = braid_points.shape[0]
            # freq_multiplier = np.array( [math.pow((i+1) / curve_length, cpow) for i in range(curve_length)])
            freq_multiplier =  np.array( [1-math.pow((i+1) / curve_length, cpow) for i in range(curve_length)])
            polyline = Curve.data.splines.new(self.hairType)
            polyline.points.add(curve_length - 1)
            if self.hairType == 'NURBS':
                polyline.order_u = 3  # like bezier thing
                polyline.use_endpoint_u = True
            for i,point in enumerate(braid_points):  # for strand point
                polyline.points[i].co = (point[0], point[1], point[2], 1)
                polyline.points[i].radius = 1-freq_multiplier[i]
        Curve.data.resolution_u = 3
        bpy.ops.object.curve_uv_refresh()
        mode = Curve.mode
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.curve.select_all(action='SELECT')
        bpy.ops.curve.switch_direction()
        bpy.ops.object.mode_set(mode=mode)
        return {"FINISHED"}

    


