import bpy
from ... base_types import AnimationNode
from bpy.props import *
from ... events import propertyChanged

class PlayedNotes(bpy.types.Node, AnimationNode):
    bl_idname = "an_PlayedNotes"
    bl_label = "SEQ Played Notes"
    bl_width_default = 200

    mess = StringProperty()

    def draw(self,layout):
        if self.mess is not '':
            layout.label(self.mess, icon='INFO')

    def create(self):
        self.newInput("Integer","Start Frame","sFrame",minValue=0)
        self.newOutput("Object List","Played Notes","playNotes")
        self.newOutput("Text List","Output Notes","outNotes")

    def execute(self,sFrame):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,0.8,1)
        outN = []
        matP = bpy.data.materials['play']   # Play Material
        frameC = (bpy.context.scene.frame_current - sFrame) * 0.1
        # Get "Note" objects if they have "Play" material
        obs = [
            ob for ob in bpy.data.objects if ob.location.x > (frameC-0.01)
            and ob.location.x < (frameC+0.01) and ob.name.startswith('Note')
            and ob.material_slots[0].material == matP]
        # Get the note value and return as Text List, return Note Objects also
        for ob in obs:
            yLoc = ob.location.y
            sclOb = [ob for ob in bpy.data.objects if ob.name.startswith('Scale')
                and ob.location.y >(yLoc-0.02) and ob.location.y < yLoc][0]
            outN.append(sclOb.data.body)

        # Message Node
        self.mess = str(len(obs))+' Note(s) at this Time Interval'
        return obs, outN
