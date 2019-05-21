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
from .fbx_geometry import *

#------------------------------------------------------------------
#   NurbsCurve
#------------------------------------------------------------------


def nurbsForm(cyclic):
    return ("Periodic" if cyclic else "Open")

    
class FbxNurbsCurve(FbxGeometryBase):
    propertyTemplate = (
"""
        PropertyTemplate: "FbxNurbsCurve" {
            Properties70:  {
                P: "Color", "ColorRGB", "Color", "",0.8,0.8,0.8
                P: "BBoxMin", "Vector3D", "Vector", "",0,0,0
                P: "BBoxMax", "Vector3D", "Vector", "",0,0,0
                P: "Primary Visibility", "bool", "", "",1
                P: "Casts Shadows", "bool", "", "",1
                P: "Receive Shadows", "bool", "", "",1
            }
        }
""")

    def __init__(self, subtype='NurbsCurve'):
        FbxGeometryBase.__init__(self, subtype, 'CURVE')
        self.template = self.parseTemplate('NurbsCurve', FbxNurbsCurve.propertyTemplate)
        self.isModel = True
        self.isObjectData = True
        self.points = CArray("Points", float, 4)
        self.knotVector = CArray("KnotVector", int, 1)
        

    def parseNodes(self, pnodes):
        rest = []
        for pnode in pnodes:
            if pnode.key == 'Points':
                self.points.parse(pnode)
            elif pnode.key == 'KnotVector':
                self.knotVector.parse(pnode)
            else:
                rest.append(pnode)

        return FbxGeometryBase.parseNodes(self, rest)

    
    def make(self, ob):        
        cu = ob.data
        spline = cu.splines[0]
        self.setMulti([
            ("GeometryVersion", 124),
            ("Type", "NurbsCurve"),
            ("NurbsCurveVersion", 100),
            ("Order", spline.order_u),
            ("Dimension", spline.point_count_u), 
            ("Rational", 0),
            ("Form", nurbsForm(spline.use_cyclic_u)),
        ])

        self.points.make( [v.co for v in spline.points] )
        nKnots = 2*spline.point_count_u
        self.knotVector.make( [n for n in range(-3,nKnots-4)] )

        return FbxGeometryBase.make(self, cu, ob)


    def writeFooter(self, fp):
        self.points.writeFbx(fp)
        self.knotVector.writeFbx(fp)
        FbxGeometryBase.writeFooter(self, fp)
        
        
    def build3(self):
        cu = fbx.data[self.id]
        spline = cu.splines.new('NURBS')
        first = True
        for pt in self.points.values:            
            if first:
                first = False
            else:
                spline.points.add()
            spline.points[-1].co = pt
        spline.use_bezier_u = False
        formU = self.get("Form")
        spline.use_cyclic_u = (formU == "Periodic")
        spline.use_endpoint_u = (formU != "Periodic")
        spline.order_u = self.get("Order")
        
        pass        


#------------------------------------------------------------------
#   Nurb geometry
#------------------------------------------------------------------
"""
class CNurbsCollection(FbxStuff):

    def __init__(self):
        self.splines = []
        

    def make(self, ob):
        cu = ob.data
        parent = fbx.nodes.objects[ob.name]
        for spline in cu.splines:
            mnode = CModel()
            mnode.name = spline.name
            snode = CNurbsSurface().make(spline)
            self.splines.append((mnode,snode))
            mnode.makeOOLink(parent)
            snode.makeOOLink(mnode)
            

    def writeFbx(self, fp):
        for mnode,snode in self.splines:
            mnode.writeFbx(fp)
            snode.writeFbx(fp)
            
"""

class FbxNurbsSurface(FbxGeometryBase):
    propertyTemplate = (
"""
        PropertyTemplate: "FbxNurbsSurface" {
            Properties70:  {
                P: "Color", "ColorRGB", "Color", "",0.8,0.8,0.8
                P: "BBoxMin", "Vector3D", "Vector", "",0,0,0
                P: "BBoxMax", "Vector3D", "Vector", "",0,0,0
                P: "Primary Visibility", "bool", "", "",1
                P: "Casts Shadows", "bool", "", "",1
                P: "Receive Shadows", "bool", "", "",1
            }
        }
""")

    def __init__(self, subtype='NurbsSurface'):
        FbxGeometryBase.__init__(self, subtype, 'CURVE')
        self.template = self.parseTemplate('NurbsSurface', FbxNurbsSurface.propertyTemplate)
        self.isModel = True
        self.isObjectData = True
        self.points = CArray("Points", float, 4)
        self.multiplicityU = CArray("MultiplicityU", int, 1)
        self.multiplicityV = CArray("MultiplicityV", int, 1)
        self.knotVectorU = CArray("KnotVectorU", int, 1)
        self.knotVectorV = CArray("KnotVectorV", int, 1)


    def parseNodes(self, pnodes):
        rest = []
        for pnode in pnodes:
            if pnode.key == 'Points':
                self.points.parse(pnode)
            elif pnode.key == 'MultiplicityU':
                self.multiplicityU.parse(pnode)
            elif pnode.key == 'MultiplicityV':
                self.multiplicityV.parse(pnode)
            elif pnode.key == 'KnotVectorU' : 
                self.knotVectorU.parse(pnode)
            elif pnode.key == 'KnotVectorV' : 
                self.knotVectorV.parse(pnode)
            else:
                rest.append(pnode)

        return FbxGeometryBase.parseNodes(self, rest)

    
    def make(self, ob):  
        print("D", ob, ob.data)
        su = ob.data
        spline = su.splines[0]
        self.setMulti([
            ("NurbsSurfaceVersion", 100),
            ("SurfaceDisplay", (4,4,4)),
            ("NurbsSurfaceOrder", (spline.order_u, spline.order_v)),
            ("Dimensions", (spline.point_count_u, spline.point_count_v)),
            ("Step", (spline.point_count_u, spline.point_count_v)),
            ("Form", (nurbsForm(spline.use_cyclic_u), nurbsForm(spline.use_cyclic_v))),
            ("FlipNormals", 0),
        ])

        for spline in su.splines:
            self.points.make( [v.co  for v in spline.points] )
            self.knotVectorU.make( [0]*spline.point_count_u + [1]*spline.point_count_u )
            self.knotVectorV.make( [0]*spline.point_count_v + [1]*spline.point_count_v )

        return FbxGeometryBase.make(self, su, ob)


    def writeFooter(self, fp):
        self.points.writeFbx(fp)
        self.knotVectorU.writeFbx(fp)
        self.knotVectorV.writeFbx(fp)
        FbxGeometryBase.writeFooter(self, fp)
        
        
    def build3(self):
        cu = fbx.data[self.id]
        dimU,dimV = self.get("Dimensions")
        stepU,stepV = self.get("Step")
        for n in range(dimU):
            spline = cu.splines.new('NURBS')
            points =  self.points.values[n*stepV:(n+1)*stepV]
            self.buildSpline(points, spline)
        for n in range(dimV):
            spline = cu.splines.new('NURBS')
            points = []
            for m in range(dimU):
                #print("     ", n, m, n + m*stepV)
                points.append(self.points.values[n + m*stepV])
            self.buildSpline(points, spline)
            
            
    def buildSpline(self, points, spline):            
        first = True
        for pt in points:            
            if first:
                first = False
            else:
                spline.points.add()
            spline.points[-1].co = pt
        spline.use_bezier_u = False
        spline.use_bezier_v = False
        formU,formV = self.get("Form")
        spline.use_cyclic_u = (formU == "Periodic")
        spline.use_cyclic_v = (formV == "Periodic")
        spline.use_endpoint_u = (formU != "Periodic")
        spline.use_endpoint_v = (formV != "Periodic")
        spline.order_u,spline.order_v = self.get("NurbsSurfaceOrder")
        
        pass        
