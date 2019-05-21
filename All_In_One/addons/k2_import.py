#!BPY

""" Registration info for Blender menus:
Name: 'K2/HON (.model/.clip)...'
Blender: 257
Group: 'Import'
Tip: 'Import a Heroes of Newerth model file'
"""

bl_info = {
    "name": "HoN Model Importer",
    "description": "Import a model from Heroes of Newerth into Blender.",
    "author": "Anton Romanov, Nathan Mitchell",
    "version": (2,0),
    "blender": (2, 5, 7),
    "api": 31236,
    "location": "File -> Import",
    "warning": '', # used for warning icon and text in addons panel
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"\
        "Scripts/My_Script",
    "tracker_url": "http://projects.blender.org/tracker/index.php?"\
        "func=detail&aid=<number>",
    "category": "Learnbgame"
}


__author__ = "Anton Romanov"
__version__ = "2010.03.24"

__bpydoc__ = """\
"""

# Copyright (c) 2010 Anton Romanov
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import bpy
import os
import struct, chunk
from mathutils import *
import math
# determines the verbosity of loggin.
#   0 - no logging (fatal errors are still printed)
#   1 - standard logging
#   2 - verbose logging
#   3 - debug level. really boring (stuff like vertex data and verbatim lines)
IMPORT_LOG_LEVEL = 3

def roundVector(vec,dec=17):
        fvec=[]
        for v in vec:
                fvec.append(round(v,dec))
        return Vector(fvec)
def roundMatrix(mat,dec=17):
        fmat = []
        for row in mat:
                fmat.append(roundVector(row,dec))
        return Matrix(fmat)
       

def read_int(honchunk):
        return struct.unpack("<i",honchunk.read(4))[0]
def read_float(honchunk):
        return struct.unpack("<f",honchunk.read(4))[0]


        
############################## 
#CLIPS
##############################
        
MKEY_X,MKEY_Y,MKEY_Z,\
MKEY_PITCH,MKEY_ROLL,MKEY_YAW,\
MKEY_VISIBILITY,\
MKEY_SCALE_X,MKEY_SCALE_Y,MKEY_SCALE_Z \
        = range(10)


def bone_depth(bone):
        if not bone.parent:
                return 0
        else:
                return 1+bone_depth(bone.parent)
                

def GenerateFrameMotions( motions, numframes, version ):
        frames = []
        for frame in range( numframes ):
                frameMotion = {}
                for bone, motion in motions.items():
                        #translation
                        if frame >= len(motion[MKEY_X]):
                                x = motion[MKEY_X][-1]
                        else:
                                x = motion[MKEY_X][frame]
                                
                        if frame >= len(motion[MKEY_Y]):
                                y = motion[MKEY_Y][-1]
                        else:
                                y = motion[MKEY_Y][frame]
        
                        if frame >= len(motion[MKEY_Z]):
                                z = motion[MKEY_Z][-1]
                        else:
                                z = motion[MKEY_Z][frame]
                                
                        position = [ x, y, z ]

                        #rotation
                        if frame >= len(motion[MKEY_PITCH]):
                                rx = motion[MKEY_PITCH][-1]
                        else:
                                rx = motion[MKEY_PITCH][frame]
        
                        if frame >= len(motion[MKEY_ROLL]):
                                ry = motion[MKEY_ROLL][-1]
                        else:
                                ry = motion[MKEY_ROLL][frame]

                        if frame >= len(motion[MKEY_YAW]):
                                rz = motion[MKEY_YAW][-1]
                        else:
                                rz = motion[MKEY_YAW][frame]
                
                        rotation = [ rx, ry, rz ]

                        #scaling
                        if version == 1:
                                if frame >= len(motion[MKEY_SCALE_X]):
                                        sx = motion[MKEY_SCALE_X][-1]
                                else:
                                        sx = motion[MKEY_SCALE_X][frame]
                                sy = sz = sx
                        else:
                                if frame >= len(motion[MKEY_SCALE_X]):
                                        sx = motion[MKEY_SCALE_X][-1]
                                else:
                                        sx = motion[MKEY_SCALE_X][frame]
                
                                if frame >= len(motion[MKEY_SCALE_Y]):
                                        sy = motion[MKEY_SCALE_Y][-1]
                                else:
                                        sy = motion[MKEY_SCALE_Y][frame]

                                if frame >= len(motion[MKEY_SCALE_Z]):
                                        sz = motion[MKEY_SCALE_Z][-1]
                                else:
                                        sz = motion[MKEY_SCALE_Z][frame]
                        
                        scale = [sx,sy,sz]
                        
                        #visibility
                        
                        if frame >= len(motion[MKEY_VISIBILITY]):
                                v = motion[MKEY_VISIBILITY][-1]
                        else:
                                v = motion[MKEY_VISIBILITY][frame]

                        visibility = v

                        frameMotion[bone] = [position, rotation, scale, visibility]

                frames.append( frameMotion )

        return frames

def GenerateMotionMatrix( location, rotation, scale ):
        euler = Euler()
        euler.order = 'ZXY'
        euler.z = math.radians(rotation[2])
        euler.x = math.radians(rotation[0])
        euler.y = math.radians(rotation[1])
        
        bone_rotation_matrix = euler.to_matrix()
        bone_rotation_matrix.resize_4x4()
        bone_rotation_matrix *= Matrix.Translation( Vector(location) )

        return bone_rotation_matrix,scale

                
############
#common
###############################



from bpy.props import *
import os.path
import os


from bpy.props import *
 

# Invoke the dialog when loading
 
#
#    Panel in tools region
#

ModelPath = '/home/nathan/blender/high.model'
ClipsPath = '/home/nathan/blender/clips'
RemoveDoubles = True
FlipUV = True

class HoNImporter(bpy.types.Operator):
        '''Load HoN model'''
        bl_idname = "import.hon_model"
        bl_label = "Import HoN Model"

        modelpath = StringProperty(name="Model Path", description="Filepath used for importing the HoN model file", maxlen=1024, default="", subtype='FILE_PATH')
        clipspath = StringProperty(name="Clips Path", description="Filepath used for importing the HoN model file", maxlen=1024, default="", subtype='FILE_PATH')
        removedoubles = BoolProperty(name="Remove Double Vertices", description="Remove all the double vertices", default=True )
        flipuv = BoolProperty(name="Flip UV Coords", description="Flip UV coords over Y-axis to line up with native HoN textures" ) 

        def execute(self, context):

                for o in bpy.data.objects:
                        o.select = False
                
                #convert the filename to an object name
                objName = bpy.path.display_name(self.modelpath.split("\\")[-1].split("/")[-1])
                obj, rig = self.CreateBlenderMesh(self.modelpath, objName, context)
                if self.clipspath:
                        clips = [f for f in  os.listdir(self.clipspath) if f.endswith('.clip')]
                        self.log( clips )
                        for clip in clips:
                                if clip:
                                        self.CreateBlenderClip(os.path.join(self.clipspath,clip), obj, rig)
                                        

                return {'FINISHED'}

        def invoke(self, context, event):
                global ModelPath, ClipsPath, RemoveDoubles, FlipUV
                self.modelpath = ModelPath
                self.clipspath = ClipsPath
                self.removedoubles = RemoveDoubles
                self.flipuv = FlipUV

                return context.window_manager.invoke_props_dialog(self)


        def log(self, msg):
                if IMPORT_LOG_LEVEL >= 1:
                        self.report({'WARNING'}, str(msg))
                
        def vlog(self, msg):
                if IMPORT_LOG_LEVEL >= 2:
                        self.report({'INFO'}, str(msg))
                
        def dlog(self, msg):
                if IMPORT_LOG_LEVEL >= 3:
                        self.report({'DEBUG'}, str(msg))
        
        def err(self, msg):
                self.report({'ERROR'}, str(msg))


        def CreateBlenderMesh(self, filename, objname, context):
                file = open(filename,'rb')
                if not file:
                        self.log("can't open file")
                        return
                sig = file.read(4)
                if sig != b'SMDL':
                        self.err('unknown file signature')
                        return

                try:
                        honchunk = chunk.Chunk(file,bigendian=0,align=0)
                except EOFError:
                        self.log('error reading first chunk')
                        return
                if honchunk.getname() != b'head':
                        self.log('file does not start with head chunk!')
                        return
                version = read_int(honchunk)
                num_meshes = read_int(honchunk)
                num_sprites = read_int(honchunk)
                num_surfs = read_int(honchunk)
                num_bones = read_int(honchunk)

                self.vlog("Version %d" % version)
                self.vlog("%d mesh(es)" % num_meshes)
                self.vlog("%d sprites(es)" % num_sprites)
                self.vlog("%d surfs(es)" % num_surfs)
                self.vlog("%d bones(es)" % num_bones)
                self.vlog("bounding box: (%f,%f,%f) - (%f,%f,%f)" % \
                        struct.unpack("<ffffff", honchunk.read(24)))
                honchunk.skip()

                scn= bpy.context.scene

                try:
                        honchunk = chunk.Chunk(file,bigendian=0,align=0)
                except EOFError:
                        self.log('error reading bone chunk')
                        return


                #read bones

                #create armature object
                armature_data = bpy.data.armatures.new('%s_Armature' % objname)
                armature_data.show_names = True
                rig = bpy.data.objects.new('%s_Rig' % objname, armature_data)
                scn.objects.link(rig)
                scn.objects.active = rig
                rig.select = True

                # armature = armature_object.getData()
                # if armature is None:
                #         base_name = Blender.sys.basename(file_object.name)
                #         armature_name = Blender.sys.splitext(base_name)[0]
                #         armature = Blender.Armature.New(armature_name)
                #         armature_object.link(armature)
                #armature.drawType = Blender.Armature.STICK
                #armature.envelopes = False
                #armature.vertexGroups = True
               
                #bpy.ops.object.editmode_toggle()
                bpy.ops.object.mode_set(mode='EDIT')

                bones = []
                bone_names = []
                parents = []
                for i in range(num_bones):
                        name = ''
                        parent_bone_index = read_int(honchunk)

                        if version == 3:
                                inv_matrix = Matrix((struct.unpack('<3f', honchunk.read(12)) + (0.0,), 
                                                     struct.unpack('<3f', honchunk.read(12)) + (0.0,), 
                                                     struct.unpack('<3f', honchunk.read(12)) + (0.0,), 
                                                     struct.unpack('<3f', honchunk.read(12)) + (1.0,)))

                                matrix = Matrix((struct.unpack('<3f', honchunk.read(12)) + (0.0,), 
                                                 struct.unpack('<3f', honchunk.read(12)) + (0.0,), 
                                                 struct.unpack('<3f', honchunk.read(12)) + (0.0,), 
                                                 struct.unpack('<3f', honchunk.read(12)) + (1.0,)))

                                name_length = struct.unpack("B" , honchunk.read(1))[0]
                                name = honchunk.read(name_length)

                                honchunk.read(1) #zero
                        elif version == 1:
                                name = ''
                                pos = honchunk.tell() - 4
                                b = honchunk.read(1)
                                while b != '\0':
                                        name += b
                                        b = honchunk.read(1)
                                honchunk.seek(pos + 0x24)
                                inv_matrix = Matrix((struct.unpack('<4f', honchunk.read(16)), 
                                                     struct.unpack('<4f', honchunk.read(16)), 
                                                     struct.unpack('<4f', honchunk.read(16)), 
                                                     struct.unpack('<4f', honchunk.read(16))))

                                matrix = Matrix((struct.unpack('<4f', honchunk.read(16)), 
                                                 struct.unpack('<4f', honchunk.read(16)), 
                                                 struct.unpack('<4f', honchunk.read(16)), 
                                                 struct.unpack('<4f', honchunk.read(16))))

                        name = name.decode()
                        self.log("bone name: %s,parent %d" % (name,parent_bone_index))
                        bone_names.append(name)
                        edit_bone = armature_data.edit_bones.new(name)
                        edit_bone.head = ( 0.0, -1.0, 0.0 )
                        edit_bone.tail = ( 0.0, 0.0, 0.0 )
                        edit_bone.transform(roundMatrix(matrix,4))
                        #edit_bone.use_connect=False
                        edit_bone.length = 1
                        parents.append(parent_bone_index)
                        bones.append(edit_bone)
                for i in range(num_bones):
                        if parents[i] != -1:
                                bones[i].parent = bones[parents[i]]
                honchunk.skip()

                bpy.ops.object.mode_set(mode='OBJECT')
                rig.show_x_ray = True
                scn.update()

                try:
                        honchunk = chunk.Chunk(file,bigendian=0,align=0)
                except EOFError:
                        self.log('error reading mesh chunk')
                        return
                while honchunk.getname() == b'mesh':
                        verts = []
                        faces = []
                        signs = []
                        nrml = []
                        texc = []
                        colors = []
                        #read mesh chunk
                        self.vlog("mesh index: %d" % read_int(honchunk))
                        mode = 1
                        if version == 3:
                                mode = read_int(honchunk)
                                self.vlog("mode: %d" % mode)
                                self.vlog("vertices count: %d" % read_int(honchunk))
                                self.vlog("bounding box: (%f,%f,%f) - (%f,%f,%f)" % \
                                        struct.unpack("<ffffff", honchunk.read(24)))
                                bone_link = read_int(honchunk)
                                self.vlog("bone link: %d" % bone_link)
                                sizename = struct.unpack('B',honchunk.read(1))[0]
                                sizemat = struct.unpack('B',honchunk.read(1))[0]
                                meshname = honchunk.read(sizename)
                                honchunk.read(1) # zero
                                materialname = honchunk.read(sizemat)
                        elif version == 1:
                                bone_link = -1
                                pos = honchunk.tell() - 4
                                b = honchunk.read(1)
                                meshname = ''
                                while b != '\0':
                                        meshname += b
                                        b = honchunk.read(1)
                                honchunk.seek(pos + 0x24)

                                b = honchunk.read(1)
                                materialname = ''
                                while b != '\0':
                                        materialname += b
                                        b = honchunk.read(1)

                        honchunk.skip()

                        meshname = meshname.decode()
                        materialname = materialname.decode()

                        if mode == 1 or not SKIP_NON_PHYSIQUE_MESHES:        
                                msh = bpy.data.meshes.new(meshname)

                                #msh = bpy.data.meshes.new(meshname)
                                #msh.mode |= Blender.Mesh.Modes.AUTOSMOOTH
                                #obj = scn.objects.new(msh)

                        while 1:
                                try:
                                        honchunk = chunk.Chunk(file,bigendian=0,align=0)
                                except EOFError:
                                        self.vlog('error reading chunk')
                                        break
                                if honchunk.getname == b'mesh':
                                        break
                                elif mode != 1 and SKIP_NON_PHYSIQUE_MESHES:
                                        honchunk.skip()
                                else:
                                        if honchunk.getname() == b'vrts':
                                                verts = self.parse_vertices(honchunk)
                                        elif honchunk.getname() == b'face':
                                                faces = self.parse_faces(honchunk,version)
                                        elif honchunk.getname() == b'nrml':
                                                nrml = self.parse_normals(honchunk)
                                        elif honchunk.getname() == b'texc':
                                                texc = self.parse_texc(honchunk,version)
                                        elif honchunk.getname() == b'colr':
                                                colors = self.parse_colr(honchunk)
                                        elif honchunk.getname() == b'lnk1' or honchunk.getname() == b'lnk3':
                                                vgroups = self.parse_links(honchunk,bone_names)
                                        elif honchunk.getname() == b'sign':
                                                signs = self.parse_sign(honchunk)
                                        else:
                                                self.vlog('unknown chunk: %s' % honchunk.chunkname)
                                                honchunk.skip()
                        if mode != 1 and SKIP_NON_PHYSIQUE_MESHES:
                                continue

                           
                        msh.materials.append(bpy.data.materials.new(materialname))

                        msh.from_pydata( verts, [], faces )
                        msh.update(calc_edges=True)

                     
                        if self.flipuv:
                                for t in range(len(texc)):
                                        texc[t] = ( texc[t][0], 1-texc[t][1] )


                        # Generate texCoords for faces
                        texcoords = []
                        for face in faces:
                                texcoords.append( [ texc[vert_id] for vert_id in face ] )
                                
                        uvMain = self.createTextureLayer("UVMain", msh, texcoords)
                                                        
                        for vertex, normal in zip(msh.vertices, nrml):
                                vertex.normal = normal
                        


                        obj = bpy.data.objects.new('%s_Object' % meshname, msh)
                        # Link object to scene
                        scn.objects.link(obj)
                        scn.objects.active = obj
                        scn.update()

                        if bone_link >=0 :
                                grp = obj.vertex_groups.new(bone_names[bone_link])
                                grp.add(list(range(len(msh.vertices))),1.0,'REPLACE')


                        for name in vgroups.keys():
                                grp = obj.vertex_groups.new(name)
                                for (v, w) in vgroups[name]:
                                        grp.add([v], w, 'REPLACE')
                        
                        mod = obj.modifiers.new('MyRigModif', 'ARMATURE')
                        mod.object = rig
                        mod.use_bone_envelopes = False
                        mod.use_vertex_groups = True 


                        if self.removedoubles:
                                obj.select = True
                                bpy.ops.object.mode_set(mode='EDIT', toggle=False)   
                                bpy.ops.mesh.remove_doubles()
                                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                                obj.select = False


                        bpy.context.scene.objects.active = rig
                        rig.select = True
                        bpy.ops.object.mode_set(mode='POSE', toggle=False)
                        pose = rig.pose
                        for b in pose.bones:
                                b.rotation_mode = "QUATERNION"
                        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                        rig.select = False
                        bpy.context.scene.objects.active = None


                scn.update()
                return ( obj, rig )



        def parse_links(self, honchunk,bone_names):
                mesh_index = read_int(honchunk)
                numverts = read_int(honchunk)
                self.vlog("links")
                self.vlog("mesh index: %d" % mesh_index)
                self.vlog("vertices number: %d" % numverts)
                vgroups = {}
                for i in range(numverts):
                        num_weights = read_int(honchunk)
                        weights = struct.unpack("<%df" % num_weights,honchunk.read(num_weights * 4))
                        indexes = struct.unpack("<%dI" % num_weights,honchunk.read(num_weights * 4))
                        for ii, index in enumerate(indexes):
                                name = bone_names[index]
                                if name not in vgroups:
                                        vgroups[name] = list()
                                vgroups[name].append( (i,weights[ii] ) ) 

                honchunk.skip()
                return vgroups

        def parse_vertices(self, honchunk):
                self.vlog('parsing vertices chunk')
                numverts = int((honchunk.chunksize - 4)/12)
                self.vlog('%d vertices' % numverts)
                meshindex = read_int(honchunk)
                return [struct.unpack("<3f", honchunk.read(12)) for i in range(numverts)]

        def parse_sign(self, honchunk):
                self.vlog('parsing sign chunk')
                numverts = int((honchunk.chunksize - 8))
                meshindex = read_int(honchunk)
                self.vlog(read_int(honchunk)) # huh?
                return [struct.unpack("<b", honchunk.read(1)) for i in range(numverts)]

        def parse_faces(self, honchunk,version):
                self.vlog('parsing faces chunk')
                meshindex = read_int(honchunk)
                numfaces = read_int(honchunk)
                self.vlog('%d faces' % numfaces)
                if version == 3:
                        size = struct.unpack('B',honchunk.read(1))[0]
                elif version == 1:
                        size = 4
                if size == 2:
                        return [struct.unpack("<3H", honchunk.read(6)) for i in range(numfaces)]
                elif size ==1:
                        return [struct.unpack("<3B", honchunk.read(3)) for i in range(numfaces)]
                elif size == 4:
                        return [struct.unpack("<3I", honchunk.read(12)) for i in range(numfaces)]
                else:
                        self.log("unknown size for faces:%d" % size)
                        return []

        def parse_normals(self, honchunk):
                self.vlog('parsing normals chunk')
                numverts = int((honchunk.chunksize - 4)/12)
                self.vlog('%d normals' % numverts)
                meshindex = read_int(honchunk)
                return [struct.unpack("<3f", honchunk.read(12)) for i in range(numverts)]

        def parse_texc(self, honchunk,version):
                self.vlog('parsing uv texc chunk')
                numverts = int((honchunk.chunksize - 4)/8)
                self.vlog('%d texc' % numverts)
                meshindex = read_int(honchunk)
                if version == 3:
                        self.vlog(read_int(honchunk)) # huh?
                return [struct.unpack("<2f", honchunk.read(8)) for i in range(numverts)]     
  
        def parse_colr(self, honchunk):
                self.vlog('parsing vertex colours chunk')
                numverts = int((honchunk.chunksize - 4)/4)
                meshindex = read_int(honchunk)
                return [struct.unpack("<4B", honchunk.read(4)) for i in range(numverts)]


        def createTextureLayer(self, name, me, texFaces):
                uvtex = me.uv_textures.new()
                uvtex.name = name
                for n,tf in enumerate(texFaces):
                        datum = uvtex.data[n]
                        datum.uv1 = tf[0]
                        datum.uv2 = tf[1]
                        datum.uv3 = tf[2]
                return uvtex


        def AnimateBones(self, action,pose,frame_motions,num_frames,armature,rig,version):
                bpy.ops.pose.select_all( action='SELECT' )
                bpy.ops.pose.transforms_clear()
                bpy.ops.pose.select_all( action='DESELECT' )
                for frame in range( num_frames ):
                        bpy.context.scene.frame_set( frame+1 )
                        frameMotion = frame_motions[frame]
                        
                        for bonename, motion in frameMotion.items():
                                if bonename not in armature.bones.keys():
                                        continue

                                pbone = pose.bones[bonename]
                                bone  = armature.bones[bonename]

                                bone_rest_matrix = bone.matrix.copy()
                                if bone.parent is not None:
                                        parent_bone = bone.parent
                                        parent_rest_bone_matrix = parent_bone.matrix.copy()
                                        parent_rest_bone_matrix.invert()
                                        bone_rest_matrix *= parent_rest_bone_matrix
                                bone_rest_matrix.invert()
                                bone_rest_matrix.resize_4x4()
                                bone.select = True

                                transform_m, scale_v = GenerateMotionMatrix( motion[0], motion[1], motion[2] )
                                pbone.matrix_basis = transform_m * bone_rest_matrix
                                pbone.scale          = tuple(motion[2])

                                bone.select = False

                        bpy.ops.pose.select_all( action='SELECT' )
                        bpy.ops.anim.keyframe_insert_menu( type='LocRot' )
                        bpy.ops.pose.select_all( action='DESELECT' )


                # if name not in armature.bones.keys():
                #         self.log ('%s not found in armature' % name)
                #         return
                # motion = motions[name]
                # bone = armature.bones[name]
                # bone_rest_matrix = bone.matrix_local.copy()

                # if bone.parent is not None:
                #                 parent_bone = bone.parent
                #                 parent_rest_bone_matrix = parent_bone.matrix_local.copy()
                #                 parent_rest_bone_matrix.invert()
                #                 bone_rest_matrix *= parent_rest_bone_matrix

                # bone_rest_matrix_inv = Matrix(bone_rest_matrix)
                # bone_rest_matrix_inv.invert()
                # pbone = pose.bones[name]
                # #bpy.context.scene.objects.active = pbone
                # bone.select = True
                # for i in range(0, num_frames):
                #         bpy.context.scene.frame_set( i )
                #         transform,size = getTransformMatrix(motions,bone,i,version)
                #         pbone.matrix_basis = transform * bone_rest_matrix_inv
                #         pbone.scale = size
                #         bpy.ops.anim.keyframe_insert_menu( type='LocRotScale' ) 

        def CreateBlenderClip(self, filename, obj, rig):
                path, base = os.path.split( filename )
                base = base.split('.')[0]

                file = open(filename,'rb')
                if not file:
                        self.log("can't open file")
                        return
                sig = file.read(4)
                if sig != b'CLIP':
                        self.err('unknown file signature')
                        return

                try:
                        clipchunk = chunk.Chunk(file,bigendian=0,align=0)
                except EOFError:
                        self.log('error reading first chunk')
                        return
                version = read_int(clipchunk)
                num_bones = read_int(clipchunk)
                num_frames = read_int(clipchunk)
                self.vlog ("version: %d" % version)
                self.vlog ("num bones: %d" % num_bones)
                self.vlog ("num frames: %d" % num_frames)


                
                # Select the armature object
                bpy.context.scene.objects.active = rig
                rig.select = True

                bpy.ops.object.mode_set(mode='POSE', toggle=False)

                pose = rig.pose

                armature = rig.data
                bone_index = -1
                motions = {}


                rig.animation_data_create()
                action = bpy.data.actions.new(name=base)
                rig.animation_data.action = action

                while 1:
                        try:
                                clipchunk = chunk.Chunk(file,bigendian=0,align=0)
                        except EOFError:
                                self.vlog('error reading chunk')
                                break
                        if version == 1:
                                name = clipchunk.read(32)
                                if '\0' in name:
                                        name = name[:name.index('\0')]
                        boneindex = read_int(clipchunk)
                        keytype = read_int(clipchunk)
                        numkeys = read_int(clipchunk)
                        if version > 1:
                                namelength = struct.unpack("B",clipchunk.read(1))[0]
                                name = clipchunk.read(namelength)
                                clipchunk.read(1)

                        name = name.decode()

                        if name not in motions:
                                motions[name] = {}
                        self.log ("%s,boneindex: %d,keytype: %d,numkeys: %d" % \
                                (name,boneindex,keytype,numkeys))
                        if keytype == MKEY_VISIBILITY:
                                data = struct.unpack("%dB"  % numkeys,clipchunk.read(numkeys))
                        else:
                                data = struct.unpack("<%df" % numkeys,clipchunk.read(numkeys * 4))
                        motions[name][keytype] = list(data)
                        clipchunk.skip()
                #file read, now animate that bastard!
                        
                frame_motions = GenerateFrameMotions( motions, num_frames, version )
                self.AnimateBones(action,pose,frame_motions,num_frames,armature,rig,version)
                        
                #pose.update()

                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)


def register():
        bpy.utils.register_class(HoNImporter)

def unregister():
        bpy.utils.unregister_class(HoNImporter)    
 

if __name__ == "__main__":
        register()
        
