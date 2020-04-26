#==============================================================
"""
Mat4 - Transformation matrix interface library
Copyright Benjamin Collins 2016,2018

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software 
without restriction, including without limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons
to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

"""
#==============================================================

import math

class Mat4:

    #constructor
    def __init__(self):
        self.mtx = self.identity()

    # return matrix
    def getMatrix(self):
        return self.mtx

    # create identity
    def identity(self):
        return [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]

    # mutliply by 4x4 matrix
    def multiply(self, factor):
        tmp = self.identity()

        for i in range(4):
            for j in range(4):
                t = 0.0
                for k in range(4):
                    t = t + (self.mtx[i][k] * factor[k][j])
                tmp[i][j] = t

        self.mtx = tmp

    # apply matrix to vec3
    def apply(self, vec3):
        vec3.append(1)
        res = [0,0,0,0]
        for i in range(4):
            t = 0.0
            for j in range(4):
                t = t + (vec3[j] * self.mtx[j][i])
            res[i] = t
        x = res[0] / res[3];
        y = res[1] / res[3];
        z = res[2] / res[3];
        return [x, y, z]

    # scale by vec3
    def scale(self, vec3):
        tmp = self.identity()
        # x
        tmp[0][0] = vec3[0]
        # y
        tmp[1][1] = vec3[1]
        # z
        tmp[2][2] = vec3[2]
        self.multiply(tmp)

    # translate by vec3
    def translate(self, vec3):
        tmp = self.identity()
        # x
        tmp[3][0] = vec3[0]
        # y
        tmp[3][1] = vec3[1]
        # z
        tmp[3][2] = vec3[2]
        self.multiply(tmp)

    # rotate by vec3
    def rotate(self, vec3, zxy_order = False):

        if zxy_order:
            z = vec3[0]
            x = vec3[1]
            y = vec3[2]
        else:
            x = vec3[0]
            y = vec3[1]
            z = vec3[2]

        # rotate x-axis
        tmp = self.identity()
        c = math.cos(x)
        s = math.sin(x)
        tmp[1][1] = c;
        tmp[1][2] = s;
        tmp[2][1] = -s;
        tmp[2][2] = c;
        self.multiply(tmp)

        # rotate y-axis
        tmp = self.identity()
        c = math.cos(y)
        s = math.sin(y)
        tmp[0][0] = c;
        tmp[0][2] = -s;
        tmp[2][0] = s;
        tmp[2][2] = c;
        self.multiply(tmp)

        # rotate z-axis
        tmp = self.identity()
        c = math.cos(z)
        s = math.sin(z)
        tmp[0][0] = c;
        tmp[0][1] = s;
        tmp[1][0] = -s;
        tmp[1][1] = c;
        self.multiply(tmp)

#==============================================================
"""
Program End
"""
#==============================================================
