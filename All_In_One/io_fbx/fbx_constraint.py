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

#------------------------------------------------------------------
#   Constraint
#------------------------------------------------------------------

class FbxConstraint(FbxObject):

    def __init__(self, subtype, btype):
        FbxObject.__init__(self, 'Constraint', subtype, btype)        

    def make(self, cns, bone=None):
        FbxObject.make(self, cns)


#------------------------------------------------------------------
#   Look At
#------------------------------------------------------------------

class CLookAttribute(FbxNodeAttribute):
    propertyTemplate = (
"""    
    PropertyTemplate: "FbxLookAttribute" {
        Properties70:  {
        P: "Look", "enum", "", "",0
        }
    }
""")

    def __init__(self, subtype='Null'):
        FbxNodeAttribute.__init__(self, subtype, 'BONEATTR', "Null")
        self.template = self.parseTemplate('LookAttribute', CLookAttribute.propertyTemplate)


    def make(self, bone):
        self.bone = bone    
        FbxNodeAttribute.make(self, bone)
        self.setProps([
            ("Look", 0),
        ])
    
    
#------------------------------------------------------------------
#   IK
#------------------------------------------------------------------

class CIKEffectorAttribute(FbxNodeAttribute):
    propertyTemplate = (
"""    
    Properties70:  {
        P: "Color", "ColorRGB", "Color", "",1,0.25,0.25
        P: "Look", "enum", "", "",3
        P: "Size", "double", "Number", "",43.4242176923077
        P: "IK Reach Translation", "IK Reach Translation", "", "A",100
        P: "IK Reach Rotation", "IK Reach Rotation", "", "A",100
    }
""")

    def __init__(self, subtype='IKEffector'):
        FbxNodeAttribute.__init__(self, subtype, 'BONEATTR', "Marker")
        self.template = self.parseTemplate('IKEffectorAttribute', CIKEffectorAttribute.propertyTemplate)


    def make(self, bone):
        self.bone = bone    
        FbxNodeAttribute.make(self, bone)
        self.setProps([
            ("Color", (1,0.25,0.25)),
            ("Look", 3),
            ("Size", bone.length),
            ("IK Reach Translation", 100),
            ("IK Reach Rotation", 100),
        ])
        self.setMulti([
            ("Version", 232),
            ("Shading", U),
            ("Culling", "CullingOff"),
        ])


    
class FbxConstraintSingleChainIK(FbxConstraint):
    propertyTemplate = (
""" 
        PropertyTemplate: "FbxConstraintSingleChainIK" {
            Properties70:  {
                P: "Active", "bool", "", "",1
                P: "Lock", "bool", "", "",0
                P: "Weight", "Weight", "", "A",100
                P: "First Joint", "object", "", ""
                P: "End Joint", "object", "", ""
                P: "Effector", "object", "", ""
                P: "Pole Vector Object", "object", "", ""
                P: "SolverType", "enum", "", "",0
                P: "PoleVectorType", "enum", "", "",0
                P: "EvaluateTSAnim", "enum", "", "",0
                P: "PoleVector", "Vector", "", "A",0,1,0
                P: "Twist", "Number", "", "A",0
            }
        }
""")

    def __init__(self, subtype='Single Chain IK'):
        FbxConstraint.__init__(self, subtype, 'IK')
        self.template = self.parseTemplate('FbxConstraintSingleChainIK', FbxConstraintSingleChainIK.propertyTemplate)
        self.handle = None
            

    def make(self, cns, owner, amtnode):
        FbxConstraint.make(self, cns, owner)
        self.setProps([
            ("PoleVector", (1,0,0)),
        ])
        self.setMulti([
            ("Type", "Single Chain IK"),
            ("MultiLayer", 0),
        ])
        ob = cns.target
        if not ob:
            return
        elif ob.type == 'ARMATURE':
            self.handle = CNull()
            end = amtnode.bones[cns.subtarget]
        else:
            self.handle = fbx.nodes.objects[ob.name]            
            bone = owner.datum.children[0]
            end = amtnode.bones[bone.name]
        self.handle.makeOPLink(self, "Effector")
        self.handle.makeOOLink(amtnode.object)

        n = cns.chain_count-1
        first = owner
        while n > 0:
            first = first.parent    
            n -= 1
        self.makePOLink(first, "First Joint")
        self.makePOLink(end, "End Joint")
        
        return self
                        
        
    def build5(self):
        first = None
        end = None
        for link in self.links:
            if link.channel == "First Joint":
                first = link.parent
            elif link.channel == "End Joint":
                end = link.parent
        if first is None or end is None:
            fbx.debug("Constraint %s %s %s" % (self, first, end))
            
        last = end.getBParent('BONE')
        n = 1
        prev = last
        while prev != first:
            prev = prev.getBParent('BONE')
            n += 1
        
        rig = last.object
        pb = rig.pose.bones[last.name]
        cns = pb.constraints.new('IK')

        links = self.getChannelChildLinks("Effector")
        if links and fbx.settings.useIkEffectors:
            ob = fbx.data[links[0].child.id]
            subtar = ""
        else:
            scn = bpy.context.scene
            scn.objects.active = rig
            bpy.ops.object.mode_set(mode='EDIT')
            eb = rig.data.edit_bones[end.name]
            eb.parent = None
            bpy.ops.object.mode_set(mode='OBJECT')        
            subtar = end.name
        
        cns.name = self.name        
        cns.target = ob
        cns.subtarget = subtar
        cns.chain_count = n
        pv = self.getProp("PoleVector")
    
#------------------------------------------------------------------
#   FK
#------------------------------------------------------------------

class CFKEffectorAttribute(FbxNodeAttribute):
    propertyTemplate = (
"""    
    Properties70:  {
        P: "Color", "ColorRGB", "Color", "",1,1,0
        P: "Look", "enum", "", "",9
        P: "Size", "double", "Number", "",10.8560544230769
    }
""")

    def __init__(self, subtype='FKEffector'):
        FbxNodeAttribute.__init__(self, subtype, 'BONEATTR', "Marker")
        self.template = self.parseTemplate('FKEffectorAttribute', CFKEffectorAttribute.propertyTemplate)


    def make(self, bone):
        self.bone = bone    
        FbxNodeAttribute.make(self, bone)
        self.setProps([
            ("Color", (1,1,0)),
            ("Look", 9),
            ("Size", bone.length),
        ])


class CFKEffector(FbxConstraint):
    propertyTemplate = (
""" 
        Properties70:  {
            P: "RotationActive", "bool", "", "",1
            P: "InheritType", "enum", "", "",1
            P: "ScalingMax", "Vector3D", "Vector", "",0,0,0
            P: "DefaultAttributeIndex", "int", "Integer", "",0
            P: "Lcl Translation", "Lcl Translation", "", "A+",3.50746280908254e-007,-1.13542262327789,2.2554818967785
            P: "Lcl Rotation", "Lcl Rotation", "", "A+",7.30690044982444e-006,-1.30020513155814e-007,2.79452068481266e-008
            P: "Lcl Scaling", "Lcl Scaling", "", "A+",0.999999761579218,0.999999761579008,0.999999761579105
            P: "MultiTake", "int", "Integer", "",1
            P: "ManipulationMode", "enum", "", "",0
            P: "ScalingPivotUpdateOffset", "Vector3D", "Vector", "",0,0,0
            P: "SetPreferedAngle", "Action", "", "",0
            P: "PivotsVisibility", "enum", "", "",1
            P: "RotationLimitsVisibility", "bool", "", "",0
            P: "LocalTranslationRefVisibility", "bool", "", "",0
            P: "RotationRefVisibility", "bool", "", "",0
            P: "RotationAxisVisibility", "bool", "", "",0
            P: "ScalingRefVisibility", "bool", "", "",0
            P: "HierarchicalCenterVisibility", "bool", "", "",0
            P: "GeometricCenterVisibility", "bool", "", "",0
            P: "ReferentialSize", "double", "Number", "",12
            P: "DefaultKeyingGroup", "int", "Integer", "",0
            P: "DefaultKeyingGroupEnum", "enum", "", "",0
            P: "Pickable", "bool", "", "",1
            P: "Transformable", "bool", "", "",1
            P: "CullingMode", "enum", "", "",0
            P: "ShowTrajectories", "bool", "", "",0
            P: "LookUI", "enum", "", "",1
            P: "ResLevel", "enum", "", "",0
            P: "Length", "double", "Number", "",200
            P: "IKSync", "bool", "", "",1
            P: "ShowReach", "bool", "", "",1
        }    
""")

    def __init__(self, subtype='FKEffector'):
        FbxConstraint.__init__(self, subtype, 'FK')
        self.template = self.parseTemplate('FKEffector', CFKEffector.propertyTemplate)
        self.attribute = CFKEffectorAttribute()
            

    def make(self, cns, bone):
        FbxConstraint.make(self, cns)
        self.setProps([
        ])
        self.setMulti([
            ("Version", 232),
            ("Shading", U),
            ("Culling", "CullingOff"),
        ])
   