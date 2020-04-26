import numpy

def getVariables(object, mesh):
    variables = {}
    for condition in object.selection_conditions:
        if condition.type == "MASK":
            variables[condition.name] = mask(object, mesh, condition.identifier,
                                                           condition.invert,
                                                           condition)
        if condition.type == "IN_RANGE":
            if condition.rangeType == "MIN_MAX":
                variables[condition.name] = verticesInRange(mesh, condition.minVector,
                                                                  condition.maxVector,
                                                                  condition.invert)
            else:
                variables[condition.name] = verticesInRangeCenter(mesh, condition.centerVector,
                                                                        condition.scaleVector,
                                                                        condition.invert)
        if condition.type == "DIRECTION":
            if condition.angleType == "MIN_MAX":
                variables[condition.name] = pointTo(mesh, condition.direction,
                                                          condition.minAngle,
                                                          condition.maxAngle,
                                                          condition.invert)
            else:
                variables[condition.name] = pointToRange(mesh, condition.direction,
                                                                condition.startAngle,
                                                                condition.angleRange,
                                                                condition.invert)
    return variables

def pointTo(mesh, direction, min, max, invert):
    normals = numpy.array([vert.normal for vert in mesh.verts], float)
    angles = numpy.arccos(numpy.dot(normals, numpy.array(direction)))
    result = (angles >= min) * (angles <= max)
    return ~result if invert else result

def pointToRange(mesh, direction, startAngle, angleRange, invert):
    return pointTo(mesh, direction, startAngle, startAngle + angleRange, invert)

def mask(object, mesh, identifier, invert, condition):
    if identifier in object.data and len(object.data[identifier]) == len(mesh.verts):
        mask = numpy.array(object.data[identifier], dtype=bool)
        condition.outDated = False
    else:
        mask = numpy.full(len(mesh.verts), False)
        condition.outDated = True
    return ~mask if invert else mask

def verticesInRange(mesh, min, max, invert):
    result = numpy.full(len(mesh.verts), False)
    for i, vert in enumerate(mesh.verts):
        co = vert.co
        if ((co.x >= min.x) and (co.y >= min.y) and (co.z >= min.z) and
            (co.x <= max.x) and (co.y <= max.y) and (co.z <= max.z)):
            result[i] = True
    return ~result if invert else result

def verticesInRangeCenter(object, center, scale, invert):
    return verticesInRange(object, center - scale, center + scale, invert)
