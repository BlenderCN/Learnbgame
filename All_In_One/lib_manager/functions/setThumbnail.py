import bpy

def set_thumbnail() :
    ob = bpy.context.scene.objects.active

    res_x = bpy.context.scene.render.resolution_x
    res_y = bpy.context.scene.render.resolution_y
    only_render = bpy.context.space_data.show_only_render
    lock_camera = bpy.context.space_data.lock_camera_and_layers
    percentage = bpy.context.scene.render.resolution_percentage
    hide_objects = {}

    for obj in bpy.context.scene.objects :
        if obj !=  ob.proxy_group and obj != ob:
            hide_objects[obj.name] = obj.hide
            obj.hide =True



    if bpy.context.space_data.local_view :
        bpy.ops.view3d.localview()


    cameraData = bpy.data.cameras.new('poseLib_thumbnail')
    camera = bpy.data.objects.new('poseLib_thumbnail',cameraData)
    bpy.context.scene.objects.link(camera)


    cameraData.lens = 85

    camera.select = True
    bpy.context.scene.objects.active = camera
    bpy.context.space_data.lock_camera_and_layers = False
    bpy.context.space_data.camera = camera

    bpy.context.space_data.lock_camera = True

    bpy.ops.view3d.camera_to_view()

    #camLoc = tuple(camera.location)
    #camRot = tuple(camera.rotation_euler)

    #bpy.ops.view3d.viewnumpad

    bpy.context.scene.render.resolution_x = 512
    bpy.context.scene.render.resolution_y = 512
    bpy.context.scene.render.resolution_percentage = 100


    bpy.context.space_data.show_only_render = True




    #bpy.context.space_data.region_3d.view_perspective ='CAMERA'

    #blenderbpy.ops.view3d.viewnumpad

    #bpy.context.space_data.lock_camera = True
    bpy.context.scene.objects.active = ob

    #camera.location = camLoc
    #camera.rotation_euler = camRot

    ob.PoseLibCustom['camera'] = camera.name
    ob.PoseLibCustom['res_x'] = res_x
    ob.PoseLibCustom['res_y'] = res_y
    ob.PoseLibCustom['only_render'] = only_render
    ob.PoseLibCustom['lock_camera'] = lock_camera
    ob.PoseLibCustom['percentage'] = percentage
    ob.PoseLibCustom['hide_objects'] = hide_objects
