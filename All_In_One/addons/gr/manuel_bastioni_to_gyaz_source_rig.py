import bpy
from bpy.types import Panel, Operator
from bpy.props import *
from mathutils import Vector, Euler, Quaternion
from math import radians, degrees
from mathutils.bvhtree import BVHTree

    
class Op_GYAZ_ManuelBastioniRigToGYAZSourceRig (bpy.types.Operator):
       
    bl_idname = "object.gyaz_bastion_to_gyaz_source_rig"  
    bl_label = "Manuel Bastioni Rig to GYAZ Source Rig"
    bl_description = ""
    
    #operator function
    def execute(self, context):
        
        """SETTINGS"""
        keep_breasts = True
        keep_twist_weights = True
        belly_locators = True

        arm_bend = 45
        finger_bend = -15

        scene = bpy.context.scene
        obj = bpy.context.object
        meshes = obj.children
        
        #gyaz stamp
        obj.data['GYAZ_rig'] = True
        
        #remove all modifiers except for armature modifier
        for mesh in meshes:
            for m in mesh.modifiers:
                if m.type != 'ARMATURE':
                    mesh.modifiers.remove (m)  
        
        #################################################################################
        #raycast function
        my_tree = BVHTree.FromObject(scene.objects[meshes[0].name], bpy.context.depsgraph)
            
        rig = obj
        
        def cast_ray_from_bone (start_bone, head_tail, ebone_pbone, direction, distance):        
            #set ray start and direction
            if ebone_pbone == 'ebone':    
                bpy.ops.object.mode_set (mode='EDIT')
                if head_tail == 'head':
                    ray_start = rig.data.edit_bones[start_bone].head
                elif head_tail == 'tail':
                    ray_start = rig.data.edit_bones[start_bone].tail
            elif ebone_pbone == 'pbone':
                bpy.ops.object.mode_set (mode='POSE')
                if head_tail == 'head':
                    ray_start = rig.pose.bones[start_bone].head
                elif head_tail == 'tail':
                    ray_start = rig.pose.bones[start_bone].tail
            ray_direction = direction
            ray_distance = 10
            
            #cast ray
            hit_loc, hit_nor, hit_index, hit_dist = my_tree.ray_cast (ray_start, ray_direction, ray_distance)
            
            return (hit_loc, hit_nor, hit_index, hit_dist)
        
        
        #################################################################################                

        if obj.type == 'ARMATURE':
            rig = obj
            
            sides = [
                ['_L', '_l'],
                ['_R', '_r']
                ]

            names_central = [
                ['root', 'root'],
                ['pelvis', 'hips'],
                ['spine01', 'spine_1'],
                ['spine02', 'spine_2'],
                ['spine03', 'spine_3'],
                ['neck', 'neck'],
                ['head', 'head']
                ]
                
            names_side = [
                ['clavicle', 'shoulder'],
                ['upperarm', 'upperarm'],
                ['lowerarm', 'forearm'],
                ['hand', 'hand'],
                ['thigh', 'thigh'],
                ['calf', 'shin'],
                ['foot', 'foot'],
                ['toes', 'toes'],
        #        ['breast', 'spring_chest']
                ]
                
            finger_names = [
                ['thumb', 'thumb'],
                ['index', 'pointer'],
                ['middle', 'middle'],
                ['ring', 'ring'],
                ['pinky', 'pinky']
                ]
                
            counters = [
                ['01', '_1'],
                ['02', '_2'],
                ['03', '_3']
                ]
                
            twist_names = ['upperarm', 'lowerarm', 'thigh', 'calf']
            new_twist_names = ['upperarm', 'forearm', 'thigh', 'shin']
            
            metacarpal_names = ['index', 'middle', 'ring', 'pinky']
            
            extra_names = ['root']
            
            breast_names = ['breast', 'spring_chest'] # old name, new name
            
            
            bpy.ops.object.mode_set (mode='OBJECT')           
            
            
            """WEIGHTS"""
            
            def merge_and_remove_weight (weight_to_merge, weight_to_merge_to):    
                for mesh in meshes:
                    bpy.ops.object.select_all (action='DESELECT')
                    mesh.select_set (True)
                    bpy.context.view_layer.objects.active = mesh
                    #mix weights if mesh has those weights
                    vgroups = mesh.vertex_groups
                    if vgroups.get (weight_to_merge) != None:
                        if vgroups.get (weight_to_merge_to) == None:
                            vgroups.new (name=weight_to_merge_to)
                        m = mesh.modifiers.new (type='VERTEX_WEIGHT_MIX', name="Mix Twist Weight")
                        m.mix_mode = 'ADD'
                        m.mix_set = 'ALL'
                        m.vertex_group_a = weight_to_merge_to
                        m.vertex_group_b = weight_to_merge
                        bpy.ops.object.modifier_apply (apply_as='DATA', modifier="Mix Twist Weight")
                        #delete surplus weights
                        vgroups = mesh.vertex_groups
                        vgroups.remove (vgroups[weight_to_merge])
            
            
            if keep_twist_weights == False:   
                for old_side, new_side in sides:
                    for name in twist_names:
                        weight_to_merge = name+'_twist'+old_side
                        weight_to_merge_to = name+old_side
                                    
                        merge_and_remove_weight (weight_to_merge, weight_to_merge_to)
                
            for old_side, new_side in sides:
                for name in metacarpal_names:
                    weight_to_merge = name+'00'+old_side
                    weight_to_merge_to = 'hand'+old_side
                    
                    merge_and_remove_weight (weight_to_merge, weight_to_merge_to)
            
            if keep_breasts == False:        
               for old_side, new_side in sides:
                    weight_to_merge = breast_names[0]+old_side
                    weight_to_merge_to = 'spine03'
                
                    merge_and_remove_weight (weight_to_merge, weight_to_merge_to)
                          
            
            for mesh in meshes:
                mesh.data.update ()
            
            bpy.ops.object.select_all (action='DESELECT')
            rig.select_set (True)
            bpy.context.view_layer.objects.active = rig
            bpy.ops.object.mode_set (mode='EDIT')
            ebones = rig.data.edit_bones

            
            """RENAME"""       
                
            for old_name, new_name in names_central:
                ebones[old_name].name = new_name

            for old_side, new_side in sides:
                for old_name, new_name in names_side:
                    ebones[old_name+old_side].name = new_name+new_side
            
            for old_side, new_side in sides:        
                for old_finger, new_finger in finger_names:
                    for old_counter, new_counter in counters:
                        ebones[old_finger+old_counter+old_side].name = new_finger+new_counter+new_side
                        
            for old_side, new_side in sides:
                ebone = ebones[breast_names[0]+old_side].name = breast_names[1]+new_side
                
            for old_side, new_side in sides:
                for index, name in enumerate (twist_names):
                    ebone = ebones[name+'_twist'+old_side]
                    ebone.name = 'twist_1_'+new_twist_names[index]+new_side
                        
            """REMOVE BONES"""
            
            for old_side, new_side in sides:
                for name in new_twist_names:
                    ebone = ebones['twist_1_'+name+new_side]
                    ebones.remove (ebone)
            
            for old_side, new_side in sides:
                for name in metacarpal_names:
                    ebone = ebones[name+'00'+old_side]
                    ebones.remove (ebone)
            
            for name in extra_names:
                ebone = ebones[name]
                ebones.remove (ebone)
                
            if keep_breasts == False:
                for old_side, new_side in sides:
                    ebone = ebones[breast_names[1]+new_side]
                    ebones.remove (ebone)
                
                
            """POSITION BONES"""
            
            ebones = rig.data.edit_bones
            
            for ebone in ebones:
                ebone.use_connect = False
            
#            for old_side, new_side in sides:        
#                foot = ebones['foot'+new_side]
#                foot.tail = foot.head[0], foot.tail[1], foot.head[2]
#                
#                toes = ebones['toes'+new_side]
#                toes.head = foot.head[0], toes.head[1], toes.head[2]
#                toes.tail = foot.head[0], toes.tail[1], toes.head[2]
#                
#                foot.roll = 0
#                toes.roll = 0
                
            ebones['hips'].head = (ebones['thigh_l'].head + ebones['thigh_r'].head) / 2
            ebones['spine_3'].tail = ebones['neck'].head
                
            for old_side, new_side in sides:
                ebone = ebones['shoulder'+new_side]
                ebone.head = ebone.head[0], ebone.tail[1], ebone.tail[2]
                
            ebone = ebones['head']
            ebone.tail = ebone.head[0], ebone.head[1], ebone.tail[2]
            
            spine_names = ['hips', 'spine_1', 'spine_2', 'spine_3', 'neck', 'head']
            
            for name in spine_names:
                ebones[name].roll = 0
                
            for old_side, new_side in sides:
                ebone = ebones['hand'+new_side]
                roll = ebone.roll
                print (degrees(roll))
                ebone.tail = ( ebone.tail - ebone.head ) + ebone.tail
                ebone.roll = roll
          
                
            """REST POSE"""
            
            bpy.ops.object.mode_set (mode='POSE')
            
            pbones = rig.pose.bones
            
            for old_side, side in sides:
                pbone = pbones['forearm'+side]
                
                eu = Euler ((radians(arm_bend), 0, 0), 'XYZ')
                qu = eu.to_quaternion ()
                pbone.rotation_quaternion = qu
                
                for old_name, name in finger_names:
                    for n in range (1, 4):
                        pbone = pbones[name+'_'+str(n)+side]
                        if 'thumb_1' not in pbone.name:
                        
                            eu = Euler ((radians(finger_bend), 0, 0), 'XYZ')
                            qu = eu.to_quaternion ()
                            pbone.rotation_quaternion = qu
            
            
            if len (meshes) > 0:
                for mesh in meshes:
                    bpy.ops.object.mode_set (mode='OBJECT')
                    bpy.ops.object.select_all (action='DESELECT')
                    mesh.select_set (True)
                    bpy.context.view_layer.objects.active = mesh                    
                                
                    #remove shape keys
                    try:
                        bpy.ops.object.shape_key_remove (all=True)
                    except:
                        'do nothing'
                    
                    #apply armature modifier
                    old_mesh = mesh.data
                    new_mesh = mesh.to_mesh (bpy.context.depsgraph, apply_modifiers=True, calc_undeformed=False)
                    mesh.data = new_mesh
                    bpy.data.meshes.remove (old_mesh)


            bpy.ops.object.mode_set (mode='OBJECT')
            bpy.ops.object.select_all (action='DESELECT')
            rig.select_set (True)
            bpy.context.view_layer.objects.active = rig                 
            
            #apply pose
            bpy.ops.object.mode_set (mode='POSE')
            bpy.ops.pose.select_all (action='SELECT')
            bpy.ops.pose.armature_apply ()
            
            
            #adjust spine
            
            #spine_1, spine_2
            bpy.ops.object.mode_set (mode='EDIT')
            ebones = rig.data.edit_bones
            loc = (ebones['spine_1'].head + ebones['spine_2'].tail ) / 2
            ebones['spine_1'].tail = loc
            ebones['spine_2'].head = loc
            
            #spine chain
            def adjust_spine_point (lower_bone, upper_bone):
                forward = (0, -1, 0)
                backward = (0, 1, 0)
                hit_loc, hit_nor, hit_index, hit_dist = cast_ray_from_bone (lower_bone, 'tail', 'ebone', forward, 10)
                front = hit_loc
                hit_loc, hit_nor, hit_index, hit_dist = cast_ray_from_bone (lower_bone, 'tail', 'ebone', backward, 10)
                back = hit_loc
                middle = ( front + back ) / 2
            
                bpy.ops.object.mode_set (mode='EDIT')
                ebones = rig.data.edit_bones
                ebones [lower_bone].tail = middle
                ebones [upper_bone].head = middle
                
                return front
                
            loc_pelvis_front = adjust_spine_point ('hips', 'spine_1')
            adjust_spine_point ('spine_1', 'spine_2')
            loc_sternum_lower = adjust_spine_point ('spine_2', 'spine_3')
            adjust_spine_point ('spine_3', 'neck')
            
            
            #additional locator bones
            if belly_locators == True:
                ebone = rig.data.edit_bones.new (name='loc_pelvis_front')
                ebone.head = loc_pelvis_front
                ebone.tail = loc_pelvis_front + Vector ((0, 0, 0.05))
                ebone.parent = rig.data.edit_bones['hips']
                
                ebone = rig.data.edit_bones.new (name='loc_sternum_lower')
                ebone.head = loc_sternum_lower
                ebone.tail = loc_sternum_lower + Vector ((0, 0, 0.05))
                ebone.parent = rig.data.edit_bones['spine_3']

       
            #enforce roll values
            bpy.ops.object.mode_set (mode='EDIT')
            ebones = rig.data.edit_bones
            bpy.ops.armature.select_all (action='SELECT')
            bpy.ops.armature.symmetrize ()
            
            #finalize
            bpy.ops.object.mode_set (mode='OBJECT')
            bpy.ops.object.select_all (action='DESELECT')
            rig.select_set (True)
            bpy.context.view_layer.objects.active = rig
            
            #GYAZ stamp
            rig.data['GYAZ_game_rig'] = True


        return {'FINISHED'}

#######################################################
#######################################################

#REGISTER

def register():
    bpy.utils.register_class (Op_GYAZ_ManuelBastioniRigToGYAZSourceRig)      
   

def unregister ():
    bpy.utils.unregister_class (Op_GYAZ_ManuelBastioniRigToGYAZSourceRig)

  
if __name__ == "__main__":   
    register()   