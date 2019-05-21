from threading import Thread, Lock

from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer, TNonblockingServer, THttpServer

import ContentProvider
from ttypes import *
from math import *

import struct
import math

import bpy
from bpy.app.handlers import persistent

class Packer:
    def __init__(self, format, iterable, f, chunkSize = 4*1024):
        self.fun = f
        self.fmt = format
        self.done = 0
        self.total = len(iterable)
        self.src = iterable
        self.chunkSize = chunkSize
        self.componentSize = struct.calcsize(format)
        self.componentCount = len(f(iterable[0]))
        self.buffer = bytearray(self.componentSize*self.componentCount*self.chunkSize)

    def __len__(self):
        return int(math.ceil(self.total / float(self.chunkSize)))

    def __iter__(self):
        return self
    
    def fill(self,base,cnt):
        o = 0
        cs = self.componentSize
        cc = self.componentCount
        fmt = self.fmt
        fun = self.fun
        buf = self.buffer
        src = self.src
        for i in range(base,base+cnt):
            a = fun(src[i])
            for j in range(0,cc):
                b = a[j]
                struct.pack_into(fmt, buf, o, b)
                o += cs

    def __next__(self):
        if self.done >= self.total:
            raise StopIteration
        if self.done + self.chunkSize <= self.total:
            self.fill(self.done,self.chunkSize)
            self.done += self.chunkSize
            return self.buffer
        else:
            l = (self.total - self.done)
            self.fill(self.done,l)
            self.done += l
            l *= self.componentCount * self.componentSize
            return self.buffer[0:l]

class PackerF(Packer):
    def __init__(self, iterable, f, chunkSize = 4*1024):
        Packer.__init__(self,'=f',iterable,f,chunkSize)

class PackerUI32(Packer):
    def __init__(self, iterable, f, chunkSize = 4*1024):
        Packer.__init__(self,'=I',iterable,f,chunkSize)

import array

def packIdxUV(mesh,name):
    if not name in mesh.uv_textures:
        return None
    #bpy.data.meshes['Monkey'].uv_textures['UVTex'].data[0].uv4    
    uva = array.array('f',[0.0 for i in range(len(mesh.vertices)*2)])
    uv = mesh.uv_textures[name].data
    faces = mesh.polygons
    for n in range(0,len(faces)):
        [a,b,c] = faces[n].vertices
        uvf = uv[n]
        uva[2*a]   = uvf.uv1[0]
        uva[2*a+1] = uvf.uv1[1]
        uva[2*b]   = uvf.uv2[0]
        uva[2*b+1] = uvf.uv2[1]
        uva[2*c]   = uvf.uv3[0]
        uva[2*c+1] = uvf.uv3[1]
    return [bytes(uva)]

def packPosition(mesh):
    a = array.array('f',[0.0 for i in range(len(mesh.polygons)*3*3)])
    i = 0
    va = mesh.vertices
    for f in mesh.polygons:
        for v in f.vertices:
            a[i] = va[v].co[0] ; i += 1
            a[i] = va[v].co[1] ; i += 1
            a[i] = va[v].co[2] ; i += 1
    return [bytes(a)]

def packNormal(mesh):
    a = array.array('f',[0.0 for i in range(len(mesh.polygons)*3*3)])
    i = 0
    va = mesh.vertices
    for f in mesh.polygons:
        for v in f.vertices:
            a[i] = va[v].normal[0] ; i += 1
            a[i] = va[v].normal[1] ; i += 1
            a[i] = va[v].normal[2] ; i += 1
    return [bytes(a)]

def packUV(mesh,name):
    if not name in mesh.uv_textures:
        return None
    a = array.array('f',[0.0 for i in range(len(mesh.polygons)*3*2)])
    i = 0
    for f in mesh.uv_textures[name].data:
        uv = f.uv_raw
        for j in range(0,6):
            a[i] = uv[j] ; i += 1
    return [bytes(a)]

def packColor(mesh,name):
    if not name in mesh.vertex_colors:
        return None
    a = array.array('f',[0.0 for i in range(len(mesh.polygons)*3*3)])
    i = 0
    for f in mesh.vertex_colors[name].data:
        a[i] = f.color1[0] ; i += 1
        a[i] = f.color1[1] ; i += 1
        a[i] = f.color1[2] ; i += 1
        a[i] = f.color2[0] ; i += 1
        a[i] = f.color2[1] ; i += 1
        a[i] = f.color2[2] ; i += 1
        a[i] = f.color3[0] ; i += 1
        a[i] = f.color3[1] ; i += 1
        a[i] = f.color3[2] ; i += 1
    return [bytes(a)]

def packMesh(mesh):
    position = VertexAttribute(b'position', AttributeType.AT_Vec3, packPosition(mesh))
    normal   = VertexAttribute(b'normal',   AttributeType.AT_Vec3, packNormal(mesh))
    uvs      = [VertexAttribute(n.encode(), AttributeType.AT_Vec2, packUV(mesh,n)) for n in mesh.uv_textures.keys()]
    colors   = [VertexAttribute(n.encode(), AttributeType.AT_Vec2, packColor(mesh,n)) for n in mesh.vertex_colors.keys()]
    return Mesh([position,normal] + uvs + colors,PrimitiveType.PT_Triangles)

def rasterizeTexture(tex,width,height,pixels,cvtFun):
    idx = 0
    dx = 1.0 / float(width)
    dy = 1.0 / float(height)
    cy = 0.0
    for x in range(0,width):
        cx = 0.0
        for y in range(0,height):
            (r,g,b,a) = tex.evaluate((cx,cy,0.0))
            pixels[idx]     = cvtFun(r)
            pixels[idx + 1] = cvtFun(g)
            pixels[idx + 2] = cvtFun(b)
            pixels[idx + 3] = cvtFun(a)
            idx += 4
            cx += dx
        cy += dy

#// Property type
#enum PropertyType {
#    PT_Bool,
#    PT_Float,
#    PT_Int,
#    PT_String,
#    PT_Unsupported
#}

#struct Property {
#    1: string propertyTypeName,
#    2: PropertyType propertyType,
#    3: i16 propertySize,
#    4: binary propertyData
#}
def encodeFloatSeq(val):
    return (PropertyType.PT_Float,array.array('f',val))

def encodeIntSeq(val):
    return (PropertyType.PT_Int,array.array('l',val))

def encodeString(val):
    return (PropertyType.PT_String, val.encode)

encoders = \
    { "<class 'Vector'>" :  encodeFloatSeq
    , "<class 'float'>" :   encodeFloatSeq
    , "<class 'int'>" :     encodeIntSeq
    , "<class 'str'>" :     encodeString
    }

def encodeProperty(val):
    print('encodeProperty')
    valType = str(type(val))
    print(valType)
    if valType in encoders:
        (propType,propData) = encoders[valType](val)
        return Property(valType.encode(),propType,len(propData),bytes(propData))
    else:
        return Property(propertyTypeName=valType.encode())

class BlenderHandler:
  def downloadMesh_temp(self, nameB):
    name = nameB.decode()
    print('downloadMesh(%s)' % name)
    if not name in bpy.data.meshes:
        return Mesh()

    # clone
    # select all: bpy.ops.mesh.select_all(action=’SELECT’)
    # bpy.ops.mesh.quads_convert_to_tris()
    # send

    #selection = bpy.context.selected_objects
    scene = bpy.context.scene
    mode = bpy.context.mode
    print(mode)
    #fsides = len(mesh.faces[0].vertices)
    # only triangles are supported
    #if fsides != 3:
    #    return Mesh()
    if mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.add(type='MESH')
    #tmpObj = bpy.context.active_object
    mesh = bpy.data.meshes[name].copy()
    tmpObj = scene.objects.active
    tmpObj.data = mesh
    tmpObj.select = True
    bpy.context.scene.update()
    print(tmpObj,bpy.context.mode)
    #if bpy.context.mode != 'EDIT':
    #    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.quads_convert_to_tris()
    bpy.context.scene.update()
    bpy.ops.object.mode_set(mode='OBJECT')
    #bpy.ops.object.delete(use_global=True)

#########
#    scene = bpy.context.scene
#    bpy.ops.object.mode_set(mode='OBJECT')
#    for i in scene.objects: i.select = False #deselect all objects
#    object.select = True
#    scene.objects.active = object #set the mesh object to current
#    bpy.ops.object.mode_set(mode='EDIT') #Operators
#    bpy.ops.mesh.select_all(action='SELECT')#select all the face/vertex/edge
#    bpy.ops.mesh.quads_convert_to_tris() #Operators
#    bpy.context.scene.update()
#    bpy.ops.object.mode_set(mode='OBJECT') # set it in object
#    print("Triangulate Mesh Done!")
#    return object
#########

    if mode != 'OBJECT':
        bpy.ops.object.mode_set(mode=mode)
    #for o in selection:
    #    o.select = True
    return packMesh(mesh)
    
    #vl = mesh.vertices
    #fl = mesh.faces
    #vcount = len(vl)
    #p = PackerF(vl,lambda v: v.co)
    #n = PackerF(vl,lambda v: v.normal)
    #i = PackerUI32(fl,lambda f: f.vertices)

    #ptype = PrimitiveType.PT_Triangles
    #pa = VertexAttribute(b'position', AttributeType.AT_Vec3, p)
    #na = VertexAttribute(b'normal', AttributeType.AT_Vec3, n)
    #uvlist = [VertexAttribute(n.encode(),AttributeType.AT_Vec2,[packIdxUV(mesh,n)]) for n in mesh.uv_textures.keys()]
    #return Mesh([pa,na] + uvlist,ptype,i)

  def downloadMeshImpl(self, nameB):
    name = nameB.decode()
    print('downloadMesh(%s)' % name)
    if not name in bpy.data.meshes:
        print('error: Mesh not found: %s' % name)
        return Mesh()
    mesh = bpy.data.meshes[name]
    fsides = len(mesh.polygons[0].vertices)
    # only triangles are supported
    if fsides != 3:
        print('error: Return empty mesh, only triangle primitive is supported!')
        return Mesh()
    return packMesh(mesh)

  def downloadTextureImpl(self, nameB, imageType, width, height):
    name = nameB.decode()
    print('downloadTexture(%s,%s,%d,%d)' % (name,imageType,width,height))
    if not name in bpy.data.textures:
        print('error: Texture not found: %s' % name)
        return []

    # create texture
    imgName = name + "_" + str(width) + "_" + str(height)
    tex = bpy.data.textures[name]
    if imageType == ImageType.IT_RGBA8:
        pixels = array.array('B',[0 for i in range(width*height*4)])
        rasterizeTexture(tex,width,height,pixels,lambda a: max(0,min(255,floor(255.0 * a))))
        return [bytes(pixels)]
    elif imageType == ImageType.IT_RGBAF:
        pixels = array.array('f',[0.0 for i in range(width*height*4)])
        rasterizeTexture(tex,width,height,pixels,lambda a: a)
        return [bytes(pixels)]
    elif imageType == ImageType.IT_JPG:
        print('downloadTexture: IT_JPG is not yet supported!')
        return []
    elif imageType == ImageType.IT_PNG:
        #img = bpy.data.images.new(name=imgName, width=width, height=height, alpha=True, float_buffer=False)
        #rasterizeTexture(tex,width,height,img.pixels,lambda a: a)
        print('downloadTexture: IT_PNG is not yet supported!')
        return []

  def downloadGroupImpl(self, nameB):
    name = nameB.decode()
    print('downloadGroup(%s)' % name)
    if not name in bpy.data.groups:
        print('error: Group not found: %s' % name)
        return []
    return [o.name.encode() for o in bpy.data.groups[name].objects]

  def queryImpl(self, dataPaths):
    return [encodeProperty(eval(dp.decode())) for dp in dataPaths]

  # Hint: this is workaround, wrappers implement sync with blender main thread, because blender python api is not threadsafe
  def downloadMesh(self, nameB):
    global mutex
    mutex.acquire()
    result = self.downloadMeshImpl(nameB)
    mutex.release()
    return result

  def downloadTexture(self, nameB, imageType, width, height):
    global mutex
    mutex.acquire()
    result = self.downloadTextureImpl(nameB, imageType, width, height)
    mutex.release()
    return result

  def downloadGroup(self, nameB):
    global mutex
    mutex.acquire()
    result = self.downloadGroupImpl(nameB)
    mutex.release()
    return result

  def query(self, dataPaths):
    global mutex
    mutex.acquire()
    result = self.queryImpl(dataPaths)
    mutex.release()
    return result

global transport
handler = BlenderHandler()
processor = ContentProvider.Processor(handler)

transport = TSocket.TServerSocket()# "localhost",9090)
server = TServer.TSimpleServer(processor, transport)

class LCServer(Thread):
    def run(self):
        global server
        print("start LCServer")
        server.serve()
        print("stop LCServer")

global serverThread
global mutex

@persistent
def syncWorkaround(scene):
    global mutex
    mutex.release()
    mutex.acquire()

def startServer():
    bpy.app.handlers.scene_update_pre.append(syncWorkaround)
    global serverThread 
    global mutex
    mutex = Lock()
    mutex.acquire()
    serverThread = LCServer()
    serverThread.start()
    
def stopServer():
    global serverThread
    global transport
    print("stop server")
    transport.close()
    bpy.app.handlers.scene_update_pre.remove(syncWorkaround)
