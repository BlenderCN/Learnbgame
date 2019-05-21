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
import sys
from . import fbx
from .fbx_basic import *
from .fbx_props import *



class FbxStuff(FbxPlug):

    def __init__(self, ftype):
        FbxPlug.__init__(self, ftype)
        self.properties = CProperties70()
        self.struct = {}
        self.template = {}
        
        
    def parseTemplate(self, ftype, template):
        template = self.properties.parseTemplate(ftype, template)        
        for key,value in template.items():
            self.template[key] = value
        return template            

    # Struct        

    def get(self, key):
        key = key.lower()
        try:
            return self.struct[key]
        except KeyError:
            fbx.debug("Unrecognized key %s" % key)
            print(self.struct)
        return self.properties.getProp(key, self.template)
        
    def set(self, key, value):
        key = key.lower()
        self.struct[key] = value
        
    def setMulti(self, list):
        for key,value in list:
            key = key.lower()
            self.struct[key] = value
            
    # Properties

    def setProp(self, key, value):
        self.properties.setProp(key, value, self.template)
        
    def setPropLong(self, name, ftype, supertype, anim, value):
        self.properties.setPropLong(name, ftype, supertype, anim, value)
        
    def getProp(self, key):
        try: 
            return self.properties.getProp(key, self.template)
        except KeyError:
            pass
        return self.struct[key]
        
    def getProp2(self, key):
        return self.properties.getProp2(key, self.template)
        
    def setProps(self, list):
        for key,value in list:
            self.setProp(key, value)
            

    def parseNodes(self, pnodes): 
        for pnode in pnodes:
            key= pnode.key.lower()
            try:
                elt = self.struct[key]
            except KeyError:
                elt = None
            
            if elt and isinstance(elt, FbxPlug):
                elt.parse(pnode)
            elif key == 'properties70':
                self.properties.parse(pnode)
            elif len(pnode.values) == 1:
                self.struct[key] = pnode.values[0]
            elif len(pnode.values) > 1:
                self.struct[key] = pnode.values  
            else:
                fbx.debug(pnode)
                pnode.write()
                halt
        return self    


    def writeFooter(self, fp):
        fp.write('    }\n')

        
    def writeProps(self, fp):        
        self.properties.write(fp, self.template)
        

    def writeStruct(self, fp):
        for key,value in self.struct.items():
            if isinstance(value, FbxPlug):
                value.writeFbx(fp)
            elif isinstance(value, str):
                fp.write('        %s: "%s"\n' % (key,value))
            elif isinstance(value, list) or isinstance(value, tuple):
                fp.write('        %s:' % key)
                c = ' '
                for x in value:
                    fp.write('%s %s' % (c,x))
                    c = ','
                fp.write('\n')
            else:
                fp.write('        %s: %s\n' % (key,value))
    

    def writeFbx(self, fp):
        self.writeHeader(fp)
        self.writeProps(fp)
        self.writeStruct(fp)
        self.writeFooter(fp)


#------------------------------------------------------------------
#   Connection node
#------------------------------------------------------------------

Prefix = {
    "Model" : "Model", 
    "Geometry" : "Geometry", 
    "Material" : "Material", 
    "Texture" : "Texture", 
    "Video" : "Video", 
    "AnimationStack" : "AnimStack", 
    "AnimationLayer" : "AnimLayer", 
    "AnimationCurveNode" : "AnimCurveNode", 
    "AnimationCurve" : "AnimCurve", 
    "NodeAttribute" : "NodeAttribute", 
    "Pose" : "Pose", 
    "Constraint" : "Constraint",

    "Null" : None
}
    
Prefix2 = {
    "Deformer" : {
        "Skin" : "Deformer", 
        "Cluster" : "SubDeformer",
        "BlendShape" : "Deformer", 
        "BlendShapeChannel" : "SubDeformer",
    },
}

class OOLink:
    def __init__(self, child, parent):
        self.child = child
        self.parent = parent
        self.channel = None
        
    def __repr__(self):
        return ("<OO %s -> %s>" % (self.child, self.parent))

    def writeFbx(self, fp):
        fp.write(
            '    ;%s::%s, %s::%s\n' % (self.child.prefix, self.child.name, self.parent.prefix, self.parent.name) +
            '    C: "OO",%d,%d\n\n' % (self.child.id, self.parent.id) )
    
        
class OPLink:
    def __init__(self, child, parent, channel):
        self.child = child
        self.parent = parent
        self.channel = channel
        
    def __repr__(self):
        return ("<OP %s -> %s, %s>" % (self.child, self.parent, self.channel))

    def writeFbx(self, fp):
        fp.write(
            '    ;%s::%s, %s::%s\n' % (self.child.prefix, self.child.name, self.parent.prefix, self.parent.name) +
            '    C: "OP",%d,%d, "%s"\n\n' % (self.child.id, self.parent.id, self.channel) )
        
        
class POLink:
    def __init__(self, child, parent, channel):
        self.child = child
        self.parent = parent
        self.channel = channel

    def __repr__(self):
        return ("<PO %s, %s -> %s>" % (self.child, self.channel, self.parent))

    def writeFbx(self, fp):
        fp.write(
            '    ;%s::%s, %s::%s\n' % (self.child.prefix, self.child.name, self.parent.prefix, self.parent.name) +
            '    C: "PO",%d, "%s",%d\n\n' % (self.child.id, self.channel, self.parent.id) )
        

class FbxObject(FbxStuff):

    def __init__(self, ftype, subtype, btype):
        FbxStuff.__init__(self, ftype)
        self.subtype = subtype
        self.rna = None
        try:
            self.prefix = Prefix[ftype]
        except KeyError:
            self.prefix = Prefix2[ftype][subtype]
        self.btype = btype
        self.links = []
        self.children = []
        self.active = False
        self.isObjectData = False


    def __repr__(self):
        return ("<CNode %d %s %s %s %s %s %s>" % (self.id, self.ftype, self.subtype, self.name, self.isModel, self.active, self.btype))
        
    # Overwrites
    
    def parse(self, pnode):     
        self.parseNodes(pnode.values[3:])
        return self


    def make(self, rna):
        FbxStuff.make(self)
        try:
            self.name = rna.name
        except AttributeError:
            pass

        self.rna = rna
        try:
            adata = rna.animation_data
        except AttributeError:
            adata = None

        if not adata:
            try:
                adata = rna.shape_keys.animation_data
            except AttributeError:
                adata = None

        if adata:
            act = adata.action
            if act:
                alayer = fbx.nodes.alayers[act.name]
                alayer.users.append(self)
        return self                
        
    
    def testDiff(self, parent):
        if self == parent:
            fbx.message("Linking to self %s" % self)
            halt

    
    def makeOOLink(self, parent):
        self.testDiff(parent)
        link = OOLink(self, parent)
        self.links.append(link)
        parent.children.append(link)

        
    def makeOPLink(self, parent, channel):
        self.testDiff(parent)
        link = OPLink(self, parent, channel)
        self.links.append(link)
        parent.children.append(link)

        
    def makePOLink(self, parent, channel):
        self.testDiff(parent)
        link = POLink(self, parent, channel)
        self.links.append(link)
        parent.children.append(link)

        
    def getBParentLink(self, btypes):
        if not isinstance(btypes, list):
            btypes = [btypes]
        for link in self.links:
            if link.parent.btype in btypes:
                return link
        return None
        
        
    def getBParent(self, btypes):
        link = self.getBParentLink(btypes)
        if link:
            return link.parent
        else:
            return None
        
        
    def getFParent(self, ftype):
        for link in self.links:
            if link.parent.ftype == ftype:
                return link.parent
        return None
        

    def getFParent2(self, ftype, subtype):
        for link in self.links:
            if (link.parent.ftype == ftype) and (link.parent.subtype == subtype):
                return link.parent
        return None                
        

    def getBChildLinks(self, btype):
        links = []
        for link in self.children:
            if link.child.btype == btype:
                links.append(link)
        return links

                
    def getChannelChildLinks(self, channel):
        links = []
        for link in self.children:
            if link.channel == channel:
                links.append(link)
        return links

                
    def writeHeader(self, fp):
        fp.write('    %s: %d, "%s::%s", "%s" {\n' % (self.ftype, self.id, self.prefix, self.name, self.subtype))


    def writeLinks(self, fp):
        if self.links:
            links = self.links
        else:
            links = [OOLink(self, fbx.root)]
        for link in links:
            link.writeFbx(fp)


#------------------------------------------------------------------
#   Root node
#------------------------------------------------------------------

class RootNode(FbxObject):

    def __init__(self):
        FbxObject.__init__(self, "Model", "", None)
        self.name = "RootNode"
        self.id = 0
        fbx.idstruct[0] = self
        self.active = True
        
    def writeFbx(self, fp):
        return

    def writeLinks(self, fp):
        return

#------------------------------------------------------------------
#   Node Attribute node
#------------------------------------------------------------------

class FbxNodeAttribute(FbxObject):

    def __init__(self, subtype, btype, typeflags=None):
        FbxObject.__init__(self, 'NodeAttribute', subtype, btype)
        self.typeflags = typeflags
        if typeflags:
            self.struct['TypeFlags'] = typeflags


    def parseNodes(self, pnodes):
        for pnode in pnodes:
            if pnode.key == 'Properties70':
                self.properties.parse(pnode)
            elif pnode.key == 'TypeFlags':
                self.typeflags = pnode.values[0]
        return self    


#------------------------------------------------------------------
#   Model node
#------------------------------------------------------------------

class CModel(FbxObject):
    propertyTemplate = (
"""
        PropertyTemplate: "FbxNode" {
            Properties70:  {
                P: "QuaternionInterpolate", "enum", "", "",0
                P: "RotationOffset", "Vector3D", "Vector", "",0,0,0
                P: "RotationPivot", "Vector3D", "Vector", "",0,0,0
                P: "ScalingOffset", "Vector3D", "Vector", "",0,0,0
                P: "ScalingPivot", "Vector3D", "Vector", "",0,0,0
                P: "TranslationActive", "bool", "", "",0
                P: "TranslationMin", "Vector3D", "Vector", "",0,0,0
                P: "TranslationMax", "Vector3D", "Vector", "",0,0,0
                P: "TranslationMinX", "bool", "", "",0
                P: "TranslationMinY", "bool", "", "",0
                P: "TranslationMinZ", "bool", "", "",0
                P: "TranslationMaxX", "bool", "", "",0
                P: "TranslationMaxY", "bool", "", "",0
                P: "TranslationMaxZ", "bool", "", "",0
                P: "RotationOrder", "enum", "", "",0
                P: "RotationSpaceForLimitOnly", "bool", "", "",0
                P: "RotationStiffnessX", "double", "Number", "",0
                P: "RotationStiffnessY", "double", "Number", "",0
                P: "RotationStiffnessZ", "double", "Number", "",0
                P: "AxisLen", "double", "Number", "",10
                P: "PreRotation", "Vector3D", "Vector", "",0,0,0
                P: "PostRotation", "Vector3D", "Vector", "",0,0,0
                P: "RotationActive", "bool", "", "",0
                P: "RotationMin", "Vector3D", "Vector", "",0,0,0
                P: "RotationMax", "Vector3D", "Vector", "",0,0,0
                P: "RotationMinX", "bool", "", "",0
                P: "RotationMinY", "bool", "", "",0
                P: "RotationMinZ", "bool", "", "",0
                P: "RotationMaxX", "bool", "", "",0
                P: "RotationMaxY", "bool", "", "",0
                P: "RotationMaxZ", "bool", "", "",0
                P: "InheritType", "enum", "", "",0
                P: "ScalingActive", "bool", "", "",0
                P: "ScalingMin", "Vector3D", "Vector", "",0,0,0
                P: "ScalingMax", "Vector3D", "Vector", "",1,1,1
                P: "ScalingMinX", "bool", "", "",0
                P: "ScalingMinY", "bool", "", "",0
                P: "ScalingMinZ", "bool", "", "",0
                P: "ScalingMaxX", "bool", "", "",0
                P: "ScalingMaxY", "bool", "", "",0
                P: "ScalingMaxZ", "bool", "", "",0
                P: "GeometricTranslation", "Vector3D", "Vector", "",0,0,0
                P: "GeometricRotation", "Vector3D", "Vector", "",0,0,0
                P: "GeometricScaling", "Vector3D", "Vector", "",1,1,1
                P: "MinDampRangeX", "double", "Number", "",0
                P: "MinDampRangeY", "double", "Number", "",0
                P: "MinDampRangeZ", "double", "Number", "",0
                P: "MaxDampRangeX", "double", "Number", "",0
                P: "MaxDampRangeY", "double", "Number", "",0
                P: "MaxDampRangeZ", "double", "Number", "",0
                P: "MinDampStrengthX", "double", "Number", "",0
                P: "MinDampStrengthY", "double", "Number", "",0
                P: "MinDampStrengthZ", "double", "Number", "",0
                P: "MaxDampStrengthX", "double", "Number", "",0
                P: "MaxDampStrengthY", "double", "Number", "",0
                P: "MaxDampStrengthZ", "double", "Number", "",0
                P: "PreferedAngleX", "double", "Number", "",0
                P: "PreferedAngleY", "double", "Number", "",0
                P: "PreferedAngleZ", "double", "Number", "",0
                P: "LookAtProperty", "object", "", ""
                P: "UpVectorProperty", "object", "", ""
                P: "Show", "bool", "", "",1
                P: "NegativePercentShapeSupport", "bool", "", "",1
                P: "DefaultAttributeIndex", "int", "Integer", "",-1
                P: "Freeze", "bool", "", "",0
                P: "LODBox", "bool", "", "",0
                P: "Lcl Translation", "Lcl Translation", "", "A",0,0,0
                P: "Lcl Rotation", "Lcl Rotation", "", "A",0,0,0
                P: "Lcl Scaling", "Lcl Scaling", "", "A",1,1,1
                P: "Visibility", "Visibility", "", "A",1
                P: "Visibility Inheritance", "Visibility Inheritance", "", "",1
            }
        }
""")

    def __init__(self, subtype, btype):
        FbxObject.__init__(self, 'Model', subtype, btype)
        self.template = self.parseTemplate('Model', CModel.propertyTemplate)
        self.setMulti([
            ('Version', 232),
            ('Shading', Y),
            ('Culling', "CullingOff"),
        ])
        self.rna = None


    def parseNodes(self, pnodes):
        for pnode in pnodes:
            if pnode.key == 'Properties70':
                self.properties.parse(pnode)
        return self    

        

