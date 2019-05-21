'''
Created on 2 wrz 2015

@author: Komi
'''
from math import acos, cos, sin, sqrt, pi

class CoordsConverter(object):

    @staticmethod
    def ToXY(RefX, RefY, alpha, radius):
        outX = RefX + radius * cos(alpha)
        outY = RefY + radius * sin(alpha)

        return outX, outY

    @staticmethod
    def ToAngular(RefX, RefY, x, y):

        r = sqrt((x - RefX) ** 2 + (y - RefY) ** 2)
        if r != 0:
            alpha = acos((x - RefX) / r)
        else:
            alpha = 0.0


        if (y < RefY):  # adjustment for third and fourth quarter of coords system
            alpha = 2 * pi - alpha

        return alpha, r

