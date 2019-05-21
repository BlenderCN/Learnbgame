import bpy
from bpy.props import *
from ... base_types import AnimationNode

class materialsInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_materialsInputNode"
    bl_label = "Materials from Project"
    bl_width_default = 180

    search = StringProperty(name = "Search String")
    message1 = StringProperty()

    def draw(self, layout):
        layout.prop(self, "search")
        if (self.message1 != ""):
            layout.label(self.message1, icon = "INFO")

    def create(self):
        self.newOutput("Generic", "First/Single Material","mat")
        self.newOutput("Generic List", "Material(s)", "mats")

    def execute(self):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if self.search != "":
            mats = [item for item in bpy.data.materials if item.name.startswith(self.search)]
        else:
            mats = bpy.data.materials
        self.message1 = str(len(mats)) + " Materials in List"
        if mats:
            mat = mats[0]
        else:
            mat = None
        return mat, mats
