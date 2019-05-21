import sys
import bpy
import struct
from mathutils import Vector

'''
class M2Loop:
    def __init__(self):
        self.timestamp = 0

    def Read(self, f):
        self.timestamp = struct.unpack("I", f.read(4))[0]

    def Write(self, f):
        f.write(struct.pack('I', self.timestamp))
'''

class C3Vector(Vector):       
    def read(self,f):
        self.x = struct.unpack("f",f.read(4))[0]
        self.y = struct.unpack("f",f.read(4))[0]
        self.z = struct.unpack("f",f.read(4))[0]

    def write(self, f):
        f.write(struct.pack("f",self.x))
        f.write(struct.pack("f",self.y))
        f.write(struct.pack("f",self.z))

class M2SplineKeyVectors(list):
    def __init__(self):
        super().__init__()
        self.append(C3Vector( (0, 0, 0)));
        self.append(C3Vector( (0, 0, 0)));
        self.append(C3Vector( (0, 0, 0)));

    def read(self,f):
        self[0].read(f)
        self[1].read(f)
        self[2].read(f)

    def write(self, f):
        self[0].write(f)
        self[1].write(f)
        self[2].write(f)
        
class M2CompQuat:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.w = 0

    def read(self,f):
        self.x = struct.unpack("h",f.read(2))[0]
        self.y = struct.unpack("h",f.read(2))[0]
        self.z = struct.unpack("h",f.read(2))[0]
        self.w = struct.unpack("h",f.read(2))[0]

    def write(self, f):
        f.write(struct.pack("h",self.x))
        f.write(struct.pack("h",self.y))
        f.write(struct.pack("h",self.z))
        f.write(struct.pack("h",self.w))

class CAaBox:
    def __init__(self):
        self.min = C3Vector( (0, 0, 0) )
        self.max = C3Vector( (0, 0, 0) )

    def read(self, f):
        self.min.read(f)
        self.max.read(f)
        
    def write(self, f):
        f.write(struct.pack('fff', self.min.x, self.min.y, self.min.z))
        f.write(struct.pack('fff', self.max.x, self.max.y, self.max.z))

class M2Array(list):
    def __init__(self):
        super().__init__()
        self.number    = 0
        self.offset    = 0
        self.type      = ''
    
    def read(self,f):
        self.number    = struct.unpack("i",f.read(4))[0]
        self.offset    = struct.unpack("i",f.read(4))[0]       
    
    def fill(self,f,type,type2 = "I"):
        self.type = type
        oldpos = f.tell()
        f.seek(self.offset)
        if(type == "M2Array"):
            for i in range(0, self.number):
                self.append(M2Array())
                self[i].read(f)
                self[i].fill(f, type2)
        elif(len(type) == 1):            
            for i in range(0, self.number):
                self.append(struct.unpack(type,f.read(struct.calcsize(type)))[0])
        else:
            for i in range(0, self.number):
                self.append(getattr(sys.modules[__name__], type)())
                self[i].read(f)
        f.seek(oldpos)
    
    def write(self, f):
        self.number = len[self]
    
        f.write(struct.pack("2i",self.number,self.offset))
        
        oldpos = f.tell()
        f.seek(self.offset)
        if(self.type == "M2Array"):
            for i in range(0, self.number):
                #self[i].offset ПРИДУМАТЬ КАК ПИСАТЬ В КОНЕЦ ФАЙЛА (ПРЕДВАРИТЕЛЬНЫЙ РАССЧЁТ РАЗМЕРА?)
                self[i].write(f)
        elif(len(self.type) == 1):            
            for i in range(0, self.number):
                f.write(struct.pack(self.type, self[i]))
        else:
            for i in range(0, self.number):
                self[i].write(f)
        f.seek(oldpos)

class M2TrackBase:
    def __init__(self):
        self.interpolation_type = 0
        self.global_sequence    = -1
        self.timestamps         = M2Array()

    def read(self, f):
        self.interpolation_type = struct.unpack("H", f.read(2))[0]
        self.global_sequence = struct.unpack("h", f.read(2))[0]
        
        self.timestamps.read(f)
        self.timestamps.fill(f,"M2Array","I")
        
    def write(self, f):
        f.write(struct.pack('H', self.interpolation_type))
        f.write(struct.pack('h', self.global_sequence))
        
        self.timestamps.write(f)
        
class M2Track(M2TrackBase):
    def __init__(self):
        super().__init__()
        self.values = M2Array()

    def read(self, f, type):
        self.interpolation_type = struct.unpack("H", f.read(2))[0]
        self.global_sequence = struct.unpack("h", f.read(2))[0]
        
        self.timestamps.read(f)
        self.timestamps.fill(f,"M2Array","I")
        
        self.values.read(f)
        self.values.fill(f,"M2Array",type)
        
    def write(self, f):
        f.write(struct.pack('H', self.interpolation_type))
        f.write(struct.pack('h', self.global_sequence))
        
        self.timestamps.write(f)
        self.values.write(f)
        
class M2Sequence:
    def __init__(self):
        self.animation_id        = 0
        self.sub_animation_id    = 0
        self.length              = 0
        self.moving_speed        = 0
        self.flags               = 0
        self.probability         = 0
        self.padding             = 0
        self.minimum_repetitions = 0
        self.maximum_repetitions = 0
        self.blend_time          = 0
        self.bounds              = CAaBox()
        self.bound_radius        = 0
        self.next_animation      = 0
        self.aliasNext           = 0   
        self.size                = 64
        
    def read(self, f):
        self.animation_id        = struct.unpack("H", f.read(2))[0]
        self.sub_animation_id    = struct.unpack("H", f.read(2))[0]
        self.length              = struct.unpack("I", f.read(4))[0]
        self.moving_speed        = struct.unpack("f", f.read(4))[0]
        self.flags               = struct.unpack("I", f.read(4))[0]
        self.probability         = struct.unpack("h", f.read(2))[0]
        self.padding             = struct.unpack("H", f.read(2))[0]
        self.minimum_repetitions = struct.unpack("I", f.read(4))[0]
        self.maximum_repetitions = struct.unpack("I", f.read(4))[0]
        self.blend_time          = struct.unpack("I", f.read(4))[0]
        self.bounds              = self.bounds.read(f)
        self.bound_radius        = struct.unpack("f", f.read(4))[0]
        self.next_animation      = struct.unpack("h", f.read(2))[0]
        self.aliasNext           = struct.unpack("H", f.read(2))[0] 

    def write(self, f):
        f.write(struct.pack('H', self.animation_id))
        f.write(struct.pack('H', self.sub_animation_id))
        f.write(struct.pack('I', self.length))
        f.write(struct.pack('f', self.moving_speed))
        f.write(struct.pack('I', self.flags))
        f.write(struct.pack('h', self.probability))
        f.write(struct.pack('H', self.padding))
        f.write(struct.pack('I', self.minimum_repetitions))
        f.write(struct.pack('I', self.maximum_repetitions))
        f.write(struct.pack('I', self.blend_time))
        self.bounds.Write(f)
        f.write(struct.pack('f', self.bound_radius))
        f.write(struct.pack('h', self.next_animation))
        f.write(struct.pack('H', self.aliasNext))

class M2CompBone:
    def __init__(self):
        self.key_bone_id = 0
        self.flags       = 0
        self.parent_bone = 0
        self.submesh_id  = 0
        self.unk         = (0,0)
        self.translation = M2Track()
        self.rotation    = M2Track()
        self.scale       = M2Track()
        self.pivot       = C3Vector( (0,0,0) )
        self.size        = 88

    def read(self, f):
        self.key_bone_id = struct.unpack("i", f.read(4))[0]
        self.flags = struct.unpack("I", f.read(4))[0]
        self.parent_bone = struct.unpack("h", f.read(2))[0]
        self.submesh_id = struct.unpack("H", f.read(2))[0]
        self.unk = struct.unpack("HH", f.read(4))
        self.translation.read(f,"C3Vector")
        self.rotation.read(f,"M2CompQuat")
        self.scale.read(f,"C3Vector")
        self.pivot.read(f)

    def write(self, f):
        f.write(struct.pack('i', self.key_bone_id))
        f.write(struct.pack('I', self.flags))
        f.write(struct.pack('h', self.parent_bone))
        f.write(struct.pack('H', self.submesh_id))
        f.write(struct.pack('HH', *self.unk))
        self.translation.write(f,"C3Vector")
        self.rotation.write(f,"M2CompQuat")
        self.scale.write(f,"C3Vector")
        self.pivot.write(f)

class M2Vertex:
    # 0x00  float   Position[3]         A vector to the position of the vertex.
    # 0x0C  uint8   BoneWeight[4]       The vertex weight for 4 bones.
    # 0x10  uint8   BoneIndices[4]      Which are referenced here.
    # 0x14  float   Normal[3]           A normal vector.
    # 0x20  float   TextureCoords[2]    Coordinates for a texture.
    # 0x28  float   Unknown[2]          Null?

    FORMAT = "<fffBBBBBBBBfffffff"
    def __init__(self):
        self.pos            = C3Vector( (0, 0, 0) )
        self.bone_weights   = ( 0, 0, 0, 0 )
        self.bone_indices   = ( 0, 0, 0, 0 )
        self.normal         = C3Vector( (0, 0, 0) )
        self.tex_coords     = Vector( (0, 0) )
        self.unknown   = ( 0, 0 )
        self.size = 48

    def read(self, f):
        self.pos.read(f)
        self.bone_weights   = struct.unpack("BBBB", f.read(4))
        self.bone_indices   = struct.unpack("BBBB", f.read(4))
        self.normal.read(f)
        self.tex_coords     = Vector( struct.unpack("ff", f.read(8)) )
        self.unknown        = struct.unpack("ff", f.read(8))

    def write(self, f):
        f.write(struct.pack('fff', *self.pos))
        f.write(struct.pack('BBBB', *self.bone_weights))
        f.write(struct.pack('BBBB', *self.bone_indices))
        f.write(struct.pack('fff', *self.normal))
        f.write(struct.pack('ff', *self.tex_coords))

class M2Color:
    def __init__(self):
        self.color = M2Track()
        self.alpha = M2Track()
        self.size = 40
    def read(self, f):
        self.color.read(f,"C3Vector")
        
        self.alpha.read(f,"H")

    def write(self, f):
        self.color.write(f,"C3Vector")
        
        self.alpha.write(f,"H")

class M2Texture:
    def __init__(self):
        self.type     = 0
        self.flags    = 0
        self.filename = M2Array()
        self.size = 16

    def read(self, f):
        self.type   = struct.unpack("I", f.read(4))[0]
        self.flags  = struct.unpack("I", f.read(4))[0]
        self.filename.read(f)
        self.filename.fill(f, "c")

    def write(self, f):
        f.write(struct.pack('I', self.type))
        f.write(struct.pack('I', self.flags))
        
        self.filename.write(f)

class M2TextureWeight:
    def __init__(self):
        self.weight = M2Track()
        self.size = 20
    def read(self, f):
        self.weight.read(f, "H")

    def write(self, f):
        self.weight.write(f, "H")

class M2TextureTransform:
    def __init__(self):
        self.translation = M2Track()
        self.rotation    = M2Track()
        self.scaling     = M2Track()
        self.size = 60

    def read(self, f):
        self.translation.read(f,"C3Vector")
        self.rotation.read(f,"M2CompQuat")
        self.scaling.read(f,"C3Vector")

    def write(self, f):
        self.translation.write(f,"C3Vector")
        self.rotation.write(f,"M2CompQuat")
        self.scaling.write(f,"C3Vector")

class M2Material:
    def __init__(self):
        self.flags         = 0
        self.blending_mode = 0
        self.size = 4
    def read(self, f):
        self.type   = struct.unpack("H", f.read(2))[0]
        self.flags  = struct.unpack("H", f.read(2))[0]

    def write(self, f):
        f.write(struct.pack('H', self.type))
        f.write(struct.pack('H', self.flags))

class M2Attachment:
    def __init__(self):
        self.id               = 0
        self.bone             = 0
        self.unk              = 0
        self.position         = C3Vector( (0, 0, 0) )
        self.animate_attached = M2Track()
        self.size = 40

    def read(self, f):
        self.type   = struct.unpack("I", f.read(4))[0]
        self.bone  = struct.unpack("H", f.read(2))[0]
        self.unk  = struct.unpack("H", f.read(2))[0]
        self.position.read(f)
        self.animate_attached.read(f, "B")

    def write(self, f):
        f.write(struct.pack('I', self.type))
        f.write(struct.pack('H', self.bone))
        f.write(struct.pack('H', self.unk))
        self.position.write(f)
        self.animate_attached.write(f, "B")

class M2Event:
    def __init__(self):
        self.identifier = 0
        self.data       = 0
        self.bone       = 0
        self.position   = C3Vector( (0, 0, 0) )
        self.enabled    = M2TrackBase()
        self.size = 36

    def read(self, f):
        self.identifier   = struct.unpack("I", f.read(4))[0]
        self.data  = struct.unpack("I", f.read(4))[0]
        self.bone  = struct.unpack("I", f.read(4))[0]
        self.position.read(f)
        self.enabled.read(f)

    def write(self, f):
        f.write(struct.pack('I', self.identifier))
        f.write(struct.pack('I', self.data))
        f.write(struct.pack('I', self.bone))
        self.position.write(f)
        self.enabled.write(f)

class M2Light:
    def __init__(self):
        self.type              = 0
        self.bone              = 0
        self.position          = C3Vector( (0, 0, 0) )
        self.ambient_color     = M2Track()
        self.ambient_intensity = M2Track()
        self.diffuse_color     = M2Track()
        self.diffuse_intensity = M2Track()
        self.attenuation_start = M2Track()
        self.attenuation_end   = M2Track()
        self.visibility        = M2Track()
        self.size = 156

    def read(self, f):
        self.type   = struct.unpack("H", f.read(2))[0]
        self.bone  = struct.unpack("h", f.read(2))[0]
        self.position.read(f)
        self.ambient_color.read(f, "C3Vector")
        self.ambient_intensity.read(f, "f")
        self.diffuse_color.read(f, "C3Vector")
        self.diffuse_intensity.read(f, "f")
        self.attenuation_start.read(f, "f")
        self.attenuation_end.read(f, "f")
        self.visibility.read(f, "B")

    def write(self, f):
        f.write(struct.pack('H', self.type))
        f.write(struct.pack('h', self.bone))
        self.position.write(f)
        self.ambient_color.write(f, "C3Vector")
        self.ambient_intensity.write(f, "f")
        self.diffuse_color.write(f, "C3Vector")
        self.diffuse_intensity.write(f, "f")
        self.attenuation_start.write(f, "f")
        self.attenuation_end.write(f, "f")
        self.visibility.write(f, "B")

class M2Camera:
    def __init__(self):
        self.type                 = 0
        self.fov                  = 0
        self.far_clip             = 0
        self.near_clip            = 0
        self.positions            = M2Track()
        self.position_base        = C3Vector( (0, 0, 0) )
        self.target_position      = M2Track()
        self.target_position_base = C3Vector( (0, 0, 0) )
        self.roll                 = M2Track()
        self.size = 100

    def read(self, f):
        self.type   = struct.unpack("I", f.read(4))[0]
        self.fov  = struct.unpack("f", f.read(4))[0]
        self.far_clip = struct.unpack("f", f.read(4))[0]
        self.near_clip = struct.unpack("f", f.read(4))[0]
        self.positions.read(f, "M2SplineKeyVectors")
        self.position_base.read(f)
        self.target_position.read(f, "M2SplineKeyVectors")
        self.target_position_base.read(f)
        self.roll.read(f, "C3Vector")

    def write(self, f):
        f.write(struct.pack('I', self.type))
        f.write(struct.pack('f', self.fov))
        f.write(struct.pack('f', self.far_clip))
        f.write(struct.pack('f', self.near_clip))
        self.positions.write(f, "M2SplineKeyVectors")
        self.position_base.write(f)
        self.target_position.write(f, "M2SplineKeyVectors")
        self.target_position_base.write(f)
        self.roll.write(f, "C3Vector")

class M2Ribbon:
    def __init__(self):
        self.ribbonId          = 0
        self.boneIndex         = 0
        self.position          = C3Vector( (0, 0, 0) )
        self.texture_refs      = M2Array()
        self.blend_refs        = M2Array()
        self.color             = M2Track()
        self.opacity           = M2Track()
        self.height_above      = M2Track()
        self.height_below      = M2Track()
        self.edgesPerSec       = 0
        self.edgeLifeSpanInSec = 0
        self.gravity           = 0
        self.m_rows            = 0
        self.m_cols            = 0
        self.texSlotTrack      = M2Track()
        self.visibilityTrack   = M2Track()
        self.priorityPlane     = 0
        self.padding           = 0
        self.size = 176

    def read(self, f):
        self.ribbonId   = struct.unpack("I", f.read(4))[0]
        self.boneIndex   = struct.unpack("I", f.read(4))[0]
        self.position.read(f)
        
        self.texture_refs.read(f)
        self.texture_refs.fill(f, "H")
        self.blend_refs.read(f)
        self.blend_refs.fill(f, "H")
        
        self.color.read(f, "C3Vector")
        self.opacity.read(f, "H")
        self.height_above.read(f, "f")
        self.height_below.read(f, "f")
        
        self.edgesPerSec   = struct.unpack("f", f.read(4))[0]
        self.edgeLifeSpanInSec   = struct.unpack("f", f.read(4))[0]
        self.gravity   = struct.unpack("f", f.read(4))[0]
        self.m_rows   = struct.unpack("H", f.read(2))[0]
        self.m_cols   = struct.unpack("H", f.read(2))[0]
        
        self.texSlotTrack.read(f, "H")
        self.visibilityTrack.read(f, "B")
        
        self.priorityPlane   = struct.unpack("h", f.read(4))[0]
        self.padding   = struct.unpack("H", f.read(4))[0]
    def write(self, f):
        f.write(struct.pack('I', self.ribbonId))
        f.write(struct.pack('I', self.boneIndex))    

        self.position.write(f)
        
        self.texture_refs.write(f)
        #self.texture_refs.fill(f, "H")
        self.blend_refs.write(f)
        #self.blend_refs.fill(f, "H")
        
        self.color.write(f, "C3Vector")
        self.opacity.write(f, "H")
        self.height_above.write(f, "f")
        self.height_below.write(f, "f")       

        f.write(struct.pack('f', self.edgesPerSec))
        f.write(struct.pack('f', self.edgeLifeSpanInSec))   
        f.write(struct.pack('f', self.gravity))
        f.write(struct.pack('H', self.m_rows))   
        f.write(struct.pack('H', self.m_cols))
        
        self.texSlotTrack.write(f, "H")
        self.visibilityTrack.write(f, "B")
        
        f.write(struct.pack('h', self.priorityPlane))
        f.write(struct.pack('H', self.padding)) 
        
class M2Header:
    FORMAT = "<IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIffffffffffffffIIIIIIIIIIIIIIIIIIIIII"
    def __init__(self):
        self.magic                           = 0
        self.version                         = 0
        self.name                            = M2Array()
        self.globalFlags                     = 0
        self.global_loops                    = M2Array()
        self.sequences                       = M2Array()
        self.sequence_lookups                = M2Array()
        self.bones                           = M2Array()
        self.key_bone_lookup                 = M2Array()
        self.vertices                        = M2Array()
        self.num_skin_profiles               = 0
        self.colors                          = M2Array()
        self.textures                        = M2Array()
        self.texture_weights                 = M2Array()
        self.texture_transforms              = M2Array()
        self.replacable_texture_lookup       = M2Array()
        self.materials                       = M2Array()
        self.bone_lookup_table               = M2Array()
        self.texture_lookup_table            = M2Array()
        self.tex_unit_lookup_table           = M2Array()
        self.transparency_lookup_table       = M2Array()
        self.texture_transforms_lookup_table = M2Array()
        self.bounding_box                    = CAaBox()
        self.bounding_sphere_radius          = 0
        self.collision_box                   = CAaBox()
        self.collision_sphere_radius         = 0
        self.collision_triangles             = M2Array()
        self.collision_vertices              = M2Array()
        self.collision_normals               = M2Array()
        self.attachments                     = M2Array()
        self.attachment_lookup_table         = M2Array()
        self.events                          = M2Array()
        self.lights                          = M2Array()
        self.cameras                         = M2Array()
        self.camera_lookup_table             = M2Array()
        self.ribbon_emitters                 = M2Array()
        self.particle_emitters               = M2Array()
        self.blend_map_overrides             = M2Array()


    def read(self, f):
        self.magic = struct.unpack("I", f.read(4))[0]
        self.version = struct.unpack("I", f.read(4))[0]
        
        self.name.read(f)
        self.name.fill(f, "c")
        print("Name")
        
        self.globalFlags = struct.unpack("I", f.read(4))[0]
        print("Flags")

        self.global_loops.read(f)
        self.global_loops.fill(f, "I")
        
        self.sequences.read(f)
        self.sequences.fill(f, "M2Sequence")
        print("Seq")
        
        self.sequence_lookups.read(f)
        self.sequence_lookups.fill(f, "H")
        
        self.bones.read(f)
        self.bones.fill(f, "M2CompBone")
        
        self.key_bone_lookup.read(f)
        self.key_bone_lookup.fill(f, "H")
        
        self.vertices.read(f)
        self.vertices.fill(f, "M2Vertex")
        
        self.num_skin_profiles = struct.unpack("I", f.read(4))[0]
        
        self.colors.read(f)
        self.colors.fill(f, "M2Color")
        print("Color")
        
        self.textures.read(f)
        self.textures.fill(f, "M2Texture")
        
        self.texture_weights.read(f)
        self.texture_weights.fill(f, "M2TextureWeight")
        
        self.texture_transforms.read(f)
        self.texture_transforms.fill(f, "M2TextureTransform")
        
        self.replacable_texture_lookup.read(f)
        self.replacable_texture_lookup.fill(f, "H")
        
        self.materials.read(f)
        self.materials.fill(f, "M2Material")
        
        self.bone_lookup_table.read(f)
        self.bone_lookup_table.fill(f, "H")
        
        self.texture_lookup_table.read(f)
        self.texture_lookup_table.fill(f, "H")
        
        self.tex_unit_lookup_table.read(f)
        self.tex_unit_lookup_table.fill(f, "H")
        
        self.transparency_lookup_table.read(f)
        self.transparency_lookup_table.fill(f, "H")
        
        self.texture_transforms_lookup_table.read(f)
        self.texture_transforms_lookup_table.fill(f, "H")
        
        self.bounding_box.read(f)
        self.bounding_sphere_radius = struct.unpack("f", f.read(4))[0]
        self.collision_box.read(f)
        self.collision_sphere_radius = struct.unpack("f", f.read(4))[0]
        
        self.collision_triangles.read(f)
        self.collision_triangles.fill(f, "H")
        
        self.collision_vertices.read(f)
        self.collision_vertices.fill(f, "C3Vector")
        
        self.collision_normals.read(f)
        self.collision_normals.fill(f, "C3Vector")
        
        self.attachments.read(f)
        self.attachments.fill(f, "M2Attachment")
        
        self.attachment_lookup_table.read(f)
        self.attachment_lookup_table.fill(f, "H")
        
        self.events.read(f)
        self.events.fill(f, "M2Event")
        
        self.lights.read(f)
        self.lights.fill(f, "M2Light")
        print("Light")
        
        self.cameras.read(f)
        self.cameras.fill(f, "M2Camera")
        
        self.camera_lookup_table.read(f)
        self.camera_lookup_table.fill(f, "H")
        
        self.ribbon_emitters.read(f)
        self.ribbon_emitters.fill(f, "M2Ribbon")
        
        self.particle_emitters.read(f)
        #self.particle_emitters.fill(f, "M2Particle")
        
        #self.blend_map_overrides.read(f)
        #self.blend_map_overrides.fill(f, "H")
    def write(self, f):
        f.write(struct.pack('fff', *self.position))
        f.write(struct.pack('BBBB', *self.bone_weights))
        f.write(struct.pack('BBBB', *self.bone_indices))
        f.write(struct.pack('fff', *self.normal))
        f.write(struct.pack('ff', *self.texture_coords))

class M2Property(list):
    def __init__(self):
        super().__init__()
        self.append(0);
        self.append(0);
        self.append(0);
        self.append(0);

    def read(self,f):
        self[0] = struct.unpack("B", f.read(1))[0]
        self[1] = struct.unpack("B", f.read(1))[0]
        self[2] = struct.unpack("B", f.read(1))[0]
        self[3] = struct.unpack("B", f.read(1))[0]

    def write(self, f):
        f.write(struct.pack("B",self[0]))
        f.write(struct.pack("B",self[1]))
        f.write(struct.pack("B",self[2]))
        f.write(struct.pack("B",self[3]))

class M2Triangle(list):
    def __init__(self):
        super().__init__()
        self.append(0);
        self.append(0);
        self.append(0);

    def read(self,f):
        self[0] = struct.unpack("H", f.read(2))[0]
        self[1] = struct.unpack("H", f.read(2))[0]
        self[2] = struct.unpack("H", f.read(2))[0]

    def write(self, f):
        f.write(struct.pack("H",self[0]))
        f.write(struct.pack("H",self[1]))
        f.write(struct.pack("H",self[2]))
        
    def to_tuple(self, offset=0):
        return (self[0] - offset, self[1] - offset, self[2] - offset) 
        
class M2SkinSection:
    def __init__(self):
        self.SubmeshID         = 0
        self.Level             = 0
        self.StartVertex       = 0
        self.nVertices         = 0
        self.StartTriangle     = 0
        self.nTriangles        = 0
        self.nBones            = 0
        self.StartBones        = 0
        self.boneInfluences    = 0
        self.RootBone          = 0
        self.CenterMass        = C3Vector( (0, 0, 0) )
        self.CenterBoundingBox = C3Vector( (0, 0, 0) )
        self.Radius            = 0
        
    def read(self, f):
        self.SubmeshID   = struct.unpack("H", f.read(2))[0]
        self.Level   = struct.unpack("H", f.read(2))[0]
        self.StartVertex   = struct.unpack("H", f.read(2))[0]
        self.nVertices   = struct.unpack("H", f.read(2))[0]
        self.StartTriangle   = struct.unpack("H", f.read(2))[0] // 3
        self.nTriangles   = struct.unpack("H", f.read(2))[0] // 3
        self.nBones   = struct.unpack("H", f.read(2))[0]
        self.StartBones   = struct.unpack("H", f.read(2))[0]
        self.boneInfluences   = struct.unpack("H", f.read(2))[0]
        self.RootBone   = struct.unpack("H", f.read(2))[0]
        self.CenterMass.read(f)
        self.CenterBoundingBox.read(f)
        self.Radius   = struct.unpack("f", f.read(4))[0]

    def write(self, f):
        f.write(struct.pack("H",self.SubmeshID))
        f.write(struct.pack("H",self.Level))
        f.write(struct.pack("H",self.StartVertex))
        f.write(struct.pack("H",self.nVertices))
        f.write(struct.pack("H",self.StartTriangle))
        f.write(struct.pack("H",self.nTriangles))
        f.write(struct.pack("H",self.nBones))
        f.write(struct.pack("H",self.StartBones))
        f.write(struct.pack("H",self.boneInfluences))
        f.write(struct.pack("H",self.RootBone))
        self.CenterMass.write(f)
        self.CenterBoundingBox.write(f)
        f.write(struct.pack("f",self.Radius))
        

class M2Batch:
    def __init__(self):
        self.flags            = 0
        self.shader_id        = 0
        self.submesh_index    = 0
        self.submesh_index2   = 0
        self.color_index      = 0
        self.render_flags     = 0
        self.layer            = 0
        self.op_count         = 0
        self.texture          = 0
        self.tex_unit_number2 = 0
        self.transparency     = 0
        self.texture_anim     = 0
      
    def read(self, f):
        self.flags   = struct.unpack("H", f.read(2))[0]
        self.shader_id   = struct.unpack("H", f.read(2))[0]
        self.submesh_index   = struct.unpack("H", f.read(2))[0]
        self.submesh_index2   = struct.unpack("H", f.read(2))[0]
        self.color_index   = struct.unpack("h", f.read(2))[0]
        self.render_flags   = struct.unpack("H", f.read(2))[0]
        self.layer   = struct.unpack("H", f.read(2))[0]
        self.op_count   = struct.unpack("H", f.read(2))[0]
        self.texture   = struct.unpack("H", f.read(2))[0]
        self.tex_unit_number2   = struct.unpack("H", f.read(2))[0]
        self.transparency   = struct.unpack("H", f.read(2))[0]
        self.texture_anim   = struct.unpack("H", f.read(2))[0]

    def write(self, f):
        f.write(struct.pack("H",self.flags))
        f.write(struct.pack("H",self.shader_id))
        f.write(struct.pack("H",self.submesh_index))
        f.write(struct.pack("H",self.submesh_index2))
        f.write(struct.pack("h",self.color_index))
        f.write(struct.pack("H",self.render_flags))
        f.write(struct.pack("H",self.layer))
        f.write(struct.pack("H",self.op_count))
        f.write(struct.pack("H",self.texture))
        f.write(struct.pack("H",self.tex_unit_number2))
        f.write(struct.pack("H",self.transparency))
        f.write(struct.pack("H",self.texture_anim))
        
class M2SkinProfile:
    def __init__(self):
        self.magic         = 0
        self.indices       = M2Array()
        self.triangles     = M2Array()
        self.properties    = M2Array()
        self.submeshes     = M2Array()
        self.texture_units = M2Array()
        self.bones         = 0
        
    def read(self, f):
        self.magic   = struct.unpack("I", f.read(4))[0]
        
        self.indices.read(f)
        self.indices.fill(f, "H")
        
        self.triangles.read(f)
        self.triangles.number = self.triangles.number // 3
        self.triangles.fill(f, "M2Triangle")
        
        self.properties.read(f)
        self.properties.fill(f, "M2Property")
        
        self.submeshes.read(f)
        self.submeshes.fill(f, "M2SkinSection")
        
        self.texture_units.read(f)
        self.texture_units.fill(f, "M2Batch")
        
        self.bones   = struct.unpack("I", f.read(4))[0]

    def write(self, f):
        f.write(struct.pack("I",self.magic))
        self.triangles.write(f)
        #self.triangles.fill(f, "M2Triangle")
        
        self.properties.write(f)
        #self.properties.fill(f, "M2Property")
        
        self.submeshes.write(f)
        #self.submeshes.fill(f, "M2SkinSection")
        
        self.texture_units.write(f)
        #self.texture_units.fill(f, "M2Batch")
        f.write(struct.pack("I",self.bones))