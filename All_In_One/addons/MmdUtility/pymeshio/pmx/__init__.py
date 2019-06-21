#!/usr/bin/env python
# coding: utf-8
"""
========================
MikuMikuDance PMX format
========================

file format
~~~~~~~~~~~
* PMDEditor's Lib/PMX仕様/PMX仕様.txt

specs
~~~~~
* textencoding: unicode
* coordinate: left handed y-up(DirectX)
* uv origin: 
* face: only triangle
* backculling: 

"""
__author__="ousttrue"
__license__="zlib"
__versioon__="1.0.0"


import io
import os
import struct
from .. import common



class Ik(common.Diff):
    """ik info
    """
    __slots__=[
            'target_index',
            'loop',
            'limit_radian',
            'link',
            ]
    def __init__(self, target_index, loop, limit_radian, link=None):
        self.target_index=target_index
        self.loop=loop
        self.limit_radian=limit_radian
        self.link=link or []

    def __eq__(self, rhs):
        return (
                self.target_index==rhs.target_index
                and self.loop==rhs.loop
                and self.limit_radian==rhs.limit_radian
                and self.link==rhs.link
                )

    def diff(self, rhs):
        self._diff(rhs, 'target_index')
        self._diff(rhs, 'loop')
        self._diff(rhs, 'limit_radian')
        self._diff_array(rhs, 'link')


class IkLink(common.Diff):
    """ik link info
    """
    __slots__=[
            'bone_index',
            'limit_angle',
            'limit_min',
            'limit_max',
            ]
    def __init__(self, bone_index, limit_angle, limit_min=None, limit_max=None):
        self.bone_index=bone_index
        self.limit_angle=limit_angle
        self.limit_min=limit_min or common.Vector3()
        self.limit_max=limit_max or common.Vector3()

    def __eq__(self, rhs):
        return (
                self.bone_index==rhs.bone_index
                and self.limit_angle==rhs.limit_angle
                and self.limit_min==rhs.limit_min
                and self.limit_max==rhs.limit_max
                )

    def diff(self, rhs):
        self._diff(rhs, 'bone_index')
        self._diff(rhs, 'limit_angle')
        self._diff(rhs, 'limit_min')
        self._diff(rhs, 'limit_max')


BONEFLAG_TAILPOS_IS_BONE=0x0001
BONEFLAG_CAN_ROTATE=0x0002
BONEFLAG_CAN_TRANSLATE=0x0004
BONEFLAG_IS_VISIBLE=0x0008
BONEFLAG_CAN_MANIPULATE=0x0010
BONEFLAG_IS_IK=0x0020
BONEFLAG_IS_EXTERNAL_ROTATION=0x0100
BONEFLAG_IS_EXTERNAL_TRANSLATION=0x0200
BONEFLAG_HAS_FIXED_AXIS=0x0400
BONEFLAG_HAS_LOCAL_COORDINATE=0x0800
BONEFLAG_IS_AFTER_PHYSICS_DEFORM=0x1000
BONEFLAG_IS_EXTERNAL_PARENT_DEFORM=0x2000
class Bone(common.Diff):
    """material

    Bone: see __init__
    """
    __slots__=[
            'name',
            'english_name',
            'position',
            'parent_index',
            'layer',
            'flag',

            'tail_position',
            'tail_index',
            'effect_index',
            'effect_factor',
            'fixed_axis',
            'local_x_vector',
            'local_z_vector',
            'external_key',
            'ik',

            'index',
            ]
    def __init__(self,
            name,
            english_name,
            position,
            parent_index,
            layer,
            flag,
            tail_position=None,
            tail_index=-1,
            effect_index=-1,
            effect_factor=0.0,
            fixed_axis=None,
            local_x_vector=None,
            local_z_vector=None,
            external_key=-1,
            ik=None
            ):
        self.name=name
        self.english_name=english_name
        self.position=position
        self.parent_index=parent_index
        self.layer=layer
        self.flag=flag
        self.tail_position=tail_position or common.Vector3()
        self.tail_index=tail_index
        self.effect_index=effect_index
        self.effect_factor=effect_factor
        self.fixed_axis=fixed_axis or common.Vector3()
        self.local_x_vector=local_x_vector or common.Vector3()
        self.local_z_vector=local_z_vector or common.Vector3()
        self.external_key=external_key
        self.ik=ik
        self.index=-1

    def __str__(self):
        return ("<pmx.Bone {name}>".format(
            name=self.name
            ))

    def __eq__(self, rhs):
        return (
                self.name==rhs.name
                and self.english_name==rhs.english_name
                and self.position==rhs.position
                and self.parent_index==rhs.parent_index
                and self.layer==rhs.layer
                and self.flag==rhs.flag
                )

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def diff(self, rhs):
        self._diff(rhs, 'name')
        self._diff(rhs, 'english_name')
        self._diff(rhs, 'position')
        self._diff(rhs, 'parent_index')
        #self._diff(rhs, 'layer')
        self._diff(rhs, 'flag')
        self._diff(rhs, 'tail_position')
        self._diff(rhs, 'tail_index')
        self._diff(rhs, 'effect_index')
        self._diff(rhs, 'effect_factor')
        self._diff(rhs, 'fixed_axis')
        self._diff(rhs, 'local_x_vector')
        self._diff(rhs, 'local_z_vector')
        self._diff(rhs, 'external_key')
        if self.ik and rhs.ik:
            self.ik.diff(rhs.ik)
        else:
            self._diff(rhs, 'ik')

    def hasFlag(self, flag):
        return (self.flag & flag)!=0

    def setFlag(self, flag, enable):
        if enable:
            self.flag |= flag
        else:
            self.flag &= ~flag

    def getConnectionFlag(self):
        return self.hasFlag(BONEFLAG_TAILPOS_IS_BONE)

    def getRotatable(self):
        return self.hasFlag(BONEFLAG_CAN_ROTATE)

    def getTranslatable(self):
        return self.hasFlag(BONEFLAG_CAN_TRANSLATE)

    def getVisibleFlag(self):
        return self.hasFlag(BONEFLAG_IS_VISIBLE)

    def getManipulatable(self):
        return self.hasFlag(BONEFLAG_CAN_MANIPULATE)

    def getIkFlag(self):
        return self.hasFlag(BONEFLAG_IS_IK)

    def getExternalRotationFlag(self):
        return self.hasFlag(BONEFLAG_IS_EXTERNAL_ROTATION)

    def getExternalTranslationFlag(self):
        return self.hasFlag(BONEFLAG_IS_EXTERNAL_TRANSLATION)

    def getFixedAxisFlag(self):
        return self.hasFlag(BONEFLAG_HAS_FIXED_AXIS)

    def getLocalCoordinateFlag(self):
        return self.hasFlag(BONEFLAG_HAS_LOCAL_COORDINATE)
    
    def getAfterPhysicsDeformFlag(self):
        return self.hasFlag(BONEFLAG_IS_AFTER_PHYSICS_DEFORM)

    def getExternalParentDeformFlag(self):
        return self.hasFlag(BONEFLAG_IS_EXTERNAL_PARENT_DEFORM)

 
MATERIALFLAG_BOTHFACE=0x01
MATERIALFLAG_GROUNDSHADOW=0x02
MATERIALFLAG_SELFSHADOWMAP=0x04
MATERIALFLAG_SELFSHADOW=0x08
MATERIALFLAG_EDGE=0x10
MATERIALSPHERE_NONE=0
MATERIALSPHERE_SPH=1
MATERIALSPHERE_SPA=2
class Material(common.Diff):
    """material

    Attributes: see __init__
    """
    __slots__=[
            'name',
            'english_name',
            'diffuse_color',
            'alpha',
            'specular_color',
            'specular_factor',
            'ambient_color',
            'flag',
            'edge_color',
            'edge_size',
            'texture_index',
            'sphere_texture_index',
            'sphere_mode',
            'toon_sharing_flag',
            'toon_texture_index',
            'comment',
            'vertex_count',
            ]
    def __init__(self,
            name,
            english_name,
            diffuse_color,
            alpha,
            specular_factor,
            specular_color,
            ambient_color,
            flag,
            edge_color,
            edge_size,
            texture_index,
            sphere_texture_index,
            sphere_mode,
            toon_sharing_flag,
            toon_texture_index=0,
            comment=common.unicode(""),
            vertex_count=0,
            ):
        self.name=name
        self.english_name=english_name
        self.diffuse_color=diffuse_color
        self.alpha=alpha
        self.specular_color=specular_color
        self.specular_factor=specular_factor
        self.ambient_color=ambient_color
        self.flag=flag
        self.edge_color=edge_color
        self.edge_size=edge_size
        self.texture_index=texture_index
        self.sphere_texture_index=sphere_texture_index
        self.sphere_mode=sphere_mode
        self.toon_sharing_flag=toon_sharing_flag
        self.toon_texture_index=toon_texture_index
        self.comment=comment
        self.vertex_count=vertex_count

    def hasFlag(self, mask):
        return (self.flag & mask)!=0

    def __eq__(self, rhs):
        return (
                self.name==rhs.name
                and self.english_name==rhs.english_name
                and self.diffuse_color==rhs.diffuse_color
                and self.alpha==rhs.alpha
                and self.specular_color==rhs.specular_color
                and self.specular_factor==rhs.specular_factor
                and self.ambient_color==rhs.ambient_color
                and self.flag==rhs.flag
                and self.edge_color==rhs.edge_color
                and self.edge_size==rhs.edge_size
                and self.texture_index==rhs.texture_index
                and self.sphere_texture_index==rhs.sphere_texture_index
                and self.sphere_mode==rhs.sphere_mode
                and self.toon_sharing_flag==rhs.toon_sharing_flag
                and self.toon_texture_index==rhs.toon_texture_index
                and self.comment==rhs.comment
                and self.vertex_count==rhs.vertex_count
                )

    def diff(self, rhs):
        #self._diff(rhs, "name")
        self._diff(rhs, "english_name")
        self._diff(rhs, "diffuse_color")
        self._diff(rhs, "alpha")
        self._diff(rhs, "specular_color")
        self._diff(rhs, "specular_factor")
        self._diff(rhs, "ambient_color")
        self._diff(rhs, "flag")
        self._diff(rhs, "edge_color")
        self._diff(rhs, "edge_size")
        self._diff(rhs, "texture_index")
        self._diff(rhs, "sphere_texture_index")
        self._diff(rhs, "sphere_mode")
        self._diff(rhs, "toon_sharing_flag")
        self._diff(rhs, "toon_texture_index")
        self._diff(rhs, "comment")
        self._diff(rhs, "vertex_count")

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def __str__(self):
        return ("<pmx.Material {name}>".format(
            name=self.english_name
            ))


class Bdef1(common.Diff):
    """bone deform. use a weight

    Attributes: see __init__
    """
    __slots__=[ 'index0']
    def __init__(self, index0):
        self.index0=index0

    def __str__(self):
        return "<Bdef1 {0}>".format(self.index0)

    def __eq__(self, rhs):
        return self.index0==rhs.index0

    def __ne__(self, rhs):
        return not self.__eq__(rhs)


class Bdef2(common.Diff):
    """bone deform. use two weights

    Attributes: see __init__
    """
    __slots__=[ 'index0', 'index1', 'weight0']
    def __init__(self, 
            index0,
            index1,
            weight0):
        self.index0=index0
        self.index1=index1
        self.weight0=weight0

    def __str__(self):
        return "<Bdef2 {0}, {1}, {2}>".format(self.index0, self.index1, self.weight0)

    def __eq__(self, rhs):
        return (
                self.index0==rhs.index0
                and self.index1==rhs.index1
                #and self.weight0==rhs.weight0
                and abs(self.weight0-rhs.weight0)<1e-5
                )

    def __ne__(self, rhs):
        return not self.__eq__(rhs)


class Bdef4(common.Diff):
    """bone deform. use four weights

    Attributes: see __init__
    """
    __slots__=[ 'index0', 'index1', 'index2', 'index3',
            'weight0', 'weight1', 'weight2', 'weight3']
    def __init__(self, 
            index0,
            index1,
            index2,
            index3,
            weight0,
            weight1,
            weight2,
            weight3):
        self.index0=index0
        self.index1=index1
        self.index2=index2
        self.index3=index3
        self.weight0=weight0
        self.weight1=weight1
        self.weight2=weight2
        self.weight3=weight3

    def __str__(self):
        return "<Bdef4 {0}:{1}, {2}:{3}, {4}:{5}, {6}:{7}>".format(
                self.index0, self.index1, self.index2, self.index3,
                self.weight0, self.weight1, self.weight2, self.weight3)

    def __eq__(self, rhs):
        return (
                self.index0==rhs.index0
                and self.index1==rhs.index1
                and self.index2==rhs.index2
                and self.index3==rhs.index3
                and abs(self.weight0-rhs.weight0)<1e-5
                and abs(self.weight1-rhs.weight1)<1e-5
                and abs(self.weight2-rhs.weight2)<1e-5
                and abs(self.weight3-rhs.weight3)<1e-5
                )

    def __ne__(self, rhs):
        return not self.__eq__(rhs)


class Sdef(common.Diff):
    """bone sphirical deform. use two weights and sphirical params

    Attributes: see __init__
    """
    __slots__=[ 'index0', 'index1', 'weight0', 
            'sdef_c', 'sdef_r0', 'sdef_r1']
    def __init__(self, 
            index0,
            index1,
            weight0,
            sdef_c,
            sdef_r0,
            sdef_r1):
        self.index0=index0
        self.index1=index1
        self.weight0=weight0
        self.sdef_c=sdef_c
        self.sdef_r0=sdef_r0
        self.sdef_r1=sdef_r1

    def __str__(self):
        return "<Sdef {0}, {1}, {2}, {3} {4} {5}>".format(
                self.index0, self.index1, self.weight0, 
                self.sdef_c, self.sdef_r0, self.sdef_r1)

    def __eq__(self, rhs):
        return (
                self.index0==rhs.index0
                and self.index1==rhs.index1
                #and self.weight0==rhs.weight0
                and abs(self.weight0-rhs.weight0)<1e-5
                and self.sdef_c==rhs.sdef_c
                and self.sdef_r0==rhs.sdef_r0
                and self.sdef_r1==rhs.sdef_r1
                )

    def __ne__(self, rhs):
        return not self.__eq__(rhs)


class Vertex(common.Diff):
    """
    ==========
    pmx vertex
    ==========

    :IVariables:
        position
            Vector3
        normal 
            Vector3
        uv 
            Vector2
        deform
            Bdef1, Bdef2 or Bdef4
        edge_factor
            float
    """
    __slots__=[ 'position', 'normal', 'uv', 'deform', 'edge_factor' ]
    def __init__(self, 
            position, 
            normal, 
            uv, 
            deform, 
            edge_factor):
        self.position=position 
        self.normal=normal
        self.uv=uv
        self.deform=deform
        self.edge_factor=edge_factor

    def __str__(self):
        return "<Vertex position:{0}, normal:{1}, uv:{2}, deform:{3}, edge:{4}".format(
                self.position, self.normal, self.uv, self.deform, self.edge_factor
                )

    def __eq__(self, rhs):
        return (
                self.position==rhs.position
                and self.normal==rhs.normal
                and self.uv==rhs.uv
                and self.deform==rhs.deform
                and self.edge_factor==rhs.edge_factor
                )

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def diff(self, rhs):
        self._diff(rhs, "position")
        self._diff(rhs, "normal")
        self._diff(rhs, "uv")
        self._diff(rhs, "deform")
        self._diff(rhs, "edge_factor")


class Morph(common.Diff):
    """pmx morph

    Attributes:
        name: 
        english_name: 
        panel:
        morph_type:
        offsets:
    """
    __slots__=[
            'name',
            'english_name',
            'panel',
            'morph_type',
            'offsets',
            ]
    def __init__(self, name, english_name, panel, morph_type, offsets=None):
        self.name=name
        self.english_name=english_name
        self.panel=panel
        self.morph_type=morph_type
        self.offsets=offsets or []

    def __eq__(self, rhs):
        return (
                self.name==rhs.name
                and self.english_name==rhs.english_name
                and self.panel==rhs.panel
                and self.morph_type==rhs.morph_type
                and self.offsets==rhs.offsets
                )

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def diff(self, rhs):
        self._diff(rhs, 'name')
        self._diff(rhs, 'english_name')
        self._diff(rhs, 'panel')
        self._diff(rhs, 'morph_type')
        #self._diff_array(rhs, 'offsets')


class VertexMorphOffset(common.Diff):
    """pmx vertex morph offset

    Attributes:
        vertex_index:
        position_offset: Vector3
    """
    __slots__=[
            'vertex_index',
            'position_offset',
            ]
    def __init__(self, vertex_index, position_offset):
        self.vertex_index=vertex_index
        self.position_offset=position_offset

    def __eq__(self, rhs):
        return (
                self.vertex_index==rhs.vertex_index 
                and self.position_offset==rhs.position_offset
                )

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def diff(self, rhs):
        self._diff(rhs, 'vertex_index')
        self._diff(rhs, 'position_offset')


class BoneMorphData(common.Diff):
    """pmx bone morph data

    Attributes:
        bone_index:
        position: Vector3
        rotation: Quaternion
    """
    __slots__=[
            'bone_index',
            'position',
            'rotation',
            ]
    def __init__(self, bone_index, position, rotation):
        self.bone_index=bone_index
        self.position=position
        self.rotation=rotation

    def __eq__(self, rhs):
        return (
                self.bone_index==rhs.bone_index 
                and self.position==rhs.position
                and self.rotation==rhs.rotation
                )

    def diff(self, rhs):
        self._diff(rhs, 'bone_index')
        self._diff(rhs, 'position')
        self._diff(rhs, 'rotation')


class UVMorphData(common.Diff):
    """pmx uv morph data

    Attributes:
        vertex_index:
        position: Vector4
    """
    __slots__=[
            'vertex_index',
            'uv',
            ]
    def __init__(self, vertex_index, uv):
        self.vertex_index=vertex_index
        self.uv=uv

    def __eq__(self, rhs):
        return (
                self.vertex_index==rhs.vertex_index 
                and self.uv==rhs.uv
                )

    def diff(self, rhs):
        self._diff(rhs, 'vertex_index')
        self._diff(rhs, 'uv')


class MaterialMorphData(common.Diff):
    """pmx mateerial morph data

    Attributes:
    """
    __slots__=[
            'material_index',
            'calc_mode',
            'diffuse',
            'specular',
            'specular_factor',
            'ambient',
            'edge_color',
            'edge_size',
            'texture_factor',
            'sphere_texture_factor',
            'toon_texture_factor',
            ]
    def __init__(self, material_index, calc_mode, 
            diffuse, specular, specular_factor,
            ambient, edge_color, edge_size, 
            texture_factor, sphere_texture_factor, toon_texture_factor):
        self.material_index=material_index
        self.calc_mode=calc_mode
        self.diffuse=diffuse
        self.specular=specular
        self.specular_factor=specular_factor
        self.ambient=ambient
        self.edge_color=edge_color
        self.edge_size=edge_size
        self.texture_factor=texture_factor
        self.sphere_texture_factor=sphere_texture_factor
        self.toon_texture_factor=toon_texture_factor


class GroupMorphData(common.Diff):
    """pmx group morph data

    Attributes:
    """
    __slots__=[
            'morph_index',
            'value',
            ]
    def __init__(self, morph_index, value):
        self.morph_index=morph_index
        self.value=value


class DisplaySlot(common.Diff):
    """pmx display slot

    Attributes:
        name: 
        english_name: 
        special_flag:
        references: list of (ref_type, ref_index)
    """
    __slots__=[
            'name',
            'english_name',
            'special_flag',
            'references',
            ]
    def __init__(self, name, english_name, special_flag, references=None):
        self.name=name
        self.english_name=english_name
        self.special_flag=special_flag
        self.references=references or []

    def __str__(self):
        return "<DisplaySlots %s(%d)>" % (self.english_name, len(self.references))

    def __eq__(self, rhs):
        return (
                self.name==rhs.name
                and self.english_name==rhs.english_name
                and self.special_flag==rhs.special_flag
                and self.references==rhs.references
                )

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def diff(self, rhs):
        self._diff(rhs, 'name')
        self._diff(rhs, 'english_name')
        self._diff(rhs, 'special_flag')
        #self._diff_array(rhs, 'references')


class RigidBodyParam(common.Diff):
    """pmx rigidbody param(for bullet)

    Attributes:
        mass:
        linear_damping:
        angular_damping:
        restitution:
        friction:
    """
    __slots__=[
            'mass',
            'linear_damping',
            'angular_damping',
            'restitution',
            'friction',
            ]
    def __init__(self, mass, 
            linear_damping, angular_damping, restitution, friction):
        self.mass=mass
        self.linear_damping=linear_damping
        self.angular_damping=angular_damping
        self.restitution=restitution
        self.friction=friction

    def __eq__(self, rhs):
        return (
                self.mass==rhs.mass
                and self.linear_damping==rhs.linear_damping
                and self.angular_damping==rhs.angular_damping
                and self.restitution==rhs.restitution
                and self.friction==rhs.friction
                )

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def diff(self, rhs):
        self._diff(rhs, 'mass')
        self._diff(rhs, 'linear_damping')
        self._diff(rhs, 'angular_damping')
        self._diff_array(rhs, 'restitution')
        self._diff_array(rhs, 'friction')


SHAPE_SPHERE=0
SHAPE_BOX=1
SHAPE_CAPSULE=2
class RigidBody(common.Diff):
    """pmx rigidbody

    Attributes:
        name: 
        english_name: 
        bone_index:
        collision_group:
        no_collision_group:
        shape:
        param:
        mode:
    """
    __slots__=[
            'name',
            'english_name',
            'bone_index',
            'collision_group',
            'no_collision_group',
            'shape_type',
            'shape_size',
            'shape_position',
            'shape_rotation',
            'param',
            'mode',
            ]
    def __init__(self,
            name,
            english_name,
            bone_index,
            collision_group,
            no_collision_group,
            shape_type,
            shape_size,
            shape_position,
            shape_rotation,
            mass,
            linear_damping,
            angular_damping,
            restitution,
            friction,
            mode
            ):
        self.name=name
        self.english_name=english_name
        self.bone_index=bone_index
        self.collision_group=collision_group
        self.no_collision_group=no_collision_group
        self.shape_type=shape_type
        self.shape_size=shape_size
        self.shape_position=shape_position
        self.shape_rotation=shape_rotation
        self.param=RigidBodyParam(mass,
                linear_damping, angular_damping,
                restitution, friction)
        self.mode=mode

    def __str__(self):
        return ("<pmx.RigidBody {name} shape:{type}>".format(
            name=self.english_name,
            type=self.shape_type
            ))

    def __eq__(self, rhs):
        return (
                self.name==rhs.name
                and self.english_name==rhs.english_name
                and self.bone_index==rhs.bone_index
                and self.collision_group==rhs.collision_group
                and self.no_collision_group==rhs.no_collision_group
                and self.shape_type==rhs.shape_type
                and self.shape_size==rhs.shape_size
                and self.param==rhs.param
                and self.mode==rhs.mode
                )

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def diff(self, rhs):
        self._diff(rhs, 'name')
        self._diff(rhs, 'english_name')
        self._diff(rhs, 'bone_index')
        self._diff(rhs, 'collision_group')
        self._diff(rhs, 'no_collision_group')
        self._diff(rhs, 'shape_type')
        if self.shape_type==SHAPE_SPHERE: 
            if self.shape_size.x!=rhs.shape_size.x:
                print(self.shape_size)
                print(rhs.shape_size)
                raise DifferenceException('self.shape_size')
        elif self.shape_type==SHAPE_BOX:
            self._diff(rhs, 'shape_size')
        elif self.shape_type==SHAPE_CAPSULE:
            if (self.shape_size.x!=rhs.shape_size.x 
                    or self.shape_size.y!=rhs.shape_size.y):
                print(self.shape_size)
                print(rhs.shape_size)
                raise DifferenceException('self.shape_size')
        else:
            assert(False)
        self._diff(rhs, 'shape_position')
        self._diff(rhs, 'shape_rotation')
        self._diff(rhs, 'param')
        self._diff(rhs, 'mode')


class Joint(common.Diff):
    """pmx joint

    Attributes:
        name: 
        english_name: 
        joint_type:
        rigidbody_index_a:
        rigidbody_index_b:
        position: Vector3
        rotation: Vector3
        translation_limit_min: Vector3
        translation_limit_max: Vector3
        rotation_limit_min: Vector3
        rotation_limit_max: Vector3
        spring_constant_translation: Vector3
        spring_constant_rotation: Vector3
    """
    __slots__=[
            'name',
            'english_name',
            'joint_type',
            'rigidbody_index_a',
            'rigidbody_index_b',
            'position',
            'rotation',
            'translation_limit_min',
            'translation_limit_max',
            'rotation_limit_min',
            'rotation_limit_max',
            'spring_constant_translation',
            'spring_constant_rotation',
            ]
    def __init__(self, name, english_name,
            joint_type,
            rigidbody_index_a,
            rigidbody_index_b,
            position,
            rotation,
            translation_limit_min,
            translation_limit_max,
            rotation_limit_min,
            rotation_limit_max,
            spring_constant_translation,
            spring_constant_rotation
            ):
        self.name=name
        self.english_name=english_name
        self.joint_type=joint_type
        self.rigidbody_index_a=rigidbody_index_a
        self.rigidbody_index_b=rigidbody_index_b
        self.position=position
        self.rotation=rotation
        self.translation_limit_min=translation_limit_min
        self.translation_limit_max=translation_limit_max
        self.rotation_limit_min=rotation_limit_min
        self.rotation_limit_max=rotation_limit_max
        self.spring_constant_translation=spring_constant_translation
        self.spring_constant_rotation=spring_constant_rotation

    def __eq__(self, rhs):
        return (
                self.name==rhs.name
                and self.english_name==rhs.english_name
                and self.joint_type==rhs.joint_type
                and self.rigidbody_index_a==rhs.rigidbody_index_a
                and self.rigidbody_index_b==rhs.rigidbody_index_b
                and self.position==rhs.position
                and self.rotation==rhs.rotation
                and self.translation_limit_min==rhs.translation_limit_min
                and self.translation_limit_max==rhs.translation_limit_max
                and self.rotation_limit_min==rhs.rotation_limit_min
                and self.rotation_limit_max==rhs.rotation_limit_max
                and self.spring_constant_translation==rhs.spring_constant_translation
                and self.spring_constant_rotation==rhs.spring_constant_rotation
                )

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def diff(self, rhs):
        self._diff(rhs, 'name')
        self._diff(rhs, 'joint_type')
        self._diff(rhs, 'rigidbody_index_a')
        self._diff(rhs, 'rigidbody_index_b')
        self._diff(rhs, 'position')
        self._diff(rhs, 'rotation')
        self._diff(rhs, 'translation_limit_min')
        self._diff(rhs, 'translation_limit_max')
        self._diff(rhs, 'rotation_limit_min')
        self._diff(rhs, 'rotation_limit_max')
        self._diff(rhs, 'spring_constant_translation')
        self._diff(rhs, 'spring_constant_rotation')


class Model(common.Diff):
    """
    ==========
    pmx model
    ==========

    :IVariables:
        version
            pmx version(expected 2.0)
        name 
            model name
        english_name 
            model name
        comment 
            comment
        english_comment 
            comment
        vertices
            vertex list
        textures
            texture list
        materials
            material list
        bones
            bone list
        morph
            morph list
        display_slots
            display list for bone/morph grouping
        rigidbodies
            bullet physics rigidbody list
        joints
            bullet physics joint list
    """
    __slots__=[
            'path',
            'version',
            'name',
            'english_name',
            'comment',
            'english_comment',
            'vertices',
            'indices',
            'textures',
            'materials',
            'bones',
            'morphs',
            'display_slots',
            'rigidbodies',
            'joints',
            ]
    def __init__(self, version=2.0
            , name=u'空モデル'
            , english_name=u'empty model'
            , comment=u'pymeshioで生成'
            , english_comment=u'created by pymeshio'
            ):
        self.path=''
        self.version=version
        self.name=name
        self.english_name=english_name
        self.comment=comment
        self.english_comment=english_comment
        self.vertices=[]
        self.indices=[]
        self.textures=[]
        self.materials=[
                Material(u'マテリアル'
                    , u'material'
                    , common.RGB(0.5, 0.5, 1)
                    , 1.0
                    , 1
                    , common.RGB(1, 1, 1)
                    , common.RGB(0, 0, 0)
                    , 0
                    , common.RGBA(0, 0, 0, 1)
                    , 0
                    , -1
                    , -1
                    , MATERIALSPHERE_NONE
                    , 1
                    , 0
                    , u"comment"
                    , 0
                    )
                ]
        self.bones=[
                Bone(u'センター'
                    , u'center'
                    , common.Vector3()
                    , -1
                    , 0
                    , 0
                    )
                ]
        self.morphs=[]
        self.display_slots=[
                DisplaySlot(u'Root', u'Root', 1, [(0, 0)])
                ]
        self.rigidbodies=[]
        self.joints=[]

    def __str__(self):
        return ('<pmx-{version} "{name}" {vertices}vertices>'.format(
            version=self.version,
            name=self.english_name,
            vertices=len(self.vertices)
            ))

    def __eq__(self, rhs):
        return (
                self.version==rhs.version
                and self.name==rhs.name
                and self.english_name==rhs.english_name
                and self.comment==rhs.comment
                and self.english_comment==rhs.english_comment
                and self.vertices==rhs.vertices
                and self.indices==rhs.indices
                and self.textures==rhs.textures
                and self.materials==rhs.materials
                and self.bones==rhs.bones
                and self.morphs==rhs.morphs
                and self.display_slots==rhs.display_slots
                and self.rigidbodies==rhs.rigidbodies
                and self.joints==rhs.joints
                )

    def __ne__(self, rhs):
        return not self.__eq__(rhs)

    def diff(self, rhs):
        self._diff(rhs, "version")
        self._diff(rhs, "name")
        self._diff(rhs, "english_name")
        self._diff(rhs, "comment")
        self._diff(rhs, "english_comment")
        #self._diff_array(rhs, "vertices")
        #self._diff_array(rhs, "indices")
        self._diff_array(rhs, "textures")
        self._diff_array(rhs, "materials")
        self._diff_array(rhs, "bones")
        self._diff_array(rhs, "morphs")
        self._diff_array(rhs, "display_slots")
        self._diff_array(rhs, "rigidbodies")
        self._diff_array(rhs, "joints")

