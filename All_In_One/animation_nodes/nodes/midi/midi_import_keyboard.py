import bpy
import os
from ... base_types import AnimationNode
from bpy.props import *
from mathutils import Matrix
from ... events import propertyChanged

class MidiImpKBNode(bpy.types.Node, AnimationNode):
    bl_idname = "an_MidiImpKBNode"
    bl_label = "MIDI Load Keyboards, etc."
    bl_width_default = 200

    message = StringProperty()
    bridgeLen = FloatProperty(name = "Bridge Length", min = 0.5, update = propertyChanged)
    scale_f = FloatProperty(name = "Scale Factor", min = 0.5, max = 1, update = propertyChanged)

    def draw(self,layout):
        col = layout.column()
        col.scale_y = 1.5
        self.invokeFunction(col, "impKeyb88", icon = "NEW",
            text = "Load Sys 88-Note Keyboard")
        self.invokeFunction(col, "impKeyb61", icon = "NEW",
            text = "Load Sys 61-Note Keyboard")
        self.invokeSelector(col, "PATH", "impUdae", icon = "NEW",
            text = "Load User Selected .DAE file")
        self.invokeSelector(col, "PATH", "impUobj", icon = "NEW",
            text = "Load User Selected .OBJ file")
        self.invokeFunction(col, "impFrets", icon = "NEW",
            text = "Build Fretboard")
        layout.prop(self, "bridgeLen")
        layout.prop(self, "scale_f")
        layout.label("Imports to Acive Layer(s)", icon = "INFO")
        if self.message != '':
            layout.label(self.message, icon = "ERROR")

    def execute(self):
        self.use_custom_color = True
        self.useNetworkColor = False
        self.color = (1,1,0.75)

    def impKeyb88(self):
        for ob in bpy.data.objects:
            ob.select = False
        path = str(bpy.utils.user_resource('SCRIPTS', "addons")) + '/zeecee_midi/88keys.dae'
        bpy.ops.wm.collada_import(filepath=path)
        self.message = ''

    def impKeyb61(self):
        for ob in bpy.data.objects:
            ob.select = False
        path = str(bpy.utils.user_resource('SCRIPTS', "addons")) + '/zeecee_midi/61keys.dae'
        bpy.ops.wm.collada_import(filepath=path)
        self.message = ''

    def impFrets(self):
        for ob in bpy.data.objects:
            ob.select = False
        path = str(bpy.utils.user_resource('SCRIPTS', "addons")) + '/zeecee_midi/bridge.dae'
        bpy.ops.wm.collada_import(filepath=path)
        self.message = ''
        scn = bpy.context.scene
        src_obj = bpy.data.objects.get('Bridge')

        if src_obj is None:
            return
        src_obj.select = True
        src_obj.scale = (self.bridgeLen,self.bridgeLen,self.bridgeLen)
        bpy.context.scene.objects.active = src_obj
        bpy.ops.object.transform_apply(location = False, scale = True, rotation = False)
        src_obj.select = False
        scl = self.scale_f
        xLoc = src_obj.location.x
        fret = self.bridgeLen
        fretN = ['NUT','F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12',
            'F13','F14','F15','F16','F17','F18','F19','F20','F21','F22','F23','F24']

        for i in range (0,25):
            new_obj = src_obj.copy()
            new_obj.data = src_obj.data.copy()
            new_obj.animation_data_clear()
            new_obj.name = fretN[i]
            scn.objects.link(new_obj)
            new_obj.location.x = fret
            new_obj.scale.y = scl
            new_obj.select = True
            bpy.context.scene.objects.active = new_obj
            bpy.ops.object.transform_apply(location = False, scale = True, rotation = False)
            new_obj.select = False
            fret = fret * (0.5**(1/12))
            scl = self.scale_f + (((self.bridgeLen - fret) / self.bridgeLen) * (1 - self.scale_f))

    def impUdae(self, path):
        if str(path).split(".")[1] == 'dae':
            bpy.ops.wm.collada_import(filepath=str(path))
            self.message = ''
        else:
            self.message = 'NOT DAE! ' + str(path)

    def impUobj(self, path):
        if str(path).split(".")[1] == 'obj':
            bpy.ops.import_scene.obj(filepath=path)
            self.message = ''
        else:
            self.message = 'NOT OBJ! ' + str(path)
