import bpy
from mathutils import *
import os

#create class for the other functions? BlockBuilder. 

MCPATH = os.path.join(os.environ['APPDATA'], '.minecraft')
# This needs to be set by the addon during initial inclusion. Set as a bpy.props.StringProperty within the Scene, then refer to it all over this addon.

class BlockType:
    """Defines a Minecraft unit substance type. More advanced meshes/objects extend this with more complex models."""
    
    def __init__(self, name, faceIndices):  # face indices is assumed to be a 6-array in TRBLFB order (top right back left front bottom)
        self.name = name
        self.faceTxIds = faceIndices
        modelName = "".join([self.name, "Block"])
        meshName =  "".join([self.name, "BlockMesh"])

    @staticmethod
    def getNameVariant(bname, blockID, extraData):
        wools = [ ['Orange', (255,150,54)],	# entirely different texture coords for these! dammit, notch!
                    ['Magenta', (227,74,240)],
                    ['LightBlue', (83,146,255)],
                    ['Yellow', (225,208,31)],
                    ['LightGreen', (67,218,53)],
                    ['Pink', (248,153,178)],
                    ['Grey', (75,75,75)],
                    ['LightGrey', (181,189,189)],
                    ['Cyan', ()],
                    ['Purple', ()],
                    ['Blue', (44,58,176)],
                    ['Brown', (99,59,32)],
                    ['DarkGreen', (64,89,27)],
                    ['Red', (188,51,46)],
                    ['Black', (28,23,23)]]
        if blockID == 35:
            return 'wool' + wools[extraData][0]	#wool is a simple index into this array.
        else:
            return bname


    def createModel():
        """Creates a singular model representing this type. If one exists already, returns reference to it rather than making more."""
        pass



#class BlockBuilder:
#    """Defines methods for creating whole-block Minecraft blocks with correct texturing - just needs minecraft path."""

def construct(blockID, basename, diffuseRGB, cubeTexFaces, extraData, constructType="box"):
    # find block function/constructor that matches the construct type.
    
    #if it's a simple cube...
    #stairs
    #onehigh
    #torch
    block = None
    if constructType == 'box':
        block = createMCBlock(basename, diffuseRGB, cubeTexFaces)	#extra data
    elif constructType == 'onehigh':
        block = createOneHigh(basename, diffuseRGB, cubeTexFaces)	#extra data
    elif constructType == '00track':
        block = createTrack(basename, diffuseRGB, cubeTexFaces, extraData)
    else:
        block = createMCBlock(basename, diffuseRGB, cubeTexFaces)	#extra data	# soon to be removed as a catch-all!
    return block




def getMCTex():
    tname = 'mcTexBlocks'
    if tname in bpy.data.textures:
        return bpy.data.textures[tname]

    print("creating fresh new minecraft terrain texture")
    texNew = bpy.data.textures.new(tname, 'IMAGE')
    texNew.image = getMCImg()
    texNew.image.use_premultiply = True
    texNew.use_alpha = True
    texNew.use_preview_alpha = True
    texNew.use_interpolation = False


def getMCImg():
    global MCPATH
    osdir = os.getcwd()	#original os folder before jumping to temp.
    if 'terrain.png' in bpy.data.images:
        return bpy.data.images['terrain.png']
    else:
        img = None
        import zipfile
        mcjar = os.path.sep.join([MCPATH, 'bin', 'minecraft.jar'])
        zf = open(mcjar, 'rb')
        zipjar = zipfile.ZipFile(zf)
        if 'terrain.png' in zipjar.namelist():
            os.chdir(bpy.app.tempdir)
            zipjar.extract('terrain.png')
        zipjar.close()
        zf.close()  #needed?
            #
        temppath = os.path.sep.join([os.getcwd(), 'terrain.png'])
        try:
            img = bpy.data.images.load(temppath)
        except:
            os.chdir(osdir)
            raise NameError("Cannot load image %s" % temppath)
        os.chdir(osdir)
        return img


def createBlockCubeUVs(blockname, me, matrl, faceIndices):    #assume me is a cube mesh.  RETURNS **NAME** of the uv layer created.
    __listtype = type([])
    if type(faceIndices) != __listtype:
        if (type(faceIndices) == type(0)):
            faceIndices = [faceIndices]*6
            print("Applying singular value to all 6 faces")
        else:
            print("setting material and uvs for %s: non-numerical face list")
            raise IndexError("improper face assignment data!")


    #now, assume we have a list of per-face block IDs.
    #faceindices should be an array of minecraft material indices (into the terrain.png) with what texture should be used for each face. Face order is [Bottom,Top,Right,Front,Left,Back]

    uname = blockname + 'UVs'

    blockUVLayer = me.uv_textures.new(uname)   #assuming it's not so assigned already, ofc.

    #get image reference (from the material texture...?)
    xim = getMCImg()

    #ADD THE MATERIAL! (could this be conditional on it already being applied?)
    if matrl.name not in me.materials:
        me.materials.append(matrl)

    meshtexfaces = blockUVLayer.data.values()
    
    for fnum, fid in enumerate(faceIndices):
        face = meshtexfaces[fnum]

        face.image = xim
        #face.blend_type = 'ALPHA'	# set per-material as of 2.60 -- need to fix this.
        ## now use instead: matrl.game_settings.alpha_blend = 'ALPHA'
        
        #TODO: now looks like: matrl.game_settings.use_backface_culling = False	#no backface cull == Make two-sided.
        #use_image
        #face.use_twoside = True	#set per-material in 2.60 -- it's now something like backface_cull = No.

        #Pick UV square off the 2D texture surface based on its Minecraft texture 'index'
        #eg 160 for lapis, 49 for glass... etc, etc.
        # that's x,y:

        #mctIndex = 3    #16  #minecraft texture index.
    
        mcTexU = fid % 16
        mcTexV = int(fid / 16)  #int division.

        #DEBUG print("minecraft chunk texture x,y within image: %d,%d" % (mcTexU, mcTexV))
    
        #multiply by square size to get U1,V1:
    
        u1 = (mcTexU * 16.0) / 256.0    # or >> 4 (div by imagesize to get as fraction)
        v1 = (mcTexV * 16.0) / 256.0    # ..
    
        v1 = 1.0 - v1 #y goes low to high for some reason.
    
        #DEBUG print("That means u1,v1 is %f,%f" % (u1,v1))
    
        #16px will be 1/16th of the image.
        #The image is 256px wide and tall.

        uvUnit = 1/16.0

        mcUV1 = Vector((u1,v1))
        mcUV2 = Vector((u1+uvUnit,v1))
        mcUV3 = Vector((u1+uvUnit,v1-uvUnit))  #subtract uvunit for y  
        mcUV4 = Vector((u1, v1-uvUnit))

        #DEBUG print("Creating UVs for face with values: %f,%f to %f,%f" % (u1,v1,mcUV3[0], mcUV3[1]))

        #can we assume the cube faces are always the same order? It seems so, yes.
        #So,face 0 is the bottom.
        if fnum == 1:    # top
            face.uv1 = mcUV2
            face.uv2 = mcUV1
            face.uv3 = mcUV4
            face.uv4 = mcUV3
        elif fnum == 5:    #back
            face.uv1 = mcUV1
            face.uv2 = mcUV4
            face.uv3 = mcUV3
            face.uv4 = mcUV2
        else:   #bottom (0) and all the other sides..
            face.uv1 = mcUV3
            face.uv2 = mcUV2
            face.uv3 = mcUV1
            face.uv4 = mcUV4

    return "".join([blockname, 'UVs'])


    #References for UV stuff:

    #http://www.blender.org/forum/viewtopic.php?t=15989&view=previous&sid=186e965799143f26f332f259edd004f4

    #newUVs = cubeMesh.uv_textures.new('lapisUVs')
    #newUVs.data.values() -> list... readonly?

    #contains one item per face...
    #each item is a bpy_struct MeshTextureFace
    #each has LOADS of options, including TWOSIDE
    # :D
    
    # .uv1 is a 2D Vector(u,v)
    #they go:
    
    # uv1 --> uv2
    #          |
    #          V
    # uv4 <-- uv3
    #
    # .. I think






def createMCBlock(mcname, colourtriple, mcfaceindices):    #should also take a diffuse colour RGB triple, to set shaded display mode nicely for the textured block.
    """Creates a new minecraft WHOLE-block if it doesn't already exist, properly textured.
    Array order for mcfaceindices is: [bottom, top, right, front, left, back]"""

    #Has an instance of this blocktype already been made?
    blockname = mcname + 'Block'
    if blockname in bpy.data.objects:
        return bpy.data.objects[blockname]

    #Create cube!
    bpy.ops.mesh.primitive_cube_add()

    blockOb = bpy.context.object    #get ref to last created ob.
    # quarter it's size, to 1x1x1 (it's currently 2 bu x 2 bu x 2 bu)
    bpy.ops.transform.resize(value=(0.5, 0.5, 0.5))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    
    blockOb.name = blockname
    blockMesh = blockOb.data
    meshname = blockname + 'Mesh'
    blockMesh.name = meshname

    #Need a material. create it new if it doesn't exist.
    matname = mcname + 'Mat'
    blockMat = None
    if matname in bpy.data.materials:
        blockMat = bpy.data.materials[matname]
    else:
        blockMat = bpy.data.materials.new(matname)
        blockMat.use_shadeless = True
        blockMat.use_face_texture = True
        blockMat.use_face_texture_alpha = True

    # assign blockmat to the block object!!
    
    if colourtriple is not None:
        #create a shaded-view material colouring
        diffusecolour = [n/256.0 for n in colourtriple]
        blockMat.diffuse_color = diffusecolour
        blockMat.diffuse_shader = 'OREN_NAYAR'
        blockMat.diffuse_intensity = 0.8
        blockMat.roughness = 0.909
        #print("Setting known diffuse color of material %s as %d,%d,%d" % (matname, blockdat[1][0], blockdat[1][1], blockdat[1][2]))            
    else:
        #create a blank/unhelpful material.
        blockMat.diffuse_color = [214,127,255] #shocking pink

#    #ADD THE MATERIAL! (could this be conditional on it already being applied?)
#    blockMesh.materials.append(blockMat)    # previously applied in the uvtex creation function for some reason...

    #mcraft-tex: ONE TEXTURE TO RULE THEM ALL (and in the darkness, bind them)
    mcTexture = getMCTex()
    blockMat.texture_slots.add()  #it has 18, but unassignable...
    mTex = blockMat.texture_slots[0]
    mTex.texture = mcTexture
    #set as active texture slot?
    
    mTex.texture_coords = 'UV'
    #mTex.mapping = 'CUBE'
    #tSlot.uv_layer = 'lapisUVs'    #the UVs I'll generate l8r
    mTex.use_map_alpha = True

    mcuvs = createBlockCubeUVs(mcname, blockMesh, blockMat, mcfaceindices)
    
    if mcuvs is not None:
        mTex.uv_layer = mcuvs
    #array order is: [bottom, top, right, front, left, back]
    
    #for the cube's faces to align correctly to Minecraft north, based on the UV assignments I've bodged, correct it all by spinning the verts after the fact. :p
    # -90degrees in Z. (clockwise a quarter turn)
    # Or, I could go through a crapload more UV assignment stuff, which is no fun at all.
    #bpy ENSURE MEDIAN rotation point, not 3d cursor pos.
    
    bpy.ops.object.mode_set(mode='EDIT')   ##the line below...
    #bpy.ops.objects.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    #don't want toggle! Want "ON"!
    bpy.ops.transform.rotate(value=(-1.5708,), axis=(0, 0, 1), constraint_axis=(False, False, True), constraint_orientation='GLOBAL')
    #bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
        
    return blockOb
    # other options are available ofc...

    #set various settings, add image texture... all that jazz.
    #Use alpha. Probably don't premult. twoside. etc.
    ## Create a GLASS BLOCK to make sure that works!

# #################################################

#TODO: Can make these work on same lines, with this having all the same code, except for the UV unwrap bit, and the meshbuild bit.
def createOneHigh(mcname, colourtriple, mcfaceindices):    #should also take a diffuse colour RGB triple, to set shaded display mode nicely for the textured block.
    """Creates a new minecraft WHOLE-block if it doesn't already exist, properly textured.
    Array order for mcfaceindices is: [bottom, top, right, front, left, back]"""
    #Has an instance of this blocktype already been made?
    #NB: Here is where to make switches for extradata renamed materials!
    #print('onehigh request: %s...' % mcname)
    blockname = mcname + 'Block'
    if blockname in bpy.data.objects:
        return bpy.data.objects[blockname]

    #print('...req: %sBlock not found in Objects. Creating...' % mcname)
    from mathutils import Vector
    #Create one-high 1/16th BU high single-face, with short sides. eg pressure plates, etc.
    # .... requires an almost unbelievable amount of faffing around to ensure the bits I want to move are properly marked as selected. Sigh.
    #create cube!
    bpy.ops.mesh.primitive_cube_add()

    blockOb = bpy.context.object    #get ref to last created ob.
    # quarter it's size, to 1x1x1 (it's currently 2 bu x 2 bu x 2 bu)
    bpy.ops.transform.resize(value=(0.5, 0.5, 0.5))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    #Make it 1 high with minimum fuss.
    mesh = blockOb.data
    verts = mesh.vertices
    topface = mesh.faces[1]
    for v in topface.vertices:
        vtx = verts[v]
        vp = vtx.co
        vtx.co = Vector((vp[0], vp[1], vp[2]-0.9375))

    #done making mesh! (now just need UVs set right)

    blockOb.name = blockname
    blockMesh = blockOb.data
    meshname = blockname + 'Mesh'
    blockMesh.name = meshname

    #Need a material. create it new if it doesn't exist.
    matname = mcname + 'Mat'
    blockMat = None
    if matname in bpy.data.materials:
        blockMat = bpy.data.materials[matname]
    else:
        blockMat = bpy.data.materials.new(matname)
        blockMat.use_shadeless = True
        blockMat.use_face_texture = True
        blockMat.use_face_texture_alpha = True

    
    if colourtriple is not None:
        diffusecolour = [n/256.0 for n in colourtriple]
        blockMat.diffuse_color = diffusecolour
        blockMat.diffuse_shader = 'OREN_NAYAR'
        blockMat.diffuse_intensity = 0.8
        blockMat.roughness = 0.909
        #print("Setting known diffuse color of material %s as %d,%d,%d" % (matname, blockdat[1][0], blockdat[1][1], blockdat[1][2]))            
    else:
        #create a blank/unhelpful material.
        blockMat.diffuse_color = [255,0,255] #shocking pink

    mcTexture = getMCTex()
    blockMat.texture_slots.add()  #it has 18, but unassignable...
    mTex = blockMat.texture_slots[0]
    mTex.texture = mcTexture
    mTex.texture_coords = 'UV'
    mTex.use_map_alpha = True

    mcuvs = createBlockCubeUVs(mcname, blockMesh, blockMat, mcfaceindices)	#replace with...
    #mcuvs = createOneHighUVs(mcname, blockMesh, blockMat, mcfaceindices)
    
    if mcuvs is not None:
        mTex.uv_layer = mcuvs

    bpy.ops.object.mode_set(mode='EDIT')   ##the line below...
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.rotate(value=(-1.5708,), axis=(0, 0, 1), constraint_axis=(False, False, True), constraint_orientation='GLOBAL')
    bpy.ops.object.mode_set(mode='OBJECT')
        
    return blockOb



if __name__ == "__main__":
    #MCPATH = os.path.join(os.environ['APPDATA'], '.minecraft')
    #BlockBuilder.create ... might tidy up namespace.
    nublock = createMCBlock("Glass", (1,2,3), [49]*6)
    #grab it, and offset it? then make more... check all test data? Unit test.
    #rotate it a bit,to ensure we got reference ok.
    print(nublock.name)