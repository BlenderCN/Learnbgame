from xml.etree.ElementTree import ElementTree


tree = ElementTree()


def findTag(xmlTree, tag):
    for i in xmlTree.iter():
        # print(i.attrib)
        if i.attrib.get("name", None) == tag:
            return i


def getSubValues(element, func=lambda x: x):
    subVals = list()
    for i in element.iter():
        if i.attrib.get('value', None) is not None:
            appendVal = func(i.attrib['value'])
            if appendVal is not None:
                subVals.append(appendVal)
    return subVals


if __name__ == '__main__':
    with open("COLTEST.GEOMETRY.MBIN.EXML") as f:
        file = tree.parse(source=f)
        bhStarts = getSubValues(findTag(file, "BoundHullVertSt"), int)
        bhEnds = getSubValues(findTag(file, "BoundHullVertEd"), int)
        print(bhStarts)
        print(bhEnds)

        bhVerts = getSubValues(findTag(file, "BoundHullVerts"))
        bhLen = len(bhVerts)
        vert_starts = list(range(bhLen))[1::5]

        # now iterate over each bh mesh
        for i in range(len(bhStarts)):
            sub_vert_starts = vert_starts[bhStarts[i]: bhEnds[i]]
            for svs in sub_vert_starts:
                data = bhVerts[svs:svs+3]
                print('{0}\t{1}\t{2}'.format(float(data[0]),
                                             float(data[1]),
                                             float(data[2])))
            print('\n')
