# coding: utf-8
import os
from pymeshio import pmx, pmd_from_file, pmd_to_pmx, pmx_from_file # pylint: disable=E0611
import bpy # pylint: disable=E0401

from . import bl


def convert_coord(pos):
    """
    Left handed y-up to Right handed z-up
    """
    return (pos.x, pos.z, pos.y)

def VtoV(v):
    return bl.createVector(v.x, v.y, v.z)

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

def __import_joints(joints, rigidbodies):
    print("create joints")
    container=bl.object.createEmpty('Joints')
    layers=[
        True, False, False, False, False, False, False, False, False, False,
        False, False, False, False, False, False, False, False, False, False,
            ]
    material=bl.material.create('joint')
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
        meshObject=bl.object.getActive()
        constraintMeshes.append(meshObject)
        mesh=bl.object.getData(meshObject)
        bl.mesh.addMaterial(mesh, material)
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
        bl.object.makeParent(container, meshObject)

    return container

def __importRigidBodies(rigidbodies, bones):
    print("create rigid bodies")

    container=bl.object.createEmpty('RigidBodies')
    layers=[
        True, False, False, False, False, False, False, False, False, False,
        False, False, False, False, False, False, False, False, False, False,
            ]
    material=bl.material.create('rigidBody')
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

        meshObject=bl.object.getActive()
        mesh=bl.object.getData(meshObject)
        rigidMeshes.append(meshObject)
        bl.mesh.addMaterial(mesh, material)
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
        bl.object.makeParent(container, meshObject)

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
    material = bl.material.create(name)
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
        bl.material.addTexture(material, texture)
    # toon texture
    if m.toon_sharing_flag==1:
        material[bl.MATERIAL_SHAREDTOON]=m.toon_texture_index
    else:
        if m.toon_texture_index!=-1:
            toon_texture=textures_and_images[m.toon_texture_index][0]
            toon_texture[bl.TEXTURE_TYPE]='TOON'
            bl.material.addTexture(material, toon_texture)
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
            bl.material.addTexture(material, sph_texture)
            material[bl.MATERIAL_SPHERE_MODE]=m.sphere_mode
    elif m.sphere_mode==pmx.MATERIALSPHERE_SPA:
        # SPA
        if m.sphere_texture_index==-1:
            material[bl.MATERIAL_SPHERE_MODE]=pmx.MATERIALSPHERE_NONE
        else:
            spa_texture=textures_and_images[m.sphere_texture_index][0]
            spa_texture[bl.TEXTURE_TYPE]='SPA'
            bl.material.addTexture(material, spa_texture, True, 'ADD')

            material[bl.MATERIAL_SPHERE_MODE]=m.sphere_mode
    else:
        print("unknown sphere mode:", m.sphere_mode)
    return material

def __create_armature(bones, display_slots, import_scale):
    """
    :Params:
        bones
            list of pymeshio.pmx.Bone
    """
    armature, armature_object=bl.armature.create()

    # numbering
    for i, b in enumerate(bones): 
        b.index=i

    # create bones
    bl.armature.makeEditable(armature_object)
    def create_bone(b):
        bone=bl.armature.createBone(armature, b.name)
        bone[bl.BONE_ENGLISH_NAME]=b.english_name
        # bone position
        bone.head=bl.createVector(*convert_coord(b.position * import_scale))
        if b.getConnectionFlag():
            # dummy tail
            bone.tail=bone.head+bl.createVector(0, import_scale, 0)
        else:
            # offset tail
            bone.tail=bone.head+bl.createVector(
                    *convert_coord(b.tail_position * import_scale))
            if bone.tail==bone.head:
                # 捻りボーン
                bone.tail=bone.head+bl.createVector(0, 0.01 * import_scale, 0)
            pass
        if not b.getVisibleFlag():
            # dummy tail
            bone.tail=bone.head+bl.createVector(0, 0.01 * import_scale, 0)
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
                bl.bone.setConnected(tail_bone)

        if bone.head==bone.tail:
            # no size bone...
            print(bone)
            bone.tail.z-=0.00001

    bl.armature.update(armature)

    # pose bone construction
    bl.enterObjectMode()
    pose = bl.object.getPose(armature_object)
    for b in bones:
        p_bone=pose.bones[b.name]
        if b.hasFlag(pmx.BONEFLAG_IS_IK):
            # create ik constraint
            ik=b.ik
            assert(len(ik.link)<16)
            ik_p_bone=pose.bones[bones[ik.target_index].name]
            assert(ik_p_bone)
            bl.constraint.addIk(
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
            bl.constraint.addCopyRotation(p_bone,
                    armature_object, constraint_p_bone, 
                    b.effect_factor)

        if b.hasFlag(pmx.BONEFLAG_HAS_FIXED_AXIS):
            bl.constraint.addLimitRotation(p_bone)

        if b.parent_index!=-1:
            parent_b=bones[b.parent_index]
            if (
                    parent_b.hasFlag(pmx.BONEFLAG_TAILPOS_IS_BONE)
                    and parent_b.tail_index==b.index
                    ):
                # 移動制限を尻尾位置の接続フラグに流用する
                bl.constraint.addLimitTranslateion(p_bone)
            else:
                parent_parent_b=bones[parent_b.parent_index]
                if (
                        parent_parent_b.hasFlag(pmx.BONEFLAG_TAILPOS_IS_BONE)
                        and parent_parent_b.tail_index==b.index
                        ):
                    # 移動制限を尻尾位置の接続フラグに流用する
                    bl.constraint.addLimitTranslateion(p_bone)

        if not b.hasFlag(pmx.BONEFLAG_CAN_TRANSLATE):
            # translatation lock
            p_bone.lock_location=(True, True, True)


    bl.armature.makeEditable(armature_object)
    bl.armature.update(armature)

    # create bone group
    bl.enterObjectMode()
    pose = bl.object.getPose(armature_object)
    #bone_groups={}
    for i, ds in enumerate(display_slots):
        #print(ds)
        g=bl.object.createBoneGroup(armature_object, ds.name, "THEME%02d" % (i+1))
        for t, index in ds.references:
            if t==0:
                name=bones[index].name
                try:
                    pose.bones[name].bone_group=g
                except KeyError:
                    print("pose %s is not found" % name)

    bl.enterObjectMode()

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


def import_pmx_model(filepath, model, import_mesh, import_physics, import_scale, **kwargs):
    if not model:
        print("fail to load %s" % filepath)
        return False
    #print(model)

    # メッシュをまとめるエンプティオブジェクト
    model_name=model.name
    if len(model_name)==0:
        model_name=model.english
        if len(model_name)==0:
            model_name=os.path.basename(filepath)

    root_object=bl.object.createEmpty(trim_by_utf8_21byte(model_name))
    root_object[bl.MMD_MB_NAME]=model.name
    root_object[bl.MMD_ENGLISH_NAME]=model.english_name
    root_object[bl.MMD_MB_COMMENT]=model.comment
    root_object[bl.MMD_ENGLISH_COMMENT]=model.english_comment

    # armatureを作る
    armature_object=__create_armature(model.bones, model.display_slots, import_scale)
    if armature_object:
        armature_object.parent=root_object

    if import_mesh:
        # テクスチャを作る
        texture_dir=os.path.dirname(filepath)
        print(model.textures)
        textures_and_images=[bl.texture.create(os.path.join(texture_dir, t))
                for t in model.textures]
        print(textures_and_images)

        # 頂点配列。(Left handed y-up) to (Right handed z-up)
        vertices = [convert_coord(v.position * import_scale)
                    for v in model.vertices]

        ####################
        # mesh object
        ####################
        # object名はutf-8で21byteまで
        mesh, mesh_object=bl.mesh.create('mesh')
        # activate object
        bl.object.deselectAll()
        bl.object.activate(mesh_object)
        bl.object.makeParent(root_object, mesh_object)

        ####################
        # vertices & faces
        ####################
        # flip
        bl.mesh.addGeometry(mesh, vertices,
                [(model.indices[i+2], model.indices[i+1], model.indices[i])
                    for i in range(0, len(model.indices), 3)])
        assert(len(model.vertices)==len(mesh.vertices))
        bl.mesh.addUV(mesh)

        ####################
        # material
        ####################
        index_gen=(i for i in model.indices)
        face_gen=(pair for pair in enumerate(mesh.tessfaces))
        for i, m in enumerate(model.materials):
            name=get_object_name("{0:02}:", i, m.name)
            material=__create_a_material(m, name, textures_and_images)
            bl.mesh.addMaterial(mesh, material)

            # texture image
            image=(textures_and_images.get[m.texture_index] 
                    if m.texture_index in textures_and_images
                    else None)

            # face params
            for _ in range(0, m.vertex_count, 3):
                face_index, face=next(face_gen)
                # assign material
                bl.face.setMaterial(face, i)
                # assign uv
                uv0=model.vertices[next(index_gen)].uv
                uv1=model.vertices[next(index_gen)].uv
                uv2=model.vertices[next(index_gen)].uv
                bl.mesh.setFaceUV(mesh, face_index, face, [# fix uv
                    (uv2.x, 1.0-uv2.y),
                    (uv1.x, 1.0-uv1.y),
                    (uv0.x, 1.0-uv0.y)
                    ],
                    image)

                # set smooth
                bl.face.setSmooth(face, True)

        # fix mesh
        mesh.update()

        ####################
        # armature
        ####################
        if armature_object:
            # armature modifirer
            bl.modifier.addArmature(mesh_object, armature_object)
            # set vertex attributes(normal, bone weights)
            bl.mesh.useVertexUV(mesh)
            for i, (v,  mvert) in enumerate(zip(model.vertices, mesh.vertices)):
                bl.vertex.setNormal(mvert, convert_coord(v.normal))
                if isinstance(v.deform, pmx.Bdef1):
                    bl.object.assignVertexGroup(mesh_object,
                            model.bones[v.deform.index0].name, i, 1.0)
                elif isinstance(v.deform, pmx.Bdef2):
                    bl.object.assignVertexGroup(mesh_object,
                            model.bones[v.deform.index0].name, i, v.deform.weight0)
                    bl.object.assignVertexGroup(mesh_object,
                            model.bones[v.deform.index1].name, i, 1.0-v.deform.weight0)
                elif isinstance(v.deform, pmx.Bdef4):
                    bl.object.assignVertexGroup(mesh_object,
                            model.bones[v.deform.index0].name, i, v.deform.weight0)
                    bl.object.assignVertexGroup(mesh_object,
                            model.bones[v.deform.index1].name, i, v.deform.weight1)
                    bl.object.assignVertexGroup(mesh_object,
                            model.bones[v.deform.index2].name, i, v.deform.weight2)
                    bl.object.assignVertexGroup(mesh_object,
                            model.bones[v.deform.index3].name, i, v.deform.weight3)
                elif isinstance(v.deform, pmx.Sdef):
                    # fail safe
                    bl.object.assignVertexGroup(mesh_object,
                            model.bones[v.deform.index0].name, i, v.deform.weight0)
                    bl.object.assignVertexGroup(mesh_object,
                            model.bones[v.deform.index1].name, i, 1.0-v.deform.weight0)
                else:
                    raise Exception("unknown deform: %s" % v.deform)

        ####################
        # shape keys
        ####################
        if len(model.morphs)>0:
            # set shape_key pin
            bl.object.pinShape(mesh_object, True)
            # create base key
            bl.object.addVertexGroup(mesh_object, bl.MMD_SHAPE_GROUP_NAME)
            # assign all vertext to group
            for i, v in enumerate(mesh.vertices):
                bl.object.assignVertexGroup(mesh_object,
                        bl.MMD_SHAPE_GROUP_NAME, i, 0)
            # create base key
            bl.object.addShapeKey(mesh_object, bl.BASE_SHAPE_NAME)
            mesh.update()

            # each morph
            for m in model.morphs:
                new_shape_key=bl.object.addShapeKey(mesh_object, m.name)
                for o in m.offsets:
                    if isinstance(o, pmx.VertexMorphOffset):
                        # vertex morph
                        bl.shapekey.assign(new_shape_key, 
                                o.vertex_index, 
                                mesh.vertices[o.vertex_index].co+
                                bl.createVector(*convert_coord(o.position_offset * import_scale)))
                    else:
                        print("unknown morph type: %s. drop" % o)
                        #raise Exception("unknown morph type: %s" % o)
                        break

            # select base shape
            bl.object.setActivateShapeKey(mesh_object, 0)

    if import_physics:
        # import rigid bodies
        rigidbody_object=__importRigidBodies(model.rigidbodies, model.bones)
        if rigidbody_object:
            bl.object.makeParent(root_object, rigidbody_object)

        # import joints
        joint_object=__import_joints(model.joints, model.rigidbodies)
        if joint_object:
            bl.object.makeParent(root_object, joint_object)

    bl.object.activate(root_object)

    return {'FINISHED'}


def _execute(filepath, **kwargs):
    """
    importer 本体
    """
    if filepath.lower().endswith(".pmd"):
        pmd_model=pmd_from_file(filepath)
        if not pmd_model:
            return

        print("convert pmd to pmx...")
        import_pmx_model(filepath, pmd_to_pmx(pmd_model), **kwargs)

    elif filepath.lower().endswith(".pmx"):
        import_pmx_model(filepath, pmx_from_file(filepath), **kwargs)

    else:
        print("unknown file type: ", filepath)


import bpy_extras.io_utils # pylint: disable=E0401
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
            default=False)

    import_scale = bpy.props.FloatProperty(
            name='import scale',
            description='to meter(1.58/20)',
            min=0.0001, max=1000000.0,
            soft_min=0.001, soft_max=100.0, default=1.0)

    def execute(self, context):
        bl.initialize('pmx_import', context.scene)
        _execute(**self.as_keywords(ignore=('filter_glob',)))
        bl.finalize()
        return  {'FINISHED'}

    @classmethod
    def menu_func(klass, self, context):
        self.layout.operator(klass.bl_idname, 
                text='MikuMikuDance model (.pmx)(.pmd)',
                icon='PLUGIN'
                )
