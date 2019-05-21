#bl_info = {
#    "name": "MineBlend 1.7",
#    "description": "Importer for viewing Minecraft 1.7 region data",
#    "author": "Adam Crossan (acro)",
#    "version": (0, 2),
#    "blender": (2, 57, 0),
#    "api": 33333,
#    "location": "File > Import > Minecraft",
#    "warning": "", # used for warning icon and text in addons panel
#    "wiki_url": "",
#    "tracker_url": "",
#    "category": "Learnbgame"
}

import bpy
from bpy.props import FloatVectorProperty
from add_utils import AddObjectHelper, add_object_data
from mathutils import Vector

#from . import minecraft_blocks

from . import blockbuild	#import *?

#gonna be using blockbuild.createMCBlock(mcname, diffuseColour, mcfaceindices) (bottom, top, right, front, left, back!)

#For wolf testing wool colours:

#Load sam's world, 1 chunk,
#3d cursor pos: Vector((-326.2510986328125, 401.4659118652344, -1.0793073670356534e-05))

# Acro's Python3.2 NBT Reader for Blender Importing Minecraft

import os, gzip
from struct import calcsize, unpack, error as StructError

#tag classes: switch/override the read functions once they know what they are
#and interpret payload by making more taggy bits as needed inside self

#add the mcpath as a context var, perhaps, so that it can be accessed from operators etc.

totalchunks = 0
wseed = None	#store chosen world's worldseed here for handy referencing for slimechunk detemination.

#TODO: a bit of OS-switching for Mac,Linux,XP,etc... and user home path!
MCPATH = os.path.join(os.environ['APPDATA'], '.minecraft')	# 'C:/users/adam/AppData/Roaming/.minecraft/'
MCSAVEPATH = os.path.join(MCPATH, 'saves/')

#TODO: Retrieve these from bpy.props properties stuck in the scene RNA...
EXCLUDED_BLOCKS = [1, 3]    #(1,3) # sort of hack to reduce loading / slowdown: (1- Stone, 3- Dirt). Other usual suspects are Grass,Water, Leaves, Sand,StaticLava

LOAD_AROUND_3D_CURSOR = False   #True   #calculates 3D cursor as a world position in Minecraft, and loads around it instead of player saved position.

#Debugging ONLY!! release version should load unknown blocks as the ref 'Fire Warning' texture thing, or something.

unknownBlockIDs = set()

#MCBINPATH -- in /bin, zipfile open minecraft.jar, and get terrain.png.
#Feed directly into Blender, or save into the Blender temp dir, then import.
print(MCPATH)

# An NBT file contains one root TAG_Compound.
# level.dat and region files have different formats.

TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10

INDENTCHAR = "  "

#Blockdata is: [name, diffusecolour RGB triple, (textureID_top, textureID_bottom, textureID_sides) triple or None if nonsquare, custommodel etc]
# Texture IDs are the 1d (2d) count of location of their 16x16 square within terrain.png in minecraft.jar

#Don't store a name for air. Ignore air.
# Order for Blender cube face creation is: [bottom, top, right, front, left, back]

BLOCKDATA = {0: ['Air'],
            1: ['Stone', (116,116,116), [1,1,1,1,1,1]],
            2: ['Grass', (95,159,53), [2,0,3,3,3,3]],    #[bottom, top, right, front, left, back] - top is 0, for now. ofc grass is biome tinted, so... fooey!
            3: ['Dirt', (150, 108, 74), [2,2,2,2,2,2]],
            4: ['Cobblestone', (94,94,94), [16,16,16,16,16,16]],
            5: ['WoodenPlank', (159,132,77), [4,4,4,4,4,4]],
            6: ['Sapling', (0,0,0), [15]*6],
            7: ['Bedrock', [51,51,51], [17]*6],
            8: ['Water', (31,85,255), [207]*6],
            9: ['WaterStat', (62,190,255), [207]*6],
            10: ['Lava', (252,0,0), [255]*6],
            11: ['LavaStat', (230,0,0), [255]*6],
            12: ['Sand', (214,208,152), [18]*6],
            13: ['Gravel', (154,135,135), [19]*6],
            14: ['GoldOre', (252,238,75), [32]*6],
            15: ['IronOre', (216,175,147), [33]*6],
            16: ['CoalOre', (69,69,69), [34]*6],
            17: ['Wood', (76,61,38), [21,21,20,20,20,20]],
            18: ['Leaves', (99,128,15), [53]*6],
            20: ['Glass', (254,254,254), [49]*6],
            21: ['LapisLazuliOre', (28,87,198), [160]*6],
            22: ['LapisLazuliBlock', (25,90,205), [144]*6],
            23: ['Dispenser', (42,42,42), [62,62,45,46,45,45]],
            24: ['Sandstone', (215,209,153), [208,176,192,192,192,192]],
            25: ['NoteBlock', (145,88,64), [74]*6],
            26: ['Bed'],
            27: ['PwrRail', (204,93,22), [163]*6, 'XD', 'onehigh'],	#meshtype-> "rail". define as 1/16thHeightBlock, read extra data to find orientation.
            28: ['DetRail', (134,101,100), [195]*6, 'XD', 'onehigh'],	#change meshtype to "rail" for purposes of slanted bits. later. PLANAR, too. no bottom face.
            29: ['StickyPiston', (114,120,70), [109,106,108,108,108,108], 'XD', 'pstn'],
            31: ['TallGrass'],	#XD
            32: ['DeadShrubs'],
            33: ['Piston', (114,120,70), [109,107,108,108,108,108], 'XD', 'pstn'],
            34: ['PistonHead', (188,152,98), [180,107,180,180,180,180]],	#or top is 106 if sticky (extra data)
            35: ['Wool', (235,235,235), [64]*6, 'XD'],  #XD means use xtra data...
            37: ['Dandelion', (204,211,2), [13]*6, 'flower'],		#TwoPlane X - find out if same for flowers,shrooms, and bigger plants.
            38: ['Rose', (247,7,15), [12]*6, 'flower'],
            39: ['BrownMushrm', (204,153,120), [29]*6, 'unsure', 'xplanes'],
            40: ['RedMushrm', (226,18,18), [28]*6, 'unsure', 'xplanes'],
            41: ['GoldBlock', (255,241,68), [23]*6],
            42: ['IronBlock'],
            43: ['DoubleSlabs'],	#xd for type
            44: ['Slabs'],	#xd for type
            45: ['BrickBlock', (124,69,24), [7]*6],
            46: ['TNT', (219,68,26), [10,9,8,8,8,8]],
            47: ['Bookshelf', (180,144,90), [35,4,4,4,4,4]],
            48: ['MossStone', (61,138,61), [36]*6],
            49: ['Obsidian', (60,48,86), [37]*6],
            50: ['Torch', (240,150,50), [80]*6, 'XD', 'torch'],
            51: ['Fire'],
            52: ['MonsterSpawner', (27,84,124), [65]*6],	#xtra data for what's spinning inside it??
            53: ['WoodenStairs', (159,132,77), [4,4,4,4,4,4], 'XD', 'stairs'],
            54: ['Chest', (164,114,39), [25,25,26,27,26,26], 'dunno'],    #texface ordering is wrong
            55: ['RedStnWire', (255,0,3), [165]*6, 'XD', 'onehigh'],	#direction-dependent, needs extra data. Also texture needs to act as bitmask alpha only, onto material colour on this thing. :S
            56: ['DiamondOre', (93,236,245), [50]*6],
            57: ['DiamondBlock', (93,236,245), [24]*6],
            58: ['CraftingTbl', (160,105,60), [43,43,59,60,59,60]],
            59: ['Seeds', (160,184,0), [180,180,94,94,94,94], 'XD', 'crops'],
            60: ['Farmland', (69,41,21), [2,87,2,2,2,2]],
            61: ['Furnace', (42,42,42), [62,62,45,44,45,45]],		#[bottom, top, right, front, left, back]
            62: ['Burnace', (50,42,42), [62,62,45,61,45,45]],
            63: ['SignPost'],
            64: ['WoodDoor', (145,109,56), [97,97,81,81,81,81], 'XD', 'door'],
            65: ['Ladder', (142,115,60), [83]*6],
            66: ['Rail', (172,136,82), [180,128,180,180,180,180], 'XD', 'onehigh'],	#to be refined for direction etc.
            67: ['CobbleStairs', (77,77,77), [16]*6, 'XD', 'stairs'],
            68: ['WallSign'],
            69: ['Lever', (105,84,51), [96]*6, 'XD', 'lever'],
            70: ['StnPressPlate', (110,110,110), [1]*6, 'none', 'onehigh'],
            71: ['IronDoor', (183,183,183), [98,98,82,82,82,82], 'XD', 'door'],
            72: ['WdnPressPlate', (159,132,77), [4]*6, 'none', 'onehigh'],
            73: ['RedstoneOre', (151,3,3), [51]*6],
            74: ['RedstoneOreGlowing', (255,3,3), [51]*6],	#wth is this?!
            75: ['RedstoneTorchOff', (86,0,0), [115]*6, "rstorchoff"],
            76: ['RedstoneTorchOn', (253,0,0), [99]*6, "rstorch"],
            77: ['StoneButton', (116,116,116), [1]*6, "btn"],
            78: ['Snow', (240,240,240), [66]*6, '', 'onehigh'],
            79: ['Ice', (220,220,255), [67]*6],
            80: ['SnowBlock', (240,240,240), [66]*6],

            81: ['Cactus', (20,141,36), [71,69,70,70,70,70], False, "cactus"],
            82: ['ClayBlock'],
            
            83: ['SugarCane', (130,168,89), [73]*6],
            84: ['Jukebox', (145,88,64), [75,74,74,74,74,74]],	#XD
            
            85: ['Fence', (160,130,70), [4]*6],	#fence mesh, no extra data.
            86: ['Pumpkin', (227,144,29), [118,102,118,119,118,118]],

            87: ['Netherrack', (137,15,15), [103]*6],
            
            
            90: ['Portal', (150,90,180), None],
            
            92: ['Cake'],
            93: ['RedRepOff', (176,176,176), [131]*6, 'xdcircuit', 'redrep'],
            94: ['RedRepOn', (176,176,176), [147]*6, 'xdcircuit', 'redrep'],
            
            96: ['Trapdoor', (117,70,34), [84]*6, 'XD', 'onehigh']
            }
    #Add in the rest!
    #Need textures and materials for each of these! damn!


BLOCKVARIANTS = { 35: [ [''],
                        ['Orange', (255,150,54)],	# entirely different texture coords for these! See about this!
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
                        ['Black', (28,23,23)]
                      ],
                  50: [ [''], #nowt on 0...
                        ['South'],
                        ['North'],
                        ['West'],
                        ['East'],
                        ['Upright']
                      ]
                }

#to read level.dat: compound, long, list short byte. int. ... end.


#Why not just do this as a 10 element array of classes, and instantiate them as list[6](bstream) ?! MAGIC!
# that's what the guy does already!

# See struct - for handling types and bitpacking and converting to/from bytes. :D


#pass classes around as objects. ie class Tag... we now have Tag in the namespace and can instantiate ones of it, right?

# Note that ONLY Named Tags carry the name and tagType data. Explicitly identified Tags (such as TAG_String above) only contains the payload.


# read binary, py 3.2 etc, you get a bytes object.
# seek(pos-in-file), tell() (number of bytes read) and read(n) read n bytes...


class TagReader:    #Tag factory...?
    #a class to generate tags based on ids.
    
    def readNamedTag(bstream):
        """Reads a named Tag from the bytestream provided. Returns a tuple of (name, tag) (where tag object is the payload). Name will be empty for Tag_END. """
        #print("RNT Starting")
        tbyte = bstream.read(1)[0]    # read 1 byte and get its numerical value        #read 1 byte, switch type generated depending (stream-reader type 'abstract?' factory
        #print("Byte read: %d" % tbyte)
        tname = TAG_String(bstream).value
        #print("Name read: %s" % tname)
        #print("RNamedT - name is %s" %tname)
        tpayload = TAGLIST[tbyte](bstream)
        tpayload.name = tname
        return (tname, tpayload)
        #object type = bleh based on the number 0-255 you just read. Which should be a 10... for TAG_Compound.

##DONT PASS THE TYPE IN TO EVERY INSTANCE WHEN ITS ALWAYS THE SAME! DEFINE IT AS A CLASS VAR IN THE SUBCLASSES.

class Tag:
    type = None

    def __init__(self, bstream):
        """Reads self-building data for this type from the bytestream given, until a complete tag instance is ready."""
        # Tag itself doesn't do this. Must be overridden.
        self.name = ""
        ## named tags..? How what when? Are named tags only named when in a tag_compound that defines their names?? And tag_compounds are always named?
        #self.value = "" needed?
        #payload... varies by subclass.
        self._parseContent(bstream)

    #Needed at all??!
    def __readName(self, bstream):
        """Only if called on a named tag .... will this be needed. may be Defined instead ... as a class method later"""
        raise NotImplementedError(self.__class__.__name__)
        pass

    def _parseContent(self, bstream):
        raise NotImplementedError(self.__class__.__name__)
        pass    # raise notimplemented...?        # SUBCLASSES IMPLEMENT THIS!

    #external code. not sure about these at all.
    #Printing / bitformatting as tree
    def toString(self):
        return self.__class__.__name__ + ('("%s")'%self.name if self.name else "") + ": " + self.__repr__()    #huh... self.repr build tree

    def printTree(self, indent=0):
        return (INDENTCHAR*indent) + self.toString()


#could just skip this class....?
class TAG_End(Tag):
    type = TAG_END

    def _parseContent(self, bstream):
        pass
    #so, in fact... no need for this at all!?!


class _TAG_Numeric(Tag):
    """parses one of the numeric types (actual type defined by subclass)"""
    #uses struct bitformats (within each subclass) to parse the value from the data stream...
    bitformat = ""    #class, not instance, var.nB: make this something that will crash badly if not overwritten properly!

    def __init__(self, bstream):
        #if self.bitformat == "":
        #    print("INCONCEIVABLE!")
        #    raise NotImplementedError(self.__class__.__name__)
        #print("fmt is: %s" % self.bitformat)
        self.size = calcsize(self.bitformat)
        super(_TAG_Numeric, self).__init__(bstream)

    def _parseContent(self, bstream):
        #struct parse it using bitformat.
        self.value = unpack(self.bitformat, bstream.read(self.size))[0]    #[0] because this always return a tuple

    def __repr__(self):
        return "%d" % self.value

class TAG_Byte(_TAG_Numeric):
    bitformat = ">b"    # class variable, NOT INSTANCE VARIABLE.
    #easy, it's read 1 byte!
    #def __parseContent(self, bstream):
    #    self.value = bstream.read(1)[0]    #grab next 1 byte in stream. That's the TAG_Byte's payload.
    #    #or rather, set bitformat to ">c"

class TAG_Short(_TAG_Numeric):
#    type = TAG_SHORT
    bitformat = ">h"

class TAG_Int(_TAG_Numeric):
    bitformat = ">i"

class TAG_Long(_TAG_Numeric):
#    id = TAG_LONG
    bitformat = ">q"

class TAG_Float(_TAG_Numeric):
#    id = TAG_FLOAT
    bitformat = ">f"
    
    def __repr__(self):
        return "%0.2f" % self.value

class TAG_Double(_TAG_Numeric):
#    id = TAG_DOUBLE
    bitformat = ">d"
    
    def __repr__(self):
        return "%0.2f" % self.value

class TAG_Byte_Array(Tag):
    type = TAG_BYTE_ARRAY
    def _parseContent(self, bstream):
        #read the length, then grab the bytes.
        length = TAG_Int(bstream)
        self.value = bstream.read(length.value)    #read n bytes from the file, where n is the numerical value of the length. Hope this works OK!

    def __repr__(self):
        return "[%d bytes array]" % len(self.value)
        
class TAG_String(Tag):
    type = TAG_STRING
    
    def _parseContent(self, bstream):
        #print ("Parsing TAG_String")
        length = TAG_Short(bstream)
        readbytes = bstream.read(length.value)
        if len(readbytes) != length.value:
            raise StructError()
        self.value = readbytes.decode('utf-8')    #unicode(read, "utf-8")

    def __repr__(self):
        return self.value

class TAG_List(Tag):
    type = TAG_LIST

    def _parseContent(self, bstream):
        tagId = TAG_Byte(bstream).value
        length = TAG_Int(bstream).value
        self.value = []
        for t in range(length):
            self.value.append(TAGLIST[tagId](bstream))    #so that's just the tags, not the repeated type ids. makes sense.

    def __repr__(self):    # use repr for outputting payload values, but printTree(indent) for outputting all. Perhaps.
        if len(self.value) > 0:
            return "%d items of type %s\r\n" % (len(self.value), self.value[0].__class__.__name__)    #"\r\n".join([k for k in self.value.keys()])    #to be redone!
        else:
            return "Empty List: No Items!"
        #represent self as nothing (type and name already output in printtree by the super().printTree call. Take a new line, and the rest will be output as subelements...
            
    def printTree(self, indent):
        outstr = super(TAG_List, self).printTree(indent)
        for tag in self.value:
            outstr += indent*INDENTCHAR + tag.printTree(indent+1) + "\r\n"
        
        return outstr
    

class TAG_Compound(Tag):
    type = TAG_COMPOUND
        #A sequential list of Named Tags. This array keeps going until a TAG_End is found.
        #NB: "Named tags" are:
        #byte tagType
        #TAG_String name
        #[payload]
    
    # This is where things get named. ALl names must be unique within the tag-compound. So it's value is a dict.
    # it's named. so first thing is, read name.
    # then, keep on reading until you get a Tag_END
    #but, in-place create tags as you go and add them to an internal tag list...
    
    #implement parsing!
    #essentially this parses the PAYLOAD of a named TAG_Compound...
    def _parseContent(self, bstream):
        #tagnext = readNamedTag()
    
        self.value = {}
        #print("Parsing TAG_Compound!")
        readType = bstream.read(1)[0]    #rly?
        #print("First compound inner tag type byte is: %d" % readType)
        while readType != TAG_END:
            tname = TAG_String(bstream).value
            #print ("Tag name read as: %s" % tname)
            payload = TAGLIST[readType](bstream)
            payload.name = tname
            self.value[tname] = payload
            readType = bstream.read(1)[0]

    def __repr__(self):    # use repr for outputting payload values, but printTree(indent) for outputting all. Perhaps.
        return "\r\n"
        #represent self as nothing (type and name already output in printtree by the super().printTree call. Take a new line, and the rest will be output as subelements...
            
    def printTree(self, indent):
        outstr = super(TAG_Compound, self).printTree(indent)
        keys = self.value.keys()
        for k in keys:
            outstr += indent*INDENTCHAR + self.value[k].printTree(indent+1) + "\r\n"
        
        return outstr


TAGLIST = {TAG_BYTE: TAG_Byte, TAG_SHORT: TAG_Short, TAG_INT: TAG_Int, 
    TAG_LONG:TAG_Long, TAG_FLOAT:TAG_Float, TAG_DOUBLE:TAG_Double, 
    TAG_BYTE_ARRAY:TAG_Byte_Array, TAG_STRING:TAG_String,
    TAG_LIST: TAG_List, TAG_COMPOUND:TAG_Compound}


def readLevelDat():
    """Reads the level.dat for info like the world name, player inventory... etc."""
    lvlfile = gzip.open('level.dat', 'rb')

    #first byte must be a 10 (TAG_Compound) containing all else.

    #read a TAG_Compound...
    #rootTag = Tag(lvlfile)

    rootTag = TagReader.readNamedTag(lvlfile)[1]    #don't care about the name... or do we? Argh, it's a named tag. Stick the name IN the tag after reading???

    print(rootTag.printTree(0))    #give it repr with an indent param...?


def readNBT(bstream):
    rootname, rootTag = TagReader.readNamedTag(bstream)
    rootTag.name = rootname    # TODO: This SHOULD be unnecessary
    
    #check if not at end of string and read more NBT tags if present...?
    
    #nfile.close()
    return rootTag

        
def readRegion(fname, vertexBuffer):
    
    #A region has an 8-KILObyte header, containing 1024 locations and 1024 timestamps. Then from 8196 onwards, it's chunk data and (arbitrary?) gaps
    #Chunks are zlib compressed and have their own structure... more on that later.
    print('== Reading region %s ==' % fname)
    
    rfile = open(fname, 'rb')
    
    regionheader = rfile.read(8192)

    chunklist = []
    chunkcount = 0
    
    cio = 0    #chunk index offset
    while cio+4 <= 4096:    #only up to end of the locations! (After that is timestamps)
        cheadr = regionheader[cio:cio+4]
        
        # 3 bytes "offset"            -- how many 4kiB disk sectors away the chunk data is from the start of the file.
        # 1 byte "sector count"    -- how many 4kiB disk sectors long the chunk data is. (this figure is rounded up during save, so this will give the last disk sector in which there's data for this chunk)

        offset = unpack(">i", b'\x00'+cheadr[0:3])[0]
        chunksectorcount = cheadr[3]    #last of the 4 bytes is the size (in 4k sectors) of the chunk
        
        chunksLoaded = 0
        if offset != 0 and chunksectorcount != 0:    #chunks not generated as those coordinates yet will be blank!
            #if chunksLoaded < 10:
            chunkdata = readChunk(rfile, offset, chunksectorcount)    #TODO Make sure you seek back to where you were to start with ...
            chunksLoaded += 1
                #return chunkcount   #bail, bail, bail!
            chunkcount += 1

            #print(chunkdata.printTree(0))
            #quit()
            #chunkcount += 1
            chunklist.append((offset,chunksectorcount))        
    #within the header, work out how many chunks are there... check timestamps... and then jump to chunk...
        cio += 4

    #
    rfile.close()

    print("Region file %s contains %d chunks." % (fname, chunkcount))
    return chunkcount


def toChunkPos(pX,pZ):
    return (pX/16, pZ/16)


def readChunkFromRegion(chunkPosX, chunkPosZ, vertexBuffer):
    """Loads chunk located at the X,Z chunk location provided."""
    from math import floor
    global totalchunks, wseed
    
    #region containing a given chunk is found thusly: floor of c over 32
    regionX = floor(chunkPosX / 32)
    regionZ = floor(chunkPosZ / 32)
    
    rheaderoffset = ((chunkPosX % 32) + (chunkPosZ % 32) * 32) * 4
    
    #print("Reading chunk %d,%d from region %d,%d" %(chunkPosX, chunkPosZ, regionX,regionZ))

    rfileName = "r.%d.%d.mcr" % (regionX, regionZ)
    if not os.path.exists(rfileName):
        #Can't load this! It doesn't exist!
        print("No such region generated.")
        return

    with open(rfileName, 'rb') as regfile:
        # header for the chunk we want is at...
        #The location in the region file of a chunk at (x, z) (in chunk coordinates) can be found at byte offset 4 * ((x mod 32) + (z mod 32) * 32) in its region file.
        #Its timestamp can be found 4096 bytes later in the file
        regfile.seek(rheaderoffset)
        cheadr = regfile.read(4)
        dataoffset = unpack(">i", b'\x00'+cheadr[0:3])[0]
        chunksectorcount = cheadr[3]
        
        if dataoffset == 0 and chunksectorcount == 0:
            print("Region exists, but chunk has never been created within it.")
        else:
            chunkdata = readChunk(regfile, dataoffset, chunksectorcount, vertexBuffer)
            #print("Loaded chunk %d,%d" % (chunkPosX,chunkPosZ))

            totalchunks += 1


def readChunk(bstream, chunkOffset, chunkSectorCount, vtxBuffer):
    #get the datastring out of the file...
    import io, zlib

    #cf = open(fname, 'rb')
    initialPos = bstream.tell()

    cstart = chunkOffset * 4096    #4 kiB
    clen = chunkSectorCount * 4096

    bstream.seek(cstart)    #this bstream is the region file

    chunkHeaderAndData = bstream.read(clen)

    #chunk header stuff is:
    # 4 bytes: length (of remaining data)
    # 1 byte : compression type (1 - gzip - unused; 2 - zlib: it should always be this in actual fact)
    # then the rest, is length-1 bytes of compressed (zlib) NBT data.

    chunkDLength = unpack(">i", chunkHeaderAndData[0:4])[0]
    chunkDCompression = chunkHeaderAndData[4]
    if chunkDCompression != 2:
        print("Not a zlib-compressed chunk!?")
        raise StringError()    #MinecraftSomethingError, perhaps.

    chunkZippedBytes = chunkHeaderAndData[5:]

    #could/should check that chunkZippedBytes is same length as chunkDLength-1.

    #put the regionfile byte stream back to where it started:
    bstream.seek(initialPos)

    #Read the compressed chunk data
    zipper = zlib.decompressobj()
    chunkData = zipper.decompress(chunkZippedBytes)
    chunkDataAsFile = io.BytesIO(chunkData)
    chunkNBT = readNBT(chunkDataAsFile)

    # Geometry creation! etc... If surface only, can get heights etc from lightarray.?

    #top level tag in NBT is an unnamed TAG_Compound, for some reason, containing a named TAG_Compound "Level"
    chunkLvl = chunkNBT.value['Level'].value
    chunkXPos = chunkLvl['xPos'].value
    chunkZPos = chunkLvl['zPos'].value
    #print("Reading blocks for chunk: (%d, %d)\n" % (chunkXPos, chunkZPos))

    readBlocks(chunkLvl, vtxBuffer)

    return chunkNBT
# kick-off reader code test skel:


def readBlocks(chunkLevelData, vertexBuffer):
    """readBlocks(chunkLevelData) -> takes a named TAG_Compound 'Level' containing a chunk's blocks, data, heightmap, xpos,zpos, etc etc. Creates Blender geom from this data.... eventually."""
    #also TileEntities and Entities. Entities will generally be an empty list.

    global unknownBlockIDs

    #chunkLocation = 'xPos' 'zPos' ...
    chunkX = chunkLevelData['xPos'].value
    chunkZ = chunkLevelData['zPos'].value

    #meshes = bpy.data.meshes
    #from that, reference the named ones for Mcraft materials.

    CHUNKSIZE_X = 16
    CHUNKSIZE_Y = 128
    CHUNKSIZE_Z = 16

    _Y_SHIFT = 7    # 2**7 is 128. use for fast multiply
    _YZ_SHIFT = 11    #16 * 128 is 2048, which is 2**11

    # Blocks, Data, Skylight, ... heightmap
    
    #TODO: Check that this chunk has even been populated...
    
    #Blocks contain all the block ids, and Data contains the extra info: 4 bits of lighting info, 4 bits of 'extra fields' eg Lamp direction, crop wetness, etc.
    # Heightmap will give us quick access to the surface of everything - ie optimise out iterating through all sky blocks! :D
    
    #To access a specific block from either the block or data array from XYZ coordinates, use the following formula:
    # Index = x + (y * Height + z) * Width 

    #naive starting point: LOAD ALL THE BLOCKS! :D :D :D

    blockData = chunkLevelData['Blocks'].value    #yields a TAG_Byte_Array value (bytes object)

    heightMap = chunkLevelData['HeightMap'].value
    
    extraData = chunkLevelData['Data'].value
    
    #256 bytes of heightmap data. 16 x 16. Each byte records the lowest level
    #in each column where the light from the sky is at full strength. Speeds 
    #computing of the SkyLight. Note: This array's indexes are ordered Z,X 
    #whereas the other array indexes are ordered X,Z,Y.
    
    #unknownBlockIDs = set() #the empty set
    
    #loadedData --> buffer everything into lists, then batch-create the vertices. Fingers crossed this makes model creation 3000 times faster.
       #list of named, distinct material meshes. add vertices to each, only in batches.

    # dataX will be dX, blender X will be bX.
    for dX in range(CHUNKSIZE_X):
        #print("looping chunk x %d" % dX)
        for dZ in range(CHUNKSIZE_Z):   #-1, -1, -1):
            #get starting Y from heightmap, ignoring excess height iterations.
            heightByte = heightMap[dX + (dZ << 4)]    # z * 16
            #gives the LOWEST LEVEL where light is max. Start at this value, and y-- until we hit bedrock at y == 0. I **THINK**
            dY = heightByte
            #for dY in range(CHUNKSIZE_Y): # naive method (iterate all)
            while dY >= 0:

                blockIndex = dY + (dZ << _Y_SHIFT) + (dX << _YZ_SHIFT)  # max number of bytes in a chunk is 32768. this is coming in at 32839 for XYZ: (15,71,8)
                blockID = blockData[ blockIndex ]

                #except IndexError:
                #    print("X:%d Y:%d Z %d, blockID from before: %d, cx,cz: %d,%d. Blockindex: %d" % (dX,dY,dZ,blockID,chunkX,chunkZ, blockIndex))
                #    raise IndexError
                
                #create this block in the output!
                if blockID != 0 and blockID not in EXCLUDED_BLOCKS:	# 0 is air

                    #Load extra data (if applicable to blockID):
                    #if it has extra data, grab 4 bits from extraData
                    datOffset = (int(blockIndex /2))    #divided by 2
                    datHiBits = blockIndex % 2 #odd or even, will be hi or low nibble
                    extraDatByte = extraData[datOffset] # should be a byte of which we only want part.
                    hiMask = 0b11110000
                    loMask = 0b00001111
                    extraValue = None
                    if datHiBits:
                        #get high 4, and shift right 4.
                        extraValue = loMask & (extraDatByte >> 4)
                    else:
                        #mask hi 4 off.
                        extraValue = extraDatByte & loMask


                    if blockID in BLOCKDATA:
                        #create block in corresponding blockmesh
                        createBlock(blockID, (chunkX, chunkZ), (dX,dY,dZ), extraValue, vertexBuffer)
                    else:
                        print("Unrecognised Block ID: %d" % blockID)
                        #createUnknownMeshBlock()
                        unknownBlockIDs.add(blockID)    #add it to the set of unknowns
                dY -= 1
    
#    print("readBlocks: Chunk Created! (%d,%d)" % (chunkX,chunkZ))


#TODO Key Options for the importer:

#"Surface only": use the heightmap and only load surface.
#Load more than just the top level, obviously, cos of cliff 
#walls, caves, etc. water should count as transparent for this process, as should glass, portal, and all nonsolid block types.
# cliffs will also need more loading,should there be overhangs.
#from side-by-side drops in surface value

#"Load horizon" / "load radius": how far away from the load point should 
#the loading continue? Can't possibly load everything.

def mcToBlendCoord(chunkPos, blockPos):
    """Converts a minecraft chunk X,Z pair and a minecraft ordered X,Y,Z block location triple into a Blender coordinate vector Vx,Vy,Vz.
And remember: in Minecraft, Y points to the sky."""
    
    # Mapping Minecraft coords -> Blender coords
    # In Minecraft, +Z (west) <--- 0 ----> -Z (east), while North is -X and South is +X
    # In Blender, north is +Y, south is-Y, west is -X and east is +X.
    # So negate Z and map it as X, and negate X and map it as Y. It's slightly odd!

    vx = -(chunkPos[1] << 4) - blockPos[2]
    vy = -(chunkPos[0] << 4) - blockPos[0]   # -x of chunkpos and -x of blockPos (x,y,z)
    vz = blockPos[1]    #Minecraft's Y.
    
    return Vector((vx,vy,vz))


def createBlock(blockID, chunkPos, blockPos, extraBlockData, vertBuffer):
    """adds a vertex to the blockmesh for blockID in the relevant location."""

    #chunkpos is X,Z; blockpos is x,y,z for block.
    mesh = getMCBlockType(blockID, extraBlockData)  #this may be inefficient. Instead, perhaps, create all the types at the start, then STOP MAKING THIS CHECK!
    if mesh is None:
        return

    typeName = mesh.name

    vertex = mcToBlendCoord(chunkPos, blockPos)

    if typeName in vertBuffer:  #was if blockID in...
        vertBuffer[typeName].append(vertex)
    else:
        vertBuffer[typeName] = [vertex]

    #xyz is local to the 'stone' mesh for example. but that's from 0 (world).
    #regionfile can be found from chunkPos.
    #Chunkpos is an X,Z pair.
    #Blockpos is an X,Y,Z triple - within chunk.

def batchBuild(meshBuffer):
    #build all geom from pydata as meshes in one shot. :(
    for meshname in (meshBuffer.keys()):
        me = bpy.data.meshes[meshname]  #getMCBlockType(bID)
        me.from_pydata(meshBuffer[meshname], [], [])
        me.update()



def getMCBlockType(blockID, extraBits):
    """Gets reference to blockmesh, creating it if not existent.
Mesh created depends on meshType from the global blockdata (eg whether it's torch or repeater, not a cube!)
The meshes also have to be unique and differently named for directional versions of the same thing - eg track round a corner or up a slope.
This also ensures material and name are set."""
    from . import blockbuild

    bdat = BLOCKDATA[blockID]

    corename = bdat[0]    # eg mcStone, mcTorch

    if len(bdat) > 1:
        colourtriple = bdat[1]
    else:
        colourtriple = [214,127,255] #shocking pink

    mcfaceindices = []
    if len(bdat) > 2 and bdat[2] is not None:
        mcfaceindices = bdat[2]

    usesExtraBits = False
    if len(bdat) > 3:
        usesExtraBits = (bdat[3] == 'XD')

    if not usesExtraBits:	#quick early create...
        landmeshname = "".join(["mc", corename])
        if landmeshname in bpy.data.meshes:
            return bpy.data.meshes[landmeshname]
        else:
            extraBits = None

    objectShape = "box"
    if len(bdat) > 4:
        objectShape = bdat[4]

#        variantData = BLOCKVARIANTS[blockID][extraBits]
#        nameVariant = BLOCKVARIANTS[blockID][extraBits][0]
        #except IndexError:
        #    print("Extra bits came back and tried to address array as: %d" % extraBits)

    #print("%d Block uses extra data: extra data is %d" % (blockID, extraBits))
    
    #real material name comes back from constructor after reading the extra data...

#    corename = "".join([corename, nameVariant])
#    meshname = "".join(["mc", corename])

    dupblock = blockbuild.construct(blockID, corename, colourtriple, mcfaceindices, extraBits, objectShape)	#creates the mesh, no matter what. So.
    #nb: construct should QUICKLY determine the exact thing it needs to make, and then CHECK if it already exists.

    blockname = dupblock.name
    landmeshname = "".join(["mc", blockname.replace('Block', '')])

    if landmeshname in bpy.data.meshes:
        return bpy.data.meshes[landmeshname]

    landmesh = bpy.data.meshes.new(landmeshname)
    landob = bpy.data.objects.new(landmeshname, landmesh)
    bpy.context.scene.objects.link(landob)

    #dupBlockOb = blockbuild.createMCBlock(typename, colourtriple, mcfaceindices)	# (bottom, top, right, front, left, back!)

    dupblock.parent = landob
    landob.dupli_type = "VERTS"
    return landmesh
    #bname = "mcb%d" % BLOCKNAMES[blockID]   # eg mcbStone

    #if landmesh in bpy.data.meshes:
    #    return bpy.data.meshes[landmeshname]
    #else:
    #    landmesh
    #    return createMinecraftType(blockID, corename, extraBits, )


def slimeOn():
    """Creates the cloneable slime block (area marker) and a mesh to duplivert it."""
    if "slimeChunks" in bpy.data.objects:
        return

    #Create cube! (give it silly eyes if possible, too!)
    #ensure 3d cursor at 0...
    
    bpy.ops.mesh.primitive_cube_add()
    slimeOb = bpy.context.object    #get ref to last created ob.
    slimeOb.name = "slimeMarker"
    bpy.ops.transform.resize(value=(8, 8, 8))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    #slimeMarkerMesh = slimeOb.data	# could use this to 
    # make it chunk-sized... starts 2x2x2
    
    # create material for the markers
    slimeMat = None
    smname = "mcSlimeMat"
    if smname in bpy.data.materials:
        slimeMat = bpy.data.materials[smname]
    else:
        slimeMat = bpy.data.materials.new(smname)
        slimeMat.diffuse_color = [86/256.0, 139.0/256.0, 72.0/256.0]
        slimeMat.diffuse_shader = 'OREN_NAYAR'
        slimeMat.diffuse_intensity = 0.8
        slimeMat.roughness = 0.909
        #slimeMat.use_shadeless = True	#traceable false!!
        slimeMat.use_transparency = True
        slimeMat.alpha = .25
        #slimeMat.use_face_texture = True
        #slimeMat.use_face_texture_alpha = True

    slimeOb.data.materials.append(slimeMat)
    slimeChunkmesh = bpy.data.meshes.new("slimeChunks")
    slimeChunkob = bpy.data.objects.new("slimeChunks", slimeChunkmesh)
    bpy.context.scene.objects.link(slimeChunkob)
    slimeOb.parent = slimeChunkob
    slimeChunkob.dupli_type = "VERTS"



def batchSlimeChunks(slimes):
    # essentially, this adds a vertex into the slime duplimesh
    #append vertex...

    #build all geom from pydata as meshes in one shot. :(

    me = bpy.data.meshes["slimeChunks"]
    me.from_pydata(slimes, [], [])
    me.update()



def getWorldSelectList():
    worldList = []
    if os.path.exists(MCSAVEPATH):
        startpath = os.getcwd()
        os.chdir(MCSAVEPATH)
        saveList = os.listdir()
        saveFolders = [f for f in saveList if os.path.isdir(f)]
        wcount = 0
        for sf in saveFolders:
            if os.path.exists(sf + "/level.dat"):
                #read actual world name(not just folder name)
                wData = None
                with gzip.open(sf + '/level.dat', 'rb') as levelDat:
                    wData = readNBT(levelDat)
                wname = wData.value['Data'].value['LevelName'].value
                wsize = wData.value['Data'].value['SizeOnDisk'].value
                readableSize = "(%0.1f)" % (wsize / (1024*1024))
                worldList.append((sf, sf, wname + " " + readableSize))
                wcount += 1
        os.chdir(startpath)

    if worldList != []:
        return worldList
        #itemlist = []
        #for n, wname in enumerate(worldList):
        #    itemlist.append((str(n), os.path.join(MCSAVEPATH,wname), wname))
        #return itemlist
    else:
        return None



def readMinecraftWorld(worldFolder, loadRadius, toggleOptions):
    global unknownBlockIDs, totalchunks, wseed

    global EXCLUDED_BLOCKS

    if not toggleOptions['omitstone']:
        EXCLUDED_BLOCKS = []

    worldList = []

    if os.path.exists(MCSAVEPATH):
        worldList = os.listdir(MCSAVEPATH)
        print("MC Path exists! %s" % os.listdir(MCPATH))
        #whereever os was before, save it,and restore it after this completes.
        os.chdir(MCSAVEPATH)

    #worldSelected = "Afarundria"
    worldSelected = worldFolder

    os.chdir(os.path.join(MCSAVEPATH, worldSelected))

    # If there's a folder DIM-1 in the world folder, you've been to the Nether!
    # And generated Nether regions. :P

    worldData = None

    with gzip.open('level.dat', 'rb') as levelDat:
        worldData = readNBT(levelDat)
#        print(levelStats.printTree(0))

    pPos = [posFloat.value for posFloat in worldData.value['Data'].value['Player'].value['Pos'].value ]   #convoluted, I grant you.
    
    wseed = worldData.value['Data'].value['RandomSeed'].value	#it's a Long
    print("World Seed : %d" % (wseed))	# or self.report....

    #print("Player is at : %0.4f %0.4f %0.4f" % (pPos[0], pPos[1], pPos[2]))
    #retrieve player location from worldstats:
    
    #if LOAD_AROUND_3D_CURSOR:
    if toggleOptions['atcursor']:
        cursorPos = bpy.context.scene.cursor_location
        #that's an x,y,z vector (in Blender coords)
        #convert to insane Minecraft coords!
        # mcraft pos = -Y, Z, -X
        pPos = [ -cursorPos[1], cursorPos[2], -cursorPos[0]]
        
    

    os.chdir("region")
    
    meshBuffer = {}

    regionfiles = os.listdir()

    playerChunk = toChunkPos(pPos[0], pPos[2])  # x, z
    
    print("Loading %d blocks around centre." % loadRadius)
    #loadRadius = 10 #Sane amount: 5 or 4. See also: 'load all' project... omit data below y-level 40. etc. other restriction options.
    #load stone...
    
    #Add an empty or something to show where the player is.
    
    #total chunk count across region files:
    totalchunks = 0
    
    pX = int(playerChunk[0])
    pZ = int(playerChunk[1])
    
    print('Loading a radius of %d chunks around load position, so creating chunks: %d,%d to %d,%d' % (loadRadius, pX-loadRadius, pZ-loadRadius, pX+loadRadius, pZ+loadRadius))

    if (toggleOptions['showslimes']):
        slimeOn()	# if set in options...
        from . import slimes
        slimeBuffer = []

    for z in range(pZ-loadRadius, pZ+loadRadius):
        for x in range(pX-loadRadius, pX+loadRadius):
            readChunkFromRegion(x,z, meshBuffer)

            if (toggleOptions['showslimes']):
                if slimes.isSlimeSpawn(wseed, x, z):
                    slimeLoc = mcToBlendCoord((x,z), (8,8,8))	#(8,8,120)
                    slimeLoc += Vector((0.5,0.5,-0.5))
                    slimeBuffer.append(slimeLoc)

    batchBuild(meshBuffer)
    if (toggleOptions['showslimes']):
        batchSlimeChunks(slimeBuffer)



    #all meshes.update()!

    #Load all chunks in a region (Noooo!)



#    firstRegion = regionfiles[0]
#    regionChunks = readRegion(firstRegion, vertexBuffer)
#    totalchunks += regionChunks
    #for r in regionfiles:
    #    print("Reading: %s" % r)
    #    totalchunks += readRegion(r)

        #print(rdat.printTree(0))
    print("%s contains %d chunks in the overworld" % (worldSelected, totalchunks))
    
    print(" ".join(["%d" % bn for bn in unknownBlockIDs]))
    
    #Debugging:
    hideIfPresent('mcStone')
    hideIfPresent('mcDirt')
    hideIfPresent('mcSandstone')
    hideIfPresent('mcIronOre')
    hideIfPresent('mcGravel')
    hideIfPresent('mcCoalOre')
    hideIfPresent('mcBedrock')
    hideIfPresent('mcRedstoneOre')

    #increase viewport clipping distance to see the world! (or maybe decrease mesh sizes??)
    #bpy.types.Space
    

def hideIfPresent(mName):
    if mName in bpy.data.objects:
        bpy.data.objects[mName].hide = True


def makeCube(scale, meshname, obname):
    scale_x = scale[0]
    scale_y = scale[1]
    scale_z = scale[2]

    x1 = -0.5 * scale_x
    x2 = 0.5 * scale_x
    y1 = -0.5 * scale_y
    y2 = 0.5 * scale_y
    z1 = -0.5 * scale_z
    z2 = 0.5 * scale_z

    verts = [Vector((x1, y2, z1)),
             Vector((x2, y2, z1)),
             Vector((x2, y1, z1)),
             Vector((x1, y1, z1)),

             Vector((x1, y2, z2)),
             Vector((x2, y2, z2)),
             Vector((x2, y1, z2)),
             Vector((x1, y1, z2)),
            ]

    edges = []
    faces = [[0, 1, 2, 3], [7,6,5,4], #top and bot
    [3,0,4,7], [4,0,1,5], [6,2,1,5], [7,3,2,6]] #sides

    #Adding UV data... how! (try something in mesh.uv_...
    #see bpy.ops.mesh.uv_... or object.uv..
    #    # see bpy.ops.mesh.uv_texture_add()
    
    mesh = bpy.data.meshes.new(meshname)
    mesh.from_pydata(verts, edges, faces)
    
    stoneblockObj = bpy.data.objects.new(obname, mesh)

    #And add the Block into the current blender scene. Could do layers = [array of bool] to set it properly. Remember [False]*32 or whatever it is...
    bpy.context.scene.objects.link(stoneblockObj)

    return stoneblockObj



def add_object(self, context):
    
    # Create the Block (to be instanced)
    
    scale_x = self.scale.x
    scale_y = self.scale.y
    scale_z = self.scale.z

    makeCube((scale_x, scale_y, scale_z), meshname, obname)

    #
    # Create the datagrid for where the blocks will appear (this will later be properly generated by the Minecraft data file...
    #

    #but can the pydata create all the verts needed? :D HELL YES! Immediately!
    meshstone = bpy.data.meshes.new('Chunkgrid.Stone')

    #create the 16x16 bit once, then replicate but change the Z??
    vx = []
    for nx in range(16):
        for ny in range(16):
            for nz in range(128):
                vx.append(Vector((nx,ny,nz)))

    meshstone.from_pydata(vx, [], [])   #no edges. No faces.

    gridObj = bpy.data.objects.new("ChunkgridStone", meshstone)
    
    bpy.context.scene.objects.link(gridObj)
   
    
    # useful for development when the mesh may be invalid.
    # mesh.validate(verbose=True)
    
    
    #where do we want the origin to be?
    #nope! Make these VERTS, instead.
    #potentially precalculate each vert pos, too!
    
    #bpy.data.groups.new("Replicant")    #we dupli this all over the new mesh...
    #create a new object, add it to the replicant group.
    
    #create the replicant mesh / object. Name it.
    #Clear its position to 0,0,0
    #Parent it to the volumegrid mesh. Like this:
    
    #create the cube myself in order to fiddle its UVs and texture it as a minecraft block type... probably. Or create cube and then jimmy around with its textures.
    
    
    stoneblockObj.parent = gridObj  #set parentage...
    gridObj.dupli_type = "VERTS"    #instantiate EVERYTHING, Hoooo!

    
    #switch volumegrid to:
    
    #bpy.data.objects['Icosphere'].dupli_type = "VERTS"
    

#nb: bpy.data.groups.remove(bpy.data.groups["MonkeyVaginas.001"])

    #nb if you try creating the same group twice,
    #the second one gets created as name.001

#Nooooooooooooonononono!
#    for xplace in range(16):
#         for yplace in range(16):
#            for zplace in range(128):
#                add_object_data(context, mesh, operator=self)
#                #can add this not as duplicate, but instance?
#                bpy.ops.transform.translate(value=(xplace,yplace,zplace))

    #add_object_data(context, mesh, operator=self)
    #bpy.ops.transform.translate(value=(1,1,1))



class OBJECT_OT_add_object(bpy.types.Operator, AddObjectHelper):	#don't extend 'add object' helper, use file import helper or something similar....
    """Add a Minecraft Chunk Test Object"""
    bl_idname = "mesh.add_mcchunk"
    bl_label = "Add Minecraft Chunk"
    bl_description = "Create a new Minecraft Chunk"
    bl_options = {'REGISTER', 'UNDO'}

    scale = FloatVectorProperty(name='scale',
                                default=(1.0, 1.0, 1.0),
                                subtype='TRANSLATION',
                                description='scaling')

    def execute(self, context):
        #At execution time, rather than otherwise,
        #dynamically define the output

        #for y in range(128):
        
        #Actual original version:
        #add_object(self, context)
        readMinecraftWorld(self,context)

        return {'FINISHED'}


# Feature TODOs
# surface load (skin only, not block instances)
# torch, stairs, rails, redrep meshblocks. flowers/shrooms.
# nether load
# mesh optimisations
# multiple loads per run -- need to name new meshes each time load performed, ie mcGrass.001
# ...