import time
import ctypes
import os
import platform
from ctypes import POINTER, Structure, c_char, c_char_p, c_uint, c_int, c_float, cast, sizeof, pointer
import bpy
from bpy.props import *

class Face(Structure):
    _fields_ = [ ("mNumIndices", c_uint), ("mIndices", POINTER(c_uint)), ]
class String(Structure):
    _fields_ = [ ("length", c_uint),("data", c_char*1024), ]
class Vector3D(Structure):
    _fields_ = [ ("x", c_float),("y", c_float),("z", c_float), ]
if '32bit' in platform.architecture():
    class MaterialProperty(Structure):
        _fields_=[("mKey", String),("mSemantic", c_uint),("mIndex", c_uint),("mDataLength", c_uint),("mType", c_uint),("mData",POINTER(c_char)),]
else: #64bit has extra padding :(
    class String4(Structure):
        _fields_ = [ ("length", c_uint),("pad",c_uint),("data", c_char*1024), ]
    class MaterialProperty(Structure):
        _fields_=[("mKey", String4),("mSemantic", c_uint),("mIndex", c_uint),("mDataLength", c_uint),("mType", c_uint),("mData",POINTER(c_char)),]
class Material(Structure):
    _fields_ = [("mProperties", POINTER(POINTER(MaterialProperty))),("mNumProperties", c_uint),("mNumAllocated", c_uint),]
class Mesh(Structure):
    _fields_ = [("mPrimitiveTypes", c_uint),("mNumVertices", c_uint),("mNumFaces", c_uint),
        ("mVertices", POINTER(Vector3D)),("mNormals", POINTER(Vector3D)),("mTangents", POINTER(Vector3D)),("mBitangents", POINTER(Vector3D)),
        ("mColors", POINTER(c_uint)*8),("mTextureCoords", POINTER(Vector3D)*8),("mNumUVComponents", c_uint*8),("mFaces", POINTER(Face)),
        ("mNumBones", c_uint),("mBones", POINTER(POINTER(c_uint))),("mMaterialIndex", c_uint),]
class Scene(Structure):
    _fields_ = [("mFlags", c_uint),("mRootNode", POINTER(c_uint)),("mNumMeshes", c_uint),("mMeshes", POINTER(POINTER(Mesh))),
    ("mNumMaterials", c_uint),("mMaterials", POINTER(POINTER(Material))),("mNumAnimations", c_uint),("mAnimations", POINTER(POINTER(c_uint))),
    ("mNumTextures", c_uint),("mTextures", POINTER(POINTER(c_uint))),("mNumLights", c_uint),("mLights", POINTER(POINTER(c_uint))),
    ("mNumCameras", c_uint),("mCameras", POINTER(POINTER(c_uint))),]

def search_library():
    import sys
    # silence 'DLL not found' message boxes on win
    try: ctypes.windll.kernel32.SetErrorMode(0x8007)
    except AttributeError: pass

    if os.name=='posix':
        ext = '.so'
    elif os.name=='nt':
        ext = '.dll'

    for i in range(len(sys.path)):
        folder = os.path.join(sys.path[i], 'assimp')
        if not os.path.exists(folder):
            continue
        for filename in os.listdir(folder):
            if filename.lower().find('assimp') >= 0 and os.path.splitext(filename)[-1].lower() == ext:
                library = os.path.join(folder, filename)
                try: dll = ctypes.cdll.LoadLibrary(library)
                except: continue
                try: load = dll.aiImportFile
                except AttributeError: pass
                else:
                    dll.aiImportFile.restype = POINTER(Scene)
                    dll.aiImportFile.argtypes = [c_char_p, c_uint]
                    return dll;
        return None

dll = search_library()

# limited replacement for BPyImage.comprehensiveImageLoad
def load_image(imagepath, dirname):
    if os.path.exists(imagepath): return bpy.data.images.load(imagepath)
    variants = [os.path.join(dirname, imagepath), os.path.join(dirname, os.path.basename(imagepath))]
    for path in variants:
        if os.path.exists(path): return bpy.data.images.load(path)
        else: print(path, "doesn't exist")
    return None

def load_assimp(path, context, ROTATE, FLATTEN, SMOOTH, REMOVE_DOUBLES):
    t = time.time()
    flags=0x2 #aiProcess_JoinIdenticalVertices
    if FLATTEN: flags = flags | 0x100 #aiProcess_PreTransformVertices
    model = dll.aiImportFile( path.encode('ascii'), flags ).contents
    materials = []
    for index in range(model.mNumMaterials):
        material = bpy.data.materials.new("Material"+str(index))
        for i in range(model.mMaterials[index].contents.mNumProperties):
            p = model.mMaterials[index].contents.mProperties[i].contents
            key = p.mKey.data.decode('utf-8')
            if p.mType == 1: value = [cast(p.mData, POINTER(c_float) )[i] for i in range(p.mDataLength//sizeof(c_float))]
            elif p.mType == 3: value = cast(p.mData, POINTER(String)).contents.data.decode('utf-8')
            elif p.mType == 4: value = [cast(p.mData, POINTER(c_int) )[i] for i in range(p.mDataLength//sizeof(c_int))]
            else: value = p.mData[:p.mDataLength]
            print( "    %s: %s" % (key, value) )
            if( key == "?mat.name" ):
                material.name = value
            if( key == "$clr.diffuse" ):
                material.diffuse_color = ( value[0], value[1], value[2] )
            if( key == "$clr.specular" ):
                material.specular_color = ( value[0], value[1], value[2] )
            if( key == "$mat.shininess" ):
                material.specular_hardness = int(value[0])
            if key == "$tex.file":
                texture= bpy.data.textures.new(value, type='IMAGE')
                image = load_image( value, os.path.dirname(path) )
                has_data = image.has_data if image else False
                if image: texture.image=image
                if p.mSemantic == 1 and has_data and image.depth == 32:
                    mtex = material.texture_slots.add()
                    mtex.texture = texture
                    mtex.texture_coords = 'UV'
                    mtex.use_map_color_diffuse = True
                    mtex.use_map_alpha = True
                    texture.use_mipmap = True
                    texture.use_interpolation = True
                    texture.use_alpha = True
                    material.alpha = 0.0
                elif p.mSemantic == 1:
                    mtex = material.texture_slots.add()
                    mtex.texture = texture
                    mtex.texture_coords = 'UV'
                    mtex.use_map_color_diffuse = True
                elif p.mSemantic in [2,7]:
                    mtex = material.texture_slots.add() #7="HARDNESS"
                    mtex.texture = texture
                    mtex.texture_coords = 'UV'
                    mtex.use_map_color_diffuse = False
                    mtex.use_map_specular = True
                #elif p.mSemantic in [3,4]:
#                    mtex = material.texture_slots.add() #4="EMIT"
#                    mtex.texture = texture
#                    mtex.texture_coords = 'UV'
#                    mtex.use_map_color_diffuse = False
#                    mtex.use_map_ambient = True
                elif p.mSemantic in [5,6]:
                    material.texture_slots.add() #5="HEIGHT"
                    mtex.texture = texture
                    mtex.texture_coords = 'UV'
                    mtex.use_map_color_diffuse = False
                    mtex.use_map_normal = True
                    texture.use_normal_map = True
                    texture.normal_space = "TANGENT"
                elif p.mSemantic == 8:
                    material.texture_slots.add()
                    mtex.texture = texture
                    mtex.texture_coords = 'UV'
                    mtex.use_map_color_diffuse = False
                    mtex.use_map_alpha = False
                    mtex.use_map_translucency = True
                    texture.use_alpha = False
                    material.use_transparency = True
                    material.transparency_method = "Z_TRANSPARENCY"
                    material.alpha = 0.0
        materials.append(material)

    bpy.ops.object.select_all(action="DESELECT")

    for index in range(model.mNumMeshes):
        mesh = model.mMeshes[index].contents
        me = bpy.data.meshes.new("Mesh")
        me.vertices.add(mesh.mNumVertices)
        me.faces.add(mesh.mNumFaces)
        if ROTATE:
            for i in range(mesh.mNumVertices):
                mesh.mVertices[i].z = mesh.mVertices[i].z * -1
            me.vertices.foreach_set("co", [f for i in range(mesh.mNumVertices) for f in (mesh.mVertices[i].x, mesh.mVertices[i].z, mesh.mVertices[i].y) ] )
        else:
            me.vertices.foreach_set("co", [f for i in range(mesh.mNumVertices) for f in (mesh.mVertices[i].x, mesh.mVertices[i].y, mesh.mVertices[i].z) ] )
        def treat_face(f):
            index = [3, 2, 1, 0]
            if f.mNumIndices == 3:
                if f.mIndices[0] == 0:
                    index = [3, 1, 0, 2]
                return f.mIndices[index[1]], f.mIndices[index[2]], f.mIndices[index[3]] ,0 
            else:
                if f.mIndices[1] == 0 or f.mIndices[0] == 0:
                    index = [1, 0, 3, 2]
                return f.mIndices[index[0]], f.mIndices[index[1]], f.mIndices[index[2]], f.mIndices[index[3]] 
        me.faces.foreach_set("vertices_raw", [ f for i in range(mesh.mNumFaces) for f in treat_face(mesh.mFaces[i]) if mesh.mFaces[i].mNumIndices >= 3 ] )
        me.show_double_sided = False
#        me.vertex_normal_flip = False
        if mesh.mTextureCoords[0] and materials[mesh.mMaterialIndex].texture_slots[0] != None:
            me.uv_textures.new()
            for i in range(mesh.mNumFaces):
                tface = me.uv_textures[0].data[i]
                index = [3, 2, 1, 0]
                if mesh.mFaces[i].mNumIndices == 3:
                    if mesh.mFaces[i].mIndices[0] == 0:
                        index = [3, 1, 0, 2]
                    tface.uv1= mesh.mTextureCoords[0][mesh.mFaces[i].mIndices[index[1]]].x, mesh.mTextureCoords[0][mesh.mFaces[i].mIndices[index[1]]].y
                    tface.uv2= mesh.mTextureCoords[0][mesh.mFaces[i].mIndices[index[2]]].x, mesh.mTextureCoords[0][mesh.mFaces[i].mIndices[index[2]]].y
                    tface.uv3= mesh.mTextureCoords[0][mesh.mFaces[i].mIndices[index[3]]].x, mesh.mTextureCoords[0][mesh.mFaces[i].mIndices[index[3]]].y
                if mesh.mFaces[i].mNumIndices == 4:
                    if mesh.mFaces[i].mIndices[1] == 0 or mesh.mFaces[i].mIndices[0] == 0:
                        index = [1, 0, 3, 2]
                    tface.uv1= mesh.mTextureCoords[0][mesh.mFaces[i].mIndices[index[0]]].x, mesh.mTextureCoords[0][mesh.mFaces[i].mIndices[index[0]]].y
                    tface.uv2= mesh.mTextureCoords[0][mesh.mFaces[i].mIndices[index[1]]].x, mesh.mTextureCoords[0][mesh.mFaces[i].mIndices[index[1]]].y
                    tface.uv3= mesh.mTextureCoords[0][mesh.mFaces[i].mIndices[index[2]]].x, mesh.mTextureCoords[0][mesh.mFaces[i].mIndices[index[2]]].y
                    tface.uv4= mesh.mTextureCoords[0][mesh.mFaces[i].mIndices[index[3]]].x, mesh.mTextureCoords[0][mesh.mFaces[i].mIndices[index[3]]].y
                tface.use_image = True
                tface.image = materials[mesh.mMaterialIndex].texture_slots[0].texture.image
        me.materials.append(materials[mesh.mMaterialIndex])
        me.validate()
        me.update()
        ob = bpy.data.objects.new("Mesh", me)
        context.scene.objects.link(ob)
        ob.select = True
        context.scene.objects.active = ob
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.flip_normals()
        if REMOVE_DOUBLES:
            bpy.ops.mesh.remove_doubles()
        if SMOOTH:
            bpy.ops.mesh.faces_shade_smooth()
        bpy.ops.object.mode_set(mode='OBJECT')

    name, ext= os.path.splitext(os.path.basename(path))
    ob = bpy.data.objects.new(name, None)
    context.scene.objects.link(ob)
    ob.select = True
    context.scene.objects.active = ob
    bpy.ops.object.parent_set(type='OBJECT')
    bpy.ops.group.create(name=name)
    bpy.ops.group.objects_add_active()

    dll.aiReleaseImport(pointer(model))
    print( "%.3f" % (time.time()-t) )

class IMPORT_OT_assimp(bpy.types.Operator):
    '''Load any file supported by Assimp (.3ds .ase .lwo .md3 .obj .ply .x ...)'''
    bl_idname = "import_scene.assimp"
    bl_label = "Import using Assimp"

    filepath = StringProperty(name="File Path", description="File path used for importing the file", maxlen= 1024, default= "", subtype='FILE_PATH')
    ROTATE = BoolProperty(name="Rotate", description="Rotate 90 around X axis", default= True)
    FLATTEN = BoolProperty(name="Flatten", description="Collapse the scene graph", default= True)
    SMOOTH = BoolProperty(name="Smooth", description="Shade smooth faces", default= True)
    REMOVE_DOUBLES = BoolProperty(name="Remove Doubles", description="Remove duplicate vertices", default= False)

    def execute(self, context):
        load_assimp(self.filepath, context, self.ROTATE, self.FLATTEN, self.SMOOTH, self.REMOVE_DOUBLES)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
