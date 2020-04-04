bl_info = {
    "name": "Export Ono3dObject (.o3o)",
    "author": "ono",
    "version": (0,0,1),
    "blender": (2, 80, 0),
    "location": "File > Export > Ono3dObject (.o3o)",
    "description": "Export Ono3dObject (.o3o)",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
    }

#g_magicCode = "Ono3dObject"
#g_version = "0.13"

import math 
import json
import collections

import os
from math import radians
import bpy
from mathutils import *

import re

config = ""
class Ono3dObjectExporterSettings:
    def __init__(self,
                 context,
                 FilePath,
                 ):
        self.context = context
        self.FilePath = FilePath

def fileout(content):
    config.File.write('{}{}'.format("  " * config.Whitespace,content))

def fileout2(content):
    config.File.write(content)

def fileoutLu():
    fileout2('[\n')
    config.Whitespace+=1

def fileoutLd():
    config.Whitespace-=1
    fileout(']\n')

def fileoutMu():
    fileout2('{\n')
    config.Whitespace+=1

def fileoutMd():
    config.Whitespace-=1
    fileout('}\n')

def ExportOno3dObject():
    config.File = open(config.FilePath, "w")

    config.Whitespace=0
    fileout2('{"format":"Ono3dObject Version 0.2"\n')

#    fileout(',"textures":')
#    fileoutLu()
#    for a in bpy.data.textures:
#        fileout('')
#        if(a != bpy.data.textures[0]):fileout2(',')
#        WriteTexture(a)
#    fileoutLd()

    fileout(',"materials":');
    fileoutLu()
    for material in bpy.data.materials:
        fileout('')
        if(material != bpy.data.materials[0]):fileout2(',')
        WriteMaterial(material)
    fileoutLd()
    
    a = [Object for Object in bpy.data.meshes if Object.name.find("@") != 0 ]
    fileout(',"meshes":')
    fileoutLu()
    for mesh in a:
        fileout('')
        if(mesh!= a[0]):fileout2(',')
        WriteMesh(mesh)
    fileoutLd()

    fileout(',"lights":')
    fileoutLu()
    for light in bpy.data.lights:
        fileout('')
        if(light!= bpy.data.lights[0]):fileout2(',')
        WriteLight(light)
    fileout('')
    fileoutLd()

#    a = [Object for Object in bpy.data.meshes if Object.name.find("@") == 0 ]
#    fileout('"Collisions":')
#    fileoutLu()
#    for mesh in a:
#        WriteColligion(mesh)
#    fileoutLd()

    a = bpy.data.armatures
    fileout(',"armatures":')
    fileoutLu()
    for Object in a:
        if(a[0] != Object):fileout2(',')
        WriteArmatureBones(Object)
    fileoutLd()

    fileout(',"framerate":{}\n'.format(int(bpy.context.scene.render.fps / bpy.context.scene.render.fps_base)))
    fileout(',"actions":')
    fileoutLu()
    for a in bpy.data.actions:
        fileout('')
        if(a!= bpy.data.actions[0]):fileout2(',')
        WriteAction(a)

    fileoutLd()

    fileout(',"objects":')
    fileoutLu()
    for obj in bpy.data.objects:
        fileout('')
        if(obj!= bpy.data.objects[0]):fileout2(',')
        fileoutMu()

        fileout('"name":"{}"\n'.format(obj.name))
        if(obj.hide_render == True): fileout(',"hide_render": 1\n')
        fileout(',"groups":[')
        for group in obj.vertex_groups:
            if(group != obj.vertex_groups[0]):fileout2(',')
            fileout2('"{}"'.format(group.name))
        fileout2(']\n')

        pose = obj.pose
        if(pose):
            fileout(',"poseBones":')
            fileoutLu()
            for bone in pose.bones:
               fileout('')
               if(bone!= pose.bones[0]):fileout2(',')
               fileout2('{')
               fileout2('"name":"{}"'.format(bone.name))
               fileout2(',"target":"{}"'.format(bone.bone.name))
               if(bone.parent):
                   fileout2(',"parent":"{}"'.format(bone.parent.name))
               fileout2(',"location":[{:9f},{:9f},{:9f}]'.format( bone.location[0],bone.location[1],bone.location[2]))
               fileout2(',"rotation":[{:9f},{:9f},{:9f},{:9f}]'.format( bone.rotation_quaternion[0],bone.rotation_quaternion[1],bone.rotation_quaternion[2],bone.rotation_quaternion[3]))
               fileout2(',"scale":[{:9f},{:9f},{:9f}]'.format( bone.scale[0],bone.scale[1],bone.scale[2]))
               fileout2('}\n')
            fileoutLd()

        fileout(',"location":[{:9f},{:9f},{:9f}]\n'.format(obj.location[0],obj.location[1],obj.location[2]))
        if(obj.rotation_mode == "QUATERNION"):
            fileout(',"rotation":[{:9f},{:9f},{:9f},{:9f}]\n'.format(obj.rotation_quaternion[0],obj.rotation_quaternion[1],obj.rotation_quaternion[2],obj.rotation_quaternion[3]))
        else:
            fileout(',"rotation":[{:9f},{:9f},{:9f}]\n'.format(obj.rotation_euler[0],obj.rotation_euler[1],obj.rotation_euler[2]))
        
        fileout(',"scale":[{:9f},{:9f},{:9f}]\n'.format(obj.scale[0],obj.scale[1],obj.scale[2]))
        if(obj.matrix_basis):
            fileout(',"matrix":{}\n'.format(stringMatrix43(obj.matrix_basis)))
        if(obj.parent):
            fileout(',"parent":"{}"\n'.format(obj.parent.name))
            if(obj.parent_bone):
                fileout(',"parent_bone":"{}"\n'.format(obj.parent_bone))
            fileout(',"iparentmatrix":{}\n'.format(stringMatrix43(obj.matrix_parent_inverse)))
        fileout(',"type":"{}"\n'.format(obj.type))
        if(obj.data):
            fileout(',"data":"{}"\n'.format(obj.data.name))
        if(obj.animation_data):
            if(obj.animation_data.action):
               fileout(',"action":"{}"\n'.format(obj.animation_data.action.name))
        if(obj.rigid_body):
            fileout(',"rigid_body":')
            fileoutMu()
            fileout('"type":"{}"\n'.format(obj.rigid_body.type))
            fileout(',"mass":{}\n'.format(obj.rigid_body.mass))
            fileout(',"collision_shape":"{}"\n'.format(obj.rigid_body.collision_shape))
            fileout(',"friction":{:9f}\n'.format(obj.rigid_body.friction))
            fileout(',"restitution":{:9f}\n'.format(obj.rigid_body.restitution))
            collision_groups=0
            for num in range(20):
                collision_groups|= (obj.rigid_body.collision_collections[num] << num)
            fileout(',"collision_groups":{}\n'.format(collision_groups))
            fileoutMd()
        if(obj.rigid_body_constraint):
            rbc=obj.rigid_body_constraint
            fileout(',"rigid_body_constraint":')
            fileoutMu()
            fileout('"breaking_threshold":{:9f}\n'.format(0+rbc.breaking_threshold))
            fileout(',"disable_collisions":{}\n'.format(0+rbc.disable_collisions))
            fileout(',"enabled":{}\n'.format(0+rbc.enabled))
            fileout(',"limit_ang_lower":[{:9f},{:9f},{:9f}]\n'.format(rbc.limit_ang_x_lower,rbc.limit_ang_y_lower,rbc.limit_ang_z_lower))
            fileout(',"limit_ang_upper":[{:9f},{:9f},{:9f}]\n'.format(rbc.limit_ang_x_upper,rbc.limit_ang_y_upper,rbc.limit_ang_z_upper))
            fileout(',"limit_lin_lower":[{:9f},{:9f},{:9f}]\n'.format(rbc.limit_lin_x_lower,rbc.limit_lin_y_lower,rbc.limit_lin_z_lower))
            fileout(',"limit_lin_upper":[{:9f},{:9f},{:9f}]\n'.format(rbc.limit_lin_x_upper,rbc.limit_lin_y_upper,rbc.limit_lin_z_upper))
            fileout(',"motor_ang_max_impulse":{:9f}\n'.format(rbc.motor_ang_max_impulse))
            fileout(',"motor_ang_target_velocity":{:9f}\n'.format(rbc.motor_ang_target_velocity))
            fileout(',"motor_lin_max_impulse":{:9f}\n'.format(rbc.motor_lin_max_impulse))
            fileout(',"motor_lin_target_velocity":{:9f}\n'.format(rbc.motor_lin_target_velocity))
            if(rbc.object1):
                fileout(',"object1":"{}"\n'.format(rbc.object1.name))
            if(rbc.object2):
                fileout(',"object2":"{}"\n'.format(rbc.object2.name))
            fileout(',"spring_damping":[{:9f},{:9f},{:9f}]\n'.format(rbc.spring_damping_x,rbc.spring_damping_y,rbc.spring_damping_z))
            fileout(',"spring_stiffness":[{:9f},{:9f},{:9f}]\n'.format(rbc.spring_stiffness_x,rbc.spring_stiffness_y,rbc.spring_stiffness_z))
            fileout(',"spring_damping_ang":[{:9f},{:9f},{:9f}]\n'.format(rbc.spring_damping_ang_x,rbc.spring_damping_ang_y,rbc.spring_damping_ang_z))
            fileout(',"spring_stiffness_ang":[{:9f},{:9f},{:9f}]\n'.format(rbc.spring_stiffness_ang_x,rbc.spring_stiffness_ang_y,rbc.spring_stiffness_ang_z))
            fileout(',"use_breaking":{}\n'.format(0+rbc.use_breaking))
            fileout(',"use_limit_ang":[{},{},{}]\n'.format(0+rbc.use_limit_ang_x,0+rbc.use_limit_ang_y,0+rbc.use_limit_ang_z))
            fileout(',"use_limit_lin":[{},{},{}]\n'.format(0+rbc.use_limit_lin_x,0+rbc.use_limit_lin_y,0+rbc.use_limit_lin_z))
            fileout(',"use_motor_ang":{}\n'.format(0+rbc.use_motor_ang))
            fileout(',"use_motor_lin":{}\n'.format(0+rbc.use_motor_lin))
            fileout(',"use_spring":[{},{},{}]\n'.format(0+rbc.use_spring_x,0+rbc.use_spring_y,0+rbc.use_spring_z))
            fileout(',"use_spring_ang":[{},{},{}]\n'.format(0+rbc.use_spring_ang_x,0+rbc.use_spring_ang_y,0+rbc.use_spring_ang_z))
            fileout(',"type":"{}"\n'.format(rbc.type))
            fileoutMd()
        b = obj.bound_box
        fileout(',"bound_box":[{:9f},{:9f},{:9f},{:9f},{:9f},{:9f}]\n'.format(b[0][0],b[0][1],b[0][2],b[6][0],b[6][1],b[6][2]))
        fileout(',"bound_type":"{}"\n'.format(obj.display_bounds_type))
        fileout(',"modifiers":')
        fileoutLu()
        for modifier in obj.modifiers:
            fileout('')
            if(modifier != obj.modifiers[0]):fileout2(',')
            fileout2('{')
            fileout2('"name":"{}"'.format(modifier.name))
            fileout2(',"type":"{}"'.format(modifier.type))
            if(modifier.type=="ARMATURE" ):
                if(modifier.object!=None ):
                    fileout2(',"object":"{}"'.format(modifier.object.name))
                    fileout2(',"vertex_group":"{}"'.format(modifier.vertex_group))
            elif(modifier.type=="MESH_DEFORM" ):
                fileout2(',"object":"{}"'.format(modifier.object.name))
            elif(modifier.type=="CLOTH" ):
                fileout2(',"pin":"{}"'.format(modifier.settings.vertex_group_mass))
                fileout2(',"mass":{}'.format(modifier.settings.mass))
                fileout2(',"structual_stiffness":{}'.format(modifier.settings.tension_stiffness))
                fileout2(',"bending_stiffness":{}'.format(modifier.settings.bending_stiffness))
                fileout2(',"spring_damping":{}'.format(modifier.settings.tension_damping))
                fileout2(',"air_damping":{}'.format(modifier.settings.air_damping))
            elif(modifier.type=="SOFT_BODY" ):
                fileout2(',"friction":{:9f}'.format(modifier.settings.friction))
                fileout2(',"mass":{:9f}'.format(modifier.settings.mass))
                fileout2(',"speed":{:9f}'.format(modifier.settings.speed))
                fileout2(',"goalDefault":{:9f}'.format(modifier.settings.goal_default))
                fileout2(',"goalMin":{:9f}'.format(modifier.settings.goal_min))
                fileout2(',"goalMax":{:9f}'.format(modifier.settings.goal_max))
                fileout2(',"goalSpring":{:9f}'.format(modifier.settings.goal_spring))
                fileout2(',"goalFriction":{:9f}'.format(modifier.settings.goal_friction))
                fileout2(',"pin":"{}"'.format(modifier.settings.vertex_group_goal))
                fileout2(',"pull":{:9f}'.format(modifier.settings.pull))
                fileout2(',"push":{:9f}'.format(modifier.settings.push))
                fileout2(',"damping":{:9f}'.format(modifier.settings.damping))
                fileout2(',"bend":{:9f}'.format(modifier.settings.bend))
            elif(modifier.type=="MIRROR" ):
                fileout2(',"use_x":{}'.format(int(modifier.use_axis[0])))
                fileout2(',"use_y":{}'.format(int(modifier.use_axis[1])))
                fileout2(',"use_z":{}'.format(int(modifier.use_axis[2])))
            fileout2('}\n')
        fileoutLd()
        fileoutMd()
    fileoutLd()

#    fileout(',"collections":')
#    fileoutLu()
#    for collection in bpy.data.collections:
#        fileout('')
#        if(collection != bpy.data.collections[0]):fileout2(',')
#        fileoutMu()
#        fileout('"name":"{}"\n'.format(collection.name))
#        fileout('"objects":[\n');
#        for object in collection.objects:
#            if(object != collection.objects[0]):fileout2(',')
#            fileout('"{}"'.format(object.name))
#        fileout2(']\n');
#        fileoutMd()
#    fileoutLd()

    fileout(',"scenes":')
    fileoutLu()
    for scene in bpy.data.scenes:
        fileout('')
        if(scene!= bpy.data.scenes[0]):fileout2(',')
        WriteScene(scene)

    fileoutLd()


    fileout('}')
    config.File.close()
    print("Finished")

def stringMatrix44(matrix):
    return '[{:9f},{:9f},{:9f},{:9f},{:9f},{:9f},{:9f},{:9f},{:9f},{:9f},{:9f},{:9f},{:9f},{:9f},{:9f},{:9f}]'.format(
         matrix[0][0], matrix[1][0], matrix[2][0], matrix[3][0]
        ,matrix[0][1], matrix[1][1], matrix[2][1], matrix[3][1]
        ,matrix[0][2], matrix[1][2], matrix[2][2], matrix[3][2]
        ,matrix[0][3], matrix[1][3], matrix[2][3], matrix[3][3])
def stringMatrix43(matrix):
    return '[{:9f},{:9f},{:9f},{:9f},{:9f},{:9f},{:9f},{:9f},{:9f},{:9f},{:9f},{:9f}]'.format(
         matrix[0][0], matrix[1][0], matrix[2][0]
        ,matrix[0][1], matrix[1][1], matrix[2][1]
        ,matrix[0][2], matrix[1][2], matrix[2][2]
        ,matrix[0][3], matrix[1][3], matrix[2][3])


def WriteTexture(Texture=None):
    if Texture is None :return
        
    fileout2('{')
    fileout2('"name":"{}"'.format(Texture.name))
    fileout2(',"typ":"{}"'.format(Texture.type))
    if(Texture.type == "IMAGE"):
        fileout2(',"path":"{}"'.format(Texture.image.filepath))
    fileout2('}\n')

def fValue( obj ):
    if(type(obj) in (str,int,float)): return obj
    else: return [p for p in obj]
    
def WriteMaterial( Material=None):
    if Material is None :return
    dict = collections.OrderedDict()
    
    dict["name"] = Material.name

    if(Material.use_nodes):
        nodes = Material.node_tree.nodes
        targets=[node for node in nodes if node.bl_idname == "ShaderNodeBsdfPrincipled"]
        if(len(targets)>0):
            node = targets[0]
            inputs= node.inputs

            dict["baseColor"] = inputs[0].default_value[0:3]
            dict["opacity"] = inputs[0].default_value[3]
            dict["metallic"] = inputs[4].default_value
            dict["roughness"] = inputs[7].default_value
            dict["ior"] = inputs[14].default_value
            dict["opacity"] = 1.0 -inputs[15].default_value
            dict["subRoughness"] = inputs[16].default_value

        if('pbrColor' in nodes):
            inputs = nodes['pbrColor'].inputs

            dict["metallic"] = inputs[1].default_value[0]
            dict["roughness"] = inputs[1].default_value[1]
            dict["subRoughness"] = inputs[1].default_value[2]

        if('ior' in nodes):
            inputs = nodes['ior'].inputs
            dict["ior"] = inputs[0].default_value

        if('baseColorTexture' in nodes):
            node = nodes['baseColorTexture']
            dict["baseColorMap"] = node.image.filepath

        if('pbrTexture' in nodes):
            node = nodes['pbrTexture']
            dict["pbrMap"] = node.image.filepath

        if('hightTexture' in nodes):
            node = nodes['hightTexture']
            dict["hightMap"] = node.image.filepath

        if('Bump' in nodes):
            inputs = nodes['Bump'].inputs
            dict["hightMapPower"] = inputs[0].default_value

        if('LightMap' in nodes):
            node = nodes['LightMap']
            dict["lightMap"] = node.image.filepath


    for key in Material.keys():
        if(key == "_RNA_UI" or key == "cycles"):continue
        dict[key] = fValue(Material.get(key))
    
    if(Material.animation_data):
        if(Material.animation_data.action):
            texture["action"] = Material.animation_data.action.name
    fileout(json.dumps(dict,ensure_ascii=False))
    fileout2('\n')


def WriteArmatureBones(Armature):
    import mathutils
    fileoutMu()
    fileout('"name":"{}" \n'.format( Armature.name))

    Bones = Armature.bones
    fileout(',"bones":')
    fileoutLu()
    for Bone in Bones:
        fileout('')
        if(Bones[0] != Bone):fileout2(',')
        fileoutMu()
        fileout('"name":"{}" \n'.format( Bone.name))
        if(Bone.parent):
            fileout(',"parent":"{}" \n'.format( Bone.parent.name))

        DataBone = Bones[Bone.name]
        BoneMatrix = DataBone.matrix_local

        fileout2(',"matrix":{}\n'.format(stringMatrix43(DataBone.matrix_local)))

        fileout(',"length":{:9f} \n'.format( Bone.length))

        fileoutMd()
    fileoutLd()
    fileoutMd()

def WriteLight(light):
    dict = collections.OrderedDict()
    dict["name"] = light.name
    dict["type"] = light.type
    dict["color"] = light.color[:]

    fileout(json.dumps(dict,ensure_ascii=False))
	

def WriteMesh(mesh):
    import mathutils
    Index = 0

    fileoutMu()
    sp = mesh.name.split("|");
    fileout('"name":"{}"\n'.format(mesh.name))
    if mesh.show_double_sided & config.EnableDoubleSided:
        fileout(',"double_sided":1\n')
    if mesh.shape_keys:
        fileout(',"shapeKeys":')
        fileoutLu()
        for shapeKey in mesh.shape_keys.key_blocks:
            fileout('')
            if(shapeKey != mesh.shape_keys.key_blocks[0]):fileout2(',')
            fileoutMu()
            fileout('"name":"{}"\n'.format(shapeKey.name ))
            fileout(',"shapeKeyPoints":')
            fileoutLu()
            for shapeKeyPoint in shapeKey.data:
                fileout('')
                if(shapeKeyPoint != shapeKey.data[0]):fileout2(',')
                fileout2('{')
                fileout2('"pos":[{:9f},{:9f},{:9f}]'.format(shapeKeyPoint.co[0], shapeKeyPoint.co[1], shapeKeyPoint.co[2]))
                fileout2('}\n')
            fileoutLd()
            fileoutMd()
        fileoutLd()
        
    

    fileout(',"vertices":')
    fileoutLu()
    for Vertex in mesh.vertices:
        Position = Vertex.co
        fileout('')
        if(Vertex != mesh.vertices[0]):fileout2(',')
        fileout2('{')
        fileout2('"pos":[{:9f},{:9f},{:9f}]'.format(Position[0], Position[1], Position[2]))
        weightmax = 0
        for group in Vertex.groups:
            weightmax += group.weight
        if len(Vertex.groups)>0:
            fileout2(',"groups":[')
            Index=0
            for group in Vertex.groups:
                if(group != Vertex.groups[0]):fileout2(',')
                fileout2('{}'.format(group.group))
                Index+=1
            fileout2(']')
            Index=0
            if(len(Vertex.groups)> 1):
                fileout2(',"groupWeights":[')
                for group in Vertex.groups:
                    if(group != Vertex.groups[0]):fileout2(',')
                    fileout2('{:9f}'.format(group.weight/weightmax))
                    Index+=1
                fileout2(']')
        fileout2('}\n')
    fileoutLd()

#    fileout(',"Edges":')
#    fileoutLu()
#    fileout('')
#    for i,edge in enumerate(mesh.edges):
#        fileout2('{},{}'.format( edge.vertices[0],edge.vertices[1]))
#        if(i<len(mesh.edges)-1):
#            fileout2(',");
#        else:
#            fileout2('\n');
#    fileoutLd()

    fileout(',"faces":')
    fileoutLu()
    faceIndex = 0
    faceIndex = 0
    for Face in mesh.polygons:
        fileout('')
        if(Face!= mesh.polygons[0]):fileout2(',')
        fileout2('{')
        fileout2('"idx":[')
        Index = 0
        for Vertex in Face.vertices:
            if(Vertex != Face.vertices[0]):fileout2(',')
            fileout2('{}'.format(Vertex))
            Index+=1
        fileout2(']')
        if(Face.use_freestyle_mark):
            fileout2(',"fs":1')
        
#        Normal = Face.normal
#        fileout2('normal:{:9f},{:9f},{:9f},'.format(Normal[0], Normal[1], Normal[2]))
        if Face.material_index < len(mesh.materials):
            if mesh.materials[Face.material_index] != None:
                fileout2(',"mat":{}'.format(bpy.data.materials.keys().index(mesh.materials[Face.material_index].name)))
        fileout2('}\n')
        faceIndex += 1
    fileoutLd()
    fileout(',"uv_layers":')
    fileoutLu()
    for uv_layer in mesh.uv_layers:
        uv = uv_layer.data
        if len(uv)<=0 :continue
        fileout('')
        if(uv_layer != mesh.uv_layers[0]):fileout2(',')
        fileoutMu()
        fileout('"name":"{}"\n'.format(uv_layer.name ))
        fileout(',"data":')
        fileoutLu()
        uvIndex = 0
        for polygon in mesh.polygons:
            if(polygon != mesh.polygons[0]):fileout(',[')
            else: fileout('[')
            for loop_index in range(polygon.loop_start, polygon.loop_start + polygon.loop_total):
                if(loop_index != polygon.loop_start):fileout2(',')
                fileout2('{:9f},{:9f}'.format( uv[loop_index].uv[0], 1 - uv[loop_index].uv[1]))
                uvIndex+=1
            fileout2(']\n')
        fileoutLd()
        fileoutMd()
    fileoutLd()

    fileoutMd()


def WriteAction(action):
    fileoutMu()
    fileout('"name":"{}"\n'.format(action.name))
    fileout(',"endframe":{}\n'.format(int(action.frame_range[1])))
    fileout(',"id_root":"{}"\n'.format(action.id_root))
    fcurvesize = 0
    i = 0

    fileout(',"fcurves":')
    fileoutLu()
    i = 0
    while i < len(action.fcurves):
        fileout('')
        if(i!=0):fileout2(',')
        fileout2('{')
        fcurve = action.fcurves[i]
        ii = 0
        p = re.search('\["(.+)"\]\.(.+)$',fcurve.data_path)
        if(not p):
            p = re.search('\[(.+)\]\.(.+)$',fcurve.data_path)
        if(p):
            pflg = p.group(2)
        else:
            pflg = fcurve.data_path
        target=""
        if p:
            target=p.group(1)
#        fileout('type:{}\n'.format(pflg))
#        fileout('data_path:{}\n'.format(fcurve.data_path))
#        fileout(',"keyframes":')
#        fileoutLu()
        fileout2('"target":"{}"'.format(target))
        if(pflg == "rotation_quaternion"):
            fileout2(',"type":"{}","idx":0,"keys":['.format(pflg))
            xi=0;yi=0;zi=0;
            pw=action.fcurves[i].keyframe_points;
            px=action.fcurves[i+1].keyframe_points;
            py=action.fcurves[i+2].keyframe_points;
            pz=action.fcurves[i+3].keyframe_points;
            for keyframe_points in fcurve.keyframe_points:
                if(keyframe_points != fcurve.keyframe_points[0]):fileout2(',')
                keytime=pw[ii].co[0]
                if(len(px)>xi+1 and keytime==int(px[xi+1].co[0]) ): xi=xi+1;
                if(len(py)>yi+1 and keytime==int(py[yi+1].co[0]) ): yi=yi+1;
                if(len(pz)>zi+1 and keytime==int(pz[zi+1].co[0]) ): zi=zi+1;
                fileout2('{')
                fileout2('"f":{},"p":[{:9f},{:9f},{:9f},{:9f}]'.format(
                int(keytime)
                ,pw[ii].co[1]
                ,px[xi].co[1]
                ,py[yi].co[1]
                ,pz[zi].co[1]));
                fileout2('}')
                ii +=1;
            fileout2(']')
            i += 4
        else:
            fileout2(',"type":"{}","idx":{},"keys":['.format(pflg,fcurve.array_index))
            for keyframe_points in fcurve.keyframe_points:
                if(keyframe_points != fcurve.keyframe_points[0]):fileout2(',')
                fileout2('{')
                fileout2('"f":{},"p":{:9f}'.format(int(keyframe_points.co[0]),keyframe_points.co[1]))
                fileout2('}')
            fileout2(']')
            i += 1
        fileout2('}\n')
#        fileoutLd()
#        fileoutMd()
    fileoutLd()
    fileoutMd()

def WriteScene(scene):
    fileoutMu()
    fileout('"name":"{}"\n'.format(scene.name))
    fileout(',"frame_start":{}\n'.format(scene.frame_start))
    fileout(',"frame_end":{}\n'.format(scene.frame_end))

    a = scene.objects
    fileout(',"objects":[')
#    fileoutLu()
    for obj in scene.objects:
        if(obj != scene.objects[0]):fileout2(',')
        fileout2('"{}"'.format(obj.name));
    fileout2(']\n')

    world = scene.world
    fileout(',"world":')
    fileoutMu()
    fileout('"name":"{}"\n'.format(world.name));
    nodes = world.node_tree.nodes

    if('envTexture' in nodes):
        node = nodes['envTexture']
        fileout(',"envTexture":"//{}"\n'.format(re.search("[^/]*$",node.image.filepath).group(0)))

    fileoutMd()
#fileoutLd()
    fileoutMd()


from bpy.props import *
class Ono3dObjectExporter(bpy.types.Operator):
    """Export to the Ono3dObject format (.o3o)"""

    bl_idname = "export.ono3o"
    bl_label = "Export Ono3dObject"
    filter_glob = StringProperty(default="*.o3o",options={'HIDDEN'})
    filepath = StringProperty(subtype='FILE_PATH')

    EnableDoubleSided = BoolProperty(name="Enable Double Sided", description="enable double sided", default=False)

    def execute(self, context):
        FilePath = self.filepath
        if not FilePath.lower().endswith(".o3o"):
            FilePath += ".o3o"
        global config
        config = Ono3dObjectExporterSettings(context,
                                         FilePath)
        config.EnableDoubleSided=self.EnableDoubleSided
        ExportOno3dObject()
        return {"FINISHED"}

    def invoke(self, context, event):
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}


def menu_func(self, context):
    default_path = os.path.splitext(bpy.data.filepath)[0] + ".o3o"
    self.layout.operator(Ono3dObjectExporter.bl_idname, text="Ono3dObject (.o3o)").filepath = default_path


classes = (
	Ono3dObjectExporter,
)
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_export.append(menu_func)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func)
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()

