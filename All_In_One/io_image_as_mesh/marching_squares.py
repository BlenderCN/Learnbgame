def create_polygon(data):
    p = getStartingPoint(data)
    return marchingSquares(data, p)

def getStartingPoint(data):
    for j, r in enumerate(data):
        for i, a in enumerate(r):
            if a > 0:
                return (i,j)

def getSquareValue(data, x, y):
    val = 0
    if data[y-1][x-1] > 0:
        val += 1
    if data[y-1][x] > 0:
        val += 2
    if data[y][x-1] > 0:
        val += 4
    if data[y][x] > 0:
        val += 8

    return val

def marchingSquares(data, startingPoint):
    ret = []

    px = startingPoint[0]
    py = startingPoint[1]

    stepX = 0
    stepY = 0
    prevX = 0
    prevY = 0

    closedLoop = False

    while not closedLoop:
        val = getSquareValue(data, px, py)

        if val == 1 or val == 5 or val == 13:
            stepX = 0
            stepY = -1
        elif val == 8 or val == 10 or val == 11:
            stepX = 0
            stepY = 1
        elif val == 4 or val == 12 or val == 14:
            stepX = -1
            stepY = 0
        elif val == 2 or val == 3 or val == 7:
            stepX = 1
            stepY = 0
        elif val == 6:
            if prevX == 0 and prevY == -1:
                stepX = -1
                stepY = 0
            else:
                stepX = 1
                stepY = 0
        elif val == 9:
            if prevX == 1 and prevY == 0:
                stepX = 0
                stepY = -1
            else:
                stepX = 0
                stepY = 1

        px += stepX
        py += stepY

        ret.append((px, py))

        prevX = stepX
        prevY = stepY

        if px == startingPoint[0] and py == startingPoint[1]:
            closedLoop=True;

    return ret
