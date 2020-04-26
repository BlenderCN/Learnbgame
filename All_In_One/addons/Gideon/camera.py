import bpy, mathutils
from math import *
from ctypes import *

#Converts Blender's camera to a Gideon representation
def convert(bl_camera_obj, scene):
    camera = bl_camera_obj.data

    #compute camera axes
    camera_tfm = bl_camera_obj.matrix_world.to_3x3()
    x_axis = camera_tfm * mathutils.Vector((1.0, 0.0, 0.0))
    y_axis = camera_tfm * mathutils.Vector((0.0, 1.0, 0.0))
    z_axis = camera_tfm * mathutils.Vector((0.0, 0.0, 1.0))
    print("Location:", bl_camera_obj.location)
    print("X Axis:", x_axis)
    print("Y Axis:", y_axis)
    print("Z Axis:", z_axis)
    
    print("Render:", scene.render.resolution_x, scene.render.resolution_y)
    print("CamToWorld:", bl_camera_obj.matrix_world)

    z_flip = mathutils.Matrix.Scale(-1.0, 4, (0, 0, 1))
    camera_to_world = bl_camera_obj.matrix_world * z_flip
    
    pixel_scale = scene.render.resolution_percentage * 0.01
    x_pixels = floor(pixel_scale * scene.render.resolution_x)
    y_pixels = floor(pixel_scale * scene.render.resolution_y)

    #view plane computation

    xratio = x_pixels * scene.render.pixel_aspect_x
    yratio = y_pixels * scene.render.pixel_aspect_y
    xaspect = 1.0
    yaspect = 1.0
    aspect = 1.0
    h_fit = True
    sensor_size = 0.0

    if (camera.sensor_fit == 'AUTO'):
        h_fit = (xratio > yratio)
        sensor_size = camera.sensor_width
    elif (camera.sensor_fit == 'HORIZONTAL'):
        h_fit = True
        sensor_size = camera.sensor_width
    else:
        h_fit = False
        sensor_size = camera.sensor_height

    if h_fit:
        aspect = xratio / yratio
        xaspect = aspect
        yaspect = 1.0
    else:
        aspect = yratio / xratio
        xaspect = 1.0
        yaspect = aspect
        
    right = xaspect
    left = -xaspect
    bottom = -yaspect
    top = yaspect
    
    #right = view_frame[0].x
    #left = view_frame[2].x
    #top = view_frame[0].y
    #bottom = view_frame[2].y
    #depth = view_frame[0].z

    #-- end

    fov = 2.0 * atan((0.5 * sensor_size) / camera.lens / aspect)
    
    view_frame = camera.view_frame(scene)
    print("View Frame:", view_frame)
    print("FOV:", fov)
    
    #compute the transform
    dcam = camera.clip_end - camera.clip_start
    persp = mathutils.Matrix(((1.0, 0.0, 0.0, 0.0),
                              (0.0, 1.0, 0.0, 0.0),
                              (0.0, 0.0, camera.clip_end / dcam, (-camera.clip_end*camera.clip_start) / dcam),
                              (0.0, 0.0, 1.0, 0.0)))
    
    inv_angle = 1.0 / tan(0.5 * fov)
    p_scale = mathutils.Matrix(((inv_angle, 0.0, 0.0, 0.0),
                                (0.0, inv_angle, 0.0, 0.0),
                                (0.0, 0.0, 1.0, 0.0),
                                (0.0, 0.0, 0.0, 1.0)))
    camera_to_screen = p_scale * persp
    
    ndc_to_raster = mathutils.Matrix.Scale(x_pixels, 4, (1, 0, 0)) * mathutils.Matrix.Scale(y_pixels, 4, (0, 1, 0))
    raster_to_ndc = ndc_to_raster.inverted()

    dx = right - left
    dy = top - bottom
    screen_to_ndc = mathutils.Matrix.Scale(1.0 / dx, 4, (1, 0, 0)) * mathutils.Matrix.Scale(1.0 / dy, 4, (0, 1, 0)) * mathutils.Matrix.Translation((-left, -bottom, 0.0))
    
    screen_to_raster = ndc_to_raster * screen_to_ndc
    raster_to_screen = screen_to_raster.inverted()
    
    print("Render Size:", x_pixels, y_pixels)
    
    screen_to_camera = camera_to_screen.inverted()
    raster_to_camera = screen_to_camera * raster_to_screen
    
    camera_to_raster = screen_to_raster * camera_to_screen

    print("Perspective:", persp)
    print("Scale:", p_scale)
    print("NDC -> Raster:", ndc_to_raster)
    print("Screen -> NDC:", screen_to_ndc)
    print("Screen -> Raster:", screen_to_raster)
    print("Raster -> Sceen:", raster_to_screen)
    print("Raster -> Camera:", raster_to_camera)
    print("Transformed:", raster_to_camera * mathutils.Vector((100, 210, 0)))
    print("Transformed Again:", camera_to_raster * raster_to_camera * mathutils.Vector((100, 210, 0)))
    print("Raster -> NDC:", raster_to_ndc * mathutils.Vector((2, 3, 0)))
    print("Raster -> NDC:", raster_to_ndc * mathutils.Vector((319, 230, 0)))
    print("Raster -> Camera:", raster_to_camera * mathutils.Vector((0, 120, 0)))
    print("Raster -> Camera:", raster_to_camera * mathutils.Vector((320, 120, 0)))
    
    #print("Transformed:", camera_to_screen * mathutils.Vector((left, 0.0, 0.0)))
    #print("Transformed:", camera_to_screen * mathutils.Vector((right, 0.0, 0.0)))
    #print("Transformed:", camera_to_screen * mathutils.Vector((0.0, bottom, 0.0)))
    #print("Transformed:", camera_to_screen * mathutils.Vector((0.0, top, 0.0)))

    c_matrix = 16 * c_float
    cam_to_world_arr = c_matrix()
    raster_to_cam_arr = c_matrix()
    arr_idx = 0
    for row_idx in range(4):
        for col_idx in range(4):
            cam_to_world_arr[arr_idx] = camera_to_world[row_idx][col_idx]
            raster_to_cam_arr[arr_idx] = raster_to_camera[row_idx][col_idx]
            arr_idx += 1
            
    return {
        'resolution'       : [x_pixels, y_pixels],
        'clip'             : [camera.clip_start, camera.clip_end],
        'camera_to_world'  : cam_to_world_arr,
        'raster_to_camera' : raster_to_cam_arr
        }
