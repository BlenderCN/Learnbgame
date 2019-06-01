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

bl_info = {
    "name": "Curve to Uniform Mesh",
    "author": "Denis Declara",
    "version": (0, 1),
    "blender": (2, 5, 3),
    "api": 32411,
    "location": "Toolshelf > search > Curve to Uniform Mesh",
    "description": "This script converts bezier curves or text objects to a mesh",
    "warning": "Beta",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
    }

"""
This script converts curves and text objects to an even mesh.
"""

##############################
import bpy
from bpy.props import *
import mathutils
from mathutils import Vector

#######################################
### Beginn of custom bezier classes ###
#######################################

# Simple class which holds a straight bezier segment
class LinearBezierSegment:
    s = Vector((0,1,0))
    e = Vector((0,0,0))
    
    def __init__ (self, start, end):
        self.s = start
        self.e = end
    
    # This method returns the length of the line segment
    def calculateLength(self):
        return (start - end).length()

    # This method evaluates the bezier curve at a
    # point t in [0, 1] 
    def at(self, t):        
        return self.s + (self.e - self.s) * t
    
# Simple class which stores one cubic bezier segment
# That is a segmend with start and end point, plus
# two control points
class CubicBezierSegment:
    s  = Vector(( -1,  0, 0)) # First  bezier point
    n1 = Vector((-.5,-.5, 0)) # Right  handle of the first bezier point
    n2 = Vector((  0,  0, 0)) # Left   handle of the second bezier point
    e  = Vector((  1,  0, 0)) # Second bezier point
    
    def __init__ (self, start, ctrl1, ctrl2, end):
        self.s  = start
        self.n1 = ctrl1
        self.n2 = ctrl2
        self.e  = end
    
    # This method evaluates the bezier curve at a
    # point t in [0, 1]
    def at(self, t):
        # This method uses the method illustrated in this animation
        # http://en.wikipedia.org/wiki/File:Bezier_3_big.gif

        # Create the first segments
        a = LinearBezierSegment(self.s,  self.n1).at(t)
        b = LinearBezierSegment(self.n1, self.n2).at(t)
        c = LinearBezierSegment(self.n2, self.e ).at(t)
        
        # Interpolate those segments
        d = LinearBezierSegment(a, b).at(t)
        e = LinearBezierSegment(b, c).at(t)
        
        # And finally interpolate one last time and return
        f = LinearBezierSegment(d, e).at(t)
        return f
    
    # Calculates an approximatino of the length. By subdividing
    # the curve in straight segments. The amount of segments
    # is specified by the parameter segments 
    # The bigger the value, the more precise the approximation
    # will be
    def calculateLength(self, segments):
        length = 0.0
        lastPoint = self.at(0.0)
        for i in range(0, segments):
            t = (i + 1) / segments
            nextPoint = self.at(t)
            length += (lastPoint - nextPoint).length
            lastPoint = nextPoint
        return length
    
    # This function returns a collection of Vectors, with
    # as many intermediate points as defined by the parameter
    # segments. Moreover it will not include the last point
    # if the argument excludeLast is set to true
    def getIntermediatePoints(self, segments, excludeLast):
        if not excludeLast:
            segments += 1
        
        points = []
        for i in range(0, segments):
            t1 = i / segments
            points.append(self.at(t1))
        return points

# This class basically represents a collection of
# cubic bezier segments, forming a closed curve
class CubicBezier:
    segments = [] # Collection of cubic bezier segments

    # Adds a segment at the end of the curve
    def addSegment(self, segment):
        self.segments.append(segment)
    
    # This function calculates the amount of subdivisions for
    # each individual bezier segment, so that the subdivision
    # results homogeneous
    # - FirstPassResolution determines the precision of the length
    #   approximation and therefore of the subdivision
    # - SegmentsPerUnit determines the density of the subdivision
    def calculateAdaptiveSegments(self, firstPassResolution = 8, segmentsPerUnit = 8):
        # If there are no segments in the curve return an empty array
        if len(self.segments) == 0:
            return []        

        # Create an array with the length of the segments
        lengths = [segment.calculateLength(firstPassResolution)
                   for segment in self.segments]

        length = 0.0
        # Sum up the length of each segment 
        for l in lengths:
            length += l
                        
        # Calculate adaptive subdivisions of segments:
        nSegments = [0] * len(self.segments)
        # Determine the amount of subdivisions to perform by
        # multiplying the density by the total length 
        segmentsToAssign = int(round(segmentsPerUnit * length))
        # Distribute those subdivisions to the individual bezier
        # segments evenly, based upon their length
        for s in range(0, len(self.segments)):
            nSegments[s] = 1 + int(lengths[s] * segmentsPerUnit)
            segmentsToAssign -= nSegments[s]

        # If, due to rounding errors, some subdivisions haven't
        # been assigned, assign those
        while segmentsToAssign > 0:
            maxDeltaIndex = 0
            for s in range(0, len(self.segments)):
                # Delta0 and Delta1 represent the length of each subdivided segment
                delta0 = lengths[maxDeltaIndex] / nSegments[maxDeltaIndex]
                delta1 = lengths[s] / nSegments[s]

                if (delta0 < delta1):
                    maxDeltaIndex = s
            # Assign one subdivision to the segment which has the biggest
            # subdivided segments.
            nSegments[maxDeltaIndex] += 1
            segmentsToAssign -= 1
        
        # Finally after long computation return the optimal subdivisions for each segment
        return nSegments

    # This function returns a collection of Vectors, with
    # a density of points  as defined by the parameter
    # segmentsPerUnit. Moreover the precision can is set by
    # the parameter firstPassResolution
    def getIntermediatePoints(self, firstPassResolution = 8, segmentsPerUnit = 8):
        points = []
            
        # Return if there are no segments in the curve
        if len(self.segments) == 0:
            return points

        # Calculate adaptive subdivision of segments:
        nSegments = self.calculateAdaptiveSegments(firstPassResolution, segmentsPerUnit)

        # Ask to each bezier segment to generate as many points as defined by nSegments[i]
        # and append those to the array points
        for s in range(0, len(self.segments)):
            segm = self.segments[s]            
            # Exclude the last point, so we do not get any duplication
            # in closed curves
            points.extend(segm.getIntermediatePoints(nSegments[s], True))
            
        return points

    # Calculates an approximatino of the length. By subdividing
    # the curve in straight segments. The density of segments
    # is specified by the parameter segmentsPerUnit 
    # The bigger the value of segmentsPerUnit and firstPassResolution
    # the more precise the approximation will be
    def calculateLength(self, firstPassResolution = 8, segmentsPerUnit = 8):
        # If the curve has no segments the length is of course 0
        if (len(self.segments) == 0):
            return 0.0
            
        length = 0.0

        # Calculate adaptive segments:
        nSegments = calculateAdaptiveSegments(firstPassResolution, segmentsPerUnit)

        # Calculate adaptive length:
        length = 0
        for s in range(0, len(self.segments)):
            segment = self.segments[s]
            length += segment.calculateLength(nSegments[s])
            
        return length

######################################
### -End of custom bezier classes- ###
######################################

def main(context, obj, options):
    #print("\n_______START_______")
    # main vars
    fillMesh = options[0]
    lengthApp = options[1]
    density = options[2]
    beautifyIters = options[3]
    if(options[4] == False): # If the execute checkbox is not checked return 
        return;

    verts = []
    faces = []
    curVertex = 0;

    originalName = obj.name
    isFontObject = (obj.type == 'FONT')
    if isFontObject:
        # Convert font objects into curves
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        context.scene.objects.active = obj
        bpy.ops.object.convert(target='CURVE', keep_original=True)
        obj = bpy.context.active_object 
        
    # Deselect all of the objects in the scene
    bpy.ops.object.select_all(action='DESELECT')
    scene = context.scene
    splines = obj.data.splines.values()

    # create a mesh datablock
    mesh = bpy.data.meshes.new("uniform_"+originalName)

    # go through splines
    for spline in splines:
        # test if spline is a bezier curve, otherwise skip it
        # also test if the curve has one or no points skip it
        if spline.type == 'BEZIER' and len(spline.bezier_points) > 1:
            # Convert blender's bpy bezier class in to my own bezier class
            bezier = CubicBezier()
            bezier.segments = []
            bp = spline.bezier_points
            for i in range(0, len(spline.bezier_points) - 1):
                bp1 = bp[i]
                bp2 = bp[i+1]
                sg = CubicBezierSegment(bp1.co, bp1.handle_right, bp2.handle_left, bp2.co)
                bezier.addSegment(sg)
            bezier.addSegment(CubicBezierSegment(bp[len(bp)-1].co, bp[len(bp)-1].handle_right, bp[0].handle_left, bp[0].co))
            
            # Sample the curve uniformly and store the points in ip
            ip = bezier.getIntermediatePoints(lengthApp, density)

            # Prepare the data to be added to blender
            firstVertexId =  curVertex
            for point in ip:
                verts.append([point.x, point.y, point.z])
                faces.append([curVertex, curVertex + 1, curVertex])
                curVertex+=1
            # Fix the mesh, closing the last edge
            faces[curVertex -1][1] = firstVertexId

    # Add geometry to mesh object
    mesh.from_pydata(verts, [], faces)
    mesh.update()

    # Create object and link it to the scene
    newMesh = bpy.data.objects.new("uniform_"+originalName, mesh)
    scene.objects.link(newMesh)
    newMesh.select = True
    scene.objects.active = newMesh
    newMesh.matrix_world = obj.matrix_world
    newMesh.data.show_all_edges = True

    # Remove double vertices
    bpy.ops.object.mode_set(mode = 'EDIT')
    #bpy.ops.mesh.remove_doubles()

    # If the user decides to fill the mesh, fill it with the
    # internal operators
    if fillMesh == True:
        bpy.ops.mesh.fill()
        # Repeat the beautify fill a couple of times as it may not
        # yield a perfect result the first time
        for i in range(0, beautifyIters):
            bpy.ops.mesh.beautify_fill()
        # Quadrangulate the mesh using blender ops
        bpy.ops.mesh.tris_convert_to_quads()

    # Switch back to object mode
    bpy.ops.object.mode_set(mode = 'OBJECT')

    # create ne object and put into scene

    if isFontObject == True:
        scene.objects.unlink(obj)

    #print("________END________\n")
    return

###########################
##### Curves OPERATOR #####
###########################
class CURVE_OT_toUniformMesh(bpy.types.Operator):
    bl_idname = 'touniformmesh.go'
    bl_label = "Convert Curve To Uniform Mesh"
    bl_description = "converts curve to an uniform mesh"
    bl_options = {'REGISTER', 'UNDO'}

        # Whetever or not to execute the modifier
    execscript = BoolProperty(name="Execute",
                            description="execute the modifier",
                            default=True)

    # Whetever or not to fill the mesh
    fillMesh = BoolProperty(name="Fill mesh",
                            description="fill the mesh",
                            default=True)

    # Precision (number of segments) of the length approximation
    lengthApp = IntProperty(name="Length approximation",
                            min=1, soft_min=1,
                            default=8,
                            description="precision of the length approximation")

        # Number of times to execute blender's beautify_fill
    beautifyIters = IntProperty(name="Beautify fill iterations",
                            min=1, soft_min=1,
                            default=5,
                            description="number of time to execute beautify fill on the mesh")

    # Amount of vertices per blender unit to compute
    density = FloatProperty(name="Density",
                            description="amount of vertices per 1 blender unit to compute",
                            min=1, soft_min=1,
                            default=32.0, precision=3)
        
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, 'execscript')
        col.prop(self, 'fillMesh')
        col.prop(self, 'density')
        col.prop(self, 'beautifyIters')
        col.prop(self, 'lengthApp')
        
    ## Check for curve or text object
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if (obj and (obj.type == 'CURVE' or obj.type == 'FONT')):
            return True
        if obj and obj.type == 'MESH' and obj.name.startswith("uniform_"):
            if obj.name[8:] in bpy.context.scene.objects:
                if bpy.context.scene.objects[obj.name[8:]].type == 'CURVE' or bpy.context.scene.objects[obj.name[8:]].type == 'FONT':
                    return True
        return False

    ## execute
    def execute(self, context):
        print("------START------")

        options = [
                self.fillMesh,      #0
                self.lengthApp,     #1
                self.density,       #2
                self.beautifyIters, #3
                self.execscript]    #4

        bpy.context.user_preferences.edit.use_global_undo = False

        # Go into object mode
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        # Grab the current object
        obj = context.active_object
        if obj.type == 'MESH':
            tempobj = obj
            print("---" + str(obj.name))
            obj = bpy.context.scene.objects[obj.name[8:]]
            print(">>>" + str(obj.name))
            bpy.context.scene.objects.active = obj;
            bpy.context.scene.objects.unlink(tempobj)

        main(context, obj, options)

        bpy.context.user_preferences.edit.use_global_undo = True

        #print("-------END-------")
        return {'FINISHED'}

    def invoke(self, context, event):
        self.execute(context)
        return {'FINISHED'}

#################################################
#### REGISTER ###################################
#################################################

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()