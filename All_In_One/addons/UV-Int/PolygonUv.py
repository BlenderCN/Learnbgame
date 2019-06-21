# Nikita Akimov
# interplanety@interplanety.org

from .Polygon2d import Polygon2d


class PolygonUv(Polygon2d):

    def __init__(self, index, points):
        Polygon2d.__init__(self, index, points)

    def __repr__(self):
        return "PolygonUv ({}) {}".format(self._index, [(point.x, point.y) for point in self.points])
