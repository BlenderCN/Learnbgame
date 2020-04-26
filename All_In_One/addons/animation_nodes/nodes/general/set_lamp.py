import bpy
from bpy.props import *
from ... base_types import AnimationNode
from ... events import propertyChanged

class SetLampColStr(bpy.types.Node, AnimationNode):
    bl_idname = "an_SetLampColStr"
    bl_label = "Set Lamp Colour & Strength"
    bl_width_default = 220

    Search = StringProperty(name = "Lamp")
    message1 = StringProperty()

    def draw(self, layout):
        layout.prop(self, "Search")
        if (self.message1 != ""):
            layout.label(self.message1, icon = "INFO")

    def create(self):
        self.newInput("Color","Color","col")
        self.newInput("Float",'Red','red',minValue=0,maxValue=1)
        self.newInput("Float",'Green','green',minValue=0,maxValue=1)
        self.newInput("Float",'Blue','blue',minValue=0,maxValue=1)
        self.newInput("Float","Strength","stren")
        self.newInput("Float","Size","lsize",minValue=0.001,maxValue = 100)
        self.newOutput("Generic List","Lamps","lamps")

    def execute(self,col,red,green,blue,stren,lsize):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if self.Search is None:
            return
        else:
            lamps = [item for item in bpy.data.lamps if item.name.startswith(self.Search)]
            if len(lamps) == 0:
                self.message1 = "No Lamps Match Search"
                return None
            elif len(lamps) > 1:
                self.message1 = "Processing "+str(len(lamps))+" Lamps"
            elif len(lamps) == 1:
                self.message1 = "Processing 1 Lamp"

            for i in lamps:
                i.shadow_soft_size = lsize
                i.node_tree.nodes['Emission'].inputs[1].default_value = stren
                if red > 0 or green > 0 or blue > 0:
                    i.node_tree.nodes['Emission'].inputs[0].default_value = [red,green,blue,1]
                else:
                    i.node_tree.nodes['Emission'].inputs[0].default_value = col
            return lamps
