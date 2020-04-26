#!BPY
# coding: utf-8
"""
 Name: 'MikuMikuDance model (.pmd)...'
 Blender: 248
 Group: 'Export'
 Tooltip: 'Export PMD file for MikuMikuDance.'
"""
__author__= ["ousttrue"]
__version__= "2.5"
__url__=()
__bpydoc__="""
pmd Importer

This script exports a pmd model.

20100318: first implementation.
20100519: refactoring. use C extension.
20100530: implement basic features.
20100612: integrate 2.4 and 2.5.
20100616: implement rigid body.
20100619: fix rigid body, bone weight.
20100626: refactoring.
20100629: sphere map.
20100710: toon texture & bone group.
20100711: separate vertex with normal or uv.
20100724: update for Blender2.53.
20100731: add full python module.
20101005: update for Blender2.54.
20101228: update for Blender2.55.
20110429: update for Blender2.57b.
20110522: implement RigidBody and Constraint.
20111002: update for pymeshio-2.1.0
20120117: fix empty morph bug(ciritical).
"""
import io

from . import bl
from . import exporter
from pymeshio import common
from pymeshio import pmd
from pymeshio import englishmap
from pymeshio.pmd import writer
import bpy
import bpy_extras.io_utils # pylint: disable=E0401


def near(x, y, EPSILON=1e-5):
    d=x-y
    return d>=-EPSILON and d<=EPSILON


def toCP932(s):
    return s.encode('cp932')


def write(ex, path):
    model=pmd.Model()

    o=ex.root.o
    englishName=o.name
    name=o[bl.MMD_MB_NAME] if bl.MMD_MB_NAME in o else 'Blenderエクスポート'
    comment=o[bl.MMD_MB_COMMENT] if bl.MMD_MB_COMMENT in o else 'Blnderエクスポート\n'
    englishComment=o[bl.MMD_COMMENT] if bl.MMD_COMMENT in o else 'blender export\n'

    model.name=name.encode('cp932')
    model.english_name=englishName.encode('cp932')
    model.comment=comment.encode('cp932')
    model.english_comment=englishComment.encode('cp932')

    # 頂点
    model.vertices=[pmd.Vertex(
        # convert right-handed z-up to left-handed y-up
        common.Vector3(pos[0], pos[2], pos[1]), 
        # convert right-handed z-up to left-handed y-up
        common.Vector3(attribute.nx, attribute.nz, attribute.ny),
        # reverse vertical
        common.Vector2(attribute.u, 1.0-attribute.v),
        ex.skeleton.indexByName(b0),
        ex.skeleton.indexByName(b1),
        int(100*weight),
        # edge flag, 0: enable edge, 1: not edge
        0 
        )
        for pos, attribute, b0, b1, weight in ex.oneSkinMesh.vertexArray.zip()]

    # 面とマテリアル
    vertexCount=ex.oneSkinMesh.getVertexCount()
    for material_name, indices in ex.oneSkinMesh.vertexArray.each():
        #print('material:', material_name)
        try:
            m=bl.material.get(material_name)
        except KeyError as e:
            m=exporter.oneskinmesh.DefaultMaterial()
        def get_texture_name(texture):
            pos=texture.replace("\\", "/").rfind("/")
            if pos==-1:
                return texture
            else:
                return texture[pos+1:]
        textures=[get_texture_name(path)
            for path in bl.material.eachEnalbeTexturePath(m)]
        #print(textures)
        # マテリアル
        model.materials.append(pmd.Material(
                # diffuse_color
                common.RGB(m.diffuse_color[0], m.diffuse_color[1], m.diffuse_color[2]),
                m.use_transparency and m.alpha or 1.0,
                # specular_factor
                0 if m.specular_toon_size<1e-5 else m.specular_toon_size * 10,
                # specular_color
                common.RGB(m.specular_color[0], m.specular_color[1], m.specular_color[2]),
                # ambient_color
                common.RGB(m.mirror_color[0], m.mirror_color[1], m.mirror_color[2]),
                # toon
                0,
                # flag
                1 if m.subsurface_scattering.use else 0,
                # vertex_count
                len(indices),
                # texture
                ('*'.join(textures) if len(textures)>0 else "").encode('cp932')
                ))
        # 面
        for i in indices:
            assert(i<vertexCount)
        for i in range(0, len(indices), 3):
            # reverse triangle
            model.indices.append(indices[i+2])
            model.indices.append(indices[i+1])
            model.indices.append(indices[i])

    boneMap=dict([(b.name, i) for i, b in enumerate(ex.skeleton.bones)])

    # bones
    for i, b in enumerate(ex.skeleton.bones):

        # name
        v=englishmap.getUnicodeBoneName(b.name)
        if not v:
            v=[b.name, b.name]
        assert(v)
        bone=pmd.Bone(v[1].encode('cp932'))

        # english name
        bone_english_name=toCP932(b.name)
        if len(bone_english_name)>=20:
            print('bone_english_name', bone_english_name)
            #assert(len(bone_english_name)<20)
        bone.english_name=bone_english_name

        bone.parent_index=b.parent_index
        bone.tail_index=b.tail_index
        bone.ik_index=0

        if b.constraint==exporter.bonebuilder.CONSTRAINT_NONE:
            bone.type=pmd.Bone.ROTATE_MOVE
        else:
            bone.type=pmd.Bone.ROTATE

        if not b.isVisible:
            bone.type=pmd.Bone.UNVISIBLE
            bone.tail_index=0

        if b.constraint==exporter.bonebuilder.CONSTRAINT_LIMIT_ROTATION:
            bone.type=pmd.Bone.ROLLING

        if b.constraint==exporter.bonebuilder.CONSTRAINT_COPY_ROTATION:
            if b.constraintInfluence==1.0:
                bone.type=pmd.Bone.ROTATE_INFL
                bone.ik_index=boneMap[b.constraintTarget]

            else:
                bone.type=pmd.Bone.TWEAK
                bone.tail_index=boneMap[b.constraintTarget]
                bone.ik_index=int(b.constraintInfluence * 100)

        # convert right-handed z-up to left-handed y-up
        bone.pos.x=b.pos[0] if not near(b.pos[0], 0) else 0
        bone.pos.y=b.pos[2] if not near(b.pos[2], 0) else 0
        bone.pos.z=b.pos[1] if not near(b.pos[1], 0) else 0
        
        model.bones.append(bone)

    # IK
    for ik in ex.skeleton.ik_list:
        solver=pmd.IK()

        solver.index=ik.target_index
        model.bones[ik.target_index].type=pmd.Bone.IK
        model.bones[ik.target_index].ik_index=0

        solver.target=ik.effector_index
        model.bones[ik.effector_index].type=pmd.Bone.IK_TARGET

        solver.length=len(ik.chain)
        for i, chain in enumerate(ik.chain):
            solver.children.append(chain.index)
            model.bones[chain.index].type=pmd.Bone.IK_ROTATE_INFL
            model.bones[chain.index].ik_index=ik.target_index

        solver.iterations=ik.iterations
        solver.weight=ik.weight
        model.ik_list.append(solver)

    for i, b in enumerate(model.bones):
        if b.type==pmd.Bone.IK_TARGET:
            b.tail_index=0
        if b.type==pmd.Bone.IK_ROTATE_INFL or b.type==pmd.Bone.IK_TARGET:
            if model.bones[b.parent_index].type==pmd.Bone.IK_ROTATE_INFL:
                b.ik_index=model.bones[b.parent_index].ik_index
        print(i, b.name, b.type)

    # 表情
    for i, m in enumerate(ex.oneSkinMesh.morphList):
        v=englishmap.getUnicodeSkinName(m.name)
        if not v:
            v=[m.name, m.name, 4]
        assert(v)
        # morph
        morph=pmd.Morph(v[1].encode("cp932"))
        morph.english_name=m.name.encode("cp932")
        m.type=v[2]
        morph.type=v[2]
        for index, offset in m.offsets:
            # convert right-handed z-up to left-handed y-up
            morph.append(index, offset[0], offset[2], offset[1])
        morph.vertex_count=len(m.offsets)
        model.morphs.append(morph)

    # 表情枠
    # type==0はbase
    for i, m in enumerate(ex.oneSkinMesh.morphList):
        if m.type==3:
            model.morph_indices.append(i)
    for i, m in enumerate(ex.oneSkinMesh.morphList):
        if m.type==2:
            model.morph_indices.append(i)
    for i, m in enumerate(ex.oneSkinMesh.morphList):
        if m.type==1:
            model.morph_indices.append(i)
    for i, m in enumerate(ex.oneSkinMesh.morphList):
        if m.type==4:
            model.morph_indices.append(i)

    # ボーングループ
    for g in ex.skeleton.bone_groups:
        name=englishmap.getUnicodeBoneGroupName(g[0])
        if not name:
            name=g[0]
        englishName=g[0]

        model.bone_group_list.append(pmd.BoneGroup(
                (name+'\n').encode('cp932'),
                (englishName).encode('cp932')
                ))

    # ボーングループメンバー
    for i, b in enumerate(ex.skeleton.bones):
        if i==0:
           continue
        #if b.type in [6, 7]:
        #   continue
        g=ex.skeleton.getBoneGroup(b)
        if g:
            model.bone_display_list.append((i, g))

    # toon
    toonMeshObject=None
    for o in bl.object.each():
        try:
            if o.name.startswith(bl.TOON_TEXTURE_OBJECT):
                toonMeshObject=o
                break
        except:
            p(o.name)
    if toonMeshObject:
        toonMesh=bl.object.getData(toonMeshObject)
        toonMaterial=bl.mesh.getMaterial(toonMesh, 0)
        material_names=[ name for name, dummy in ex.oneSkinMesh.vertexArray.each() ]
        for i in range(10):
            t=bl.material.getTexture(toonMaterial, i)
            if t:
                model.toon_textures[i]=("%s" % t.name).encode('cp932')
                # update toon_index
                for material_name, material in zip(material_names, model.materials):
                    try:
                        m=bl.material.get(material_name)
                        if any(t == slot.texture for slot in m.texture_slots if slot is not None):
                            material.toon_index=i
                    except KeyError as e:
                        pass
            else:
                model.toon_textures[i]=("toon%02d.bmp" % (i+1)).encode('cp932')
    else:
        for i in range(10):
            model.toon_textures[i]=("toon%02d.bmp" % (i+1)).encode('cp932')

    # rigid body
    rigidNameMap={}
    for i, obj in enumerate(ex.oneSkinMesh.rigidbodies):
        name=obj[bl.RIGID_NAME] if bl.RIGID_NAME in obj else obj.name
        #print('rigidbody', name)
        rigidNameMap[name]=i
        boneIndex=boneMap[obj[bl.RIGID_BONE_NAME]]
        if boneIndex==0:
            boneIndex=-1
            bone=ex.skeleton.bones[0]
        else:
            bone=ex.skeleton.bones[boneIndex]
        # x, z, y -> x, y, z
        if obj[bl.RIGID_SHAPE_TYPE]==0:
            shape_type=pmd.SHAPE_SPHERE
            shape_size=common.Vector3(obj.scale[0], 0, 0)
        elif obj[bl.RIGID_SHAPE_TYPE]==1:
            shape_type=pmd.SHAPE_BOX
            shape_size=common.Vector3(obj.scale[0], obj.scale[2], obj.scale[1])
        elif obj[bl.RIGID_SHAPE_TYPE]==2:
            shape_type=pmd.SHAPE_CAPSULE
            shape_size=common.Vector3(obj.scale[0], obj.scale[2], 0)
        rigidBody=pmd.RigidBody(
                name.encode('cp932'), 
                collision_group=obj[bl.RIGID_GROUP],
                no_collision_group=obj[bl.RIGID_INTERSECTION_GROUP],
                bone_index=boneIndex,
                shape_position=common.Vector3(
                    obj.location.x-bone.pos[0],
                    obj.location.z-bone.pos[2],
                    obj.location.y-bone.pos[1]),
                shape_rotation=common.Vector3(
                    -obj.rotation_euler[0],
                    -obj.rotation_euler[2],
                    -obj.rotation_euler[1]),
                shape_type=shape_type,
                shape_size=shape_size,
                mass=obj[bl.RIGID_WEIGHT],
                linear_damping=obj[bl.RIGID_LINEAR_DAMPING],
                angular_damping=obj[bl.RIGID_ANGULAR_DAMPING],
                restitution=obj[bl.RIGID_RESTITUTION],
                friction=obj[bl.RIGID_FRICTION],
                mode=obj[bl.RIGID_PROCESS_TYPE]
                )
        model.rigidbodies.append(rigidBody)

    # constraint
    model.joints=[pmd.Joint(
        name=obj[bl.CONSTRAINT_NAME].encode('cp932'),
        rigidbody_index_a=rigidNameMap[obj[bl.CONSTRAINT_A]],
        rigidbody_index_b=rigidNameMap[obj[bl.CONSTRAINT_B]],
        position=common.Vector3(
            obj.location[0], 
            obj.location[2], 
            obj.location[1]),
        rotation=common.Vector3(
            -obj.rotation_euler[0], 
            -obj.rotation_euler[2], 
            -obj.rotation_euler[1]),
        translation_limit_min=common.Vector3(
            obj[bl.CONSTRAINT_POS_MIN][0],
            obj[bl.CONSTRAINT_POS_MIN][1],
            obj[bl.CONSTRAINT_POS_MIN][2]
            ),
        translation_limit_max=common.Vector3(
            obj[bl.CONSTRAINT_POS_MAX][0],
            obj[bl.CONSTRAINT_POS_MAX][1],
            obj[bl.CONSTRAINT_POS_MAX][2]
            ),
        rotation_limit_min=common.Vector3(
            obj[bl.CONSTRAINT_ROT_MIN][0],
            obj[bl.CONSTRAINT_ROT_MIN][1],
            obj[bl.CONSTRAINT_ROT_MIN][2]),
        rotation_limit_max=common.Vector3(
            obj[bl.CONSTRAINT_ROT_MAX][0],
            obj[bl.CONSTRAINT_ROT_MAX][1],
            obj[bl.CONSTRAINT_ROT_MAX][2]),
        spring_constant_translation=common.Vector3(
            obj[bl.CONSTRAINT_SPRING_POS][0],
            obj[bl.CONSTRAINT_SPRING_POS][1],
            obj[bl.CONSTRAINT_SPRING_POS][2]),
        spring_constant_rotation=common.Vector3(
            obj[bl.CONSTRAINT_SPRING_ROT][0],
            obj[bl.CONSTRAINT_SPRING_ROT][1],
            obj[bl.CONSTRAINT_SPRING_ROT][2])
        )
        for obj in ex.oneSkinMesh.constraints]

    bl.message('write: %s' % path)
    with io.open(path, 'wb') as f:
        return writer.write(f, model)


def _execute(filepath='', **kwargs):
    active=bl.object.getActive()
    if not active:
        print("abort. no active object.")
        return

    ex=exporter.Exporter()
    ex.setup()

    write(ex, filepath)
    bl.object.activate(active)
    return {'FINISHED'}


class ExportPmd(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    '''Export to PMD file format (.pmd)'''
    bl_idname = 'export_scene.mmd_pmd'
    bl_label = 'Export PMD'

    filename_ext = '.pmd'
    filter_glob = bpy.props.StringProperty(
            default='*.pmd', options={'HIDDEN'})

    use_selection = bpy.props.BoolProperty(
            name='Selection Only', 
            description='Export selected objects only', 
            default=False)

    def execute(self, context):
        bl.initialize('pmd_export', context.scene)
        _execute(**self.as_keywords(
            ignore=('check_existing', 'filter_glob', 'use_selection')))
        bl.finalize()
        return {'FINISHED'}

    @classmethod
    def menu_func(klass, self, context):
        default_path=bpy.data.filepath.replace('.blend', '.pmd')
        self.layout.operator(klass.bl_idname,
                text='Miku Miku Dance Model(.pmd)',
                icon='PLUGIN'
                ).filepath=default_path
