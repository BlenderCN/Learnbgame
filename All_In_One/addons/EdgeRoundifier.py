# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    "name": "Edge Roundifier",
    "category": "Mesh",
    'author': 'Piotr Komisarczyk (komi3D)',
    'version': (0, 0, 1),
    'blender': (2, 7, 1),
    'location': 'SPACE > Edge Roundifier or CTRL-E > Edge Roundifier',
    'description': 'Mesh editing script allowing edge rounding',
    'wiki_url': '',
    'tracker_url': '',
    'category': 'Mesh'
}

import math

import bmesh
import bpy
import bpy.props
from mathutils import Vector


# variable controlling all print functions
debug = False

def debugPrint(*text):
    if debug:
        for t in text:
            print(text)


###################################################################################
####################### Geometry and math calcualtion methods #####################

class CalculationHelper:
    def __init__(self):
        '''
        Constructor
        '''
    def getLineCoefficientsPerpendicularToVectorInPoint(self, point, vector):
        x, y, z = point
        xVector, yVector, zVector = vector
        destinationPoint = (x + yVector, y - xVector, z)
        return self.getCoefficientsForLineThrough2Points(point, destinationPoint)

    def getQuadraticRoots(self, coef):
        if len(coef) != 3:
            return NaN
        else:
            a, b, c = coef
            delta = self.getDelta(coef)
            if delta == 0:
                x = -b / (2 * a)
                return (x, x)
            elif delta < 0:
                return None
            else :
                x1 = (-b - math.sqrt(delta)) / (2 * a)
                x2 = (-b + math.sqrt(delta)) / (2 * a)
                return (x1, x2)

    def getDelta(self, coef):
        delta = math.pow(coef[1], 2) - 4 * coef[0] * coef[2]
        return delta

    def getCoefficientsForLineThrough2Points(self, point1, point2):
        x1, y1, z1 = point1
        x2, y2, z2 = point2
        #TODO how to handle other planes YZ, XZ???
        xabs = math.fabs(x2 - x1)
        yabs = math.fabs(y2 - y1)
        debugPrint("XABS = ", xabs)
        debugPrint("YABS = ", yabs)
        if xabs <= 0.0001:
            return None #this means line x= edgeCenterX
        if yabs <= 0.0001:
            A = 0
            B = y1
            return A, B
        A = (y2 - y1) / (x2 - x1)
        B = y1 - (A * x1)
        return (A, B)

    def getLineCircleIntersections(self, lineAB, circleMidPoint, radius):
        # (x - a)**2 + (y - b)**2 = r**2 - circle equation
        # y = A*x + B - line equation
        # f * x**2 + g * x + h = 0 - quadratic equation
        A, B = lineAB
        a, b = circleMidPoint
        f = 1 + math.pow(A, 2)
        g = -2 * a + 2 * A * B - 2 * A * b
        h = math.pow(B, 2) - 2 * b * B - math.pow(radius, 2) + math.pow(a, 2) + math.pow(b, 2)
        coef = [f,g,h]
        roots = self.getQuadraticRoots(coef)
        if roots != None:
            x1 = roots[0]
            x2 = roots[1]
            point1 = [x1, A * x1 + B]
            point2 = [x2, A * x2 + B]
            return (point1, point2)
        else:
            return None
        
    def getLineCircleIntersectionsWhenXPerpendicular(self, xValue, circleMidPoint, radius):
        # (x - a)**2 + (y - b)**2 = r**2 - circle equation
        # x = xValue - line equation
        # f * x**2 + g * x + h = 0 - quadratic equation
        # TODO fix it for planes other then
        a, b = circleMidPoint
        f = 1
        g = -2 * b
        h = math.pow(a, 2) + math.pow(b, 2) + math.pow(xValue, 2) - 2* a * xValue  -math.pow(radius, 2)
        coef = [f,g,h]
        roots = self.getQuadraticRoots(coef)
        if roots != None:
            y1 = roots[0]
            y2 = roots[1]
            point1 = [xValue, y1]
            point2 = [xValue, y2]
            return (point1, point2)
        else:
            return None

    def getEdgeLength(self, point1, point2):
        x1, y1, z1 = point1
        x2, y2, z2 = point2
        #TODO assupmtion Z=0
        length = math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2) + math.pow(z2 - z1, 2))
        return length

    # point1 is the point near 90 deg angle
    def getAngle(self, point1, point2, point3):
        distance1 = self.getEdgeLength(point1, point2)
        distance2 = self.getEdgeLength(point2, point3)
        cos = distance1 / distance2
        alpha = math.acos(cos)
        degAlpha = (alpha / (math.pi * 2)) * 360
        return (alpha, degAlpha)

    def getVectorBetween2VertsXYZ(self, vert1, vert2):
        output = [vert2[0] - vert1[0], vert2[1] - vert1[1], vert2[2] - vert1[2]]
        return output

    def getVectorLength(self, vector):
        return self.getEdgeLength([0, 0, 0], vector)

    def getNormalizedVector(sefl, vector):
        v = Vector(vector)
        return v.normalized()

    def getCenterBetween2VertsXYZ(self, vert1, vert2):
        vector = self.getVectorBetween2VertsXYZ(vert1, vert2)
        halfvector = [vector[0]/2,vector[1]/2,vector[2]/2]
        center = (vert1[0] + halfvector[0], vert1[1] + halfvector[1], vert1[2] + halfvector[2])
        return center

########################################################
################# SELECTION METHODS ####################

class SelectionHelper:
    def selectVertexInMesh(self, mesh, vertex):
        bpy.ops.object.mode_set(mode = "OBJECT")
        for v in mesh.vertices:
            if (v.co[0] == vertex[0]) and (v.co[1] == vertex[1]) and (v.co[2] == vertex[2]):
                v.select = True
                break

        bpy.ops.object.mode_set(mode = "EDIT")
        
    def getSelectedVertex(self, mesh):
        bpy.ops.object.mode_set(mode = "OBJECT")
        for v in mesh.vertices:
            if v.select == True :
                bpy.ops.object.mode_set(mode = "EDIT")
                return v

        bpy.ops.object.mode_set(mode = "EDIT")
        return None

    def refreshMesh(self, bm, mesh):
        bpy.ops.object.mode_set(mode = 'OBJECT')
        bm.to_mesh(mesh)
        bpy.ops.object.mode_set(mode = 'EDIT')



###################################################################################

class EdgeRoundifier(bpy.types.Operator):
    """Edge Roundifier"""      # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "mesh.edge_roundifier"        # unique identifier for buttons and menu items to reference.
    bl_label = "Edge Roundifier"  # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    threshold=0.0005 #used for remove doubles and edge selection at the end
#TODO: 
# 1) offset - move arcs perpendicular to edges
# 2) allow other spin axes X and Y (global)

    r = bpy.props.FloatProperty(name = '', default = 1, min = 0.00001, max = 1000.0, step = 0.1, precision = 3)
    a = bpy.props.FloatProperty(name = '', default = 180, min = 0.1, max = 180.0, step = 0.5, precision = 1)
    n = bpy.props.IntProperty(name = '', default = 4, min = 1, max = 100, step = 1)
    flip = bpy.props.BoolProperty(name = 'flip', default = False)
    invertAngle = bpy.props.BoolProperty(name = 'invertAngle', default = False)
    fullCircles = bpy.props.BoolProperty(name = 'fullCircles', default = False)
    removeDoubles = bpy.props.BoolProperty(name = 'removeDoubles', default = False)
    #FUTURE TODO: OFFSET
    #offset = bpy.props.BoolProperty(name = 'offset', default = False)
    
    modeItems = [('Radius', "Radius", ""), ("Angle", "Angle","")]
    modeEnum = bpy.props.EnumProperty(
        items = modeItems,
        name = '',
        default = 'Radius',
        description = "Edge Roundifier mode")
    
    angleItems = [('Other', "Other", "User defined angle"),('180', "180", "HemiCircle"), ('120', "120", "TriangleCircle"),
                    ('90', "90", "QuadCircle"), ('60', "60", "HexagonCircle"),
                    ('45', "45", "OctagonCircle"), ('30', "30", "12-gonCircle")]

    angleEnum = bpy.props.EnumProperty(
        items = angleItems,
        name = '',
        default = 'Other',
        description = "Presets prepare standard angles and calculate proper ray")

    refItems = [('ORG', "Origin", "Use Origin Location"), ('CUR', "3D Cursor", "Use 3DCursor Location")]
    referenceLocation = bpy.props.EnumProperty(
        items = refItems,
        name = '',
        default = 'ORG',
        description = "Reference location used by Edge Roundifier to calculate initial centers of drawn arcs")

    calc = CalculationHelper()
    sel = SelectionHelper()

    def prepareMesh(self,context):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')

        mesh = context.scene.objects.active.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        edges = self.getSelectedEdges(bm)
        return edges, mesh, bm

    def prepareParameters(self):

        parameters = { "plane" : "XY"}
        parameters["radius"] = self.r
        parameters["angle"] = self.a
        parameters["segments"] = self.n
        parameters["flip"] = self.flip
        parameters["fullCircles"] = self.fullCircles
        parameters["invertAngle"] = self.invertAngle
        parameters["angleEnum"] = self.angleEnum
        parameters["modeEnum"] = self.modeEnum 
        parameters["refObject"] = self.referenceLocation
        parameters["removeDoubles"] = self.removeDoubles
        #FUTURE TODO OFFSET
        #parameters["offset"] = self.offset
        return parameters

    def draw(self, context):
        layout = self.layout
        layout.label('Radius < edge_length/2 causes arcs to disappear.')
        row = layout.row(align = False)
        row.label('Mode:')
        row.prop(self, 'modeEnum', expand = True, text = "a")
        row = layout.row(align = False)
        layout.label('Quick angle:')
        layout.prop(self, 'angleEnum', expand = True, text = "abv")
        row = layout.row(align = False)
        row.label('Angle:')
        row.prop(self, 'a')
        row = layout.row(align = False)
        row.label('Radius:')
        row.prop(self, 'r')
        row = layout.row(align = True)
        row.label('Segments:')
        row.prop(self, 'n', slider = True)
        row = layout.row(align = False)
        row.prop(self, 'flip')
        row.prop(self, 'invertAngle')
        row = layout.row(align = False)
        row.prop(self, 'fullCircles')
        row.prop(self, 'removeDoubles')
        #FUTURE TODO OFFSET
        #row.prop(self, 'offset')
        
        layout.label('Reference Location:')
        layout.prop(self, 'referenceLocation', expand = True, text = "a")

    def execute(self, context):

        edges, mesh, bm = self.prepareMesh(context)
        parameters = self.prepareParameters()
        
        debugPrint ("EDGES ", edges)
        
        if len(edges) > 0:
            self.roundifyEdges(edges, parameters, bm, mesh)

            if parameters["removeDoubles"] == True:
                bpy.ops.mesh.select_all(action = "SELECT")
                bpy.ops.mesh.remove_doubles(threshold = self.threshold)
                bpy.ops.mesh.select_all(action = "DESELECT")
            
            self.selectEdgesAfterRoundifier(context, edges)
        else:
            debugPrint("No edges selected!")
            self.report({'INFO'}, "Edge Roundifier: No edges selected!")
        return {'FINISHED'} 
       
##########################################
    def roundifyEdges(self, edges, parameters, bm, mesh):
        for e in edges:
            self.roundify(e, parameters, bm, mesh)


    def getEdgeInfoAfterTranslation(self, edge, objectLocation):
        vertices = self.getVerticesFromEdge(edge)
        v1, v2 = vertices
        V1 = [v1.co.x, v1.co.y, v1.co.z]
        V2 = [v2.co.x, v2.co.y, v2.co.z]
        OriginalVertices = [V1, V2]
        V1Translated = self.translateByVector(V1, objectLocation)
        V2Translated = self.translateByVector(V2, objectLocation)
        edgeVector = self.calc.getVectorBetween2VertsXYZ(V1, V2)
        edgeLength = self.calc.getVectorLength(edgeVector)
        edgeCenter = self.calc.getCenterBetween2VertsXYZ(V1Translated, V2Translated)
        debugPrint("Edge info======================================")
        debugPrint("V1 info==============")
        debugPrint(V1)
        debugPrint("V2 info==============")
        debugPrint(V2)
        debugPrint("V1 TRANS info==============")
        debugPrint(V1Translated)
        debugPrint("V2 TRANS info==============")
        debugPrint(V2Translated)
        debugPrint("Edge Length==============")
        debugPrint(edgeLength)
        debugPrint("Edge Center==============")
        debugPrint(edgeCenter)
        debugPrint("Edge info======================================")
        return OriginalVertices, V1Translated, V2Translated, edgeVector, edgeLength, edgeCenter


    def roundify(self, edge, parameters, bm, mesh):
        # assumption Z=0 for all vertices

        # BECAUSE ALL DATA FROM MESH IS IN LOCAL COORDINATES
        # AND SPIN OPERATOR WORKS ON GLOBAL COORDINATES
        # WE FIRST NEED TO TRANSLATE ALL INPUT DATA BY VECTOR EQUAL TO ORIGIN POSITION AND THEN PERFORM CALCULATIONS

        objectLocation = bpy.context.active_object.location  # Origin Location

        # OriginalVertices stores Local Coordinates, V1, V2 stores translated coordinates
        OriginalVertices, V1, V2, edgeVector, edgeLength, edgeCenter = self.getEdgeInfoAfterTranslation(edge, objectLocation)

        lineAB = self.calc.getLineCoefficientsPerpendicularToVectorInPoint(edgeCenter, edgeVector)
        debugPrint("Line Coefficients:", lineAB)
        
        circleMidPoint = V1
        circleMidPointOnPlane = (V1[0], V1[1])  # only for Z=0 plane
        radius = parameters["radius"]
        angle = 0

        if (parameters["modeEnum"] == 'Angle'):
            if (parameters["angleEnum"] != 'Other'):
                radius, angle = self.CalculateRadiusAndAngleForAnglePresets(parameters["angleEnum"], radius, angle, edgeLength)
            else:
                radius, angle = self.CalculateRadiusAndAngleForOtherAngle(edgeLength)
            
        debugPrint("RADIUS = ", radius)
        debugPrint("ANGLE = ", angle)
        roots = None
        if angle != math.pi:  # mode other than 180
            if lineAB == None:
                roots = self.calc.getLineCircleIntersectionsWhenXPerpendicular(edgeCenter[0], circleMidPointOnPlane, radius)
            else:
                roots = self.calc.getLineCircleIntersections(lineAB, circleMidPointOnPlane, radius)
            if roots == None:
                self.report({'WARNING'}, "Edge Roundifier: No centers were found. Increase radius!")
                debugPrint("No centers were found. Change radius to higher value")
                return None
            roots = self.addMissingCoordinate(roots, V1[2])  # adds Z = 0 coordinate

        else:
            roots = [edgeCenter, edgeCenter]

        debugPrint("roots=")
        debugPrint(roots)

        refObjectLocation = None

        if parameters["refObject"] == "ORG":
            refObjectLocation = objectLocation
        else:
            refObjectLocation = bpy.context.scene.cursor_location

        chosenSpinCenter = self.getSpinCenterClosestToRefCenter(refObjectLocation, roots, parameters["flip"])
 

        if (parameters["modeEnum"] == "Radius"):
            halfAngle = self.calc.getAngle(edgeCenter, chosenSpinCenter, circleMidPoint)
            angle = 2 * halfAngle[0]  # in radians
            self.a = math.degrees(angle) # in degrees
  
        spinAxis = (0, 0, 1)  # Z axis by default

        vertIndex = self.getProperVertexIndex(chosenSpinCenter, V1, V2, refObjectLocation)

        if(parameters["invertAngle"]):
            vertIndex = self.getTheOtherIndex(vertIndex)
            angle = 2 * math.pi - angle

        if(parameters["fullCircles"]):
            angle = 2 * math.pi

        bpy.ops.mesh.select_all(action = "DESELECT")
        
        self.sel.selectVertexInMesh(mesh, OriginalVertices[vertIndex])

        bpy.ops.mesh.duplicate() #duplicate selected vertex 

        #FUTURE TODO OFFSET      
#        if parameters["offset"]:
#            offset = self.getOffsetVectorForTangency(edgeCenter, chosenSpinCenter, radius, self.invertAngle)
#            self.moveSelectedVertexByVector(mesh,offset)
#            chosenSpinCenterOffset = self.translateByVector(chosenSpinCenter, offset)
#            chosenSpinCenter = chosenSpinCenterOffset

        steps = parameters["segments"]

        bpy.ops.mesh.spin(
            steps=steps,
            dupli=False, 
            angle=angle, 
            center=chosenSpinCenter, 
            axis=spinAxis)



##########################################

    def getOffsetVectorForTangency(self, edgeCenter, chosenSpinCenter, radius, invertAngle):
        if invertAngle == False:
            edgeCentSpinCentVector = self.calc.getVectorBetween2VertsXYZ(edgeCenter, chosenSpinCenter)
        else:
            edgeCentSpinCentVector = self.calc.getVectorBetween2VertsXYZ(chosenSpinCenter, edgeCenter)
            
        vectorLength = self.calc.getVectorLength(edgeCentSpinCentVector)
        if invertAngle == False:
            offsetLength = radius - vectorLength
        else:
            offsetLength = radius + vectorLength
        normalizedVector = self.calc.getNormalizedVector(edgeCentSpinCentVector)
        offsetVector = (offsetLength * normalizedVector[0],
                        offsetLength * normalizedVector[1],
                        offsetLength * normalizedVector[2])
        return offsetVector
    
    def moveSelectedVertexByVector(self, mesh, offset):
        vert = self.sel.getSelectedVertex(mesh)
        vert.co.x =  vert.co.x + offset[0]
        vert.co.y =  vert.co.y + offset[1]
        vert.co.z =  vert.co.z + offset[2]

    def translateRoots(self, roots, objectLocation):
        # translationVector = self.calc.getVectorBetween2VertsXYZ(objectLocation, [0,0,0])
        r1 = self.translateByVector(roots[0], objectLocation)
        r2 = self.translateByVector(roots[1], objectLocation)
        return [r1, r2]

    def translateByVector(self, point, vector):
        translated = (point[0] + vector[0],
        point[1] + vector[1],
        point[2] + vector[2])
        return translated

    def CalculateRadiusAndAngleForOtherAngle(self, edgeLength):
        degAngle = self.a
        angle = math.radians(degAngle)
        self.r = radius = edgeLength / (2 * math.sin(angle/2)) 
        return radius, angle

    def CalculateRadiusAndAngleForAnglePresets(self, mode, initR, initA, edgeLength):
        radius = initR
        angle = initA
          
        if mode == "180":
            radius = edgeLength / 2
            angle = math.pi
        elif mode == "120":
            radius = edgeLength / 3 * math.sqrt(3)
            angle = 2 * math.pi / 3
        elif mode == "90":
            radius = edgeLength / 2 * math.sqrt(2)
            angle = math.pi / 2
        elif mode == "60":
            radius = edgeLength
            angle = math.pi / 3
        elif mode == "45":
            radius = edgeLength / (2 * math.sin(math.pi/8)) 
            angle = math.pi / 4    
        elif mode == "30":
            radius = edgeLength / (2 * math.sin(math.pi/12)) 
            angle = math.pi / 6      
        self.a = math.degrees(angle)
        self.r = radius
        debugPrint ("mode output, radius = ", radius, "angle = ", angle)
        return radius, angle

    #


    def getTheOtherIndex(self, vertexIndex):
        if vertexIndex == 0:
            return 1
        else:
            return 0

    def getProperVertexIndex(self, chosenSpinCenter, V1, V2, refObjectLocation):
        # TODO: I DON"T like this code :) there has to be a simpler way to check that!
        S = chosenSpinCenter
        E = self.calc.getCenterBetween2VertsXYZ(V1, V2)
        # edge is like y=x, S below edge OR         # edge is like y=-x, S below edge
        if (S[0] > E[0] and S[1] < E[1]) or (S[0] < E[0] and S[1] < E[1]):
            if V1[0] < E[0]:
                return 0  # V1
            if V2[0] < E[0]:
                return 1  # V2
        # edge is like y=x, S above edge  OR         # edge is like y=-x, S above edge
        if (S[0] < E[0] and S[1] > E[1]) or (S[0] > E[0] and S[1] > E[1]):
            if V1[0] > E[0]:
                return 0  # V1
            if V2[0] > E[0]:
                return 1  # V2


        # horizontal edge
        if S[0] == E[0] and S[1] < E[1]:
            if V1[0] < E[0]:
                return 0  # V1
            if V2[0] < E[0]:
                return 1  # V2
        if S[0] == E[0] and S[1] > E[1]:
            if V1[0] > E[0]:
                return 0  # V1
            if V2[0] > E[0]:
                return 1  # V1
        # spin center in the center of horizontal edge
        if S[0] == E[0] and S[1] == E[1] and V1[1] == V2[1]:
            if (refObjectLocation[1] < E[1]) and (V1[0] < E[0]):
                return 0  # V1
            if (refObjectLocation[1] < E[1]) and (V2[0] < E[0]):
                return 1  # V1
            if (refObjectLocation[1] > E[1]) and (V1[0] > E[0]):
                return 0  # V1
            if (refObjectLocation[1] > E[1]) and (V2[0] > E[0]):
                return 1  # V1

        # vertical edge
        if S[0] < E[0] and S[1] == E[1]:
            if V1[1] > E[1]:
                return 0  # V1
            if V2[1] > E[1]:
                return 1  # V2
        if S[0] > E[0] and S[1] == E[1]:
            if V1[1] < E[1]:
                return 0  # V1
            if V2[1] < E[1]:
                return 1  # V1

        # spin center in the center of vertical edge
        if S[0] == E[0] and S[1] == E[1] and V1[0] == V2[0]:

            if (refObjectLocation[0] < E[0]) and (V1[1] > E[1]):
                return 0  # V1
            if (refObjectLocation[0] < E[0]) and (V2[1] > E[1]):
                return 1  # V1
            if (refObjectLocation[0] > E[0]) and (V1[1] < E[1]):
                return 0  # V1
            if (refObjectLocation[0] > E[0]) and (V2[1] < E[1]):
                return 1  # V1

        return 0
        

    def getSpinCenterClosestToRefCenter(self, objLocation, roots, flip):
        root0Distance = self.calc.getEdgeLength(objLocation, roots[0])
        root1Distance = self.calc.getEdgeLength(objLocation, roots[1])
        chosenId = 0
        rejectedId = 1
        if (root0Distance > root1Distance):
            chosenId = 1
            rejectedId = 0
        if flip == True:
            return roots[rejectedId]
        else:
            return roots[chosenId]

    def addMissingCoordinate(self,roots,axisOffset):
        #TODO add X or Y or Z = 0, current assumption is Z = 0
        if roots != None:
            for root in roots:
                root.append(axisOffset)
        return roots

    def getSelectedEdges(self,bm):
        listOfSelectedEdges = []
        for e in bm.edges:
            if e.select == True:
                debugPrint("edges:", e)
                listOfSelectedEdges.append(e)
        return listOfSelectedEdges
    
    def selectEdgesAfterRoundifier(self, context, edges):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')
        mesh = context.scene.objects.active.data
        bmnew = bmesh.new()
        bmnew.from_mesh(mesh)
        self.deselectEdges(bmnew)
        for selectedEdge in edges:
            for e in bmnew.edges:
                if math.fabs(e.verts[0].co.x - selectedEdge.verts[0].co.x) <= self.threshold \
                and math.fabs(e.verts[0].co.y - selectedEdge.verts[0].co.y) <= self.threshold \
                and math.fabs(e.verts[0].co.y - selectedEdge.verts[0].co.y) <= self.threshold \
                and math.fabs(e.verts[1].co.x - selectedEdge.verts[1].co.x) <= self.threshold \
                and math.fabs(e.verts[1].co.y - selectedEdge.verts[1].co.y) <= self.threshold \
                and math.fabs(e.verts[1].co.y - selectedEdge.verts[1].co.y) <= self.threshold:
                    e.select_set(True)
                    
        bpy.ops.object.mode_set(mode='OBJECT')
        bmnew.to_mesh(mesh)
        bmnew.free()
        bpy.ops.object.mode_set(mode='EDIT')

                    
    def deselectEdges(self, bm):
        for edge in bm.edges:
            edge.select_set(False)
    

    def getVerticesFromEdge(self,edge):
        v1 = edge.verts[0]
        v2 = edge.verts[1]
        return (v1,v2)

    def debugPrintEdgesInfo(self, edges):
        debugPrint("=== Selected edges ===")
        for e in edges:
            v1 = e.verts[0]
            v2 = e.verts[1]
            debugPrint(v1.co.x, v1.co.y, v1.co.z)
            debugPrint(v2.co.x, v2.co.y, v2.co.z)
            debugPrint("----------")

        
    @classmethod
    def poll(cls, context):
        return (context.scene.objects.active.type == 'MESH') and (context.scene.objects.active.mode == 'EDIT')

def draw_item(self, context):
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.operator('mesh.edge_roundifier')

 
def register():
    bpy.utils.register_class(EdgeRoundifier)
    bpy.types.VIEW3D_MT_edit_mesh_edges.append(draw_item)


def unregister():
    bpy.utils.unregister_class(EdgeRoundifier)
    bpy.types.VIEW3D_MT_edit_mesh_edges.remove(draw_item)

if __name__ == "__main__":
    register()

