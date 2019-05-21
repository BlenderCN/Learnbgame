#+
# This add-on script for Blender 2.5 turns a mesh object into the
# tread around the circumference of a tyre.
#
# Copyright 2010-2012 Lawrence D'Oliveiro <ldo@geek-central.gen.nz>.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#-

import math
import sys # debug
import bpy
import mathutils

bl_info = \
    {
        "name" : "Tread Tiler",
        "author" : "Lawrence D'Oliveiro <ldo@geek-central.gen.nz>",
        "version" : (0, 6, 0),
        "blender" : (2, 5, 6),
        "api" : 32411,
        "location" : "View 3D > Edit Mode > Tool Shelf",
        "description" :
            "Turns a mesh object into the tread around the circumference of a tyre.\n\n"
            "Ensure the mesh contains a single isolated vertex which will be the centre"
            " of rotation. Select the two opposite sides of the rest of the mesh which"
            " will be joined in adjacent copies; the script will automatically figure out"
            " how many copies are necessary.",
        "warning" : "",
        "wiki_url" : "",
        "tracker_url" : "",
        "category" : "Mesh",
    }

class Failure(Exception) :

    def __init__(self, Msg) :
        self.Msg = Msg
    #end __init__

#end Failure

def NearlyEqual(X, Y, Tol) :
    """are X and Y equal to within fraction Tol."""
    return abs(X - Y) <= Tol * abs(X + Y) / 2
#end NearlyEqual

def VecNearlyEqual(X, Y, Tol) :
    """are the corresponding elements of vectors X and Y equal to within fraction Tol."""
    X = X.copy()
    X.resize_3d()
    Y = Y.copy()
    Y.resize_3d()
    MaxTol = max(abs(X[i] + Y[i]) / 2 for i in (0, 1, 2)) * Tol
    return \
      (
            abs(X[0] - Y[0]) <= MaxTol
        and
            abs(X[1] - Y[1]) <= MaxTol
        and
            abs(X[2] - Y[2]) <= MaxTol
      )
    return Result
#end VecNearlyEqual

class TileTread(bpy.types.Operator) :
    bl_idname = "mesh.tile_tread"
    bl_label = "Tile Tread"
    bl_context = "mesh_edit"
    bl_options = {"REGISTER", "UNDO"}

    join_ends = bpy.props.BoolProperty \
      (
        name = "Join Ends",
        description = "Join the inner edges to make a torus",
        default = False
      )
    smooth_join = bpy.props.BoolProperty \
      (
        name = "Smooth Join",
        description = "Smooth the faces created by joining the inner edges",
        default = False
      )
    rotation_radius = bpy.props.FloatProperty \
      (
        "Radius",
        description = "Adjust radius of rotation centre",
        subtype = "DISTANCE",
        unit = "LENGTH"
      )
    rotation_tilt = bpy.props.FloatProperty \
      (
        "Tilt",
        description = "Adjust angle around rotation axis",
        subtype = "ANGLE"
      )
    rotation_asym = bpy.props.FloatProperty \
      (
        "Asym",
        description = "Adjust angle around tangent to circumference",
        subtype = "ANGLE"
      )

    def draw(self, context) :
        TheCol = self.layout.column(align = True)
        TheCol.prop(self, "join_ends")
        TheCol.prop(self, "smooth_join")
        TheCol.label("Rotation Centre Adjust:")
        TheCol.prop(self, "rotation_radius")
        TheCol.prop(self, "rotation_tilt")
        TheCol.prop(self, "rotation_asym")
    #end draw

    def action_common(self, context, redoing) :
        save_mesh_select_mode = tuple(context.tool_settings.mesh_select_mode)
        try :
            if not redoing :
                if context.mode != "EDIT_MESH" :
                    raise Failure("not editing a mesh")
                #end if
                TheObject = context.scene.objects.active
                if TheObject == None or not TheObject.select :
                    raise Failure("no selected object")
                #end if
                # save the name of the object so I can find it again
                # when I'm reexecuted. Can't save a direct reference,
                # as that is likely to become invalid. Blender guarantees
                # the name is unique anyway.
                self.orig_object_name = TheObject.name
            else :
                TheObject = context.scene.objects[self.orig_object_name]
            #end if
            TheMesh = TheObject.data
            if type(TheMesh) != bpy.types.Mesh :
                raise Failure("selected object is not a mesh")
            #end if
            context.tool_settings.mesh_select_mode = (True, False, False) # vertex selection mode
            NewMeshName = TheObject.name + " tread"
            if not redoing :
                bpy.ops.object.editmode_toggle()
                bpy.ops.object.editmode_toggle()
                  # Have to get out of edit mode and back in again in order
                  # to synchronize possibly cached state of vertex selections
            #end if
            VertexEdges = {} # mapping from vertex to connected edges
            for ThisEdge in TheMesh.edges :
                for ThisVertex in ThisEdge.vertices :
                    if not ThisVertex in VertexEdges :
                        VertexEdges[ThisVertex] = []
                    #end if
                    VertexEdges[ThisVertex].append(ThisEdge)
                #end for
            #end for
            if self.join_ends :
                EdgeFaces = {} # mapping from edge to adjacent faces
                for ThisFace in TheMesh.polygons :
                    for ThisEdge in ThisFace.edge_keys :
                        if not ThisEdge in EdgeFaces :
                            EdgeFaces[ThisEdge] = []
                        #end if
                        EdgeFaces[ThisEdge].append(ThisFace.edge_keys)
                    #end for
                #end for
            #end if
            FaceSettings = {}
            for ThisFace in TheMesh.polygons :
                FaceSettings[tuple(sorted(ThisFace.vertices))] = \
                    {
                        "use_smooth" : ThisFace.use_smooth,
                        "material_index" : ThisFace.material_index,
                    }
            #end for
            # Find two continuous lines of selected vertices. Each line begins
            # and ends with a vertex connected to one other vertex, while the
            # intermediate vertices are each connected to two other vertices.
            # Why not allow two selected loops of vertices as well, you may ask?
            # Because then I can't figure out which vertex on one loop should be
            # merged with which one on the other loop in an adjacent copy.
            SelectedLines = []
            Seen = set()
            for ThisVertex in TheMesh.vertices :
                ThisVertex = ThisVertex.index
                if not ThisVertex in Seen and TheMesh.vertices[ThisVertex].select :
                    Connected = []
                    for ThisEdge in VertexEdges.get(ThisVertex, []) :
                        for OtherVertex in ThisEdge.vertices :
                            if OtherVertex != ThisVertex and TheMesh.vertices[OtherVertex].select :
                                Connected.append(OtherVertex)
                            #end if
                        #end for
                    #end for
                    if len(Connected) > 2 or len(Connected) == 0 :
                        sys.stderr.write("Connected to %d: %s\n" % (ThisVertex, repr(Connected))) # debug
                        raise Failure("selection must be lines of vertices")
                    #end if
                    if len(Connected) == 1 :
                        # start a line from here
                        ThatVertex = Connected[0]
                        ThisLine = [ThisVertex, ThatVertex]
                        Seen.update(ThisLine)
                        while True :
                            NextVertex = None
                            for ThisEdge in VertexEdges[ThatVertex] :
                                for OtherVertex in ThisEdge.vertices :
                                    if (
                                            TheMesh.vertices[OtherVertex].select
                                        and
                                            OtherVertex != ThatVertex
                                        and
                                            OtherVertex != ThisLine[-2]
                                        and
                                            OtherVertex != ThisVertex
                                    ) :
                                        if NextVertex != None :
                                            raise Failure \
                                              (
                                                "selection must be simple lines of vertices"
                                              )
                                        #end if
                                        NextVertex = OtherVertex
                                    #end if
                                #end for
                            #end for
                            if NextVertex == None :
                                break
                            Seen.add(NextVertex)
                            ThisLine.append(NextVertex)
                            ThatVertex = NextVertex
                        #end while
                        SelectedLines.append(ThisLine)
                    #end if
                #end if
            #end for
            if len(SelectedLines) != 2 :
                raise Failure("selection must contain exactly two lines of vertices")
            #end if
            OldVertices = []
              # for making my own copy of coordinates from original mesh. This seems
              # to give more reliable results than repeatedly accessing the original
              # mesh. Why?
            Unconnected = set()
            Center = None
            for ThisVertex in TheMesh.vertices :
                OldVertices.append \
                  (
                    {
                        "co" : ThisVertex.co.copy(),
                        "bevel_weight" : ThisVertex.bevel_weight,
                        "groups" : tuple
                          (
                            {
                                "group" : g.group,
                                "weight" : g.weight,
                            }
                          for g in ThisVertex.groups
                          ),
                    }
                  )
                if ThisVertex.index not in VertexEdges :
                    Unconnected.add(ThisVertex.index)
                else :
                    if Center == None :
                        Center = ThisVertex.co.copy()
                    else :
                        Center += ThisVertex.co
                    #end if
                #end if
            #end for
            if len(Unconnected) > 1 :
                raise Failure("must be no more than one unconnected vertex to serve as centre of rotation")
            #end if
            Center /= (len(OldVertices) - len(Unconnected))
              # centre of mesh (excluding unconnected vertex)
            if len(Unconnected) == 1 :
                RotationCenterVertex = Unconnected.pop()
                RotationCenter = OldVertices[RotationCenterVertex]["co"]
            else :
                # no unconnected vertex, use 3D cursor instead
                RotationCenterVertex = None
                RotationCenter = TheObject.matrix_world.inverted() * context.scene.cursor_location
                  # 3D cursor is in global coords, need object coords
            #end if
            TileLine1 = SelectedLines[0]
            TileLine2 = SelectedLines[1]
            if len(TileLine1) != len(TileLine2) :
                raise Failure("selected lines don't have same number of vertices")
            #end if
            if len(TileLine1) < 2 :
                raise Failure("selected lines must have at least two vertices")
            #end if
            Tolerance = 0.01
            Slope1 = (OldVertices[TileLine1[-1]]["co"] - OldVertices[TileLine1[0]]["co"]).normalized()
            Slope2 = (OldVertices[TileLine2[-1]]["co"] - OldVertices[TileLine2[0]]["co"]).normalized()
            if math.isnan(tuple(Slope1)[0]) or math.isnan(tuple(Slope2)[0]) :
                raise Failure("selected lines must have nonzero length")
            #end if
            if VecNearlyEqual(Slope1, Slope2, Tolerance) :
                pass # fine
            elif VecNearlyEqual(Slope1, - Slope2, Tolerance) :
                TileLine2 = list(reversed(TileLine2))
            else :
                sys.stderr.write("Slope1 = %s, Slope2 = %s\n" % (repr(Slope1), repr(Slope2))) # debug
                raise Failure("selected lines are not parallel")
            #end if
            for i in range(1, len(TileLine1) - 1) :
                Slope1 = (OldVertices[TileLine1[i]]["co"] - OldVertices[TileLine1[0]]["co"]).normalized()
                Slope2 = (OldVertices[TileLine2[i]]["co"] - OldVertices[TileLine2[0]]["co"]).normalized()
                if math.isnan(tuple(Slope1)[0]) or math.isnan(tuple(Slope2)[0]) :
                    # should I allow this?
                    raise Failure("selected lines contain overlapping vertices")
                #end if
                if not VecNearlyEqual(Slope1, Slope2, Tolerance) :
                    raise Failure("selected lines are not parallel")
                #end if
            #end for
            if self.join_ends :
                # Find two continuous lines of vertices connecting the ends of
                # the selected lines. These will be joined with additional faces
                # to complete the torus in the generated mesh.
                JoinLine1 = []
                JoinLine2 = []
                Vertex1 = TileLine1[0]
                Vertex2 = TileLine1[-1]
                Vertex1Prev = TileLine1[1]
                Vertex2Prev = TileLine1[-2]
                while True :
                    JoinLine1.append(Vertex1)
                    JoinLine2.append(Vertex2)
                    if Vertex1 == TileLine2[0] or Vertex2 == TileLine2[-1] :
                        if Vertex1 != TileLine2[0] or Vertex2 != TileLine2[-1] :
                            sys.stderr.write("JoinLine1 so far: %s\n" % repr(JoinLine1)) # debug
                            sys.stderr.write("JoinLine2 so far: %s\n" % repr(JoinLine2)) # debug
                            sys.stderr.write("TileLine1 = %s\n" % repr(TileLine1)) # debug
                            sys.stderr.write("TileLine2 = %s\n" % repr(TileLine2)) # debug
                            raise Failure("end lines to be joined do not have equal numbers of vertices")
                        #end if
                        break
                    #end if
                    if Vertex1 == TileLine2[-1] or Vertex2 == TileLine2[0] :
                        raise Failure("end lines to be joined don't connect properly between selected lines")
                    #end if
                    Vertex1Next, Vertex2Next = None, None
                    for ThisEdge in VertexEdges[Vertex1] :
                        if len(EdgeFaces[tuple(ThisEdge.vertices)]) == 1 : # ensure it's not an interior edge
                            for ThisVertex in ThisEdge.vertices :
                                if ThisVertex != Vertex1 and ThisVertex != Vertex1Prev :
                                    if Vertex1Next != None :
                                        raise Failure("can't find unique line between ends to join")
                                    #end if
                                    Vertex1Next = ThisVertex
                                #end if
                            #end for
                        #end if
                    #end for
                    for ThisEdge in VertexEdges[Vertex2] :
                        if len(EdgeFaces[tuple(ThisEdge.vertices)]) == 1 : # ensure it's not an interior edge
                            for ThisVertex in ThisEdge.vertices :
                                if ThisVertex != Vertex2 and ThisVertex != Vertex2Prev :
                                    if Vertex2Next != None :
                                        raise Failure("can't find unique line between ends to join")
                                    #end if
                                    Vertex2Next = ThisVertex
                                #end if
                            #end for
                        #end if
                    #end for
                    if Vertex1Next == None or Vertex2Next == None :
                        raise Failure("can't find line between ends to join")
                    #end if
                    Vertex1Prev, Vertex2Prev = Vertex1, Vertex2
                    Vertex1, Vertex2 = Vertex1Next, Vertex2Next
                #end while
            #end if
            ReplicationVector =  \
                (
                    (OldVertices[TileLine2[0]]["co"] + OldVertices[TileLine2[-1]]["co"]) / 2
                -
                    (OldVertices[TileLine1[0]]["co"] + OldVertices[TileLine1[-1]]["co"]) / 2
                )
                  # displacement between mid points of tiling edges
            RotationRadius = Center - RotationCenter
            RotationAxis = RotationRadius.cross(ReplicationVector).normalized()
            if redoing :
                RotationRadius =  \
                    (
                        RotationRadius.normalized() * self.rotation_radius
                    *
                        mathutils.Matrix.Rotation(self.rotation_tilt, 4, RotationAxis + RotationRadius)
                    *
                        mathutils.Matrix.Rotation(self.rotation_asym, 4, ReplicationVector.normalized())
                    )
                RotationAxis = RotationRadius.cross(ReplicationVector).normalized()
                RotationCenter = Center - RotationRadius
            else :
                self.rotation_radius = RotationRadius.magnitude
                self.rotation_tilt = 0
                self.rotation_asym = 0
            #end if
            sys.stderr.write("SelectedLines = %s\n" % repr(SelectedLines)) # debug
            sys.stderr.write("Center = %s\n" % repr(Center)) # debug
            sys.stderr.write("RotationCenter = %s\n" % repr(RotationCenter)) # debug
            sys.stderr.write("ReplicationVector = %s\n" % repr(ReplicationVector)) # debug
            RotationRadiusLength = RotationRadius.magnitude
            Replicate = 2 * math.pi * RotationRadiusLength / ReplicationVector.magnitude
            IntReplicate = round(Replicate)
            Rescale = IntReplicate / Replicate
            sys.stderr.write("RotationRadius = %s, axis = %s, NrCopies = %.2f * %.2f = %d\n" % (repr(RotationRadius), repr(RotationAxis), Replicate, Rescale, IntReplicate)) # debug
            if not redoing :
                bpy.ops.object.editmode_toggle()
            #end if
            NewMesh = bpy.data.meshes.new(NewMeshName)
            NewVertices = []
            Faces = []
            # sin and cos of half-angle subtended by mesh at RotationCenter
            HalfWidthSin = ReplicationVector.magnitude / RotationRadiusLength / 2
            if abs(HalfWidthSin) > 1 :
                raise Failure("rotation radius too small")
            #end if
            HalfWidthCos = math.sqrt(1 - HalfWidthSin * HalfWidthSin)
            ReplicationUnitVector = ReplicationVector.normalized()
            RotationRadiusUnitVector = RotationRadius.normalized()
            MergeVertex = dict(zip(TileLine2, TileLine1))
              # vertices to be merged in adjacent copies of mesh
            if RotationCenterVertex != None :
                MergeVertex[RotationCenterVertex] = None # special case, omit from individual copies of mesh
            #end if
            MergedWithVertex = dict(zip(TileLine1, TileLine2))
            RenumberVertex = dict \
              (
                (i, i) for i in range(0, len(OldVertices))
              ) # to begin with
            for v in reversed(sorted(MergeVertex.keys())) : # renumbering of remaining vertices after merging
                RenumberVertex[v] = None # this one disappears
                for j in range(v + 1, len(OldVertices)) : # following ones drop down by 1
                    if RenumberVertex[j] != None :
                        RenumberVertex[j] -= 1
                    #end if
                #end for
            #end for
            NrVerticesPerTile = len(OldVertices) - len(TileLine2) - (0, 1)[RotationCenterVertex != None]
            TotalNrVertices = NrVerticesPerTile * IntReplicate
            for i in range(0, IntReplicate) :
                ThisXForm = \
                    (
                        mathutils.Matrix.Translation(RotationCenter)
                    *
                        mathutils.Matrix.Rotation
                          (
                            math.pi * 2 * i / IntReplicate, # angle
                            4, # size
                            RotationAxis # axis
                          )
                    *
                        mathutils.Matrix.Scale
                          (
                            Rescale, # factor
                            4, # size
                            ReplicationVector # axis
                          )
                    *
                        mathutils.Matrix.Translation(- RotationCenter)
                    )
                for VertIndex, ThisVertex in enumerate(OldVertices) :
                    ThisVertex = ThisVertex["co"]
                    if not VertIndex in MergeVertex :
                      # vertex in TileLine2 in this copy will be merged with TileLine1 in next copy
                        ThisSin = \
                            (
                                ((ThisVertex - Center) * ReplicationUnitVector)
                            /
                                RotationRadiusLength
                            )
                        ThisCos = math.sqrt(1 - ThisSin * ThisSin)
                        VertexOffset = RotationRadiusLength * (ThisCos - HalfWidthCos)
                        VertexOffset = \
                            (
                                VertexOffset * ThisCos * RotationRadiusUnitVector
                            +
                                VertexOffset * ThisSin * ReplicationUnitVector
                            )
                        ThisVertex = ThisXForm * (ThisVertex + VertexOffset)
                        if VertIndex in MergedWithVertex :
                          # compute merger of vertex in TileLine1 in this copy with
                          # TileLine2 in previous copy
                            ThatVertex = OldVertices[MergedWithVertex[VertIndex]]["co"]
                            ThatSin = \
                                (
                                    ((ThatVertex - Center) * ReplicationUnitVector)
                                /
                                    RotationRadiusLength
                                )
                            ThatCos = math.sqrt(1 - ThatSin * ThatSin)
                            VertexOffset = RotationRadiusLength * (ThatCos - HalfWidthCos)
                            VertexOffset = \
                                (
                                    VertexOffset * ThatCos * RotationRadiusUnitVector
                                +
                                    VertexOffset * ThatSin * ReplicationUnitVector
                                )
                            ThatVertex = \
                                (
                                    (
                                        mathutils.Matrix.Translation(RotationCenter)
                                    *
                                        mathutils.Matrix.Rotation
                                          (
                                            math.pi * 2 * ((i + IntReplicate - 1) % IntReplicate) / IntReplicate, # angle
                                            4, # size
                                            RotationAxis # axis
                                          )
                                    *
                                        mathutils.Matrix.Scale
                                          (
                                            Rescale, # factor
                                            4, # size
                                            ReplicationVector # axis
                                          )
                                    *
                                        mathutils.Matrix.Translation(- RotationCenter)
                                    )
                                *
                                    (ThatVertex + VertexOffset)
                                )
                            ThisVertex = (ThisVertex + ThatVertex) / 2
                        #end if
                        NewVertices.append(dict(OldVertices[VertIndex])) # shallow copy is enough
                        NewVertices[-1]["co"] = ThisVertex
                    #end if
                #end for
                for ThisFace in TheMesh.faces :
                    NewFace = []
                    for v in ThisFace.vertices :
                        if v in MergeVertex :
                            v = (RenumberVertex[MergeVertex[v]] + (i + 1) * NrVerticesPerTile) % TotalNrVertices
                        else :
                            v = RenumberVertex[v] + i * NrVerticesPerTile
                        #end if
                        NewFace.append(v)
                    #end for
                    Faces.append(NewFace)
                #end for
                if self.join_ends :
                    # add faces to close up the gap between JoinLine1 and JoinLine2
                    Vertex1Prev, Vertex2Prev = JoinLine1[0], JoinLine2[0]
                    for Vertex1, Vertex2 in zip(JoinLine1[1:-1], JoinLine2[1:-1]) :
                        Faces.append \
                          (
                            [
                                RenumberVertex[Vertex1Prev] + i * NrVerticesPerTile,
                                RenumberVertex[Vertex2Prev] + i * NrVerticesPerTile,
                                RenumberVertex[Vertex2] + i * NrVerticesPerTile,
                                RenumberVertex[Vertex1] + i * NrVerticesPerTile,
                            ]
                          )
                        Vertex1Prev, Vertex2Prev = Vertex1, Vertex2
                    #end for
                    Faces.append \
                      (
                        [
                            RenumberVertex[Vertex1Prev] + i * NrVerticesPerTile,
                            RenumberVertex[Vertex2Prev] + i * NrVerticesPerTile,
                            (RenumberVertex[MergeVertex[JoinLine2[-1]]] + (i + 1) * NrVerticesPerTile) % TotalNrVertices,
                            (RenumberVertex[MergeVertex[JoinLine1[-1]]] + (i + 1) * NrVerticesPerTile) % TotalNrVertices,
                        ]
                      )
                #end if
            #end for
            NewMesh.from_pydata(list(v["co"] for v in NewVertices), [], Faces)
            NewObj = bpy.data.objects.new(NewMeshName, NewMesh)
            for g in TheObject.vertex_groups :
                NewObj.vertex_groups.new(g.name)
            #end for
            for m in TheMesh.materials :
                NewMesh.materials.append(m)
            #end for
            if len(TheMesh.materials) != 0 and self.join_ends and self.smooth_join :
                NewMesh.materials.append(TheMesh.materials[0])
                JoinedFaceMaterial = len(NewMesh.materials) - 1 # 0-based
            else :
                JoinedFaceMaterial = None
            #end if
            for i in range(0, len(NewVertices)) :
                NewMesh.vertices[i].bevel_weight = NewVertices[i]["bevel_weight"]
                for g in NewVertices[i]["groups"] :
                    NewObj.vertex_groups[g["group"]].add \
                      (
                        index = (i,), # not batching because each vertex might have different weight
                        weight = g["weight"],
                        type = "ADD"
                      )
                 #end for
            #end for
            # copy material and smoothness settings to corresponding faces of new mesh
            OldFaceSettings = FaceSettings
            FaceSettings = {}
            for OldFaceVertices in OldFaceSettings :
                FaceVertices = []
                for OldVertex in OldFaceVertices :
                    if OldVertex in MergeVertex :
                        NewVertex = RenumberVertex[MergeVertex[OldVertex]]
                    else :
                        NewVertex = RenumberVertex[OldVertex]
                    #end if
                    if NewVertex != None :
                        FaceVertices.append(NewVertex)
                    #end if
                #end for
                FaceSettings[tuple(sorted(FaceVertices))] = OldFaceSettings[tuple(sorted(OldFaceVertices))]
            #end for
            for ThisFace in NewMesh.faces :
                FaceVertices = tuple(sorted((v % NrVerticesPerTile for v in sorted(ThisFace.vertices))))
                if FaceVertices in FaceSettings :
                    ThisFaceSettings = FaceSettings[FaceVertices]
                    ThisFace.use_smooth = ThisFaceSettings["use_smooth"]
                    ThisFace.material_index = ThisFaceSettings["material_index"]
                else :
                    ThisFace.use_smooth = self.smooth_join
                    if JoinedFaceMaterial != None :
                        ThisFace.material_index = JoinedFaceMaterial
                    #end if
                #end if
            #end for
            NewMesh.update()
            context.scene.objects.link(NewObj)
            NewObj.matrix_local = TheObject.matrix_local
            NewObjName = NewObj.name
            bpy.ops.object.select_all(action = "DESELECT")
            bpy.ops.object.select_name(name = NewObjName)
            for ThisVertex in NewMesh.vertices :
                ThisVertex.select = True # usual Blender default for newly-created object
            #end for
            NewMesh.update()
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.normals_make_consistent()
            bpy.ops.object.editmode_toggle()
            # all done
            Status = {"FINISHED"}
        except Failure as Why :
            sys.stderr.write("Failure: %s\n" % Why.Msg) # debug
            self.report({"ERROR"}, Why.Msg)
            Status = {"CANCELLED"}
        #end try
        context.tool_settings.mesh_select_mode = save_mesh_select_mode
        return Status
    #end action_common

    def execute(self, context) :
        return self.action_common(context, True)
    #end execute

    def invoke(self, context, event) :
        return self.action_common(context, False)
    #end invoke

#end TileTread

def add_invoke_button(self, context) :
    TheCol = self.layout.column(align = True) # gives a nicer grouping of my items
    TheCol.label("Tread Tiler:")
    TheCol.operator("mesh.tile_tread", text = "Tile Tread")
#end add_invoke_button

def register() :
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_PT_tools_meshedit.append(add_invoke_button)
#end register

def unregister() :
    bpy.utils.unregister_module(__name__)
    bpy.types.VIEW3D_PT_tools_meshedit.remove(add_invoke_button)
#end unregister

if __name__ == "__main__" :
    register()
#end if
