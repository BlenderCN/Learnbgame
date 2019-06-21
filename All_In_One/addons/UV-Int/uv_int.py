# Nikita Akimov
# interplanety@interplanety.org

import bpy
from .Uvmap import Uvmap
from .Polygon2d import Polygon2d


class UV_int_separate(bpy.types.Operator):
    bl_idname = 'uv_int.separate_meshloops'
    bl_label = 'UV-Int: Separate'
    bl_description = 'Separate MeshUVLoops'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.active_object:
            bpy.ops.object.mode_set(mode = 'OBJECT')
            meshdata = bpy.context.active_object.data
            for polygon in meshdata.polygons:
                polygondata = [(meshdata.uv_layers.active.data[ii].uv[:]) for ii in polygon.loop_indices] # uv[:] - Vector -> tuple
                polygoncenter = Polygon2d.polygoncentroid(polygondata)
                for i in polygon.loop_indices:
                    if meshdata.uv_layers.active:
                        meshuvloop = meshdata.uv_layers.active.data[i]
                        if meshuvloop.select:
                            moveto = (meshuvloop.uv - polygoncenter) * 0.8 + polygoncenter
                            meshuvloop.uv.x = moveto.x
                            meshuvloop.uv.y = moveto.y
            bpy.ops.object.mode_set(mode = 'EDIT')
        return {'FINISHED'}


class UV_int_separate_by_edge(bpy.types.Operator):
    bl_idname = 'uv_int.separate_meshloops_by_edge'
    bl_label = 'UV-Int: Separate by edge'
    bl_description = 'Separate MeshUVLoops by edge'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.active_object:
            bpy.ops.object.mode_set(mode = 'OBJECT')
            meshdata = bpy.context.active_object.data
            if meshdata.uv_layers.active:
                selected_data = Uvmap.get_selected_pointgroups(meshdata)
                if selected_data:
                    for pointgoup in selected_data['point_groups']:
                        edgescount = len(selected_data['point_groups'][pointgoup]['edgesmap'])
                        movinglength = None
                        for polygon in selected_data['point_groups'][pointgoup]['polygons']:
                            radius_min = polygon.radius_min()
                            if movinglength is None or movinglength > radius_min:
                                movinglength = radius_min
                        movinglength /= 3
                        movinglength /= edgescount   # делить нм колв-во ребер входящих в группу
                        for point in selected_data['point_groups'][pointgoup]['vertexes']:
                            for edge in selected_data['point_groups'][pointgoup]['edgesmap']:
                                sign = edge.pointside(point.polygon.centroid())
                                if edge.vertexes[0].x == pointgoup[0] and edge.vertexes[0].y == pointgoup[1]:   # for input edges
                                    point.moveto(point.x + sign * movinglength * edge.normal().x, point.y + sign * movinglength * edge.normal().y)
            bpy.ops.object.mode_set(mode = 'EDIT')
        return {'FINISHED'}


class UV_int_weld(bpy.types.Operator):
    bl_idname = 'uv_int.weld_meshloops'
    bl_label = 'UV-Int: Weld'
    bl_description = 'Weld MeshUVLoops'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if bpy.context.active_object and bpy.context.active_object.data.uv_layers.active:
            bpy.ops.uv.weld()
        return {'FINISHED'}


def register():
    bpy.utils.register_class(UV_int_separate)
    bpy.utils.register_class(UV_int_weld)
    bpy.utils.register_class(UV_int_separate_by_edge)


def unregister():
    bpy.utils.unregister_class(UV_int_separate_by_edge)
    bpy.utils.unregister_class(UV_int_weld)
    bpy.utils.unregister_class(UV_int_separate)
