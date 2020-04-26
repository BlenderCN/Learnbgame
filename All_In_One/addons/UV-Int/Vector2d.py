# Nikita Akimov
# interplanety@interplanety.org

import math


class Vector2d:

    def __init__(self, x, y):
        self.__x = x
        self.__y = y

    def __repr__(self):
        return "Vector2d({x},{y})".format(x=self.__x, y=self.__y)

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, newx):
        self.__x = newx

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, newy):
        self.__y = newy

    def add(self, vec2):
        if isinstance(vec2, Vector2d):
            return Vector2d(self.__x + vec2.__x, self.__y + vec2.__y)

    @staticmethod
    def vector2dsubtract(vec2, vec1):
        if hasattr(vec1,'x') and hasattr(vec1,'y') and hasattr(vec2,'x') and hasattr(vec2,'y'):
            return Vector2d(vec2.x - vec1.x, vec2.y - vec1.y)

    def subtract(self, vec2):
        if hasattr(vec2, 'x') and hasattr(vec2, 'y'):
            return Vector2d(self.x - vec2.x, self.y - vec2.y)

    def length(self):
        return math.sqrt(self.__x ** 2 + self.__y ** 2)

    @staticmethod
    def vector2dnormalize(vec):
        return Vector2d(vec.x / vec.length(), vec.y / vec.length())

    def normalize(self):
        return __class__.vector2dnormalize(self)
