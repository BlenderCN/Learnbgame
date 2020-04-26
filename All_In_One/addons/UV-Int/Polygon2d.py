# Nikita Akimov
# interplanety@interplanety.org

import mathutils
from .Vector2d import Vector2d


class Polygon2d:

    def __init__(self, index, points):
        self._index = index
        self.__points = []
        if isinstance(points, (list, tuple)):
            self.__points = [Vector2d(point[0], point[1]) for point in points]

    def __repr__(self):
        return "Polygon2d ({}) {}".format(self._index, [(point.x, point.y) for point in self.__points])

    @property
    def index(self):
        return self._index

    @property
    def points(self):
        return self.__points

    @staticmethod
    def polygoncentroid(polygon_data):
        # returns the coordinates of the polygon center by coordinates if its vertexes
        if isinstance(polygon_data, (list, tuple)):
            # polygon_data format = ((0, 0), (1, 0), (1, 1), (0, 1))
            x_list = [vertex[0] for vertex in polygon_data]
            y_list = [vertex[1] for vertex in polygon_data]
            length = len(polygon_data)
            x = sum(x_list) / length
            y = sum(y_list) / length
            return mathutils.Vector((x, y))
        else:
            print(type(polygon_data))
            return None

    def centroid(self):
        return __class__.polygoncentroid([(point.x, point.y) for point in self.__points])

    def radius_min(self):
        rez = None
        centroid = self.centroid()
        for point in self.__points:
            radius = point.subtract(centroid).length()
            if rez is None or radius < rez:
                rez = radius
        return rez
