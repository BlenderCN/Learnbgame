"""TODO: DOC"""

import collections
import enum


class VertexComponentMask(enum.IntFlag):
    Coord = 1 << 0
    Normal = 1 << 1
    NormalUB4N = 1 << 2
    Uv0 = 1 << 3
    Uv0S2 = 1 << 4
    Uv1 = 1 << 5
    Uv1S2 = 1 << 6
    Uv2 = 1 << 7
    Uv2S2 = 1 << 8
    Uv3 = 1 << 9
    Uv3S2 = 1 << 10
    Color = 1 << 11
    ColorUB4N = 1 << 12
    Tangent = 1 << 13
    TangentUB4N = 1 << 14
    Binormal = 1 << 15
    BinormalUB4N = 1 << 16
    Weights = 1 << 17
    WeightsUB4N = 1 << 18
    JIndices = 1 << 19
    JIndicesUB4 = 1 << 20


VertexComponentData = collections.namedtuple('VertexComponent',
                                             'format count size')
VertexComponents = {
            VertexComponentMask.Coord:        VertexComponentData('3f', 3, 4),
            VertexComponentMask.Normal:       VertexComponentData('3f', 3, 4),
            VertexComponentMask.NormalUB4N:   VertexComponentData('4B', 4, 1),
            VertexComponentMask.Uv0:          VertexComponentData('2f', 2, 4),
            VertexComponentMask.Uv0S2:        VertexComponentData('2h', 2, 2),
            VertexComponentMask.Uv1:          VertexComponentData('2f', 2, 4),
            VertexComponentMask.Uv1S2:        VertexComponentData('2h', 2, 2),
            VertexComponentMask.Uv2:          VertexComponentData('2f', 2, 4),
            VertexComponentMask.Uv2S2:        VertexComponentData('2h', 2, 2),
            VertexComponentMask.Uv3:          VertexComponentData('2f', 2, 4),
            VertexComponentMask.Uv3S2:        VertexComponentData('2h', 2, 2),
            VertexComponentMask.Color:        VertexComponentData('4f', 4, 4),
            VertexComponentMask.ColorUB4N:    VertexComponentData('4B', 4, 1),
            VertexComponentMask.Tangent:      VertexComponentData('3f', 4, 4),
            VertexComponentMask.TangentUB4N:  VertexComponentData('4B', 4, 1),
            VertexComponentMask.Binormal:     VertexComponentData('3f', 3, 4),
            VertexComponentMask.BinormalUB4N: VertexComponentData('4B', 4, 1),
            VertexComponentMask.Weights:      VertexComponentData('4f', 4, 4),
            VertexComponentMask.WeightsUB4N:  VertexComponentData('4B', 4, 1),
            VertexComponentMask.JIndices:     VertexComponentData('4f', 4, 4),
            VertexComponentMask.JIndicesUB4:  VertexComponentData('4B', 4, 1)}

Header = collections.namedtuple('Header', 'magic \
                                           num_groups \
                                           num_vertices \
                                           vertex_width \
                                           num_triangles \
                                           num_edges \
                                           vertex_components')

Group = collections.namedtuple('Group', 'vertex_first \
                                         vertex_count \
                                         triangle_first \
                                         triangle_count \
                                         edge_first \
                                         edge_count')

Vertex = collections.namedtuple('Vertex', 'coord \
                                           uv0 \
                                           uv1 \
                                           uv2 \
                                           uv3')
