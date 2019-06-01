import bpy

class Initialize_Camera_Properties:
    lastCamera = None
    def update_checker(scene):
        currentCam = scene.camera
        if currentCam.data.use_camera_res:
            lastCam = Initialize_Camera_Properties.lastCamera
            if lastCam == None:
                lastCam = currentCam
                print ('Setting camera')
            if lastCam != currentCam:
                Initialize_Camera_Properties.update_manager(scene)
            Initialize_Camera_Properties.lastCamera = currentCam
    
    def update_manager(scene):
        if scene.camera.data.res_type == 'res_type_paper':
            Initialize_Camera_Properties.update_camera(scene)
        else:
            Initialize_Camera_Properties.update_camera_px(scene)
    
    def update_camera(scene):
        render = scene.render
        camera = scene.camera.data
        width = camera.width
        height = camera.height
        modelScale = camera.mod_scale
        paperScale = camera.paper_scale
        
        ppi = camera.res
        
        if camera.use_camera_res:
            render.resolution_percentage = 100
            render.resolution_x = width *  ppi * 39.3701
            render.resolution_y = height * ppi * 39.3701
        
            if width > height:
                camera.ortho_scale = (render.resolution_x/ppi/39.3701) * (modelScale/paperScale)
            else:
                camera.ortho_scale = (render.resolution_y/ppi/39.3701) * (modelScale/paperScale)
    
    def update_camera_px(scene):
        render = scene.render
        camera = scene.camera.data
        width_px = camera.width_px
        height_px = camera.height_px
        modelScale = camera.mod_scale
        pixelScale = camera.pixel_scale
        percentScale = camera.percent_scale
        
        if camera.use_camera_res:
            render.resolution_x = width_px
            render.resolution_y = height_px
            render.resolution_percentage = percentScale
        
            if width_px > height_px:
                camera.ortho_scale = (render.resolution_x) * (modelScale/(pixelScale*(percentScale/100)))
            else:
                camera.ortho_scale = (render.resolution_y) * (modelScale/(pixelScale*(percentScale/100)))
     
    def update(self,context):
        Initialize_Camera_Properties.update_manager(context.scene)
        

    def add_camera_to_render_name(scene):
        filename = scene.render.Filename
        cameraName = scene.Camera.data.name
        scene.render.Filename = filename + '_' + cameraName

   
    #Width Property
    bpy.types.Camera.width =  bpy.props.FloatProperty(
        name = "Width", 
        description = "Camera Width in Units", 
        unit = 'LENGTH',
        default = 0.43, 
        min = 0.0, 
        update = update
        )
    
    #Height Property
    bpy.types.Camera.height = bpy.props.FloatProperty(
        name = "Height", 
        description = "Camera Height in Units", 
        unit = 'LENGTH', 
        default = 0.28, 
        min = 0.0, 
        update = update
        )
        
    #Width_px Property
    bpy.types.Camera.width_px =  bpy.props.IntProperty(
        name = "X", 
        description = "Camera Width in Pixels", 
        subtype = 'PIXEL',
        default = 1920, 
        min = 4, 
        update = update,
        step = 100
        )
        
    #Width_px Property
    bpy.types.Camera.height_px =  bpy.props.IntProperty(
        name = "Y", 
        description = "Camera Height in Pixels", 
        subtype = 'PIXEL',
        default = 1080, 
        min = 4, 
        update = update,
        step = 100
        )
    
    #Percent Scale Property
    bpy.types.Camera.percent_scale =  bpy.props.IntProperty(
        name = "Percent Scale", 
        description = "Percentage scale for render resolution", 
        subtype = 'PERCENTAGE',
        default = 50, 
        min = 1,
        max = 100,
        update = update,
        step = 100
        )
        
    #PPI Property
    bpy.types.Camera.res = bpy.props.IntProperty(
        name = "res_prop", 
        description = "Resolution in Pixels Per Inch", 
        subtype = 'FACTOR', 
        default = 150, 
        min = 1, 
        soft_max = 600, 
        soft_min =50,
        update = update, 
        step = 1, 
        )
    
    #Model Length
    bpy.types.Camera.mod_scale = bpy.props.FloatProperty(
        name = "mod_scale", 
        description = "Length on Model", 
        unit = 'LENGTH', 
        default = .1, 
        min = 0.0, 
        update = update
        )
    
    #Paper Length
    bpy.types.Camera.paper_scale = bpy.props.FloatProperty(
        name = "paper_scale",
        description = "Length on Paper",
        unit = 'LENGTH',
        default = 1, min = 0.0, 
        update = update
        )
        
    #Pixel Length
    bpy.types.Camera.pixel_scale = bpy.props.IntProperty(
        name = "Pixel Scale",
        description = "Number of Pixels",
        subtype = 'PIXEL',
        default = 100, 
        min = 0, 
        update = update
        )
    
    #Enable/Disable
    bpy.types.Camera.use_camera_res = bpy.props.BoolProperty(
        name = "use_camera_scale",
        description = "Enable Per Camera Render Settings",
        update = update
        )
    
    #Resolution Type
    bpy.types.Camera.res_type = bpy.props.EnumProperty(
        items=[
            ('res_type_paper','Paper','Define Resolution by Paper Size and Pixels Per Inch'), 
            ('res_type_pixels','Pixels','Blender Standard, Define Resolution in Pixels')
            ],
        name ="Resolution Type",
        description = 'Method For Defining Render Size', 
        default = 'res_type_pixels',
        update = update
        #options = 'ENUM_FLAG'
        )
        
    #CameraName As Render Suffix
    bpy.types.Camera.add_camera_name = bpy.props.BoolProperty(
        name = "Add Camera Name to Filename",
        description = "Add the camera name to the end of output file name",
        )