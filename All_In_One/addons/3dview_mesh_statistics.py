# ##### BEGIN GPL LICENSE BLOCK #####
#
#  3dview_mesh_statistics.py
#  Calculate volume, area, center of mass of current mesh
#  Copyright (C) 2015 Quentin Wenger
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



bl_info = {"name": "Mesh Statistics",
           "description": "Display Volume, Area, CoM of current Mesh",
           "author": "Quentin Wenger (Matpi)",
           "version": (1, 0),
           "blender": (2, 74, 0),
           "location": "3D View(s) -> Properties -> Mesh Statistics",
           "warning": "",
           "wiki_url": "",
           "tracker_url": "",
           "category": "3D View"
           }



import bpy
from mathutils import Matrix, Vector
from mathutils.geometry import area_tri#, tessellate_polygon
from bpy_extras.mesh_utils import ngon_tessellate, edge_face_count
from bgl import glBegin, glPointSize, glColor3f, glVertex3f, glEnd, GL_POINTS


handle = []
do_draw = [False]
com = [(0.0, 0.0, 0.0)]


def arithmeticMean(items):
    """
    Arithmetic mean of the items.
    """
    # sum() doesn't work for lists of Vectors... :-/
    s = items[0].copy()
    for item in items[1:]:
        s += item
    return s/len(items)

def weightedMean(couples):
    """
    Weighted mean of the couples (item, weight).
    """
    # could be made nicer, but this is fast
    items_weighted_sum = couples[0][0]*couples[0][1]
    weights_sum = couples[0][1]
    for item, weight in couples:
        items_weighted_sum += item*weight
        weights_sum += weight
        
    return items_weighted_sum/weights_sum


def calculateTriangleArea(mesh, vertices, matrix):
    vcs = [matrix*mesh.vertices[i].co for i in vertices]
    return area_tri(*vcs)



def calculateArea(mesh, matrix=None):
    """
    Simply sum up faces areas.
    """
    area = 0.0
    if matrix is None:
        for polygon in mesh.polygons:
            area += polygon.area
    else:
        for polygon in mesh.polygons:
            if len(polygon.vertices) == 3:
                area += calculateTriangleArea(mesh, polygon.vertices, matrix)
            elif len(polygon.vertices) == 4:
                area += calculateTriangleArea(mesh, [polygon.vertices[i] for i in (0, 1, 2)], matrix)
                area += calculateTriangleArea(mesh, [polygon.vertices[i] for i in (0, 2, 3)], matrix)
            else:
                tris = ngon_tessellate(mesh, polygon.vertices)
                for tri in tris:
                    area += calculateTriangleArea(mesh, tri, matrix)

    return area
                

def calculateTriangleVolume(vertices, reference_point):
    # vertices are already in the right order, thanks to Blender
    vcs = []
    for v in vertices:
        v4 = v.to_4d()
        v4[3] = 1.0
        vcs.append(v4)
    ref4 = reference_point.to_4d()
    ref4[3] = 1.0
    vcs.append(ref4)

    return Matrix(vcs).determinant()/6.0

def calculateTriangleCOM(vertices, reference_point):
    v = vertices.copy()
    v.append(reference_point)
    return arithmeticMean(v)


def calculatePolygonVolume(mesh, polygon, reference_point):
    if len(polygon.vertices) == 3:
        vcs = [mesh.vertices[polygon.vertices[i]].co for i in (0, 1, 2)]
        return calculateTriangleVolume(vcs, reference_point)

    elif len(polygon.vertices) == 4:
        vcs1 = [mesh.vertices[polygon.vertices[i]].co for i in (0, 1, 2)]
        vcs2 = [mesh.vertices[polygon.vertices[i]].co for i in (0, 2, 3)]
        v1 = calculateTriangleVolume(vcs1, reference_point)
        v2 = calculateTriangleVolume(vcs2, reference_point)
        return v1 + v2

    else:
        volume = 0.0
        tris = ngon_tessellate(mesh, polygon.vertices)
        for tri in tris:
            volume += calculateTriangleVolume(
                [mesh.vertices[i].co for i in tri], reference_point)
        return volume



def calculatePolygonCOM(mesh, polygon, reference_point):
    if len(polygon.vertices) == 3:
        vcs = [mesh.vertices[polygon.vertices[i]].co for i in (0, 1, 2)]
        return calculateTriangleCOM(vcs, reference_point)

    elif len(polygon.vertices) == 4:
        vcs1 = [mesh.vertices[polygon.vertices[i]].co for i in (0, 1, 2)]
        vcs2 = [mesh.vertices[polygon.vertices[i]].co for i in (0, 2, 3)]
        v1 = calculateTriangleVolume(vcs1, reference_point)
        v2 = calculateTriangleVolume(vcs2, reference_point)
        com1 = calculateTriangleCOM(vcs1, reference_point)
        com2 = calculateTriangleCOM(vcs2, reference_point)
        return (com1*v1 + com2*v2)/(v1 + v2)

    else:
        couples = []
        tris = ngon_tessellate(mesh, polygon.vertices)
        for tri in tris:
            vs = [mesh.vertices[i].co for i in tri]
            couples.append(
                (calculateTriangleCOM(vs, reference_point),
                 calculateTriangleVolume(vs, reference_point)))
        return weightedMean(couples)


def calculateVolume(mesh, reference_point=Vector((0.0, 0.0, 0.0))):
    """
    Same method as in "Measure Panel" addon.
    See Sheue-ling Lien, James T. Kajiya,
        "A Symbolic Method for Calculating the Integral Properties
         of Arbitrary Nonconvex Polyhedra"
        IEEE October 1984
    """
    volume = 0.0
    for polygon in mesh.polygons:
        volume += calculatePolygonVolume(mesh, polygon, reference_point)
    
    return volume



def calculateCOM_Volume(mesh, reference_point=Vector((0.0, 0.0, 0.0))):
    couples = []
    for polygon in mesh.polygons:
        v = calculatePolygonVolume(mesh, polygon, reference_point)
        com = calculatePolygonCOM(mesh, polygon, reference_point)
        couples.append((com, v))
    
    return weightedMean(couples)


def calculateCOM_Faces(mesh):
    couples = []
    for polygon in mesh.polygons:
        couples.append((polygon.center, polygon.area))
    
    return weightedMean(couples)


def calculateCOM_Edges(mesh):
    couples = []
    for edge in mesh.edges:
        v1, v2 = [mesh.vertices[edge.vertices[i]].co for i in range(2)]
        # not necessary to run arithmeticMean() for 2 vertices...
        couples.append(((v1 + v2)/2.0, (v2 - v1).length))
    
    return weightedMean(couples)


def calculateCOM_Vertices(mesh):
    points = [vertex.co for vertex in mesh.vertices]
    
    return arithmeticMean(points)



def isManifold(mesh, do_check=True):
    if not do_check:
        return True

    """
    edges = {}
    for poly in mesh.polygons:
        for k in poly.edge_keys:
            if k in edges:
                if edges[k] > 1:
                    return False
                edges[k] += 1
            else:
                edges[k] = 1

    s = sorted(edges.values())
    if s[0] != 2 or s[-1] != 2:
        print(2)
        return False
    """

    s = sorted(edge_face_count(mesh))
    if s[0] != 2 or s[-1] != 2:
        return False

    # XXX: check for verts/edges out of faces?
    """
    for edge in mesh.edges:
        if edge not in edges:
            return False
    """

    return True


def isNormalsOrientationClean(mesh, do_check=True):
    if not do_check:
        return True
    
    for i, p in enumerate(mesh.polygons):
        e = p.edge_keys
        set_e = set(e)
        p_edges = [(p.vertices[i - 1], v) for i, v in enumerate(p.vertices)]
        for q in mesh.polygons[i + 1:]:
            f = q.edge_keys
            q_edges = [(q.vertices[i - 1], v) for i, v in enumerate(q.vertices)]
            inter = set_e.intersection(set(f))
            if len(inter) == 0:
                continue
            vs = inter.pop()
            if (vs in p_edges) == (vs in q_edges):
                return False

    return True



def updateScene(scene=None, force=False):
    if bpy.context.mode == 'OBJECT':
        if bpy.context.object is not None:
            if bpy.context.object.type == 'MESH':
                if bpy.context.object.data is not None:
                    obj = bpy.context.object
                    mesh = obj.data
                    stat = bpy.context.window_manager.mesh_statistics

                    if stat.updating_locked or force:

                        error_manifold = False
                        error_normals = False

                        if stat.area_use:
                            stat.area = calculateArea(mesh, obj.matrix_world)
                        if stat.volume_use or (stat.com_use and stat.com_method == 'VOLUME'):
                            if isManifold(mesh, stat.check_mesh):
                                if isNormalsOrientationClean(mesh, stat.check_mesh):
                                    if stat.reference_point_auto:
                                        stat.reference_point = calculateCOM_Vertices(mesh)
                                else:
                                    error_normals = True
                            else:
                                error_manifold = True
                        if stat.volume_use:
                            if not error_manifold and not error_normals:
                                stat.volume = calculateVolume(mesh, Vector(stat.reference_point))*obj.scale[0]*obj.scale[1]*obj.scale[2]
                        if stat.com_use:
                            if stat.com_method == 'VERTICES':
                                stat.com = obj.matrix_world * calculateCOM_Vertices(mesh)
                            elif stat.com_method == 'EDGES':
                                stat.com = obj.matrix_world * calculateCOM_Edges(mesh)
                            elif stat.com_method == 'FACES':
                                stat.com = obj.matrix_world * calculateCOM_Faces(mesh)
                            elif stat.com_method == 'VOLUME':
                                if not error_manifold and not error_normals:
                                    stat.com = obj.matrix_world * calculateCOM_Volume(mesh, Vector(stat.reference_point))

                        stat.error_manifold = error_manifold
                        stat.error_normals = error_normals


                    if (stat.com_draw and stat.com_use and
                        (stat.com_method != 'VOLUME' or
                         (not stat.error_manifold and not stat.error_normals))):
                        do_draw[0] = True
                        com[0] = stat.com
                    else:
                        do_draw[0] = False



def refreshScene(self, context):
    bpy.ops.wm.com_refresh()

def refreshSceneIfManual(self, context):
    if not self.reference_point_auto:
        bpy.ops.wm.com_refresh()



def drawCallback():
    if bpy.context.mode == 'OBJECT':
        if do_draw[0]:
            # from math_viz
            glPointSize(5.0)
            glBegin(GL_POINTS)
            glColor3f(0.0, 1.0, 0.0)
            glVertex3f(*com[0])
            glEnd()
            glPointSize(1.0)
    


class MeshStatisticsCollectionGroup(bpy.types.PropertyGroup):
    com = bpy.props.FloatVectorProperty(
        name="Center of Mass",
        description="Mean position of the mesh elements",
        size=3,
        precision=5)
    com_method = bpy.props.EnumProperty(
        name="Method",
        description="Method used to calculate the Center of Mass",
        items=[('VERTICES', "Vertices", "Arithmetic mean of the vertices' positions"),
               ('EDGES', "Edges", "Mean of the edges centers weighted with their lengths"),
               ('FACES', "Faces", "Mean of the faces centers weighted with their areas"),
               ('VOLUME', "Volume", "Mean of the centers of mass of the faces tetrahedrons "\
                                    "with respect to an arbitrary reference point; "\
                                    "theoretically the most accurate method")],
        default='VOLUME',
        update=refreshScene)
    com_use = bpy.props.BoolProperty(
        name="Center of Mass",
        description="Display the mesh Center of Mass",
        default=False,
        update=refreshScene)
    com_draw = bpy.props.BoolProperty(
        name="Draw",
        description="Draw the mesh Center of Mass in the View; note: "\
                    "it may be hidden behind faces, look in Wire Shading Mode if needed",
        default=False)
    area = bpy.props.FloatProperty(
        name="Area",
        description="Sum of the mesh faces areas",
        precision=5)
    area_use = bpy.props.BoolProperty(
        name="Area",
        description="Display the mesh Area",
        default=False,
        update=refreshScene)
    volume = bpy.props.FloatProperty(
        name="Volume",
        description="Sum of the mesh faces tetrahedrons "\
                    "with respect to an arbitrary reference point; "\
                    "exact for manifold meshes",
        precision=5)
    volume_use = bpy.props.BoolProperty(
        name="Volume",
        description="Display the mesh Volume",
        default=False,
        update=refreshScene)
    reference_point = bpy.props.FloatVectorProperty(
        name="Reference Point",
        description="Point to be used for volume and center of mass "\
                    "calculation (in local space); "\
                    "arbitrary, but can help restricting rounding errors",
        size=3,
        precision=5,
        update=refreshSceneIfManual)
    reference_point_auto = bpy.props.BoolProperty(
        name="Automatic Reference Point",
        description="Automatically pick up a reference point (the center of the vertices)",
        default=True,
        update=refreshScene)
    error_manifold = bpy.props.BoolProperty(
        default=False)
    error_normals = bpy.props.BoolProperty(
        default=False)
    updating_locked = bpy.props.BoolProperty(
        name="Locked Refresh",
        description="Whether to continuously update values",
        default=False)
    check_mesh = bpy.props.BoolProperty(
        name="Check Mesh",
        description="Whether to check if mesh is manifold and has good normals; "\
                    "this is a heavy calculation, to be avoided if not necessary",
        default=False,
        update=refreshScene)



class COMToEmptyOperator(bpy.types.Operator):
    bl_idname = "wm.com_to_empty"
    bl_label = "Place Empty"
    bl_description = "Create an Empty at the mesh Center of Mass position and set it as active object"
    
    @classmethod
    def poll(cls, context):
        return (context.area.type == 'VIEW_3D' and
            context.mode == 'OBJECT' and
            context.object is not None and
            context.object.type == 'MESH' and
            context.object.data is not None)

    def execute(self, context):
        obj = context.object

        com = context.window_manager.mesh_statistics.com

        bpy.ops.object.add(type='EMPTY', location=com)

        # context change?
        bpy.context.object.name = "COM_" + obj.name
        bpy.context.object.show_x_ray = True

        return {'FINISHED'}



class RefreshOperator(bpy.types.Operator):
    bl_idname = "wm.com_refresh"
    bl_label = "Refresh"
    bl_description = "Update values"

    @classmethod
    def poll(cls, context):
        return (context.area.type == 'VIEW_3D' and
            context.mode == 'OBJECT' and
            context.object is not None and
            context.object.type == 'MESH' and
            context.object.data is not None)

    def execute(self, context):
        if not context.window_manager.mesh_statistics.updating_locked:
            updateScene(force=True)
        return {'FINISHED'}




def Vector3DToString(vector):
    return "x: %.5f   y: %.5f   z: %.5f" % tuple(vector)

    
class MeshStatisticsPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Mesh Statistics"

    
    @classmethod
    def poll(cls, context):
        return (context.area.type == 'VIEW_3D' and
            context.mode == 'OBJECT' and
            context.object is not None and
            context.object.type == 'MESH' and
            context.object.data is not None)

    def draw(self, context):
        layout = self.layout

        stat = context.window_manager.mesh_statistics

        row = layout.row()
        split = row.split(percentage=0.3)
        split2 = split.split(align=True)
        if stat.updating_locked:
            split2.operator("wm.com_refresh", text="", icon='FILE_REFRESH', emboss=False)
            split2.prop(stat, "updating_locked", icon_only=True, toggle=True, icon='LOCKED')
        else:
            split2.operator("wm.com_refresh", text="", icon='FILE_REFRESH')
            split2.prop(stat, "updating_locked", icon_only=True, toggle=True, icon='UNLOCKED')
            
        row = layout.row()
        row.prop(stat, "area_use")
        if stat.area_use:
            row.label(text="%.5f" % stat.area)

        row = layout.row()
        row.prop(stat, "volume_use")
        if stat.volume_use:
            if not stat.error_manifold and not stat.error_normals:
                row.label(text="%.5f" % stat.volume)

        row = layout.row()
        row.prop(stat, "com_use")
        if stat.com_use:
            row = layout.row()
            row.prop(stat, "com_method", expand=True)
            if stat.com_method == 'VOLUME':
                if not stat.error_manifold and not stat.error_normals:
                    split = layout.split(percentage=0.7)
                    split.label(text=Vector3DToString(stat.com))
                    split2 = split.split(align=True)
                    split2.prop(stat, "com_draw", toggle=True)
                    split2.operator("wm.com_to_empty")

            else:
                split = layout.split(percentage=0.7)
                split.label(text=Vector3DToString(stat.com))
                split2 = split.split(align=True)
                split2.prop(stat, "com_draw", toggle=True)
                split2.operator("wm.com_to_empty")


        if stat.volume_use or (stat.com_use and stat.com_method == 'VOLUME'):
            box = layout.box()
            box.label("Volume & Volume Center of Mass Options")
            split = box.split(percentage=0.4)
            split.prop(stat, "check_mesh")
            split.label(text="Warning: heavy calculation!", icon='ERROR')
            if stat.error_manifold:
                column = box.column(align=True)
                column.label(text="Error: mesh is not manifold;", icon='CANCEL')
                column.label(text="this could lead to wrong calculations;")
                column.label(text="try to find problematic edges and vertices")
            elif stat.error_normals:
                column = box.column(align=True)
                column.label(text="Error: mesh normals orientation is not consistent;", icon='CANCEL')
                column.label(text="this could lead to wrong calculations;")
                column.label(text="try to recalculate them")
                               
            else:                        
                row = box.row()
                row.prop(stat, "reference_point_auto")
                if not stat.reference_point_auto:
                    row = box.row()
                    row.prop(stat, "reference_point")
            
        

def register():
    bpy.utils.register_module(__name__)
    bpy.types.WindowManager.mesh_statistics = bpy.props.PointerProperty(
        type=MeshStatisticsCollectionGroup)
    bpy.app.handlers.scene_update_post.append(updateScene)
    if not handle:
        handle[:] = [bpy.types.SpaceView3D.draw_handler_add(drawCallback, (), 'WINDOW', 'POST_VIEW')]

def unregister():
    del bpy.types.WindowManager.mesh_statistics
    # to be sure...
    if updateScene in bpy.app.handlers.scene_update_post:
        bpy.app.handlers.scene_update_post.remove(updateScene)
    if handle:
        bpy.types.SpaceView3D.draw_handler_remove(handle[0], 'WINDOW')
        handle[:] = []
    bpy.utils.unregister_module(__name__)
    

if __name__ == "__main__":
    register()
