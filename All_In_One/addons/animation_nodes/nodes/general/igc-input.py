import bpy
import os
from bpy.props import *
from ... base_types import AnimationNode
from math import pi,cos

class IgcInputNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_IgcInputNode"
    bl_label = "IGC Animation Node"
    bl_width_default = 400

    # Setup vartiables
    offset = IntProperty(name = "Offset - Anim Start Frame", default = 1, min = -1000, max = 1000)
    skip = IntProperty(name = "Skip Entries Size", default = 1, min = 1, max = 10)
    e_off = IntProperty(name = "Start Easting Value", default = 0, min = 0, max = 170)
    n_off = IntProperty(name = "Start Northing Value", default = 0, min = 0, max = 80)
    g_scale = FloatProperty(name = "Geographic Scale", default = 1, min = 0.05, max = 10)
    t_scale = FloatProperty(name = "Time Scale", default = 1, min = 0.05, max = 10)
    message1 = StringProperty("")
    message2 = StringProperty("")
    igcFilePath = StringProperty()
    igcName = StringProperty()

    def draw(self, layout):
        layout.prop(self, "offset")
        layout.prop(self, "skip")
        layout.prop(self, "e_off")
        layout.prop(self, "n_off")
        layout.prop(self, "g_scale")
        layout.prop(self, "t_scale")
        layout.separator()
        col = layout.column()
        col.scale_y = 1.5
        self.invokeSelector(col ,"PATH", "loadIGC", icon = "NEW",
            text = "Select IGC File & Animate")
        if (self.message1 != ""):
            layout.label(self.message1, icon = "INFO")
        if (self.message2 != ""):
            layout.label(self.message2, icon = "ERROR")

    def execute(self):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (0.8,0.9,1)

    def loadIGC(self, path):
        self.message1 = ''
        self.igcFilePath = str(path)
        self.igcName = str(os.path.basename(path)).split(".")[0]
        self.message1 = "IGC File Loaded: " + str(os.path.basename(path))
        fix = True
        num = 1
        igc_file = self.igcFilePath
        # Create Empty to Animate get id of empty if it exists
        if bpy.data.objects[self.igcName] != 'None':
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects[self.igcName].select = True
            bpy.ops.object.delete()
        bpy.ops.object.add(type='EMPTY',location=(0,0,0),radius = 3)
        bpy.context.active_object.name = self.igcName
        bpy.context.active_object.empty_draw_type = "PLAIN_AXES"
        bpy.context.active_object.show_name = True
        #Open IGC file
        with open(igc_file) as f1:
            time = self.offset
            for line in f1:
                if line[0] == 'B':
                    if fix:
                        ang = int(line[7:9])
                        fix = False
                    #Easting
                    deg = int(line[15:18])
                    men = float(line[18:23]) / 60000
                    eloc = (deg+men-self.e_off) * 100000 * cos(ang*pi/180) * self.g_scale
                    #Correct East-West
                    if line[23] == 'W':
                        eloc = eloc * -1
                    # Northing
                    dng = int(line[7:9])
                    mnn = float(line[9:14]) / 60000
                    nloc = (dng+mnn-self.n_off) * 100000 * cos(ang*pi/180) * self.g_scale
                    #Correct North-South
                    if line[14] == 'S':
                        nloc = nloc * -1
                    alt = int(line[25:30]) * self.g_scale
                    ob = bpy.context.object
                    ob.location = [eloc,nloc,alt]
                    if num == 1:
                        ob.keyframe_insert(data_path='location', index=0, frame=time)
                        ob.keyframe_insert(data_path='location', index=1, frame=time)
                        ob.keyframe_insert(data_path='location', index=2, frame=time)
                    num = num + 1
                    if num > self.skip:
                        num = 1
                    time = time + (bpy.context.scene.render.fps * self.t_scale)
        bpy.ops.screen.frame_jump(end=False)
