import bpy
from ... base_types import AnimationNode
from bpy.props import *
from mathutils import Vector, Euler, Quaternion
from ... events import propertyChanged

varStore = {}
enum = [("STRING","String","String Variable","",0),
    ("FLOAT","Float","Float Variable","",1),
    ("INTEGER","Integer","Integer Variable","",2),
    ("VECTOR","Vector","Vector Variable","",3),
    ("EULER","Euler","Euler Rotation Variable","",4),
    ("QUATERNION","Quaternion","Quaternion Rotation Variable","",5),
    ("BOOLEAN","Boolean","Boolean Rotation Variable","",6)]

class variableATTRtore(bpy.types.Node, AnimationNode):
    bl_idname = "an_variableATTRStore"
    bl_label = "Variable Store"
    bl_width_default = 200

    mess = StringProperty()
    mode = EnumProperty(name = "Type", items = enum, update = AnimationNode.refresh)

    def draw(self,layout):
        layout.prop(self, "mode")
        layout.prop(self, "booC")
        if self.mess != '':
            layout.label(self.mess,icon = "ERROR")

    def drawAdvanced(self, layout):
        self.invokeFunction(layout, "clearCache", text = "Clear Variables")

    def clearCache(self):
        varStore.clear()

    def create(self):
        if self.mode == "STRING":
            self.newInput("Text", "Input", "varInput")
            self.newOutput("Text", "Output", "varOutput")
        elif self.mode == "INTEGER":
            self.newInput("Integer", "Input", "varInput")
            self.newOutput("Integer", "Output", "varOutput")
        elif self.mode == "FLOAT":
            self.newInput("Float", "Input", "varInput")
            self.newOutput("Float", "Output", "varOutput")
        elif self.mode == "VECTOR":
            self.newInput("Vector", "Input", "varInput")
            self.newOutput("Vector", "Output", "varOutput")
        elif self.mode == "EULER":
            self.newInput("Euler", "Input", "varInput")
            self.newOutput("Euler", "Output", "varOutput")
        elif self.mode == "QUATERNION":
            self.newInput("Quaternion", "Input", "varInput")
            self.newOutput("Quaternion", "Output", "varOutput")
        elif self.mode == "BOOLEAN":
            self.newInput("Boolean", "Input", "varInput")
            self.newOutput("Boolean", "Output", "varOutput")
        self.newInput("Boolean", "Update Variable", "boolInput")

    def execute(self,varInput,boolInput):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)
        if '.' in self.name:
            key = 'VAR'+self.name.split('.')[1]
        else:
            key = 'VAR000'
        self.label = 'Var Key: '+key
        if boolInput:
            varStore[key] = varInput
        if key in varStore:
            return varStore.get(key)
        else:
            # Trap for no value if Trigger Node is used
            if self.mode == "STRING":
                return ''
            elif self.mode == "INTEGER":
                return 0
            elif self.mode == "FLOAT":
                return 0
            elif self.mode == "VECTOR":
                return Vector((0,0,0))
            elif self.mode == "EULER":
                return Euler((0,0,0))
            elif self.mode == "QUATERNION":
                return Quaternion((1,0,0,0))
            elif self.mode == "BOOLEAN":
                return False
