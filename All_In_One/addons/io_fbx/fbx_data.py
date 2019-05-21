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

import bpy

from . import fbx
from .fbx_basic import *
from .fbx_props import *
from .fbx_model import *
from . import fbx_null
from . import fbx_mesh
from . import fbx_deformer
from . import fbx_armature
from . import fbx_nurb
from . import fbx_lamp
from . import fbx_camera
from . import fbx_material
from . import fbx_texture
from . import fbx_image
from . import fbx_object
from . import fbx_anim
from . import fbx_constraint


class NodeStruct:

    def __init__(self):
        self.meshes = {}
        self.armatures = {}
        self.bones = {}
        self.limbs = {}
        self.curves = {}
        self.nurbs = {}
        self.textcurves = {}
        self.lamps = {}
        self.cameras = {}
        self.materials = {}
        self.textures = {}
        self.images = {}
        self.objects = {}
        self.actions = {}
        
        self.astacks = {}
        self.alayers = {}
        #self.anodes = {}
        #self.acurves = {}
        
    def getAllNodes(self):
        return (
            [fbx.root] +
            list(self.images.values()) +
            list(self.textures.values()) +
            list(self.materials.values()) +
            list(self.objects.values()) +
            list(self.meshes.values()) +
            list(self.bones.values()) +
            list(self.limbs.values()) +
            list(self.curves.values()) +
            list(self.nurbs.values()) +
            list(self.textcurves.values()) +
            list(self.armatures.values()) +
            list(self.lamps.values()) +
            list(self.cameras.values()) +
            list(self.actions.values()) +

            list(self.astacks.values()) +
            list(self.alayers.values()) +
            #list(self.anodes.values()) +
            #list(self.acurves.values()) +
            []
        )
        
        
#------------------------------------------------------------------
#   Parsing
#------------------------------------------------------------------

def parseNodes(pnode):
    fbx.root = RootNode()
    fbx.nodes = {}
    fbx.takes = []

    pObjectsNode = None
    pLinksNode = None
    pTakesNode = None
    
    for pnode1 in pnode.values:
        if pnode1.key == "Objects":
            pObjectsNode = pnode1
        elif pnode1.key == "Connections":
            pLinksNode = pnode1
        elif pnode1.key == "Takes":
            pTakesNode = pnode1
           
    if pObjectsNode:
        for pnode2 in pObjectsNode.values:
            createNode(pnode2)

    if pLinksNode:            
        for pnode2 in pLinksNode.values:
            parseLink(pnode2)

    if pObjectsNode:
        for pnode2 in pObjectsNode.values:
            parseObjectProperty(pnode2)

    if pTakesNode:
        for pnode2 in pTakesNode.values:
            node = fbx_anim.FbxTake()
            fbx.takes.append(node)
            node.parse(pnode2)
        

def parseLink(pnode):
    oo = pnode.values[0]
    if oo == "OO":
        child = fbx.idstruct[pnode.values[1]]
        parent = fbx.idstruct[pnode.values[2]]
        child.makeOOLink(parent)  
    elif oo == "OP":
        child = fbx.idstruct[pnode.values[1]]
        parent = fbx.idstruct[pnode.values[2]]
        channel = pnode.values[3]
        child.makeOPLink(parent, channel)  
    elif oo == "PO":
        child = fbx.idstruct[pnode.values[1]]
        parent = fbx.idstruct[pnode.values[3]]
        channel = pnode.values[2]
        child.makePOLink(parent, channel)  
    else:
        fbx.debug("parseLink %s" % oo)
        halt      
    

def createNode(pnode):
    id,name,subtype = nodeInfo(pnode)

    node = None
    if pnode.key == 'Geometry':
        if subtype == 'Mesh':
            node = fbx_mesh.FbxMesh(subtype)
        elif subtype == 'Shape':
            node = fbx_mesh.FbxShape(subtype)
        elif subtype == 'NurbsCurve':
            node = fbx_nurb.FbxNurbsCurve(subtype)
        elif subtype == 'NurbsSurface':
            node = fbx_nurb.FbxNurbsSurface()
    elif pnode.key == 'Material':
        node = fbx_material.FbxSurfaceMaterial(subtype)
    elif pnode.key == 'Texture':
        node = fbx_texture.FbxFileTexture(subtype)
    elif pnode.key == 'Video':
        node = fbx_image.CImage(subtype)
    elif pnode.key == 'Model':
        if subtype in fbx_object.Ftype2Btype:
            node = fbx_object.CObject(subtype)
        elif subtype == "Null":
            node = fbx_null.CNull(subtype)
        elif subtype == "LimbNode":
            node = fbx_armature.CBone(subtype)
        elif subtype in ["CameraSwitcher"]:
            node = fbx_null.CNull(subtype)
    elif pnode.key == 'NodeAttribute':            
        if subtype == "LimbNode":
            node = fbx_armature.CBoneAttribute()
        elif subtype == "Light":
            node = fbx_lamp.FbxLight()
        elif subtype == "Camera":
            node = fbx_camera.FbxCamera()
        elif subtype == "IKEffector":
            node = fbx_constraint.CIKEffectorAttribute()
        elif subtype == "FKEffector":
            node = fbx_constraint.CFKEffectorAttribute()
        elif subtype == "Null":
            node = fbx_null.FbxNullAttribute()
        elif subtype in ["CameraSwitcher"]:
            node = fbx_null.FbxNullAttribute()
    elif pnode.key == 'Pose':            
        node = fbx_armature.FbxPose()
    elif pnode.key == 'Bone':            
        node = fbx_armature.CBone()
    elif pnode.key == 'Constraint':            
        if subtype == "Single Chain IK":
            node = fbx_constraint.FbxConstraintSingleChainIK()
    elif pnode.key == 'Deformer':     
        if subtype == 'Skin':
            node = fbx_deformer.FbxSkin()
        elif subtype == 'Cluster':
            node = fbx_deformer.FbxCluster()        
        elif subtype == 'BlendShape':
            node = fbx_deformer.FbxBlendShape()        
        elif subtype == 'BlendShapeChannel':
            node = fbx_deformer.FbxBlendShapeChannel()        
    elif pnode.key == 'AnimationStack':   
        node = fbx_anim.CAnimationStack(subtype)
    elif pnode.key == 'AnimationLayer':            
        node = fbx_anim.CAnimationLayer(subtype)
    elif pnode.key == 'AnimationCurveNode':            
        node = fbx_anim.FbxAnimationCurveNode(subtype)
    elif pnode.key == 'AnimationCurve':            
        node = fbx_anim.FbxAnimationCurve(subtype)

    if node:
        node.setid(id, name)
        fbx.nodes[node.id] = node        
    else:
        fbx.debug("Bug: %s %s %s" % (pnode.key, subtype, pnode))


def parseObjectProperty(pnode):
    id,name,subtype = nodeInfo(pnode)
    fbx.nodes[id].parse(pnode)        
    
#------------------------------------------------------------------
#   Building
#------------------------------------------------------------------

    
def buildObjects(context):

    fbx.data = {}
    scn = context.scene
    fbx.setCsysChangers()
    
    fbx.message("  Creating nodes")
    
    for node in fbx.nodes.values():
        if node.ftype == "Geometry":
            if node.subtype == "Mesh":
                data = bpy.data.meshes.new(node.name)
            elif node.subtype == "NurbsCurve":
                data = bpy.data.curves.new(node.name, 'CURVE')
            elif node.subtype == "NurbsSurface":
                data = bpy.data.curves.new(node.name, 'SURFACE')
            elif node.subtype == "Shape":
                continue
        elif node.ftype == "Material":
            data = bpy.data.materials.new(node.name)
        elif node.ftype == "Texture":
            data = bpy.data.textures.new(node.name, type='IMAGE')
        elif node.ftype == "Video":
            continue
            bpy.data.images.new(node.name)
        elif node.ftype == "AnimationLayer":
            data = bpy.data.actions.new(node.name)
        #elif node.ftype == "AnimationCurve":
        #    data = bpy.data.fcurves.new(node.name)
        elif node.ftype == "Pose":
            data = node
        elif node.ftype == "Constraint":
            data = node
        elif node.ftype == "NodeAttribute":
            if node.typeflags == "Light":
                data = bpy.data.lamps.new(node.name, type='POINT')
            elif node.typeflags == "Camera":
                data = bpy.data.cameras.new(node.name)
            else:
                #print("Skipped", node)
                continue
        else:
            #print("Skipped", node)
            continue
            
        fbx.data[node.id] = data
        
    for node in fbx.nodes.values():
        if node.ftype == "Model":
            print(node)
            if node.subtype in ["LimbNode"]:
                continue
            elif node.subtype == "Null":
                btype = node.getBtype()
                if btype == 'ARMATURE':
                    amt = bpy.data.armatures.new(node.name)
                    data = bpy.data.objects.new(node.name, amt)
                    scn.objects.link(data)
                elif btype == 'EMPTY':
                    data = bpy.data.objects.new(node.name, None)
                    scn.objects.link(data)
            else:
                for link in node.children:
                    if link.child.subtype == node.subtype:
                        data = bpy.data.objects.new(node.name, fbx.data[link.child.id])
                        scn.objects.link(data)
                        break
            fbx.data[node.id] = data
                    
    fbx.message("  Building objects")
    for node in fbx.nodes.values():
        node.build1()
    for node in fbx.nodes.values():
        node.build2()
    for node in fbx.nodes.values():
        node.build3()
    for node in fbx.nodes.values():
        node.build4()
    for node in fbx.nodes.values():
        node.build5()         
        
    fbx.message("  Building takes")
    if len(fbx.takes) > 1:
        take = fbx.takes[-1]
        take.build()
        

#------------------------------------------------------------------
#   Activating
#------------------------------------------------------------------

def activateGeometryData(datum):
    for mat in datum.materials:
        activateData(mat)
    skeys = datum.shape_keys
    if skeys and skeys.animation_data:
        act = skeys.animation_data.action
        if act:
            fbx.active.actions[act.name] = act


def activateData(datum):

    if datum is None:
        return
                
    elif isinstance(datum, bpy.types.Object):
        if (not fbx.settings.selectedOnly) or datum.select:
            fbx.active.objects[datum.name] = datum        
            activateData(datum.data)

    elif isinstance(datum, bpy.types.Mesh):
        fbx.active.meshes[datum.name] = datum        
        activateGeometryData(datum)

    elif isinstance(datum, bpy.types.SurfaceCurve):
        fbx.active.nurbs[datum.name] = datum        
        activateGeometryData(datum)

    elif isinstance(datum, bpy.types.TextCurve):
        pass

    elif isinstance(datum, bpy.types.Curve):
        fbx.active.curves[datum.name] = datum        
        activateGeometryData(datum)

    elif isinstance(datum, bpy.types.Armature):
        fbx.active.armatures[datum.name] = datum        

    elif isinstance(datum, bpy.types.Material):
        fbx.active.materials[datum.name] = datum        
        for mtex in datum.texture_slots:
            if mtex:
                tex = mtex.texture
                if tex and tex.type == 'IMAGE':
                    activateData(tex)

    elif isinstance(datum, bpy.types.Texture):
        fbx.active.textures[datum.name] = datum      
        img = datum.image
        if img:
            activateData(img)

    elif isinstance(datum, bpy.types.Image):
        fbx.active.images[datum.name] = datum        

    elif isinstance(datum, bpy.types.Camera):
        fbx.active.cameras[datum.name] = datum        

    elif isinstance(datum, bpy.types.Lamp):
        fbx.active.lamps[datum.name] = datum        

    if hasattr(datum, "animation_data") and datum.animation_data:
        act = datum.animation_data.action
        if act:
            fbx.active.actions[act.name] = act

#------------------------------------------------------------------
#   Making
#------------------------------------------------------------------

def makeNodes(context):

    resetFbx()
    fbx.setCsysChangers()
    fbx.root = RootNode()
    fbx.nodes = NodeStruct()
    fbx.active = NodeStruct()
    
    # First pass: activate
    
    for ob in context.scene.objects:
        if ob.select:
            activateData(ob)
    
    print(fbx.active.actions.items())
    
    # Second pass: create nodes
    
    for ob in fbx.active.objects.values():
        if ob.type == 'MESH':
            fbx.nodes.meshes[ob.data.name] = fbx_mesh.FbxMesh()
        elif ob.type == 'ARMATURE':
            fbx.nodes.armatures[ob.data.name] = fbx_armature.CArmature()
        elif ob.type == 'CURVE':
            #if isinstance(ob.data, bpy.types.SurfaceCurve):
            #    fbx.nodes.nurbs[ob.data.name] = fbx_nurb.CNurbsCollection()
            if isinstance(ob.data, bpy.types.TextCurve):
                pass
            else:
                fbx.nodes.curves[ob.data.name] = fbx_nurb.FbxNurbsCurve()
        elif ob.type == 'SURFACE':
            fbx.nodes.nurbs[ob.data.name] = fbx_nurb.FbxNurbsSurface()
        elif ob.type == 'LAMP':
            fbx.nodes.lamps[ob.data.name] = fbx_lamp.FbxLight()
        elif ob.type == 'CAMERA':
            fbx.nodes.cameras[ob.data.name] = fbx_camera.FbxCamera()
        elif ob.type == 'EMPTY':
            pass
        else:
            fbx.debug("Unrecognized object %s t %s" % (ob, ob.type))
            halt
            continue
        fbx.nodes.objects[ob.name] = fbx_object.CObject(ob.type)
        
    for mat in fbx.active.materials.values():
        fbx.nodes.materials[mat.name] = fbx_material.FbxSurfaceMaterial()

    for tex in fbx.active.textures.values():
        if tex.type == 'IMAGE':
            fbx.nodes.textures[tex.name] = fbx_texture.FbxFileTexture()

    for img in fbx.active.images.values():
        fbx.nodes.images[img.name] = fbx_image.CImage()

    for act in fbx.active.actions.values():        
        fbx.nodes.alayers[act.name] = fbx_anim.CAnimationLayer()

    # Third pass: make the nodes
    
    for ob in fbx.active.objects.values():
        if ob.type == 'MESH':
            node = fbx.nodes.meshes[ob.data.name]
        elif ob.type == 'CURVE':
            node = fbx.nodes.curves[ob.data.name]            
        elif ob.type == 'SURFACE':
            node = fbx.nodes.nurbs[ob.data.name]
        else:
            continue
        
        print("AO", ob, node)

        node.make(ob)
        fbx.nodes.objects[ob.name].make(ob)
        rig = ob.parent
        if rig and rig.type == 'ARMATURE':
            fbx.nodes.armatures[rig.data.name].addDeformer(node, ob)             

    for ob in fbx.active.objects.values():
        if ob.type == 'ARMATURE':
            amt = fbx.nodes.armatures[ob.data.name]
            amt.make(ob)
            fbx.nodes.objects[ob.name].make(ob)

    for ob in fbx.active.objects.values():
        if ob.type == 'LAMP':
            fbx.nodes.lamps[ob.data.name].make(ob)
        elif ob.type == 'CAMERA':
            fbx.nodes.cameras[ob.data.name].make(ob)
        elif ob.type == 'EMPTY':
            pass
        else:
            continue
        fbx.nodes.objects[ob.name].make(ob)
            
    for mat in fbx.active.materials.values():
        fbx.nodes.materials[mat.name].make(mat)

    for tex in fbx.active.textures.values():
        if tex.type == 'IMAGE':
            fbx.nodes.textures[tex.name].make(tex)

    for img in fbx.active.images.values():
        fbx.nodes.images[img.name].make(img)


    # Fourth pass: link actions
    
    for act in fbx.active.actions.values():        
        fbx.nodes.alayers[act.name].make(act)
            
    if fbx.nodes.alayers:
        first = True
        for alayer in fbx.nodes.alayers.values():
            if first:
                astack = fbx.nodes.astacks[alayer.name] = fbx_anim.CAnimationStack().make(alayer)
                first = False
            alayer.makeOOLink(astack)


def makeTakes(context):

    fbx.takes = {}
    
    for astack in fbx.nodes.astacks.values():
        fbx.takes[astack.name] = fbx_anim.FbxTake().make(context.scene, astack.name)
    
    #for act in fbx.active.actions.values():   
    #    fbx.takes[act.name] = fbx_anim.FbxTake().make(context.scene, act)
    

