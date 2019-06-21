import bpy
import math
import re
from . import se3
from . import blutils
from mathutils import *

def write_file(path, animation_name, context):
    selected_objects = context.selected_objects
    scene = context.scene
    
    render_settings = scene.render
    fps = render_settings.fps
    fps_base = render_settings.fps_base
    frame_start = scene.frame_start
    frame_end = scene.frame_end
    
    put_back_frame = scene.frame_current
    
    se3_animation = se3.Animation(version=1.02, name=animation_name,
                                  second_per_frame=fps_base/fps,
                                  first_frame=frame_start,
                                  last_frame=frame_end)
    
    for object in selected_objects:
        if object.type == 'ARMATURE':
            pose_bones = object.pose.bones
            
            for pose_bone in pose_bones:
                scene.frame_set(frame_start)
                
                bone = pose_bone.bone
                bone_head = bone.head
                armature_matrix = bone.matrix
                
                se3_envelope = se3.Envelope(pose_bone.name)
                
                se3_pos_x = se3.Channel('Pos.X')
                se3_pos_y = se3.Channel('Pos.Y')
                se3_pos_z = se3.Channel('Pos.Z')
                
                se3_rot_h = se3.Channel('Rot.H')
                se3_rot_p = se3.Channel('Rot.P')
                se3_rot_b = se3.Channel('Rot.B')

                if pose_bone.parent:
                    parent_length = bone.parent.length

                    se3_default_matrix = se3.to_child_rotation_matrix(armature_matrix)
                    se3_default_euler = se3.matrix_to_euler(se3_default_matrix)
                    
                    se3_default_position = se3.to_child_position(bone_head, parent_length)

                    se3_pos_x.default = se3_default_position[0]
                    se3_pos_y.default = se3_default_position[1]
                    se3_pos_z.default = se3_default_position[2]
                    
                    se3_rot_h.default = se3_default_euler[0]
                    se3_rot_p.default = se3_default_euler[1]
                    se3_rot_b.default = se3_default_euler[2]
                    
                    while scene.frame_current <= frame_end:
                        current_frame = scene.frame_current
                        
                        basis_matrix = pose_bone.matrix_basis
                        basis_loc = pose_bone.location
                        
                        print(basis_loc)

                        se3_key_matrix = se3.to_child_rotation_matrix(basis_matrix) * se3_default_matrix
                        
                        se3_key_euler = se3.matrix_to_euler(se3_key_matrix)

                        se3_pos_x.frames.append( (current_frame, se3_default_position[0] + (-basis_loc[0]) ) )
                        se3_pos_y.frames.append( (current_frame, se3_default_position[1] +   basis_loc[2]) )
                        se3_pos_z.frames.append( (current_frame, se3_default_position[2] +   basis_loc[1]) )
                        
                        se3_rot_h.frames.append((current_frame, se3_key_euler[0]))
                        se3_rot_p.frames.append((current_frame, se3_key_euler[1]))
                        se3_rot_b.frames.append((current_frame, se3_key_euler[2]))
                        
                        scene.frame_set(current_frame + 1)
                else:
                    se3_default_matrix = se3.to_free_rotation_matrix(armature_matrix)
                    se3_default_euler = se3.matrix_to_euler(se3_default_matrix)
                    
                    se3_default_position = se3.to_free_position(bone_head)
                    
                    se3_pos_x.default = se3_default_position[0]
                    se3_pos_y.default = se3_default_position[1]
                    se3_pos_z.default = se3_default_position[2]
                    
                    se3_rot_h.default = se3_default_euler[0]
                    se3_rot_p.default = se3_default_euler[1]
                    se3_rot_b.default = se3_default_euler[2]
                    
                    while scene.frame_current <= frame_end:
                        current_frame = scene.frame_current
                        
                        se3_key_matrix = se3.to_free_rotation_matrix(pose_bone.matrix)

                        se3_key_euler = se3.matrix_to_euler(se3_key_matrix)
                        se3_key_position = se3.to_free_position(pose_bone.head)
                        
                        se3_pos_x.frames.append((current_frame, se3_key_position[0]))
                        se3_pos_y.frames.append((current_frame, se3_key_position[1]))
                        se3_pos_z.frames.append((current_frame, se3_key_position[2]))
                        
                        se3_rot_h.frames.append((current_frame, se3_key_euler[0]))
                        se3_rot_p.frames.append((current_frame, se3_key_euler[1]))
                        se3_rot_b.frames.append((current_frame, se3_key_euler[2]))
                        
                        scene.frame_set(current_frame + 1)
                
                se3_envelope.channels.extend([se3_pos_x, se3_pos_y, se3_pos_z, se3_rot_h, se3_rot_p, se3_rot_b])
                se3_animation.envelopes.append(se3_envelope)
        
        elif object.type == 'MESH':
            shape_keys = blutils.get_non_basis_keys(object.data)
            
            se3_envelope = se3.Envelope("morph")
            
            for shape_key in shape_keys:
                scene.frame_set(frame_start)
                
                se3_morph_name = shape_key.name
                
                if re.match("^position", se3_morph_name, re.IGNORECASE):
                    se3_morph_name = "_" + se3_morph_name
                
                se3_channel = se3.Channel("Val.{0}".format(se3_morph_name))
                se3_channel.default = shape_key.slider_min
                
                while scene.frame_current <= frame_end:
                    se3_channel.frames.append( (scene.frame_current, shape_key.value) )
                    scene.frame_set(scene.frame_current + 1)
                
                se3_envelope.channels.append(se3_channel)
            
            se3_animation.envelopes.append(se3_envelope)
    
    scene.frame_set(put_back_frame)
    
    aaf = open(path, 'w')
    se3_animation.write_to_file(aaf)
    aaf.close()
    return {'FINISHED'}