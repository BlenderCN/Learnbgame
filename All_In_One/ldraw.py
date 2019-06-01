bl_info = {
    'name': "Import LDraw model format",
    'author': "Spencer Alves (impiaaa)",
    'version': (1, 0),
    'blender': (2, 70, 0),
    'location': "File > Import > Import LDraw",
    'description': "This script imports LDraw model files.",
    # used for warning icon and text in addons panel
    'warning': "Some parts may be distorted",
    "category": "Learnbgame",
}

"""\
This script imports LDraw model files.

From the LDraw website:
"LDraw(tm) is an open standard for LEGO CAD programs that allow the user to
create virtual LEGO models and scenes. You can use it to document models you
have physically built, create building instructions just like LEGO, render 3D
photo realistic images of your virtual models and even make animations. The
possibilities are endless. Unlike real LEGO bricks where you are limited by the
number of parts and colors, in LDraw nothing is impossible."

Usage:
    Execute this script from the "File->Import" menu and choose your model
    file. Make sure that the LDraw dir field is set to your LDraw install
    directory, chose the options you'd like on the left (more help in the
    tooltips), and click Import.

Changelog:
    1.0
        Initial re-release for Blender 2.60
"""

import bpy, bpy.props, bpy.utils, mathutils, bmesh
import sys, os, math, time, warnings

DEFAULTMAT = mathutils.Matrix.Scale(0.025, 4)
DEFAULTMAT *= mathutils.Matrix.Rotation(math.pi/-2.0, 4, 'X') # -90 degree rotation
THRESHOLD = 0.0001
CW = 0
CCW = 1
MAXPATH = 1024
LOWRES = False

### UTILITY FUNCTIONS ###

def hex2rgb(hexColor):
    if hexColor[0] == '#':
        hexColor = hexColor[1:]
    return int(hexColor[0:2], 16)/255.0, int(hexColor[2:4], 16)/255.0, int(hexColor[4:6], 16)/255.0

def parseColorLine(ls, keys, flags=set()):
    d = {}
    s = set()
    for idx, val in enumerate(ls):
        if val in keys and idx+1 < len(ls):
            d[val] = ls[idx+1]
        elif val in flags:
            s.add(val)
    return d, s

def copyAndApplyMaterial(o, mat):
    # Copies and object AND all of its children. Links children to the current
    # scene, but not the parent.
    # Also recursively set mat to the 0 material slot.
    p = o.copy()
    if mat is not None:
        if len(p.material_slots) > 0:
            p.material_slots[0].material = mat
        else:
            p.active_material_index = 0
            p.active_material = mat
            p.material_slots[0].link = 'OBJECT'
            p.active_material = mat
    # This loop is REALLY SLOW for large scenes, since .children iterates through
    # every object in the scene
    for c in o.children:
        if c.ldrawInheritsColor:
            d = copyAndApplyMaterial(c, mat)
            d.ldrawInheritsColor = True
        else:
            d = copyAndApplyMaterial(c, None)
            d.ldrawInheritsColor = False
        bpy.context.scene.objects.link(d)
        d.parent = p
    return p

def matrixEqual(a, b, threshold=THRESHOLD):
    if len(a.col) != len(b.col):
        return False
    for i in range(len(a)):
        for j in range(len(a[i])):
            if a[i][j] - b[i][j] > threshold:
                return False
    return True

class BFCContext(object):
    def __init__(self, other=None, copy=False):
        if copy:
            self.localCull = other.localCull
            self.winding = other.winding
            self.invertNext = other.invertNext
            self.certified = other.certified
            self.accumCull = other.accumCull
            self.accumInvert = other.accumInvert
        else:
            self.localCull = True
            self.winding = CCW
            self.invertNext = False
            self.certified = None
            if other is not None and other.certified:
                self.certified = True
                self.accumCull = other.accumCull and other.localCull
                self.accumInvert = other.accumInvert ^ other.invertNext
            else:
                self.accumCull = False
                self.accumInvert = False

def setMeshSmooth(me):
    for mp in me.faces:
        mp.smooth = True

partsCache = set()
def isAPart(name):
    global partsCache
    if name in partsCache:
        return True
    elif os.path.exists(os.path.join(LDRAWDIR, "parts", name)):
        partsCache.add(name)
        return True
    else:
        return False

def srgbToLinearrgb(c):
	if c < 0.04045:
		return 0.0 if c < 0.0 else (c * (1.0 / 12.92))
	else:
		return ((c + 0.055) * (1.0 / 1.055)) ** 2.4

def srgbToLinearrgbV3V3(srgb):
    return srgbToLinearrgb(srgb[0]), srgbToLinearrgb(srgb[1]), srgbToLinearrgb(srgb[2])

### IMPORTER ###

def parseColorAttributes(line, extraAttribs={}):
    if 'MATERIAL' in line:
        matIndex = line.index("MATERIAL")
        materialName = line[matIndex+1]
        # "MATERIAL should be the last tag in the !COLOUR statement"
        materialLine = line[matIndex+2:]
        line = line[:matIndex]
        materialAttribs, materialFlags = parseColorLine(materialLine,
            {'VALUE', 'ALPHA', 'LUMINANCE', 'FRACTION', 'VFRACTION', 'SIZE', 'MINSIZE', 'MAXSIZE'})
    else:
        materialName = None
        materialAttribs, materialFlags = None, None

    attribs, flags = parseColorLine(line,
        {'CODE', 'VALUE', 'EDGE', 'ALPHA', 'LUMINANCE'}, # expect a value after
        {'CHROME', 'PEARLESCENT', 'RUBBER', 'MATTE_METALLIC', 'METAL'}) # expect only one
    attribs.update(extraAttribs)
    
    return attribs, flags, materialName, materialAttribs, materialFlags

def doMaterialFreestyle(mat, attribs):
    edge = attribs['EDGE']
    if edge[0] == '#':
        mat.line_color = srgbToLinearrgbV3V3(hex2rgb(edge))+(1.0,)
    elif edge.isdigit():
        # References another color
        edge = int(edge)
        if edge in MATERIALS:
            mat.line_color = MATERIALS[edge].diffuse_color
        else:
            # TODO: The color may not have been defined yet, so we should
            # postpone edge color lookups until the end
            warnings.warn("Undefined color {0}".format(edge))
    else:
        warnings.warn("Malformed edge color reference: {0}".format(edge))

def createMaterial(name, line, extraAttribs={}):
    global MATERIALS
    
    attribs, flags, materialName, materialAttribs, materialFlags = parseColorAttributes(line, extraAttribs)
    
    del line
    
    value = srgbToLinearrgbV3V3(hex2rgb(attribs['VALUE']))
    
    materialId = attribs['CODE']
    if materialId.isdigit():
        materialId = int(materialId)
        if materialId in (16, 24):
            return None # Not allowed to use these colors directly
    
    if name in bpy.data.materials:
        mat = bpy.data.materials[name]
    else:
        mat = bpy.data.materials.new(name)
    MATERIALS[materialId] = mat
    
    mat.diffuse_color = value
    alpha = int(attribs.get('ALPHA', 255))
    mat.alpha = alpha/255.0
    
    if hasattr(mat, 'line_color'):
        # If Freestyle is enabled, set the line color as the LDraw edge color
        doMaterialFreestyle(mat, attribs)
    
    doMaterialInternal(mat, alpha, attribs, flags, materialName, materialAttribs, materialFlags)
    #doMaterialCycles(mat, value, alpha, attribs, flags, materialName, materialAttribs, materialFlags)
    
    return mat

def doMaterialInternal(mat, alpha, attribs, flags, materialName, materialAttribs, materialFlags):
    mat.emit = int(attribs.get('LUMINANCE', 0))/127.0

    if "CHROME" in flags:
        mat.ambient = 0.25
        mat.diffuse_intensity = 0.6
        mat.raytrace_mirror.use = True
        mat.specular_intensity = 1.4
        mat.roughness = 0.01
        mat.raytrace_mirror.reflect_factor = 0.3
    elif "PEARLESCENT" in flags:
        mat.ambient = 0.22
        mat.diffuse_intensity = 0.6
        mat.raytrace_mirror.use = True
        mat.specular_intensity = 0.1
        mat.roughness = 0.32
        mat.raytrace_mirror.reflect_factor = 0.07
    elif "RUBBER" in flags:
        mat.ambient = 0.5
        mat.specular_intensity = 0.19
        mat.specular_slope = 0.235
        mat.diffuse_intensity = 0.6
    elif "MATTE_METALLIC" in flags:
        mat.raytrace_mirror.use = True
        mat.raytrace_mirror.reflect_factor = 0.84
        mat.diffuse_intensity = 0.844
        mat.specular_intensity = 0.5
        mat.specular_hardness = 40
        mat.gloss_factor = 0.725
    elif "METAL" in flags:
        mat.raytrace_mirror.use = True
        mat.raytrace_mirror.reflect_factor = 0.9
        mat.diffuse_fresnel = 0.93
        mat.diffuse_intensity = 1.0
        mat.darkness = 0.771
        mat.specular_intensity = 1.473
        mat.specular_hardness = 292
    elif alpha < 255:
        mat.raytrace_mirror.use = True
        mat.ambient = 0.3
        mat.diffuse_intensity = 0.8
        mat.raytrace_mirror.reflect_factor = 0.1
        mat.specular_intensity = 0.3
        mat.raytrace_transparency.ior = 1.40
    else:
        mat.ambient = 0.1
        mat.specular_intensity = 0.2
        mat.diffuse_intensity = 1.0

    # Only these two are official, and they are nearly the same.
    if materialName == "GLITTER" or materialName == "SPECKLE":
        # I could use a particle system to make it more realistic,
        # but it would be VERY slow. Use procedural texture for now.
        # TODO There has to be a better way.
        if mat.name in bpy.data.textures:
            tex = bpy.data.textures[mat.name]
        else:
            tex = bpy.data.textures.new(mat.name, "STUCCI")
        value = srgbToLinearrgbV3V3(hex2rgb(materialAttribs["VALUE"]))
        # Alpha value is the same for the whole material, so the
        # texture can "inherit" this value, but ignore luminance, since
        # Blender textures only have color and transparency.
        fraction = float(materialAttribs["FRACTION"])
        tex.use_color_ramp = True
        tex.color_ramp.interpolation = "CONSTANT"
        tex.color_ramp.elements[0].color = value+(alpha/255.0,)
        tex.color_ramp.elements[1].color = [0, 0, 0, 0]
        tex.color_ramp.elements.new(fraction).color = value+(0.0,)
        if "SIZE" not in materialAttribs:
            # Hmm.... I don't know what to do here.
            size = int(materialAttribs["MINSIZE"])+int(materialAttribs["MAXSIZE"])
            size /= 2.0
        else:
            size = float(materialAttribs["SIZE"])
        size *= 0.025
        tex.noise_scale = size
        slot = mat.texture_slots.add()
        slot.texture = tex
        mat.use_textures[0] = True

    if alpha < 255:
        mat.use_transparency = True
        mat.transparency_method = "RAYTRACE"

def doMaterialCycles(mat, value, alpha, attribs, flags, materialName, materialAttribs, materialFlags):
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()
    shout = tree.nodes.new('ShaderNodeOutputMaterial')
    if "CHROME" in flags:
        pass
    elif "PEARLESCENT" in flags:
        pass
    elif "RUBBER" in flags:
        pass
    elif "MATTE_METALLIC" in flags:
        pass
    elif "METAL" in flags:
        pass
    elif alpha < 224:
        mix = tree.nodes.new('ShaderNodeMixShader')
        mix.inputs['Fac'].default_value = alpha/2047.0
        
        refr = tree.nodes.new('ShaderNodeBsdfRefraction')
        refr.inputs['Color'].default_value = value+(1.0,)
        refr.inputs['Roughness'].default_value = 0.0
        refr.inputs['IOR'].default_value = 1.40
        tree.links.new(refr.outputs['BSDF'], mix.inputs[1])
        
        gloss = tree.nodes.new('ShaderNodeBsdfGlossy')
        gloss.inputs['Color'].default_value = (1.0,1.0,1.0,1.0)
        gloss.inputs['Roughness'].default_value = 0.0
        tree.links.new(gloss.outputs['BSDF'], mix.inputs[2])
        
        tree.links.new(mix.outputs['Shader'], shout.inputs['Surface'])
    elif alpha < 255:
        pass
    else:
        mix = tree.nodes.new('ShaderNodeMixShader')
        mix.inputs['Fac'].default_value = 0.0625
        
        diff = tree.nodes.new('ShaderNodeBsdfDiffuse')
        diff.inputs['Color'].default_value = value+(1.0,)
        diff.inputs['Roughness'].default_value = 0.0
        tree.links.new(diff.outputs['BSDF'], mix.inputs[1])
        
        gloss = tree.nodes.new('ShaderNodeBsdfGlossy')
        gloss.inputs['Color'].default_value = (1.0,1.0,1.0,1.0)
        gloss.inputs['Roughness'].default_value = 0.0
        tree.links.new(gloss.outputs['BSDF'], mix.inputs[2])
        
        tree.links.new(mix.outputs['Shader'], shout.inputs['Surface'])

def lineType0(line, bfc, someObj=None):
    # Comment or meta-command
    if len(line) < 2:
        return
    if line[1] in ('WRITE', 'PRINT'):
        #Blender.Draw.PupMenu("Message in file:%t|"+(' '.join(line[2:])))
        pass
    elif line[1] == 'CLEAR':
        #bpy.ops.wm.redraw_timer()
        pass
    elif line[1] == 'PAUSE':
        #Blender.Draw.PupMenu("Paused.%t")
        pass
    elif line[1] == 'SAVE':
        #bpy.ops.render.render()
        pass
    elif line[1] == '!COLOUR':
        name = line[2].strip()
        line = [s.upper() for s in line]
        createMaterial(name, line)

    elif line[1] == "BFC":
        # http://www.ldraw.org/article/415
        if bfc.certified and "NOCERTIFY" not in line:
            bfc.certified = True
        for option in line[2:]:
            if option == "CERTIFY":
                assert bfc.certified is None or bfc.certified
                bfc.certified = True
            elif option == "NOCERTIFY":
                assert not bfc.certified
                bfc.certified = False
            elif option == "CLIP":
                bfc.localCull = True
            elif option == "NOCLIP":
                bfc.localCull = False
            elif option == "CCW":
                # According to the spec, winding should alternate depending on
                # accumInvert. However, for an importer, since accumInvert
                # depends on the files above in the hierarchy, we should only
                # use locally-specified winding, then invert when collapsing
                # the mesh
                bfc.winding = CCW
            elif option == "CW":
                bfc.winding = CW
            elif option == "INVERTNEXT":
                bfc.invertNext = True

def colorReference(s):
    if s.isdigit():
        materialId = int(s)
        if materialId in (16, 24):
            return materialId, None
        elif materialId in MATERIALS:
            return materialId, MATERIALS[materialId]
        else:
            warnings.warn("Undefined color {0}".format(materialId))
    elif s.startswith("0x2"):
        # Direct color
        if s in MATERIALS:
            return None, MATERIALS[s]
        else:
            return None, createMaterial(s, [], {"VALUE": s[3:], "CODE": s})
    else:
        warnings.warn("Malformed color reference: {0}".format(s))
    return None, None

def findMaterialIndex(listOfSlots, material):
    for idx, slot in enumerate(listOfSlots):
        if slot.link == "DATA" and slot.material == material:
            return idx

def lineType1(line, oldObj, oldMaterial, bfc, subfiles={}, merge=False):
    # File reference
    idx = -1
    for i in range(14):
        while True:
            nextSpace = line.find(' ', idx+1)
            if nextSpace == -1: return
            if nextSpace > idx+1:
                idx = nextSpace
                break
            idx = nextSpace
    fname = line[idx+1:].lower()
    line = line.split()
    newMatrix = mathutils.Matrix()
    newMatrix[0][:] = [float(line[ 5]), float(line[ 6]), float(line[ 7]), float(line[2])]
    newMatrix[1][:] = [float(line[ 8]), float(line[ 9]), float(line[10]), float(line[3])]
    newMatrix[2][:] = [float(line[11]), float(line[12]), float(line[13]), float(line[4])]
    newMatrix[3][:] = [           0.0,              0.0,             0.0,            1.0]
    
    if newMatrix.determinant() < 0:
        bfc.invertNext = not bfc.invertNext
    
    materialId, material = colorReference(line[1])
    if materialId in (16, 24):
        material = oldMaterial
    if fname in subfiles:
        newObj = readFile(fname, BFCContext(bfc), subfiles=subfiles, material=material, merge=merge)
    elif fname == 'light.dat' and USELIGHTS:
        l = bpy.data.lamps.new(fname)
        newObj = bpy.data.objects.new(fname, l)

        l.color = material.diffuse_color
        l.energy = material.alpha
        l.shadow_method = "RAY_SHADOW"
    else:
        newObj = readFile(fname, BFCContext(bfc), material=material, merge=merge or (MERGEPARTS and isAPart(fname)))
    if newObj:
        if isAPart(fname):
            if not ((fname[0] == 's') and (fname[1] in ('/', '\\'))):
                newMatrix *= GAPMAT
        newObj.ldrawInheritsColor = materialId in (16, 24)
        if merge:
            oldToNewMatMap = {0: 0}
            for subMatIdx, subMaterialSlot in enumerate(newObj.material_slots):
                if newObj.ldrawInheritsColor and subMaterialSlot.link == "OBJECT": continue
                matIdx = findMaterialIndex(oldObj.material_slots, subMaterialSlot.material)
                if matIdx is None:
                    oldObj.data.materials.append(subMaterialSlot.material)
                    oldToNewMatMap[subMatIdx] = len(oldObj.material_slots)-1
                else:
                    oldToNewMatMap[subMatIdx] = matIdx
            bm = bmesh.new()
            bm.from_mesh(newObj.data, face_normals=False)
            
            # Only use invertNext (not accumInvert), since reversals will be
            # accumulated when collapsing/merging
            if bfc.invertNext:
                bmesh.ops.reverse_faces(bm, faces=bm.faces, flip_multires=False)
            
            for face in bm.faces:
                face.material_index = oldToNewMatMap[face.material_index]
            bm.transform(newMatrix)
            bm.from_mesh(oldObj.data, face_normals=False)
            bm.to_mesh(oldObj.data)
            bm.free()
            childData = newObj.data
            #bpy.data.objects.remove(newObj)
            #bpy.data.meshes.remove(childData)
        else:
            bpy.context.scene.objects.link(newObj)
            newObj.parent = oldObj
            newObj.matrix_local = newMatrix
            if not matrixEqual(newMatrix, newObj.matrix_local):
                warnings.warn("Object matrix has changed, model may have errors!")

def findVert(bm, loc):
    for bv in bm.verts:
        if bv.co == loc: return bv
    return bm.verts.new(loc)

def poly(line, bm, bfc):
    # helper function for making polygons
    vertices = []
    for i in range(0, len(line), 3):
        vertices.append(findVert(bm, mathutils.Vector((float(line[i]), float(line[i+1]), float(line[i+2])))))
    if bfc.winding == CW:
        vertices.reverse()
    return bm.faces.new(vertices)

def readLine(line, o, material, bfc, bm, subfiles={}, readLater=None, merge=False):
    # Returns True if the file references any files or contains any polys;
    # otherwise, it is likely a header file and can be ignored.
    line = line.strip()
    if len(line) == 0:
        return False
    command = line[:max(line.find(' '), 1)]
    if command == '0':
        # Comment or meta-command
        sline = line.split()
        lineType0(sline, bfc)
        if len(sline) < 2 or sline[1] != "BFC":
            bfc.invertNext = False
        return False
    elif command == '1':
        # File reference
        if readLater is None:
            lineType1(line, o, material, BFCContext(bfc, True), subfiles=subfiles, merge=merge)
        else:
            newbfc = BFCContext(bfc, True)
            readLater.append((line, o, material, newbfc, subfiles, merge))
        bfc.invertNext = False
        return True
    elif command in ('3', '4'):
        # Tri or quad (poly)
        line = line.split()
        try:
            newFace = poly(line[2:], bm, bfc)
        except ValueError as e:
            warnings.warn(e)
            bfc.invertNext = False
            return True # for debugging, maybe?
        color, faceMat = colorReference(line[1])
        if color not in (16, 24):
            slotIdx = -1
            for i, matSlot in enumerate(o.material_slots):
                if matSlot.material == faceMat and matSlot.link == "DATA":
                    slotIdx = i
                    break
            if slotIdx == -1:
                o.data.materials.append(faceMat)
                newFace.material_index = len(o.material_slots)-1
            else:
                newFace.material_index = slotIdx
        else:
            newFace.material_index = 0
        bfc.invertNext = False
        return True
    elif command == '2':
        # Line
        line = line.split()
        verts = [findVert(bm, mathutils.Vector((float(line[2]), float(line[3]), float(line[4])))),
                 findVert(bm, mathutils.Vector((float(line[5]), float(line[6]), float(line[7]))))]
        newEdge = bm.edges.get(verts, None)
        if newEdge is None: newEdge = bm.edges.new(verts)
        newEdge.smooth = False
        bfc.invertNext = False
        return True
    elif command == '5':
        # Conditional line
        # Not supported
        bfc.invertNext = False
        return False
    else:
        warnings.warn("Unknown linetype %s\n" % command)
        return False

def readFile(fname, bfc, first=False, smooth=False, material=None, transform=False, subfiles={}, merge=False):
    global IGNOREOBJECTS
    if fname in subfiles:
        # part of a multi-part
        import io
        f = io.StringIO(subfiles[fname])
    else:
        fname = fname.replace('\\', os.path.sep)
        f = None

        paths = [fname,
                 os.path.join(LDRAWDIR, "parts", fname),
                 os.path.join(LDRAWDIR, "p", fname),
                 os.path.join(LDRAWDIR, "models", fname)]
        if HIRES:
            paths.insert(2, os.path.join(LDRAWDIR, "p", "48", fname))
        if LOWRES:
            paths.insert(2, os.path.join(LDRAWDIR, "p", "8", fname))

        for path in paths:
            if os.path.exists(path):
                f = open(path)
                break

        if f is None:
            warnings.warn("Could not find file %s" % fname)
            return

        if os.path.splitext(fname)[1] in ('.mpd', '.ldr'):
            # multi-part!
            subfiles = {}
            name = None
            firstName = None
            for line in f:
                if line[0] == '0':
                    sline = line.split()
                    if len(sline) < 2:
                        continue
                    if sline[1] == 'FILE':
                        i = line.find('FILE')
                        i += 4
                        name = line[i:].strip().lower()
                        subfiles[name] = ''
                        if firstName is None:
                            firstName = name
                    elif sline[1] == 'NOFILE':
                        name = None
                    elif name is not None:
                        subfiles[name] += line
                elif name is not None:
                    subfiles[name] += line
            if firstName is None:
                # This is if it wasn't actually multi-part (as is the case with most LDRs)
                firstName = fname.lower()
                f.seek(0)
                subfiles[firstName] = f.read()
            f.close()
            # "When an MPD file is used to store a multi-file model, the first
            # file in the MPD is treated as the 'main model'"
            return readFile(firstName, bfc, first=first, smooth=smooth, material=material, transform=transform, subfiles=subfiles, merge=merge)

    mname = os.path.split(fname)[1]
    if mname in IGNOREOBJECTS:
        return None
    if mname in bpy.data.objects:
        # We don't need to re-import a part if it's already in the file
        obj = copyAndApplyMaterial(bpy.data.objects[mname], material)
        obj.active_material_index = 0
        obj.active_material = material
        obj.material_slots[0].link = 'OBJECT'
        obj.active_material = material
        return obj

    mesh = bpy.data.meshes.new(mname)
    bm = bmesh.new()
    obj = bpy.data.objects.new(mname, mesh)

    obj.active_material_index = 0
    obj.active_material = material
    obj.material_slots[0].link = 'OBJECT'
    obj.active_material = material

    containsData = False
    if first:
        lines = f.readlines()
        f.close()
        total = len(lines)
        readLaterLines = [None]*total
        for idx, line in enumerate(lines):
            readLater = []
            containsData = readLine(line, obj, material, bfc, bm, subfiles=subfiles, readLater=readLater, merge=merge) or containsData
            readLaterLines[idx] = readLater
        if transform:
            obj.matrix_local = DEFAULTMAT
        del lines
    else:
        readLater = []
        for line in f:
            containsData = readLine(line, obj, material, bfc, bm, subfiles=subfiles, readLater=readLater, merge=merge) or containsData
        f.close()

    if SMOOTH and (
        (('con' in fname) and
         (not fname.startswith('con'))) or
        ('cyl' in fname) or
        ('sph' in fname) or
        fname.startswith('t0') or
        fname.startswith('t1') or
        ('bump' in fname)):

        setMeshSmooth(bm)

        # Old method - the loop is probably faster (being written in C), but it
        # causes a scene update after
        #bpy.ops.object.shade_smooth()

    if SMOOTH and isAPart(fname):
        setMeshSmooth(bm)
        mesh.use_auto_smooth = True
        mesh.auto_smooth_angle = math.pi
        mesh.show_edge_sharp = True
    
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.1)
    bm.to_mesh(mesh)
    bm.free()

    if first:
        bpy.context.window_manager.progress_begin(0, total)
        for idx, readLater in enumerate(readLaterLines):
            for args in readLater:
                print("Processing line {0}/{1}".format(idx+1, total))
                lineType1(*args)
                bpy.context.window_manager.progress_update(idx+1)
        bpy.context.window_manager.progress_end()
    else:
        for args in readLater:
            lineType1(*args)
    
    #bm = bmesh.new()
    #bm.from_mesh(mesh)
    #bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.0001)
    #bm.to_mesh(mesh)
    #bm.free()
    mesh.update()
    
    if not containsData:
        # This is to check for header files (like ldconfig.ldr) and
        # other blank files (like 4-4edge.dat)
        IGNOREOBJECTS.add(mname)
        bpy.data.objects.remove(obj)
        return None
    return obj

def main(fname, context=None, transform=False):
    global MATERIALS, IGNOREOBJECTS
    #Blender.Window.WaitCursor(1)
    start = time.time()
    MATERIALS = {}
    IGNOREOBJECTS = set()
    readFile(os.path.join(LDRAWDIR, "LDConfig.ldr"), BFCContext(), first=False)
    obj = readFile(fname, BFCContext(), first=True, transform=transform, merge=(MERGEPARTS and isAPart(fname)))
    bpy.context.scene.objects.link(obj)
    context.scene.update()
    print('LDraw "{0}" imported in {1:.4} seconds.'.format(fname, time.time()-start))

class IMPORT_OT_ldraw(bpy.types.Operator):
    '''Import LDraw model Operator.'''
    bl_idname = "import_scene.ldraw_dat"
    bl_label = "Import LDR/DAT/MPD"
    bl_description = "Import an LDraw model file (.dat, .ldr, .mpd)"
    bl_options = {'REGISTER', 'UNDO'}

    filepath = bpy.props.StringProperty(name="File Path", description="Filepath used for importing the LDR/DAT/MPD file", maxlen=MAXPATH, default="")

    ldrawPathProp = bpy.props.StringProperty(name="LDraw directory", description="The directory in which the P and PARTS directories reside", maxlen=MAXPATH, default={"win32": "C:\\Program Files\\LDraw", "darwin": "/Library/LDraw"}.get(sys.platform, "/usr/share/ldraw"))
    transformProp = bpy.props.BoolProperty(name="Transform", description="Transform objects to match Blender's coordinate system", default=True)
    smoothProp = bpy.props.BoolProperty(name="Smooth", description="Automatically shade round primitives (cyl, sph, con, tor) smooth", default=True)
    hiResProp = bpy.props.BoolProperty(name="Hi-Res prims", description="Force use of high-resolution primitives, if possible", default=False)
    lightProp = bpy.props.BoolProperty(name="Lights from model", description="Create lamps in place of light.dat references", default=True)
    scaleProp = bpy.props.FloatProperty(name="Seam width", description="The amout of space in-between individual parts", default=0.0066667, min=0.0, max=1.0, precision=3)
    mergePartsProp = bpy.props.BoolProperty(name="Merge parts", description="Automatically combine sub-parts into single objects", default=True)

    def execute(self, context):
        global LDRAWDIR, SMOOTH, HIRES, USELIGHTS, GAPMAT, MERGEPARTS
        LDRAWDIR = str(self.ldrawPathProp)
        transform = bool(self.transformProp)
        SMOOTH = bool(self.smoothProp)
        HIRES = bool(self.hiResProp)
        USELIGHTS = bool(self.lightProp)
        gap = float(self.scaleProp)
        GAPMAT = mathutils.Matrix.Scale(1.0-gap, 4)
        MERGEPARTS = bool(self.mergePartsProp)
        main(self.filepath, context, transform)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


def menu_import(self, context):
    self.layout.operator(IMPORT_OT_ldraw.bl_idname, text="LDraw Model (.dat, .mpd, .ldr)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_import)
    bpy.types.Object.ldrawInheritsColor = bpy.props.BoolProperty()

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_import)
    del bpy.types.Object.ldrawInheritsColor

if __name__ == "__main__":
    register()
    #import cProfile
    #LDRAWDIR = "/Library/LDraw"
    #LDRAWDIR = "C:\\Program Files\\LDraw"
    #LDRAWDIR = "/home/spencer/ldraw"
    #SMOOTH = True
    #HIRES = False
    #USELIGHTS = True
    #gap = 1.0/64.0
    #GAPMAT = mathutils.Matrix.Scale(1.0-gap, 4)
    #try:
    #    cProfile.run('main(os.path.join(LDRAWDIR, "models", "pyramid.dat"), bpy.context, True)')
    #finally:
    #    sys.stderr.flush()
    #    sys.stdout.flush()
