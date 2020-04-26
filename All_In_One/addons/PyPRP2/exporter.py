#    This file is part of PyPRP2.
#    
#    Copyright (C) 2010 PyPRP2 Project Team
#    See the file AUTHORS for more info about the team.
#    
#    PyPRP2 is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    
#    PyPRP2 is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with PyPRP2.  If not, see <http://www.gnu.org/licenses/>.


import bpy
from bpy.props import *
from PyHSPlasma import *
import modifiers
import geometry
import physics
import material
import lights
import animations
import utils
import os
import math

class VisibleObjectStuff: #do YOU have a better name for it? ;P
    def __init__(self, agename, pagename):
        self.geomgr = geometry.GeometryManager(agename, pagename)
        self.materials = {} #keyed by Blender material
        self.lights = {} #keyed by Blender lights

def export_clean(path,agename): #deletes old files before export
    items = os.listdir(path)
    for item in items:
        if item.startswith(agename) and item.endswith((".age", ".fni", ".prp", ".sum")):
            os.remove(os.path.join(path,item))

def convert_version(spv):
    if spv == "PVPRIME":
        return pvPrime
    elif spv == "PVPOTS":
        return pvPots
    elif spv == "PVMOUL":
        return pvMoul
    elif spv == "PVEOA":
        return pvEoa
    elif spv == "PVHEX":
        return pvHex

def export_scene_as_prp(rm, loc, blscene, agename, path):
    vos = VisibleObjectStuff(agename, blscene.name)
    print("Exporting Materials")
    ExportAllMaterials(rm, loc, blscene, vos)
    print("Exporting Scene Data")
    ExportSceneNode(rm, loc, blscene,blscene.name,agename, vos)
    vos.geomgr.FinallizeAllDSpans()
    page = plPageInfo()
    page.location = loc
    page.age = agename
    page.page = blscene.name
    rm.AddPage(page)
    fullpagename = "%s_District_%s.prp"%(page.age, page.page)
    print("Writing Page %s"%fullpagename)
    rm.WritePage(os.path.join(path,fullpagename), page)
    GeoMgr = None #clean up

def export_fog(s, world):
    yon = 10000 #no corresponding input in Blender (we'll need to make one)
    s.writeLine("Graphics.Renderer.Setyon %f" % yon)
    color = tuple(world.horizon_color)
    s.writeLine("Graphics.Renderer.Fog.SetDefColor %f %f %f" % color)
    s.writeLine("Graphics.Renderer.SetClearColor %f %f %f" % color)
    mist = world.mist_settings
    if mist.use_mist:
        equation = mist.falloff
        end = mist.start+mist.depth
        density = 1.0
        if equation == "LINEAR":
            s.writeLine("Graphics.Renderer.Fog.SetDefLinear %f, %f, %f" % (mist.start, end, density))
        elif equation == "QUADRATIC":
            s.writeLine("Graphics.Renderer.Fog.SetDefExp2 %f, %f" % (end, density))
        else:
            raise Exception("Mist Falloff \"%s\" not supported!" % equation)

class PlasmaExportAge(bpy.types.Operator):
    '''Export as Plasma Age'''
    bl_idname = "export.plasmaage"
    bl_label = "Export Age"

    filename_ext = ".age"
    filter_glob = StringProperty(default="*.age", options={'HIDDEN'})

    def execute(self, context):
        world = bpy.context.scene.world
        plsettings = world.plasma_age        
        agename = plsettings.name
        agedir = bpy.path.abspath(plsettings.export_dir)
        if not agename:
            raise Exception("You must give your age a name!")
        if not agedir:
            raise Exception("You must specify an export directory!")
        if not os.path.exists(agedir):
            os.mkdir(agedir)
        print("Cleaning up old files...",end=" ")
        export_clean(agedir, agename)
        print("Done")
        pversion = convert_version(plsettings.plasmaversion)
        print(pversion)
        rm = plResManager(pversion)
        ageinfo = plAgeInfo()
        ageinfo.name = agename
        ageinfo.dayLength = plsettings.daylength
        ageinfo.seqPrefix = plsettings.prefix
        ageinfo.maxCapacity = plsettings.maxcapacity
        ageinfo.lingerTime = plsettings.lingertime
        ageinfo.releaseVersion = plsettings.releaseversion
        if plsettings.startdatetime > 0:
            ageinfo.startDateTime = plsettings.startdatetime
        print("Commencing export of Scenes/Pages")
        if context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        pageid = 0
        for scene in bpy.data.scenes:
            if not scene.plasma_page.isexport:
                print("Skipping Export of Page: \"%s\""%scene.name)
                continue
            print("Exporting Page: \"%s\""%scene.name)
            loc = plLocation()
            loc.page = int(pageid)
            loc.prefix = int(plsettings.prefix)
            export_scene_as_prp(rm, loc, scene, agename, agedir)
            pageflags = 0
            if not scene.plasma_page.load:
                pgflags  |= kFlagPreventAutoLoad
            ageinfo.addPage((scene.name,pageid,pageflags))
            pageid += 1
        print("Writing age file to %s"%os.path.join(agedir,agename+".age"))
        ageinfo.writeToFile(os.path.join(agedir,agename+".age"), pversion)
        print("Writing fni file...")
        if pversion in [pvPrime, pvPots, pvMoul]:
            enc = plEncryptedStream.kEncXtea
        else:
            enc = plEncryptedStream.kEncAuto
        fnifile = plEncryptedStream(pversion)
        fnifile.open(os.path.join(agedir,agename+".fni"), fmWrite, enc)
        export_fog(fnifile, world)
        fnifile.close()
        if pversion != pvMoul:
            print("Writing sum file...")
            sumfile = plEncryptedStream(pversion)
            sumfile.open(os.path.join(agedir,agename+".sum"), fmWrite, enc)
            sumfile.writeInt(0)
            sumfile.writeInt(0)
            sumfile.close()
        del rm
        print("Export Complete")
        return {'FINISHED'}

class PlasmaExportResourcePage(bpy.types.Operator):
    '''Export as Plasma Resource Page'''
    bl_idname = "export.plasmaprp"
    bl_label = "Export PRP"

    filename_ext = ".prp"
    filter_glob = StringProperty(default="*.prp", options={'HIDDEN'})

    version = EnumProperty(attr="plasma_version",
                              items=(
                                  ("PVPRIME", "Plasma 2.0 (59.11)", "Ages Beyond Myst, To D'ni, Untìl Uru"),
                                  ("PVPOTS", "Plasma 2.0 (59.12)", "Path of the Shell, Complete  Chronicles"),
                                  ("PVMOUL", "Plasma 2.0 (70.9)", "Myst Online: Uru Live, MOULagain, MagiQuest Online"),
                                  ("PVEOA", "Plasma 2.1", "End of Ages, Crowthistle"),
                                  ("PVHEX", "Plasma 3.0", "HexIsle")
                              ),
                              name="Plasma Version",
                              description="Plasma Engine Version",
                              default="PVPOTS")

    def execute(self, context):
        print("Exporting as prp...")
        world = bpy.context.scene.world.plasma_age
        agename = plsettings.name
        agedir = bpy.path.abspath(plsettings.export_dir)
        rm = plResManager(convert_version(self.properties.version))
        i = 0
        loc = plLocation()
        loc.page = 0
        loc.prefix = plsettings.prefix
        export_scene_as_prp(rm, loc, bpy.context.scene, agename, agedir)
        print("Export Complete")
        return {'FINISHED'}


def ExportAvAnimPage():  #this function is so hacky it should be euthanized along with the companion cube
    cfg = PlasmaConfigParser()
    filepath = cfg.get('Paths', 'filepath')
    if filepath == None:
        raise Exception("Can't find variable filepath in config.")
    if len(bpy.data.worlds) > 1:
        raise Exception("Multiple worlds have been detected, please delete all except one of them to continue.")
    try:
        plsettings = bpy.context.scene.world.plasma_age
    except:
        raise Exception("Please go take a look at your world settings.  That's the little globe button.")            
    agename = plsettings.agename
    if not agename:
        raise Exception("You must give your age a name!")

    pversion = convert_version(plsettings.plasmaversion)    
    rm = plResManager(pversion)
    loc = plLocation()
    loc.page = 0 #:P
    loc.prefix = plsettings.prefix

    pagename = bpy.data.scenes[0].name
#fun ;)
    node = plSceneNode("%s_District_%s"%(agename, pagename))
    rm.AddObject(loc,node)
    atcanim = animations.processArmature(bpy.data.scenes[0].objects["PlasmaArmature"],pagename)
    rm.AddObject(loc,atcanim)
    node.addPoolObject(atcanim.key)

    page = plPageInfo()
    page.location = loc
    page.age = agename
    page.page = pagename
    rm.AddPage(page)
    fullpagename = "%s_District_%s.prp"%(page.age, page.page)
    print("Writing Page %s"%fullpagename)
    rm.WritePage(os.path.join(filepath,fullpagename), page)


class PlasmaExport(bpy.types.Operator):
    bl_idname = "export.plasmaexport"
    bl_label = "Plasma Export"
    type = EnumProperty(items=(
                                  ("age", "Export Age", ""),
                                  ("prp", "Export PRP", ""),
                                  ("aaprp", "Avatar Animation Page (testing use ONLY)", "")
                              ),
                              name="Export Type",
                              description="Export Type")
    def execute(self, context):
        if self.properties.type == "age":
            bpy.ops.export.plasmaage()
        elif self.properties.type == "prp":
            bpy.ops.export.plasmaprp('INVOKE_DEFAULT', path="/")
        elif self.properties.type == "aaprp":
            ExportAvAnimPage()
        ##TODO have an "Export Append" option that splices your pages into an existing age
        return {'FINISHED'}

###### End of Blender operator stuff ######

def ExportAllMaterials(rm, loc, blScn, vos):
    for blObj in blScn.objects:
        for materialslot in blObj.material_slots:
            mat = materialslot.material
            if not mat in vos.materials: #if we haven't already added it
                gmat = material.ExportMaterial(rm, loc, mat)
                vos.materials[mat] = gmat.key

def ExportSceneNode(rm,loc,blScn,pagename,agename, vos):
    name = "%s_District_%s"%(agename, pagename)
    node = plSceneNode(name)
    rm.AddObject(loc,node)
    #get those lamps to export first
    for blObj in blScn.objects:
        if blObj.plasma_settings.noexport:
            continue
        if blObj.type == "LAMP":
            plScnObj = ExportSceneObject(rm, loc, blObj, vos)
            node.addSceneObject(plScnObj.key)
            
    for blObj in blScn.objects:
        if blObj.plasma_settings.noexport:
            continue
        if blObj.type != "LAMP":
            plScnObj = ExportSceneObject(rm, loc, blObj, vos)
            node.addSceneObject(plScnObj.key)
    return node


def ExportSceneObject(rm,loc,blObj, vos):
    print("[Exporting %s]"%blObj.name)
    so = plSceneObject(blObj.name)
    rm.AddObject(loc, so)
    so.sceneNode = rm.getSceneNode(loc).key
    hasCI = False
    
    blmods = blObj.plasma_settings.modifiers
    for mod_link in blmods:
        scene = blObj.users_scene[0] #Hack.  This should be made to support multiple scenes.
        if mod_link.name and modifiers.modDataExists(mod_link, scene):
            mod = modifiers.getModFromLink(mod_link, scene)
            modifiers.getClassFromModType(mod_link.modclass).Export(rm, so, blObj, mod)
    if blObj.plasma_settings.isdrawable:
        hasCI = True # TODO: make more informed decisions about when to export a CI
    if blObj.type == "LAMP":
        hasCI = True #force CI for lamp
        light = lights.ExportLamp(rm, loc, blObj, so).key
        vos.lights[blObj] = light
        so.addInterface(light)
    elif blObj.type == "EMPTY":
        hasCI = True
    else: # we try to export all remaining types as meshes, if it all possible
        try:
            blMesh = blObj.to_mesh(bpy.context.scene, True, 'RENDER')
            print("    as a mesh")
            physics = blObj.plasma_settings.physics.enabled
            if physics:
                print("    with a physical")
                so.sim = ExportSimInterface(rm,loc,blObj,blMesh,so).key
            #drawable
            isdrawable = blObj.plasma_settings.isdrawable
            print("    as a drawable")
            if isdrawable:
                so.draw = ExportDrawInterface(rm,loc,blObj,blMesh,so,hasCI,vos).key
            bpy.context.blend_data.meshes.remove(blMesh)
        except:
            pass
    if hasCI:
        print("With CI")
        so.coord = ExportCoordInterface(rm,loc,blObj,so).key
    return so

def ExportCoordInterface(rm,loc,blObj,so):
    ci = plCoordinateInterface(blObj.name)
    rm.AddObject(loc,ci)
    ci.owner = so.key
    #matrix fun
    l2w = utils.blMatrix44_2_hsMatrix44(blObj.matrix_local)
    ci.localToWorld = l2w
    ci.localToParent = l2w
    matcopy = blObj.matrix_local.__copy__()
    matcopy.invert()
    w2l = utils.blMatrix44_2_hsMatrix44(matcopy)
    ci.worldToLocal = w2l
    ci.parentToLocal = w2l
    return ci

def ExportDrawInterface(rm,loc,blObj, blMesh,so, hasCI,vos):
    di = plDrawInterface(blObj.name)
    rm.AddObject(loc,di)
    di.owner = so.key
    renderlevel = 0
    #deciding what render level/criteria is currently very crude
    if blMesh.vertex_colors.get("Alpha"): #if we have vertex alpha paint
        renderlevel |= (plRenderLevel.kBlendRendMajorLevel << plRenderLevel.kMajorShift)
    passindxstr = ""
    if blObj.pass_index != 0:
        passindxstr = str(blObj.pass_index)
    spanind = vos.geomgr.FindOrCreateDrawableSpans(rm, loc, renderlevel, 0, passindxstr)
    dspans,diind = vos.geomgr.AddBlenderMeshToDSpans(spanind,blObj, blMesh, hasCI, vos) #export our mesh
    di.addDrawable(dspans.key,diind)
    return di

def ExportSimInterface(rm,loc,blObj,blMesh,so):
    si = plSimulationInterface(blObj.name)
    rm.AddObject(loc,si)
    si.owner = so.key
    si.physical = physics.plPhysicalPanel.Export(rm,loc,blObj,blMesh,so).key
    return si

def register():
    bpy.utils.register_class(PlasmaExportAge)
    bpy.utils.register_class(PlasmaExportResourcePage)
    bpy.utils.register_class(lights.PlasmaVBakeLight)

def unregister():
    bpy.utils.unregister_class(lights.PlasmaVBakeLight)
    bpy.utils.unregister_class(PlasmaExportResourcePage)
    bpy.utils.unregister_class(PlasmaExportAge)
