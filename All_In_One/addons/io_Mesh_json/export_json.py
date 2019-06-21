import bpy
import mathutils

import os
import os.path
import math
import operator

MAX_INFLUENCES = 3

# #####################################################
# Utils
# #####################################################

def write_file( fname, content ):
    out = open( fname, "w" )
    out.write( content )
    out.close()

def ensure_folder_exist( foldername ):
    if not os.access( foldername, os.R_OK|os.W_OK|os.X_OK ):
        os.makedirs( foldername )

def ensure_extension( filepath, extension ):
    if not filepath.lower().endswith( extension ):
        filepath += extension
    return filepath

MAT4X4 = "[%s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s, %s,%s,%s,%s]"
def mat4_string( m ):
    return MAT4X4 % ( m[0][0],m[1][0],m[2][0],m[3][0], m[0][1],m[1][1],m[2][1],m[3][1], m[0][2],m[1][2],m[2][2],m[3][2], m[0][3],m[1][3],m[2][3],m[3][3] )

def get_action_state( action, bone, frame ):
    ngroups = len( action.groups )

    pos = mathutils.Vector((0,0,0))
    rot = mathutils.Quaternion((0,0,0,1))
    scl = mathutils.Vector((1,1,1))

    if ngroups > 0:
        index = 0

        for i in range( ngroups ):
            if action.groups[i].name == bone.name:
                index = i

        for channel in action.groups[index].channels:
            value = channel.evaluate( frame )

            if "location" in channel.data_path:
                if channel.array_index == 0:
                    pos.x = value
                elif channel.array_index == 1:
                    pos.y = value
                elif channel.array_index == 2:
                    pos.z = value

            if "quaternion" in channel.data_path:
                if channel.array_index == 0:
                    rot.w = value
                elif channel.array_index == 1:
                    rot.x = value
                elif channel.array_index == 2:
                    rot.y = value
                elif channel.array_index == 3:
                    rot.z = value

            if "scale" in channel.data_path:
                if channel.array_index == 0:
                    scl.x = value
                elif channel.array_index == 1:
                    scl.y = value
                elif channel.array_index == 2:
                    scl.z = value

    pos = bone.head_local + pos
    rot = bone.matrix_local.to_quaternion() * rot
    rot.normalize()

    return pos, rot, scl

# #####################################################
# Templates - mesh
# #####################################################

TEMPLATE_FILE = """\
{
    "vertices": [%(vertices)s],
    "normals": [%(normals)s],
    "colors": [%(colors)s],
    "uvs": [%(uvs)s],
    "faces": [%(faces)s],
    "bones": [%(bones)s],
    "boneWeights": [%(boneWeights)s],
    "boneIndices": [%(boneIndices)s],
    "animations": {%(animations)s}
}
"""

TEMPLATE_KEYFRAMES  = '[ %g,%g,%g, %g,%g,%g,%g, %g,%g,%g ]'
TEMPLATE_BONE = """\
{
    "parent": %(parent)d,
    "name": "%(name)s",
    "bindPose": %(bindPose)s,
    "skinned": %(skinned)s,
    "position": [0,0,0],
    "rotation": [0,0,0,1],
    "scale": [1,1,1],
    "inheritRotation": %(inheritRotation)s,
    "inheritScale": %(inheritScale)s
}
"""

def flat_array( array ):
    return ", ".join( str( round( x, 6 ) ) for x in array )

def get_animation():
    if( len( bpy.data.armatures ) == 0 ):
        return ""

    fps = bpy.data.scenes[0].render.fps
    armature = bpy.data.armatures[0]
    animations_string = ""

    count = -1;
    action_count = len( bpy.data.actions ) - 1

    for action in bpy.data.actions:
        count += 1

        end_frame = int( action.frame_range[1] )
        start_frame = int( action.frame_range[0] )
        frame_length = int( end_frame - start_frame )

        frames = []

        for frame in range( frame_length ):
            key_frame = []

            for hierarchy in armature.bones:
                pos, rot, scl = get_action_state( action, hierarchy, frame )

                px, py, pz = pos.x, pos.y, pos.z
                rx, ry, rz, rw = rot.x, rot.y, rot.z, rot.w
                sx, sy, sz = scl.x, scl.y, scl.z

                bone_frame = TEMPLATE_KEYFRAMES % ( px, py, pz, rx, ry, rz, rw, sx, sy, sz )
                key_frame.append( bone_frame )

            key_frame_string = "[%s]" % ",".join( key_frame )
            frames.append( key_frame_string );

        frame_string = ",".join( frames )
        animations_string += '"%s": [%s]' % ( action.name, frame_string )

        if( count < action_count ):
            animations_string += ","
    return animations_string


def get_mesh_string( obj ):
    mesh = obj.to_mesh( bpy.context.scene, True, "PREVIEW" )

    vertices = []
    normals = []
    colors = []
    uvs = []
    indices = []
    bones = []
    boneIndices = []
    boneWeights = []

    vertex_number = -1
    for face in obj.data.polygons:
        vertices_in_face = face.vertices[:]

        for vertex in vertices_in_face:

            vertex_number += 1

            vertices.append( obj.data.vertices[ vertex ].co.x )
            vertices.append( obj.data.vertices[ vertex ].co.y )
            vertices.append( obj.data.vertices[ vertex ].co.z )

            normals.append( obj.data.vertices[ vertex ].normal.x )
            normals.append( obj.data.vertices[ vertex ].normal.y )
            normals.append( obj.data.vertices[ vertex ].normal.z )

            indices.append( vertex_number )

    if len( mesh.tessface_uv_textures ) > 0:
        for data in mesh.tessface_uv_textures.active.data:
            uvs.append( data.uv1.x )
            uvs.append( data.uv1.y )
            uvs.append( data.uv2.x )
            uvs.append( data.uv2.y )
            uvs.append( data.uv3.x )
            uvs.append( data.uv3.y )

    if len( mesh.tessface_vertex_colors ) > 0:
        for data in mesh.tessface_vertex_colors.active.data:
            colors.append( data.color1.r )
            colors.append( data.color1.g )
            colors.append( data.color1.b )
            colors.append( data.color2.r )
            colors.append( data.color2.g )
            colors.append( data.color2.b )
            colors.append( data.color3.r )
            colors.append( data.color3.g )
            colors.append( data.color3.b )

    if( len( bpy.data.armatures ) > 0 ):
        armature = bpy.data.armatures[0]

        for face in obj.data.polygons:
            vertices_in_face = face.vertices[:]

            for vertex_index in vertices_in_face:
                vertex = obj.data.vertices[ vertex_index ]
                bone_array = []

                for group in vertex.groups:
                    index = group.group
                    weight = group.weight

                    bone_array.append( (index, weight) )

                for i in range( MAX_INFLUENCES ):

                    if i < len( bone_array ):
                        bone_proxy = bone_array[i]

                        found = 0
                        index = bone_proxy[0]
                        weight = bone_proxy[1]

                        for j, bone in enumerate( armature.bones ):
                            if obj.vertex_groups[ index ].name == bone.name:
                                boneIndices.append("%d" % j )
                                boneWeights.append("%g" % weight )
                                found = 1
                                break

                        if found != 1:
                            boneIndices.append("0")
                            boneWeights.append("0")
                    else:
                        boneIndices.append("0")
                        boneWeights.append("0")

        bone_id = -1
        for bone in armature.bones:
            bone_id += 1

            parent_index = -1
            weight = 0
            skinned = "false"
            inheritRotation = "false"
            inheritScale = "false"

            pos = bone.head

            if bone.parent != None:
                parent_index = i = 0
                pos = bone.head_local - bone.parent.head_local

                for parent in armature.bones:
                    if parent.name == bone.parent.name:
                        parent_index = i
                    i += 1

            j = -1
            for boneIndex in boneIndices:
                j += 1
                if int( boneIndex ) == bone_id:
                    weight += float( boneWeights[j] )

            if weight > 0:
                skinned = "true"

            if bone.use_inherit_rotation:
                inheritRotation = "true"

            if bone.use_inherit_scale:
                inheritScale = "true"

            name = bone.name
            bindPose = bone.matrix_local.inverted()

            bones.append(TEMPLATE_BONE % {
                "parent": parent_index,
                "name": name,
                "bindPose": mat4_string( bindPose ),
                "skinned": skinned,
                "inheritRotation": inheritRotation,
                "inheritScale": inheritScale,
            })

    return TEMPLATE_FILE % {
        "vertices": flat_array( vertices ),
        "normals":  flat_array( normals ),
        "colors": flat_array( colors ),
        "uvs": flat_array( uvs ),
        "faces": flat_array( indices ),
        "bones": ",".join( bones ),
        "boneIndices": ",".join( boneIndices ),
        "boneWeights": ",".join( boneWeights ),
        "animations": get_animation()
    }



def export_mesh( obj, filepath ):
    text = get_mesh_string( obj )
    write_file( filepath, text )

    print("writing", filepath, "done")


# #####################################################
# Main
# #####################################################

def save( operator, context, filepath = "" ):
    filepath = ensure_extension( filepath, ".json")

    bpy.ops.object.duplicate()
    bpy.ops.object.mode_set( mode = "OBJECT" )
    bpy.ops.object.modifier_add( type="TRIANGULATE" )
    bpy.ops.object.modifier_apply( apply_as = "DATA", modifier = "Triangulate" )

    export_mesh( context.active_object, filepath )
    bpy.ops.object.delete()

    return {"FINISHED"}
