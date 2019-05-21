# Nikita Akimov
# interplanety@interplanety.org

from .Vector2d import Vector2d
from .VertexUv import VertexUv
from .EdgeUv import EdgeUv
from .PolygonUv import PolygonUv
import copy


class Uvmap:

    @staticmethod
    def get_selected_pointgroups(meshdata):
        data = {"point_groups": {}}
        dataitem = {"vertexes": [], "edges": [], "polygons": [], 'edgesmap': []}
        for polygon_index, polygon in enumerate(meshdata.polygons):
            for i1, i in enumerate(polygon.loop_indices):
                meshuvloop = meshdata.uv_layers.active.data[i]
                meshuvloop_prev = meshdata.uv_layers.active.data[i - 1 if i1 > 0 else i + len(polygon.loop_indices) - 1]
                meshuvloop_next = meshdata.uv_layers.active.data[i + 1 if (i1 < (len(polygon.loop_indices) - 1)) else (i - (len(polygon.loop_indices) - 1))]
                if meshuvloop.select:
                    if meshuvloop.uv[:] not in data['point_groups']:
                        data['point_groups'][meshuvloop.uv[:]] = copy.deepcopy(dataitem)
                    if meshuvloop_next.select and meshuvloop_next.uv[:] not in data['point_groups']:
                        data['point_groups'][meshuvloop_next.uv[:]] = copy.deepcopy(dataitem)
                    polygon_uv = PolygonUv(polygon_index, [(meshdata.uv_layers.active.data[i2].uv[:]) for i2 in polygon.loop_indices])
                    point_uv = VertexUv(meshuvloop, polygon_uv)
                    edge_uv = None
                    if meshuvloop_next.select:
                        edge_uv = EdgeUv(i1, point_uv, VertexUv(meshuvloop_next, polygon_uv))
                    data['point_groups'][meshuvloop.uv[:]]['vertexes'].append(point_uv)
                    if edge_uv:
                        # edges
                        data['point_groups'][meshuvloop.uv[:]]['edges'].append(edge_uv)
                        data['point_groups'][meshuvloop_next.uv[:]]['edges'].append(edge_uv)
                        data['point_groups'][meshuvloop.uv[:]]['edgesmap'].append(EdgeUv(i1, Vector2d(edge_uv.vertexes[0].x, edge_uv.vertexes[0].y), Vector2d(edge_uv.vertexes[1].x, edge_uv.vertexes[1].y)))
                        data['point_groups'][meshuvloop_next.uv[:]]['edgesmap'].append(EdgeUv(i1, Vector2d(edge_uv.vertexes[0].x, edge_uv.vertexes[0].y), Vector2d(edge_uv.vertexes[1].x, edge_uv.vertexes[1].y)))
                    if polygon_uv.index not in [polygon1.index for polygon1 in data['point_groups'][meshuvloop.uv[:]]['polygons']]:
                        data['point_groups'][meshuvloop.uv[:]]['polygons'].append(polygon_uv)
        return data
