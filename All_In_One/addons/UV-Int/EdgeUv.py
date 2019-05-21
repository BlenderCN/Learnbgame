# Nikita Akimov
# interplanety@interplanety.org

from .Vector2d import Vector2d


class EdgeUv:

    def __init__(self, index, vertexuv1, vertexuv2):
        # (int, VertexUv, VertexUv)
        self.__index = index
        self.__vertexes = [vertexuv1, vertexuv2]

    def __repr__(self):
        return "EdgeUv(({}) 0: {}, 1: {})".format(self.__index, self.__vertexes[0], self.__vertexes[1])

    @property
    def vertexes(self):
        return self.__vertexes

    @staticmethod
    def edgepointside(edge, point):
        # (EdgeUv, VertexUV)
        # >0 - right
        # <0 - left
        # ==0 - on edge
        side = (point.x - edge.vertexes[0].x) * (edge.vertexes[1].y - edge.vertexes[0].y) - (point.y - edge.vertexes[0].y) * (edge.vertexes[1].x - edge.vertexes[0].x)
        return -1 if side < 0 else (1 if side > 0 else 0)

    def pointside(self, point):
        return __class__.edgepointside(self, point)

    def normal(self):
        return Vector2d(self.__vertexes[1].y - self.__vertexes[0].y, self.__vertexes[0].x - self.__vertexes[1].x).normalize()
