
'''
Copyright (C) 2015 Andreas Esau
andreasesau@gmail.com

Created by Andreas Esau

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy
import bmesh
import json
from bpy.props import FloatProperty, IntProperty, BoolProperty, StringProperty, CollectionProperty, FloatVectorProperty, EnumProperty, IntVectorProperty
from collections import OrderedDict
from .. functions import *
import math
from mathutils import Vector,Matrix, Quaternion, Euler
import shutil

json_data = OrderedDict({
            "info":"Generated with COA Tools",
            "frameRate": 24,
            "name": "Project Name",
            "version": "5.5",
            "compatibleVersion": "5.5",
            "armature": []
            })

armature_data = OrderedDict({
            "type":"Armature",
            "frameRate":24,
            "name":"Armature",
            "aabb":{"width":0,"y":0,"height":0,"x":0},
            "bone":[],
            "slot":[],
            "skin":[{"name":"","slot":[]}],
            "ik":[],
            "animation":[],
            "defaultActions":[{"gotoAndPlay":""}]
           })

animation_data = OrderedDict({
            "duration": 0,
            "playTimes": 0,
            "name": "Anim Name",
            "bone": [],
            "frame": [],
            "slot": [],
            "ffd": [],
            })
    
skin = OrderedDict({
        "name":"",
        "slot":[],
        })

atlas_data = {}

display = [
            OrderedDict({
                "edges": [],
                "uvs": [],
                "type": "mesh",
                "vertices": [],
                "transform": {
                    "x": -2
                },
                "userEdges": [],
                "width": 480,
                "triangles": [],
                "height": 480,
                "name": "output_file",
                "path": ""
            })
        ]


bone_default_pos = {}
bone_default_rot = {}
vert_coords_default = {}
tex_pathes = {}
img_names = {} ### exported image names
tmp_slots_data = {}

def setup_armature_data(root_bone):
    armature_data = OrderedDict({
                "type":"Armature",
                "frameRate":24,
                "name":"Armature",
                "aabb":{"width":0,"y":0,"height":0,"x":0},
                "bone":[{"name":root_bone.name}],
                "slot":[],
                "skin":[{"name":"","slot":[]}],
                "ik":[],
                "animation":[],
                "defaultActions":[{"gotoAndPlay":""}]
               })
    return armature_data
           
def setup_json_project(project_name):
    json_data = OrderedDict({
                "info":"Generated with COA Tools",
                "frameRate": 24,
                "name": project_name,
                "version": "5.5",
                "compatibleVersion": "5.5",
                "armature": []
                })
    return json_data                

def get_sprite_image_data(sprite_data):
    #mat = sprite.active_material
    mat = sprite_data.materials[0]
    tex = [slot.texture for slot in mat.texture_slots if slot != None and slot.texture.type == "IMAGE"][0]
    img = tex.image if tex.image != None else None    
    
    return mat, tex, img
    
def copy_textures(self,sprites,texture_dir_path):
    global img_names
    img_names = {}
    for sprite in sprites:
        if sprite.type == "MESH":
            imgs = []
            if sprite.coa_type == "MESH":
                if len(sprite.data.materials) > 0:
                    mat, tex, img = get_sprite_image_data(sprite.data)
                    imgs.append({"img":img,"key":sprite.data.name})
            elif sprite.coa_type == "SLOT":
                for slot in sprite.coa_slot:
                    if len(slot.mesh.materials) > 0:
                        mat, tex, img = get_sprite_image_data(slot.mesh)
                        imgs.append({"img":img,"key":slot.mesh.name})
                
            for data in imgs:
                img = data["img"]
                key = data["key"]
                
                src_path = bpy.path.abspath(img.filepath)
                img_name = os.path.basename(src_path)
                dst_path = os.path.join(texture_dir_path,img_name)
                
                img_names[key] = img_name[:img_name.rfind(".")]
                
                if self.scene.coa_export_image_mode == "IMAGES":
                    if os.path.isfile(src_path):
                        shutil.copyfile(src_path,dst_path)
                    else:
                        img.save_render(dst_path)
                    
                        

def remove_base_sprite(obj):
    bpy.context.scene.objects.active = obj
    obj.hide = False
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    verts = []
        
    if "coa_base_sprite" in obj.vertex_groups and obj.data.coa_hide_base_sprite:
        v_group_idx = obj.vertex_groups["coa_base_sprite"].index
        for i,vert in enumerate(obj.data.vertices):
            for g in vert.groups:
                if g.group == v_group_idx:
                    verts.append(bm.verts[i])
                    break

    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')


    bmesh.ops.delete(bm,geom=verts,context=1)
    bm = bmesh.update_edit_mesh(obj.data) 
    bpy.ops.object.mode_set(mode="OBJECT")



##### get mesh data like vertices, edges, triangles and uvs   ##### Start

def get_mixed_vertex_data(obj):
    shapes = obj.data.shape_keys
    verts = []
    index = int(obj.active_shape_key_index)
    shape_key = obj.shape_key_add("tmp_mixed_mesh",from_mix=True)
    for vert in shape_key.data:
        coord = obj.matrix_world * vert.co
        verts.append([vert.co[0],vert.co[1],vert.co[2]])
    obj.shape_key_remove(shape_key)            
    obj.active_shape_key_index = index
    return verts    

### get vertices information
def convert_vertex_data_to_pixel_space(verts):
    data = []
    for vert in verts:
        for i,coord in enumerate(vert):
            if i in [0,2]:
                multiplier = 1
                if i == 2:
                    multiplier = -1
                value = round(multiplier*coord*100,2)
                data.append(value)
    return data 

### get edge information
def get_edge_data(bm,only_outer_edges=True):
    edges = []
    for edge in bm.edges:
            if (edge.is_boundary and only_outer_edges) or (not edge.is_boundary and not only_outer_edges):
                for i,vert in enumerate(edge.verts):
                    edges.append(vert.index)
                    
              
    return edges

### get triangle information
def get_triangle_data(bm):
    triangles = []
    for face in bm.faces:
        for i,vert in enumerate(face.verts):
            triangles.append(vert.index)
    return triangles

### get mesh vertex corrseponding uv vertex        
def uv_from_vert_first(uv_layer, v):
    for l in v.link_loops:
        uv_data = l[uv_layer]
        return uv_data.uv
    return None

### get uv information
def get_uv_data(bm):
    uvs = []
    uv_layer = bm.loops.layers.uv.active
    for vert in bm.verts:
        uv_first = uv_from_vert_first(uv_layer,vert)
        for i,val in enumerate(uv_first):
            if i == 1:
                value = round(-val + 1,5)
                uvs.append(value)
            else:
                value = round(val,5)
                uvs.append(value)
    return uvs

def get_modulate_color(sprite):
    color = sprite.coa_modulate_color
    alpha = sprite.coa_alpha
    color_data = {"rM":int(100*color[0]),"gM":int(100*color[1]),"bM":int(100*color[2]),"aM":int(100*alpha)}
    return color_data

##### get mesh data like vertices, edges, triangles and uvs   ##### End


### get slot data
def get_slot_data(self,sprites):
    slot_data = []
    for sprite in sprites:
        if sprite.type == "MESH":
            slot = OrderedDict()
            slot["name"] = sprite.name
            slot["parent"] = self.sprite_object.name #sprite.parent.name
            slot_data.append(slot)
            
            if len(sprite.coa_slot) > 0:
                slot["displayIndex"] = sprite.coa_slot_index
            
            color = get_modulate_color(sprite)
            if color["rM"] != 100 or color["gM"] != 100 or color["bM"] != 100 or color["aM"] != 100:
                slot["color"] = color
    return slot_data    

def normalize_weights(obj, armature, threshold):
    for vert in obj.data.vertices:
        weight_total = 0.0
        groups = []
        for group in vert.groups:
            vgroup = obj.vertex_groups[group.group]
            group_name = vgroup.name
            if (group.weight > threshold and armature == None) or (group.weight > threshold and armature != None and group_name in armature.data.bones):
                groups.append(group)
            
        for group in groups:
            vgroup = obj.vertex_groups[group.group]
            weight_total += group.weight
        for group in groups:
            group.weight = 1*(group.weight/weight_total)
            

    
### get skin data
def get_skin_slot(self,sprite,armature,scale,slot_data=None):
    context = bpy.context
    sprite_name = str(sprite.name)
    sprite_data_name = sprite.data.name if slot_data == None else slot_data.name
    ### make a sprite duplicate and make it active
    if slot_data == None:
        sprite_data = sprite.data.copy()
    else:
        sprite_data = slot_data.copy()    
    sprite = sprite.copy()
    sprite.data = sprite_data
    self.scene.objects.link(sprite)
    self.scene.objects.active = sprite
    
    ### normalize weights
    normalize_weights(sprite, armature, 0.0)
    for area in context.screen.areas:
            if area.type == "VIEW_3D":
                for region in area.regions:
                    override = context.copy()
                    override["object"] = sprite
                    override["edit_object"] = sprite
                    #bpy.ops.object.vertex_group_clean(override, group_select_mode='BONE_DEFORM', keep_single=True)
                    bpy.ops.object.vertex_group_clean(override, group_select_mode='ALL', keep_single=True)
    ###
    
    global tmp_sprites
    tmp_slots_data[sprite_data_name] = {"data":sprite_data,"object":sprite,"name":sprite_data_name}
    
    ### get sprite material, texture and img data
    mat, tex, img = get_sprite_image_data(sprite_data)
    tex_path = os.path.join(self.scene.coa_project_name+"_texture" , img_names[sprite_data_name])
    tex_pathes[sprite_name] = tex_path
    ### delete basesprite mesh in sprite duplicate
    remove_base_sprite(sprite)
    
    ### get display data of a sprite
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(sprite.data)
    
    ### generate display data dictionary
    display_data = OrderedDict()
    
    ### get general skin information
    display_data["type"] = "mesh"
    display_data["name"] = sprite_data_name#sprite_name
    if self.scene.coa_export_image_mode == "IMAGES":
        display_data["path"] = img_names[sprite_data_name]
    
    if self.scene.coa_export_image_mode == "IMAGES":
        display_data["width"] = int(img.size[0])
        display_data["height"] = int(img.size[1])
    elif self.scene.coa_export_image_mode == "ATLAS":
        display_data["width"] = atlas_data[sprite_data_name]["width"]
        display_data["height"] = atlas_data[sprite_data_name]["height"]
        
    verts = get_mixed_vertex_data(sprite)
    vert_coords_default[sprite_name] = verts
    display_data["vertices"] = convert_vertex_data_to_pixel_space(verts)
    
    bm = bmesh.from_edit_mesh(sprite.data)
    display_data["userEdges"] = get_edge_data(bm,only_outer_edges=False)
    display_data["edges"] = get_edge_data(bm)
    display_data["triangles"] = get_triangle_data(bm)
    display_data["uvs"] = get_uv_data(bm)
    
    if armature != None:
        armature.data.pose_position = "REST"
        bpy.context.scene.update()
        
        weights, bones = get_bone_weight_data(self,sprite,armature)
        
        display_data["weights"] = weights
        
        display_data["bonePose"] = []
        for bone in bones:
            mat = get_bone_matrix(armature,bone["bone"],relative=False)
            display_data["bonePose"].append(bone["index"]+1)
            display_data["bonePose"].append(round(mat[0][0],5))
            display_data["bonePose"].append(round(mat[0][1],5))
            display_data["bonePose"].append(round(mat[1][0],5))
            display_data["bonePose"].append(round(mat[1][1],5))
            display_data["bonePose"].append(round(mat[1][3] * scale ,5))#pos x
            display_data["bonePose"].append(round(-mat[0][3] *scale ,5))#pos y
        armature.data.pose_position = "POSE"    
        bpy.context.scene.update()
        
        w = sprite.matrix_local[0][0]
        x = sprite.matrix_local[0][2]
        y = sprite.matrix_local[2][0]
        z = sprite.matrix_local[2][2]
        display_data["slotPose"] = [w,x,y,z, sprite.matrix_local.to_translation()[0]*scale, -sprite.matrix_local.to_translation()[2]*scale]
    
    bpy.ops.object.mode_set(mode="OBJECT")
    
    #bpy.data.objects.remove(sprite,do_unlink=True)
    return display_data
    

def get_skin_data(self,sprites,armature,scale):
    context = bpy.context
    
    global tex_pathes
    tex_pathes = {}
    
    ### skin data array
    skin_data = [{"slot":[]}]

    for sprite in sprites:
        ### create slot data
        slot_data = OrderedDict()
        slot_data["name"] = sprite.name
        slot_data["display"] = []
        
        if sprite.type == "MESH":
            if sprite.coa_type == "MESH":
                data2 = get_skin_slot(self,sprite,armature,scale)
                slot_data["display"].append(data2) 
            elif sprite.coa_type == "SLOT":
                for slot in sprite.coa_slot:
                    data2 = get_skin_slot(self,sprite,armature,scale,slot_data=slot.mesh)
                    slot_data["display"].append(data2)
                    
            skin_data[0]["slot"].append(slot_data)             
    return skin_data

### get bone data
def create_cleaned_armature_copy(self,armature,sprites):
    context = bpy.context
    if armature != None:
        scene = bpy.context.scene
        
        armature_data = armature.data.copy()
        armature_copy = armature.copy()
        armature_copy.data = armature_data
        armature_copy.name = "COA_EXPORT_ARMATURE"
        
        scene.objects.link(armature_copy)
        
        delete_non_deform_bones(self,armature_copy,sprites)
        create_copy_transform_constraints(self,armature,armature_copy)
        
        ### store armature rest position. Relevant for later animation calculations
        scale = 1/get_addon_prefs(context).sprite_import_export_scale
        
        armature_copy.data.pose_position = "REST"
        armature.data.pose_position = "REST"
        bpy.context.scene.frame_set(bpy.context.scene.frame_current)
        for bone in armature_copy.data.bones:
            transformations = {}
            transformations["bone_pos"] = get_bone_pos(armature_copy,bone,scale)
            transformations["bone_rot"] = get_bone_angle(armature_copy,bone)
            transformations["bone_scale"] = get_bone_scale(armature_copy,bone)
            
            self.armature_restpose[bone.name] = transformations
        armature_copy.data.pose_position = "POSE"
        armature.data.pose_position = "POSE"
        return armature_copy
    return None

def bone_is_deform_bone(self,bone,sprites):
    for sprite in sprites:
        if sprite.type == "MESH":
            init_mesh = sprite.data
            meshes = []
            ### get a list of all meshes in sprite -> slot objects containt multiple meshes
            if sprite.coa_type == "MESH":
                meshes.append(sprite.data)
            elif sprite.coa_type == "SLOT":
                for slot in sprite.coa_slot:
                    meshes.append(slot.mesh)
                
            ### check all meshes if bone is deforming that mesh        
            for mesh in meshes:
                sprite.data = mesh
                if sprite.parent_bone == bone.name:
                    sprite.data = init_mesh
                    return True
                if not bone.name in sprite.vertex_groups:
                    break
                else:
                    v_group = sprite.vertex_groups[bone.name]
                    for vert in sprite.data.vertices:
                        try:
                            weight = v_group.weight(vert.index)
                            if weight > 0:
                                sprite.data = init_mesh
                                return True
                        except:
                            pass
            sprite.data = init_mesh
    return False    

### is used for export armature. All non deform bones will be deleted and deform bone animations baked in later process
def delete_non_deform_bones(self,armature,sprites):
    context = bpy.context
    context.scene.objects.active = armature
    
    bpy.ops.object.mode_set(mode="EDIT")
    
    for bone in armature.data.bones:
        pbone = armature.pose.bones[bone.name]
        ebone = armature.data.edit_bones[bone.name]
        
        if pbone.is_in_ik_chain or len(pbone.constraints) > 0:
            ebone.parent = None
        
        is_deform_bone = bone_is_deform_bone(self,bone,sprites)
        is_driver = bone_is_driver(bone,sprites)
        is_const_target = bone_is_constraint_target(bone,armature)
        has_children = len(bone.children) > 0
        
        if (not is_deform_bone and is_driver) or (not is_deform_bone and is_const_target) or (not is_deform_bone and not has_children) or (not is_deform_bone and not bone.use_deform):
            armature.data.edit_bones.remove(armature.data.edit_bones[bone.name])
    
    bpy.ops.object.mode_set(mode="OBJECT")        

def get_driver_bone_target(driver):
    targets = []
    for v in driver.driver.variables:
        if v.targets[0].bone_target != "":
            targets.append(v.targets[0].bone_target)
    return targets

def bone_is_constraint_target(bone,armature):
    for pbone in armature.pose.bones:
        for const in pbone.constraints:
            if hasattr(const,"subtarget") and const.subtarget == bone.name:
                return True
    return False        

def bone_is_driver(bone,sprites):
    for sprite in sprites:
        if sprite.type == "MESH":
            meshes = []
            if sprite.coa_type == "MESH":
                meshes.append(sprite.data)
            elif sprite.coa_type == "SLOT":
                for slot in sprite.coa_slot:
                    meshes.append(slot.mesh)
            
            all_bone_targets = []
            if sprite.animation_data != None:
                for driver in sprite.animation_data.drivers:
                    bone_targets = get_driver_bone_target(driver)
                    all_bone_targets += bone_targets
            for mesh in meshes:
                if mesh.animation_data != None:
                    for driver in mesh.animation_data.drivers:
                        bone_targets = get_driver_bone_target(driver)
                        all_bone_targets += bone_targets
                if mesh.shape_keys != None and mesh.shape_keys.animation_data != None:
                    for driver in mesh.shape_keys.animation_data.drivers:
                        bone_targets = get_driver_bone_target(driver)
                        all_bone_targets += bone_targets
                if bone.name in all_bone_targets:
                    return True        
    return False

def create_copy_transform_constraints(self,armature_from, armature_to):
    for bone in armature_to.pose.bones:
        for const in bone.constraints:
            bone.constraints.remove(const)
        if bone.name in armature_from.pose.bones:
            const = bone.constraints.new("COPY_TRANSFORMS")
            const.target = armature_from
            const.subtarget = bone.name
            const.target_space = "POSE"
            const.owner_space = "POSE"

def get_bone_matrix(armature,bone,relative=True):
    pose_bone = armature.pose.bones[bone.name]
    
    m = Matrix() ### inverted posebone origin matrix
    m.row[0] = [0,0,1,0]
    m.row[1] = [1,0,0,0]
    m.row[2] = [0,1,0,0]
    m.row[3] = [0,0,0,1]
    
    if bone.parent == None:
        mat_bone_space = m * pose_bone.matrix
    else:
        if relative:
            #if bone.use_inherit_rotation and bone.use_inherit_scale:
            mat_bone_space = pose_bone.parent.matrix.inverted() * pose_bone.matrix
        else:
            mat_bone_space = m * pose_bone.matrix
    
    #### remap matrix
    loc, rot, scale = mat_bone_space.decompose()
    
    #if not bone.use_inherit_scale:
    #    scale = (m * pose_bone.matrix).decompose()[2]
    
    loc_mat = Matrix.Translation(loc)
    
    rot_mat = rot.inverted().to_matrix().to_4x4()
    
    scale_mat = Matrix()
    scale_mat[0][0] = scale[1]
    scale_mat[1][1] = scale[0]
    scale_mat[2][2] = scale[2]
    mat_bone_space = loc_mat * rot_mat * scale_mat
    return mat_bone_space

def get_bone_pos(armature,bone,scale):
    loc, rot, sca = get_bone_matrix(armature,bone).decompose()
    
    pos_2d = Vector((loc[1],-loc[0])) * scale # flip x and y and negate x to fit dragonbones coordinate system
    return pos_2d 

def get_bone_angle(armature,bone,relative=True):
    loc, rot, scale = get_bone_matrix(armature,bone,relative).decompose()
    rot_x = round(math.degrees(rot.to_euler().x),2)
    rot_y = round(math.degrees(rot.to_euler().y),2)
    rot_z = -round(math.degrees(rot.to_euler().z),2)
#    if get_bone_scale(armature,bone)[0] < 0:
#        rot_z = - rot_z
    return rot_z

def get_bone_scale(armature,bone):
    mat = get_bone_matrix(armature,bone)
    loc, rot, scale = get_bone_matrix(armature,bone).decompose()
#    scale = Vector(((scale[0]),abs(scale[1]),abs(scale[2])))
    return scale
            
def get_bone_data(self,armature,sprite_object,scale):
    
    bone_data = []
    bone_data.append(OrderedDict({"name":self.sprite_object.name})) ### append root
    
    for bone in armature.data.bones:
        data = {}
        data["name"] = bone.name
        data["transform"] = {}
        
        ### get bone position
        pos = get_bone_pos(armature,bone,scale)
        bone_default_pos[bone.name] = Vector(pos)
        if pos != Vector((0,0)):
            data["transform"]["x"] = pos[0]
            data["transform"]["y"] = pos[1]
        
        ### get bone angle    
        angle = get_bone_angle(armature,bone)
        bone_default_rot[bone.name] = angle
        if angle != 0:
            data["transform"]["skX"] = angle
            data["transform"]["skY"] = angle
            
        ### get bone scale
        sca = get_bone_scale(armature,bone)
        if sca != Vector((1.0,1.0,1.0)):
            data["transform"]["scX"] = sca[0]
            data["transform"]["scY"] = sca[1]
        
        if int(bone.use_inherit_rotation) != 1:
            data["inheritRotation"] = int(bone.use_inherit_rotation)
        if int(bone.use_inherit_scale) != 1:    
            data["inheritScale"] = int(bone.use_inherit_scale)
        if bone.parent != None:
            data["parent"] = bone.parent.name
        else:
            data["parent"] = sprite_object.name
        data["length"] = int((bone.head - bone.tail).length*scale)
        
        bone_data.append(data)
        
    return bone_data             

def get_bone_index(self,armature,bone_name):
    armature_bones = []
    for bone in armature.data.bones:
        armature_bones.append(bone)
    
    for i,bone in enumerate(armature_bones):
        if bone_name == bone.name:
            return i

### get weight data
def get_bone_weight_data(self,obj,armature):
    data = []
    bone_names = []
    bones = []
    for vert in obj.data.vertices:
        groups = []
        for group in vert.groups:
            group_name = obj.vertex_groups[group.group].name
            if group_name in armature.data.bones:
                groups.append({"group":group,"group_name":group_name})
        
        data.append(len(groups))    
        for group in groups:
            b_index = get_bone_index(self,armature,group["group_name"])
            bone_index = b_index+1
            data.append(bone_index)
            bone_weight = round(group["group"].weight,6)
            data.append(bone_weight)
            
            if group["group_name"] not in bone_names:
                bone_names.append(group["group_name"])
    
    armature_bones = []
    for bone in armature.data.bones:
        armature_bones.append(bone)   
                
    for i,bone in enumerate(armature_bones):
        if bone.name in bone_names:
            bone = armature.data.bones[bone.name]            
            bones.append({"index":i,"bone":bone})        
    return data, bones

### Export Animations
### get objs and bones that are keyed on given frame    
def bone_key_on_frame(bone,frame,action,type="LOCATION"): ### LOCATION, ROTATION, SCALE, ANY
    type = "."+type.lower()
    if action != None:
        for fcurve in action.fcurves:
            if bone.name in fcurve.data_path and (type in fcurve.data_path or type == ".any"):
                for keyframe in fcurve.keyframe_points:
                    if keyframe.co[0] == frame:
                        return True
    return False   

def property_key_on_frame(obj,prop_names,frame,type="PROPERTY"):
    if type == "SHAPEKEY":
        obj = obj.shape_keys
    
    if obj != None and obj.animation_data != None:
    ### check if property has a key set
        action = obj.animation_data.action
        if action != None:
            for fcurve in action.fcurves:
                for prop_name in prop_names:
                    if prop_name in fcurve.data_path:
                        for keyframe in fcurve.keyframe_points:
                            if keyframe.co[0] == frame:
                                return True
    ### check if property has a bone driver and bone has a key set
        for driver in obj.animation_data.drivers:
            for prop_name in prop_names:
                if prop_name in driver.data_path:
                    for var in driver.driver.variables:
                        armature = var.targets[0].id
                        if armature != None:
                            bone_target = var.targets[0].bone_target
                            if bone_target in armature.data.bones:
                                bone = armature.data.bones[bone_target]
                                pbone = armature.pose.bones[bone_target]
                                key_on_frame = bone_key_on_frame(bone,frame,armature.animation_data.action,type="ANY")
                                if key_on_frame:
                                    return key_on_frame
                                for const in pbone.constraints:
                                    if const.type == "ACTION":
                                        bone = armature.data.bones[const.subtarget] if const.subtarget in armature.data.bones else None
                                        if bone != None:
                                            key_on_frame = bone_key_on_frame(bone,frame,armature.animation_data.action,type="ANY")
                                        if key_on_frame:
                                            return key_on_frame    
    return False
    
def get_animation_data(self,sprite_object,armature,armature_orig):
    context = bpy.context
    scale = 1/get_addon_prefs(context).sprite_import_export_scale
    anims = sprite_object.coa_anim_collections
    
    animations = []
    
    for anim_index,anim in enumerate(anims):
        if anim.name not in ["NO ACTION","Restpose"]:
            sprite_object.coa_anim_collections_index = anim_index ### set animation
            
            anim_data = animation_data.copy()
            anim_data["duration"] = anim.frame_end
            anim_data["playTimes"] = 0
            anim_data["name"] = anim.name
            anim_data["bone"] = []
            anim_data["slot"] = []
            anim_data["zOrder"] = {}
            anim_data["ffd"] = []
            
            
            ### append all slots to list
            slot_keyframe_duration = {}
            ffd_keyframe_duration = {}
            ffd_last_frame_values = {}
            for slot in self.sprites:
                if slot.type == "MESH":
                    anim_data["slot"].append({"name":slot.name,"colorFrame":[],"displayFrame":[]})
                    slot_keyframe_duration[slot.name] = {"color_duration":0,"display_duration":0}
                
                  
                    if slot.coa_type == "MESH":
                        anim_data["ffd"].append({"name":slot.data.name,"slot":slot.name,"frame":[]})
                        ffd_keyframe_duration[slot.data.name] = {"ffd_duration":0}
                        ffd_last_frame_values[slot.data.name] = None
                    elif slot.coa_type == "SLOT":
                        for slot2 in slot.coa_slot:
                            anim_data["ffd"].append({"name":slot2.mesh.name,"slot":slot.name,"frame":[]})
                            ffd_keyframe_duration[slot2.mesh.name] = {"ffd_duration":0}
                            ffd_last_frame_values[slot2.mesh.name] = None
                            
            ### check if slot has animation data. if so, store for later usage                
            SHAPEKEY_ANIMATION = {}
            for i in range(anim.frame_end+1):
                frame = anim.frame_end-i
                for slot in self.sprites:
                    if slot.type == "MESH":
                        
                        slot_data = []
                        if slot.coa_type == "MESH":
                            slot_data = [tmp_slots_data[slot.data.name]]
                        elif slot.coa_type == "SLOT":
                            for slot2 in slot.coa_slot:
                                slot_data.append(tmp_slots_data[slot2.mesh.name])
                        
                for item in slot_data:
                    data = item["data"]
                    data_name = item["name"]
                    
                    key_blocks = []
                    if data.shape_keys != None:
                        for key in data.shape_keys.key_blocks:
                            key_blocks.append(key.name)        
                    if property_key_on_frame(data,key_blocks,frame,type="SHAPEKEY"):
                        SHAPEKEY_ANIMATION[slot.name] = True
                        break
                            
            
            ### append all bones to list
            bone_keyframe_duration = {}
            if armature != None:
                for bone in armature.data.bones:
                    anim_data["bone"].append({"name":bone.name,"translateFrame":[],"rotateFrame":[],"scaleFrame":[]})
                    bone_keyframe_duration[bone.name] = {"scale_duration":0,"rot_duration":0,"pos_duration":0,"last_scale":None, "last_rot":None, "last_pos":None}
            
            for i in range(anim.frame_end+1):
                frame = anim.frame_end-i
                context.scene.frame_set(frame)
                
                #### HANDLE SLOT ANIMATION
                j = 0
                for slot in self.sprites:
                    if slot.type == "MESH":
                        slot_keyframe_duration[slot.name]["color_duration"] += 1
                        slot_keyframe_duration[slot.name]["display_duration"] += 1
                        
                        if property_key_on_frame(slot,["coa_alpha","coa_modulate_color"],frame):
                            
                            keyframe_data = {}
                            keyframe_data["duration"] = slot_keyframe_duration[slot.name]["color_duration"]
                            keyframe_data["tweenEasing"] = 0
                            keyframe_data["value"] = get_modulate_color(slot)
                            
                            anim_data["slot"][j]["colorFrame"].insert(0,keyframe_data)
                            slot_keyframe_duration[slot.name]["color_duration"] = 0
                        
                        if property_key_on_frame(slot,["coa_slot_index"],frame) or frame in [0,anim.frame_end]:
                            keyframe_data = {}
                            keyframe_data["duration"] = slot_keyframe_duration[slot.name]["display_duration"]
                            keyframe_data["value"] = slot.coa_slot_index
                            
                            anim_data["slot"][j]["displayFrame"].insert(0,keyframe_data)
                            slot_keyframe_duration[slot.name]["display_duration"] = 0
                            
                            
                        j += 1
                #### HANDLE BONE ANIMATION
                if armature != None:
                    for j,bone in enumerate(armature.data.bones):
                        bone_orig = armature_orig.data.bones[bone.name]
                        pose_bone_orig = armature_orig.pose.bones[bone.name]
                        const_len = len(pose_bone_orig.constraints)
                        in_ik_chain = pose_bone_orig.is_in_ik_chain
                        
                        bone_keyframe_duration[bone.name]["scale_duration"] += 1
                        bone_keyframe_duration[bone.name]["rot_duration"] += 1
                        bone_keyframe_duration[bone.name]["pos_duration"] += 1
                        
                        bake_anim = self.scene.coa_export_bake_anim and frame%self.scene.coa_export_bake_steps==0
                        
                        ### bone position
                        if bone_key_on_frame(bone_orig,frame,armature_orig.animation_data.action,type="LOCATION") or frame in [0,anim.frame_end] or const_len > 0 or in_ik_chain or bake_anim:
                            bone_pos = get_bone_pos(armature,bone,scale) - self.armature_restpose[bone.name]["bone_pos"]
                            
                            keyframe_data = {}
                            keyframe_data["duration"] = bone_keyframe_duration[bone.name]["pos_duration"]
                            keyframe_data["curve"] = [.5,0,.5,1] if bake_anim == False else [0,0,1,1]
                            keyframe_data["x"] = round(bone_pos[0],2)
                            keyframe_data["y"] = round(bone_pos[1],2)
                            
                            if (frame in [0,anim.frame_end]) or (bone_keyframe_duration[bone.name]["last_pos"] != [keyframe_data["x"], keyframe_data["y"]]):
                                
                                ### if previous keyframe differs and keyframe duration is greater 1 add an extra keyframe inbetween
                                if bone_keyframe_duration[bone.name]["pos_duration"] > 1 and (bone_keyframe_duration[bone.name]["last_pos"] != [keyframe_data["x"], keyframe_data["y"]]):
                                    keyframe_data_last = {}
                                    keyframe_data_last["duration"] = bone_keyframe_duration[bone.name]["pos_duration"]-1
                                    keyframe_data_last["curve"] = [.5,0,.5,1] if bake_anim == False else [0,0,1,1]
                                    keyframe_data_last["x"] = bone_keyframe_duration[bone.name]["last_pos"][0]
                                    keyframe_data_last["y"] = bone_keyframe_duration[bone.name]["last_pos"][1]
                                    anim_data["bone"][j]["translateFrame"].insert(0,keyframe_data_last)
                                    
                                    keyframe_data["duration"] = 1
                                    
                                anim_data["bone"][j]["translateFrame"].insert(0,keyframe_data)
                                bone_keyframe_duration[bone.name]["pos_duration"] = 0
                                bone_keyframe_duration[bone.name]["last_pos"] = [keyframe_data["x"], keyframe_data["y"]]
                        
                        ### bone rotation
                        if bone_key_on_frame(bone_orig,frame,armature_orig.animation_data.action,type="ROTATION") or frame in [0,anim.frame_end] or const_len > 0 or in_ik_chain or bake_anim:
                            bone_rot = get_bone_angle(armature,bone) - self.armature_restpose[bone.name]["bone_rot"]
                            
                            keyframe_data = {}
                            keyframe_data["duration"] = bone_keyframe_duration[bone.name]["rot_duration"]
                            keyframe_data["curve"] = [.5,0,.5,1] if bake_anim == False else [0,0,1,1]
                            keyframe_data["rotate"] = bone_rot
                            
                            if (frame in [0,anim.frame_end]) or (bone_keyframe_duration[bone.name]["last_rot"] != keyframe_data["rotate"]):
                                
                                ### if previous keyframe differs and keyframe duration is greater 1 add an extra keyframe inbetween
                                if bone_keyframe_duration[bone.name]["rot_duration"] > 1 and (bone_keyframe_duration[bone.name]["last_rot"] != keyframe_data["rotate"]):
                                    keyframe_data_last = {}
                                    keyframe_data_last["duration"] = bone_keyframe_duration[bone.name]["rot_duration"]-1
                                    keyframe_data_last["curve"] = [.5,0,.5,1] if bake_anim == False else [0,0,1,1]
                                    keyframe_data_last["rotate"] = bone_keyframe_duration[bone.name]["last_rot"]
                                    anim_data["bone"][j]["rotateFrame"].insert(0,keyframe_data_last)
                                    
                                    keyframe_data["duration"] = 1
                                
                                
                                anim_data["bone"][j]["rotateFrame"].insert(0,keyframe_data)
                                bone_keyframe_duration[bone.name]["rot_duration"] = 0
                                bone_keyframe_duration[bone.name]["last_rot"] = keyframe_data["rotate"]
                        
                        ### bone scale
                        if bone_key_on_frame(bone_orig,frame,armature_orig.animation_data.action,type="SCALE") or frame in [0,anim.frame_end] or const_len > 0 or in_ik_chain or bake_anim:
                            
                            bone_scale = get_bone_scale(armature,bone)
                            
                            keyframe_data = {}
                            keyframe_data["duration"] = bone_keyframe_duration[bone.name]["scale_duration"]
                            keyframe_data["curve"] = [.5,0,.5,1] if bake_anim == False else [0,0,1,1]
                            keyframe_data["x"] = round(bone_scale[0],2)
                            keyframe_data["y"] = round(bone_scale[1],2)
                            
                            if (frame in [0,anim.frame_end]) or (bone_keyframe_duration[bone.name]["last_scale"] != [keyframe_data["x"], keyframe_data["y"]]):
                                
                                ### if previous keyframe differs and keyframe duration is greater 1 add an extra keyframe inbetween
                                if bone_keyframe_duration[bone.name]["scale_duration"] > 1 and (bone_keyframe_duration[bone.name]["last_scale"] != [keyframe_data["x"], keyframe_data["y"]]):
                                    keyframe_data_last = {}
                                    keyframe_data_last["duration"] = bone_keyframe_duration[bone.name]["scale_duration"]-1
                                    keyframe_data_last["curve"] = [.5,0,.5,1] if bake_anim == False else [0,0,1,1]
                                    keyframe_data_last["x"] = bone_keyframe_duration[bone.name]["last_scale"][0]
                                    keyframe_data_last["y"] = bone_keyframe_duration[bone.name]["last_scale"][1]
                                    anim_data["bone"][j]["scaleFrame"].insert(0,keyframe_data_last)
                                    
                                    keyframe_data["duration"] = 1
                                
#                                if bone_keyframe_duration[bone.name]["last_scale"] != None and ((bone_keyframe_duration[bone.name]["last_scale"][1] < 0 and keyframe_data["y"] > 0) or (bone_keyframe_duration[bone.name]["last_scale"][1] > 0 and keyframe_data["y"] < 0)):
#                                    keyframe_data["curve"] = []
                                
                                anim_data["bone"][j]["scaleFrame"].insert(0,keyframe_data)
                                bone_keyframe_duration[bone.name]["scale_duration"] = 0
                                bone_keyframe_duration[bone.name]["last_scale"] = [keyframe_data["x"], keyframe_data["y"]]
                
                #### HANDLE FFD Transformations (Blender Shapekeys)
                j = 0
                for slot in self.sprites:
                    if slot.type == "MESH":
                        
                        slot_data = []
                        if slot.coa_type == "MESH":
                            slot_data = [tmp_slots_data[slot.data.name]]
                        elif slot.coa_type == "SLOT":
                            for slot2 in slot.coa_slot:
                                slot_data.append(tmp_slots_data[slot2.mesh.name])
                        
                        for item in slot_data:
                            data = item["data"]
                            data_name = item["name"]
                            
                            bake_anim = self.scene.coa_export_bake_anim and frame%self.scene.coa_export_bake_steps==0
                            
                            if data.shape_keys != None:
                                ffd_keyframe_duration[data_name]["ffd_duration"] += 1
                                
                                key_blocks = []
                                for key in data.shape_keys.key_blocks:
                                    key_blocks.append(key.name)
                                if property_key_on_frame(data,key_blocks,frame,type="SHAPEKEY") or (frame in [0,anim.frame_end] and data_name in SHAPEKEY_ANIMATION) or bake_anim:
                                    ffd_data = {}
                                    ffd_data["duration"] = ffd_keyframe_duration[data_name]["ffd_duration"]
                                    ffd_data["curve"] = [.5,0,.5,1] if bake_anim == False else [0,0,1,1]
#                                    if bake_anim == False:
#                                        ffd_data["curve"] = [.5,0,.5,1]
#                                    else:    
#                                        ffd_data["tweenEasing"] = 0
                                    
                                    verts = get_mixed_vertex_data(item["object"])
                                    verts_relative = []
                                    for i,co in enumerate(verts):
                                        verts_relative.append(Vector(co) - Vector(vert_coords_default[slot.name][i]))
                                    
                                    ffd_data["vertices"] = convert_vertex_data_to_pixel_space(verts_relative)     
                                    
                                    if (frame in [0, anim.frame_end]) or (ffd_last_frame_values[data_name] != ffd_data["vertices"]):
                                        ### if previous keyframe differs and keyframe duration is greater 1 add an extra keyframe inbetween
                                        if ffd_data["duration"] > 1 and (ffd_last_frame_values[data_name] != ffd_data["vertices"]):
                                            ffd_data_last = {}
                                            ffd_data_last["duration"] = ffd_keyframe_duration[data_name]["ffd_duration"]-1
                                            ffd_data_last["curve"] = [.5,0,.5,1]
                                            ffd_data_last["vertices"] = ffd_last_frame_values[data_name]
                                            
                                            anim_data["ffd"][j]["frame"].insert(0,ffd_data_last)
                                            ffd_data["duration"] = 1
                                        
                                        anim_data["ffd"][j]["frame"].insert(0,ffd_data)
                                        ffd_keyframe_duration[data_name]["ffd_duration"] = 0
                                        ffd_last_frame_values[data_name] = ffd_data["vertices"]
                            j += 1            
            

            ### cleanup animation data
            delete_keys = []
            for key in anim_data:
                data = anim_data[key]
                if type(data) == list:
                    if len(data) == 0:
                        delete_keys.append(key)
                    else:
                        for item in data:
                            delete_keys2 = []
                            if type(item) == dict:
                                for key2 in item:
                                    data2 = item[key2]
                                    if type(data2) == list:
                                        if len(data2) == 0:
                                            #del item[key2]
                                            delete_keys2.append(key2)
                            for key2 in delete_keys2:
                                del item[key2]
            for key in delete_keys:
                del anim_data[key]
                             
            animations.append(anim_data)
    return animations


class DragonBonesExport(bpy.types.Operator):
    bl_idname = "coa_tools.export_dragon_bones"
    bl_label = "Dragonbones Export"
    bl_description = ""
    bl_options = {"REGISTER"}
    
    reduce_size = BoolProperty(default=False)
    
    sprite_object = None
    armature = None
    sprites = None
    scale = 0.0
    
    armature_restpose = {}
    
    json_data = {}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def draw(self,context):
        layout = self.layout
        col = layout.column()
        col.prop(self,"bake_anim",text="Bake Animation")
        if self.bake_anim:
            col.prop(self,"bake_interval",text="Bake Interval")
        col.prop(self,"reduce_size",text="Reduce Export Size")
        
        if self.generate_atlas:
            box = col.box()
        else:
            box = col    
        box.prop(self,"generate_atlas",text="Generate Texture Atlas")
        if self.generate_atlas:
            row = box.row()
            #row.prop(self,"atlas_size",text="Atlas Size",expand=True)
            if self.atlas_size == "MANUAL":
                row = box.row()
                row.prop(self,"atlas_dimension",text="")
            row = box.row()    
            row.prop(self,"unwrap_method",text="Unwrap Method",expand=True)  
            row = box.row()
            row.prop(self,"island_margin",text="Sprite Margin")  
    
    def get_init_state(self,context):
        self.selected_objects = context.selected_objects[:]
        self.active_object = context.active_object
        self.sprite_object = get_sprite_object(context.active_object)
        
        self.animation_index = self.sprite_object.coa_anim_collections_index
        self.frame_current = context.scene.frame_current
    
    def set_init_state(self,context):
        for obj in context.scene.objects:
            if obj in self.selected_objects:
                obj.select = True
            else:    
                obj.select = False
        context.scene.objects.active = self.active_object
        
        if len(self.sprite_object.coa_anim_collections) > 0:
            self.sprite_object.coa_anim_collections_index = self.animation_index
        context.scene.frame_current = self.frame_current
    
    def execute(self, context):
        global tmp_slots_data
        tmp_slots_data = {}
        
        self.get_init_state(context)
        self.scene = context.scene
        
        ### set animation mode to action
        coa_nla_mode = str(self.scene.coa_nla_mode)
        self.scene.coa_nla_mode = "ACTION"
            
        
        ### get sprite object, sprites and armature
        self.scale = 1/get_addon_prefs(context).sprite_import_export_scale
        self.sprite_object = get_sprite_object(context.active_object)
        self.armature_orig = get_armature(self.sprite_object)
        
        self.sprites = get_children(context,self.sprite_object,[])
        self.sprites = sorted(self.sprites, key=lambda obj: obj.location[1], reverse=True) ### sort objects based on the z depth. needed for draw order
        
        self.armature = create_cleaned_armature_copy(self,self.armature_orig,self.sprites) ### create a cleaned copy of the armature that contains only deform bones and which has applied copy transform constraints

        ### get export, project and json path
        export_path = bpy.path.abspath(self.scene.coa_export_path)
        texture_dir_path = os.path.join(export_path , self.scene.coa_project_name+"_texture")
        json_path = os.path.join(export_path,self.scene.coa_project_name+"_ske.json")
        
        ### check if export dir exists
        if not os.path.exists(export_path):
            self.report({"WARNING"},"Export Path does not exists. Set a valid Export Path.")
            return{'CANCELLED'}
        
        
        ### export texture atlas
        if self.scene.coa_export_image_mode == "ATLAS":
            sprites = [sprite for sprite in self.sprites if sprite.type == "MESH"]
            generate_texture_atlas(self, sprites, self.scene.coa_project_name, export_path, img_width=self.scene.coa_atlas_resolution_x, img_height=self.scene.coa_atlas_resolution_y)
        
        ### create texture directory
        if self.scene.coa_export_image_mode == "IMAGES":
            if os.path.exists(texture_dir_path):
                shutil.rmtree(texture_dir_path)
            os.makedirs(texture_dir_path)
        
        ### copy all textures to texture directory
        copy_textures(self,self.sprites,texture_dir_path)
        
        ### create json data
        if self.armature != None:
            self.armature.data.pose_position = "REST"
            self.armature_orig.data.pose_position = "REST"
        
        self.json_data = setup_json_project(self.scene.coa_project_name) ### create base template
        self.json_data["armature"] =  [setup_armature_data(self.sprite_object)] ### create base armature
        self.json_data["armature"][0]["slot"] = get_slot_data(self,self.sprites)
        self.json_data["armature"][0]["skin"] = get_skin_data(self,self.sprites,self.armature,self.scale)
        self.json_data["armature"][0]["bone"] = get_bone_data(self,self.armature,self.sprite_object,self.scale) if self.armature != None else [{"name":self.sprite_object.name}]
        
        if self.armature != None:
            self.armature.data.pose_position = "POSE"
            self.armature_orig.data.pose_position = "POSE"
        self.json_data["armature"][0]["animation"] = get_animation_data(self,self.sprite_object,self.armature,self.armature_orig)
        
        ### write and store json file
        self.reduce_size = True
        if self.reduce_size:
            json_file = json.dumps(self.json_data,separators=(',',':'))
        else:    
            json_file = json.dumps(self.json_data, indent="\t", sort_keys=False)
        
        text_file = open(json_path, "w")
        text_file.write(json_file)
        text_file.close()
        
        
        
        
        ### cleanup scene
        self.set_init_state(context) ### restore initial object selection
        if self.armature != None:
            bpy.data.objects.remove(self.armature) ### delete copied armature
            
        for key in tmp_slots_data:
            bpy.data.objects.remove(tmp_slots_data[key]["object"],do_unlink=True)
        
        self.scene.coa_nla_mode = coa_nla_mode    
            
        self.report({"INFO"},"Export successful.")
        return {"FINISHED"}
    
    
class DragonbonesExportPanel(bpy.types.Panel):
    bl_idname = "dragonbones_export_panel"
    bl_label = "Dragonbones Export Panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    bpy.types.Scene.coa_project_name = bpy.props.StringProperty(default="New Project", name="Project name")
    bpy.types.Scene.coa_export_path = bpy.props.StringProperty(default="", name="Export Path",subtype="DIR_PATH")
    bpy.types.Scene.coa_export_image_mode = bpy.props.EnumProperty(default="ATLAS", name="Image Mode",items=(("ATLAS","Atlas","Atlas"),("IMAGES","Images","Images")))
    bpy.types.Scene.coa_atlas_resolution_x = bpy.props.IntProperty(default=1024,name="Resolution X",min=8,subtype="PIXEL")
    bpy.types.Scene.coa_atlas_resolution_y = bpy.props.IntProperty(default=1024, name="Resolution Y",min=8,subtype="PIXEL")
    bpy.types.Scene.coa_export_bake_anim = bpy.props.BoolProperty(default=False, name="Bake Animation")
    bpy.types.Scene.coa_export_bake_steps = bpy.props.IntProperty(default=1, min=1, name="Bake Steps",description="Set key every x Frame.")
    
    
    def draw(self, context):
        
        
        layout = self.layout
        self.scene = context.scene
        
        col = layout.column()
        col.prop(self.scene,"coa_project_name",text="Project Name")
        col.prop(self.scene,"coa_export_path",text="Export Path")
        
        row = col.row()
        row.prop(self.scene,"coa_export_image_mode",expand=True)
        if self.scene.coa_export_image_mode == "ATLAS":
            subcol = col.column(align=True)
            subcol.label(text="Texture Atlas Size:")
            subcol.prop(self.scene,"coa_atlas_resolution_x",text="X")
            subcol.prop(self.scene,"coa_atlas_resolution_y",text="Y")
        col.prop(self.scene,"coa_export_bake_anim")
        if self.scene.coa_export_bake_anim:
            col.prop(self.scene,"coa_export_bake_steps")    
        op = col.operator("coa_tools.export_dragon_bones")
        
        
def generate_texture_atlas(self, sprites, atlas_name, img_path, img_width=512, img_height=1024):
    global atlas_data
    atlas_data = {}
    
    context = bpy.context
    
    ### deselect all objects
    for obj in context.scene.objects:
        obj.select = False
    
    ### get a list of all sprites and containing slots    
    slots = []
    for sprite in sprites:
        if sprite.type == "MESH":    
            if sprite.coa_type == "MESH":
                slots.append({"sprite":sprite,"slot":sprite.data})
            elif sprite.coa_type == "SLOT":
                for i,slot in enumerate(sprite.coa_slot):
                    slots.append({"sprite":sprite,"slot":slot.mesh}) 
    
    ### loop over all slots and create an object with slot assigned   
    for slot in slots:
        dupli_sprite = slot["sprite"].copy()
        dupli_sprite.data = slot["slot"].copy()
        context.scene.objects.link(dupli_sprite)
        dupli_sprite.hide = False
        dupli_sprite.select = True
        context.scene.objects.active = dupli_sprite
        
        ### delete shapekeys
        if dupli_sprite.data.shape_keys != None:
            shapekeys = dupli_sprite.data.shape_keys.key_blocks
            for i in range(len(shapekeys)):
                shapekeys = dupli_sprite.data.shape_keys.key_blocks
                dupli_sprite.shape_key_remove(shapekeys[len(shapekeys)-1])
        ### apply/delete modifieres
        for modifier in dupli_sprite.modifiers:
            if modifier.name == "coa_base_sprite" and modifier.type == "MASK":
                if len(dupli_sprite.data.vertices) > 4:
                    modifier.invert_vertex_group = False
                    override = bpy.context.copy()
                    override["object"] = dupli_sprite
                    override["active_object"] = dupli_sprite
                    bpy.ops.object.modifier_apply(override, apply_as="DATA", modifier=modifier.name)   
        for modifier in dupli_sprite.modifiers:
            dupli_sprite.modifiers.remove(modifier)
                
        ### delete vertex_groups
        for group in dupli_sprite.vertex_groups:
            dupli_sprite.vertex_groups.remove(group)
            
        ### assign mesh as vertex group    
        dupli_sprite.vertex_groups.new(name=slot["slot"].name)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='SELECT')
        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                for region in area.regions:
                    if region.type == "WINDOW":
                        override = context.copy()
                        override["area"] = area
                        override["edit_object"] = dupli_sprite
                        override["active_object"] = dupli_sprite
                        override["object"] = dupli_sprite
                        override["region"] = region
                        bpy.ops.object.vertex_group_assign(override)
                        break
                        
        bpy.ops.object.mode_set(mode="OBJECT")
    
    ### join all slots into one
    bpy.ops.object.join()
    
    ### rename new object
    tex_atlas_obj = context.active_object
    tex_atlas_obj.name = "coa_tex_atlas"
    
    
    ### create atlas image
    img_atlas = bpy.data.images.new(atlas_name, width=img_width, height=img_height)
    img_atlas.generated_color = [0,0,0,0]
    
    ### assign img atlas to uvs
    for v in tex_atlas_obj.data.uv_textures.active.data:
        v.image = img_atlas
    
    
    ### create new uv map atlas
    coa_uv_atlas = tex_atlas_obj.data.uv_textures.new(name="COA_UV_ATLAS")
    coa_uv_atlas = tex_atlas_obj.data.uv_textures[coa_uv_atlas.name]
    tex_atlas_obj.data.uv_textures.active = coa_uv_atlas
    tex_atlas_obj.hide_render = False
    
    ### generate one texture atlas for all sprites
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.reveal()

    for area in context.screen.areas:
        if area.type == "VIEW_3D":
            for region in area.regions:
                if region.type == "WINDOW":
                    override = context.copy()
                    override["area"] = area
                    override["edit_object"] = context.edit_object
                    override["region"] = region
                    bpy.ops.uv.project_from_view(override, camera_bounds=False, correct_aspect=True, scale_to_bounds=False)
                    break
    
    bpy.ops.uv.select_all(action='SELECT')
    for area in context.screen.areas:
        if area.type == "VIEW_3D":
            for region in area.regions:
                if region.type == "WINDOW":
                    override = context.copy()
                    override["area"] = area
                    override["edit_object"] = context.edit_object
                    override["region"] = region
                    bpy.ops.uv.pack_islands(rotate=False, margin=.01)
                    break
    bpy.ops.object.mode_set(mode="OBJECT")
    
    ### assign img atlas to uvs
    for v in tex_atlas_obj.data.uv_textures.active.data:
        v.image = img_atlas
    ### bake uv atlas
    context.scene.render.bake_type = "TEXTURE"
    context.scene.render.use_bake_selected_to_active = False
    context.scene.render.use_bake_clear = False
    context.scene.render.bake_margin = 0

    bpy.ops.object.bake_image()
    
    ### get uv coordinates
    bpy.ops.object.mode_set(mode="EDIT")
    
    bm = bmesh.from_edit_mesh(tex_atlas_obj.data)
    uv_layer = bm.loops.layers.uv["COA_UV_ATLAS"]
    
    
    sprite_data = []
    
    for group in tex_atlas_obj.vertex_groups:
        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                for region in area.regions:
                    if region.type == "WINDOW":
                        override = context.copy()
                        override["area"] = area
                        override["edit_object"] = tex_atlas_obj
                        override["active_object"] = tex_atlas_obj
                        override["object"] = tex_atlas_obj
                        override["region"] = region
                        bpy.ops.object.vertex_group_set_active(override, group=group.name)
                        bpy.ops.mesh.select_all(action='DESELECT')
                        bpy.ops.object.vertex_group_select(override)
                        break
        bmesh.update_edit_mesh(tex_atlas_obj.data)
        x = 1.0
        y = 1.0
        width = 0.0
        height = 0.0
        for vert in bm.verts:
            if vert.select:
                uv = uv_from_vert_first(uv_layer,vert)
                x = min(uv[0],x)
                y = min(1-uv[1],y)
                width = max(uv[0],width)
                height = max(1-uv[1],height)
        width = width - x
        height = height - y
        
        x_px = int(img_width*x)
        y_px = int(img_height*y)
        width_px = abs(int(img_width*width))
        height_px = abs(int(img_height*height))
        
        sprite = {}
        sprite["name"] = group.name
        sprite["x"] = x_px
        sprite["y"] = y_px
        sprite["width"] = width_px
        sprite["height"] = height_px
        sprite_data.append(sprite)
        atlas_data[group.name] = {"width":width_px,"height":height_px}

    bpy.ops.object.mode_set(mode="OBJECT")
    ### collect sprite atlas data
    texture_atlas = {}
    texture_atlas["width"] = img_width
    texture_atlas["height"] = img_height
    texture_atlas["imagePath"] = atlas_name + "_tex.png"
    texture_atlas["name"] = self.scene.coa_project_name
    texture_atlas["SubTexture"] = sprite_data        
    
    if self.reduce_size:
        json_file = json.dumps(texture_atlas,separators=(',',':'))
    else:    
        json_file = json.dumps(texture_atlas, indent="\t", sort_keys=False)
    
    json_path = os.path.join(img_path,atlas_name+"_tex.json")
    text_file = open(json_path, "w")
    text_file.write(json_file)
    text_file.close()
         
    texture_path = os.path.join(img_path,atlas_name+"_tex.png")
    img_atlas.save_render(texture_path)
    
    
    bpy.data.objects.remove(tex_atlas_obj, do_unlink=True)