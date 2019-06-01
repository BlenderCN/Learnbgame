import bpy
from bpy.props import FloatProperty
from bpy.types import Operator
import os

#define functions

def setDim(index):

    ob = bpy.context.object

    dimensions = ob.dimensions

    # if user doesn't change dimension value, it will not be set and cause an error
    try:
        newDim = bpy.context.scene['dimension']
    except:
        newDim = 2

    oldDim = dimensions[index]

    scalar = newDim / oldDim

    scale = ob.scale

    scale *= scalar



#create variable containing dimension measurement
bpy.types.Scene.dimension = FloatProperty( name = "dimension", default = 2.0, subtype = 'DISTANCE', unit = 'LENGTH', description = "New dimension measurement" )


class xDim(bpy.types.Operator):
    bl_idname = "object.set_x_dimension"
    bl_label = "Set X Dimension"
    bl_options = {"UNDO"}

    def invoke(self, context, event):
        setDim(0) # call function
        return {"FINISHED"} # done

class yDim(bpy.types.Operator):
    bl_idname = "object.set_y_dimension"
    bl_label = "Set Y Dimension"
    bl_options = {"UNDO"}

    def invoke(self, context, event):
        setDim(1) # call function
        return {"FINISHED"} # done

class zDim(bpy.types.Operator):
    bl_idname = "object.set_z_dimension"
    bl_label = "Set Z Dimension"
    bl_options = {"UNDO"}

    def invoke(self, context, event):
        setDim(2) # call function
        return {"FINISHED"} # done


class propDim(bpy.types.Panel):
    """Set Dimension, Lock Proportions"""
    bl_label = "Set Dimension, Lock Proportions"
    bl_category = "Custom Tools"
    bl_context = "objectmode"
    bl_region_type = 'TOOLS'
    bl_space_type = 'VIEW_3D'

    def draw(self, context):
        layout = self.layout

        ob = context.object

        row = layout.row()
        row.label(text="Set dimension in one axis. Other axes will scale proportionally.")

        row = layout.row()
        row.column().prop(context.scene, "dimension")

        row = layout.row(align=True)
        row.column().operator("object.set_x_dimension", text="Set X")
        row.column().operator("object.set_y_dimension", text="Set Y")
        row.column().operator("object.set_z_dimension", text="Set Z")
