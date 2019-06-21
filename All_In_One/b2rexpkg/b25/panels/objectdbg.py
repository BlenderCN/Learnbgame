"""
 Panel to show debug information about objects.
"""

import bpy

#from ..properties import B2RexObjectProps

from bpy.props import StringProperty, PointerProperty, IntProperty
from bpy.props import BoolProperty, FloatProperty, CollectionProperty
from bpy.props import FloatVectorProperty

handled_props = [StringProperty, IntProperty, BoolProperty, FloatProperty]

class ObjectDebugPanel(bpy.types.Panel):
    bl_label = "OpenSim Debug" #baseapp.title
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_idname = "b2rex.panel.objectdbg"

    @classmethod
    def poll(cls, context):
        for obj in context.selected_objects:
            if obj.opensim.uuid:
                return True

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        self.draw_debug(context, box)

    def draw_debug(self, context, box):
        for obj in context.selected_objects:
            row = box.row() 
            if obj.opensim.uuid:
                for propname in set(dir(bpy.types.B2RexObjectProps)):
                    aprop = getattr(bpy.types.B2RexObjectProps, propname)
                    if propname.startswith("__"):
                        continue
                        
                    elif aprop.__class__ == tuple and aprop[0] in handled_props:
                        row = box.row()
                        row.prop(obj.opensim, propname)

