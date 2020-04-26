import bpy
import ctypes
import math
from arnold import *
from .Options import *
from .Camera import *
from .Lights import *
from .Materials import *
from .Textures import *
from .Meshes import *

class Renderer(bpy.types.RenderEngine):
    # These three members are used by blender to set up the
    # RenderEngine; define its internal name, visible name and capabilities.
    bl_idname = 'BtoA'
    bl_label = 'Arnold'
    bl_use_preview = True
    global BtoARend
    global BtoABuckets

    scene = bpy.context.scene

    def _getPreviewMaterial(self,scene):
        objects_mats = {} 
        for obj in [ob for ob in scene.objects if ob.is_visible(scene) and not ob.hide_render]:
            if obj.type == 'MESH':
                for mat in obj.data.materials:
                    if mat is not None:
                        if not obj.name in objects_mats.keys(): objects_mats[obj] = [] 
                        objects_mats[obj].append(mat)
 
        PREVIEW_TYPE = None     # 'MATERIAL' or 'TEXTURE'
             
        # find objects that are likely to be the preview objects
        preview_objects = [o for o in objects_mats.keys() if o.name.startswith('preview')]
        if len(preview_objects) > 0: 
            PREVIEW_TYPE = 'MATERIAL'
        else:
            preview_objects = [o for o in objects_mats.keys() if o.name.startswith('texture')]
            if len(preview_objects) > 0: 
                PREVIEW_TYPE = 'TEXTURE'
             
        if PREVIEW_TYPE == None:
            return
             
        # TODO: scene setup based on PREVIEW_TYPE
             
        # find the materials attached to the likely preview object
        likely_materials = objects_mats[preview_objects[0]]
        if len(likely_materials) < 1: 
            print('no preview materials')
            return
             
        pm = likely_materials[0]
        return pm

    # This is the only method called by blender, in this example
    # we use it to detect preview rendering and call the implementation
    # in another method.
    def render(self, scene):
        global BtoARend
        BtoARend = self

        scale = scene.render.resolution_percentage / 100.0
        self.size_x = int(scene.render.resolution_x * scale)
        self.size_y = int(scene.render.resolution_y * scale)
 
        if scene.name == 'preview':
            self.render_preview(scene)
        else:
            self.render_scene(scene)

    # In this example, we fill the preview renders with a flat green color.
    def render_preview(self, scene):
        global BtoARend
        global BtoABuckets
        self.scene = scene
        #return

        AiBegin()
        #AiMsgSetConsoleFlags(AI_LOG_ALL)
        # Filter
        filter = AiNode(b"cook_filter")
        AiNodeSetStr(filter,b"name",b"outfilter")

        # Display
        output = AiNode(b"driver_display")
        AiNodeSetStr(output,b"name",b"outdriver")
        AiNodeSetPtr(output,b"callback",self.g_displayCallback)

        options = AiUniverseGetOptions()
        outStr= "%s %s %s %s"%("RGBA","RGBA","outfilter","outdriver")
        outs = AiArray(1, 1, AI_TYPE_STRING, outStr.encode('utf-8'))
        AiNodeSetArray(options,b"outputs",outs)
        
        AiNodeSetInt(options,b"xres",self.size_x)
        AiNodeSetInt(options,b"yres",self.size_y)
        AiNodeSetInt(options,b"AA_samples",2)
        AiNodeSetInt(options,b"GI_diffuse_depth",1)
        AiNodeSetInt(options,b"GI_glossy_depth",1)
        
        cam = AiNode(b"persp_camera")
        AiNodeSetPtr(options,b"camera",cam)
        # light 1
        li01 = AiNode(b"point_light")
        pos = AiArrayAllocate(1,1,AI_TYPE_POINT)
        AiArraySetPnt(pos,0,AtPoint(1,1,0)) 
        AiNodeSetArray(li01,b"position",pos)
        # light 2
        li02 = AiNode(b"point_light")
        pos = AiArrayAllocate(1,1,AI_TYPE_POINT)
        AiArraySetPnt(pos,0,AtPoint(-1,-0.2,0)) 
        AiNodeSetArray(li02,b"position",pos)

        # materials
        pm = self._getPreviewMaterial(scene)
        if pm == None:
            return
        materials = Materials(scene)
        mat = materials.writeMaterial(pm)
        
        floorMat = AiNode(b"standard")
        rwallMat = AiNode(b"standard")
        AiNodeSetRGB(rwallMat,b"Kd_color",1,0,0) 
        lwallMat = AiNode(b"standard")
        AiNodeSetRGB(lwallMat,b"Kd_color",0,0,1) 
        
        # sphere
        sp = AiNode(b"sphere")
        AiNodeSetPtr(sp,b"shader",mat)
        AiNodeSetPnt(sp,b"center",0,0,-2.75)
        
        # walls
        floor = AiNode(b"plane")
        AiNodeSetPnt(floor,b"point",0,-0.5,0)
        AiNodeSetVec(floor,b"normal",0,1,0)
        AiNodeSetPtr(floor,b"shader",floorMat)
        rwall = AiNode(b"plane")
        AiNodeSetPnt(rwall,b"point",-2.5,0,-3)
        AiNodeSetVec(rwall,b"normal",-0.75,0,-0.15)
        AiNodeSetPtr(rwall,b"shader",rwallMat)
        lwall = AiNode(b"plane")
        AiNodeSetPnt(lwall,b"point",2.5,0,-3)
        AiNodeSetVec(lwall,b"normal",0.75,0,-0.15)
        AiNodeSetPtr(lwall,b"shader",lwallMat)

        BtoABuckets = {}
        #res = AiRender(AI_RENDER_MODE_CAMERA)
        self.__DoProgressiveRender()
        BtoABuckets = {}
        AiEnd()

    # In this example, we fill the full renders with a flat blue color.
    def render_scene(self, scene):
        global BtoABuckets
        self.scene = scene
     
        AiBegin()
        AiMsgSetConsoleFlags(AI_LOG_WARNINGS)
        
        # Filter
        filter = AiNode(b"cook_filter")
        AiNodeSetStr(filter,b"name",b"outfilter")

        # Display
        output = AiNode(b"driver_display")
        AiNodeSetStr(output,b"name",b"outdriver")
        AiNodeSetPtr(output,b"callback",self.g_displayCallback)
        # Options
        options = Options(self)
        options.setOutput("outfilter","outdriver",outType="RGBA")
        options.writeOptions()
        # Camera
        camera = Camera(self)
        camera.writeCamera()
        options.setCamera(camera.ArnoldCamera)

        # Lights
        lights = Lights()
        lights.writeLights()

        # textures
        textures = Textures(self.scene)
        textures.writeTextures()

        # Material
        materials = Materials(self.scene,textures)
        materials.writeMaterials()
        
        # Meshes
        meshes = Meshes(scene,materials)
        meshes.writeMeshes()

        BtoABuckets = {}
        if (scene.BtoA.enable_progressive):
            self.__DoProgressiveRender()
        else:
            res = AiRender(AI_RENDER_MODE_CAMERA)
        AiASSWrite(b"/tmp/.ass/everything.ass", AI_NODE_ALL, False);    
        BtoABuckets = {}
        AiEnd()

    # Callback for Arnold display driver
    def ArnoldDisplayCallback(x, y, width, height, buffer, data):
        global BtoARend
        global BtoABuckets

        self = BtoARend
        result = self.begin_result(x,
                                   self.size_y - y - height,
                                   width,height)
        layer = result.layers[0]
        if buffer:
            bucket = []
            row = []
            pixels = ctypes.cast(buffer, POINTER(AtUInt8))
            # Here we write the pixel values to the RenderResult
            for i in range(0,width*height*4,4):
                r = pixels[i]
                g = pixels[i+1]
                b = pixels[i+2]
                a = pixels[i+3]
                pixelColor = [r/255,g/255,b/255,a/255]
                row.append(pixelColor)
            
            for i in range(0,len(row),width):
                qq = row[i:i+width]
                qq.reverse()
                bucket.extend(qq)

            bucket.reverse()
            BtoABuckets["%s%s"%(x,y)]=bucket
            layer.rect = bucket
        else:
            size = width * height
            try:
                bucket = BtoABuckets["%s%s"%(x,y)]
            except:
                bucket = [[0,0,0,1]] * size

            edge = [0.5,0.25,0.25,1]
            if self.scene.name !="preview":
                for i in range(0,size,width*2): 
                    bucket[i] = edge
                    bucket[i+width - 1] = edge
                for i in [0,size - width]:
                    for j in range(i,i+width,2):
                        bucket[j] = edge

            layer.rect = bucket
        
        self.end_result(result)
        
    g_displayCallback = AtDisplayCallBack(ArnoldDisplayCallback)

    def __DoProgressiveRender(self):
        '''Handles the rendering of progressive refinement'''
        options = AiUniverseGetOptions()
        sampleLevel = AiNodeGetInt(options,b"AA_samples")
        smin = min(self.scene.BtoA.progressive_min, sampleLevel)
        smax = max(sampleLevel, smin)

        samples = [s for s in range(smin, smax + 1) if s != 0 and (s <= 1 or s == smax)]
        sminval = smin
        samples=[]
        while sminval != 0:
            samples.append(sminval)
            sminval = int(math.ceil(sminval*0.5))
        if smax != 0:
            samples.append(smax)
        res = AI_SUCCESS
        for i in samples:
            AiNodeSetInt(options,b"AA_samples", i)
            res = AiRender(AI_RENDER_MODE_CAMERA)

            #self.renderFinished.emit(self.renderInterrupted)

            #if res != AI_SUCCESS or self.restartRequested:
            #    break

        # Make sure the original values are restored in case of render interruption
        AiNodeSetInt(options,b"AA_samples", sampleLevel)

        return res

# registering and menu integration
def register():
    bpy.utils.register_class(Renderer)
 
# unregistering and removing menus
def unregister():
    bpy.utils.unregister_class(Renderer)
 


