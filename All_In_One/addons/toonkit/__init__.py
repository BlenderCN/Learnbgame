# Copyright (C) Cogumelo Softworks - ToonKit for Cycles v1.1
# License: http://www.gnu.org/licenses/gpl.html GPL version 3 or higher

# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
    "name": "Cycles ToonKit",
    "author": "Cogumelo Softworks",
    "version": (1,2),
    "blender": (2,80,0),
    "location": "Cycles Node Material",
    "description": "NPR/Toon Rendering on Cycles",
    "wiki_url":  "http://cgcookiemarkets.com/blender/all-products/baketool/?view=docs",
    "warning": "",
    "category": "Render"
}

import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.app.handlers import persistent
import mathutils
import math
import os
import random
        
#------------------------------- DATA ------------------------------------
def set_preset(self,value):
    bpy.context.scene.cycles.max_bounces = 8
    bpy.context.scene.cycles.min_bounces = 8
    bpy.context.scene.cycles.diffuse_bounces = 8
    bpy.context.scene.cycles.glossy_bounces = 8
    bpy.context.scene.cycles.transmission_bounces = 8
    bpy.context.scene.cycles.volume_bounces = 8
    bpy.context.scene.cycles.use_transparent_shadows = False
    bpy.context.scene.cycles.caustics_reflective = False
    bpy.context.scene.cycles.caustics_refractive = False
    
    bpy.context.scene.cycles.use_animated_seed = True
    bpy.context.scene.cycles.preview_samples = 8
    bpy.context.scene.cycles.device = "CPU"
    bpy.context.scene.cycles.shading_system = True;
    
    value = bpy.context.scene.NPRSettings.scene_preset
    #print(value)
        
    if(value == "PREVIEW"):
        bpy.context.scene.cycles.samples = 2
        bpy.context.scene.cycles.preview_samples = 2
        bpy.context.scene.render.layers.active.cycles.use_denoising = False
        bpy.context.scene.render.tile_x = 32
        bpy.context.scene.render.tile_y = 32
        
    
    if(value == "DRAFT"):
        bpy.context.scene.cycles.samples = 8
        bpy.context.scene.cycles.preview_samples = 8
        bpy.context.scene.render.layers.active.cycles.use_denoising = False
        bpy.context.scene.render.tile_x = 32
        bpy.context.scene.render.tile_y = 32
        
    if(value == "DRAFT2"):
        bpy.context.scene.cycles.samples = 8
        bpy.context.scene.cycles.preview_samples = 8
        bpy.context.scene.render.layers.active.cycles.use_denoising = True
        bpy.context.scene.render.tile_x = 256
        bpy.context.scene.render.tile_y = 256

    if(value == "MID"):
        bpy.context.scene.cycles.samples = 16
        bpy.context.scene.cycles.preview_samples = 16
        bpy.context.scene.render.layers.active.cycles.use_denoising = False
        bpy.context.scene.render.tile_x = 32
        bpy.context.scene.render.tile_y = 32
        
    if(value == "PRODUCTION"):
        bpy.context.scene.cycles.samples = 32
        bpy.context.scene.cycles.preview_samples = 32
        bpy.context.scene.render.layers.active.cycles.use_denoising = False
        bpy.context.scene.render.tile_x = 32
        bpy.context.scene.render.tile_y = 32
        
    if(value == "PRODUCTION2"):
        bpy.context.scene.cycles.samples = 32
        bpy.context.scene.cycles.preview_samples = 32
        bpy.context.scene.render.layers.active.cycles.use_denoising = True
        bpy.context.scene.render.layers.active.cycles.denoising_radius = 3
        bpy.context.scene.render.tile_x = 256
        bpy.context.scene.render.tile_y = 256
        
    return None
    
class NPR_GlobalSettings(bpy.types.PropertyGroup):
    # LineArt
    lineart_samples = bpy.props.IntProperty(default=5)
    lineart_relative = bpy.props.IntProperty(default=0)
    lineart_size = bpy.props.FloatProperty(default=0.5)
    lineart_normall = bpy.props.FloatProperty(default=0.9)
    lineart_depthl = bpy.props.FloatProperty(default=0.2)
    
    # Setup Scene
    presets = [
    ("PREVIEW","Preview","",1),
    ("DRAFT", "Draft", "", 2),
    ("DRAFT2", "Draft Denoised", "", 3),
    ("MID", "Mid", "", 4),
    ("PRODUCTION", "Production", "",5),
    ("PRODUCTION2", "Production Denoised", "", 6),
    ]
    
    scene_preset = bpy.props.EnumProperty(items=presets, update=set_preset,name="Render Quality Preset", default="DRAFT")
    
class NPR_LightSettings(bpy.types.PropertyGroup):
    radius = bpy.props.FloatProperty(default = 5,min=0)
    smooth = bpy.props.FloatProperty(min=0,max=1, default = 0.5)
    color = bpy.props.FloatVectorProperty(size = 3, subtype = "COLOR", default=(1.0,1.0,1.0),min=0.0,max=1.0)
                                                         
    shadow_smooth = bpy.props.FloatProperty(default = 0,min=0,max=1)
    use_shadow = bpy.props.BoolProperty(default = True)
    lightGroup = bpy.props.IntProperty(default = 0)
    
class NPR_WorldSettings(bpy.types.PropertyGroup):
    ambient = bpy.props.FloatVectorProperty(size = 3, subtype = "COLOR", default=(0.0,0.0,0.0),min=0.0,max=1.0)

#------------------------------- FUNCTIONS ------------------------------------    
def add_node(context, nodetype):
    bpy.ops.node.add_node(type=nodetype.__name__,use_transform=True)
    node = context.active_node
    return node
    
def pre_frame_change(scene):
    if scene.render.engine == 'CYCLES':
        # Scan materials to see if I have a custom node within any of the trees.
        for m in bpy.data.materials:
            if m.node_tree != None:
                for n in m.node_tree.nodes:
                    if n.bl_idname == 'CustomNodeType':
                        if(n.evaluate()):
                            n.update()

#------------------------------- HANDLERS AND SETTINGS ------------------------------------

def UpdateAllShadersPath():
    if bpy.context.scene.render.engine == 'CYCLES':
        # Scan materials to see if I have a custom node within any of the trees.
        for m in bpy.data.materials:
            if m.node_tree != None:
                for n in m.node_tree.nodes:
                    if("NPR" in n.name and n.type == "SCRIPT"):
                        pathname = os.path.dirname(n.filepath)
                        basename = os.path.basename(n.filepath)
                        n.filepath = bpy.context.user_preferences.addons[__name__].preferences.filepath + basename
                        print(n.filepath)

def UpdateLineArtFromGlobal():
    if bpy.context.scene.render.engine == 'CYCLES':
        # Scan materials to see if I have a custom node within any of the trees.
        for m in bpy.data.materials:
            if m.node_tree != None:
                for n in m.node_tree.nodes:
                    # Object Info
                    if "NPRLineShader" in n.name:
                        if(n.inputs["UseGlobal"].default_value == 1): # Use Global = 1
                            #if "2" not in n.name: 
                                #n.inputs["Samples"].default_value = bpy.context.scene.NPRSettings.lineart_samples
                            n.inputs["Size"].default_value = bpy.context.scene.NPRSettings.lineart_size
                            n.inputs["NormalLimit"].default_value = bpy.context.scene.NPRSettings.lineart_normall
                            n.inputs["DepthLimit"].default_value = bpy.context.scene.NPRSettings.lineart_depthl
                            n.inputs["Relative"].default_value = bpy.context.scene.NPRSettings.lineart_relative

#------------------------------- MAIN UI ------------------------------------
class NPRWorldSettingsPanel(bpy.types.Panel):
    """Main panel with properties"""
    bl_label = "ToonKit World Settings"
    bl_idname = "toonkit.worldsettings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "world"
        
    @classmethod
    def poll(cls,context):
        if bpy.context.scene.render.engine == "CYCLES":
            return True
        else:
            return False
    
    def draw(self,context):
        box = self.layout
        
        box.label(text="ToonKit Settings:",icon="COLOR")
        box.prop(bpy.context.world.NPRSettings, "ambient",text="Ambient Light")

class NPRLightSettingsPanel(bpy.types.Panel):
    """Main panel with properties"""
    bl_label = "ToonKit Light Settings"
    bl_idname = "toonkit.lightsettings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
   
    @classmethod
    def poll(cls,context):
        if bpy.context.scene.render.engine == "CYCLES" and bpy.context.active_object.type == "LIGHT":
            return True
        else:
            return False
    
    def draw(self,context):
        box = self.layout
        
        box.label(text="ToonKit Settings:",icon="COLOR")
        box.prop(bpy.context.active_object.data.NPRSettings, "lightGroup",text="Light Group")
        
        #box.label("SHADING:")
        
        box.prop(bpy.context.active_object.data.NPRSettings, "color",text="Color")
        if(bpy.context.active_object.data.type == "POINT"):
            box.prop(bpy.context.active_object.data.NPRSettings, "radius",text="Radius")
        box.prop(bpy.context.active_object.data.NPRSettings, "smooth",text="Smooth")
        
        
        #box.label("SHADOWS:")
        box.prop(bpy.context.active_object.data.NPRSettings, "use_shadow",text="Enable Shadow")
        #box.prop(bpy.context.active_object.data.NPRSettings, "shadow_sampling",text="Sampling")
        box.prop(bpy.context.active_object.data.NPRSettings, "shadow_smooth",text="Smooth")
        
        
class NPRPanel(bpy.types.Panel):
    """Main panel with properties"""
    bl_label = "ToonKit Render Settings"
    bl_idname = "toonkit.properties"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
        
    @classmethod
    def poll(cls,context):
        if bpy.context.scene.render.engine == "CYCLES":
            return True
        else:
            return False
    
    def draw(self,context):
        box = self.layout
        
        box.label(text="Quick Render Setup",icon="SCENE")
        box.prop(bpy.context.scene.NPRSettings, "scene_preset",text ="")
        box.separator()
        
        box.label(text="LineArt Global Settings:",icon="IPO_LINEAR")
        #box.prop(bpy.context.scene.NPRSettings, "lineart_samples",text="Samples")
        box.prop(bpy.context.scene.NPRSettings, "lineart_relative",text="Relative")
        box.prop(bpy.context.scene.NPRSettings, "lineart_size",text="Size")
        box.prop(bpy.context.scene.NPRSettings, "lineart_normall",text="Normal Limit")
        box.prop(bpy.context.scene.NPRSettings, "lineart_depthl",text ="Depth Limit")
        box.operator(NPRUpdateGlobalLineArt.bl_idname)
        
        
        
        
class NPRUpdateGlobalLineArt(bpy.types.Operator):
    """ToonKit Ligh Info"""
    bl_idname = "npr.updategloballineart"
    bl_label = "Update LineArt"
    
    @classmethod
    def poll(cls,context):
        if bpy.context.scene.render.engine == "CYCLES":
            return True
        else:
            return False

    def execute(self, context):
        UpdateLineArtFromGlobal()
        return {'FINISHED'}
        
#------------------------------- OTHER CUSTOM NODES NODES --------------------------
class NPRGetInfo(bpy.types.Operator):
    """ToonKit Ligh Info"""
    bl_idname = "npr.getinfo"
    bl_label = "Light Info"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, NPRGetInfoNode)
        node.name = "NPRLighInfo"
        node.label = "Light Info"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
class NPRGetInfoNode(Node):
    '''ToonKit Get Light Values'''
    bl_idname = 'NPRGetInfoNode'
    bl_label = 'Light Info'
    bl_icon = 'INFO'

    pos = bpy.props.FloatVectorProperty()
    rot = bpy.props.FloatVectorProperty()
    color = bpy.props.FloatVectorProperty(subtype = "COLOR", size = 3,min = 0,max=1)
    target = bpy.props.StringProperty(description = "if Target is filled it will bake all passes and objects for the target selected")
    lightSmooth = bpy.props.FloatProperty()
    shadowSmooth = bpy.props.FloatProperty()
    radius = bpy.props.FloatProperty()
    
    def evaluate(self):
        try:
            bpy.data.objects[self.target]
        except:
            return False
        
        #if(self.target == "" or bpy.data.objects[self.target] == None ):
            #return False
        
            
        newpos = bpy.data.objects[self.target].location
        if(newpos[:] != self.pos[:]):
            self.pos = newpos
            return True
            
        newrot = bpy.data.objects[self.target].rotation_euler
        if(newrot[:] != self.rot[:]):
            self.rot = newrot
            return True
        
        if(bpy.data.objects[self.target].type == "LIGHT"):
            newcolor = bpy.data.objects[self.target].data.NPRSettings.color;
            if(newcolor != self.color):
                self.color = newcolor
                return True
                
            lSmooth = bpy.data.objects[self.target].data.NPRSettings.smooth;
            if(lSmooth != self.lightSmooth):
                self.lightSmooth = lSmooth
                return True
            
            sSmooth = bpy.data.objects[self.target].data.NPRSettings.shadow_smooth;
            if(sSmooth != self.shadowSmooth):
                self.shadowSmooth = sSmooth
                return True
                
            radius = bpy.data.objects[self.target].data.NPRSettings.radius;
            if(radius != self.radius):
                self.radius = radius
                return True

        return False

    
    def init(self, context):
        
        self.outputs.new('NodeSocketColor', "Light Color")
        self.outputs["Light Color"].default_value = [0,0,0,1];
        
        self.outputs.new('NodeSocketFloat', "Radius")
        self.outputs["Radius"].default_value = 0;
        
        self.outputs.new('NodeSocketFloat', "Smooth")
        self.outputs["Smooth"].default_value = 0;
        
        self.outputs.new('NodeSocketFloat', "Shadow Smooth")
        self.outputs["Shadow Smooth"].default_value = 0;

        
        self.outputs.new('NodeSocketVector', "Position")
        self.outputs["Position"].default_value = [0,0,0];
        
        self.outputs.new('NodeSocketVector', "Direction")
        self.outputs["Direction"].default_value = [0,0,0];
        
        

    def update(self):
        if self.target == "" or self.target == None:
            return;
            
        out = self.outputs["Position"]
        if out.is_linked :
            for o in out.links:
                try:
                    o.to_socket.node.inputs[o.to_socket.name].default_value = bpy.data.objects[self.target].location
                except:
                    pass
                    
        out = self.outputs["Direction"]
        if out.is_linked :
            for o in out.links:
                try:
                    vec = mathutils.Vector((0.0,0.0,1.0));
                    vec.rotate(bpy.data.objects[self.target].rotation_euler);
                    o.to_socket.node.inputs[o.to_socket.name].default_value = vec;
                except:
                    pass
        
        out = self.outputs["Light Color"]
        if out.is_linked :
            for o in out.links:
                try:
                    emitColor = bpy.data.objects[self.target].data.NPRSettings.color;
                    o.to_socket.node.inputs[o.to_socket.name].default_value = (emitColor[0],emitColor[1],emitColor[2],0.0);
                except:
                    pass
                    
        out = self.outputs["Smooth"]
        if out.is_linked :
            for o in out.links:
                try:
                    smooth = bpy.data.objects[self.target].data.NPRSettings.smooth;
                    o.to_socket.node.inputs[o.to_socket.name].default_value = smooth;
                except:
                    pass
                    
        out = self.outputs["Shadow Smooth"]
        if out.is_linked :
            for o in out.links:
                try:
                    sSmooth = bpy.data.objects[self.target].data.NPRSettings.shadow_smooth;
                    o.to_socket.node.inputs[o.to_socket.name].default_value = sSmooth;
                except:
                    pass
                    
        out = self.outputs["Radius"]
        if out.is_linked :
            for o in out.links:
                try:
                    radius = bpy.data.objects[self.target].data.NPRSettings.radius;
                    o.to_socket.node.inputs[o.to_socket.name].default_value = radius;
                except:
                    pass

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.prop_search(self, "target", context.scene, "objects", text="")
        pass

    # Optional: custom label
    # Explicit user label overrides this, but here we can define a label dynamically.
    def draw_label(self):
        return "Light Info"
           

class NPRGetSceneLightInfo(bpy.types.Operator):
    """ToonKit Ligh Info"""
    bl_idname = "npr.getscenelightinfo"
    bl_label = "Scene Info"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, NPRGetSceneLightInfoNode)
        node.name = "NPRSceneLighInfo"
        node.label = "Scene Light Info"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT') 
        
class NPRGetSceneLightInfoNode(Node):
    '''ToonKit Get Scene Light Values'''
    bl_idname = 'NPRGetSceneLightInfoNode'
    bl_label = 'Scene Light Info'
    bl_icon = 'INFO'

    data = bpy.props.StringProperty()
    dataAmbColor = bpy.props.StringProperty()
    lightCount = bpy.props.IntProperty()
    lightGroup = bpy.props.IntProperty(min=0)
    
    def evaluate(self):
        markToUpdate = False
        
        dataLights = self.data.split(";")
        
        updatedData = "";
        
        # Get Ambient Light Color
        ambientColor = str("{0:.2f}".format(bpy.context.scene.world.NPRSettings.ambient[0]) + "|" + "{0:.2f}".format(bpy.context.scene.world.NPRSettings.ambient[1]) + "|" + "{0:.2f}".format(bpy.context.scene.world.NPRSettings.ambient[2])) + ";"
        
        # Update if AmbLight Changed
        if(self.dataAmbColor != ambientColor):
            markToUpdate = True
            self.dataAmbColor = ambientColor
            
        updatedData += ambientColor
        
        # Get all Light objects
        lightList = [] 
        for obj in bpy.context.scene.objects:
            if obj.type == "LIGHT":
                if obj.data.NPRSettings.lightGroup == self.lightGroup:
                    lightList.append(obj)
        
        # Update if Light Count Changed
        if(self.lightCount != len(lightList)):
            self.lightCount = len(lightList)
            markToUpdate = True
            
        
        for i,obj in enumerate(lightList):
           
            
            lightType = str(obj.data.type)
            lightPos = "{0:.2f}".format(obj.location[0]) + "," + "{0:.2f}".format(obj.location[1]) + "," + "{0:.2f}".format(obj.location[2])
            
            vec = mathutils.Vector((0.0,0.0,1.0));
            vec.rotate(obj.rotation_euler);
            
            lightRot = "{0:.2f}".format(vec[0]) + "," + "{0:.2f}".format(vec[1]) + "," + "{0:.2f}".format(vec[2])
            
            lightSmooth = "{0:.2f}".format(obj.data.NPRSettings.smooth)
            lightRadius = "{0:.2f}".format(obj.data.NPRSettings.radius)
            lightColor = str("{0:.2f}".format(obj.data.NPRSettings.color[0]) + "|" + "{0:.2f}".format(obj.data.NPRSettings.color[1]) + "|" + "{0:.2f}".format(obj.data.NPRSettings.color[2]))
            shadowSmooth = "{0:.2f}".format(obj.data.NPRSettings.shadow_smooth)

            
            if(obj.data.NPRSettings.use_shadow):
                useShadow = str(1)
            else:
                useShadow = str(0)
                
            dataPos = ""
            # If there's the DataLight
            try:
                 # The First Light object is the Ambient so start with 1 instead 0
                
                data = dataLights[i+1].split(",")             
                
                dataType = data[0]
                
                if(lightType != dataType):
                    markToUpdate = True
                    dataType = lightType
                    
                
                dataPos = data[1] + "," + data[2] + "," + data[3]
                if(dataPos != lightPos):
                    markToUpdate = True
                    dataPos = lightPos
                    
                    
                dataRot = data[4] + "," + data[5] + "," + data[6]
                if(dataRot != lightRot):
                    markToUpdate = True
                    dataRot = lightRot
                    
                dataSmooth = data[7]   
                if(dataSmooth != lightSmooth):
                    markToUpdate = True
                    dataSmooth = lightSmooth
                    
                dataRadius = data[8]
                if(dataRadius != lightRadius):
                    markToUpdate = True
                    dataRadius = lightRadius
                    
                dataColor = data[9]
                if(dataColor != lightColor):
                    markToUpdate = True
                    dataColor = lightColor
                
                dataShadowSmooth = data[10]
                if(dataShadowSmooth != shadowSmooth):
                    markToUpdate = True
                    dataShadowSmooth = shadowSmooth
                
                dataUseShadow = data[11]
                if(dataUseShadow != useShadow ):
                    markToUpdate = True
                    dataUseShadow = useShadow
                
            except:
                
                # if not create
                markToUpdate = True
                dataType = lightType;
                dataPos = lightPos;
                dataRot = lightRot;
                dataSmooth = lightSmooth
                dataRadius = lightRadius
                dataColor = lightColor
                dataUseShadow = useShadow
                dataShadowSmooth = shadowSmooth
                #dataAmbLight = ambLight
                #dataShadowSampling = shadowSampling
                
            updatedData += dataType + "," + dataPos + "," + dataRot + "," + dataSmooth + "," + dataRadius + "," + dataColor + "," + dataShadowSmooth + "," + dataUseShadow
            
            # Se não for o ultimo
            if(i < len(lightList)-1):
                updatedData += ";"
                
        self.data = updatedData;
        return markToUpdate
    
    def init(self, context):
        
        self.outputs.new('NodeSocketString', "Data")
        self.outputs["Data"].default_value = "";

    def update(self):
        #print("updated " + str(random.randint(0,100)))
        out = self.outputs["Data"]
        if out.is_linked:
            for o in out.links:
                try:
                    o.to_socket.node.inputs[o.to_socket.name].default_value = self.data
                    #print(self.data)
                except:
                    pass

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.prop(self, "lightGroup",text="Light Group")
        pass

    # Optional: custom label
    # Explicit user label overrides this, but here we can define a label dynamically.
    def draw_label(self):
        return "Light Info"
        
    def draw_buttons_ext(self, context, layout):
        layout.prop(self, "lightGroup",text="Light Group")
 
 

#------------------------------- OPERATOR NODES ------------------------------------
class NPRFXBlur(bpy.types.Operator):
    """Blur Effect to be applied in the Texture Vector input (Make sure you have a UV Connect to it)"""
    bl_idname = "npr.fxblur"
    bl_label = "Blur Effect"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_FXBlur.osl"
        node.name = "FXBlur"
        node.label = "Blur Effect"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

class NPRFXPixelize(bpy.types.Operator):
    """Pixelize Effect to be applied in the Texture Vector input (Make sure you have a UV Connect to it)"""
    bl_idname = "npr.fxpixelize"
    bl_label = "Pixelize Effect"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_FXPixelize.osl"
        node.name = "FXPixel"
        node.label = "Pixelize Effect"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
class NPRFXPaint(bpy.types.Operator):
    """Paint/Deform Effect to be applied in the Texture Vector input (Make sure you have a UV Connect to it)"""
    bl_idname = "npr.fxpaint"
    bl_label = "Paint Effect"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_FXPaint.osl"
        node.name = "FXPaint"
        node.label = "Paint Effect"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

class NPRProcTexHair(bpy.types.Operator):
    """Procedural Hair/Lines Texture Generator (Make sure you have a UV Connect to it) """
    bl_idname = "npr.preceduralhair"
    bl_label = "Hair"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_Hair.osl"
        node.name = "NPRHair"
        node.label = "Texture Hair"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
class NPRProcTexHalftone(bpy.types.Operator):
    """Procedural View Based Halftone Texture Generator (5 patterns to Select)"""
    bl_idname = "npr.proctexhalf"
    bl_label = "Halftone"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_Halftone.osl"
        node.name = "NPRHalftone"
        node.label = "Texture Halftone"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
   
class NPRTextureRamp2D(bpy.types.Operator):
    """Texture Ramp2D Mapper to be applied in the Texture Vector input (Make sure you have a UV Connect to it)"""
    bl_idname = "npr.ramp2d"
    bl_label = "Ramp2D"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_Ramp2D.osl"
        node.name = "NPRRamp2D"
        node.label = "Ramp2D Mapper"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

class NPRTextureSpriteSheet(bpy.types.Operator):
    """Texture Sprite Sheet Mapper to be applied in the Texture Vector input (Make sure you have a UV Connect to it)"""
    bl_idname = "npr.spritesheet"
    bl_label = "Sprite Sheet"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_SpriteSheet.osl"
        node.name = "NPRSpriteSheet"
        node.label = "SpriteSheet Mapper"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
class NPRSimplifyNormals(bpy.types.Operator):
    """Simplify Normals of some model to be more sphere alike """
    bl_idname = "npr.simplifynormals"
    bl_label = "Simplify Normals"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_SimplifyNormals.osl"
        node.name = "NPRSimplifyNormals"
        node.label = "Simplify Normals"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
class NPRTextureMatcap(bpy.types.Operator):
    """Texture Matcap Mapper to be applied in the Texture Vector input (Make sure you have a UV Connect to it)"""
    bl_idname = "npr.matcap"
    bl_label = "Matcap"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_Matcap.osl"
        node.name = "NPRMatcap"
        node.label = "Matcap Mapper"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
class NPRPMask(bpy.types.Operator):
    """Set objects prefixed with '+' on top of others """
    
    bl_idname = "npr.pmask"
    bl_label = "Penetration Mask"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_PMask.osl"
        node.name = "NPRPMask"
        node.label = "Penetration Mask"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')                                  
class NPRAddShader(bpy.types.Operator):
    """Mix Two Shaders pondered by the Fac value"""
    bl_idname = "npr.add"
    bl_label = "Add Mixer"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_Aditive.osl"
        node.name = "NPRAddShader"
        node.label = "Add Shader"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
class NPRMultiBlend(bpy.types.Operator):
    """Mix Many Inputs pondered by a value"""
    bl_idname = "npr.multiblend"
    bl_label = "MultiBlend"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_MBlend.osl"
        node.name = "NPRMultiBlend"
        node.label = "MultiBlend"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
class NPRLine(bpy.types.Operator):
    """Sampled Line Rendering"""
    bl_idname = "npr.line"
    bl_label = "LineArt (Sampled)"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_Line.osl"
        node.name = "NPRLineShader"
        node.label = "LineArt (Sampled)"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
class NPRLine2(bpy.types.Operator):
    """Deterministic Line Rendering"""
    bl_idname = "npr.line2"
    bl_label = "LineArt (Deterministic)"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_Line2.osl"
        node.name = "NPRLineShader2"
        node.label = "LineArt (Deterministic)"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
class NPRDepth(bpy.types.Operator):
    """Camera Depth Normalized by Far and Near Values """
    bl_idname = "npr.depth"
    bl_label = "Depth"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_Depth.osl"
        node.name = "NPRDepth"
        node.label = "Camera Depth"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
class NPRAO(bpy.types.Operator):
    """Ambient Occlusion caused by self occlusion or near objects"""
    bl_idname = "npr.ao"
    bl_label = "Ambient Occlusion"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_AO.osl"
        node.name = "NPRAO"
        node.label = "Ambient Occlusion"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

class NPRGooch(bpy.types.Operator):
    """Technical Shading used for good visibility """
    bl_idname = "npr.gooch"
    bl_label = "Cool Warm"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_Gooch.osl"
        node.name = "NPRGooch"
        node.label = "Cool Warm"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
class NPRRim(bpy.types.Operator):
    """View Based Rim Light Effect"""
    bl_idname = "npr.rim"
    bl_label = "Rim"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_Rim.osl"
        node.name = "NPRRim"
        node.label = "Rim"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

class NPRSpecularDir(bpy.types.Operator):
    """Specular from specific Light Direction"""
    bl_idname = "npr.speculardir"
    bl_label = "Directional Specular"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'
    
    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_SpecularDir.osl"
        node.name = "NPRSpecularDir"
        node.label = "Directional Specular"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
class NPRSpecularPoint(bpy.types.Operator):
    """Specular from specific Light Direction"""
    bl_idname = "npr.specularpoint"
    bl_label = "Point Specular"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'
    
    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_SpecularPoint.osl"
        node.name = "NPRSpecularPoint"
        node.label = "Point Specular"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')

class NPRLightDir(bpy.types.Operator):
    """ Shading and Shadow from a single Directional Lamp"""
    bl_idname = "npr.dirlight"
    bl_label = "Directional Light"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_LightDir.osl"
        node.name = "NPRLightDir"
        node.label = "Directional Light"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
class NPRLightPoint(bpy.types.Operator):
    """ToonKit Point Light Complete"""
    bl_idname = "npr.pointlight"
    bl_label = "Point Light"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_LightPoint.osl"
        node.name = "NPRLightPoint"
        node.label = "Point Light"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
class NPRSceneLight(bpy.types.Operator):
    """ToonKit Scene Light"""
    bl_idname = "npr.scenelight"
    bl_label = "Scene Light"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_SceneLight.osl"
        node.name = "NPRSceleLight"
        node.label = "Scene Light"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
class NPRShadowScene(bpy.types.Operator):
    """ToonKit Directional Shading"""
    bl_idname = "npr.shadowscene"
    bl_label = "Scene Shadow"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_SoftShadowScene.osl"
        node.name = "NPRShadowScene"
        node.label = "Scene Shadow"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
class NPRShadowDir(bpy.types.Operator):
    """ToonKit Directional Shadow"""
    bl_idname = "npr.shadowdir"
    bl_label = "Directional Shadow"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_SoftShadowDir.osl"
        node.name = "NPRDirShadow"
        node.label = "Directional Shadow"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
class NPRShadowPoint(bpy.types.Operator):
    """ToonKit Point Shadow"""
    bl_idname = "npr.shadowpoint"
    bl_label = "Point Shadow"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_SoftShadowPoint.osl"
        node.name = "NPRPointShadow"
        node.label = "Point Shadow"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
class NPRShadingScene(bpy.types.Operator):
    """ToonKit Scene Shading"""
    bl_idname = "npr.shadingscene"
    bl_label = "Scene Shading"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_ShadingScene.osl"
        node.name = "NPRSceneShading"
        node.label = "Scene Shading"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
class NPRShadingPoint(bpy.types.Operator):
    """Shading from Single Point Light Object"""
    bl_idname = "npr.pointshading"
    bl_label = "Point Shading"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        # Node 1
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_ShadingPoint.osl"
        node.name = "NPRShading"
        node.label = "Point Shading"       
        
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
class NPRShadingDir(bpy.types.Operator):
    """ToonKit Shading"""
    bl_idname = "npr.directionalshading"
    bl_label = "Directional Shading"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_ShadingDir.osl"
        node.name = "NPRShadingDir"
        node.label = "Directional Shading"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
class NPREasyToon(bpy.types.Operator):
    """Uber Toonkit Shader"""
    bl_idname = "npr.easytoon"
    bl_label = "EasyToon"

    @classmethod
    def poll(cls, context):
        space = context.space_data
        return space.type == 'NODE_EDITOR'

    def execute(self, context):
        node = add_node(context, bpy.types.ShaderNodeScript)
        node.mode = "EXTERNAL"
        path = context.user_preferences.addons[__name__].preferences.filepath
        node.filepath = path + "/CNPRK_EasyToon.osl"
        node.name = "NPREasyToon"
        node.label = "EasyToon"
        return bpy.ops.node.translate_attach_remove_on_cancel('INVOKE_DEFAULT')
        
        
#------------------------------- MENUS ------------------------------------
class NPRMenuFullLight(bpy.types.Menu):
    bl_label = "Full Light"
    bl_idname = "NPRMenuFullLight"

    def draw(self, context):
        layout = self.layout
        layout.operator(NPREasyToon.bl_idname)
        layout.separator()
        layout.operator(NPRLightDir.bl_idname)
        layout.operator(NPRLightPoint.bl_idname)
        layout.operator(NPRSceneLight.bl_idname)

class NPRMenuLight(bpy.types.Menu):
    bl_label = "Light"
    bl_idname = "NPRMenuLight"

    def draw(self, context):
        layout = self.layout
        layout.menu(NPRMenuShading.bl_idname)
        layout.menu(NPRMenuShadow.bl_idname)
        layout.menu(NPRMenuFullLight.bl_idname)
        
class NPRMenuShading(bpy.types.Menu):
    bl_label = "Shading"
    bl_idname = "NPRMenuShading"

    def draw(self, context):
        layout = self.layout
        
        layout.operator(NPRShadingPoint.bl_idname)
        layout.operator(NPRShadingDir.bl_idname)
        layout.operator(NPRShadingScene.bl_idname)
        layout.separator()
        layout.operator(NPRSpecularDir.bl_idname)
        layout.operator(NPRSpecularPoint.bl_idname)
        layout.separator()
        layout.operator(NPRGooch.bl_idname)
        
        
        
class NPRMenuSceneInfo(bpy.types.Menu):
    bl_label = "Input"
    bl_idname = "NPRMenuSceneInfo"

    def draw(self, context):
        layout = self.layout
        layout.operator(NPRGetInfo.bl_idname)
        layout.operator(NPRGetSceneLightInfo.bl_idname)
        
class NPRMenuShadow(bpy.types.Menu):
    bl_label = "Shadow"
    bl_idname = "NPRMenuShadow"

    def draw(self, context):
        layout = self.layout
        layout.operator(NPRShadowPoint.bl_idname)
        layout.operator(NPRShadowDir.bl_idname)
        layout.operator(NPRShadowScene.bl_idname)
       
class NPRMenuMixers(bpy.types.Menu):
    bl_label = "Utilities"
    bl_idname = "NPRMenuMixer"

    def draw(self, context):
        layout = self.layout
        layout.operator(NPRAddShader.bl_idname)
        layout.operator(NPRMultiBlend.bl_idname)
        layout.operator(NPRPMask.bl_idname)                                   
        
        layout.operator(NPRSimplifyNormals.bl_idname)
    
class NPRMenuTexture(bpy.types.Menu):
    bl_label = "Textures"
    bl_idname = "NPRMenuTexture"

    def draw(self, context):
        layout = self.layout
       
        layout.menu(NPRMenuPatterns.bl_idname)
        layout.menu(NPRMenuTextMappers.bl_idname)
        layout.menu(NPRMenuTextEffects.bl_idname)
              
class NPRMenuPatterns(bpy.types.Menu):
    bl_label = "Patterns"
    bl_idname = "NPRMenuPatterns"

    def draw(self, context):
        layout = self.layout
       
        layout.operator(NPRProcTexHalftone.bl_idname)
        layout.operator(NPRProcTexHair.bl_idname)
        
class NPRMenuTextMappers(bpy.types.Menu):
    bl_label = "Mappers"
    bl_idname = "NPRMenuTexMappers"

    def draw(self, context):
        layout = self.layout
        
        layout.operator(NPRTextureMatcap.bl_idname)
        layout.operator(NPRTextureSpriteSheet.bl_idname)
        layout.operator(NPRTextureRamp2D.bl_idname)
        
class NPRMenuTextEffects(bpy.types.Menu):
    bl_label = "Effects"
    bl_idname = "NPRMenuTexEffects"

    def draw(self, context):
        layout = self.layout
       
        layout.operator(NPRFXBlur.bl_idname)
        layout.operator(NPRFXPaint.bl_idname)
        layout.operator(NPRFXPixelize.bl_idname)
        
class NPRMenuComponents(bpy.types.Menu):
    bl_label = "Effects"
    bl_idname = "NPRMenuComponents"

    def draw(self, context):
        layout = self.layout
        
        
        layout.operator(NPRLine2.bl_idname)
        layout.operator(NPRLine.bl_idname)
        layout.separator()
        layout.operator(NPRRim.bl_idname)
        layout.operator(NPRDepth.bl_idname)
        layout.separator()
        layout.operator(NPRAO.bl_idname)      
        
class NPRMenuPointLight(bpy.types.Menu):
    bl_label = "Point Light"
    bl_idname = "NPRMenuPointLight"

    def draw(self, context):
        layout = self.layout
        layout.operator(NPRLightPoint.bl_idname)
        layout.operator(NPRShadingPoint.bl_idname)
        layout.operator(NPRShadowPoint.bl_idname)
        
class NPRMenuDirLight(bpy.types.Menu):
    bl_label = "Directional Light"
    bl_idname = "NPRMenuDirLight"

    def draw(self, context):
        layout = self.layout
        layout.operator(NPRLightDir.bl_idname)
        layout.operator(NPRShadingDir.bl_idname)
        layout.operator(NPRShadowDir.bl_idname)       
        
class NPRMenu(bpy.types.Menu):
    bl_label = "ToonKit"
    bl_idname = "NPRMenu"

    def draw(self, context):
        layout = self.layout
        
        layout.menu(NPRMenuLight.bl_idname)
        layout.menu(NPRMenuSceneInfo.bl_idname)
        layout.menu(NPRMenuComponents.bl_idname)
        layout.menu(NPRMenuMixers.bl_idname)
        layout.menu(NPRMenuTexture.bl_idname)
        

        
def draw_nprmenu(self, context):
    layout = self.layout
    layout.menu(NPRMenu.__name__,text="ToonKit")
    
    
#------------------------------- PREFERENCES ------------------------------------
class NPRPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    filepath = bpy.props.StringProperty(
            name="Shaders Path",
            subtype='FILE_PATH',
            default = bpy.utils.user_resource('SCRIPTS', "addons") + "/toonkit/shaders/",
            )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "filepath")

        
#------------------------------- HANDLERS and UPDATE -------------------------------------------------
@persistent
def UpdateNPRNodes(scene):
    if scene.render.engine == 'CYCLES':
        # Scan materials to see if I have a custom node within any of the trees.
        for m in bpy.data.materials:
            if m.node_tree != None:
                for n in m.node_tree.nodes:
                    # Object Info
                    if n.bl_idname == NPRGetInfoNode.bl_idname or n.bl_idname == NPRGetSceneLightInfoNode.bl_idname:
                        if(n.evaluate()):
                            n.update()
        
        # Scan node groups to see if I have a custom node within any of the trees.
        for g in bpy.data.node_groups:
            for n in g.nodes:
                if n.bl_idname == NPRGetInfoNode.bl_idname or n.bl_idname == NPRGetSceneLightInfoNode.bl_idname:
                    if(n.evaluate()):
                        n.update()

# Update all shaders Path based on User Preference
@persistent
def load_handler(dummy):
    UpdateAllShadersPath()
    bpy.ops.npr.modal_timer_operator("INVOKE_DEFAULT")

class ModalTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "npr.modal_timer_operator"
    bl_label = "Toonkit Update"

    _timer = None

    def modal(self, context, event):
        """
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}
        """
        if event.type == 'TIMER':
            UpdateNPRNodes(context.scene);

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(1/60,window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
# SET ALL SHADERS TO INTERNAL -----------------------
class NPRSetAllShadersInternal(bpy.types.Operator):
    """ToonKit Set All Shaders Internal"""
    bl_idname = "npr.setshadersinternal"
    bl_label = "Set All Shaders Internal"

    def execute(self, context):
        SetAllShadersToInternal()
        return{"FINISHED"}

def SetAllShadersToInternal():
    # Scan materials to see if I have a custom node within any of the trees.
    for m in bpy.data.materials:
        if m.node_tree != None:
            for n in m.node_tree.nodes:
                if n.bl_static_type == "SCRIPT":
                    PackShader(n)
               
    
    # Scan node groups to see if I have a custom node within any of the trees.
    for g in bpy.data.node_groups:
        for n in g.nodes:
            if n.bl_static_type == "SCRIPT":
                PackShader(n)   

def PackShader(node):
    path = node.filepath
    name = os.path.basename(path)
    hasText = False
    textInternal = None
    for text in bpy.data.texts:
        if text.name == name:
            hasText = True
            textInternal = text
    
    if (not hasText):
        bpy.ops.text.open(filepath=path,  internal=True)
        
        # Find generated text
        for text in bpy.data.texts:
            if text.name == name:
                hasText = True
                textInternal = text
    
    node.mode = "INTERNAL"
    node.script = textInternal
    

def add_setallshaders(self, context):
    self.layout.separator()
    self.layout.operator(NPRSetAllShadersInternal.bl_idname,text="Toonkit Pack Shaders ")    

# HELP -------------------------------------------------- 
def add_help(self, context):
    self.layout.separator()
    self.layout.operator(NPROpenHelp.bl_idname,text="Toonkit Docs",icon='QUESTION')
    
class NPROpenHelp(bpy.types.Operator):
    """ Open the MotionTool Documentation """
    bl_idname = "npr.openhelp"
    bl_label = "Toonkit Open Docs"
        
    def execute(self,context):
        bpy.ops.wm.url_open(url="http://cogumelosoftworks.com/index.php/toonkit")
        return{"FINISHED"}
#------------------------------- REGISTERS ------------------------------------

def register():
    bpy.app.handlers.load_post.append(load_handler)
    bpy.utils.register_class(ModalTimerOperator)
    
    #bpy.app.handlers.scene_update_post.append(UpdateNPRNodes)
    
    bpy.utils.register_class(NPROpenHelp)
    # Append Help on Info
    bpy.types.TOPBAR_MT_help.append(add_help)
    
    bpy.utils.register_class(NPRPreferences)
    bpy.utils.register_class(NPRUpdateGlobalLineArt)
    
    bpy.utils.register_class(NPRLightSettingsPanel)
    bpy.utils.register_class(NPRWorldSettingsPanel)
    bpy.utils.register_class(NPRPanel)
    bpy.utils.register_class(NPR_GlobalSettings)
    bpy.utils.register_class(NPR_LightSettings)
    
    bpy.types.Light.NPRSettings = bpy.props.PointerProperty(type=NPR_LightSettings)
    bpy.types.Scene.NPRSettings = bpy.props.PointerProperty(type=NPR_GlobalSettings)
    
    bpy.utils.register_class(NPR_WorldSettings)
    bpy.types.World.NPRSettings = bpy.props.PointerProperty(type=NPR_WorldSettings)
    
    bpy.utils.register_class(NPRGetSceneLightInfoNode)
    bpy.utils.register_class(NPRGetSceneLightInfo)
    bpy.utils.register_class(NPRGetInfoNode)
    bpy.utils.register_class(NPRGetInfo)
    
    bpy.utils.register_class(NPRAO)
    bpy.utils.register_class(NPRRim)
    bpy.utils.register_class(NPRSpecularDir)
    bpy.utils.register_class(NPRSpecularPoint)
    bpy.utils.register_class(NPRGooch)
    bpy.utils.register_class(NPRDepth)
    
    bpy.utils.register_class(NPRSceneLight)
    bpy.utils.register_class(NPRShadowScene)
    bpy.utils.register_class(NPRShadowDir)
    bpy.utils.register_class(NPRShadowPoint)
    bpy.utils.register_class(NPRLightPoint)
    bpy.utils.register_class(NPRLightDir)
    
    bpy.utils.register_class(NPREasyToon)
    bpy.utils.register_class(NPRShadingScene)
    bpy.utils.register_class(NPRShadingDir)
    bpy.utils.register_class(NPRShadingPoint)
    
    
    bpy.utils.register_class(NPRProcTexHair)
    bpy.utils.register_class(NPRProcTexHalftone)
    bpy.utils.register_class(NPRSimplifyNormals)
    bpy.utils.register_class(NPRTextureMatcap)
    bpy.utils.register_class(NPRTextureSpriteSheet)
    bpy.utils.register_class(NPRTextureRamp2D)
    
    bpy.utils.register_class(NPRFXPaint)
    bpy.utils.register_class(NPRFXBlur)
    bpy.utils.register_class(NPRFXPixelize)

    bpy.utils.register_class(NPRLine2)
    bpy.utils.register_class(NPRLine)
    bpy.utils.register_class(NPRPMask)
    bpy.utils.register_class(NPRAddShader)
    bpy.utils.register_class(NPRMultiBlend)

    bpy.utils.register_class(NPRMenuShadow)
    bpy.utils.register_class(NPRMenuShading)
    bpy.utils.register_class(NPRMenuSceneInfo)
    bpy.utils.register_class(NPRMenuLight)
    bpy.utils.register_class(NPRMenuFullLight)
    
    bpy.utils.register_class(NPRMenuTextEffects)
    bpy.utils.register_class(NPRMenuPatterns)
    bpy.utils.register_class(NPRMenuTextMappers)
    bpy.utils.register_class(NPRMenuTexture)
    bpy.utils.register_class(NPRMenuPointLight)
    bpy.utils.register_class(NPRMenuDirLight)
    
    
    bpy.utils.register_class(NPRMenuComponents)
    bpy.utils.register_class(NPRMenuMixers)
    bpy.utils.register_class(NPRMenu)
    
    bpy.types.NODE_MT_add.append(draw_nprmenu)


def unregister():

    bpy.app.handlers.load_post.remove(load_handler)
    bpy.utils.unregister_class(ModalTimerOperator)
    
    bpy.utils.unregister_class(NPR_GlobalSettings)
    bpy.utils.unregister_class(NPR_LightSettings)
    
    bpy.utils.unregister_class(NPRPreferences)
    bpy.utils.unregister_class(NPROpenHelp)
    bpy.utils.unregister_class(NPRSetAllShadersInternal)
    
    bpy.utils.unregister_class(NPRUpdateGlobalLineArt)
    
    bpy.utils.unregister_class(NPRLightSettingsPanel)
    bpy.utils.unregister_class(NPRWorldSettingsPanel)
    bpy.utils.unregister_class(NPRPanel)
    bpy.utils.unregister_class(NPR_GlobalSettings)
    
    bpy.utils.unregister_class(NPRGetSceneLightInfoNode)
    bpy.utils.unregister_class(NPRGetSceneLightInfo)
    bpy.utils.unregister_class(NPRGetInfoNode)
    bpy.utils.unregister_class(NPRGetInfo)
    
    bpy.utils.unregister_class(NPRAO)
    bpy.utils.unregister_class(NPRRim)
    bpy.utils.unregister_class(NPRSpecularDir)
    bpy.utils.unregister_class(NPRSpecularPoint)
    bpy.utils.unregister_class(NPRGooch)
    bpy.utils.unregister_class(NPRDepth)
    
    bpy.utils.unregister_class(NPRShadingScene)
    bpy.utils.unregister_class(NPRShadingDir)
    bpy.utils.unregister_class(NPRShadingPoint)
    
    
    bpy.utils.unregister_class(NPRSceneLight)   
    bpy.utils.unregister_class(NPRShadowScene)    
    bpy.utils.unregister_class(NPRShadowDir)
    bpy.utils.unregister_class(NPRShadowPoint)
    bpy.utils.unregister_class(NPRLightPoint)
    bpy.utils.unregister_class(NPRLightDir)

    bpy.utils.unregister_class(NPRProcTexHair)
    bpy.utils.unregister_class(NPRProcTexHalftone)
    bpy.utils.unregister_class(NPRSimplifyNormals)
    bpy.utils.unregister_class(NPRTextureMatcap)
    bpy.utils.unregister_class(NPRTextureSpriteSheet)
    bpy.utils.unregister_class(NPRTextureRamp2D)
    
    bpy.utils.unregister_class(NPRFXPaint)
    bpy.utils.unregister_class(NPRFXBlur)
    bpy.utils.unregister_class(NPRFXPixelize)

    bpy.utils.unregister_class(NPRLine2)
    bpy.utils.unregister_class(NPRLine)
    bpy.utils.unregister_class(NPRPMask)
    bpy.utils.unregister_class(NPRAddShader)
    bpy.utils.unregister_class(NPRMultiBlend)
    
    bpy.utils.register_class(NPRMenuLight)
    bpy.utils.register_class(NPRMenuFullLight)
    
    bpy.utils.unregister_class(NPREasyToon)
    bpy.utils.unregister_class(NPRMenuShadow)
    bpy.utils.unregister_class(NPRMenuShading)
    bpy.utils.unregister_class(NPRMenuSceneInfo)
    
    bpy.utils.unregister_class(NPRMenuTextEffects)
    bpy.utils.unregister_class(NPRMenuPatterns)
    bpy.utils.unregister_class(NPRMenuTextMappers)
    bpy.utils.unregister_class(NPRMenuTexture)
    
    bpy.utils.unregister_class(NPRMenuPointLight)
    bpy.utils.unregister_class(NPRMenuDirLight)
    bpy.utils.unregister_class(NPRMenuComponents)
    bpy.utils.unregister_class(NPRMenuMixers)
    bpy.utils.unregister_class(NPRMenu)
    
    bpy.types.NODE_MT_add.remove(draw_nprmenu)

if __name__ == "__main__":
    register()

