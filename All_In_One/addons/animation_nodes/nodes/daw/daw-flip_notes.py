import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged

class SeqFlipNote(bpy.types.Node, AnimationNode):
    bl_idname = "an_SeqFlipNote"
    bl_label = "SEQ Set Notes"
    bl_width_default = 200

    procN = BoolProperty(name='Edit Notes',default = True)

    def draw(self,layout):
        layout.prop(self,'procN')

    def execute(self):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,1)
        matO = bpy.data.materials['open']   # Open Material
        matP = bpy.data.materials['play']   # Play Material
        # Get list of "Note" obejcts
        obs = [ob for ob in bpy.context.selected_objects if ob.name.startswith('Note')]

        # Flip ths material for selected Note object
        for ob in obs:
            if ob.material_slots[0].material == matO:
                ob.material_slots[0].material = matP
            else:
                ob.material_slots[0].material = matO
            # Deselect Object once processed so it doesn't recurse
            ob.select = False
