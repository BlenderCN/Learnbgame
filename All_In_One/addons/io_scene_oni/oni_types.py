import os, re, sys, bpy, math
from io_scene_oni.oni_files import ONI_FILES, BODYPARTS
from io_scene_oni.oni_utils import (
        Object,
        readString,
        readInt,
        readInt8,
        readCString,
        readField,
        readFields,
        readArray,
        readBytes,
        readShort,
        readUShort,
        readFloat
    )
from mathutils import Vector, Euler

class Oni:
    def __init__(self, gdf):
        self.gdf = gdf
        self.files = []
        self.lfiles = {}

        pattern = r"""level([0-9]+)_(Final|Tools).dat"""        
        for fname in os.listdir(self.gdf): 
            if not fname.endswith('.dat'):
                continue

            match = re.search(pattern, fname)
            if match is None:
                continue

            level = int(match.group(1))
            ftype = match.group(2)

            if ftype != 'Final':
                continue

            oif = OniInstanceFile(self, fname, level)
            self.files.append(oif)
            self.lfiles[level] = oif

        self.files = sorted(self.files, key=lambda f: f.level)

    def findOniDescriptor(self, desc):
        for f in self.files:
            descs = f.find(desc.tag, desc.name)
            for d in descs:
                if not d.isEmpty():
                    return d
        return None


class OniInstanceFile: 
    def __init__(self, oni, fname, level):
        self.oni = oni   
        self.fname = fname
        self.rawfname = fname[0:-3]+'raw'
        self.level = level
        self.file = open(self.oni.gdf + '/' + self.fname, 'rb')
        self.rawfile = False

        try:
            self.checksum = readBytes(self.file, 8)
            self.version = readString(self.file, 4)
            self.signature = readBytes(self.file, 8)
            self.instance_desc_count = readInt(self.file)
            self.name_desc_count = readInt(self.file)
            self.template_desc_count = readInt(self.file)
            self.data_table_offset = readInt(self.file)
            self.data_table_size = readInt(self.file)
            self.name_table_offset = readInt(self.file)
            self.name_table_size = readInt(self.file)
            self.file.seek(16, 1)   
            self.inst_descs = self.readInstanceDescriptors() 

        finally: 
            self.file.close() 

    def ensureOpen(self):
        if self.file.closed:
            self.file = open(self.oni.gdf + '/' + self.fname, 'rb')
            return False
        else:
            return True

    def ensureRawOpen(self):
        if not self.rawfile or self.rawfile.closed:
            self.rawfile = open(self.oni.gdf + '/' + self.rawfname, 'rb')
            return False
        else:
            return True
    
    def readInstanceDescriptors(self):
        descs = []
        for i in range(self.instance_desc_count):
            descs.append(OniInstanceDesc(self))
        return descs

    def getByPointer(self, pointer):
        return self.inst_descs[(pointer - 1) >> 8]

    def find(self, tag, name=None):

        if tag is None:
            if name is None:
                return None
            else:
                descs = []
                for d in self.inst_descs:
                    if name in d.name:
                        descs.append(d)
                return descs
        else:   
            if not hasattr(self, 'tagmap'):
                self.tagmap = {}
                for d in self.inst_descs:
                    if not d.tag in self.tagmap:
                        self.tagmap[d.tag] = []
                    self.tagmap[d.tag].append(d)

            if name is None:
                return self.tagmap[tag]
            else:
                descs = []
                for d in self.tagmap[tag]:
                    if name in d.name:
                        descs.append(d)
                return descs

    def findByName(self, tag, name=None):
        if not hasattr(self, 'tagmap'):
            self.tagmap = {}
            for d in self.inst_descs:
                if not d.tag in self.tagmap:
                    self.tagmap[d.tag] = []
                self.tagmap[d.tag].append(d)
        if name is None:
            return self.tagmap[tag]
        else:
            descs = []
            for d in self.tagmap[tag]:
                if name in d.name:
                    descs.append(d)
            return descs

    def printM3GM(self):
        for d in self.inst_descs:
            if d.tag == 'M3GM' and d.isNamed():
                if d.name == 'M3GMjet':
                    d.getData()
                    d.print()
                    d.data.draw()


class OniInstanceDesc:
    def __init__(self, oif):
        self.oif = oif
        f = oif.file
        self.tag = readString(f, 4)
        self.data_offset = readInt(f)
        self.name_offset = readInt(f)
        self.data_size = readInt(f)
        self.flags = readInt(f)
        self.data = None

        #if self.flags & 0x01:
        #    self.name = 'unnamed'
        #else:
        pos = f.tell()
        f.seek(oif.name_table_offset + self.name_offset)
        self.name = readCString(f)
        #print(self.tag + ' - ' + self.name)
        f.seek(pos)

    def isNamed(self):
        return not(self.flags & 0x01)

    def isEmpty(self):
        return self.flags & 0x02

    def isShared(self):
        return self.flags & 0x08

    def getData(self):
        if self.data is None:
            desc = self
            if self.isEmpty():
                print('searching desc...')
                desc  = self.oif.oni.findOniDescriptor(self)
                if desc is None:
                    print("Descriptor data wasn't found!") 
                    self.print()

            this_module = sys.modules[__name__]
            if hasattr(this_module, self.tag):
                inst_class = getattr(this_module, self.tag)
                self.data = inst_class(desc)
            else:
                self.data = OniInstance(desc)
        return self.data

    def print(self):
        fields = ONI_FILES[self.tag]
        print('name = ' + self.name)
        print('tag = ' + self.tag)
        print('data_offset = ' + str(self.data_offset))
        print('name_offset = ' + str(self.name_offset))
        print('data_size = ' + str(self.data_size))
        print('flags = ' + str(self.flags))

        if self.data is None:
            print("data wasn't read")
        else:
            dir(self.data)
            self.data.print()

class OniInstance:
    def __init__(self, oid):
        self.oid = oid
        wasOpen = self.oid.oif.ensureOpen()
        f = self.oid.oif.file

        try:
            pos = f.tell()
            offset =  self.oid.oif.data_table_offset + self.oid.data_offset

            f.seek(offset - 8)
            setattr(self, 'res_id', readInt(f))
            setattr(self, 'lev_id', readInt(f))

            fields = ONI_FILES[self.oid.tag]['fields']
            readFields(f, self, fields)
            f.seek(pos)
        finally:
            if not wasOpen:
                f.close()

    def print(self):
        fields = ONI_FILES[self.oid.tag]['fields']
        print('res_id = ' + str(self.res_id))
        print('lev_id = ' + str(self.lev_id))
        for x in fields:
            value = getattr(self, x[0])
            if x[0][0:5] == 'link_' and value & 0x01:
                value = str(value) + ' = n_' + str((value - 1) >> 8)
            print(x[0] + ' = ' + str(value))

class M3GM(OniInstance):
    def draw(self, pos=None):
        oif = self.oid.oif
        xyz = oif.getByPointer(self.link_xyz)
        tstrip = oif.getByPointer(self.link_tstrip)
        fnorm = oif.getByPointer(self.link_fnorm)
        fgrouping = oif.getByPointer(self.link_fgrouping)
        #txmp = self.oid.oif.getByPointer(self.link_texture)
        #txmp.print()

        wasOpen = oif.ensureOpen()
        f = oif.file
        try:
            coords=[]
            for p in xyz.getData().points:
                coords.append(tuple(p))

            fnorms = fnorm.getData().vectors_coords
            fgroups = fgrouping.getData()
            tstrips = tstrip.getData()
             
            faces = self.calcFaces(coords, tstrips.strips, fnorms, fgroups.strips)
            return self.drawObject(self.oid.name, coords, faces, pos)
            
        finally:
            if not wasOpen:
                f.close()

    def drawObject(self, name, points, faces, pos=None):
        me = bpy.data.meshes.new('mesh'+name)
        ob = bpy.data.objects.new(name, me)    

        if pos is None:
            ob.location = bpy.context.scene.cursor_location  
        else:
            ob.location = Vector(pos)
        bpy.context.scene.objects.link(ob)  

        me.from_pydata(points, [], faces) 
        me.update(calc_edges=True)   

        return ob

    # points represent triangle strips
    # high bit in indexes indicates new strip
    def calcFaces(self, points, points_indexes, faces_normals, faces_indexes):
        faces=[]
        for i in range(len(points_indexes)):
            point_index = points_indexes[i]
            
            # new triangles strip, if high bit is set 
            if point_index < 0:                  
                point_index = point_index & 0x0FFFFFFF
                face = ()

            face += (point_index,)

            # if triangle is ready
            if len(face) == 3:                    
                face_index = faces_indexes[len(faces)]
                face_points = [points[idx] for idx in face]
                solved_face = self.calcFaceByNormal(face_points, faces_normals[face_index], face)
                faces.append(solved_face)

                # continue strip
                face = face[1:]

        return faces

    # calculates right order of points for Backface Culling
    def calcFaceByNormal(self, points, normal, face):
        a = [ t - u for t,u in zip(points[1], points[0])]   # vector a = point[1] - point[0]
        b = [ t - u for t,u in zip(points[2], points[0])]   # vector b = point[2] - point[0]
        # normal = a x b = (a2b3-a3b2)i-(a1b3-a3b1)j+(a1b2-a2b1)k.
        myNormal = Vector([a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0]])
        angle = myNormal.angle(Vector(normal))

        # if vectors are in opposite direction change points order
        if angle > math.pi/2 or angle < -math.pi/2:
            return (face[1], face[0], face[2])
        return face


class TRCM(OniInstance):

    def draw(self):
        wasOpen = self.oid.oif.ensureOpen()
        f = self.oid.oif.file
        try:
            scene = bpy.context.scene        
            lf = self.oid.oif

            trga = lf.getByPointer(self.link_TRGA)
            trga.getData()
            #trga.print()    
            trta = lf.getByPointer(self.link_TRTA)
            trta.getData()
            #trta.print()    
            tria = lf.getByPointer(self.link_TRIA)
            tria.getData()
            #tria.print()



            armdata = bpy.data.armatures.new('arm_konoko')
            ob_new = bpy.data.objects.new('konoko', armdata)
            bpy.context.scene.objects.link(ob_new)
            self.object = ob_new

            for i in bpy.context.scene.objects:
                    i.select = False #deselect all objects
            ob_new.select = True
            bpy.context.scene.objects.active = ob_new

            pos = []
            self.bodyparts = []
            self.bones = []
            for i in range(tria.data.size):
                link = trga.data.links_M3GM[i]
                m3gm = lf.getByPointer(link)
                if not m3gm.isNamed():
                    m3gm.name = BODYPARTS[i]
                offset = trta.data.bones_offsets[i]
                bone_info = tria.data.bones[i]

                if bone_info.parent == i:
                    pos.append(offset)
                else:
                    pos.append([(x + y) for x, y in zip(pos[bone_info.parent], offset)])
                    # pos.append(offset)

                obj = m3gm.getData().draw(pos[i])#
                self.bodyparts.append(obj)

                bone = self.drawBone(ob_new, BODYPARTS[i], pos[i])

                #print(m3gm.name)
                if  bone_info.parent != i:
                    bone.parent = ob_new.data.edit_bones[bone_info.parent]     

                bpy.ops.object.mode_set(mode='OBJECT')
                self.bones.append(ob_new.data.bones[i])
                obj.parent = ob_new
                obj.parent_bone = bone.name
                obj.parent_type = 'BONE'

                #bpy.ops.object.parent_set()


        finally:
            if not wasOpen:
                f.close()

    def drawBone(self, ob_new, name, pos):
        bpy.ops.object.mode_set(mode='EDIT')
        newbone = ob_new.data.edit_bones.new('bone_'+name)
        newbone.head = Vector(pos)
        newbone.tail = newbone.head + Vector((1,0,0))
        newbone.use_relative_parent = True
        #bpy.ops.object.mode_set(mode='OBJECT')
        return newbone

class ONCC(OniInstance):  
    def importModel(self):
        lf = self.oid.oif
        trbs = lf.getByPointer(self.link_TRBS)
        trbs.getData()
        #trbs.print()
        
        link = trbs.data.links_TRCM[4]
        #for link in trbs.data.links_TRCM:
        trcm = lf.getByPointer(link)
        trcm.getData()
        #trcm.print()

        trcm.data.draw()
        self.object = trcm.data.object
        self.bodyparts = trcm.data.bodyparts
        self.bones = trcm.data.bones

    def importAnimations(self): 
        lf = self.oid.oif       
        trac = lf.getByPointer(self.link_TRAC)
        trac.getData()
        #trac.print()


        for i in bpy.context.scene.objects:
                i.select = False #deselect all objects
        bpy.context.scene.objects.active = None
    
        for anim in trac.data.anims:
            #anim = trac.data.anims[1]
            tram = lf.getByPointer(anim.link_TRAM)
            if tram.name != 'TRAMKONCOMrun_throw_fw': continue
            print(str(anim.weight) + ' - ' + tram.name + ':')
            tram.getData()
            #tram.print()

            tram.data.readBodyparts()
            tram.data.readPos()
            #print('bodyparts:')
            #print(tram.data.bodyparts)

            self.object.location = Vector(tram.data.pos)
            
            bpy.context.scene.frame_start = 0
            bpy.context.scene.frame_end = tram.data.frames_num - 1


            keyInterp = bpy.context.user_preferences.edit.keyframe_new_interpolation_type
            bpy.context.user_preferences.edit.keyframe_new_interpolation_type ='LINEAR'

            #self.object.animation_data_create()
            #self.object.animation_data.action = bpy.data.actions.new(name=tram.name)

            g = 3.1416/180

            rotate = bpy.ops.transform.rotate
            for i in range(tram.data.bodyparts_num):
                #if i > 0: continue
                #bone = self.bones[i]
                bone = self.object.pose.bones[i]
                bpart = self.bodyparts[i]
                print(bpart)
                print(bone)
                #bpart.select = True

                #bpy.context.scene.objects.active = bpart
                trambp = tram.data.bodyparts[i]

                #obj = bpy.context.object
                #print(obj)

                #bone.animation_data_create()
                #bone.animation_data.action = bpy.data.actions.new(name=tram.name+"_"+BODYPARTS[i])

                angles_sum = [0,0,0]
                frameN = 0
                for frame in trambp.frames:
                    frameN += frame.frames_num
                    bpy.context.scene.frame_set(frameN)

                    angles = [math.radians(a) for a in frame.angles]
                    angles_delta = [self.getNearestAngle(a, b) for a,b in zip(angles_sum, angles)]
                    angles_sum = [a+b for a,b in zip(angles_sum, angles_delta)]

                    mode = 'ZYX'
                    euler = Euler(angles_sum, mode)
                    #bone.matrix = euler.to_matrix().to_4x4()
                    bone.rotation_mode = mode
                    bone.rotation_euler = euler
                    bone.keyframe_insert(data_path='rotation_euler')

                    #bone.rotation_mode = 'QUATERNION'
                    #bone.rotation_quaternion = euler.to_quaternion()
                    #bone.matrix = euler.to_quaternion().to_matrix().to_4x4()
                    #bone.keyframe_insert(data_path='rotation_quaternion')
                    #if i == 0:
                    #    print(frameN)
                    #    print(str(frame.angles) + ' - ' + str(bone.rotation_euler))

                #bpart.select = False

            bpy.context.user_preferences.edit.keyframe_new_interpolation_type = keyInterp
        
    def getNearestAngle(self, a, b):
        pi2 = 2*3.1416
        while a > pi2: a -= pi2
        while a < -pi2: a += pi2
        c = b - a
        if c > 3.1416:
            return c - 2*3.1416
        elif c < -3.1416:
            return c + 2*3.1416
        else:
            return c

class TRAM(OniInstance):
    def readPos(self):
        wasOpen = self.oid.oif.ensureRawOpen()
        f = self.oid.oif.rawfile
        try:
            f.seek(self.offset_y)
            y = readFloat(f)

            f.seek(self.offset_xz)
            x = readFloat(f)
            z = readFloat(f)
            setattr(self, 'pos', [x, y, z])
        finally:
            if not wasOpen:
                f.close()

    def readBodyparts(self):
        wasOpen = self.oid.oif.ensureRawOpen()
        f = self.oid.oif.rawfile
        #print(f)
        try:
            f.seek(self.offset_bodyparts)
            bodyparts = []

            print(self.frames_num)
            print(self.compression_size)
            print(self.offset_bodyparts)

            for i in range(self.bodyparts_num):
                bodypart = Object()
                bodypart.start_pos = readShort(f)
                #print(str(i) + ' - ' + str(bodypart.start_pos))
                bodypart.frames = []
                bodyparts.append(bodypart)

            for i in range(self.bodyparts_num):
                #print(BODYPARTS[i])
                bodypart = bodyparts[i]
                f.seek(self.offset_bodyparts + bodypart.start_pos)
                fcount = 0
                bodypart.frames.append(self.readKeyFrame(f, self.compression_size, True))
                while fcount < self.frames_num - 1:
                    kf = self.readKeyFrame(f, self.compression_size, False)
                    bodypart.frames.append(kf)
                    fcount += kf.frames_num
                #print('fcount = ' + str(fcount))

            setattr(self, 'bodyparts', bodyparts)

        finally:
            if not wasOpen:
                f.close()

    def readKeyFrame(self, f, cs, start):
        kf = Object()
        kf.frames_num = 0
        kf.angles = []
        if not start:
            kf.frames_num = readInt8(f)

        if cs == 6:
            for i in range(3):
                kf.angles.append(readShort(f) * 0.0054932) 
        elif cs == 16:
            for i in range(4):
                kf.angles.append(readFloat(f))


        #print(kf.frames_num)
        #print(kf.angles)
        return kf
