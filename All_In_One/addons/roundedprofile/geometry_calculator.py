'''
Created on 28 cze 2015

@author: Komi
'''
from math import fabs, sqrt, acos, degrees, pi

from mathutils import Vector

LINE_TOLERANCE = 0.0001

class GeometryCalculator(object):
    '''
    classdocs
    '''
    XY = 'XY'
    XZ = 'XZ'
    YZ = 'YZ'

    selectedPlane = XY

    def __init__(self):
        '''
        Constructor
        '''
        pass



    def getVectorAndLengthFrom2Points(self, c1, c2):
        if (c1 == None) or (c2 == None):
            return (None, None)
        center_vec = c2 - c1
        center_vec_len = center_vec.length
        return (center_vec, center_vec_len)

    def getCircleIntersections(self, center1, r1, center2, r2):

        center_vec, center_vec_len = self.getVectorAndLengthFrom2Points(center1, center2)
        vec = None
        sumOfRadius = r1 + r2
        differenceOfRadius = fabs(r1 - r2)

        if ((center1 == center2) and (r1 == r2)):
            return None
        if center_vec_len == 0:
            return None

        if (sumOfRadius == center_vec_len):  # one intersection
            vec = center1 + center_vec * r1 / center_vec_len
            return [vec]
        elif (differenceOfRadius == center_vec_len):  # one intersection
            vec = center1 - center_vec * r1 / center_vec_len
            return [vec]
        elif ((sumOfRadius > center_vec_len) and (differenceOfRadius > center_vec_len)) or (sumOfRadius < center_vec_len):  # none intersections:
            return None
        elif (sumOfRadius > center_vec_len) and (differenceOfRadius < center_vec_len):  # two intersections
            return self.calculateTwoIntersections(center1, r1, center2, r2)
        else:
            return 333

    def calculateTwoIntersections(self, center1, r1, center2, r2):
        center_vec, center_vec_len = self.getVectorAndLengthFrom2Points(center1, center2)
        x = None
        if r1 > center_vec_len or r2 > center_vec_len :
            x = self._getXWhenCirclesHaveLargeOverlap(center_vec_len, r1, r2)
            return self.calculateCircleIntersectionsWithLargeOverlap(center1, r1, center2, r2, x)
        else:
            x = self._getXWhenCirclesHaveSmallOverlap(center_vec_len, r1, r2)
            return self.calculateCircleIntersectionsWithSmallOverlap(center1, r1, center2, r2, x)

    def _getXWhenCirclesHaveLargeOverlap(self, A, r1, r2):
        return ((A ** 2 + r2 ** 2) - r1 ** 2) / (-2 * A)

    def _getXWhenCirclesHaveSmallOverlap(self, A, r1, r2):
        return ((A ** 2 + r2 ** 2) - r1 ** 2) / (2 * A)


    def getPerpendicularVector(self, center_vec):
        if self.selectedPlane == self.XY:
            return Vector((-center_vec[1], center_vec[0], center_vec[2]))
        elif self.selectedPlane == self.YZ:
            return Vector((center_vec[0], -center_vec[2], center_vec[1]))
        elif self.selectedPlane == self.XZ:
            return Vector((-center_vec[2], center_vec[1], center_vec[0]))

    def calculateCircleIntersectionsWithLargeOverlap(self, center1, r1, center2, r2, x):
        #
        center_vec, center_vec_len = self.getVectorAndLengthFrom2Points(center1, center2)
        A = center_vec_len
        h = sqrt(r2 ** 2 - x ** 2)

        intersectionX = center2 + center_vec * (x / A)
        perpendicularVec = self.getPerpendicularVector(center_vec)  # TODO calculate perpendicular based on selected plane
        perpendicularVecLen = perpendicularVec.length
        intersection1 = intersectionX + perpendicularVec * (h / perpendicularVecLen)
        intersection2 = intersectionX - perpendicularVec * (h / perpendicularVecLen)

        return [intersection1, intersection2]

    def calculateCircleIntersectionsWithSmallOverlap(self, center1, r1, center2, r2, x):
        #
        center_vec, center_vec_len = self.getVectorAndLengthFrom2Points(center1, center2)
        A = center_vec_len
        h = sqrt(r2 ** 2 - x ** 2)

        intersectionX = center1 + center_vec * ((A - x) / A)
        perpendicularVec = self.getPerpendicularVector(center_vec)  # TODO calculate perpendicular based on selected plane
        perpendicularVecLen = perpendicularVec.length
        intersection1 = intersectionX + perpendicularVec * (h / perpendicularVecLen)
        intersection2 = intersectionX - perpendicularVec * (h / perpendicularVecLen)

        return [intersection1, intersection2]




    def getAngleBetween3Points(self, point1, point2, point3):
        p2p1Vector, p2p1Length = self.getVectorAndLengthFrom2Points(point2, point1)
        p1p3Vector, p1p3Length = self.getVectorAndLengthFrom2Points(point1, point3)
        p2p3Vector, p2p3Length = self.getVectorAndLengthFrom2Points(point2, point3)

        if (p2p1Vector == None) or (p1p3Vector == None) or (p2p3Vector == None):
            return (None, None)

        if p2p1Vector.normalized() == p2p3Vector.normalized() :
            angle = 0.0
            return angle, angle

        if p2p1Vector.normalized() == p2p3Vector.normalized().negate() :
            angle = pi
            return angle, degrees(angle)

        A = p2p1Length
        B = p2p3Length
        C = p1p3Length

        y = (A ** 2 + C ** 2 - B ** 2) / (2 * C)
        x = sqrt(A ** 2 - y ** 2)

        alpha = 0
        beta = 0
        if (A != 0):
            alpha = acos(x / A)
        if (B != 0):
            beta = acos(x / B)
        angle = alpha + beta
        angle = self._adjustAnglePlusOrMinus(point1, point3, p2p1Vector, angle)
        angleDeg = degrees(angle)

        return (angleDeg, angle)

    def getPositiveAngleBetween3Points(self, point1, point2, point3):
        angleDeg, angle = self.getAngleBetween3Points(point1, point2, point3)
        if angle == None:
            return None, None

        if angle < 0:
            angle = (2 * pi) + angle
        return degrees(angle), angle


    def _adjustAnglePlusOrMinus(self, point1, point3, p2p1Vector, angle):
        MinusVector = self.getPerpendicularVector(p2p1Vector)
        PlusVector = (-1) * MinusVector
        P1Plus = point1 + PlusVector
        P1Minus = point1 + MinusVector
        P1PlusP3Vector, P1PlusP3Length = self.getVectorAndLengthFrom2Points(P1Plus, point3)
        P1MinusP3Vector, P1MinusP3Length = self.getVectorAndLengthFrom2Points(P1Minus, point3)
        if (P1MinusP3Length < P1PlusP3Length):
            angle = -angle
        return angle

    def getCoefficientsForLineThrough2Points(self, point1, point2):
        x1, y1, z1 = point1
        x2, y2, z2 = point2

        # mapping x1,x2, y1,y2 to proper values based on plane
        if self.selectedPlane == self.YZ:
            x1 = y1
            x2 = y2
            y1 = z1
            y2 = z2
        if self.selectedPlane == self.XZ:
            y1 = z1
            y2 = z2

        # Further calculations the same as for XY plane
        xabs = abs(x2 - x1)
        yabs = abs(y2 - y1)

        if xabs <= LINE_TOLERANCE:
            return None  # this means line x = edgeCenterX
        if yabs <= LINE_TOLERANCE:
            A = 0
            B = y1
            return A, B
        A = (y2 - y1) / (x2 - x1)
        B = y1 - (A * x1)
        return (A, B)

    def getLineCircleIntersections(self, lineAB, circleMidPoint, radius):
        # (x - a)**2 + (y - b)**2 = r**2 - circle equation
        # y = A*x + B - line equation
        # f * x**2 + g * x + h = 0 - quadratic equation
        if (lineAB == None) or (circleMidPoint == None):
            return None
        A, B = lineAB
        a, b, c = circleMidPoint
        f = 1 + (A ** 2)
        g = -2 * a + 2 * A * B - 2 * A * b
        h = (B ** 2) - 2 * b * B - (radius ** 2) + (a ** 2) + (b ** 2)
        coef = [f, g, h]
        roots = self.getQuadraticRoots(coef)
        if roots != None:
            x1 = roots[0]
            x2 = roots[1]
            # TODO: handle XZ and YZ
            point1 = Vector((x1, A * x1 + B, c))
            point2 = Vector((x2, A * x2 + B, c))
            return [point1, point2]
        else:
            return None

    def getLineCircleIntersectionsWhenXPerpendicular(self, verticalLinePoint, circleMidPoint, radius):
        # (x - a)**2 + (y - b)**2 = r**2 - circle equation
        # x = xValue - line equation
        # f * x**2 + g * x + h = 0 - quadratic equation
        xValue = verticalLinePoint[0]
        if self.selectedPlane == self.YZ:
            xValue = verticalLinePoint[1]
        if self.selectedPlane == self.XZ:
            xValue = verticalLinePoint[0]

        a, b, c = circleMidPoint
        f = 1
        g = -2 * b
        h = (a ** 2) + (b ** 2) + (xValue ** 2) - 2 * a * xValue - (radius ** 2)
        coef = [f, g, h]
        roots = self.getQuadraticRoots(coef)
        if roots != None:
            y1 = roots[0]
            y2 = roots[1]
            point1 = Vector((xValue, y1, c))
            point2 = Vector((xValue, y2, c))
            return [point1, point2]
        else:
            return None

    def getLineCoefficientsPerpendicularToVectorInPoint(self, point, vector):
        x, y, z = point
        xVector, yVector, zVector = vector
        destinationPoint = (x + yVector, y - xVector, z)
        if self.selectedPlane == self.YZ:
            destinationPoint = (x , y + zVector, z - yVector)
        if self.selectedPlane == self.XZ:
            destinationPoint = (x + zVector, y, z - xVector)
        return self.getCoefficientsForLineThrough2Points(point, destinationPoint)

    def getQuadraticRoots(self, coef):
        if len(coef) != 3:
            return NaN
        else:
            a, b, c = coef
            delta = b ** 2 - 4 * a * c
            if delta == 0:
                x = -b / (2 * a)
                return (x, x)
            elif delta < 0:
                return None
            else :
                x1 = (-b - sqrt(delta)) / (2 * a)
                x2 = (-b + sqrt(delta)) / (2 * a)
                return (x1, x2)

    def getClosestPointToRefPoint(self, points, refCenter):
        closestPoint = None
        lowestLength = None
        for point in points:
            currentVector, currentLength = self.getVectorAndLengthFrom2Points(point, refCenter)
            if (lowestLength == None or currentLength < lowestLength):
                lowestLength = currentLength
                closestPoint = point
        return closestPoint

    def getFarthestPointToRefPoint(self, points, refCenter):
        farthestPoint = None
        highestLength = None
        for point in points:
            currentVector, currentLength = self.getVectorAndLengthFrom2Points(point, refCenter)
            if (highestLength == None or currentLength > highestLength):
                highestLength = currentLength
                farthestPoint = point
        return farthestPoint
