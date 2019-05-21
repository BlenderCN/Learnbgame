bl_info = {
    "name": "Camera Image Plane",
    "author": "Christophe Seux",
    "version": (1, 0),
    "blender": (2, 78, 0),
    "description": "Adds an image plane on the active camera",
    "warning": "",
    "wiki_url": "",
    "category": "User",
    }

import bpy
import os

from bpy.types import Menu, Panel, UIList, PropertyGroup
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, BoolVectorProperty, PointerProperty


def create_empty(name,parent):
    plane =bpy.data.objects.new(name,None)
    plane.empty_draw_type ='IMAGE'
    plane.empty_image_offset=[-0.5,-0.5]
    plane.empty_draw_size=1.0
        
    if not plane.get('_RNA_UI') :
        plane['_RNA_UI'] = {}
    
    if not parent.get('_RNA_UI') :
        parent['_RNA_UI'] = {}
    
    plane["transparency"] = 0.75
    plane["offset_X"] = 0.0
    plane["thumbnail_offset_X"] = -3.35
    plane["offset_Y"] = 0.0
    plane["thumbnail_offset_Y"] = 3.35
    plane["size"] = 1.0
    plane["thumbnail_size"] = 0.33
    plane["thumbnail"] = False
    parent["distance"] = 8.0
    
    plane['_RNA_UI']["transparency"] = {'description': '', 'max': 1.0, 'soft_max': 1.0, 'soft_min': 0.0, 'min': 0.0}
    plane['_RNA_UI']["offset_X"] = {'description': '', 'max': 100.0, 'soft_max': 100.0, 'soft_min': -100.0, 'min': -100.0}
    plane['_RNA_UI']["thumbnail_offset_X"] = {'description': '', 'max': 100.0, 'soft_max': 100.0, 'soft_min': -100.0, 'min': -100.0}
    plane['_RNA_UI']["offset_Y"] = {'description': '', 'max': 100.0, 'soft_max': 100.0, 'soft_min': -100.0, 'min': -100.0}
    plane['_RNA_UI']["thumbnail_offset_Y"] = {'description': '', 'max': 100.0, 'soft_max': 100.0, 'soft_min': -100.0, 'min': -100.0}
    plane['_RNA_UI']["size"] = {'description': '', 'max': 100.0, 'soft_max': 100.0, 'soft_min': -100.0, 'min': -100.0}
    plane['_RNA_UI']["thumbnail_size"] = {'description': '', 'max': 100.0, 'soft_max': 100.0, 'soft_min': 100.0, 'min': -100.0}
    plane['_RNA_UI']["thumbnail"] = {'description': '', 'max': 1.0, 'soft_max': 1.0, 'soft_min': 0.0, 'min': 0.0}
    parent['_RNA_UI']["distance"] = {'description': '', 'max': 500.0, 'soft_max': 500.0, 'soft_min': 0.0, 'min': 0.0}
      
    return (plane)
    
def SetupDriver(plane,empty,image,camera):
    
    drivers = plane.driver_add('delta_scale',-1)
    
    def var_cam(d):
        camAngle = d.variables.new()
        camAngle.name = 'camAngle'
        camAngle.type = 'SINGLE_PROP'
        camAngle.targets[0].id = camera
        camAngle.targets[0].data_path="data.angle"
    
    def var_depth(d):
        depth = d.variables.new()
        depth.name = 'depth'
        depth.type = 'LOC_DIFF'
        depth.targets[0].id = empty    
        depth.targets[1].id = camera  
        depth.targets[0].data_path = 'location'
        depth.targets[0].transform_type = 'LOC_Z'
        
    for d in drivers :
        d.driver.type = 'SCRIPTED'
        d.driver.expression ="depth*tan(camAngle/2)*2"
        
        var_cam(d.driver)
        var_depth(d.driver)     
    
    driver = plane.driver_add('delta_location',0).driver
    driver.type= 'SCRIPTED'
    driver.use_self =True
    driver.expression ='(self["thumbnail_offset_X"] if self["thumbnail"] else self["offset_X"])*0.1*depth*tan(camAngle/2)*2'
    var_cam(driver)
    var_depth(driver)    
    
    imageRatio = bpy.context.scene.render.resolution_y/bpy.context.scene.render.resolution_x
    driver = plane.driver_add('delta_location',1).driver
    driver.type= 'SCRIPTED'
    driver.use_self =True
    driver.expression ='(self["thumbnail_offset_Y"] if self["thumbnail"] else self["offset_Y"])*0.1*depth*tan(camAngle/2)*2*%s'%round(imageRatio,3)
    var_cam(driver)
    var_depth(driver)   
    
    driver = plane.driver_add('color',3).driver
    driver.type= 'SCRIPTED'
    driver.use_self =True
    driver.expression ='self["transparency"]'
        
    driver = plane.driver_add('empty_draw_size',-1).driver
    driver.type= 'SCRIPTED'
    driver.use_self =True
    driver.expression ='self["thumbnail_size"] if self["thumbnail"] else self["size"]'

    driver = plane.parent.driver_add('delta_location',2).driver
    driver.type= 'SCRIPTED'
    driver.use_self =True
    driver.expression ='-self["distance"]'    

    
class imagePlane_thumbnail(bpy.types.Operator):
    """Toogle between expand and thumbnail"""
    bl_idname = "image_plane.thumbnail"
    bl_label = "Image Plane Thumbnail"
    bl_options = {'REGISTER', 'UNDO'}
    property = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'CAMERA' or context.space_data.region_3d.view_perspective == 'CAMERA')

    def execute(self, context):
        imagePlane = self.property 
        imagePlaneOb = bpy.context.scene.objects.get(imagePlane)
        
        if imagePlaneOb["thumbnail"] ==True :
            imagePlaneOb["thumbnail"] =0
        else :
            imagePlaneOb["thumbnail"] =1

        imagePlaneOb.location=imagePlaneOb.location

        return {'FINISHED'}


class cameraImagePlane_list(PropertyGroup):
    imagePlane = StringProperty(name="imagePlane")

 
    
class cameraImagePlane(PropertyGroup):
    show_image = BoolProperty(name="Show Image", default=True)
    show_expanded = BoolProperty(name="Show Expanded", default=True)
    thumbnail = BoolProperty(name="Thumbnail", default=False)
    
    #imagePlane_list = CollectionProperty(type=cameraImagePlane_list)

    
class removeCreateCameraImagePlane(bpy.types.Operator):
    """Remove mesh plane"""
    bl_idname = "remove.camera_image_plane"
    bl_label = "Remove Camera Image Plane"
    bl_options = {'REGISTER', 'UNDO'}
    property = bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'CAMERA' or context.space_data.region_3d.view_perspective == 'CAMERA')

    def execute(self, context):
        imagePlane = self.property 
        imagePlaneList = bpy.context.object.data.CameraImagePlane.get("cameraImagePlane_list")
        
        if not imagePlaneList :
            imagePlaneList = []
        
        imagePlaneList.remove(imagePlane)
        bpy.context.object.data.CameraImagePlane["cameraImagePlane_list"] = imagePlaneList
        
        bpy.context.scene.objects.unlink(bpy.context.scene.objects.get(imagePlane))
        bpy.context.scene.objects.unlink(bpy.context.scene.objects.get(imagePlane+'_target'))
        
        bpy.data.objects.remove(bpy.data.objects.get(imagePlane))
        bpy.data.objects.remove(bpy.data.objects.get(imagePlane+'_target'))
        
        return {'FINISHED'}
        
        
class addCameraImagePlane(bpy.types.Operator):
    """Add mesh plane(s) from image files with the appropiate aspect ratio"""
    bl_idname = "add.camera_image_plane"
    bl_label = "Add Camera Image Plane"
    bl_options = {'REGISTER', 'UNDO'}
    
    property = bpy.props.StringProperty()
    # -----------
    # File props.
    files = CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN', 'SKIP_SAVE'})

    directory = StringProperty(maxlen=1024, subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})
    
    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'CAMERA' or context.space_data.region_3d.view_perspective == 'CAMERA')

    def execute(self, context):
       
        import_list, directory = self.generate_paths()
            
        if context.object.type == 'CAMERA' :
            camera = bpy.context.object
        else :
            camera = bpy.context.scene.camera
        
        cameraName = camera.name.replace('.','_').replace('-','_')
        
        offset = 8
        
        for path in import_list :
            image =0
            for i in bpy.data.images :
                if i.filepath == directory+path :
                    image = i
                    break
            
            if image ==0 :
                image = bpy.data.images.load(directory+path)
                image.name = os.path.splitext(path)[0].replace('.','_').replace('-','_')[0:30]
            
            imagePlaneName = "IP_%s_%s"%(cameraName,image.name)
            
            if bpy.data.objects.get(imagePlaneName) :
                bpy.data.objects.get(imagePlaneName).name+="_copy"
            if bpy.data.objects.get(imagePlaneName+'_target') :
                bpy.data.objects.get(imagePlaneName+'_target').name+="_copy"
                
            empty = bpy.data.objects.new(imagePlaneName+'_target', None)
            bpy.context.scene.objects.link(empty)
            empty.parent = camera
                
            plane = create_empty(imagePlaneName,empty)          
            bpy.context.scene.objects.link(plane)
           
            plane.data = image
            plane.data.update()
            plane.show_transparent = True
            plane.image_user.frame_duration = image.frame_duration
            plane.image_user.use_auto_refresh = True
            plane.image_user.frame_start = bpy.context.scene.frame_start
            plane.parent = empty

            empty.empty_draw_size = 0.02
            empty.empty_draw_type = 'SINGLE_ARROW'
            empty.lock_location=[True,True,False]
            empty.hide_select = True
            
            bpy.context.scene.update()
            
            SetupDriver(plane,empty,image,camera)
                                    
            imagePlane=plane.name
                        
            bpy.context.scene.update()
            
            imagePlaneList = bpy.context.object.data.CameraImagePlane.get("cameraImagePlane_list")
            
            if not imagePlaneList :
                imagePlaneList = []
            
            imagePlaneList.append(imagePlane)
            bpy.context.object.data.CameraImagePlane["cameraImagePlane_list"] = imagePlaneList

        return {'FINISHED'}

    def invoke(self, context, event):
        #self.update_extensions(context)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def generate_paths(self):
        return (fn.name for fn in self.files), self.directory

        
class CameraMoviePlanePanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Image Plane"
    bl_context = "scene"
        
    @classmethod
    def poll(self, context):
        return (context.object and context.object.type == 'CAMERA' or context.space_data.region_3d.view_perspective == 'CAMERA')

    def draw_header(self, context):
        view = context.space_data

        self.layout.prop(view, "show_background_images", text="")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        
        row.operator("add.camera_image_plane", emboss=True, text="Add Camera Plane",icon="RENDER_RESULT")
        
        if context.object.type == 'CAMERA' :
            camera = bpy.context.object.data
        else :
            camera = bpy.context.scene.camera.data
            
        if camera.CameraImagePlane.get('cameraImagePlane_list'):
            for imagePlane in camera.CameraImagePlane['cameraImagePlane_list'] :
                box = layout.box()
                col = box.column()
                row = col.row(align=True)
                
                #eval("context.scene.%s"%imagePlane)
                imagePlaneProp = camera.CameraImagePlane
                imagePlaneOb = bpy.data.objects.get(imagePlane)
                
                if imagePlaneProp.show_expanded == True :
                    show_icon = "TRIA_DOWN"
                else :
                    show_icon = "TRIA_RIGHT"            
                
                row.prop(imagePlaneProp,"show_expanded" ,emboss=False, text="",icon = show_icon)
                row.label(text = imagePlane)

                if imagePlaneOb["thumbnail"] == 0 :
                    show_icon = "FULLSCREEN_EXIT"
                else :
                    show_icon = "FULLSCREEN_ENTER"
                
                row.operator("image_plane.thumbnail",emboss=False,text="",icon = show_icon).property = imagePlane
                
                if imagePlaneProp.show_image == True :
                    show_icon = "RESTRICT_VIEW_OFF"
                else :
                    show_icon = "RESTRICT_VIEW_ON"
                    
                row.prop(imagePlaneOb,"hide" ,emboss=False, text="",icon = show_icon)
                row.operator("remove.camera_image_plane", emboss=False, text="",icon = "X").property = imagePlane
                
                if imagePlaneProp.show_expanded == True :
                    row = col.row()
                    row.prop(imagePlaneOb.parent,'["distance"]',text = "Distance")

                    row = col.row()
                    if imagePlaneOb["thumbnail"] ==False:
                        row.prop(imagePlaneOb,'["size"]',text = "Size")
                        row = col.row()
                        row.prop(imagePlaneOb,'["offset_X"]',text = "X")
                        row.prop(imagePlaneOb,'["offset_Y"]',text = "Y")                    
                    
                    else :
                        row.prop(imagePlaneOb,'["thumbnail_size"]',text = "Size")
                        row = col.row()
                        row.prop(imagePlaneOb,'["thumbnail_offset_X"]',text = "X")
                        row.prop(imagePlaneOb,'["thumbnail_offset_Y"]',text = "Y")
                    
                    if imagePlaneOb.data.frame_duration>1 :
                        row = col.row()
                        row.prop(imagePlaneOb.image_user,"frame_start",text = "Start")
                    
                    row = col.row()
                    row.prop(imagePlaneOb,'["transparency"]',text = "Transparency",slider=True)


def register():
    
    bpy.utils.register_module(__name__)
    bpy.types.Camera.CameraImagePlane = bpy.props.PointerProperty(type=cameraImagePlane)

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Camera.CameraImagePlane 



if __name__ == "__main__":  
    register()  
    
