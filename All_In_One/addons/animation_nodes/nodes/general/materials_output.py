import bpy
from bpy.props import *
from ... base_types import AnimationNode

class materialsOutputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_materialsOutputNode"
    bl_label = "Materials Output"
    bl_width_default = 180

    def create(self):
        self.newInput("Object", "Object", "obj")
        self.newInput("Integer", "Mat Slot", "slot")
        self.newInput("Float", "Input", "inpt")
        self.newInput("Float", "Trip", "trip")
        self.newInput("Generic", "Material 1", "mat_1")
        self.newInput("Generic", "Material 2", "mat_2")
        self.newOutput("Object", "Object", "obj")

    def execute(self, obj, slot, inpt, trip, mat_1, mat_2):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if not obj:
            return None
        if mat_1:
            if len(obj.material_slots) < 1:
                obj.data.materials.append(mat_1)
            elif not mat_2:
                if len(obj.material_slots) >= (slot + 1):
                    obj.material_slots[slot].material = mat_1
            elif mat_2 and (inpt > trip):
                if len(obj.material_slots) >= (slot + 1):
                    obj.material_slots[slot].material = mat_2
            elif mat_2 and (inpt <= trip):
                if len(obj.material_slots) >= (slot + 1):
                    obj.material_slots[slot].material = mat_1

        return obj
