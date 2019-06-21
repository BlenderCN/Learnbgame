# =============================================================================
# (C) Copyright 2014
# Australian Centre for Microscopy & Microanalysis
# The University of Sydney
# =============================================================================
# File:   blend/space.py
# Date:   2014-07-01
# Author: Varvara Efremova
#
# Description:
# Blender API wrapper for scene/world/etc general operations
# =============================================================================

import bpy

# === Render ===
def camera_add(name, origin=(0, 0, 0), clip_start=0.1, clip_end=1000.0):
    """Create camera"""
    # Create and general object options
    cam = bpy.data.cameras.new(name+"_cam")
    obj = bpy.data.objects.new(name, cam)
    obj.location = origin
    obj.show_name = True

    # Lens options
    cam.clip_start = clip_start
    cam.clip_end = clip_end

    # Link to scene and set active
    scene = bpy.context.scene
    scene.objects.link(obj)
    scene.objects.active = obj
    obj.select = True
    scene.camera = obj
    scene.update()
    return obj

def lamp_add(name, origin=(0.0, 0.0, 0.0), rotation_euler=(0.0, 0.0, 0.0), ltype='POINT', color=(0.0, 0.0, 0.0), view_align=True):
    """Create lamp"""
    # Create and general object options
    lamp = bpy.data.lamps.new(name+"_lamp", ltype)
    obj = bpy.data.objects.new(name, lamp)
    obj.location = origin
    obj.rotation_euler = rotation_euler
    obj.show_name = True

    # Lamp options
    lamp.color = color

    # Link to scene and set active
    scene = bpy.context.scene
    scene.objects.link(obj)
    scene.objects.active = obj
    obj.select = True
    scene.update()
    return obj

def camera_add_to_view(name, clip_start=0.1, clip_end=1000.0):
    """Create camera positioned at current view"""
    cam = camera_add(name=name, clip_start=clip_start, clip_end=clip_end)
    # Move camera to current view
    bpy.ops.view3d.camera_to_view()
    return cam

def camlamp_add_to_view(ltype='SUN', lcolor=(1.0, 1.0, 1.0), clip_start=0.1, clip_end=1000.0):
    """TEMP: Create camera and lamp positioned at current view"""
    cam = camera_add(name="Camera", clip_start=clip_start, clip_end=clip_end)
    # Move camera to current view
    bpy.ops.view3d.camera_to_view()

    # FIXME TEMP add lamp at camera's position and rotation
    loc = cam.location
    rot = cam.rotation_euler
    lamp = lamp_add(name="Lamp", origin=loc, rotation_euler=rot, ltype=ltype, color=lcolor)
    return cam, lamp

# === Camera/lamp manipulation ===
def camera_set_active(cam):
    """Set cam to active camera"""
    scene = bpy.context.scene
    scene.camera = cam

def camera_position_on():
    """Turn View3D viewpoint camera positioning on"""
    bpy.context.region_data.view_perspective = 'CAMERA'
    bpy.context.space_data.lock_camera = True

def camera_position_off():
    """Turn View3D viewpoint camera positioning off"""
    bpy.context.space_data.lock_camera = False
    bpy.context.region_data.view_perspective = 'PERSP'

# === Groups ===
def group_add_object(grp, obj):
    """Add obj to group grp"""
    grp.objects.link(obj)

def group_add(groupname):
    """Create new group"""
    grp = bpy.data.groups.new(groupname)
    return grp

def group_get(groupname):
    """Returns first group matching groupname"""
    for grp in bpy.data.groups:
        if groupname == grp.name:
            return grp
    return False

# === Scene/view maniuplations ===
def delete_all():
    """ Delete all objects/meshes in scene """
    # Gather list of items of interest
    candidate_list = [item.name for item in bpy.data.objects if item.type == "MESH"]

    # Select them only
    for object_name in candidate_list:
        bpy.data.objects[object_name].select = True

    # Remove all selected
    bpy.ops.object.delete()

    # Remove the meshes, they have no users anymore.
    for item in bpy.data.meshes:
        bpy.data.meshes.remove(item)

# === viewpoint maniuplation ===
def view_selected_pattern(exp):
    """Select objects with name matching exp, and view"""
    bpy.ops.object.select_pattern(pattern=exp, case_sensitive=False, extend=False)
    bpy.ops.view3d.view_selected()

def view_selected_group(gname):
    """Select objects in gname group, and view"""
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_same_group(group=gname)
    bpy.ops.view3d.view_selected()

def get_area(name='VIEW_3D'):
    """Return View3D space object"""
    def areas_tuple():
        res = {}
        count = 0
        for area in bpy.context.screen.areas:
            res[area.type] = count
            count += 1
        return res

    areas = areas_tuple()
    view3d = bpy.context.screen.areas[areas[name]].spaces[0]
    return view3d









# ====== SCRAAAAAPS ==============
# === POINTCLOUD STUFF ===
#def obj_view_wireframe(obj):
#    """Draw object as wireframe in View3D"""
#    obj.show_wire = True
#    obj.draw_type = 'WIRE'
#def create_material_wire(name, mtype='WIRE', color=(1.0, 1.0, 1.0), emit=0.0, alpha=1.0):
#    """Create basic wireframe material"""
#    mat = bpy.data.materials.new(name)
#    mat.type = mtype
#
#    mat.diffuse_color = color
#    mat.diffuse_shader = 'LAMBERT'
#    mat.diffuse_intensity = 1.0
#
#    mat.specular_color = color
#    mat.specular_shader = 'COOKTORR'
#    mat.specular_intensity = 0.5
#
#    mat.emit = emit
#
#    mat.alpha = alpha
#    mat.ambient = 1
#    return mat








# === SCRAPS ===
# FIXME FIXME FIXME
def add_lamp_to_view(name, ltype='SUN', color=(0.0, 0.0, 0.0)):
    # FIXME a bit hacky here
    # Creates camera, sets camera to view,
    # gets its location and rotation and applies these to lamp

    # --- Previous code attempting to use rv3d properties ---
    ### TODO test if this works if mouse is outside of view3d??
    #v3d = get_area('VIEW_3D')
    #rv3d = v3d.region_3d
    ###
    #### calculate position to place lamp at
    #loc = rv3d.view_location.copy()            # Vector location
    #rot = rv3d.view_rotation.to_euler()        # Quaternion rotation
    #mat = rv3d.view_matrix         # 4x4 rotation matrix
    #pmat = rv3d.perspective_matrix
    #loc, rot, sca = (pmat+mat).decompose()
    # -------------------------------------------------------
    #bpy.ops.object.lamp_add(type=lamptype, location=loc, rotation=rot)
    #obj = bpy.context.object
    #obj.name = name
    #return obj

    scene = bpy.context.scene

    # Camera hacks ...
    bpy.ops.object.camera_add()
    cam_obj = bpy.context.object
    bpy.ops.view3d.camera_to_view()

    # Add lamp at current camera location and view rotation
    bpy.ops.object.lamp_add(type=lamptype, location=cam_obj.location, view_align=True)
    lamp_obj = bpy.context.object
    lamp_obj.name = name
    lamp_data = lamp_obj.data
    lamp_data.name = name+"_data"

    # Create lamp datablock, create obj, link to scene
    #lamp_data = bpy.data.lamps.new(name=name+"_data", type='SUN')
    #lamp_object = bpy.data.objects.new(name=name, object_data=lamp_data)
    #scene.objects.link(lamp_object)

    #lamp_object.location = cam_obj.location
    #lamp_object.rotation = rv3d.view_rotation.to_euler()

    # Remove camera
    #bpy.ops.object.select_all(action='DESELECT')
    #cam_obj.select = True
    #scene.objects.active = cam_obj
    #bpy.ops.object.delete()

    # Make active
    lamp_obj.select = True
    scene.objects.active = lamp_obj

    return lamp_obj

# FIXME is this needed??
def set_cursor_pivot_to_center(points):
    center = np.mean(points, axis=0)

    # Move cursor to centre of mesh and set pivot point around cursor
    def areas_tuple():
        res = {}
        count = 0
        for area in bpy.context.screen.areas:
            res[area.type] = count
            count += 1
        return res
    areas = areas_tuple()
    view3d = bpy.context.screen.areas[areas['VIEW_3D']].spaces[0]

    view3d.pivot_point='CURSOR'
    view3d.cursor_location = tuple(center)



