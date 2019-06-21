from arnold import *
from mathutils import Matrix

def MakeAtMatrix(bmatrix):
    matrix = AtMatrix()
    matrix.a00 = bmatrix[0][0]
    matrix.a01 = bmatrix[0][1]
    matrix.a02 = bmatrix[0][2]
    matrix.a03 = bmatrix[0][3]
    matrix.a10 = bmatrix[1][0]
    matrix.a11 = bmatrix[1][1]
    matrix.a12 = bmatrix[1][2]
    matrix.a13 = bmatrix[1][3]
    matrix.a20 = bmatrix[2][0]
    matrix.a21 = bmatrix[2][1]
    matrix.a22 = bmatrix[2][2]
    matrix.a23 = bmatrix[2][3]
    matrix.a30 = bmatrix[3][0]
    matrix.a31 = bmatrix[3][1]
    matrix.a32 = bmatrix[3][2]
    matrix.a33 = bmatrix[3][3]
    return matrix

def getYUpMatrix(bmatrix):
    rotMatrix = Matrix.Rotation(math.radians(-90),4,'X')  * bmatrix 
    return MakeAtMatrix(rotMatrix)

def mapValue(val):
    if val in [False,True]:
        return str(val).lower()
    else:
        return str(val)
        
def formatProperty(prop,val):
    if val == None:
        return ""
    if prop == 'matrix':
        return "\t%s%s\n" %(prop,formatMatrix(val))
    else:
        return "\t%s%s%s\n" % (prop," "*max(1,40 - len(prop)),mapValue(val))

def formatList(prop,val,list):
    value = list[val]
    return "\t%s%s%s\n" % (prop," "*max(1,40 - len(prop)),mapValue(value))

#####
#
# matrix    a list of matrices
def formatMatrix(matrixList):
    msg = " 1 %s MATRIX\n" % len(matrixList)
    for matrix in matrixList:
        msg += " "*44+(" ".join("%s" % (k) for k in matrix[0][0:]))+"\n"
        msg +=" "*44+(" ".join("%s" % (k) for k in matrix[1][0:]))+"\n"
        msg +=" "*44+(" ".join("%s" % (k) for k in matrix[2][0:]))+"\n"
        msg +=" "*44+(" ".join("%s" % (k) for k in matrix[3][0:]))
        if matrix != matrixList[-1]:
            msg +="\n"
    return msg
