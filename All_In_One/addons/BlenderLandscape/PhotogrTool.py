import bpy
import os
from .functions import *


#class CAMERA_PH_presets(Menu):
#    bl_label = "cameras presets"
#    preset_subdir = "ph_camera"
#    preset_operator = "script.execute_preset"
#    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_GAME'}
#    draw = Menu.draw_preset




class VIEW3D_OT_tex_to_material(bpy.types.Operator):
    """Create texture materials for images assigned in UV editor"""
    bl_idname = "view3d.tex_to_material"
    bl_label = "Texface Images to Material/Texture (Material Utils)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        if context.selected_editable_objects:
            tex_to_mat()
            return {'FINISHED'}
        else:
            self.report({'WARNING'},
                        "No editable selected objects, could not finish")
            return {'CANCELLED'}


class ToolsPanel5(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
#    bl_context = "objectmode"
    bl_category = "3DSC"
    bl_label = "Photogrammetry tool"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        cam_ob = None
        cam_ob = scene.camera

        if scene.render.engine != 'BLENDER_RENDER':
            row = layout.row()
            row.label(text="Please, activate BI engine !")
        elif cam_ob is None:
            row = layout.row()
            row.label(text="Please, add a Cam to see tools here")
            
        else:
            obj = context.object
            obj_selected = scene.objects.active
            cam_cam = scene.camera.data
            row = layout.row()
            row.label(text="Set up scene", icon='RADIO')
            row = layout.row()
            self.layout.operator("isometric.scene", icon="RENDER_REGION", text='Isometric scene')
            self.layout.operator("canon6d.scene", icon="RENDER_REGION", text='CANON 6D scene')
            self.layout.operator("nikond3200.scene", icon="RENDER_REGION", text='NIKON D3200 scene')
            if scene.objects.active:
                if obj.type in ['MESH']:
                    pass
                elif obj.type in ['CAMERA']:
                    row = layout.row()
                    row.label(text="Set selected cams as:", icon='RENDER_STILL')
                    self.layout.operator("nikond320018mm.camera", icon="RENDER_REGION", text='Nikon d3200 18mm')
                    self.layout.operator("canon6d35mm.camera", icon="RENDER_REGION", text='Canon6D 35mm')
                    self.layout.operator("canon6d24mm.camera", icon="RENDER_REGION", text='Canon6D 24mm')
                    self.layout.operator("canon6d14mm.camera", icon="RENDER_REGION", text='Canon6D 14mm')
                    row = layout.row()
                    row.label(text="Visual mode for selected cams:", icon='NODE_SEL')
                    self.layout.operator("better.cameras", icon="NODE_SEL", text='Better Cams')
                    self.layout.operator("nobetter.cameras", icon="NODE_SEL", text='Disable Better Cams')
                    row = layout.row()
                    row = layout.row()
                else:
                    row = layout.row()
                    row.label(text="Please select a mesh or a cam", icon='OUTLINER_DATA_CAMERA')
 
            row = layout.row()
            row.label(text="Painting Toolbox", icon='TPAINT_HLT')
            row = layout.row()
            row.label(text="Folder with undistorted images:")
            row = layout.row()
            row.prop(context.scene, 'BL_undistorted_path', toggle = True)
            row = layout.row()

            if cam_ob is not None:
                row.label(text="Active Cam: " + cam_ob.name)
                self.layout.operator("object.createcameraimageplane", icon="IMAGE_COL", text='Photo to camera')
                row = layout.row()
                row = layout.row()
                row.prop(cam_cam, "lens")
                row = layout.row()
                is_cam_ob_plane = check_children_plane(cam_ob)
#                row.label(text=str(is_cam_ob_plane))
                if is_cam_ob_plane:
                    if obj.type in ['MESH']:
                        row.label(text="Active object: " + obj.name)
                        self.layout.operator("paint.cam", icon="IMAGE_COL", text='Paint active from cam')
                else:
                    row = layout.row()
                    row.label(text="Please, set a photo to camera", icon='TPAINT_HLT')
                
                self.layout.operator("applypaint.cam", icon="IMAGE_COL", text='Apply paint')
                self.layout.operator("savepaint.cam", icon="IMAGE_COL", text='Save modified texs')
                row = layout.row()
            else:
                row.label(text="!!! Import some cams to start !!!")

class OBJECT_OT_IsometricScene(bpy.types.Operator):
    bl_idname = "isometric.scene"
    bl_label = "Isometric scene"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        set_up_scene(3000,3000,True)
        return {'FINISHED'}

class OBJECT_OT_Canon6Dscene(bpy.types.Operator):
    bl_idname = "canon6d.scene"
    bl_label = "Canon 6D scene"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        set_up_scene(5472,3648,False)
        return {'FINISHED'}
    
class OBJECT_OT_nikond3200scene(bpy.types.Operator):
    bl_idname = "nikond3200.scene"
    bl_label = "Nikon d3200 scene"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        set_up_scene(4512,3000,False)
        return {'FINISHED'}

class OBJECT_OT_nikond320018mm(bpy.types.Operator):
    bl_idname = "nikond320018mm.camera"
    bl_label = "Set as nikond3200 18mm"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selection:
            set_up_lens(obj,23.2,15.4,18)
        return {'FINISHED'}

class OBJECT_OT_Canon6D35(bpy.types.Operator):
    bl_idname = "canon6d35mm.camera"
    bl_label = "Set as Canon 6D 35mm"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selection:
            set_up_lens(obj,35.8,23.9,35)
        return {'FINISHED'}

class OBJECT_OT_Canon6D24(bpy.types.Operator):
    bl_idname = "canon6d24mm.camera"
    bl_label = "Set as Canon 6D 14mm"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selection:
            set_up_lens(obj,35.8,23.9,24)
        return {'FINISHED'}

class OBJECT_OT_Canon6D14(bpy.types.Operator):
    bl_idname = "canon6d14mm.camera"
    bl_label = "Set as Canon 6D 14mm"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selection:
            set_up_lens(obj,35.8,23.9,14.46)
        return {'FINISHED'}

class OBJECT_OT_BetterCameras(bpy.types.Operator):
    bl_idname = "better.cameras"
    bl_label = "Better Cameras"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        for cam in selection:
            cam.select = True
            cam.data.show_limits = True
            cam.data.clip_start = 0.5
            cam.data.clip_end = 4
            cam.scale[0] = 0.1
            cam.scale[1] = 0.1
            cam.scale[2] = 0.1
        return {'FINISHED'}

class OBJECT_OT_NoBetterCameras(bpy.types.Operator):
    bl_idname = "nobetter.cameras"
    bl_label = "Disable Better Cameras"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        selection = bpy.context.selected_objects
        bpy.ops.object.select_all(action='DESELECT')
        for cam in selection:
            cam.select = True
            cam.data.show_limits = False
        return {'FINISHED'}

#______________________________________________________________

class CreateCameraImagePlane(bpy.types.Operator):
    """Create image plane for camera"""
    bl_idname= "object.createcameraimageplane"
    bl_label="Camera Image Plane"
    bl_options={'REGISTER', 'UNDO'}
    def SetupDriverVariables(self, driver, imageplane):
        camAngle = driver.variables.new()
        camAngle.name = 'camAngle'
        camAngle.type = 'SINGLE_PROP'
        camAngle.targets[0].id = imageplane.parent
        camAngle.targets[0].data_path="data.angle"

        depth = driver.variables.new()
        depth.name = 'depth'
        depth.type = 'TRANSFORMS'
        depth.targets[0].id = imageplane
        depth.targets[0].data_path = 'location'
        depth.targets[0].transform_type = 'LOC_Z'
        depth.targets[0].transform_space = 'LOCAL_SPACE'

    def SetupDriversForImagePlane(self, imageplane):
        driver = imageplane.driver_add('scale',1).driver
        driver.type = 'SCRIPTED'
        self.SetupDriverVariables( driver, imageplane)
        #driver.expression ="-depth*math.tan(camAngle/2)*resolution_y*pixel_y/(resolution_x*pixel_x)"
        driver.expression ="-depth*tan(camAngle/2)*bpy.context.scene.render.resolution_y * bpy.context.scene.render.pixel_aspect_y/(bpy.context.scene.render.resolution_x * bpy.context.scene.render.pixel_aspect_x)"
        driver = imageplane.driver_add('scale',0).driver
        driver.type= 'SCRIPTED'
        self.SetupDriverVariables( driver, imageplane)
        driver.expression ="-depth*tan(camAngle/2)"

    # get selected camera (might traverse children of selected object until a camera is found?)
    # for now just pick the active object
        

    def createImagePlaneForCamera(self, camera):
        imageplane = None

        depth = 10
        
        cameraname = correctcameraname(camera.name)

        try:
            undistortedpath = bpy.context.scene.BL_undistorted_path
        except:
            raise Exception("Hey Buddy, you have to set the undistorted images path !")
            
        try:
            cam_texture = bpy.data.images.load(undistortedpath+cameraname)
        except:
            raise NameError("Cannot load image %s" % bpy.data.images.load(undistortedpath+cameraname))
        
        
        #create imageplane
        bpy.ops.mesh.primitive_plane_add()#radius = 0.5)
        imageplane = bpy.context.active_object
        
        imageplane.name = ("objplane_"+cameraname)
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='TOGGLE')
        bpy.ops.transform.resize( value=(0.5,0.5,0.5))
        bpy.ops.uv.smart_project(angle_limit=66,island_margin=0, user_area_weight=0)
        bpy.ops.uv.select_all(action='TOGGLE')
        bpy.ops.transform.rotate(value=1.5708, axis=(0,0,1) )
        bpy.ops.object.editmode_toggle()

        imageplane.location = (0,0,-depth)
        imageplane.parent = camera

        #calculate scale
        #REPLACED WITH CREATING EXPRESSIONS
        self.SetupDriversForImagePlane(imageplane)

        #setup material
        if( len( imageplane.material_slots) == 0 ):
            bpy.ops.object.material_slot_add()
            #imageplane.material_slots.
        bpy.ops.material.new()
        mat_index = len(bpy.data.materials)-1
        imageplane.material_slots[0].material = bpy.data.materials[mat_index]
        material =  imageplane.material_slots[0].material
        # if not returned by new use imgeplane.material_slots[0].material
        material.name = 'mat_imageplane_'+cameraname

        material.use_nodes = False

        activename = bpy.path.clean_name(bpy.context.scene.objects.active.name)

        bpy.context.object.data.uv_textures.active.data[0].image = cam_texture

        bpy.ops.view3d.tex_to_material()

        return {'FINISHED'}

    def execute(self, context):
#        camera = bpy.context.active_object #bpy.data.objects['Camera']
        scene = context.scene
        undistortedpath = bpy.context.scene.BL_undistorted_path
        cam_ob = bpy.context.scene.camera

        if not undistortedpath:
            raise Exception("Set the Undistort path before to activate this command")
        else:
            obj_exists = False
            for obj in cam_ob.children:
                if obj.name.startswith("objplane_"):
                    obj.hide = False
                    obj_exists = True
                    bpy.ops.object.select_all(action='DESELECT')
                    scene.objects.active = obj
                    obj.select = True
                    return {'FINISHED'}
            if obj_exists is False:
                camera = bpy.context.scene.camera
                return self.createImagePlaneForCamera(camera)

class OBJECT_OT_paintcam(bpy.types.Operator):
    bl_idname = "paint.cam"
    bl_label = "Paint selected from current cam"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        scene = context.scene
        undistortedpath = bpy.context.scene.BL_undistorted_path
        cam_ob = bpy.context.scene.camera

        if not undistortedpath:
            raise Exception("Set the Undistort path before to activate this command")
        else:
            for obj in cam_ob.children:
                if obj.name.startswith("objplane_"):
                    obj.hide = True
            bpy.ops.paint.texture_paint_toggle()
            bpy.context.space_data.show_only_render = True
            bpy.ops.image.project_edit()
            obj_camera = bpy.context.scene.camera
    
            undistortedphoto = undistortedpath+correctcameraname(obj_camera.name)
            cleanpath = bpy.path.abspath(undistortedphoto)
            bpy.ops.image.external_edit(filepath=cleanpath)

            bpy.context.space_data.show_only_render = False
            bpy.ops.paint.texture_paint_toggle()

        return {'FINISHED'}

class OBJECT_OT_applypaintcam(bpy.types.Operator):
    bl_idname = "applypaint.cam"
    bl_label = "Apply paint"
    bl_options = {"REGISTER"}

    def execute(self, context):
        bpy.ops.paint.texture_paint_toggle()
        bpy.ops.image.project_apply()
        bpy.ops.paint.texture_paint_toggle()
        return {'FINISHED'}


