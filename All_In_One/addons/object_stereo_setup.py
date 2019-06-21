# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    'name': 'Create Stereo Setup',
    'description': 'Create Stereo Setup for selected camera.',
    'location': 'View3D > Shift+Alt+T',
    'author': 'Bartek Skorupa',
    'version': (1, 0),
    'blender': (2, 6, 4),
    "category": "Learnbgame",
    "warning": "",
    }

import bpy

def globals():
    global C
    global D
    global O
    global scn
    global suffix_l
    global suffix_r
    global suffix_np
    global suffix_fp
    global suffix_mfp
    global mat_name
    global mat_color
    global near_scale
    global far_scale
    global near_loc_z
    global far_loc_z
    global min_far_loc_z
    global near_max_z
    global bracket
    global fp_np_ratio
    global fp_influence

    C = bpy.context
    D = bpy.data
    O = bpy.ops
    scn = C.scene
    suffix_l = ' L'
    suffix_r = ' R'
    suffix_np = ' Near Plane'
    suffix_fp = ' Far Plane'
    suffix_mfp = ' min Far'
    mat_name = 'STEREO_NF_DISPLAY'
    mat_color = [0.6, 0.7, 1.0]
    near_scale = [3.2, 1.8, 1.0]
    far_scale = [6.4, 3.6, 1.0]
    near_loc_z = -2.0
    far_loc_z = -5.0
    min_far_loc_z = -5.0
    near_max_z = -0.0001
    bracket = 15.0
    fp_np_ratio = 2.0
    fp_influence = 1.0


def doit(cam_l):  # create stereo setup
    globals()
    # create material for near and far planes if doesn't exist
    material = create_material()
    
    # add objects
    cam_r = add_cam_r(cam_l)  # add right camera (cam_l needed to get data)
    near = add_near(material)  # add near plane and assign material to it
    far = add_far(near)  # add far plane (duplicate near and offset)
    min_far = add_min_far()  # add empty as minimum far plane
    
    # name objects
    name_objects(cam_l, cam_r, near, far, min_far)  # name all objects basing on cam_l name
        
    # set parents
    for ob in [cam_r, near, far, min_far]:
        ob.parent = cam_l
    
    # drivers
    add_min_far_drivers(min_far, cam_r, near, far)  # location Z to be no smaller than ratio*nearLocZ
    add_cam_r_drivers(cam_r, cam_l, near, min_far)  # for location X and for camera shift to position depth bracket so that near sits on screen

    # clean scene
    O.object.select_all(action = 'DESELECT')
    scn.objects.active = cam_r
    cam_r.select = True
    
    return {'FINISHED'}


def undoit(object):  # delete all elements of stereo setup
    globals()
    cam_l = None
    basename = get_basename(object.name)
    if (basename + suffix_l == object.name):
        cam_l = object
    elif (object.parent != None):
        parent = object.parent
        basename = get_basename(parent.name)
        if (basename + suffix_l == parent.name):
            cam_l = parent
    if (cam_l != None):
        cam_l.select = False
        for ob in cam_l.children:
            for s_name in [basename + suffix_r, basename + suffix_np, basename + suffix_fp, basename + suffix_mfp]:
                if ob.name == s_name:
                    ob.select = True
                    break
        O.object.delete()
        scn.objects.active = cam_l
        cam_l.select = True
    
    return {'FINISHED'}


def create_material():  # material for Near and Far Plane
    no_material = True
    for mat in D.materials:
        if mat.name == mat_name:
            no_material = False
            material = mat
            break
    if no_material:
        material = D.materials.new(name = mat_name)
        material.diffuse_color = mat_color
        material.diffuse_intensity = 1.0
        material.specular_intensity = 0.0
        material.use_transparency = True
        material.transparency_method = 'Z_TRANSPARENCY'
        material.alpha = 0.7

    return material

    
def add_cam_r(cam_l):  # add right camera with copy of cam_l data and custom properties
    O.object.add(type = 'CAMERA')
    cam_r = C.object
    # lock cam_r transforms
    for i in [0, 1, 2]:
        cam_r.lock_location[i] = True
        cam_r.lock_rotation[i] = True
        cam_r.lock_scale[i] = True
    # data
    data = cam_r.data
    data.name = cam_l.data.name + suffix_r
    data.lens = cam_l.data.lens
    data.sensor_width = cam_l.data.sensor_width
    # add custom properties for cam_r
    cam_r['FP/NP Minimum Ratio'] = fp_np_ratio
    cam_r['Depth Bracket'] = bracket
    cam_r['FP Influence'] = fp_influence
    cam_r['_RNA_UI'] = {
        'Depth Bracket': {
            'min': 0.0,
            'max': 10000.0,
            'description': 'Desired Depth Bracket in pixels'
            },
        'FP/NP Minimum Ratio': {
            'min': 1.001,
            'max': 100.0,
            'description': 'Minimum Ratio between destances of Near and Far planes. Set to 2 to avoid too big Stereo Base in shallow scenes'
            },
        'FP Influence': {
            'min': 0.0,
            'max': 1.0,
            'description': 'Influence of Far Plane. Set to 0 if Far Plane is in infinity'
            },
        }

    return cam_r


def add_near(material):  # Add Near Plane with material and Limit Location constraint
    O.mesh.primitive_plane_add()
    near = C.object
    # transforms
    near.location.z = near_loc_z
    near.scale = near_scale
    # lock transforms
    near.lock_location[0] = True
    near.lock_location[1] = True
    for i in [0, 1, 2]:
        near.lock_rotation[i] = True
    # material
    O.object.material_slot_add()
    near.data.materials[0] = material
    # show transparency in viewport
    near.show_transparent = True
    #hide render
    near.hide_render = True
    # add limit location constraint to prevent location of 0.0 (avoid dividing by 0.0 in drivers)
    O.object.constraint_add(type = 'LIMIT_LOCATION')
    const = near.constraints[0]
    const.use_max_z = True
    const.max_z = near_max_z
    const.owner_space = 'LOCAL'
    const.use_transform_limit = True

    return near

    
def add_far(near):  # Add Far Plane - duplicate Near and clear Limit Location constraint
    O.object.duplicate()
    far = C.object
    far.location.z = far_loc_z
    far.scale = far_scale
    # clear constraint
    O.object.constraints_clear()

    return far


def add_min_far():
    O.object.add()
    min_far = C.object
    min_far.location.z = min_far_loc_z  # set location.z to value different than 0 to avoid ZeroDivisionError after setting drivers
    # lock transforms
    for i in [0, 1, 2]:
        min_far.lock_location[i] = True
        min_far.lock_rotation[i] = True
        min_far.lock_scale[i] = True
    
    return min_far

    
def name_objects(cam_l, cam_r, near, far, min_far):
    name = cam_l.name
    basename = get_basename(name)
    if name == basename:
        cam_l.name = basename + suffix_l  # add suffix_L if not already added
    cam_r.name = basename + suffix_r  # name right camera
    near.name = basename + suffix_np  # name near plane
    far.name = basename + suffix_fp  # name far plane
    min_far.name = basename + suffix_mfp  # name min_far
    
    return


def get_basename(name):
    if name[-2:len(name)] == suffix_l:
        basename = name[0:-2]
    else:
        basename = name

    return basename


def add_min_far_drivers(min_far, cam_r, near, far):
    driver = min_far.driver_add('location', 2).driver
    
    props = [
        ['N', near, 'location.z'],
        ['F', far, 'location.z'],
        ['min_ratio', cam_r, '["FP/NP Minimum Ratio"]']
        ]
    
    for prop in props:
        var = driver.variables.new()
        var.name = prop[0]
        var.type = 'SINGLE_PROP'
        var.targets[0].id = prop[1]
        var.targets[0].data_path = prop[2]
    driver.expression = '(N*min_ratio <= F)*(N*min_ratio) + (N*min_ratio > F)*F'
    driver.show_debug_info = True
    
    return


def add_cam_r_drivers(cam_r, cam_l, near, min_far):
    d1 = cam_r.driver_add('location', 0).driver
    d2 = cam_r.data.driver_add('shift_x').driver
    d3 = cam_r.data.driver_add('shift_y').driver
    d4 = cam_r.data.driver_add('sensor_width').driver
    d5 = cam_r.data.driver_add('lens').driver
    
    drivers = [d1, d2, d3, d4, d5]
    
    props = [
        [
        ['Bracket', cam_r, '["Depth Bracket"]'],
        ['Factor', cam_r, '["FP Influence"]'],
        ['Sensor', cam_l, 'data.sensor_width'],
        ['Lens', cam_l, 'data.lens'],
        ['Near', near, 'location.z'],
        ['Far', min_far, 'location.z'],
        ['-(Bracket / bpy.context.scene.render.resolution_x) * (Sensor / (Lens/Near - (Lens/Far)*Factor))'],
        ],[
        ['Base', cam_r, 'location.x'],
        ['Near', near, 'location.z'],
        ['Sensor', cam_l, 'data.sensor_width'],
        ['Lens', cam_l, 'data.lens'],
        ['R_Shiftx', cam_l, 'data.shift_x'],
        ['(Base / Sensor) * (Lens / Near) + R_Shiftx'],
        ],[
        ['Shifty', cam_l, 'data.shift_y'],
        ['Shifty']
        ],[
        ['Sensor_w', cam_l, 'data.sensor_width'],
        ['Sensor_w']
        ],[
        ['Lens', cam_l, 'data.lens'],
        ['Lens']
        ],
    ]

    for i, driver in enumerate(drivers):
        for prop in props[i]:
            if (len(prop) == 3):
                var = driver.variables.new()
                var.name = prop[0]
                var.type = 'SINGLE_PROP'
                var.targets[0].id = prop[1]
                var.targets[0].data_path = prop[2]
            else:
                driver.expression = prop[0]
        driver.show_debug_info = True
    
    return
    

class CreateStereoSetup(bpy.types.Operator):
    bl_idname = "object.create_stereo_setup"
    bl_label = "Create Stereo Setup"
    
    @classmethod
    def poll(cls, context):
        if bpy.context.object:
            return bpy.context.object.type == 'CAMERA'
    
    def execute(self, context):
        return doit(bpy.context.object)

class ClearStereoSetup(bpy.types.Operator):
    bl_idname = "object.clear_stereo_setup"
    bl_label = "Clear Stereo Setup"
    
    @classmethod
    def poll(cls, context):
        return bpy.context.object != None
    
    def execute(self, context):
        return undoit(bpy.context.object)

class StereoSetupMenu(bpy.types.Menu):
    bl_idname = "OBJECT_MT_stereo_setup"
    bl_label = "Stereo Setup"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("object.create_stereo_setup", text = "Create Stereo Setup")
        layout.operator("object.clear_stereo_setup", text = "Remove Stereo Setup")


addon_keymaps = []

def register():
    bpy.utils.register_module(__name__)
    km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name="Object Mode")
    kmi = km.keymap_items.new('wm.call_menu', 'T', 'PRESS', shift = True, alt = True)
    kmi.properties.name = 'OBJECT_MT_stereo_setup'
    addon_keymaps.append((km, kmi))

def unregister():
    bpy.utils.unregister_module(__name__)
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
	