""" 
**Project Name:**      MakeHuman

**Product Home Page:** http://www.makehuman.org/

**Code Home Page:**    http://code.google.com/p/makehuman/

**Authors:**           Thomas Larsson

**Copyright(c):**      MakeHuman Team 2001-2013

**Licensing:**         AGPL3 (see also http://www.makehuman.org/node/318)

**Coding Standards:**  See http://www.makehuman.org/node/165

Abstract
--------
MHX (MakeHuman eXchange format) exporter for Blender 2.5.
Version 1.0

"""

bl_info = {
    'name': 'Export MakeHuman (.mhx)',
    'author': 'Thomas Larsson',
    'version': '1.4',
    'blender': (2, 5, 7),
    'api': 33590,
    'location': 'File > Export',
    'description': 'Export files in the MakeHuman eXchange format (.mhx)',
    'url': 'http://www.makehuman.org',
    "category": "Learnbgame",
    }

"""
Place this file in the .blender/scripts/addons dir
You have to activated the script in the "Add-Ons" tab (user preferences).
Access from the File > Export menu.
"""

MAJOR_VERSION = 1
MINOR_VERSION = 4
SUB_VERSION = 0

import bpy
import mathutils
import os
import types
import array
import struct

verbosity = 1
Epsilon = 1e-3
done = 0

#
#
#

MaxDepth = 6
Optimize = 3

M_Mat    = 0x01
M_Geo    = 0x02
M_Amt    = 0x04
M_Obj    = 0x08
M_Game    = 0x10
M_Scn    = 0x20
M_Tool    = 0x40
M_Anim    = 0x80

M_Nodes = 0x0100
M_Sel    = 0x200
M_Shape    = 0x400
M_VGroup = 0x800
M_Part = 0x1000
M_MHPart = 0x2000
M_UnselShape = 0x4000
M_Rigify = 0x8000

M_All = 0

expMsk = 0
theRig = ""

Quick = True

#
#    RegisteredBlocks: ( local, refer, creator )
#

RegisteredBlocks = {
    'Scene' : (False, True, "''"),
    'World' : (False, True, "''"),
    'Object' : (False, True, "''"),
    'Group' : (False, True, "''"),
    'Action' : (False, True, "''"),

    'Mesh' : (False, True, "''"),
    'Armature' : (False, True, "''"),
    'Lamp' : (False, True, "''"),
    'Camera' : (False, True, "''"),
    'Curve' : (False, True, "''"),
    'Empty' : (False, True, "''"),

    'Material' : (False, True, "''"),
    'Texture' : (False, True, "''"),
    'Image' : (False, True, "''"),

    'Modifier' : (True, False, "'rna.modifiers.new(\"%s\",\"%s\")' % (name, subtype)"),
    'Constraint' : (True, False, "'rna.constraints.new(\"%s\")' % (subtype)"),

    'MeshTextureFaceLayer' : (True, True, "'uvTexCreator(rna,\"%s\")' % (name)"),
    'MeshColorLayer' : (True, True, "'vertColCreator(rna,\"%s\")' % (name)"),
    'VertexGroup' : (True, True, "'vertGroupCreator(rna,\"%s\")' % (name)"),
    'ShapeKey' : (True, True, "'shapeKeyCreator(rna,\"%s\")' % (name)"),
    'ParticleSystem' : (True, True, "'partSysCreator(rna,\"%s\")' % (name)"),

    'Bone' : (True, True, "'edit_bones.new(\"%s\")' % (name)"),
    'BoneGroup' : (True, True, "'boneGroupCreator(rna,\"%s\")' % (name)"),
    
    'FCurve' : (True, False, "'drivers.new(\"%s\")' % (name)"),
    'DriverVariable' : (True, False, "'variables.new(\"%s\")' % (name)"),

    'Spline' : (True, False, "'rna.modifiers.new(\"%s\",\"%s\")' % (name, subtype)"),
    'BezierSplinePoint' : (True, False, "'rna.modifiers.new(\"%s\",\"%s\")' % (name, subtype)"),

}

createdLocal = {
    'Modifier' : {},
    'Constraint' : {},
    'Bone' : {}, 
    'BoneGroup' : {}, 
    'Spline' : {},
    'BezierSplinePoint' : {},

    'MeshTextureFaceLayer' : {},
    'MeshColorLayer' : {},
    'VertexGroup' : {},
    'ShapeKey' : {},
    'ParticleSystem' : {},
}


ModifierTypes = {
    'ArrayModifier' : 'ARRAY', 
    'BevelModifier' : 'BEVEL', 
    'BooleanModifier' : 'BOOLEAN', 
    'BuildModifier' : 'BUILD', 
    'DecimateModifier' : 'DECIMATE', 
    'EdgeSplitModifier' : 'EDGE_SPLIT', 
    'MaskModifier' : 'MASK', 
    'MirrorModifier' : 'MIRROR', 
    'MultiresModifier' : 'MULTIRES', 
    'SolidifyModifier' : 'SOLIDIFY', 
    'SubsurfModifier' : 'SUBSURF', 
    'UVProjectModifier' : 'UV_PROJECT', 
    'ArmatureModifier' : 'ARMATURE', 
    'CastModifier' : 'CAST', 
    'CurveModifier' : 'CURVE', 
    'DisplaceModifier' : 'DISPLACE', 
    'HookModifier' : 'HOOK', 
    'LatticeModifier' : 'LATTICE', 
    'MeshDeformModifier' : 'MESH_DEFORM', 
    'ShrinkWrapModifier' : 'SHRINKWRAP', 
    'SimpleDeformModifier' : 'SIMPLE_DEFORM', 
    'SmoothModifier' : 'SMOOTH', 
    'WaveModifier' : 'WAVE', 
    'ClothModifier' : 'CLOTH', 
    'CollisionModifier' : 'COLLISION', 
    'ExplodeModifier' : 'EXPLODE', 
    'FluidSimulationModifier' : 'FLUID_SIMULATION', 
    'ParticleInstanceModifier' : 'PARTICLE_INSTANCE', 
    'ParticleSystemModifier' : 'PARTICLE_SYSTEM', 
    'SmokeModifier' : 'SMOKE', 
    'SoftBodyModifier' : 'SOFT_BODY', 
    'SurfaceModifier' : 'SURFACE'
}

ConstraintTypes = {
    'CopyLocationConstraint' : 'COPY_LOCATION', 
    'CopyRotationConstraint' : 'COPY_ROTATION', 
    'CopyScaleConstraint' : 'COPY_SCALE', 
    'CopyTransformsConstraint' : 'COPY_TRANSFORMS', 
    'LimitDistanceConstraint' : 'LIMIT_DISTANCE', 
    'LimitLocationConstraint' : 'LIMIT_LOCATION', 
    'LimitRotationConstraint' : 'LIMIT_ROTATION',
    'LimitScaleConstraint' : 'LIMIT_SCALE', 
    'TransformConstraint' : 'TRANSFORM', 
    'ClampToConstraint' : 'CLAMP_TO', 
    'DampedTrackConstraint' : 'DAMPED_TRACK', 
    'IKConstraint' : 'IK', 
    'LockedTrackConstraint' : 'LOCKED_TRACK', 
    'SplineIKConstraint' : 'SPLINE_IK', 
    'StretchToConstraint' : 'STRETCH_TO', 
    'TrackToConstraint' : 'TRACK_TO', 
    'ActionConstraint' : 'ACTION', 
    'ChildOfConstraint' : 'CHILD_OF', 
    'FloorConstraint' : 'FLOOR', 
    'FollowPathConstraint' : 'FOLLOW_PATH', 
    'RigidBodyJointConstraint' : 'RIGID_BODY_JOINT', 
    'ScriptConstraint' : 'SCRIPT', 
    'ShrinkWrapConstraint' : 'SHRINKWRAP'
}

TextureTypes = {
    'ImageTexture' : 'IMAGE',
    'MarbleTexture' : 'MARBLE',
    'EnvironmentMapTexture' : 'ENVIRONMENT_MAP',
    'PointDensityTexture' : 'POINT_DENSITY',
    'VoxelDataTexture' : 'VOXEL_DATA',
    'BlendTexture' : 'BLEND',
    'MusgraveTexture' : 'MUSGRAVE',
    'StucciTexture' : 'STUCCI',
    'VoronoiTexture' : 'VORONOI',
    'CloudsTexture' : 'CLOUDS',
    'MagicTexture' : 'MAGIC',
    'PluginTexture' : 'PLUGIN',
    'WoodTexture' : 'WOOD',
    'DistortedNoiseTexture' : 'DISTORTED_NOISE',
    'NoiseTexture' : 'NOISE',
}

PropertyTypes = {
    'BoolProperty' : 'BOOLEAN',
    'IntProperty' : 'INT',
    'FloatProperty' : 'FLOAT',
    'StringProperty' : 'STRING',
    'EnumProperty' : 'ENUM',
    'PointerProperty' : 'POINTER',
    'CollectionProperty' : 'COLLECTION',

    'BoolVectorProperty' : 'BOOLEAN',
    'IntVectorProperty' : 'INT',
    'FloatVectorProperty' : 'FLOAT',
}

MinBlockLevel = {
    
    'Object' : M_Geo,
    'Mesh' : M_Geo,
    'MeshTextureFaceLayer' : M_Geo,
    'MeshColorLayer' : M_Geo,
    'ShapeKey' : M_Geo,
    'VertexGroup' : M_Geo,
    'Armature' : M_Geo,
    'Pose' : M_Geo,
    'PoseBone' : M_Geo,
    'Material' : M_Mat,
    'Texture' : M_Mat,
    'Image' : M_Mat,
    'Group' : M_Geo,
    'NodeGroup' : M_Geo,
    'Particle' : M_Geo,
    'ParticleSystem' : M_Geo,
    'Action' : M_Anim, 
    'Camera' : M_Scn, 
    'Lamp' : M_Scn, 
    'Scene' : M_Scn,
    'Brush' : M_Tool,
    'Actuator' : M_Game,
    'Controller' : M_Game,
    'Property' : M_Game, 
    'Sensor' : M_Game, 

    'MaterialHalo' : M_Scn, 
    'MaterialPhysics' : M_Game, 
    'MaterialRaytraceTransparency' : M_Scn, 
    'MaterialStrand' : M_Mat, 
    'MaterialVolume' : M_Mat, 
    'AnimViz' : M_Anim, 
    'AnimVizOnionSkinning' : M_Anim, 
    'AnimVizMotionPaths' : M_Anim, 
    'FieldSettings' : M_Scn, 
    'CurveMapping' : M_Scn, 
    'EffectorWeights' : M_Geo, 
    'PointCache' : 0, 
    'SceneRenderData' : 0,
    'GameObjectSettings' : M_Game,
}
        
#
#    exportDefault(typ, data, header, prio, exclude, arrays, pad, fp):
#

def exportDefault(typ, data, header, prio, exclude, arrays, pad, fp):
    if not data:
        return
    if verbosity > 2:
        print("**", data)
    try:
        if not data.enabled:
            return
    except:
        pass
    try:
        name = data.name.replace(' ','_')
    except:
        name = ''

    fp.write("%s%s %s" % (pad, typ, name))
    for val in header:
        fp.write(" %s" % val)
    fp.write("\n")
    writePrio(data, prio, pad+"  ", fp)

    for (arrname, arr) in arrays:
        #fp.write(%s%s\n" % (pad, arrname))
        for elt in arr:
            exportDefault(arrname, elt, [], [], [], [], pad+'  ', fp)

    writeDir(data, prio+exclude+arrays, pad+"  ", fp)
    fp.write("%send %s\n" % (pad,typ))
    return

#
#
#

def initLocalData():
    global createdLocal
    for key in createdLocal.keys():
        createdLocal[key] = []

#
#    writePrio(data, prio, pad, fp):
#    writeDir(data, exclude, pad, fp):
#    writeSubDir(data, exclude, pad, depth, fp):
#

def writePrio(data, prio, pad, fp):
    for ext in prio:
        writeExt(ext, data, [], pad, 0, fp)

def writeDir(data, exclude, pad, fp):
    for ext in dir(data):
        writeExt(ext, data, exclude, pad, 0, fp)
    try:
        props = data.items()
    except:
        props = []
    for (key,val) in props:
        if key != '_RNA_UI':
            fp.write('%sProperty %s\n' % (pad, key))
            writeDir(val, [], pad+'  ', fp)
            fp.write('%send Property\n' %pad)
            #fp.write("%s%sProperty %s" % (pad, key, val.name))
            #writeQuoted(val, fp)
            #fp.write(" ;\n")
    return

def writeSubDir(data, exclude, pad, depth, fp):
    if depth > MaxDepth:
        msg = "OVERFLOW in writeSubDir\n"
        # raise NameError(msg)
        fp.write(msg)
        return
    for ext in dir(data):
        writeExt(ext, data, exclude, pad, depth, fp)
    return

def writeQuoted(arg, fp):
    typ = type(arg)
    if typ == int or typ == float or typ == bool:
        fp.write("%s" % arg)
    elif typ == str:
        fp.write("'%s'"% stringQuote(arg.replace(' ', '_')))
    elif len(arg) > 1:
        c = '['
        for elt in arg:
            fp.write(c)
            writeQuoted(elt, fp)
            c = ','
        fp.write("]")
    else:
        raise NameError("Unknown property %s %s" % (arg, typ))
        fp.write('%s' % arg)

def stringQuote(string):
    s = ""
    for c in string:
        if c == '\\':
            s += "\\\\"
        elif c == '\"':
            s += "\\\""
        elif c == '\'':
            s += "\\\'"
        else:
            s += c
    return s
        
            
#
#    writeExt(ext, data, exclude, pad, depth, fp):        
#

def writeExt(ext, data, exclude, pad, depth, fp):
    if verbosity > 2:
        print(pad, ext)
    if hasattr(data, ext):
        writeValue(ext, getattr(data, ext), exclude, pad, depth, fp)

#
#    writeValue(ext, arg, exclude, pad, depth, fp):
#

excludeList = [\
    # 'material', 'materials', 'active_material', 
    'bl_rna', 'fake_user', 'id_data', 'rna_type', 'name', 'tag', 'users', 'type'
]

Danger = ['particle_edit']    # ['ParticleEdit', 'color_ramp']


def writeValue(ext, arg, exclude, pad, depth, fp):
    global todo

    if len(str(arg)) == 0 or\
       arg == None or\
       arg == [] or\
       ext[0] == '_' or\
       ext in excludeList or\
       ext in exclude or\
       ext in Danger:
        return
        
    if ext == 'end':
        print("RENAME end", arg)
        ext = '\\ end'

    typ = type(arg)
    #print("D", ext, typ)
    typeSplit = str(typ).split("'")
    if typ == int:
        fp.write("%s%s %d ;\n" % (pad, ext, arg))
    elif typ == float:
        fp.write("%s%s %.3f ;\n" % (pad, ext, arg))
    elif typ == bool:
        fp.write("%s%s %s ;\n" % (pad, ext, arg))
    elif typ == str:
        fp.write("%s%s '%s' ;\n" % (pad, ext, stringQuote(arg.replace(' ','_'))))
    elif typ == list:
        fp.write("%s%s List\n" % (pad, ext))
        n = 0
        for elt in arg:
            writeValue("[%d]" % n, elt, [], pad+"  ", depth+1, fp)
            n += 1
        fp.write("%send List\n" % pad)
    elif typ == mathutils.Vector:
        c = '('
        fp.write("%s%s " % (pad, ext))
        for elt in arg:
            fp.write("%s%.3f" % (c,elt))
            c = ','
        fp.write(") ;\n")
    elif typ == mathutils.Euler:
        fp.write("%s%s (%.3f,%.3f,%.3f) ;\n" % (pad, ext, arg[0], arg[1], arg[2]))
    elif typ == mathutils.Quaternion:
        fp.write("%s%s (%.3f,%.3f,%.3f,%.3f) ;\n" % (pad, ext, arg[0], arg[1], arg[2], arg[3]))
    elif typ == mathutils.Matrix:
        fp.write("%s%s Matrix\n" % (pad, ext))
        n = len(arg)
        for i in range(n):
            fp.write("%s  row " %pad)
            for j in range(n):
                fp.write("%s " % arg[i][j])
            fp.write(";\n")
        fp.write("%send Matrix\n" %pad)
    elif writeArray(ext, arg, pad, depth, fp):
        pass
    elif typeSplit[0] == '<class ':
        writeClass(typeSplit, ext, arg, pad, depth, fp)
    else:
        fp.write("# *** %s %s %s %s \n" % (ext, type(arg), arg))

    '''
    elif typ == dict:
        fp.write("%s%s dict\n" % (pad, ext))
        for (key,val) in arg.items():
            fp.write("%s  %s : %s ; \n" % (pad, key, val))
        fp.write("%send dict\n" % pad)
    elif type(arg) == tuple:
        fp.write("%s%s %s ;\n" % (pad, ext, arg))
    elif typ == array:
        fp.write("%s%s array %s ;\n" % (pad, ext, arg))
    elif type(arg) == struct:
        fp.write("%s%s struct %s ;\n" % (pad, ext, arg))
    '''

#
#    extractBpyType(data):
#

def extractBpyType(data):
    typeSplit = str(type(data)).split("'")
    if typeSplit[0] != '<class ':
        return None
    print(typeSplit)
    classSplit = typeSplit[1].split(".")
    if classSplit[0] == 'bpy' and classSplit[1] == 'types':
        return classSplit[2]
    elif classSplit[0] == 'bpy_types':
        return classSplit[1]
    else:
        return None
#
#    writeClass(string, ext, arg, pad, depth, fp):
#

def writeClass(list, ext, arg, pad, depth, fp):
    if depth > MaxDepth:
        fp.write("OVERFLOW in writeClass\n")
        return
    
    classSplit = list[1].split('.')
    if classSplit[0] == "bpy" and classSplit[1] == 'types':
        #<class 'bpy.types.GameObjectSettings'>
        writeBpyType(classSplit[2], ext, arg, pad, depth, fp)        
    elif classSplit[0] == "bpy_types":
        #<class 'bpy.types.GameObjectSettings'>
        writeBpyType(classSplit[1], ext, arg, pad, depth, fp)
    elif classSplit[0] == 'bpy_prop_collection':
        writeBpyPropCollection(ext, arg, pad, depth, fp)        
    elif classSplit[0] == "'netrender":
        return
    elif classSplit[0] == "builtin_function_or_method":
        return
        propName = str(arg).split()[2]
        writeProperty(propName, ext, arg, pad, depth, fp)
    elif classSplit[0] == "PropertyRNA" or classSplit[0] == "PropertyCollectionRNA":
        #<class 'PropertyRNA'>
        #print("PROP", arg, dir(arg))
        if 1 and dir(arg) != []:
            typeSplit = str(type(arg.rna_type)).split("'")
            fp.write("%s%s PropertyRNA\n" % (pad, ext))
            writeSubDir(arg, [], pad+"  ", depth+1, fp)
            # writeClass(typeSplit[1], ext, arg, pad+"  ", depth+1, fp)
            fp.write("%send PropertyRNA\n" % pad)
        return
    elif classSplit[0] == "method":
        fp.write("%s# **METHOD** %s \n" % (pad, arg))
        pass
    else:
        fp.write("%s# **CLASS** %s %s %s \n" % (pad, ext, classSplit, arg))
    return
    
#
#    writeProperty(propName, ext, prop, pad, depth, fp):
#

def writeProperty(propName, ext, prop, pad, depth, fp):
    if propName == '<generic':
        return
    return
    print("BUILTIN", propName, prop, dir(prop))
    fp.write("%s%s Property %s\n" % (pad, ext, PropertyTypes[propName]))
    writeDir(prop, [], pad+"  ", fp)
    fp.write("%send Property\n" % pad)
    
#
#    writeArray(ext, arg, pad, depth, fp):
#

def writeArray(ext, arg, pad, depth, fp):
    try:
        elt = arg[0]
    except:
        return False

    typ = type(elt)
    if typ == int or typ == float:
        fp.write("%s%s Array " % (pad, ext))
        for elt in arg:
            fp.write("%s " % elt)
        fp.write(" ;\n")
    elif typ == bool:
        fp.write("%s%s Array " % (pad, ext))
        for elt in arg:
            if elt:
                fp.write('1 ')
            else:
                fp.write('0 ')
        fp.write(' ;\n')
    else:
        for n,elt in enumerate(arg):
            if elt != None:
                writeValue("%s[%d]" %(ext,n), elt, [], pad, depth+1, fp)        

            
    return True

#
#    writeBpyType(typ, ext, data, pad, depth, fp):
#

def writeBpyType(typ, ext, data, pad, depth, fp):
    if typ in Danger:
        fp.write(" DANGER %s ;\n" % typ)
        return

    try:
        msk = MinBlockLevel[typ]
    except:
        msk = M_All            
    #print("Msk", msk)
    if msk & expMsk == 0:
        return

    try:
        name = data.name.replace(' ','_')
    except:
        name = "None"

    try:
        enabled = data.enabled
    except:
        enabled = True
    if not enabled:
        return

    subtype = None
    try:
        subtype = ModifierTypes[typ]
        typ = 'Modifier'
    except:
        pass
    try:
        subtype = ConstraintTypes[typ]
        typ = 'Constraint'
    except:
        pass
    try:
        subtype = TextureTypes[typ]
        typ = 'Texture'
    except:
        pass

    try:
        (locl, refer, quoted) = RegisteredBlocks[typ]
    except:
        locl = True
        refer = False

    try:
        creator = eval(quoted)
    except:
        creator = ""
    if creator == None:
        creator = ""
    
    if locl:
        if refer:
            if name in createdLocal[typ]:

                fp.write("%s%s Refer %s %s ;\n" % (pad, ext, typ, name))
                return
            rnaType = 'Define'
            createdLocal[typ].append(name)
        else:
            rnaType = 'Struct'
    else:
        if refer:
            fp.write("%s%s Refer %s %s ;\n" % (pad, ext, typ, name))
            return
        else:
            raise NameError("Global Refer %s %s %s" % (ext, typ, name))
        
    fp.write("%s%s %s %s %s %s" % (pad, ext, rnaType, typ, name, creator))
    fp.write("\n")
    writeSubDir(data, [], pad+"  ", depth+1, fp)
    fp.write("%send %s\n" % (pad, rnaType))
    return

def writeBpyPropCollection(ext, data, pad, depth, fp):
    if len(data) == 0:
        return
    fp.write("%s%s Collection\n" % (pad, ext))
    print("coll", ext, data, len(data))
    print("values", data.values())
    print("dir", dir(data))
    n = 0
    for elt in data.items():
        writeValue("%s{%d]" %(ext,n), elt, [], pad+"  ", depth+1, fp)
        n += 1
    fp.write("%send Collection\n" % pad)
    return

#
#    exportAnimationData(adata, fp):
#    exportAction(act, fp):
#    exportFCurve(fcu, fp):
#    exportActionGroup(grp, fp):
#    exportChannel(chnl, fp):
#    exportDriver(drv, fp):
#    exportDriverVariable(drv, fp):
#


def exportAnimationData(adata, fp):
    if adata == None:
        return
    pad = "  "
    #name = adata.name.replace(' ', '_')
    fp.write("%sAnimationData\n" % pad)
    exported = {}
    for drv in adata.drivers:
        exportFCurve(drv, exported, pad+"  ", fp)
    writeDir(adata, ['drivers'], pad+"  ", fp)
    fp.write("%send AnimationData\n\n" % pad)

def exportAction(act, fp):
    name = act.name.replace(' ', '_')
    fp.write("Action %s \n" % name)
    exported = {}
    for fcu in act.fcurves:
        exportFCurve(fcu, exported, "  ", fp)
    writeDir(act, ['fcurves', 'groups'], "  ", fp)
    fp.write("end Action\n\n")
    return

def exportFCurve(fcu, exported, pad, fp):
    dataPath = fcu.data_path.replace(' ', '_')
    words = dataPath.split('"')
    #print("Fcurve", dataPath, words)

    fp.write("%sFCurve %s %d\n"  % (pad, dataPath, fcu.array_index))
    if fcu.driver:
        exportDriver(fcu.driver, pad+"  ", fp)
    for kpt in fcu.keyframe_points:
        exportKeyFramePoint(kpt, pad+"  ", fp)
    for pt in fcu.sampled_points:
        exportSampledPoint(pt, pad+"  ", fp)
    for fmod in fcu.modifiers:
        exportFModifier(fmod, pad+"  ", fp)
    # exportActionGroup(fcu.group, pad+"  ", fp)
    prio = ['extrapolation']
    writePrio(fcu, prio, pad+"  ", fp)
    exclude = ['modifiers', 'keyframe_points', 'sampled_points', 'group', 'data_path', 'array_index', 'driver',
        'auto_clamped_handles', 'color', 'color_mode', 'muted', 'visible']
    writeDir(fcu, prio+exclude, pad+"  ", fp)
    fp.write("%send FCurve\n\n" % pad)
    return 

def alreadyExported(exported, key, val):
    try:
        if val in exported[key]:
            return True
        else:
            exported[key].append(val)
    except:
        exported[key] = [val]
    return False

def exportDriver(drv, pad, fp):
    fp.write("%sDriver %s \n" % (pad, drv.type))
    for var in drv.variables:
        exportDriverVariable(var, pad+"  ", fp)
    writeDir(drv, ['variables'], pad+"  ", fp)
    fp.write("%send Driver\n\n" % pad)

def exportFModifier(fmod, pad, fp):
    fp.write("%sFModifier %s \n" % (pad, fmod.type))
    writeDir(fmod, [], pad+"  ", fp)
    fp.write("%send FModifier\n\n" % pad)

def exportDriverVariable(var, pad, fp):
    name = var.name.replace(' ', '_')
    fp.write("%sDriverVariable %s %s \n" % (pad,name, var.type))
    for targ in var.targets:
        exportDriverTarget(targ, pad+'  ', fp)
    writeDir(var, ['targets'], pad+"  ", fp)
    fp.write("%send DriverVariable\n\n" % pad)

def exportDriverTarget(targ, pad, fp):
    fp.write("%sTarget %s %s\n" % (pad, targ.data_path, targ.id_type))
    writeDir(targ, ['data_path', 'id_type'], pad+'  ', fp)
    fp.write("%send Target\n" % pad)

def exportActionGroup(grp, fp):
    fp.write("%sGroup %s \n" % (pad,grp.name.replace(' ', '_')))
    for chnl in grp.channels:
        exportChannel(chnl, pad+"  ", fp)
    writeDir(grp, ['channels'], "      ", fp)
    fp.write("%send Group\n\n" % pad)

def exportChannel(chnl, pad, fp):
    fp.write("%sChannel %s %d\n" % (pad, chnl.data_path.replace(' ', '_'), chnl.array_index))
    for kpt in chnl.keyframe_points:
        exportKeyFramePoint(kpt, pad+"  ", fp)
    writeDir(chnl, ['keyframe_points', 'group', 'data_path', 'array_index'], pad+"  ", fp)
    fp.write("%send Channels\n\n" % pad)

def exportKeyFramePoint(kpt, pad, fp):
    #fp.write("%skp %.3f %.6f %.6f %.6f %.6f %.6f ;\n" % 
    #    (pad, kpt.co[0], kpt.co[1], kpt.handle1[0], kpt.handle1[1], kpt.handle2[0], kpt.handle2[1]))
    fp.write("%skp %.3f %.6f ;\n" % (pad, kpt.co[0], kpt.co[1]))

def writeTuple(list, fp):
    c = '('
    for elt in list:
        fp.write("%s%.2f" % (c, elt))
        c = ','
    fp.write(") ")
    return
#
#    exportMaterial(mat, fp):
#    exportMTex(index, mtex, use, fp):
#    exportTexture(tex, fp):
#    exportImage(img, fp)
#

def exportMaterial(mat, fp):
    fp.write("Material %s \n" % mat.name.replace(' ', '_'))
    for (n,mtex) in enumerate(mat.texture_slots):
        if mtex:
            exportMTex(n, mtex, mat.use_textures[n], fp)
    prio = ['diffuse_color', 'diffuse_shader', 'diffuse_intensity', 
        'specular_color', 'specular_shader', 'specular_intensity']
    writePrio(mat, prio, "  ", fp)
    exportRamp(mat.diffuse_ramp, 'diffuse_ramp', fp)
    exportRamp(mat.specular_ramp, 'specular_ramp', fp)
    exportDefault("Halo", mat.halo, [], [], [], [], '  ', fp)
    exportDefault("RaytraceTransparency", mat.raytrace_transparency, [], [], [], [], '  ', fp)
    exportDefault("SSS", mat.subsurface_scattering, [], [], [], [], '  ', fp)
    exportDefault("Strand", mat.strand, [], [], [], [], '  ', fp)
    exportNodeTree(mat.node_tree, fp)
    writeDir(mat, prio+['texture_slots', 'volume', 'node_tree',
        'diffuse_ramp', 'specular_ramp', 'use_diffuse_ramp', 'use_specular_ramp', 
        'halo', 'raytrace_transparency', 'subsurface_scattering', 'strand'], "  ", fp)
    fp.write("end Material\n\n")

MapToTypes = {
    'use_map_alpha' : 'ALPHA',
    'use_map_ambient' : 'AMBIENT',
    'use_map_color_diffuse' : 'COLOR',
    'use_map_color_emission' : 'COLOR_EMISSION',
    'use_map_color_reflection' : 'COLOR_REFLECTION',
    'use_map_color_spec' : 'COLOR_SPEC',
    'use_map_color_transmission' : 'COLOR_TRANSMISSION',
    'use_map_density' : 'DENSITY',
    'use_map_diffuse' : 'DIFFUSE',
    'use_map_displacement' : 'DISPLACEMENT',
    'use_map_emission' : 'EMISSION',
    'use_map_emit' : 'EMIT', 
    'use_map_hardness' : 'HARDNESS',
    'use_map_mirror' : 'MIRROR',
    'use_map_normal' : 'NORMAL',
    'use_map_raymir' : 'RAYMIR',
    'use_map_reflect' : 'REFLECTION',
    'use_map_scatter' : 'SCATTERING',
    'use_map_specular' : 'SPECULAR_COLOR', 
    'use_map_translucency' : 'TRANSLUCENCY',
    'use_map_warp' : 'WARP',
}

def exportMTex(index, mtex, use, fp):
    tex = mtex.texture
    texname = tex.name.replace(' ','_')
    mapto = None
    prio = []
    for ext in MapToTypes.keys():
        if getattr(mtex, ext):
            if mapto == None:
                mapto = MapToTypes[ext]
            prio.append(ext)    
            print("Mapto", ext, mapto)
            
    fp.write("  MTex %d %s %s %s\n" % (index, texname, mtex.texture_coords, mapto))
    writePrio(mtex, ['texture']+prio, "    ", fp)
    print("MTEX", texname,  list(MapToTypes.keys()) )
    writeDir(mtex, list(MapToTypes.keys()) + ['texture', 'type', 'texture_coords', 'offset'], "    ", fp)
    print("DONE MTEX", texname)
    fp.write("  end MTex\n\n")
    return

def exportTexture(tex, fp):
    if not tex:
        return
    fp.write("Texture %s %s\n" % (tex.name.replace(' ', '_'), tex.type))
    if tex.type == 'IMAGE' and tex.image:
        fp.write("  Image %s ;\n" % tex.image.name.replace(' ', '_'))
        fp.write("end Texture\n\n")
        return

    exportRamp(tex.color_ramp, "color_ramp", fp)
    exportNodeTree(tex.node_tree, fp)
    writeDir(tex, ['color_ramp', 'node_tree', 'image_user', 'use_nodes', 'use_textures', 'type', 'users_material'], "  ", fp)
    fp.write("end Texture\n\n")

def exportImage(img, fp):
    imgName = img.name.replace(' ', '_')
    if imgName == 'Render_Result':
        return
    fp.write("Image %s\n" % imgName)
    fp.write("  Filename %s ;\n" % (img.filepath))
    # writeDir(img, [], "  ", fp)
    fp.write("end Image\n\n")

def exportRamp(ramp, name, fp):
    if ramp == None:
        return
    print(ramp)
    fp.write("  Ramp %s\n" % name)

    for elt in ramp.elements:
        col = elt.color
        fp.write("    Element (%.3f,%.3f,%.3f,%.3f) %.3f ;\n" % (col[0], col[1], col[2], col[3], elt.position))
    writeDir(ramp, ['elements'], "    ", fp)
    fp.write("  end Ramp\n")

#
#    exportWorld(world, fp):
#    exportScene(scn, fp):
#

def exportWorld(world, fp):
    fp.write("World %s\n" % (world.name.replace(' ', '_')))
    exportDefault("Lighting", world.lighting, [], [], [], [], '  ', fp)
    exportDefault("Mist", world.mist, [], [], [], [], '  ', fp)
    exportDefault("Stars", world.stars, [], [], [], [], '  ', fp)
    writeDir(world, ['lighting', 'mist', 'stars'], "  ", fp)
    fp.write("end World\n\n")

def exportScene(scn, fp):
    fp.write("Scene %s\n" % (scn.name.replace(' ', '_')))
    exportNodeTree(scn.nodetree, fp)
    exportGameData(scn.game_data, fp)
    for kset in scn.all_keying_sets:
        exportDefault("KeyingSet", kset, [kset.name], [], ['type_info'], [], '  ', fp)
    for obase in scn.bases:
        exportDefault("ObjectBase", obase, [], [], [], [], '  ', fp)
    for ob in scn.objects:
        fp.write("  Object %s ;\n" % (ob.name.replace(' ','_')))
    exportDefault("RenderSettings", scn.render, [], [], [], [('Layer', scn.render.layers)], '  ', fp)
    exportToolSettings(scn.tool_settings, fp)
    exportDefault("UnitSettings", scn.unit_settings, [], [], [], [], '  ', fp)
    writeDir(scn, 
        ['bases', 'all_keying_sets', 'game_data', 'network_render', 'nodetree', 'objects', 'render',
        'pose_templates', 'tool_settings', 'unit_settings'], "  ", fp)
    fp.write("end Scene\n\n")

def exportToolSettings(tset, fp):
    fp.write("  ToolSettings\n")
    exportDefault("ImagePaint", tset.image_paint, [], [], [], [], '    ', fp)
    exportDefault("Sculpt", tset.sculpt, [], [], [], [], '    ', fp)
    exportDefault("VertexPaint", tset.vertex_paint, [], [], [], [], '    ', fp)
    exportDefault("WeightPaint", tset.weight_paint, [], [], [], [], '    ', fp)
    writeDir(tset, ['image_paint', 'sculpt', 'vertex_paint', 'weight_paint'], '    ', fp)
    fp.write("  end ToolSettings\n")

def exportGameData(gdata, fp):
    fp.write("  GameData\n")
    writeDir(gdata, [], "    ", fp)
    fp.write("  end GameData\n")


#
#    exportNodeTree(tree, fp)
#    exportNode(node, fp)
#

def exportNodeTree(tree, fp):
    if tree == None:
        return
    print(tree)
    fp.write("  NodeTree %s\n" % tree.name.replace(' ', '_'))
    exportAnimationData(tree.animation_data, fp)
    for node in tree.nodes:
        exportNode(node, fp)
    writeDir(tree, ['nodes'], "  ", fp)
    fp.write("  end NodeTree\n")
    return

def exportNode(node, fp):
    fp.write("    Node %s\n" % node.name.replace(' ', '_'))
    loc = node.location
    fp.write("      location (%.3f, %3.f) ;\n" % (loc[0], loc[1]))
    fp.write("      Inputs\n")
    for inp in node.inputs:
        exportNodeSocket(inp, fp)
    fp.write("      end Inputs\n")
    fp.write("      Outputs\n")
    for outp in node.outputs:
        exportNodeSocket(outp, fp)
    fp.write("      end Outputs\n")
    fp.write("    end Node\n")
    return

def exportNodeSocket(socket, fp):
    print(dir(socket.rna_type))
    fp.write("        Socket %s %s\n" % (socket.name.replace(' ', '_'), socket.rna_type.name.replace(' ', '_')))
    writeDir(socket, [], "          ", fp)
    #fp.write("          default_value %s ; \n" %socket.default_value)
    #fp.write("          rna_type %s ; \n" %socket.rna_type)
    fp.write("        end Socket\n")
    return
    

#
#    exportObject(ob, fp):
# 

def exportObject(ob, fp):
    global hairFile

    fp.write("\n# ----------------------------- %s --------------------- # \n\n" % ob.type )
    if ob.type == "MESH":
        exportMesh(ob, fp)
    elif ob.type == "ARMATURE":
        exportArmature(ob, fp)
    elif ob.type == "EMPTY":
        pass
    elif ob.type == "CURVE":
        exportCurve(ob, fp)
    elif ob.type == "SURFACE":
        exportSurface(ob, fp)
    elif ob.type == 'LATTICE':
        exportLattice(ob, fp)
    elif ob.type == 'TEXT':
        exportTextCurve(ob, fp)
    elif not expMsk & M_Obj:
        return
    elif ob.type == 'LAMP':
        exportLamp(ob, fp)
    else:
        exportDefaultObject(ob,fp)

    if ob.data:
        datName = ob.data.name.replace(' ','_')
    else:
        datName = 'None'
    fp.write("\nObject %s %s %s\n" % (ob.name.replace(' ', '_'), ob.type, datName))

    writeArray('layers', ob.layers, "  ", 1, fp)

    for mod in ob.modifiers:
        exportModifier(mod, fp)

    if Quick:
        fp.write("end Object\n\n")
        return 
        
    for cns in ob.constraints:
        exportConstraint(cns, fp)

    for psys in ob.particle_systems:
        exportParticleSystem(psys, "  ", fp)

    exportAnimationData(ob.animation_data, fp)
    exportDefault("FieldSettings", ob.field, [], [], [], [], '  ', fp)
    writeDir(ob, 
        ['data','parent_vertices', 'mode', 'scene_users', 'children', 'pose', 'field',
        'material_slots', 'modifiers', 'constraints', 'layers', 'bound_box', 'group_users',
        'animation_visualisation', 'animation_data', 'particle_systems', 'active_particle_system',
        'active_shape_key', 'vertex_groups', 'active_vertex_group', 'materials'], "  ", fp)
    fp.write("end Object\n\n")
    return 

#
#    exportParticleSystem(psys, pad, fp):
#    exportParticleSettings(settings, psys, pad, fp):
#    exportParticle(par, nmax, pad, fp):
#

def exportParticleSystem(psys, pad, fp):
    name = psys.name.replace(' ', '_')
    fp.write("%sParticleSystem %s %s \n" % (pad,name, psys.settings.type))
    createdLocal['ParticleSystem'].append(name)
    exportParticleSettings(psys.settings, psys, pad, fp)
    writeDir(psys,
        ['settings', 'child_particles', 'particles', 'editable', 'edited', 'global_hair', 'multiple_caches'], 
        pad+"  ", fp)
    if psys.edited:
        exportParticles(psys.particles,  psys.settings.amount, pad+"  ", fp)
    fp.write("%send ParticleSystem\n" % pad)

def exportParticleSettings(settings, psys, pad, fp):
    fp.write("%ssettings Struct ParticleSettings %s \n" % (pad, settings.name.replace(' ','_')))
    prio = ['amount', 'hair_step', 'rendered_child_nbr', 'child_radius', 'child_random_size']
    writePrio(settings, prio, pad+"  ", fp)
    writeDir(settings, prio, pad+"  ", fp)
    fp.write("%send Struct\n" % pad)

def exportParticles(particles, nmax, pad, fp):
    fp.write("%sParticles\n" % pad)
    n = 0
    prio = ['location']
    for par in particles:
        if n < nmax:
            fp.write("%s  Particle \n" % pad)
            for h in par.hair:
                fp.write("%s    h " % pad)
                writeTuple(h.location, fp)
                fp.write(" %d %.3f ;\n" % (h.time, h.weight))
            writePrio(par, prio, pad+"    ", fp)
            fp.write("%s  end Particle\n" % pad)
            n += 1
    writeDir(particles[0], prio+['hair'], pad+"  ", fp)
    fp.write("%send Particles\n" % pad)

    
#
#    exportMesh(ob, fp):
#

def exportMesh(ob, fp):
    me = ob.data
    meName = me.name.replace(' ', '_')
    obName = ob.name.replace(' ', '_')
    if verbosity > 0:
        print( "Saving mesh "+meName )

    fp.write("Mesh %s %s \n" % (meName, obName))

    if me.vertices:
        fp.write("  Verts\n")
        for v in me.vertices:
            fp.write("    v %.3f %.3f %.3f ;\n" %(v.co[0], v.co[1], v.co[2]))
        v = me.vertices[0]
        #writeDir(v, ['co', 'index', 'normal'], "      ", fp)
        fp.write("  end Verts\n")

    if me.polygons:
        fp.write("  Faces\n")
        for f in me.polygons:
            fp.write("    f ")
            for v in f.vertices:
                fp.write("%d " % v)
            fp.write(";\n")
        if len(me.materials) <= 1:
            f = me.polygons[0]
            fp.write("    ftall %d %d ;\n" % (f.material_index, f.use_smooth))
        else:
            """
            for f in me.polygons:
                fp.write("    ft %d %d ;\n" % (f.material_index, f.use_smooth))
            """
            mi = -1
            us = -1
            n = 0
            for f in me.polygons:
                if (f.material_index == mi) and (f.use_smooth == us):
                    n += 1
                else:
                    if n > 1:
                        fp.write("    ftn %d %d %d ;\n" % (n, mi, us))
                    elif n > 0:
                        fp.write("    ft %d %d ;\n" % (mi, us))
                    mi = f.material_index
                    us = f.use_smooth
                    n = 1
            if n > 1:
                fp.write("    ftn %d %d %d ;\n" % (n, mi, us))
            elif n > 0:
                fp.write("    ft %d %d ;\n" % (mi, us))

        fp.write("  end Faces\n")
    elif me.edges:
        fp.write("  Edges\n")
        for e in me.edges:
            fp.write("    e %d %d ;\n" % (e.vertices[0], e.vertices[1]))
        e = me.edges[0]
        #writeDir(e, ['vertices'], "      ", fp)
        fp.write("  end Edges\n")

    if Quick:
        fp.write("end Mesh\n")
        return # exportMesh

    for uvtex in me.uv_textures:
        uvtexName = uvtex.name.replace(' ','_')
        fp.write("  MeshTextureFaceLayer %s\n" % uvtexName)
        fp.write("    Data \n")
        for data in uvtex.data.values():
            v = data.uv_raw
            fp.write("      vt %.3f %.3f %.3f %.3f %.3f %.3f %.3f %.3f ;\n" % 
                (v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7]))
        writeDir(uvtex.data[0], 
            ['uv1', 'uv2', 'uv3', 'uv4', 'uv', 'uv_raw', 'uv_pinned', 'uv_selected'], "      ", fp)
        fp.write("    end Data\n")
        writeDir(uvtex, ['data'], "    ", fp)
        createdLocal['MeshTextureFaceLayer'].append(uvtexName)
        fp.write("  end MeshTextureFaceLayer\n")
        
    for vcol in me.vertex_colors:
        vcolName = vcol.name.replace(' ','_')
        fp.write("  MeshColorLayer %s\n" % vcolName)
        if Optimize < 2:
            fp.write("    Data \n")
            for data in vcol.data.values():
                fp.write("      cv ")
                writeTuple(data.color1, fp)
                writeTuple(data.color2, fp)
                writeTuple(data.color3, fp)
                writeTuple(data.color4, fp)
                fp.write(" ;\n")
            fp.write("    end Data\n")
        writeDir(vcol, ['data'], "    ", fp)
        createdLocal['MeshColorLayer'].append(vcolName)
        fp.write("  end MeshColorLayer\n")

    """
    for v in me.sticky:
        fp.write("  sticky %.3f %.3f\n" % (v.co[0], v.co[1]))
    """    

    for mat in me.materials:
        if mat:
            fp.write("  Material %s ;\n" % mat.name.replace(" ", "_"))
    
    exportVertexGroups(ob, me, 'All', fp)

    if me.shape_keys:
        global FacialKey, BodyKey
        if expMsk & M_Shape:
            exportShapeKeys(ob, FacialKey, "True", fp)
            exportShapeKeys(ob, BodyKey, "True", fp)

    if me.animation_data:         
        exportAnimationData(me.animation_data, fp)

    #writePrio(me, ['vertex_colors'], "  ", fp)

    exclude = ['edge_face_count', 'edge_face_count_dict', 'edge_keys', 'edges', 'faces', 'vertices', 'texspace_loc', 
        'texspace_size', 'active_uv_texture', 'active_vertex_color', 'uv_texture_clone', 'uv_texture_stencil',
        'float_layers', 'int_layers', 'string_layers', 'shape_keys', 'uv_textures', 'vertex_colors', 'materials', 
        'total_face_sel', 'total_edge_sel', 'total_vert_sel']
    writeDir(me, exclude, "  ", fp)
    fp.write("end Mesh\n")
    return # exportMesh

CommonVertGroups = [
    'Eye_L', 'Eye_R', 'Gums', 'Head', 'Jaw', 'Left', 'LoLid_L', 'LoLid_R', 'Middle', 'Right',
    'ToungeBase', 'ToungeTip', 'UpLid_L', 'UpLid_R', 'Scalp']

FaceVertGroups = [
    'UpLipMid', 'UpLipMid_L', 'UpLipMid_R', 'MouthCorner_L', 'MouthCorner_R', 'LoLipMid_L', 'LoLipMid_R', 'LoLipMid', 
    'NoseTip', 'BrowMid', 'BrowMid_L', 'BrowMid_R']

ToeVertGroups = [
    'Toe-1-1_L', 'Toe-1-1_R', 'Toe-1-2_L', 'Toe-1-2_R', 
    'Toe-2-1_L', 'Toe-2-1_R', 'Toe-2-2_L', 'Toe-2-2_R', 'Toe-2-3_L', 'Toe-2-3_R', 
    'Toe-3-1_L', 'Toe-3-1_R', 'Toe-3-2_L', 'Toe-3-2_R', 'Toe-3-3_L', 'Toe-3-3_R', 
    'Toe-4-1_L', 'Toe-4-1_R', 'Toe-4-2_L', 'Toe-4-2_R', 'Toe-4-3_L', 'Toe-4-3_R', 
    'Toe-5-1_L', 'Toe-5-1_R', 'Toe-5-2_L', 'Toe-5-2_R', 'Toe-5-3_L', 'Toe-5-3_R']

def exportVertexGroups(ob, me, typ, fp):
    toeLeft = {}
    toeRight = {}
    for vg in ob.vertex_groups:
        index = vg.index
        vgName = vg.name.replace(' ','_')

        doExport = False
        doToe = False
        if typ == 'Common':
            if vgName in CommonVertGroups:
                doExport = True
        elif typ == 'Face':
            if vgName in FaceVertGroups:
                doExport = True
        elif typ == 'Toe':
            if vgName in ToeVertGroups:
                doExport = True
                doToe = True
                if vgName[-1] == 'L':
                    toeDict = toeLeft
                elif vgName[-1] == 'R':
                    toeDict = toeRight
                else:
                    raise NameError("Toe %s" % vgName)
        elif typ == 'Rig':
            if vgName not in CommonVertGroups+ToeVertGroups:
                doExport = True
        elif typ == 'All':
            doExport = True

        if doExport:
            fp.write("  VertexGroup %s\n" % (vgName))
            for v in me.vertices:
                for grp in v.groups:
                    if grp.group == index and grp.weight > 0.005:
                        fp.write("    wv %d %.3f ;\n" % (v.index, grp.weight))
                        if doToe:
                            addToeWeight(toeDict, v.index, grp.weight)
                            
            fp.write("  end VertexGroup\n")
            createdLocal['VertexGroup'].append(vgName)

    return (toeLeft, toeRight)

def addToeWeight(toeDict, v, w):
    try:
        w1 = toeDict[v]
    except:
        w1 = 0
    if w > w1:
        toeDict[v] = w
    return

def dumpVertexGroup(toeDict, vgName, fp):
    fp.write("  VertexGroup %s\n" % (vgName))
    for (v,w) in toeDict.items():
        fp.write("    wv %d %.3f ;\n" % (v,w))
    fp.write("  end VertexGroup\n")
    

#
#    exportShapeKeys(ob, keyList, toggle, fp):
#

FacialKey = {
    "Basis"    : (None, 0, 1),

    "BrowsDown" : ("LR", 0, 1),
    "BrowsMidDown" : ("Sym", 0, 1),
    "BrowsMidUp" : ("Sym", 0, 1),
    "BrowsOutUp" : ("LR", 0, 1),
    #"BrowsSqueeze" : ("Sym", 0, 1),
    "CheekUp" : ("LR", 0, 1),
    "Frown" : ("LR", 0, 1),
    "UpLidDown" : ("LR", 0, 1),
    "LoLidUp" : ("LR", 0, 1),
    "Narrow" : ("LR", 0, 1),
    "Smile" : ("LR", 0, 1),
    "Sneer" : ("LR", 0, 1),
    #"Squint" : ("LR", 0, 1),
    "TongueOut" : ("Sym", 0, 1),
    "ToungeUp" : ("Sym", 0, 1),
    "ToungeLeft" : ("Sym", 0, 1),
    "ToungeRight" : ("Sym", 0, 1),
    "UpLipUp" : ("LR", 0, 1),
    "LoLipDown" : ("LR", 0, 1),
    #"MouthOpen" : ("Sym", 0, 1),
    "UpLipDown" : ("LR", 0, 1),
    "LoLipUp" : ("LR", 0, 1),

    "MouthOpen" : ("Sym", 0, 2.0),
    "MouthCornerDepth" : ("LR", -1.0, 2.0),
    "LipsOut" : ("HJ", 0, 2.0),
    "LipsIn" : ("HJ", 0, 2.0),
    "MouthHeight" : ("LR", -1.0, 2.0),
    "LipsMidHeight" : ("HJ", -1.0, 2.0),
    "MouthCornerHeight" : ("LRHJ", -1.0, 2.0),
    "MouthWidth" : ("LR", 0, 1.0),
    "MouthNarrow" : ("LR", 0, 1.0),
    "LipsPart" : ("Sym", -1.0, 2.0),
    "TongueHeight" : ("Sym", -1.0, 2.0),
    "TongueDepth" : ("Sym", -1.0, 2.0),
    "TongueWidth" : ("Sym", 0, 1.0),
    "TongueBackHeight" : ("Sym", 0, 1.0),
    "BrowsMidHeight" : ("Sym", -1.0, 2.0),
    "BrowsSqueeze" : ("Sym", 0.0, 2.0),
    "BrowsOuterHeight" : ("LR", -1.0, 2.0),
    "NoseWrinkle" : ("Sym", 0.0, 2.0),
    "CheekFlex" : ("LR", -0.0, 2.0),
    "Squint" : ("LR", 0, 2.0),
    "CheekBalloon" : ("Sym", -1, 2.0),
}

BodyKey = {
    "BendElbowForward" : ("LR", 0, 1),
    "BendHeadForward" : ("Sym", 0, 1),
    "BendLegForward" : ("LR", 0, 1),
    "BendLegBack" : ("LR", 0, 1.5),
    "BendLegOut" : ("LR", 0, 1.5),
    "BendKneeBack" : ("LR", 0, 1),
    "BendArmDown" : ("LR", 0, 1),
    "BendArmUp" : ("LR", 0, 1),
    "BicepFlex" : ("LR", 0, 1),
    "BreatheIn" : ("Sym", 0, 1.5),
}

def findGroup(ob, name):
    for grp in ob.vertex_groups:
        if grp.name == name:
            return grp.index
    raise NameError("%s has no vertex group %s" % (ob, name))

def exportShapeKeys(ob, keyList, toggle, fp):
    me = ob.data
    skeys = me.shape_keys
    fp.write("ShapeKeys\n")
    try:
        headgrp = findGroup(ob, 'Head')
        jawgrp = findGroup(ob, 'Jaw')
    except:
        headgrp = None
        jawgrp = None
    for skey in skeys.keys:
        skeyName = skey.name.replace(' ','_')    
        try:
            (lr, slidermin, slidermax) = keyList[skeyName]
        except:
            lr = None

        if lr:
            if lr == 'LRHJ':
                exportShapeKey('Up'+skeyName, me.vertices, 'LR', skey, toggle, headgrp, slidermin, slidermax, fp)
                exportShapeKey('Lo'+skeyName, me.vertices, 'LR', skey, toggle, jawgrp, slidermin, slidermax, fp)
            elif lr == 'HJ':
                exportShapeKey('Up'+skeyName, me.vertices, 'Sym', skey, toggle, headgrp, slidermin, slidermax, fp)
                exportShapeKey('Lo'+skeyName, me.vertices, 'Sym', skey, toggle, jawgrp, slidermin, slidermax, fp)
            else:
                exportShapeKey(skeyName, me.vertices, lr, skey, toggle, -1, slidermin, slidermax, fp)
        else:
            fp.write("  ShapeKey %s %s %s\n" % (skeyName, "Sym", toggle))
            writeDir(skey, ['data', 'relative_key', 'frame'], "    ", fp)
            fp.write("  end ShapeKey\n")

    if skeys.animation_data:         
        exportAnimationData(skeys.animation_data, fp)
    fp.write("end ShapeKeys\n")
    return

def exportShapeKey(skeyName, verts, lr, skey, toggle, vgroup, slidermin, slidermax, fp):
    print(skeyName)
    fp.write("  ShapeKey %s %s %s\n" % (skeyName, lr, toggle))
    #writeDir(skey, ['data', 'relative_key', 'frame'], "    ", fp)
    fp.write("    slider_min %s ;\n" % slidermin)
    fp.write("    slider_max %s ;\n" % slidermax)
    for (n,pt) in enumerate(skey.data):
        vert = verts[n]
        if (expMsk & M_UnselShape or vert.select):
            dv = pt.co - vert.co
            if vgroup >= 0:
                w = 0
                for grp in vert.groups:
                    if grp.group == vgroup:
                        w = grp.weight
                dv *= w
            if dv.length > Epsilon:
                fp.write("    sv %d %.4f %.4f %.4f ;\n" %(n, dv[0], dv[1], dv[2]))
    fp.write("  end ShapeKey\n")
    print(skey)
    createdLocal['ShapeKey'].append(skeyName)
    return

#
#    exportArmature(ob, fp):
#    exportBone(fp, n, bone):
#

def exportArmature(ob, fp):
    global createdLocal
    amt = ob.data
    amtName = amt.name.replace(' ','_')
    obName = ob.name.replace(' ','_')
    
    if verbosity > 0:
        print( "Saving amt "+amtName +"!!!" )

    bpy.context.scene.objects.active = ob
    fp.write("Armature %s %s " % (amtName, obName))

    bpy.ops.object.mode_set(mode='EDIT')
    bones = amt.edit_bones.values()
    fp.write("  Normal \n")
    
    print(obName, amt.edit_bones.keys(), amt.edit_bones.values(), bones, bpy.context.object)
    for b in bones:
        print("  ", obName, b.name, b.parent)
        if b.parent == None:
            exportBone(fp, b)
            fp.write("\n")


    # prio = ['animation_data']
    prio = []
    writePrio(amt, prio, "  ", fp)
    writeDir(amt, prio+['animation_data', 'edit_bones', 'bones'], "  ", fp)
    fp.write("end Armature\n")
    return # exportArmature


def writeBone(bone, fp):
    fp.write("  Bone %s True\n" % (bone.name.replace(' ','_')))
    x = bone.head
    fp.write("    head %.3f %.3f %.3f ; \n" % (x[0], x[1], x[2]))
    x = bone.tail
    fp.write("    tail %.3f %.3f %.3f ; \n" % (x[0], x[1], x[2]))
    writePrio(bone, ['roll'], "    ", fp)
    return

def exportBone(fp, bone):
    flags = 0
    writeBone(bone, fp)

    if bone.parent:
        fp.write("    parent Refer Bone %s ;\n" % (bone.parent.name.replace(' ','_')))

    exclude = ['head', 'tail', 'parent', 'head_local', 'tail_local', 'matrix_local', 'children']
    exclude += ['matrix',  'envelope_distance', 'envelope_weight', 'head_radius', 'tail_radius',
        'selected', 'selected_head', 'selected_tail']
    writeDir(bone, exclude, "    ", fp)

    fp.write("  end Bone\n\n")
    if bone.children:
        for child in bone.children:
            exportBone(fp, child)
    return

#
#
#    exportPose(ob, fp):
#    exportBoneGroup(bg, fp):
#    exportPoseBone(fp, pb):
#

def exportPose(ob, fp):
    global createdLocal
    obName = ob.name.replace(' ','_')
    
    if verbosity > 0:
        print( "Saving pose "+obName )

    bpy.context.scene.objects.active = ob
    bpy.ops.object.mode_set(mode='POSE')
    fp.write("\nPose %s True \n" % (obName))    
    createdLocal['BoneGroup'] = []
    for bg in ob.pose.bone_groups.values():
        exportBoneGroup(fp, bg)
    for pb in ob.pose.bones.values():
        exportPoseBone(fp, pb)
    writeDir(ob.pose, ['bones', 'bone_groups'], "  ", fp)
    fp.write("end Pose\n")
    bpy.ops.object.mode_set(mode='OBJECT')
    return # exportPose

def exportPoseBone(fp, pb):
    fp.write("\n  Posebone %s True\n" % (pb.name.replace(' ', '_')))
    for cns in pb.constraints:
        exportConstraint(cns, fp)
    #writeArray('lock_ik', [pb.lock_ik_x, pb.lock_ik_y, pb.lock_ik_z], "    ", 1, fp)
    #writeArray('use_ik_limit', [pb.use_ik_limit_x, pb.use_ik_limit_y, pb.use_ik_limit_z], "    ", 1, fp)
    writeArray('ik_max', [pb.ik_max_x, pb.ik_max_y, pb.ik_max_z], "    ", 1, fp)
    writeArray('ik_min', [pb.ik_min_x, pb.ik_min_y, pb.ik_min_z], "    ", 1, fp)
    writeArray('ik_stiffness', [pb.ik_stiffness_x, pb.ik_stiffness_y, pb.ik_stiffness_z], "    ", 1, fp)
    exclude = ['constraints', 
        #'lock_ik_x', 'lock_ik_y', 'lock_ik_z', 
        #'use_ik_limit_x', 'use_ik_limit_y', 'use_ik_limit_z', 
        'ik_max_x', 'ik_max_y', 'ik_max_z', 
        'ik_min_x', 'ik_min_y', 'ik_min_z', 
        'ik_stiffness_x', 'ik_stiffness_y', 'ik_stiffness_z',
        'custom_shape_transform', 'original_length', 'bone_group_index', 
        'matrix_basis', 'matrix_channel',
        'parent', 'children', 'bone', 'child', 'head', 'tail', 'is_in_ik_chain']
    exclude += ['channel_matrix', 'matrix', 'rotation_axis_angle', 'rotation_euler', 'rotation_mode',
        'rotation_quaternion', 'scale', 'selected']
    writeDir(pb, exclude, "    ", fp)    
    fp.write("  end Posebone\n")
    return


def exportBoneGroup(fp, bg):
    global createdLocal
    name = bg.name.replace(' ', '_')
    fp.write("    BoneGroup %s\n" % (name))
    writeDir(bg, [], "      ", fp)    
    fp.write("    end BoneGroup\n")
    createdLocal['BoneGroup'].append(name)
    return

#
#    exportConstraint(cns, fp):
#

def exportConstraint(cns, fp):
    try:
        name = cns.name.replace(' ', '_')
    except:
        return
    fp.write("    Constraint %s %s True\n" % (name, cns.type))
    writePrio(cns, ['target'], "      ", fp)

    try:
        writeArray('invert', [cns.invert_x, cns.invert_y, cns.invert_z], "      ", 2, fp)
    except:
        pass
    try:
        writeArray('use', [cns.use_x, cns.use_y, cns.use_z], "      ", 2, fp)
    except:
        pass
    try:
        writeArray('pos_lock', [cns.pos_lock_x, cns.pos_lock_y, cns.pos_lock_z], "      ", 2, fp)
    except:
        pass
    try:
        writeArray('rot_lock', [cns.rot_lock_x, cns.rot_lock_y, cns.rot_lock_z], "      ", 2, fp)
    except:
        pass

    exclude = ['invert_x', 'invert_y', 'invert_z', 'use_x', 'use_y', 'use_z',
        'head_tail',
        'pos_lock_x', 'pos_lock_y', 'pos_lock_z', 'rot_lock_x', 'rot_lock_y', 'rot_lock_z', 
        'error_location', 'error_rotation', 'is_valid',
        'disabled', 'lin_error', 'rot_error', 'target', 'type']
    exclude += ['distance']
    writeDir(cns, exclude, "      ", fp)    
    fp.write("    end Constraint\n")
    return

#
#    exportModifier(mod, fp):
#

def exportModifier(mod, fp):
    name = mod.name.replace(' ', '_')
    fp.write("    Modifier %s %s\n" % (name, mod.type))
    writeDir(mod, ['is_bound', 'is_external', 'total_levels'], "      ", fp)    
    fp.write("    end Modifier\n")
    return

#
#    exportDefaultObject(ob,fp):
#

def exportDefaultObject(ob,fp):
    data = ob.data
    obtype = ob.type.capitalize()

    fp.write("%s %s \n" % (obtype, data.name.replace(' ', '_')))
    writeDir(data, [], "  ", fp)
    fp.write("end %s\n" % obtype)
    return

#
#    exportLamp(ob, fp):
#

def exportLamp(ob, fp):
    la = ob.data
    fp.write("Lamp %s %s\n" % (la.name.replace(' ', '_'), ob.name.replace(' ', '_') ))
    writeDir(la, ['falloff_curve'], "  ", fp)
    exportFalloffCurve(la.falloff_curve, fp)
    fp.write("end Lamp\n")

def exportFalloffCurve(focu, fp):
    fp.write("  FalloffCurve\n")
    writeDir(focu, ['curves'], "    ", fp)
    exportDefault('CurveMap', focu.curves, [], [], [], [('CurveMapPoint', focu.curves.points)], '    ', fp)
    fp.write("  end FalloffCurve\n")

#
#
#
#

def exportTextCurve(ob, fp):
    txt = ob.data
    fp.write("TextCurve %s %s\n" % (txt.name.replace(' ', '_'), ob.name.replace(' ', '_')))
    writeDir(txt, ['splines', 'points', 'body_format', 'edit_format', 'font', 'textboxes'], "  ", fp)
    for bfmt in txt.body_format:
        exportDefault('BodyFormat', bfmt, [], [], [], [], '  ', fp)
    exportDefault('EditFormat', txt.edit_format, [], [], [], [], '  ', fp)
    exportDefault('Font', txt.font, [], [], [], [], '  ', fp)
    for tbox in txt.textboxes:
        exportDefault('TextBox', tbox, [], [], [], [], '  ', fp)
    for spline in txt.splines:
        exportSpline(spline, "  ", fp)
    fp.write("end TextCurve\n")

#
#    exportCurve(ob, fp):
#    exportSurface(ob, fp):
#    exportSpline(spl, pad, fp):
#    exportBezierPoint(bz, pad, fp):
#

def exportCurve(ob, fp):
    cu = ob.data
    cuname = cu.name.replace(' ', '_') 
    obname = ob.name.replace(' ', '_') 
    fp.write("Curve %s %s\n" % (cuname, obname))
    writeDir(cu, ['splines', 'points'], "  ", fp)
    for spline in cu.splines:
        exportSpline(spline, "  ", fp)
    fp.write("end Curve\n")

def exportSurface(ob, fp):
    su = ob.data
    suname = su.name.replace(' ', '_') 
    obname = ob.name.replace(' ', '_') 
    fp.write("Surface %s %s\n" % (suname, obname))
    writeDir(su, ['splines', 'points'], "  ", fp)
    for spline in su.splines:
        exportSpline(spline, "  ", fp)
    fp.write("end Surface\n")
    

def exportSpline(spline, pad, fp):
    fp.write("%sSpline %s %d %d\n" % (pad, spline.type, spline.point_count_u, spline.point_count_v))
    writeDir(spline, ['bezier_points', 'character_index', 'points', 'point_count_u', 'point_count_v'], "    ", fp)
    for bz in spline.bezier_points:
        fp.write("%s  bz " % pad)
        writeTuple(bz.co, fp)
        writeTuple(bz.handle1, fp)
        fp.write("%s " % bz.handle1_type)
        writeTuple(bz.handle2, fp)
        fp.write("%s ;\n" % bz.handle2_type)
    for pt in spline.points:
        fp.write("%s  pt " % pad)
        writeTuple(pt.co, fp)
        fp.write(" ;\n")
    fp.write("%send Spline\n" % pad)

#
#    exportLattice(ob, fp):
#

def exportLattice(ob, fp):
    lat = ob.data
    latName = lat.name.replace(' ', '_') 
    obName = ob.name.replace(' ', '_') 
    fp.write("Lattice %s %s\n" % (latName, obName))
    writeDir(lat, ['points'], "  ", fp)
    fp.write("  Points\n")
    for pt in lat.points:
        x = pt.co
        y = pt.co_deform
        fp.write("    pt (%.3f,%.3f,%.3f) (%.3f,%.3f,%.3f) ;\n" % (x[0], x[1], x[2], y[0], y[1], y[2]))
    fp.write("  end Points\n")
    fp.write("end Lattice\n")

#
#    exportGroup(grp, fp):
#

def exportGroup(grp, fp):
    name = grp.name.replace(' ', '_') 
    fp.write("Group %s\n" % (name))
    fp.write("  Objects\n")
    for ob in grp.objects:
        fp.write("    ob %s ;\n" % ob.name.replace(' ','_'))
    fp.write("  end Objects\n")
    writeDir(grp, ['objects'], "  ", fp)
    fp.write("end Group\n")


#
#    writeHeader(fp):
#    writeMaterials(fp):
#    writeAnimations(fp):
#    writeArmatures(fp):
#    writeMeshes(fp):
#    writeTools(fp):
#    writeScenes(fp):
#

def selectStatus(ob):
    if expMsk & M_Sel:
        return ob.select
    return True

def writeHeader(fp):
    fp.write(
"# Blender 2.5 exported MHX \n" +
"MHX %d %d %d ;\n" % (MAJOR_VERSION, MINOR_VERSION, SUB_VERSION) +
"#if Blender24\n" +
"  error 'This file can only be read with Blender 2.5' ;\n" +
"#endif\n")
    return

def writeMaterials(fp):
    if bpy.data.images:
        fp.write("\n# --------------- Images ----------------------------- # \n \n")
        for img in bpy.data.images:
            initLocalData()
            exportImage(img, fp)

    if bpy.data.textures:
        fp.write("\n# --------------- Textures ----------------------------- # \n \n")            
        for tex in bpy.data.textures:
            initLocalData()
            exportTexture(tex, fp)
            
    if bpy.data.materials:
        fp.write("\n# --------------- Materials ----------------------------- # \n \n")
        for mat in bpy.data.materials:
            print(mat)
            initLocalData()
            exportMaterial(mat, fp)
    return

def writeAnimations(fp):
    if bpy.data.actions:
        fp.write("\n# --------------- Actions ----------------------------- # \n \n")
        for act in bpy.data.actions:
            initLocalData()
            exportAction(act, fp)
    return

def writeArmatures(fp):
    if bpy.data.objects:        
        fp.write("\n# --------------- Armatures ----------------------------- # \n \n")
        for ob in bpy.data.objects:
            if ob.type == 'ARMATURE' and selectStatus(ob):
                initLocalData()
                exportObject(ob, fp)
    return

def writePoses(fp):
    if bpy.data.objects:        
        fp.write("\n# --------------- Pose ----------------------------- # \n \n")
        for ob in bpy.data.objects:
            if ob.type == 'ARMATURE' and selectStatus(ob):
                initLocalData()
                exportPose(ob, fp)
    return

def writeMeshes(fp):
    if bpy.data.objects:        
        for ob in bpy.data.objects:
            if ob.type != 'ARMATURE' and selectStatus(ob):
                initLocalData()
                exportObject(ob, fp)
    if bpy.data.groups:
        fp.write("\n# ---------------- Groups -------------------------------- # \n \n")
        for grp in bpy.data.groups:
            initLocalData()
            exportGroup(grp, fp)

    return

def writeHumanMesh(fp):
    try:
        ob = bpy.data.objects['Human']
    except:
        return
    initLocalData()
    exportObject(ob, fp)
    return

def writeTools(fp):
    if bpy.data.brushes:
        print(list(bpy.data.brushes))
        for brush in bpy.data.brushes:
            initLocalData()
            exportDefault('Brush', brush, [], [], [], [], '', fp)

    if bpy.data.libraries:        
        fp.write("\n# --------------- Libraries ----------------------------- # \n \n")
        print(list(bpy.data.libraries))
        for lib in bpy.data.libraries:
            initLocalData()
            exportDefault("Library", lib, [], [], [], [], '', fp)
    return

def writeNodeTrees(fp):        
    print("NT", list(bpy.data.node_groups))
    if bpy.data.node_groups:        
        fp.write("\n# --------------- Node trees ----------------------------- # \n \n")
        for ngrp in bpy.data.node_groups:
            print("Grp", ngrp)
            initLocalData()
            exportDefault("NodeGroup", ngrp, [], [], [], [], '', fp)


def writeScenes(fp):
    if bpy.data.worlds:
        fp.write("\n# --------------- Worlds ----------------------------- # \n \n")
        for world in bpy.data.worlds:
            initLocalData()
            exportWorld(world, fp)

    if bpy.data.scenes:
        fp.write("\n# --------------- Scenes ----------------------------- # \n \n")
        for scn in bpy.data.scenes:
            initLocalData()
            exportScene(scn, fp)
    return

#
#    writeMhxFile(fileName):
#

def writeMhxFile(fileName, msk):
    global expMsk
    expMsk = msk
    print("expMsk %x %x %x" %( expMsk, M_Mat, expMsk&M_Mat))
    n = len(fileName)
    if fileName[n-3:] != "mhx":
        raise NameError("Not a mhx file: " + fileName)
    fp = open(fileName, "w")
    writeHeader(fp)
    if expMsk & M_Nodes:
        writeNodeTrees(fp)
    if expMsk & M_Mat:
        writeMaterials(fp)
    if expMsk & M_Amt:
        writeArmatures(fp)
    if expMsk & M_Anim:
        writeAnimations(fp)
    if expMsk & M_Geo:
        writeHumanMesh(fp)
        writeMeshes(fp)
    if expMsk & M_Amt:
        writePoses(fp)
    if expMsk & M_Tool:
        writeTools(fp)
    if expMsk & M_Scn:
        writeScenes(fp)
    mhxClose(fp)
    return

#
#    MakeHuman directory
#

MHXDir = '/home/thomas/svn/makehuman/data/templates/'
TrashDir = '/home/thomas/mhx5/trash/'

# MHXDir = 'C:/home/svn/data/templates/'
# TrashDir = 'C:/home/thomas/mhx5/trash/'

def mhxOpen(msk, name):
    if expMsk & msk:
        fdir = MHXDir
    else:
        fdir = TrashDir
    fileName = "%s%s" % (fdir, name)
    print( "Writing MHX file " + fileName )
    return open(fileName, 'w')

def mhxClose(fp):    
    print("%s written" % fp.name)
    fp.close()
    return

#
#    User interface
#

DEBUG= False
from bpy.props import *
from bpy_extras.io_utils import ImportHelper

mask = M_Geo+M_VGroup+M_Shape

class ExportMhx(bpy.types.Operator, ImportHelper):
    '''Export to MHX file format (.mhx)'''
    bl_idname = "export.makehuman_mhx"
    bl_description = 'Export to MHX file format (.mhx)'
    bl_label = "Export MHX"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    filename_ext = ".mhx"
    filter_glob = StringProperty(default="*.mhx", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="File path for the exported MHX file", maxlen= 1024, default= "")

    sel = BoolProperty(name="Selected only", description="Only selected objects", default=mask&M_Sel)
    #xall = BoolProperty(name="Everything", description="Include everything", default=mask&M_All)
    mat = BoolProperty(name="Materials", description="Include materials", default=mask&M_Mat)
    geo = BoolProperty(name="Geometry", description="Include geometry", default=mask&M_Geo)
    amt = BoolProperty(name="Armatures", description="Include armature", default=mask&M_Amt)
    anim = BoolProperty(name="Animations", description="Include animations and drivers", default=mask&M_Anim)
    shape = BoolProperty(name="Shapes", description="Include shapes", default=mask&M_Shape)
    unselshape = BoolProperty(name="Unselected shapes", description="Include unselected verts in shapes", default=mask&M_UnselShape)
    vgroup = BoolProperty(name="Vertex groups", description="Include vertex groups", default=mask&M_VGroup)
    obj = BoolProperty(name="Objects", description="Include other objects", default=mask&M_Obj)

    def execute(self, context):
        global toggle
        O_Sel = M_Sel if self.properties.sel else 0
        #O_All = M_All if self.properties.xall else 0
        O_Mat = M_Mat if self.properties.mat else 0
        O_Geo = M_Geo if self.properties.geo else 0
        O_Amt = M_Amt if self.properties.amt else 0
        O_Anim = M_Anim if self.properties.anim else 0
        O_Shape = M_Shape if self.properties.shape else 0
        O_UnselShape = M_UnselShape if self.properties.unselshape else 0
        O_VGroup = M_VGroup if self.properties.vgroup else 0
        O_Obj = M_Obj if self.properties.obj else 0

        mask = O_Sel | O_Mat | O_Geo | O_Amt | O_Anim | O_Shape | O_UnselShape | O_VGroup | O_Obj
        
        writeMhxFile(self.properties.filepath, mask)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func(self, context):
    self.layout.operator(ExportMhx.bl_idname, text="MakeHuman (.mhx)...")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func)
 
def unregister():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
    register()

#
#    Testing
#
"""
hairFile = "particles25.mhx"
theRig = "classic"
#theRig = "gobo"
writeMhxFile('/home/thomas/myblends/test.mhx', M_Mat+M_Geo+M_Amt+M_VGroup+M_Anim+M_Shape+M_Obj+M_Nodes+M_Scn)
#writeMhxFile('/home/thomas/myblends/test.mhx', M_All)
#writeMhxFile('/home/thomas/myblends/sintel/simple2.mhx', M_Amt+M_Anim)
"""

