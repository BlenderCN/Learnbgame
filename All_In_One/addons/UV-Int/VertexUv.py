# Nikita Akimov
# interplanety@interplanety.org

from .Vector2d import Vector2d


class VertexUv(Vector2d):

    def __init__(self, mesh_uv_loop, polygon):
        super().__init__(mesh_uv_loop.uv.x, mesh_uv_loop.uv.y)
        self.__mesh_uv_loop = mesh_uv_loop
        self.__polygon = polygon

    def __repr__(self):
        return "VertexUv(x: {}, y: {}, MeshUvLoop: {}, Polygon: {})".format(self.x, self.y, self.__mesh_uv_loop, self.__polygon)

    @property
    def polygon(self):
        return self.__polygon

    def moveto(self, newx, newy):
        self.x = newx
        self.y = newy
        self.__mesh_uv_loop.uv.x = newx
        self.__mesh_uv_loop.uv.y = newy
