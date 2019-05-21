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
import math
from . import fbx
from . import fbx_token
from .fbx_basic import *

#------------------------------------------------------------------
#   Properties70 nodes
#------------------------------------------------------------------

class CProperties70(FbxPlug):
    def __init__(self):
        FbxPlug.__init__(self, "Properties70")
        self.properties = {}
        

    def parseTemplate(self, ftype, template):
        try:
            return fbx.templates[ftype]
        except KeyError:
            pass
        
        proplist = fbx_token.tokenizePropertyString(template)
        template = {}
        for prop in proplist:
            template[prop[0]] = CPropertyTemplate(prop)
        
        fbx.templates[ftype] = template
        return template
        
    
    def setProp(self, key, value, template):
        try:
            prop = self.properties[key]
        except KeyError:
            prop = None
        if prop is None:
            try:
                prop = self.properties[key] = template[key].newProp(key)
            except KeyError:
                return
        prop.value = value
        prop.isSet = True
        

    def setPropLong(self, name, ftype, supertype, anim, value):
        try:
            prop = self.properties[name]
        except KeyError:
            prop = None
        if prop is None:
            prop = self.properties[name] = newProp(name, ftype, supertype, anim)
        print("  ", prop)
        prop.value = value
        prop.isSet = True

            
    def getProp2(self, key, template):
        if isinstance(key, list):
            for key1 in key:
                try:
                    return True,self.properties[key1].value
                except KeyError:
                    pass
        else:                   
            try:
                return True,self.properties[key].value
            except KeyError:
                pass
        return False,template[key].value        


    def getProp(self, key, template):
        _,value = self.getProp2(key, template)
        return value

    
    def write(self, fp, template):
        if not self.properties:
            return
        fp.write('        Properties70:  {\n')
        for key,prop in self.properties.items():
            if prop.isSet:
                prop.write(fp)
            else:
                default = template[key].value
                if prop.differ(template[key].value):
                    prop.write(fp)
        fp.write('        }\n')


    def parse(self, pnode0):    
        global TypedNode
        for pnode in pnode0.values:
            if pnode.key == "P":
                name = pnode.values[0]
                ftype = pnode.values[1]
                supertype = pnode.values[2]
                anim = pnode.values[3]
                name = pnode.values[0]
                node = newProp(name, ftype, supertype, anim).parse(pnode)
                self.properties[node.name] = node
        return self                

    def make(self, props):
        if None in props:
            halt
        for node in props:
            self.properties[node.name] = node
        return self


    def nodes(self):        
        return self.properties.values()


#------------------------------------------------------------------
#   New prop
#------------------------------------------------------------------

SimpleTypes = [
        "int", "short", "float", "bool", "enum", "double", "Number",
        "Int", "Short", "Float", "Bool", "Enum", "Double",
        "ULongLong", "Shape",
        "FieldOfView",
        "Time", "KTime",
        "Visibility", "Visibility Inheritance"
]
    
StringTypes = [
        "KString", "object", "Url", "DateTime", "Filename"
]
    
VectorTypes = [
        "Vector", "Vector3D",
        "Lcl Translation", "Lcl Rotation", "Lcl Scaling",
        "Color", "ColorRGB"
]
    
CompoundTypes = [
        "Compound",
]

def newProp(name, ftype, supertype, anim):        
    if ftype in SimpleTypes:
       prop = CProperty(name, ftype, supertype, anim)
    elif ftype in VectorTypes:
        prop = CVectorProperty(name, ftype, supertype, anim)
    elif ftype in StringTypes:
        prop = CStringProperty(name, ftype, supertype, anim)
    elif ftype in CompoundTypes:
        prop = CCompoundProperty(name, ftype, supertype, anim)
    else:
        fbx.debug("Unknown proptype %s" % ftype)
        halt
    return prop
        
#------------------------------------------------------------------
#   Property template node
#------------------------------------------------------------------

class CPropertyTemplate:
    
    def __init__(self, values):
        self.name = values[0]
        self.ftype = values[1]
        self.supertype = values[2]
        self.anim = values[3]
        if len(values) == 5:
            self.value = values[4]
        else:
            self.value = tuple(values[4:])
        
    def __repr__(self):
        return ("<PropTemplate n %s t %s s %s a %s v %s>" % (self.name, self.ftype, self.supertype, self.anim, self.value))
            
    def newProp(self, name):
        return newProp(name, self.ftype, self.supertype, self.anim)
        
            
        
#------------------------------------------------------------------
#   Property node
#------------------------------------------------------------------

class CProperty(FbxPlug):

    def __init__(self, name, ftype, supertype, anim):
        FbxPlug.__init__(self, ftype)
        self.name = name
        self.value = None
        self.supertype = supertype
        self.anim = anim
        self.isSet = False
        
    def __repr__(self):
        return ("<CProperty n:%s v:%s t:%s s:%s a:%s i:%s>" % 
                (self.name, self.value, self.ftype, self.supertype, self.anim, self.isSet))     
    
    def parse(self, pnode):
        values = pnode.values
        self.name = values[0]
        self.ftype = values[1]
        self.supertype = values[2]
        self.anim = values[3]
        if len(values) > 5:
            self.value = values[4:]
        elif len(values) == 5:
            self.value = values[4]
        elif values[1] in ["Compound"]:
            pass
        else:
            fbx.debug("%s: %s" % (pnode.key, pnode.values))
            halt
        return self    

    def set(self, name, value, anim):
        self.name = name
        self.value = value
        self.anim = anim
        return self

    def differ(self, value):
        return (self.value != value)
        
        
    def write(self, fp):
        fp.write('            P: "%s", "%s", "%s", "%s", %s\n' % (self.name, self.ftype, self.supertype, self.anim, self.flatten()))

    def flatten(self):
        return self.value
        
    def build3(self):
        return self.value


class CStringProperty(CProperty):

    def flatten(self):
        return '"%s"' % self.value

    
class CVectorProperty(CProperty):

    def flatten(self):
        return "%.5g, %.5g, %.5g" % (round(self.value[0]), round(self.value[1]), round(self.value[2]))


class CCompoundProperty(CProperty):

    def write(self, fp):
        print(self.name, self.supertype, self.anim, self.value)
        print(self)
        basetype = "Number"
        fp.write('            P: "%s|X", "%s", "%s", "%s", %s\n' % (self.name, basetype, self.supertype, self.anim, self.value[0]))
        fp.write('            P: "%s|Y", "%s", "%s", "%s", %s\n' % (self.name, basetype, self.supertype, self.anim, self.value[1]))
        fp.write('            P: "%s|Z", "%s", "%s", "%s", %s\n' % (self.name, basetype, self.supertype, self.anim, self.value[2]))


