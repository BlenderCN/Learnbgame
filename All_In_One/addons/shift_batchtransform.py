#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#  ***** GPL LICENSE BLOCK *****


####------------------------------------------------------------------------------------------------------------------------------------------------------
#### HEADER
####------------------------------------------------------------------------------------------------------------------------------------------------------

bl_info = {
    "name"              : "SHIFT - Batch Transform",
    "author"            : "Andrej Szontagh",
    "version"           : (1,0),
    "blender"           : (2, 5, 9),
    "api"               : 39307,
    "category"          : "Object",
    "location"          : "3D View > Properties",
    "warning"           : '',
    "wiki_url"          : "",
    "tracker_url"       : "",
    "description"       : "Transform selected objects at once"}

import bpy
import time
import math
import random
import operator
import mathutils

from math       import *
from bpy.props  import *

####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS LOCATION
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processLocationX ():

    # shortcut
    props = bpy.context.scene.shift_batchtransform        
    
    # shortcut
    selected = bpy.context.selected_objects

    # use random ?
    if (props.locrandom):

        # use relative ?
        if (props.locrelative):
            
            for i, obj in enumerate (selected):
                r = random.random ()
                obj.location [0] += r * props.locaxisx + (1.0 - r) * props.locmin
        else:
            for i, obj in enumerate (selected):
                r = random.random ()
                obj.location [0]  = r * props.locaxisx + (1.0 - r) * props.locmin
    else:
        
        # use relative ?
        if (props.locrelative):
            
            for i, obj in enumerate (selected):
                obj.location [0] += props.locaxisx
        else:
            for i, obj in enumerate (selected):
                obj.location [0]  = props.locaxisx

def processLocationY ():

    # shortcut
    props = bpy.context.scene.shift_batchtransform        
    
    # shortcut
    selected = bpy.context.selected_objects

    # use random ?
    if (props.locrandom):
        
        # use relative ?
        if (props.locrelative):
            
            for i, obj in enumerate (selected):
                r = random.random ()
                obj.location [1] += r * props.locaxisy + (1.0 - r) * props.locmin
        else:
            for i, obj in enumerate (selected):
                r = random.random ()
                obj.location [1]  = r * props.locaxisy + (1.0 - r) * props.locmin
    else:
        
        # use relative ?
        if (props.locrelative):
            
            for i, obj in enumerate (selected):
                obj.location [1] += props.locaxisy
        else:
            for i, obj in enumerate (selected):
                obj.location [1]  = props.locaxisy

def processLocationZ ():

    # shortcut
    props = bpy.context.scene.shift_batchtransform        
    
    # shortcut
    selected = bpy.context.selected_objects

    # use random ?
    if (props.locrandom):
    
        # use relative ?
        if (props.locrelative):
            
            for i, obj in enumerate (selected):
                r = random.random ()
                obj.location [2] += r * props.locaxisz + (1.0 - r) * props.locmin
        else:
            for i, obj in enumerate (selected):
                r = random.random ()
                obj.location [2]  = r * props.locaxisz + (1.0 - r) * props.locmin
    else:
        
        # use relative ?
        if (props.locrelative):
            
            for i, obj in enumerate (selected):
                obj.location [2] += props.locaxisz
        else:
            for i, obj in enumerate (selected):
                obj.location [2]  = props.locaxisz
        
####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS ROTATION
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processRotationX ():

    # shortcut
    props = bpy.context.scene.shift_batchtransform        
    
    # shortcut
    selected = bpy.context.selected_objects

    # use random ?
    if (props.rotrandom):
        
        # use relative ?
        if (props.rotrelative):
            
            for i, obj in enumerate (selected):
                r = random.random ()
                obj.rotation_euler [0] += r * props.rotaxisx + (1.0 - r) * props.rotmin
        else:
            for i, obj in enumerate (selected):
                r = random.random ()
                obj.rotation_euler [0]  = r * props.rotaxisx + (1.0 - r) * props.rotmin
    else:
        
        # use relative ?
        if (props.rotrelative):
            
            for i, obj in enumerate (selected):
                obj.rotation_euler [0] += props.rotaxisx
        else:
            for i, obj in enumerate (selected):
                obj.rotation_euler [0]  = props.rotaxisx

def processRotationY ():

    # shortcut
    props = bpy.context.scene.shift_batchtransform        
    
    # shortcut
    selected = bpy.context.selected_objects

    # use random ?
    if (props.rotrandom):
        
        # use relative ?
        if (props.rotrelative):
            
            for i, obj in enumerate (selected):
                r = random.random ()
                obj.rotation_euler [1] += r * props.rotaxisy + (1.0 - r) * props.rotmin
        else:
            for i, obj in enumerate (selected):
                r = random.random ()
                obj.rotation_euler [1]  = r * props.rotaxisy + (1.0 - r) * props.rotmin
    else:
        
        # use relative ?
        if (props.rotrelative):
            
            for i, obj in enumerate (selected):
                obj.rotation_euler [1] += props.rotaxisy
        else:
            for i, obj in enumerate (selected):
                obj.rotation_euler [1]  = props.rotaxisy

def processRotationZ ():

    # shortcut
    props = bpy.context.scene.shift_batchtransform        
    
    # shortcut
    selected = bpy.context.selected_objects

    # use random ?
    if (props.rotrandom):
        
        # use relative ?
        if (props.rotrelative):
            
            for i, obj in enumerate (selected):
                r = random.random ()
                obj.rotation_euler [2] += r * props.rotaxisz + (1.0 - r) * props.rotmin
        else:
            for i, obj in enumerate (selected):
                r = random.random ()
                obj.rotation_euler [2]  = r * props.rotaxisz + (1.0 - r) * props.rotmin
    else:

        # use relative ?
        if (props.rotrelative):

            for i, obj in enumerate (selected):
                obj.rotation_euler [2] += props.rotaxisz
        else:
            for i, obj in enumerate (selected):
                obj.rotation_euler [2]  = props.rotaxisz
        
####------------------------------------------------------------------------------------------------------------------------------------------------------
#### PROCESS SCALE
####------------------------------------------------------------------------------------------------------------------------------------------------------

def processScaleX ():

    # shortcut
    props = bpy.context.scene.shift_batchtransform        
    
    # shortcut
    selected = bpy.context.selected_objects

    # use uniform ?
    if (props.scaleuniform):
        
        # use random ?
        if (props.scalerandom):
            
            # use relative ?
            if (props.scalerelative):
                
                for i, obj in enumerate (selected):
                    r = random.random ();   r = r * props.scaleaxisx + (1.0 - r) * props.scalemin
                    obj.scale [0] *= r
                    obj.scale [1] *= r
                    obj.scale [2] *= r
            else:
                for i, obj in enumerate (selected):
                    r = random.random ()
                    obj.scale [0]  = r * props.scaleaxisx + (1.0 - r) * props.scalemin
                    obj.scale [1]  = obj.scale [0]
                    obj.scale [2]  = obj.scale [0]
        else:
            
            # use relative ?
            if (props.scalerelative):
                
                for i, obj in enumerate (selected):
                    obj.scale [0] *= props.scaleaxisx
                    obj.scale [1] *= props.scaleaxisx
                    obj.scale [2] *= props.scaleaxisx
            else:
                for i, obj in enumerate (selected):
                    obj.scale [0]  = props.scaleaxisx
                    obj.scale [1]  = obj.scale [0]
                    obj.scale [2]  = obj.scale [0]
                
    else:
        
        # use random ?
        if (props.scalerandom):

            # use relative ?
            if (props.scalerelative):
            
                for i, obj in enumerate (selected):
                    r = random.random ()
                    obj.scale [0] *= r * props.scaleaxisx + (1.0 - r) * props.scalemin
            else:
                for i, obj in enumerate (selected):
                    r = random.random ()
                    obj.scale [0]  = r * props.scaleaxisx + (1.0 - r) * props.scalemin
                
        else:
            
            # use relative ?
            if (props.scalerelative):
                
                for i, obj in enumerate (selected):
                    obj.scale [0] *= props.scaleaxisx
            else:
                for i, obj in enumerate (selected):
                    obj.scale [0]  = props.scaleaxisx


def processScaleY ():

    # shortcut
    props = bpy.context.scene.shift_batchtransform        
    
    # shortcut
    selected = bpy.context.selected_objects

    # use uniform ?
    if (props.scaleuniform):
    
        # use random ?
        if (props.scalerandom):
            
            # use relative ?
            if (props.scalerelative):
                
                for i, obj in enumerate (selected):
                    r = random.random ();   r = r * props.scaleaxisy + (1.0 - r) * props.scalemin
                    obj.scale [1] *= r
                    obj.scale [0] *= r
                    obj.scale [2] *= r
            else:
                for i, obj in enumerate (selected):
                    r = random.random ()
                    obj.scale [1]  = r * props.scaleaxisy + (1.0 - r) * props.scalemin
                    obj.scale [0]  = obj.scale [1]
                    obj.scale [2]  = obj.scale [1]
        else:

            # use relative ?
            if (props.scalerelative):
            
                for i, obj in enumerate (selected):
                    obj.scale [1] *= props.scaleaxisy
                    obj.scale [0] *= props.scaleaxisy
                    obj.scale [2] *= props.scaleaxisy
            else:
                for i, obj in enumerate (selected):
                    obj.scale [1]  = props.scaleaxisy
                    obj.scale [0]  = obj.scale [1]
                    obj.scale [2]  = obj.scale [1]
    else:
        
        # use random ?
        if (props.scalerandom):
            
            # use relative ?
            if (props.scalerelative):
                
                for i, obj in enumerate (selected):
                    r = random.random ()
                    obj.scale [1] *= r * props.scaleaxisy + (1.0 - r) * props.scalemin
            else:
                for i, obj in enumerate (selected):
                    r = random.random ()
                    obj.scale [1]  = r * props.scaleaxisy + (1.0 - r) * props.scalemin
        else:

            # use relative ?
            if (props.scalerelative):
                
                for i, obj in enumerate (selected):
                    obj.scale [1] *= props.scaleaxisy
            else:
                for i, obj in enumerate (selected):
                    obj.scale [1]  = props.scaleaxisy

def processScaleZ ():

    # shortcut
    props = bpy.context.scene.shift_batchtransform        
    
    # shortcut
    selected = bpy.context.selected_objects

    # use uniform ?
    if (props.scaleuniform):
        
        # use random ?
        if (props.scalerandom):
            
            # use relative ?
            if (props.scalerelative):
                
                for i, obj in enumerate (selected):
                    r = random.random ();   r = r * props.scaleaxisz + (1.0 - r) * props.scalemin
                    obj.scale [2] *= r
                    obj.scale [0] *= r
                    obj.scale [1] *= r
            else:
                for i, obj in enumerate (selected):
                    r = random.random ();
                    obj.scale [2]  = r * props.scaleaxisz + (1.0 - r) * props.scalemin
                    obj.scale [0]  = obj.scale [2]
                    obj.scale [1]  = obj.scale [2]
        else:
            
            # use relative ?
            if (props.scalerelative):
                
                for i, obj in enumerate (selected):
                    obj.scale [2] *= props.scaleaxisz
                    obj.scale [0] *= props.scaleaxisz
                    obj.scale [1] *= props.scaleaxisz
            else:
                for i, obj in enumerate (selected):
                    obj.scale [2]  = props.scaleaxisz
                    obj.scale [0]  = obj.scale [2]
                    obj.scale [1]  = obj.scale [2]
    else:
        
        # use random ?
        if (props.scalerandom):
            
            # use relative ?
            if (props.scalerelative):
                
                for i, obj in enumerate (selected):
                    r = random.random ()
                    obj.scale [2] *= r * props.scaleaxisz + (1.0 - r) * props.scalemin
            else:
                for i, obj in enumerate (selected):
                    r = random.random ()
                    obj.scale [2]  = r * props.scaleaxisz + (1.0 - r) * props.scalemin
        else:
            
            # use relative ?
            if (props.scalerelative):
                
                for i, obj in enumerate (selected):
                    obj.scale [2] *= props.scaleaxisz
            else:
                for i, obj in enumerate (selected):
                    obj.scale [2]  = props.scaleaxisz
        
####------------------------------------------------------------------------------------------------------------------------------------------------------
#### INTEGRATION AND GUI
####------------------------------------------------------------------------------------------------------------------------------------------------------

class SHIFT_BatchTransform_LocationXOp (bpy.types.Operator):

    bl_idname       = "shift.batch_transform_locationx_operator"
    bl_label        = "SHIFT - Batch Transform"
    bl_description  = "Applies location to all selected objects"
    bl_register     = True
    bl_undo         = True
    
    def execute (self, context):

        processLocationX ()

        return {'FINISHED'}

class SHIFT_BatchTransform_LocationYOp (bpy.types.Operator):

    bl_idname       = "shift.batch_transform_locationy_operator"
    bl_label        = "SHIFT - Batch Transform"
    bl_description  = "Applies location to all selected objects"
    bl_register     = True
    bl_undo         = True
    
    def execute (self, context):

        processLocationY ()

        return {'FINISHED'}
    
class SHIFT_BatchTransform_LocationZOp (bpy.types.Operator):

    bl_idname       = "shift.batch_transform_locationz_operator"
    bl_label        = "SHIFT - Batch Transform"
    bl_description  = "Apply location to all selected objects"
    bl_register     = True
    bl_undo         = True
    
    def execute (self, context):

        processLocationZ ()

        return {'FINISHED'}
    
class SHIFT_BatchTransform_RotateXOp (bpy.types.Operator):

    bl_idname       = "shift.batch_transform_rotationx_operator"
    bl_label        = "SHIFT - Batch Transform"
    bl_description  = "Apply rotation to all selected objects"
    bl_register     = True
    bl_undo         = True
    
    def execute (self, context):

        processRotationX ()

        return {'FINISHED'}
    
class SHIFT_BatchTransform_RotateYOp (bpy.types.Operator):

    bl_idname       = "shift.batch_transform_rotationy_operator"
    bl_label        = "SHIFT - Batch Transform"
    bl_description  = "Apply rotation to all selected objects"
    bl_register     = True
    bl_undo         = True
    
    def execute (self, context):

        processRotationY ()

        return {'FINISHED'}
    
class SHIFT_BatchTransform_RotateZOp (bpy.types.Operator):

    bl_idname       = "shift.batch_transform_rotationz_operator"
    bl_label        = "SHIFT - Batch Transform"
    bl_description  = "Apply rotation to all selected objects"
    bl_register     = True
    bl_undo         = True
    
    def execute (self, context):

        processRotationZ ()

        return {'FINISHED'}

class SHIFT_BatchTransform_ScaleXOp (bpy.types.Operator):

    bl_idname       = "shift.batch_transform_scalex_operator"
    bl_label        = "SHIFT - Batch Transform"
    bl_description  = "Apply scale to all selected objects"
    bl_register     = True
    bl_undo         = True
    
    def execute (self, context):

        processScaleX ()

        return {'FINISHED'}

class SHIFT_BatchTransform_ScaleYOp (bpy.types.Operator):

    bl_idname       = "shift.batch_transform_scaley_operator"
    bl_label        = "SHIFT - Batch Transform"
    bl_description  = "Apply scale to all selected objects"
    bl_register     = True
    bl_undo         = True
    
    def execute (self, context):

        processScaleY ()

        return {'FINISHED'}

class SHIFT_BatchTransform_ScaleZOp (bpy.types.Operator):

    bl_idname       = "shift.batch_transform_scalez_operator"
    bl_label        = "SHIFT - Batch Transform"
    bl_description  = "Apply scale to all selected objects"
    bl_register     = True
    bl_undo         = True
    
    def execute (self, context):

        processScaleZ ()

        return {'FINISHED'}

class SHIFT_BatchTransform_panel (bpy.types.Panel):
     
    bl_idname   = "object.batch_transform_panel"
    bl_label    = "SHIFT - Batch Transform"
    bl_context  = "objectmode"
    bl_register = True
    bl_undo     = True

    bl_space_type   = 'VIEW_3D'
    bl_region_type  = 'TOOLS'

    def draw (self, context):

        props = bpy.context.scene.shift_batchtransform
            
        layout = self.layout

        layout.label                ('Transform selected objects at once')

        box = layout.box ()
        box.label                   ('Location')
        _box = box.box ()
        split = _box.split          (percentage = 0.35, align = False)

        split1 = split.split        (percentage = 0.8, align = False)
        col = split1.column         (align = True)
        col.operator                ('shift.batch_transform_locationx_operator', 'Apply')
        col.operator                ('shift.batch_transform_locationy_operator', 'Apply')
        col.operator                ('shift.batch_transform_locationz_operator', 'Apply')
        col = split1.column         (align = True)
        col.label                   ('X :')
        col.label                   ('Y :')
        col.label                   ('Z :')
        
        col = split.column          (align = True)
        col.prop                    (props, 'locaxisx')
        col.prop                    (props, 'locaxisy')
        col.prop                    (props, 'locaxisz')

        _box = _box.box ()
        _box.prop                   (props, 'locrelative')

        _box = box.box ()
        col = _box.column           (align = False)
        split = col.split           (percentage = 0.5, align = False)
        split.prop                  (props, 'locrandom')
        split.prop                  (props, 'locmin')
        
        box = layout.box ()
        box.label                   ('Rotation')
        _box = box.box ()
        split = _box.split          (percentage = 0.35, align = False)

        split1 = split.split        (percentage = 0.8, align = False)
        col = split1.column         (align = True)
        col.operator                ('shift.batch_transform_rotationx_operator', 'Apply')
        col.operator                ('shift.batch_transform_rotationy_operator', 'Apply')
        col.operator                ('shift.batch_transform_rotationz_operator', 'Apply')
        col = split1.column         (align = True)
        col.label                   ('X :')
        col.label                   ('Y :')
        col.label                   ('Z :')
        
        col = split.column          (align = True)
        col.prop                    (props, 'rotaxisx')
        col.prop                    (props, 'rotaxisy')
        col.prop                    (props, 'rotaxisz')

        _box = _box.box ()
        _box.prop                   (props, 'rotrelative')
        
        _box = box.box ()
        col = _box.column           (align = False)
        split = col.split           (percentage = 0.5, align = False)
        split.prop                  (props, 'rotrandom')
        split.prop                  (props, 'rotmin')

        box = layout.box ()
        box.label                   ('Scale')        
        _box = box.box ()
        split = _box.split          (percentage = 0.35, align = False)

        split1 = split.split        (percentage = 0.8, align = False)
        col = split1.column         (align = True)
        col.operator                ('shift.batch_transform_scalex_operator', 'Apply')
        col.operator                ('shift.batch_transform_scaley_operator', 'Apply')
        col.operator                ('shift.batch_transform_scalez_operator', 'Apply')
        col = split1.column         (align = True)
        col.label                   ('X :')
        col.label                   ('Y :')
        col.label                   ('Z :')
        
        col = split.column          (align = True)
        col.prop                    (props, 'scaleaxisx')
        col.prop                    (props, 'scaleaxisy')
        col.prop                    (props, 'scaleaxisz')

        _box = _box.box ()
        split = _box.split          (percentage = 0.5, align = False)
        split.prop                  (props, 'scalerelative')
        split.prop                  (props, 'scaleuniform')

        _box = box.box ()
        col = _box.column           (align = False)
        split = col.split           (percentage = 0.5, align = False)
        split.prop                  (props, 'scalerandom')
        split.prop                  (props, 'scalemin')

class SHIFT_BatchTransform_props (bpy.types.PropertyGroup):
    """
    bpy.context.scene.shift_batchtransform
    """

    # options
    
    # ----------------------------------------------------------
    locaxisx = FloatProperty (
        description = "X axis",
        min         = -10000.0,
        max         =  10000.0,
        precision   = 3,
        step        = 1,
        subtype     = 'DISTANCE',
        default     = 0.0)
    locaxisy = FloatProperty (
        description = "Y axis",
        min         = -10000.0,
        max         =  10000.0,
        precision   = 3,
        step        = 1,
        subtype     = 'DISTANCE',
        default     = 0.0)
    locaxisz = FloatProperty (
        description = "Z axis",
        min         = -10000.0,
        max         =  10000.0,
        precision   = 3,
        step        = 1,
        subtype     = 'DISTANCE',
        default     = 0.0)
    locmin = FloatProperty (
        description = "Minimum value",
        min         = -10000.0,
        max         =  10000.0,
        precision   = 3,
        step        = 1,
        subtype     = 'DISTANCE',
        default     = 0.0)
    locrandom = BoolProperty (
        name        = "random",
        description = "Use random generated values in selected range",
        default     = False)
    locrelative = BoolProperty (
        name        = "relative",
        description = "Use relative transformations",
        default     = False)
         
    # ----------------------------------------------------------
    rotaxisx = FloatProperty (
        description = "X axis",
        min         = - math.pi,
        max         =   math.pi,
        precision   = 1,
        step        = 1,
        subtype     = 'ANGLE',
        default     = 0.0)
    rotaxisy = FloatProperty (
        description = "Y axis",
        min         = - math.pi,
        max         =   math.pi,
        precision   = 1,
        step        = 1,
        subtype     = 'ANGLE',
        default     = 0.0)
    rotaxisz = FloatProperty (
        description = "Z axis",
        min         = - math.pi,
        max         =   math.pi,
        precision   = 1,
        step        = 1,
        subtype     = 'ANGLE',
        default     = 0.0)
    rotmin = FloatProperty (
        description = "Minimum value",
        min         = - math.pi,
        max         =   math.pi,
        precision   = 1,
        step        = 1,
        subtype     = 'ANGLE',
        default     = 0.0)
    rotrandom = BoolProperty (
        name        = "random",
        description = "Use random generated values in selected range",
        default     = False)
    rotrelative = BoolProperty (
        name        = "relative",
        description = "Use relative transformations",
        default     = False)

    # ----------------------------------------------------------
    scaleaxisx = FloatProperty (
        description = "X axis",
        min         = -10.0,
        max         = 10.0,
        precision   = 3,
        step        = 1,
        subtype     = 'NONE',
        default     = 1.0)
    scaleaxisy = FloatProperty (
        description = "Y axis",
        min         = -10.0,
        max         = 10.0,
        precision   = 3,
        step        = 1,
        subtype     = 'NONE',
        default     = 1.0)
    scaleaxisz = FloatProperty (
        description = "Z axis",
        min         = -10.0,
        max         = 10.0,
        precision   = 3,
        step        = 1,
        subtype     = 'NONE',
        default     = 1.0)
    scalemin = FloatProperty (
        description = "Minimum value",
        min         = -10.0,
        max         = 10.0,
        precision   = 3,
        step        = 1,
        subtype     = 'NONE',
        default     = 1.0)
    scalerandom = BoolProperty (
        name        = "random",
        description = "Use random generated values in selected range",
        default     = False)
    scaleuniform = BoolProperty (
        name        = "uniform",
        description = "Use uniform scaleing",
        default     = False)
    scalerelative = BoolProperty (
        name        = "relative",
        description = "Use relative transformations",
        default     = False)
                
def register ():

    bpy.utils.register_module (__name__)

    bpy.types.Scene.shift_batchtransform = bpy.props.PointerProperty (type = SHIFT_BatchTransform_props)    
    
def unregister ():

    bpy.utils.unregister_module (__name__)

    try:    del bpy.types.Scene.shift_batchtransform
    except: pass
             
if __name__ == "__main__":
    
    register ()
