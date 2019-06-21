"""Geometry module.

This module contain geometry utilities.
"""
import mathutils

# coords in blender start from bottom-right corner as (0.0, 0.0)
# so change accordling


class Rectangle():
    """Rectangle rappresentation.

    :param lowest: lowest corner
    :type lowest: :class:`mathutils.Vector`
    :param highest: highest corner
    :type lowest: :class:`mathutils.Vector`
    """

    def __init__(self, lowest, highest):
        self.__topLeft = mathutils.Vector((lowest.x, highest.y))
        self.__bottomRight = mathutils.Vector((highest.x, lowest.y))

    def topLeft(self):
        """Return the top left corner.

        :return: top left corner
        :rtype: :class:`mathutils.Vector`
        """
        return self.__topLeft

    def top(self):
        """Return the top.

        :return: top edge
        :rtype: int
        """
        return self.__topLeft.y

    def topRight(self):
        """Return the top right corner.

        :return: top right corner
        :rtype: :class:`mathutils.Vector`
        """
        return mathutils.Vector((self.__bottomRight.x, self.__topLeft.y))

    def right(self):
        """Return the right edge.

        :return: right edge
        :rtype: int
        """
        return self.__bottomRight.x

    def bottomRight(self):
        """Return the bottom right corner.

        :return: top bottom right
        :rtype: :class:`mathutils.Vector`
        """
        return self.__bottomRight

    def bottom(self):
        """Return the bottom edge.

        :return: bottom edge
        :rtype: int
        """
        return self.__bottomRight.y

    def bottomLeft(self):
        """Return the bottom left corner.

        :return: bottom left
        :rtype: :class:`mathutils.Vector`
        """
        return mathutils.Vector((self.__topLeft.x, self.__bottomRight.y))

    def left(self):
        """Return the left edge.

        :return: left edge
        :rtype: int
        """
        return self.__topLeft.x

    def center(self):
        """Return the bounding box center.

        :return: rectangle center
        :rtype: :class:`mathutils.Vector`
        """
        return (self.__topLeft + self.__bottomRight) / 2


class Size():
    """Rappresentation of size.

    :param width: width.
    :type width: float
    :param height: height.
    :type height: float
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height
