import bpy

def createLayerArray(layer_numbers, total_layers):
    array = [False] * total_layers
    for i in layer_numbers:
        array[i] = True
    return array

def createNewBone(object, new_bone_name, parent_name, parent_connected, head, tail, roll, layer_number):
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    
    if new_bone_name in object.data.edit_bones:
        return
    
    new_edit_bone = object.data.edit_bones.new(new_bone_name)    
    new_edit_bone.use_connect = parent_connected
    new_edit_bone.parent = object.data.edit_bones[parent_name]    
    new_edit_bone.use_inherit_rotation = True
    new_edit_bone.use_local_location = True
    new_edit_bone.use_inherit_scale = False
    
    new_edit_bone.head = head
    new_edit_bone.tail = tail
    new_edit_bone.roll = roll
    
    new_edit_bone.layers = createLayerArray([layer_number], 32)    
    new_edit_bone.use_deform = False
    new_edit_bone.show_wire = True

def copyDeformationBone(object, new_bone_name, deform_bone_name, parent_name, parent_connected, 
        layer_number):
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    deform_edit_bone = object.data.edit_bones[deform_bone_name]
    createNewBone(object, new_bone_name, parent_name, parent_connected, 
        deform_edit_bone.head.copy(), deform_edit_bone.tail.copy(), deform_edit_bone.roll, 
        layer_number)
        
def addCopyConstraint(object, pose_bone, constraint_type, name, influence, subtarget):
    if name not in pose_bone.constraints:
        constraint = pose_bone.constraints.new(constraint_type)    
        constraint.name = name
        constraint.influence = influence
        constraint.target = object
        constraint.subtarget = subtarget
        return constraint

def addLimitConstraint(pose_bone, constraint_type, name, influence, x = [False], y = [False],
        z = [False]):
    if name not in pose_bone.constraints:
        constraint = pose_bone.constraints.new(constraint_type)    
        constraint.name = name
        constraint.influence = influence
        
        if x[0]:
            constraint.use_limit_x = True
            constraint.min_x = x[1]
            constraint.max_x = x[2]

        if y[0]:
            constraint.use_limit_y = True
            constraint.min_y = y[1]
            constraint.max_y = y[2]
            
        if z[0]:
            constraint.use_limit_z = True
            constraint.min_z = z[1]
            constraint.max_z = z[2]
        
        return constraint    
    
def addDriver(source, property, target, dataPath, negative = False):
    driver = source.driver_add(property).driver

    var = driver.variables.new()
    var.type = 'SINGLE_PROP'
    var.name = 'x'
    var.targets[0].id = target
    var.targets[0].data_path = dataPath

    if not negative:
        driver.expression = var.name
    else:
        driver.expression = "1 - " + var.name        
        
def createGizmo(context, name, mesh_data, gizmos_parent):
    if name in bpy.data.objects:
        return
     
    verts = mesh_data[0]
    edges = mesh_data[1]
    
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, edges, [])
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    context.scene.objects.link(obj)
    obj.layers = createLayerArray([19], 20)
    obj.parent = gizmos_parent    
    
def setCustomShape(object, bone_name, gizmo_name, scale):
    bpy.ops.object.mode_set(mode='POSE', toggle=False)
    
    pose_bone = object.pose.bones[bone_name]
    gizmo_obj = bpy.data.objects[gizmo_name]
    
    pose_bone.custom_shape = gizmo_obj
    pose_bone.use_custom_shape_bone_size = True
    pose_bone.custom_shape_scale = scale
    