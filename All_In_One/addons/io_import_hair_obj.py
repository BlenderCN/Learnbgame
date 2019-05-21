# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Project Name:        MakeHuman
# Product Home Page:   http://www.makehuman.org/
# Code Home Page:      http://code.google.com/p/makehuman/
# Authors:             Thomas Larsson
# Script copyright (C) MakeHuman Team 2001-2013
# Coding Standards:    See http://www.makehuman.org/node/165

"""
Abstract
Import obj file with curves as hair for Blender 2.5
Version 0.6

Place the script in the .blender/scripts/addons dir
Activate the script in the "Add-Ons" tab (user preferences).
Access from the File > Import menu.

Alternatively, run the script in the script editor (Alt-P), and access from the File > Import menu
"""

bl_info = {
    'name': 'Import MakeHuman hair (.obj)',
    'author': 'Thomas Larsson',
    'version': '0.7',
    'blender': (2, 5, 6),
    'api': 35774,
    'location': 'File > Import',
    'description': 'Import MakeHuman hair file (.obj)',
    'wiki_url': 'http://sites.google.com/site/makehumandocs/blender-export-and-mhx/hair',
    'category': 'Import-Export'}

import bpy
import mathutils
from mathutils import *
import os

#
#    Structure of obj file
#

"""
v 0.140943 8.017279 0.227470
v 0.136992 8.053163 0.281365
v 0.232386 8.314340 0.444419
v 0.450719 8.241523 0.873019
v 0.415614 7.887863 1.029564
v 0.297117 7.653935 1.108557
v -0.113154 7.533733 1.182444
cstype bspline
deg 3
curv 0.0 1.0 -1 -2 -3 -4 -5 -6 -7
parm u 0.0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0
end
"""

#
#    importHair(context, filename, scale, invert, useCurves):
#

def importHair(context, filename, scale, invert, useCurves):
    try:
        ob = context.object
        dx = ob['MhxOffsetX']
        dy = ob['MhxOffsetY']
        dz = ob['MhxOffsetZ']
    except:
        (dx,dy,dz) = (0,0,0)

    (name, guides) = readHairFile(filename, scale, (dx,dy,dz))
    if invert:
        for guide in guides:
            guide.reverse()
    (nmax,nguides) = equalizeHairLengths(guides)
    print("%d guides, %d steps" % (len(nguides), nmax))
    if useCurves:
        makeCurves(name, nguides)
    else:
        makeHair(name, nmax-1, nguides)
        bpy.ops.particle.particle_edit_toggle()

    '''
    fp = open("/home/thomas/myblends/hair/test2.txt", "w")
    nmax = len(guides[0])
    for m,guide in enumerate(guides):
        printGuideAndHair(fp, guide, psys.particles[m], psys.settings.hair_step, nmax)
    fp.close()    
    '''
    return

#
#    writeHairFile(fileName, scale):
#    For debugging, export hair as obj
#

def writeHairFile(fileName, scale):
    ob = bpy.context.object
    psys = ob.active_particle_system
    if psys and psys.name == 'Hair':
        pass
    else:
        raise NameError("Active object has no hair")

    filePath = os.path.realpath(os.path.expanduser(fileName))
    print( "Writing hair " + filePath )
    fp = open(filePath, "w")

    for n,par in enumerate(psys.particles):
        v = par.location / scale
        fp.write("v %.3f %.3f %.3f\n" % (v[0], v[1], v[2]))
        for h in par.hair_keys:
            v = h.location / scale
            fp.write("v %.3f %.3f %.3f\n" % (v[0], v[1], v[2]))
        fp.write("g Hair.%03d\n" % n)
        fp.write("end\n\n")
    fp.close()
    return

#
#    readHairFile(fileName, scale, offset):
#    Read obj file with hair strands as curves
#

def readHairFile(fileName, scale, offset):
    (name, ext) = os.path.splitext(os.path.basename(fileName))
    filePath = os.path.realpath(os.path.expanduser(fileName))
    print( "Reading hair " + filePath )
    fp = open(filePath, "rU")
    guide = []
    guides = []
    lineNo = 0
    (dx,dy,dz) = offset

    for line in fp: 
        words= line.split()
        lineNo += 1
        if len(words) == 0:
            pass
        elif words[0] == 'v':
            (x,y,z) = (float(words[1]), float(words[2]), float(words[3]))
            guide.append(scale*Vector((x-dx,-z+dz,y-dy)))
        elif words[0] == 'end':
            guides.append(guide)
            guide = []
        elif words[0] == 'f':
            raise NameError("Hair file '%s' must only contain curves, not meshes" % filePath)
        else:
            pass
    fp.close()
    print("File %s read" % fileName)
    return (name, guides)

#
#    equalizeHairLengths(guides):
#    All hairs in Blender must have the same length. Interpolate the guide curves ensure this.
#
    
def equalizeHairLengths(guides):
    nmax = 0
    nguides = []
    for guide in guides:
        n = len(guide)
        if n > nmax:
            nmax = n
        #for k in range(1,n):
        #    guide[k] -= guide[0]
    
    for guide in guides:
        if len(guide) < nmax:
            nguide = recalcHair(guide, nmax)
        else:
            nguide = guide
        nguides.append(nguide)
    return (nmax, nguides)

#
#    recalcHair(guide, nmax):
#    Recalculates a single hair curve
#
    
def recalcHair(guide, nmax):
    n = len(guide)
    if n == nmax:
        return guide
    dx = float(nmax)/n
    x = 0.0
    y0 = Vector([0.0, 0.0, 0.0])
    y0 = guide[0]
    nguide = [guide[0].copy()]
    for k in range(1,n):
        y = guide[k]
        f = (y-y0)/dx
        x += dx
        while x > 0.9999:
            y0 += f
            nguide.append(y0.copy())
            k += 1
            x -= 1
    y0 = guide[n-1]
    nguide.append(y0.copy())
    return nguide
            
#
#    printGuides(fp, guide, nguide, nmax):
#    printGuideAndHair(fp, guide, par, hs, nmax):
#    For debugging
#

def printGuides(fp, guide, nguide, nmax):
    if len(nguide) != nmax:
        fp.write("wrong size %d != %d\n" % (len(nguide), nmax))
        return
    fp.write("\n\n")
    for n,v in enumerate(guide):
        nv = nguide[n]
        fp.write("(%.3f %.3f %.3f)\t=> (%.3f %.3f %.3f)\n" % (v[0], v[1], v[2], nv[0], nv[1], nv[2]))
    for n in range(len(guide), nmax):
        nv = nguide[n]
        fp.write("\t\t\t\t=> (%.3f %.3f %.3f)\n" % (nv[0], nv[1], nv[2]))
    return
    
def printGuideAndHair(fp, guide, par, hs, nmax):
    fp.write("\n\n")
    for n,v in enumerate(guide):
        if n == 0:
            nv = par.location
        else:
            nv = par.hair_keys[n-1].co
        fp.write("%2d %2d  (%.3f %.3f %.3f)\t=> (%.3f %.3f %.3f)" % (n-1, hs, v[0], v[1], v[2], nv[0], nv[1], nv[2]))
        if n > 0:
            h = par.hair_keys[n-1]
            lv = h.co_hair_space
            fp.write(" (%.3f %.3f %.3f) %.3f %.3f\n" % (lv[0], lv[1], lv[2], h.time, h.weight))
        else:
            fp.write("\n")
    return
    
#    
#    makeHair(name, hstep, guides):
#    Create particle hair from guide curves. 
#    hstep = hair_step setting
#

def makeHair(name, hstep, guides):
    ob = bpy.context.object
    bpy.ops.object.particle_system_add()
    psys = ob.particle_systems.active
    psys.name = name

    settings = psys.settings
    settings.type = 'HAIR'
    settings.name = 'HairSettings'
    settings.count = len(guides)
    settings.hair_step = hstep
    # [‘VERT’, ‘FACE’, ‘VOLUME’, ‘PARTICLE’]
    settings.emit_from = 'FACE'
    settings.use_render_emitter = True

    settings.use_hair_bspline = True
    #settings.hair_geometry = True
    #settings.grid_resolution = 
    #settings.draw_step = 1

    settings.material = 3
    #settings.use_render_adaptive = True
    settings.use_strand_primitive = True

    settings.child_type = 'SIMPLE'
    settings.child_nbr = int(1000/settings.count)+1
    settings.rendered_child_count = 10*settings.child_nbr
    settings.child_length = 1.0
    settings.child_radius = 0.2

    '''
    settings.clump_factor = 0.0
    settings.clumppow = 0.0

    settings.rough_endpoint = 0.0
    settings.rough_end_shape = 1.0
    settings.rough1 = 0.0
    settings.rough1_size = 1.0
    settings.rough2 = 0.0
    settings.rough2_size = 1.0
    settings.rough2_thres = 0.0

    settings.kink = 'CURL'
    settings.kink_amplitude = 0.2
    settings.kink_shape = 0.0
    settings.kink_frequency = 2.0
    '''
    bpy.ops.particle.disconnect_hair(all=True)
    bpy.ops.particle.particle_edit_toggle()

    for m,guide in enumerate(guides):
        par = psys.particles[m]
        setStrand(guide, par, hstep)

    bpy.ops.particle.select_all(action='SELECT')
    bpy.ops.particle.connect_hair(all=True)
    return

#
#    setStrand(guide, par, hstep):
#

def setStrand(guide, par, hstep):
    nmax = hstep
    dt = 100.0/(hstep)
    dw = 1.0/(hstep-1)
    if len(guide) < nmax+1:
        nmax = len(guide)-1
        #raise NameError("Wrong length %d != %d" % (len(guide), hstep))
    par.location = guide[0]
    for n in range(0, nmax):
        point = guide[n+1]
        h = par.hair_keys[n]
        #h.co = point
        h.co_hair_space = point
        h.time = (n+1)*dt
        w = 1.0 - (n+1)*dw
        h.weight = max(w, 0.0)
    for n in range(nmax, hstep):
        point = guide[nmax]
        h = par.hair_keys[n]
        #h.co = point
        h.co_hair_space = point
        h.time = (n+1)*dt
        w = 1.0 - (n+1)*dw
        h.weight = max(w, 0.0)

    #print(par.location)
    #for n in range(0, hstep):
    #    print("  ", par.hair_keys[n].co)
    return

#
#    reverseStrands(ob):
#    getGuideFromHair(par):
#

def reverseStrands(ob):
    psys = ob.particle_systems.active
    if (not psys) or psys.settings.type != 'HAIR':
        print("Cannot reverse strands. No active hair.")
        return
    for par in psys.particles:
        if par.select:
            guide = getGuideFromHair(par)
            hstep = len(guide)
            setStrand(guide, par, psys.hair_step)
    return

def getGuideFromHair(par):
    guide = [par.location]
    for h in par.hair_keys:
        guide.append( h.co_hair_space.copy() )
    guide.reverse()
    return guide

#
#    makeCurves(name, guides):
#    setSplinePoint(pt, x):
#

def makeCurves(name, guides):
    cu = bpy.data.curves.new(name, 'CURVE')
    ob = bpy.data.objects.new(name, cu)
    bpy.context.scene.objects.link(ob)
    cu.dimensions = '3D'

    for guide in guides:
        npoints = len(guide)
        spline = cu.splines.new('NURBS')
        spline.points.add(npoints-1)
        for n in range(npoints):
            setSplinePoint(spline.points[n].co, guide[n])
    return ob

def setSplinePoint(pt, x):
    pt[0] = x[0]
    pt[1] = x[1]
    pt[2] = x[2]
    return

#
#    reverseCurves(ob):
#

def reverseCurves(ob):
    for spline in ob.data.splines:
        selected = False
        for pt in spline.points:
            if pt.select:
                selected = True
                break
        if selected:
            guide = []
            for pt in spline.points:
                guide.append(pt.co.copy())
            guide.reverse()
            npoints = len(guide)
            for n in range(npoints):
                setSplinePoint(spline.points[n].co, guide[n])
    return

#
#    makeHairFromCurve(ob, cuOb):
#

def makeHairFromCurve(ob, cuOb):
    guides = []
    for spline in cuOb.data.splines:
        guide = []
        for pt in spline.points:
            x = pt.co
            guide.append( Vector((x[0], x[1], x[2])) )
        guides.append(guide)
    makeHair('Hair', len(guides[0])-1, guides)
    return

#
#    User interface
#

DEBUG= False
from bpy.props import *
from bpy_extras.io_utils import ImportHelper


#
#    class ImportMhHairObj(bpy.types.Operator):
#

class ImportMhHairObj(bpy.types.Operator, ImportHelper):
    """Import MakeHuman hair from OBJ curves file (.obj)"""
    bl_idname = "import_hair.makehuman_obj"
    bl_description = 'Import MakeHuman hair from OBJ curves file (.obj)'
    bl_label = "Import MakeHuman hair"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    filename_ext = ".obj"
    filter_glob = StringProperty(default="hair_*.obj", options={'HIDDEN'})
    filepath = StringProperty(name="File Path", description="File path used for importing the .obj file", maxlen= 1024, default= "")

    scale = FloatProperty(name="Scale", description="Default meter, decimeter = 1.0", default=1.0)
    invert = BoolProperty(name="Invert", description="Invert hair direction", default=False)
    useCurves = BoolProperty(name="Curves", description="Import curves as curves", default=False)
    
    def execute(self, context):
        p = self.properties
        importHair(context, p.filepath, p.scale, p.invert, p.useCurves)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#
#    class MhxHairPanel(bpy.types.Panel):
#

class MhxHairPanel(bpy.types.Panel):
    bl_label = "MakeHuman Hair"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    
    def draw(self, context):
        layout = self.layout
        scn = context.scene
        #layout.operator("view3d.mhx_reverse_strands")
        layout.operator("view3d.mhx_reverse_curve")
        layout.operator("view3d.mhx_make_hair_from_curves")

#
#    class VIEW3D_OT_MhxReverseStrandsButton(bpy.types.Operator):
#

class VIEW3D_OT_MhxReverseStrandsButton(bpy.types.Operator):
    bl_idname = "view3d.mhx_reverse_strands"
    bl_label = "Reverse strands"

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.particle_systems.active)    

    def execute(self, context):
        reverseStrands(context.object)
        print("Strands reversed")
        return{'FINISHED'}    

#
#    class VIEW3D_OT_MhxReverseCurveButton(bpy.types.Operator):
#

class VIEW3D_OT_MhxReverseCurveButton(bpy.types.Operator):
    bl_idname = "view3d.mhx_reverse_curve"
    bl_label = "Reverse curve"

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'CURVE')

    def execute(self, context):
        reverseCurves(context.object)
        print("Curve reversed")
        return{'FINISHED'}    

#
#    class VIEW3D_OT_MhxMakeHairFromCurvesButton(bpy.types.Operator):
#

class VIEW3D_OT_MhxMakeHairFromCurvesButton(bpy.types.Operator):
    bl_idname = "view3d.mhx_make_hair_from_curves"
    bl_label = "Make hair from curves"

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'MESH')    

    def execute(self, context):
        ob = context.object
        for cuOb in context.scene.objects:
            if cuOb.select and cuOb.type == 'CURVE':
                makeHairFromCurve(ob, cuOb)
        print("Made hair from curves")
        return{'FINISHED'}    

#
#    Register
#

def menu_func(self, context):
    self.layout.operator(ImportMhHairObj.bl_idname, text="MakeHuman hair (.obj)...")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func)
 
def unregister():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
    register()

#
#    Testing
#

'''
guide1 = [ [0, 1, 0], [0, 2, 0], [0, 2, 1] ]
guide2 = [ [1, 0, 0], [1, 1, 0], [1, 1, 1] ]
guide3 = [ [2, 0, 0], [2, 1, 0], [2, 1, 1] ]
makeHair('H1', 3, [guide1, guide2, guide3])
makeHair('H2', 3, [guide2])
makeHair('H3', 3, [guide3])


readHairFile('/home/thomas/myblends/hair/hair_hairy.obj', 1.0, False)
writeHairFile('/home/thomas/myblends/hair/haired.obj', 1.0)
'''


