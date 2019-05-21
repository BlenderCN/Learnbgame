# coding: utf-8
"""
pmx reader
"""
import io
import os
from .. import common
from .. import pmx


class Reader(common.BinaryReader):
    """pmx reader
    """
    def __init__(self, ios,
            text_encoding,
            extended_uv,
            vertex_index_size,
            texture_index_size,
            material_index_size,
            bone_index_size,
            morph_index_size,
            rigidbody_index_size
            ):
        super(Reader, self).__init__(ios)
        self.read_text=self.get_read_text(text_encoding)
        if extended_uv>0:
            raise common.ParseException(
                    "extended uv is not supported", extended_uv)
        if vertex_index_size <= 2:
            self.read_vertex_index=lambda : self.read_uint(vertex_index_size)
        else:
            self.read_vertex_index=lambda : self.read_int(vertex_index_size)
        self.read_texture_index=lambda : self.read_int(texture_index_size)
        self.read_material_index=lambda : self.read_int(material_index_size)
        self.read_bone_index=lambda : self.read_int(bone_index_size)
        self.read_morph_index=lambda : self.read_int(morph_index_size)
        self.read_rigidbody_index=lambda : self.read_int(rigidbody_index_size)

    def __str__(self):
        return '<pmx.Reader>'

    def get_read_text(self, text_encoding):
        if text_encoding==0:
            def read_text():
                size=self.read_int(4)
                return self.unpack("{0}s".format(size), size).decode("utf-16-le")
            return read_text
        elif text_encoding==1:
            def read_text():
                size=self.read_int(4)
                return self.unpack("{0}s".format(size), size).decode("UTF8")
            return read_text
        else:
            print("unknown text encoding", text_encoding)

    def read_vertex(self):
        return pmx.Vertex(
                self.read_vector3(), # pos
                self.read_vector3(), # normal
                self.read_vector2(), # uv
                self.read_deform(), # deform(bone weight)
                self.read_float() # edge factor
                )

    def read_deform(self):
        deform_type=self.read_int(1)
        if deform_type==0:
            return pmx.Bdef1(self.read_bone_index())
        elif deform_type==1:
            return pmx.Bdef2(
                    self.read_bone_index(),
                    self.read_bone_index(),
                    self.read_float()
                    )
        elif deform_type==2:
            return pmx.Bdef4(
                    self.read_bone_index(),
                    self.read_bone_index(),
                    self.read_bone_index(),
                    self.read_bone_index(),
                    self.read_float(),
                    self.read_float(),
                    self.read_float(),
                    self.read_float()
                    )
        elif deform_type==3:
            return pmx.Sdef(
                    self.read_bone_index(),
                    self.read_bone_index(),
                    self.read_float(),
                    self.read_vector3(),
                    self.read_vector3(),
                    self.read_vector3()
                    )
        else:
            raise common.ParseException(
                    "unknown deform type: {0}".format(deform_type))

    def read_material(self):
        material=pmx.Material(
                name=self.read_text(),
                english_name=self.read_text(),
                diffuse_color=self.read_rgb(),
                alpha=self.read_float(),
                specular_color=self.read_rgb(),
                specular_factor=self.read_float(),
                ambient_color=self.read_rgb(),
                flag=self.read_int(1),
                edge_color=self.read_rgba(),
                edge_size=self.read_float(),
                texture_index=self.read_texture_index(),
                sphere_texture_index=self.read_texture_index(),
                sphere_mode=self.read_int(1),
                toon_sharing_flag=self.read_int(1),
                )
        if material.toon_sharing_flag==0:
            material.toon_texture_index=self.read_texture_index()
        elif material.toon_sharing_flag==1:
            material.toon_texture_index=self.read_int(1)
        else:
            raise common.ParseException(
                    "unknown toon_sharing_flag {0}".format(
                        material.toon_sharing_flag))
        material.comment=self.read_text()
        material.vertex_count=self.read_int(4)
        return material

    def read_bone(self):
        bone=pmx.Bone(
                name=self.read_text(),
                english_name=self.read_text(),
                position=self.read_vector3(),
                parent_index=self.read_bone_index(),
                layer=self.read_int(4),
                flag=self.read_int(2)                
                )
        if not bone.getConnectionFlag():
            bone.tail_position=self.read_vector3()
        elif bone.getConnectionFlag():
            bone.tail_index=self.read_bone_index()
        else:
            raise common.ParseException(
                    "unknown bone conenction flag: {0}".format(
                bone.getConnectionFlag()))

        if bone.getExternalRotationFlag() or bone.getExternalTranslationFlag():
            bone.effect_index=self.read_bone_index()
            bone.effect_factor=self.read_float()

        if bone.getFixedAxisFlag():
            bone.fixed_axis=self.read_vector3()

        if bone.getLocalCoordinateFlag():
            bone.local_x_vector=self.read_vector3()
            bone.local_z_vector=self.read_vector3()

        if bone.getExternalParentDeformFlag():
            bone.external_key=self.read_int(4)

        if bone.getIkFlag():
            bone.ik=self.read_ik()

        return bone

    def read_ik(self):
        ik=pmx.Ik(
                target_index=self.read_bone_index(),
                loop=self.read_int(4),
                limit_radian=self.read_float())
        link_size=self.read_int(4)
        ik.link=[self.read_ik_link() 
                for _ in range(link_size)]
        return ik

    def read_ik_link(self):
        link=pmx.IkLink(
                self.read_bone_index(),
                self.read_int(1))
        if link.limit_angle==0:
            pass
        elif link.limit_angle==1:
            link.limit_min=self.read_vector3()
            link.limit_max=self.read_vector3()
        else:
            raise common.ParseException(
                    "invalid ik link limit_angle: {0}".format(
                link.limit_angle))
        return link

    def read_morgh(self):
        name=self.read_text()
        english_name=self.read_text()
        panel=self.read_int(1)
        morph_type=self.read_int(1)
        offset_size=self.read_int(4)
        morph=pmx.Morph(name, english_name, 
                panel, morph_type)
        if morph_type==0:
            # group
            morph.offsets=[self.read_group_morph_data() 
                    for _ in range(offset_size)]
        elif morph_type==1:
            # vertex
            morph.offsets=[self.read_vertex_position_morph_offset() 
                    for _ in range(offset_size)]
        elif morph_type==2:
            # bone
            morph.offsets=[self.read_bone_morph_data()
                    for _ in range(offset_size)]
        elif morph_type==3:
            # uv
            morph.offsets=[self.read_uv_morph_data()
                    for _ in range(offset_size)]
        elif morph_type==4:
            # uv extended1
            morph.offsets=[self.read_uv_morph_data()
                    for _ in range(offset_size)]
        elif morph_type==5:
            # uv extended2
            morph.offsets=[self.read_uv_morph_data()
                    for _ in range(offset_size)]
        elif morph_type==6:
            # uv extended3
            morph.offsets=[self.read_uv_morph_data()
                    for _ in range(offset_size)]
        elif morph_type==7:
            # uv extended4
            morph.offsets=[self.read_uv_morph_data()
                    for _ in range(offset_size)]
        elif morph_type==8:
            # material
            morph.data=[self.read_material_morph_data()
                    for _ in range(offset_size)]
        else:
            raise common.ParseException(
                    "unknown morph type: {0}".format(morph_type))
        return morph

    def read_group_morph_data(self):
        return pmx.GroupMorphData(
                self.read_morph_index(), 
                self.read_float()
                )

    def read_vertex_position_morph_offset(self):
        return pmx.VertexMorphOffset(
                self.read_vertex_index(), self.read_vector3())

    def read_bone_morph_data(self):
        return pmx.BoneMorphData(
                self.read_bone_index(), 
                self.read_vector3(),
                self.read_quaternion()
                )

    def read_uv_morph_data(self):
        return pmx.UVMorphData(
                self.read_vertex_index(), 
                self.read_vector4(),
                )

    def read_material_morph_data(self):
        return pmx.MaterialMorphData(
                self.read_material_index(),
                self.read_int(1),
                self.read_rgba(),
                self.read_rgb(), self.read_float(),
                self.read_rgb(),
                self.read_rgba(),
                self.read_float(),
                self.read_rgba(),
                self.read_rgba(),
                self.read_rgba()
                )

    def read_display_slot(self):
        display_slot=pmx.DisplaySlot(self.read_text(), self.read_text(), 
                self.read_int(1))
        display_count=self.read_int(4)
        for _ in range(display_count):
            display_type=self.read_int(1)
            if display_type==0:
                display_slot.references.append(
                        (display_type, self.read_bone_index()))
            elif display_type==1:
                display_slot.references.append(
                        (display_type, self.read_morph_index()))
            else:
                raise common.ParseException(
                        "unknown display_type: {0}".format(display_type))
        return display_slot

    def read_rigidbody(self):
        return pmx.RigidBody(
                name=self.read_text(), 
                english_name=self.read_text(),
                bone_index=self.read_bone_index(),
                collision_group=self.read_int(1),
                no_collision_group=self.read_int(2),
                shape_type=self.read_int(1),
                shape_size=self.read_vector3(),
                shape_position=self.read_vector3(),
                shape_rotation=self.read_vector3(),
                mass=self.read_float(),
                linear_damping=self.read_float(),
                angular_damping=self.read_float(),
                restitution=self.read_float(),
                friction=self.read_float(),
                mode=self.read_int(1)
                )

    def read_joint(self):
        return pmx.Joint(
                name=self.read_text(),
                english_name=self.read_text(),
                joint_type=self.read_int(1),
                rigidbody_index_a=self.read_rigidbody_index(),
                rigidbody_index_b=self.read_rigidbody_index(),
                position=self.read_vector3(),
                rotation=self.read_vector3(),
                translation_limit_min=self.read_vector3(),
                translation_limit_max=self.read_vector3(),
                rotation_limit_min=self.read_vector3(),
                rotation_limit_max=self.read_vector3(),
                spring_constant_translation=self.read_vector3(),
                spring_constant_rotation=self.read_vector3())


def read_from_file(path):
    """
    read from file path, then return the pmx.Model.

    :Parameters:
      path
        file path

    >>> import pmx.reader
    >>> m=pmx.reader.read_from_file('resources/初音ミクVer2.pmx')
    >>> print(m)
    <pmx-2.0 "Miku Hatsune" 12354vertices>

    """
    if not os.path.exists(path):
        print("{0} is not exist !".format(path))
        return
    pmx=read(io.BytesIO(common.readall(path)))
    pmx.path=path
    return pmx


def read(ios):
    """
    read from ios, then return the pmx pmx.Model.

    :Parameters:
      ios
        input stream (in io.IOBase)

    >>> import pmx.reader
    >>> m=pmx.reader.read(io.open('resources/初音ミクVer2.pmx', 'rb'))
    >>> print(m)
    <pmx-2.0 "Miku Hatsune" 12354vertices>

    """
    assert(isinstance(ios, io.IOBase))
    reader=common.BinaryReader(ios)

    # header
    signature=reader.unpack("4s", 4)
    if signature!=b"PMX ":
        raise common.ParseException(
                "invalid signature", signature)

    version=reader.read_float()
    if version!=2.0:
        print("unknown version", version)
    model=pmx.Model(version)

    # flags
    flag_bytes=reader.read_int(1)
    if flag_bytes!=8:
        raise common.ParseException(
                "invalid flag length", reader.flag_bytes)
    text_encoding=reader.read_int(1)
    extended_uv=reader.read_int(1)
    vertex_index_size=reader.read_int(1)
    texture_index_size=reader.read_int(1)
    material_index_size=reader.read_int(1)
    bone_index_size=reader.read_int(1)
    morph_index_size=reader.read_int(1)
    rigidbody_index_size=reader.read_int(1)
    
    # pmx custom reader
    reader=Reader(reader.ios,
            text_encoding,
            extended_uv,
            vertex_index_size,
            texture_index_size,
            material_index_size,
            bone_index_size,
            morph_index_size,
            rigidbody_index_size
            )

    # model info
    model.name = reader.read_text()
    model.english_name = reader.read_text()
    model.comment = reader.read_text()
    model.english_comment = reader.read_text()

    # model data
    model.vertices=[reader.read_vertex() 
            for _ in range(reader.read_int(4))]
    model.indices=[reader.read_vertex_index() 
            for _ in range(reader.read_int(4))]
    model.textures=[reader.read_text() 
            for _ in range(reader.read_int(4))]
    model.materials=[reader.read_material() 
            for _ in range(reader.read_int(4))]
    model.bones=[reader.read_bone() 
            for _ in range(reader.read_int(4))]
    model.morphs=[reader.read_morgh() 
            for _ in range(reader.read_int(4))]
    model.display_slots=[reader.read_display_slot() 
            for _ in range(reader.read_int(4))]
    model.rigidbodies=[reader.read_rigidbody()
            for _ in range(reader.read_int(4))]
    model.joints=[reader.read_joint()
            for _ in range(reader.read_int(4))]

    return model

