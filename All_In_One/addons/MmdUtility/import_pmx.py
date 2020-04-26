# coding: utf-8
"""
PMXモデルをインポートする。

1マテリアル、1オブジェクトで作成する。
PMDはPMXに変換してからインポートする。
"""

from .pymeshio import pmx

import bpy_extras
import mathutils
import os
print("imported modules: "+__name__)

if "bpy" in locals():
    import imp
    imp.reload(bl)
else:
    from . import bl
import bpy


def createEmpty(scene, name):
    empty=bpy.data.objects.new(name, None)
    scene.objects.link(empty)
    return empty

def assignVertexGroup(o, name, index, weight):
    if name not in o.vertex_groups:
        o.vertex_groups.new(name)
    o.vertex_groups[name].add([index], weight, 'ADD')

def createBoneGroup(scene, o, name, color_set='DEFAULT'):
    # create group
    o.select=True 
    scene.objects.active=o
    bpy.ops.object.mode_set(mode='POSE', toggle=False)
    bpy.ops.pose.group_add()
    # set name
    pose=o.pose
    g=pose.bone_groups.active
    g.name=name
    g.color_set=color_set
    return g

def createTexture(path):
    texture=bpy.data.textures.new(os.path.basename(path), 'IMAGE')
    texture.use_mipmap=True
    texture.use_interpolation=True
    texture.use_alpha=True
    try:
        image=bpy.data.images.load(path)
    except RuntimeError:
        print('fail to create:', path)
        image=bpy.data.images.new('Image', width=16, height=16)
    texture.image=image
    return texture, image

def addTexture(material, texture, enable=True, blend_type='MULTIPLY'):
    # search free slot
    index=None
    for i, slot in enumerate(material.texture_slots):
        if not slot:
            index=i
            break
    if index==None:
        return
    material.use_shadeless=True
    #
    slot=material.texture_slots.create(index)
    slot.texture=texture
    slot.texture_coords='UV'
    slot.blend_type=blend_type
    slot.use_map_alpha=True
    slot.use=enable
    return index

def createMesh(scene, name):
    mesh=bpy.data.meshes.new("Mesh")
    mesh_object= bpy.data.objects.new(name, mesh)
    scene.objects.link(mesh_object)
    return mesh, mesh_object

def addGeometry(mesh, vertices, faces):
    from bpy_extras.io_utils import unpack_list, unpack_face_list
    mesh.vertices.add(len(vertices))
    mesh.vertices.foreach_set("co", unpack_list(vertices))
    mesh.tessfaces.add(len(faces))
    mesh.tessfaces.foreach_set("vertices_raw", unpack_face_list(faces))
    #mesh.from_pydata(vertices, [], faces)
    """
    mesh.add_geometry(len(vertices), 0, len(faces))
    # add vertex
    unpackedVertices=[]
    for v in vertices:
        unpackedVertices.extend(v)
    mesh.vertices.foreach_set("co", unpackedVertices)
    # add face
    unpackedFaces = []
    for face in faces:
        if len(face) == 4:
            if face[3] == 0:
                # rotate indices if the 4th is 0
                face = [face[3], face[0], face[1], face[2]]
        elif len(face) == 3:
            if face[2] == 0:
                # rotate indices if the 3rd is 0
                face = [face[2], face[0], face[1], 0]
            else:
                face.append(0)
        unpackedFaces.extend(face)
    mesh.faces.foreach_set("verts_raw", unpackedFaces)
    """
    assert(len(vertices)==len(mesh.vertices))
    #assert(len(faces)==len(cls.getFaces(mesh)))

def setFaceUV(m, i, face, uv_array, image):
    uv_face=m.tessface_uv_textures[0].data[i]
    uv_face.uv=uv_array
    if image:
        uv_face.image=image
        #uv_face.use_image=True

def createArmature(scene):
    armature = bpy.data.armatures.new('Armature')
    armature_object=bpy.data.objects.new('Armature', armature)
    scene.objects.link(armature_object)

    armature_object.show_x_ray=True
    armature.show_names=True
    #armature.draw_type='OCTAHEDRAL'
    armature.draw_type='STICK'
    #armature.use_deform_envelopes=False
    #armature.use_deform_vertex_groups=True
    #armature.use_mirror_x=True

    return armature, armature_object

def makeEditable(scene, armature_object):
    # select only armature object and set edit mode
    scene.objects.active=armature_object
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)

def addIk(p_bone, 
        armature_object, effector_name, 
        chain, weight, iterations):
    constraint = p_bone.constraints.new('IK')
    constraint.chain_count=len(chain)
    constraint.target=armature_object
    constraint.subtarget=effector_name
    constraint.use_tail=False
    #constraint.influence=weight * 0.25
    constraint.iterations=iterations * 10

def addCopyRotation(pose_bone, target_object, target_bone, factor):
    c=pose_bone.constraints.new(type='COPY_ROTATION')
    c.target=target_object
    c.subtarget=target_bone.name
    c.influence=factor
    c.target_space='LOCAL'
    c.owner_space='LOCAL'


def convert_coord(pos):
    """
    Left handed y-up to Right handed z-up
    """
    return (pos.x, pos.z, pos.y)

def VtoV(v):
    return createVector(v.x, v.y, v.z)
def createVector(x, y, z):
    return mathutils.Vector([x, y, z])


def trim_by_utf8_21byte(src):
    len_list=[len(src[:i].encode('utf-8')) for i in range(1, len(src)+1, 1)]
    max_length=21
    letter_count=0
    for str_len in len_list:
        if str_len>max_length:
            break
        letter_count+=1
    return src[:letter_count]

def get_object_name(fmt, index, name):
    """
    object名を作る。最大21バイト
    """
    #len_list=[len(name[:i].encode('utf-8')) for i in range(1, len(name)+1, 1)]
    #prefix=
    return trim_by_utf8_21byte(fmt.format(index)+name)
    """
    max_length=21-len(prefix)
    for str_len in len_list:
        if str_len>max_length:
            break
        letter_count+=1
    name=prefix+name[:letter_count]
    #print("%s(%d)" % (name, letter_count))
    return name
    """

def __import_joints(scene, joints, rigidbodies):
    print("create joints")
    container=createEmpty(scene, 'Joints')
    layers=[
        True, False, False, False, False, False, False, False, False, False,
        False, False, False, False, False, False, False, False, False, False,
            ]
    material=bpy.data.materials.new('joint')

    material.diffuse_color=(1, 0, 0)
    constraintMeshes=[]
    for i, c in enumerate(joints):
        bpy.ops.mesh.primitive_uv_sphere_add(
                segments=8,
                ring_count=4,
                size=0.1,
                location=(c.position.x, c.position.z, c.position.y),
                layers=layers
                )
        meshObject=scene.objects.active
        constraintMeshes.append(meshObject)
        mesh=meshObject.data
        mesh.materials.append(material)
        meshObject.name=get_object_name("j{0:02}:", i, c.name)
        #meshObject.draw_transparent=True
        #meshObject.draw_wire=True
        meshObject.draw_type='SOLID'
        rot=c.rotation
        meshObject.rotation_euler=(-rot.x, -rot.z, -rot.y)

        meshObject[bl.CONSTRAINT_NAME]=c.name
        meshObject[bl.CONSTRAINT_A]=rigidbodies[c.rigidbody_index_a].name
        meshObject[bl.CONSTRAINT_B]=rigidbodies[c.rigidbody_index_b].name
        meshObject[bl.CONSTRAINT_POS_MIN]=VtoV(c.translation_limit_min)
        meshObject[bl.CONSTRAINT_POS_MAX]=VtoV(c.translation_limit_max)
        meshObject[bl.CONSTRAINT_ROT_MIN]=VtoV(c.rotation_limit_min)
        meshObject[bl.CONSTRAINT_ROT_MAX]=VtoV(c.rotation_limit_max)
        meshObject[bl.CONSTRAINT_SPRING_POS]=VtoV(c.spring_constant_translation)
        meshObject[bl.CONSTRAINT_SPRING_ROT]=VtoV(c.spring_constant_rotation)

    for meshObject in reversed(constraintMeshes):
        meshObject.parent=container

    return container

def __importRigidBodies(scene, rigidbodies, bones):
    print("create rigid bodies")

    container=createEmpty(scene, 'RigidBodies')
    layers=[
        True, False, False, False, False, False, False, False, False, False,
        False, False, False, False, False, False, False, False, False, False,
            ]
    material=bpy.data.materials.new('rigidBody')
    rigidMeshes=[]
    for i, rigid in enumerate(rigidbodies):
        if rigid.bone_index==-1:
            # no reference bone
            bone=bones[0]
        else:
            bone=bones[rigid.bone_index]
        pos=rigid.shape_position
        size=rigid.shape_size

        if rigid.shape_type==0:
            bpy.ops.mesh.primitive_ico_sphere_add(
                    location=(pos.x, pos.z, pos.y),
                    layers=layers
                    )
            bpy.ops.transform.resize(
                    value=(size.x, size.x, size.x))
        elif rigid.shape_type==1:
            bpy.ops.mesh.primitive_cube_add(
                    location=(pos.x, pos.z, pos.y),
                    layers=layers
                    )
            bpy.ops.transform.resize(
                    value=(size.x, size.z, size.y))
        elif rigid.shape_type==2:
            bpy.ops.mesh.primitive_cylinder_add(
                    location=(pos.x, pos.z, pos.y),
                    layers=layers
                    )
            bpy.ops.transform.resize(
                    value=(size.x, size.x, size.y))
        else:
            assert(False)

        meshObject=scene.objects.active
        mesh=meshObject.data
        rigidMeshes.append(meshObject)
        mesh.materials.append(material)
        meshObject.name=get_object_name("r{0:02}:", i, rigid.name)
        #meshObject.draw_transparent=True
        #meshObject.draw_wire=True
        meshObject.draw_type='WIRE'
        rot=rigid.shape_rotation
        meshObject.rotation_euler=(-rot.x, -rot.z, -rot.y)

        meshObject[bl.RIGID_NAME]=rigid.name
        meshObject[bl.RIGID_SHAPE_TYPE]=rigid.shape_type
        meshObject[bl.RIGID_PROCESS_TYPE]=rigid.mode
        meshObject[bl.RIGID_BONE_NAME]=bone.name
        meshObject[bl.RIGID_GROUP]=rigid.collision_group
        meshObject[bl.RIGID_INTERSECTION_GROUP]=rigid.no_collision_group
        meshObject[bl.RIGID_WEIGHT]=rigid.param.mass
        meshObject[bl.RIGID_LINEAR_DAMPING]=rigid.param.linear_damping
        meshObject[bl.RIGID_ANGULAR_DAMPING]=rigid.param.angular_damping
        meshObject[bl.RIGID_RESTITUTION]=rigid.param.restitution
        meshObject[bl.RIGID_FRICTION]=rigid.param.friction

    for meshObject in reversed(rigidMeshes):
        meshObject.parent=container

    return container

def __create_a_material(m, name, textures_and_images):
    """
    materialを作成する

    :Params:
        m
            pymeshio.pmx.Material
        name
            material name
        textures_and_images
            list of (texture, image)
    """
    material = bpy.data.materials.new(name)
    # diffuse
    material.diffuse_shader='FRESNEL'
    material.diffuse_color=[
            m.diffuse_color.r, m.diffuse_color.g, m.diffuse_color.b]
    material.alpha=m.alpha
    # specular
    material.specular_shader='TOON'
    material.specular_color=[
            m.specular_color.r, m.specular_color.g, m.specular_color.b]
    material.specular_toon_size=m.specular_factor * 0.1
    # ambient
    material.mirror_color=[
            m.ambient_color.r, m.ambient_color.g, m.ambient_color.b]
    # flag
    material[bl.MATERIALFLAG_BOTHFACE]=m.hasFlag(pmx.MATERIALFLAG_BOTHFACE)
    material[bl.MATERIALFLAG_GROUNDSHADOW]=m.hasFlag(pmx.MATERIALFLAG_GROUNDSHADOW)
    material[bl.MATERIALFLAG_SELFSHADOWMAP]=m.hasFlag(pmx.MATERIALFLAG_SELFSHADOWMAP)
    material[bl.MATERIALFLAG_SELFSHADOW]=m.hasFlag(pmx.MATERIALFLAG_SELFSHADOW)
    material[bl.MATERIALFLAG_EDGE]=m.hasFlag(pmx.MATERIALFLAG_EDGE)
    # edge_color
    # edge_size
    # other
    material.preview_render_type='FLAT'
    material.use_transparency=True
    # texture
    if m.texture_index!=-1:
        texture=textures_and_images[m.texture_index][0]
        addTexture(material, texture)
    # toon texture
    if m.toon_sharing_flag==1:
        material[bl.MATERIAL_SHAREDTOON]=m.toon_texture_index
    else:
        if m.toon_texture_index!=-1:
            toon_texture=textures_and_images[m.toon_texture_index][0]
            toon_texture[bl.TEXTURE_TYPE]='TOON'
            addTexture(material, toon_texture)
    # sphere texture
    if m.sphere_mode==pmx.MATERIALSPHERE_NONE:
        material[bl.MATERIAL_SPHERE_MODE]=pmx.MATERIALSPHERE_NONE
    elif m.sphere_mode==pmx.MATERIALSPHERE_SPH:
        # SPH
        if m.sphere_texture_index==-1:
            material[bl.MATERIAL_SPHERE_MODE]=pmx.MATERIALSPHERE_NONE
        else:
            sph_texture=textures_and_images[m.sphere_texture_index][0]
            sph_texture[bl.TEXTURE_TYPE]='SPH'
            addTexture(material, sph_texture)
            material[bl.MATERIAL_SPHERE_MODE]=m.sphere_mode
    elif m.sphere_mode==pmx.MATERIALSPHERE_SPA:
        # SPA
        if m.sphere_texture_index==-1:
            material[bl.MATERIAL_SPHERE_MODE]=pmx.MATERIALSPHERE_NONE
        else:
            spa_texture=textures_and_images[m.sphere_texture_index][0]
            spa_texture[bl.TEXTURE_TYPE]='SPA'
            addTexture(material, spa_texture, True, 'ADD')

            material[bl.MATERIAL_SPHERE_MODE]=m.sphere_mode
    else:
        print("unknown sphere mode:", m.sphere_mode)
    return material

def __create_armature(scene, bones, display_slots):
    """
    :Params:
        bones
            list of pymeshio.pmx.Bone
    """
    armature, armature_object=createArmature(scene)

    # numbering
    for i, b in enumerate(bones): 
        b.index=i

    # create bones
    makeEditable(scene, armature_object)
    def create_bone(b):
        bone=armature.edit_bones.new(b.name)
        bone[bl.BONE_ENGLISH_NAME]=b.english_name
        # bone position
        bone.head=createVector(*convert_coord(b.position))
        if b.getConnectionFlag():
            # dummy tail
            bone.tail=bone.head+createVector(0, 1, 0)
        else:
            # offset tail
            bone.tail=bone.head+createVector(
                    *convert_coord(b.tail_position))
            if bone.tail==bone.head:
                # 捻りボーン
                bone.tail=bone.head+createVector(0, 0.01, 0)
            pass
        if not b.getVisibleFlag():
            # dummy tail
            bone.tail=bone.head+createVector(0, 0.01, 0)
        return bone
    bl_bones=[create_bone(b) for b in bones]

    # build skeleton
    used_bone_name=set()
    for b, bone in zip(bones, bl_bones):
        if b.name!=bone.name:
            if b.name in used_bone_name:
                print("duplicated bone name:[%s][%s]" %(b.name, bone.name))
            else:
                print("invalid name:[%s][%s]" %(b.name, bone.name))
        used_bone_name.add(b.name)
        if b.parent_index!=-1:
            # set parent
            parent_bone=bl_bones[b.parent_index]
            bone.parent=parent_bone

        if b.getConnectionFlag() and b.tail_index!=-1:
            assert(b.tail_index!=0)
            # set tail position
            tail_bone=bl_bones[b.tail_index]
            bone.tail=tail_bone.head
            # connect with child
            tail_b=bones[b.tail_index]
            if bones[tail_b.parent_index]==b:
                # connect with tail
                tail_bone.use_connect=True

        if bone.head==bone.tail:
            # no size bone...
            print(bone)
            bone.tail.z-=0.00001


    # pose bone construction
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    pose = armature_object.pose
    for b in bones:
        p_bone=pose.bones[b.name]
        if b.hasFlag(pmx.BONEFLAG_IS_IK):
            # create ik constraint
            ik=b.ik
            assert(len(ik.link)<16)
            ik_p_bone=pose.bones[bones[ik.target_index].name]
            assert(ik_p_bone)
            addIk(
                    ik_p_bone, 
                    armature_object, b.name,
                    ik.link, ik.limit_radian, ik.loop)
            armature.bones[b.name][bl.IK_UNITRADIAN]=ik.limit_radian
            for chain in ik.link:
                if chain.limit_angle:
                    ik_p_bone=pose.bones[bones[chain.bone_index].name]
                    # IK limit
                    # x
                    if chain.limit_min.x==0 and chain.limit_max.x==0:
                        ik_p_bone.lock_ik_x=True
                    else:
                        ik_p_bone.use_ik_limit_x=True
                        # left handed to right handed ?
                        ik_p_bone.ik_min_x=-chain.limit_max.x
                        ik_p_bone.ik_max_x=-chain.limit_min.x

                    # y
                    if chain.limit_min.y==0 and chain.limit_max.y==0:
                        ik_p_bone.lock_ik_y=True
                    else:
                        ik_p_bone.use_ik_limit_y=True
                        ik_p_bone.ik_min_y=chain.limit_min.y
                        ik_p_bone.ik_max_y=chain.limit_max.y

                    # z
                    if chain.limit_min.z==0 and chain.limit_max.z==0:
                        ik_p_bone.lock_ik_z=True
                    else:
                        ik_p_bone.use_ik_limit_z=True
                        ik_p_bone.ik_min_z=chain.limit_min.z
                        ik_p_bone.ik_max_z=chain.limit_max.z

        if b.hasFlag(pmx.BONEFLAG_IS_EXTERNAL_ROTATION):
            constraint_p_bone=pose.bones[bones[b.effect_index].name]
            addCopyRotation(p_bone,
                    armature_object, constraint_p_bone, 
                    b.effect_factor)

        if b.hasFlag(pmx.BONEFLAG_HAS_FIXED_AXIS):
            c=p_bone.constraints.new(type='LIMIT_ROTATION')
            c.owner_space='LOCAL'

        if b.parent_index!=-1:
            parent_b=bones[b.parent_index]
            if (
                    parent_b.hasFlag(pmx.BONEFLAG_TAILPOS_IS_BONE)
                    and parent_b.tail_index==b.index
                    ):
                # 移動制限を尻尾位置の接続フラグに流用する
                c=p_bone.constraints.new(type='LIMIT_LOCATION')
                c.owner_space='LOCAL'
            else:
                parent_parent_b=bones[parent_b.parent_index]
                if (
                        parent_parent_b.hasFlag(pmx.BONEFLAG_TAILPOS_IS_BONE)
                        and parent_parent_b.tail_index==b.index
                        ):
                    # 移動制限を尻尾位置の接続フラグに流用する
                    c=p_bone.constraints.new(type='LIMIT_LOCATION')
                    c.owner_space='LOCAL'

        if not b.hasFlag(pmx.BONEFLAG_CAN_TRANSLATE):
            # translatation lock
            p_bone.lock_location=(True, True, True)


    makeEditable(scene, armature_object)

    # create bone group
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    pose = armature_object.pose
    bone_groups={}
    for i, ds in enumerate(display_slots):
        #print(ds)
        g=createBoneGroup(scene, armature_object, ds.name, "THEME%02d" % (i+1))
        for t, index in ds.references:
            if t==0:
                name=bones[index].name
                try:
                    pose.bones[name].bone_group=g
                except KeyError as e:
                    print("pose %s is not found" % name)

    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    # fix flag
    boneNameMap={}
    for b in bones:
        boneNameMap[b.name]=b
    for b in armature.bones.values():
        if not boneNameMap[b.name].hasFlag(pmx.BONEFLAG_IS_VISIBLE):
            b.hide=True
        if not boneNameMap[b.name].hasFlag(pmx.BONEFLAG_TAILPOS_IS_BONE):
            b[bl.BONE_USE_TAILOFFSET]=True
            

    return armature_object


def import_pmx_model(scene, filepath, model, import_mesh, import_physics, **kwargs):
    if not model:
        print("fail to load %s" % filepath)
        return False
    print(model)

    # メッシュをまとめるエンプティオブジェクト
    model_name=model.name
    if len(model_name)==0:
        model_name=model.english
        if len(model_name)==0:
            model_name=os.path.basename(filepath)

    root_object=createEmpty(scene, trim_by_utf8_21byte(model_name))
    root_object[bl.MMD_MB_NAME]=model.name
    root_object[bl.MMD_ENGLISH_NAME]=model.english_name
    root_object[bl.MMD_MB_COMMENT]=model.comment
    root_object[bl.MMD_ENGLISH_COMMENT]=model.english_comment

    # armatureを作る
    armature_object=__create_armature(scene, model.bones, model.display_slots)
    if armature_object:
        armature_object.parent=root_object

    if import_mesh:
        # テクスチャを作る
        texture_dir=os.path.dirname(filepath)
        print(model.textures)
        textures_and_images=[createTexture(os.path.join(texture_dir, t))
                for t in model.textures]
        print(textures_and_images)

        # 頂点配列。(Left handed y-up) to (Right handed z-up)
        vertices=[convert_coord(pos)
                for pos in (v.position for v in model.vertices)]

        ####################
        # mesh object
        ####################
        # object名はutf-8で21byteまで
        mesh, mesh_object=createMesh(scene, 'mesh')
        # activate object
        bpy.ops.object.select_all(action='DESELECT')
        mesh_object.select=True 
        scene.objects.active=mesh_object
        mesh_object.parent=root_object

        ####################
        # vertices & faces
        ####################
        # flip
        addGeometry(mesh, vertices,
                [(model.indices[i+2], model.indices[i+1], model.indices[i])
                    for i in range(0, len(model.indices), 3)])
        assert(len(model.vertices)==len(mesh.vertices))
        mesh.tessface_uv_textures.new()

        ####################
        # material
        ####################
        index_gen=(i for i in model.indices)
        face_gen=(pair for pair in enumerate(mesh.tessfaces))
        for i, m in enumerate(model.materials):
            name=get_object_name("{0:02}:", i, m.name)
            material=__create_a_material(m, name, textures_and_images)
            mesh.materials.append(material)

            # texture image
            image=(textures_and_images.get[m.texture_index] 
                    if m.texture_index in textures_and_images
                    else None)

            # face params
            for _ in range(0, m.vertex_count, 3):
                face_index, face=next(face_gen)
                # assign material
                face.material_index=i
                # assign uv
                uv0=model.vertices[next(index_gen)].uv
                uv1=model.vertices[next(index_gen)].uv
                uv2=model.vertices[next(index_gen)].uv
                setFaceUV(mesh, face_index, face, [# fix uv
                    (uv2.x, 1.0-uv2.y),
                    (uv1.x, 1.0-uv1.y),
                    (uv0.x, 1.0-uv0.y)
                    ],
                    image)

                # set smooth
                face.use_smooth=True

        # fix mesh
        mesh.update()

        ####################
        # armature
        ####################
        if armature_object:
            # armature modifirer
            mod=mesh_object.modifiers.new("Modifier", "ARMATURE")
            mod.object = armature_object
            mod.use_bone_envelopes=False
            for i, (v,  mvert) in enumerate(zip(model.vertices, mesh.vertices)):
                mvert.normal=mathutils.Vector(convert_coord(v.normal))
                if isinstance(v.deform, pmx.Bdef1):
                    assignVertexGroup(mesh_object,
                            model.bones[v.deform.index0].name, i, 1.0)
                elif isinstance(v.deform, pmx.Bdef2):
                    assignVertexGroup(mesh_object,
                            model.bones[v.deform.index0].name, i, v.deform.weight0)
                    assignVertexGroup(mesh_object,
                            model.bones[v.deform.index1].name, i, 1.0-v.deform.weight0)
                elif isinstance(v.deform, pmx.Bdef4):
                    assignVertexGroup(mesh_object,
                            model.bones[v.deform.index0].name, i, v.deform.weight0)
                    assignVertexGroup(mesh_object,
                            model.bones[v.deform.index1].name, i, v.deform.weight1)
                    assignVertexGroup(mesh_object,
                            model.bones[v.deform.index2].name, i, v.deform.weight2)
                    assignVertexGroup(mesh_object,
                            model.bones[v.deform.index3].name, i, v.deform.weight3)
                elif isinstance(v.deform, pmx.Sdef):
                    # fail safe
                    assignVertexGroup(mesh_object,
                            model.bones[v.deform.index0].name, i, v.deform.weight0)
                    assignVertexGroup(mesh_object,
                            model.bones[v.deform.index1].name, i, 1.0-v.deform.weight0)
                else:
                    raise Exception("unknown deform: %s" % v.deform)

        ####################
        # shape keys
        ####################
        if len(model.morphs)>0:
            # set shape_key pin
            mesh_object.show_only_shape_key=True
            # create base key
            mesh_object.vertex_groups.new(bl.MMD_SHAPE_GROUP_NAME)
            # assign all vertext to group
            for i, v in enumerate(mesh.vertices):
                assignVertexGroup(mesh_object,
                        bl.MMD_SHAPE_GROUP_NAME, i, 0);
            # create base key
            baseShapeBlock=mesh_object.shape_key_add(bl.BASE_SHAPE_NAME)
            mesh.update()

            # each morph
            for m in model.morphs:
                new_shape_key=mesh_object.shape_key_add(m.name)
                for o in m.offsets:
                    if isinstance(o, pmx.VertexMorphOffset):
                        # vertex morph
                        new_shape_key.data[o.vertex_index].co=mesh.vertices[o.vertex_index].co+createVector(*convert_coord(o.position_offset))
                    else:
                        print("unknown morph type: %s. drop" % o)
                        #raise Exception("unknown morph type: %s" % o)
                        break

            # select base shape
            mesh_object.active_shape_key_index=0

    if import_physics:
        # import rigid bodies
        rigidbody_object=__importRigidBodies(scene, model.rigidbodies, model.bones)
        if rigidbody_object:
            rigidbody_object.parent=root_object

        # import joints
        joint_object=__import_joints(scene, model.joints, model.rigidbodies)
        if joint_object:
            joint_object.parent=root_object

    root_object.select=True 
    scene.objects.active=root_object

    return {'FINISHED'}


def _execute(scene, filepath, **kwargs):
    """
    importer 本体
    """
    if filepath.lower().endswith(".pmd"):
        from .pymeshio.pmd import reader
        pmd_model=reader.read_from_file(filepath)
        if not pmd_model:
            return

        print("convert pmd to pmx...")
        from .pymeshio import converter
        import_pmx_model(scene, filepath, converter.pmd_to_pmx(pmd_model), **kwargs)

    elif filepath.lower().endswith(".pmx"):
        from .pymeshio.pmx import reader
        import_pmx_model(scene, filepath, reader.read_from_file(filepath), **kwargs)

    else:
        print("unknown file type: ", filepath)


class ImportPmx(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    '''Import from PMX Format(.pmx)(.pmd)'''
    bl_idname='import_scene.mmd_pmx_pmd'
    bl_label='Import PMX/PMD'
    bl_options={'UNDO'}
    filename_ext='.pmx;.pmd'
    filter_glob=bpy.props.StringProperty(
            default='*.pmx;*.pmd', options={'HIDDEN'})

    #use_englishmap=bpy.props.BoolProperty(
    #        name='use english map', 
    #        description='Convert name to english(not implemented)',
    #        default=False)

    import_mesh=bpy.props.BoolProperty(
            name='import mesh', 
            description='import polygon mesh',
            default=True)

    import_physics=bpy.props.BoolProperty(
            name='import physics objects', 
            description='import rigid body and constraints',
            default=True)

    def execute(self, context):
        _execute(context.scene, **self.as_keywords(ignore=('filter_glob',)))
        context.scene.update()
        return  {'FINISHED'}

    @classmethod
    def menu_func(klass, self, context):
        self.layout.operator(klass.bl_idname, 
                text='MikuMikuDance model (.pmx)(.pmd)',
                icon='PLUGIN'
                )

