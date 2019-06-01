from enum import Enum
from io import open
import re
import sys
import os


def printMaterialSerializerUsage():
    print("usage: blender --python OgreMaterialSerializer.py -- file.material");

try:
    import bpy;
except ImportError:
    print("You need to execute this script using blender");
    printMaterialSerializerUsage();
    sys.exit();

try:
    from OgreSerializer import OgreSerializer
    from OgreStringUtils import OgreStringUtils

except ImportError as e:
    directory = os.path.dirname(os.path.realpath(__file__));
    print("Import error: " + str(e) + " manual compilation" );
    srcfile="OgreSerializer.py"; exec(compile(open(os.path.join(directory,srcfile)).read(), srcfile, 'exec'))
    srcfile="OgreStringUtils.py";exec(compile(open(os.path.join(directory,srcfile)).read(), srcfile, 'exec'))

#Enumerates the types of programs which can run on the GPU.
class OgreGpuProgramType(Enum):
    GPT_VERTEX_PROGRAM = "GPT_VERTEX_PROGRAM";
    GPT_FRAGMENT_PROGRAM = "GPT_FRAGMENT_PROGRAM";
    GPT_GEOMETRY_PROGRAM = "GPT_GEOMETRY_PROGRAM";
    GPT_DOMAIN_PROGRAM = "GPT_DOMAIN_PROGRAM";
    GPT_HULL_PROGRAM = "GPT_HULL_PROGRAM";
    GPT_COMPUTE_PROGRAM = "GPT_COMPUTE_PROGRAM";

#Enum to identify material sections.
class OgreMaterialScriptSection(Enum):
    MSS_NONE = "MSS_NONE";
    MSS_MATERIAL = "MSS_MATERIAL";
    MSS_TECHNIQUE = "MSS_TECHNIQUE";
    MSS_PASS = "MSS_PASS";
    MSS_TEXTUREUNIT = "MSS_TEXTUREUNIT";
    MSS_PROGRAM_REF = "MSS_PROGRAM";
    MSS_PROGRAM = "MSS_PROGRAM";
    MSS_DEFAULT_PARAMETERS = "MSS_DEFAULT_PARAMETERS";
    MSS_TEXTURESOURCE = "MSS_TEXTURESOURCE";

#Struct for holding a program definition which is in progress.
class OgreMaterialScriptProgramDefinition:
    def __init__(self):
        self.name = "";
        self.progType = None;
        self.language = "";
        self.source = "";
        self.syntax = "";
        self.supportsSkeletalAnimation = False;
        self.supportsMorphAnimation = False;
        self.usesVertexTextureFetch = False;
        self.customParameters = {};

#Struct for holding the script context while parsing.Struct for holding the script context while parsing.
class OgreMaterialScriptContext:
    def __init__(self):
        self.section = OgreMaterialScriptSection.MSS_NONE;
        self.groupName = "";
        self.material = None;
        self.technique = None;
        self.Pass = None;
        self.textureUnit = None;
        self.program = None;
        self.isVertexProgramShadowCaster = False;
        self.isFragmentProgramShadowCaster = False;
        self.isVertexProgramShadowReceiver = False;
        self.isFragmentProgramShadowReceiver = False;
        self.programParams = None;
        self.numAnimationParametrics = 0;
        self.programDef = None;
        self.techLev = -1;
        self.passLev = -1;
        self.stateLev = -1;
        self.defaultParamLines = [];
        self.lineNo = 0;
        self.filename = "";


def logParseError(error, context):
    if (not context.filename and context.material is not None):
        print("Error in material " + context.material.name + " : " + error);
    else:
        if (context.material is not None):
            print("Error in material " + context.material.name + " at line " + str(context.lineNo) + " of " + context.filename + ": " + error);
        else:
            print("Error at line " + str(context.lineNo) + " of " + context.filename + ": " + error);


#function def for attribute parser; return value determines if the next line should be {
# bool attribute_parser(params_str, context)


def parseColourValue(params,context):
    try:
        if (len(params)==3):
            return (float(params[0]),float(params[1]),float(params[2]),1.0);
        elif (len(params)==4):
            return (float(params[0]),float(params[1]),float(params[2]),float(params[3]));
    except TypeError:
        logParseError("Error excepted float value",context);
    return (1.0,1.0,1.0,1.0);

def parseMaterial(params, context):
    vecparams = re.split(pattern=":",string=params,maxsplit=1);
    if (len(vecparams) >= 2):
        print("Material inheritance not supported yet");
        raise NotImplementedError;
    matname=OgreStringUtils.trim(vecparams[0]);
    matname = re.sub("\.material$","",matname);
    print("Creating Material: " + matname);
    context.material = bpy.data.materials.new(matname);
    context.section = OgreMaterialScriptSection.MSS_MATERIAL;
    return True;


def parseVertexProgramRef(params, context):
    context.section = OgreMaterialScriptSection.MSS_PROGRAM_REF;
    #TODO FIND A CORRESPONDANCE WITH CYCLES MATERIALS
    print("Find a vertex program reference " + params + " (not supported)")
    return True;

def parseGeometryProgramRef(params, context):
    context.section = OgreMaterialScriptSection.MSS_PROGRAM_REF;
    #TODO FIND A CORRESPONDANCE WITH CYCLES MATERIALS
    print("Find a geometry program reference " + params + " (not supported)")
    return True;

def parseFragmentProgramRef(params, context):
    context.section = OgreMaterialScriptSection.MSS_PROGRAM_REF;
    #TODO FIND A CORRESPONDANCE WITH CYCLES MATERIALS
    print("Find a fragment program reference " + params + " (not supported)")
    return True;

def parseVertexProgram(params, context):
    #TODO implement
    raise NotImplementedError;

def parseGeometryProgram(params, context):
    #TODO implement
    raise NotImplementedError;

def parseFragmentProgram(params, context):
    #TODO implement
    raise NotImplementedError;

def parseTechnique(params, context):
    context.section = OgreMaterialScriptSection.MSS_TECHNIQUE;
    print("Find technique " + params + " but this have no use for blender");
    #TODO FIND A CORRESPONDANCE WITH CYCLES MATERIALS
    return True;

def parsePass(params, context):
    #TODO FIND A CORRESPONDANCE WITH CYCLES MATERIALS
    context.section = OgreMaterialScriptSection.MSS_PASS;
    print("Find pass " + params + " but this have no use for blender");
    return True;

def parseAmbient(params, context):
    vecparams = re.split(pattern=" |\t", string=params);
    if (len(vecparams) == 1):
        if (vecparams[0] == "vertexcolour"):
            context.material.use_vertex_color_paint = True;
    elif (len(vecparams) == 3 or len(vecparams) == 4):
        color = parseColourValue(vecparams,context);
        #Blender seems not have an ambient color parameter
        print("Parse ambient color (not used): " + str(color));
        #context.material.ambient_color = color[:3];
        print("Parse ambient: " + str(color[3]));
        context.material.ambient = color[3];
    else:
        logParseError("Bad ambient attribute, wrong number of parameters (expected 1, 3 or 4)",context);
    return False;

def parseDiffuse(params, context):
    vecparams = re.split(pattern=" |\t", string=params);
    if (len(vecparams) == 1):
        if (vecparams[0] == "vertexcolour"):
            context.material.use_vertex_color_paint = True;
    elif (len(vecparams) == 3 or len(vecparams) == 4):
        color = parseColourValue(vecparams,context);
        print("Parse diffuse color: " + str(color[:3]));
        context.material.diffuse_color = color[:3];
        print("Parse diffuse intensity (alpha): " + str(color[3]));
        context.material.diffuse_intensity = color[3];
    else:
        logParseError("Bad diffuse attribute, wrong number of parameters (expected 1, 3 or 4)",context);
    return False;

def parseSpecular(params, context):
    vecparams = re.split(pattern=" |\t", string=params);
    if (len(vecparams) == 2):
        if (vecparams[0] == "vertexcolour"):
            context.material.use_vertex_color_paint = True;
        else:
            logParseError("Bad specular attribute, double parameter statement must be 'vertexcolour <shininess>'",context);
    elif (len(vecparams) == 4 or len(vecparams) == 5):
        color = parseColourValue(vecparams[:len(vecparams)-1],context);
        print("Parse specular color: " + str(color[:3]));
        context.material.specular_color = color[:3];
        print("Parse specular intensity: " + str(float(vecparams[-1])));
        context.material.specular_intensity = float(vecparams[-1]);
    else:
        logParseError("Bad specular attribute, wrong number of parameters (expected 2, 4 or 5)",context);
    return False;

def parseEmissive(params, context):
    vecparams = re.split(pattern=" |\t", string=params);
    if (len(vecparams) == 1):
        if (vecparams[0] == "vertexcolour"):
            context.material.use_vertex_color_paint = True;
    elif (len(vecparams) == 3):
        color = parseColourValue(vecparams,context);
        #Blender seems not have an emissive color parameter
        print("Parse emissive color (not used): " + str(color));
        #context.material.emit_color = color[:3];
        emit_intensity = color[0]*0.2126 + color[1]*0.7152 + color[2]*0.0722;
        print("Compute emit intensity from emissive color: " + str(emit_intensity));
        context.material.emit = emit_intensity;
    elif (len(vecparams) == 4):
        color = parseColourValue(vecparams,context);
        print("Parse emissive color (not used): " + str(color));
        emit_intensity = (color[0]*0.2126 + color[1]*0.7152 + color[2]*0.0722)*color[3];
        print("Compute emit intensity from emissive color + alpha: " + str(emit_intensity));
        context.material.emit = emit_intensity;
    else:
        logParseError("Bad diffuse attribute, wrong number of parameters (expected 1, 3 or 4)",context);
    return False;

def parseTextureUnit(params, context):
    context.section = OgreMaterialScriptSection.MSS_TEXTUREUNIT;
    if (params):
        logParseError("Unsupported texture unit parameter yet: " + params, context);
        context.stateLev += 1;
        #raise NotImplementedError;
    else:
        context.stateLev += 1;
    context.textureUnit = context.material.texture_slots.add();
    return True;

def parseTextureSource(params, context):
    raise NotImplementedError;

def parseTexture(params, context):
    vecparams = re.split(pattern=" |\t", string=params);
    if (len(vecparams)>5):
        logParseError("Invalid texture attribute - expected only up to 5 parameters.",context);
    if (vecparams[0] in bpy.data.textures.keys()):
        context.textureUnit.texture = bpy.data.textures[vecparams[0]];
    else:
        context.textureUnit.texture = bpy.data.textures.new(vecparams[0], type = 'IMAGE');
        img = None;
        img_filename = os.path.join(os.getcwd(),vecparams[0]);
        try:
            img = bpy.data.images.load(img_filename);
            context.textureUnit.texture.image = img;
        except:
            logParseError("Cannot locate the file '"+img_filename+"'",context);

    for p in vecparams[1:]:
        if (p=="1d"):
            raise NotImplementedError;
        elif (p=="2d"):
            pass;
        elif (p=="3d"):
            raise NotImplementedError;
        elif (p=="cubic"):
            raise NotImplementedError;
        elif (p=="unlimited"):
            raise NotImplementedError;
        elif (p=="alpha"):
            raise NotImplementedError;
        elif (p=="gamma"):
            raise NotImplementedError;
        else:
             logParseError("Invalid texture option - "+p+".",context);
    return False;

def parseTexCoord(params, context):
    if (int(params) != 0):
        logParseError("Unsupported multiple texcoord (texcoord given " + params + ")",context);
    return False;

class OgreMaterialSerializer(OgreSerializer):


    def __init__(self):
        OgreSerializer.__init__(self);

        #Set up root attribute parsers
        self._rootAttribParsers = {};
        self._rootAttribParsers["material"] = parseMaterial;
        self._rootAttribParsers["vertex_program"] = parseVertexProgram;
        self._rootAttribParsers["geometry_program"] = parseGeometryProgram;
        self._rootAttribParsers["fragment_program"] = parseFragmentProgram;


        #Set up material attribute parsersSet up material attribute parsers
        self._materialAttribParsers = {};
        self._materialAttribParsers["technique"] = parseTechnique;

        #Set up technique attribute parsersSet up technique attribute parsers
        self._techniqueAttribParsers = {};
        self._techniqueAttribParsers["pass"] = parsePass;

        #Set up pass attribute parsersSet up pass attribute parsers
        self._passAttribParsers = {};
        self._passAttribParsers["ambient"] = parseAmbient;
        self._passAttribParsers["diffuse"] = parseDiffuse;
        self._passAttribParsers["specular"] = parseSpecular;
        self._passAttribParsers["emissive"] = parseEmissive;
        self._passAttribParsers["texture_unit"] = parseTextureUnit;
        self._passAttribParsers["fragment_program_ref"] = parseFragmentProgramRef;
        self._passAttribParsers["geometry_program_ref"] = parseGeometryProgramRef;
        self._passAttribParsers["vertex_program_ref"] = parseVertexProgramRef;


        #Set up texture unit attribute parsers
        self._textureUnitAttribParsers = {};
        self._textureUnitAttribParsers["texture_source"] = parseTextureSource;
        self._textureUnitAttribParsers["texture"] = parseTexture;
        self._textureUnitAttribParsers["tex_coord_set"] = parseTexCoord;

        #Set up program reference attribute parsers
        self._programRefAttribParsers = {};

        #Set up program definition attribute parsers
        self._programAttribParsers = {};

        #Set up program default param attribute parsersSet up program default param attribute parsers
        self._programDefaultParamAttribParsers = {};

        self._scriptContext = OgreMaterialScriptContext();
        self._defaults = False;

    def _invokeParser(self,line, parsers):
        splitCmd = re.split(pattern=" |\t", string=line, maxsplit=1);
        if (splitCmd[0] in parsers):
            cmd = "";
            if (len(splitCmd) >= 2):
                cmd = splitCmd[1];
            return parsers[splitCmd[0]](cmd,self._scriptContext);
        else:
            print("Skip unsupported command: " + splitCmd[0]);
            #logParseError("Unrecognised command: " + splitCmd[0], self._scriptContext);
            return False;


    def _parseScriptLine(self, line):
        section = self._scriptContext.section;
        if (section==OgreMaterialScriptSection.MSS_NONE):
            if (line=="}"):
                logParseError("Unexpected terminating brace.",self._scriptContext);
                return False;
            else:
                return self._invokeParser(line,self._rootAttribParsers);
        elif (section==OgreMaterialScriptSection.MSS_MATERIAL):
            if (line=="}"):
                self._scriptContext.section = OgreMaterialScriptSection.MSS_NONE;
                self._scriptContext.material = None;
                self._scriptContext.passLev = -1;
                self._scriptContext.stateLev = -1;
                self._scriptContext.techLev = -1;
            else:
                return self._invokeParser(line,self._materialAttribParsers);
        elif (section==OgreMaterialScriptSection.MSS_TECHNIQUE):
            if (line=="}"):
                self._scriptContext.section = OgreMaterialScriptSection.MSS_MATERIAL;
                self._scriptContext.passLev = -1;
            else:
                return self._invokeParser(line,self._techniqueAttribParsers);
        elif (section==OgreMaterialScriptSection.MSS_PASS):
            if (line=="}"):
                self._scriptContext.section = OgreMaterialScriptSection.MSS_TECHNIQUE;
                self._scriptContext.Pass = None;
                self._scriptContext.stateLev = -1;
            else:
                return self._invokeParser(line, self._passAttribParsers);
        elif (section==OgreMaterialScriptSection.MSS_TEXTUREUNIT):
            if (line=="}"):
                self._scriptContext.section = OgreMaterialScriptSection.MSS_PASS;
                self._scriptContext.textureUnit = None;
            else:
                return self._invokeParser(line,self._textureUnitAttribParsers);
        elif (section==OgreMaterialScriptSection.MSS_TEXTURESOURCE):
            if (line=="}"):
                #TODO END CREATING TEXTURE
                self._scriptContext.section = OgreMaterialScriptSection.MSS_TEXTUREUNIT;
            else:
                #TODO PARSE TEXTURE CUSTOM PARAMETERS
                pass;
        elif (section==OgreMaterialScriptSection.MSS_PROGRAM_REF):
            if (line=="}"):
                self._scriptContext.section = OgreMaterialScriptSection.MSS_PASS;
                self._scriptContext.program = None;
            else:
                return self._invokeParser(line,self._programRefAttribParsers);
        elif (section==OgreMaterialScriptSection.MSS_PROGRAM):
            if (line=="}"):
                #TODO FINNISH PROGRAM definition
                self._scriptContext.section = OgreMaterialScriptSection.MSS_NONE;
                self._scriptContext.defaultParamLines = [];
                self._scriptContext.programDef = None;
            else:
                #TODO FIND AND INVOKE A custom parser
                return self._invokeParser(line, self._programAttribParsers);
        elif (section==OgreMaterialScriptContext.MSS_DEFAULT_PARAMETERS):
            if (lines=="}"):
                self._scriptContext.section = OgreMaterialScriptSection.MSS_PROGRAM;
            else:
                self._scriptContext.defaultParamLines.append(line);
        return False;

    def parseScript(self,stream, filename="", groupName="GLOBAL"):
        self._scriptContext = OgreMaterialScriptContext();
        self._scriptContext.filename = filename;
        self._scriptContext.groupName = groupName;
        eof = False;
        nextIsOpenBracket = False;
        self._scriptContext.lineNo = 1;
        while (not eof):
            try:
                line = OgreSerializer.getLine(stream);
                #print ("line " + str(self._scriptContext.lineNo) + ":\"" + line + "\"");
                self._scriptContext.lineNo += 1;
                if (not ((not line) or line.startswith("//"))):
                    if (nextIsOpenBracket):
                        if (line != "{"):
                            logParseError("Expecting '{' but got " + line + " instead.", self._scriptContext);
                        nextIsOpenBracket = False;
                    else:
                        nextIsOpenBracket = self._parseScriptLine(line);

            except (EOFError, IndexError) as e:
                eof = True;
        if (self._scriptContext.section != OgreMaterialScriptSection.MSS_NONE):
            logParseError("Unexpected end of file.", self._scriptContext);
        else:
            print(filename + " loaded with success !")


if __name__ == "__main__":
    argv = sys.argv;
    try:
        argv = argv[argv.index("--")+1:];  # get all args after "--"
    except:
        printMaterialSerializerUsage();
        sys.exit();
    if (len(argv) > 0):
        filename = argv[0];
        matfile = open(filename,mode='rb');
        matserializer = OgreMaterialSerializer();
        matserializer.disableValidation();
        matserializer.parseScript(matfile, filename);
    else:
        printMaterialSerializerUsage();
