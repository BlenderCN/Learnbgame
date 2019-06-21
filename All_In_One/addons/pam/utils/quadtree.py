"""Quadtrees for caching uv-maps"""

# Dict with cached uv-maps
quadtrees = {}

class Quadtree_node:
    """Represents a node in the quadtree in which Polygons can be inserted.
    A Polygon is a tuple of two lists of the same size. The first list contains the
    uv-coordinates and the second the 3d-coordinates. Only the uv-coordinates are used
    for sorting into the quadtree, the rest is just for storage."""
    def __init__(self, left, top, right, bottom):
        """Left, top, right, bottom are the boundaries of this quad"""
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.children = [None, None, None, None]
        self.polygons = []

    def addPolygon(self, polygon):
        """Inserts a polygon into the quadtree."""
        if self.children[0]:
            if self.children[0].addPolygon(polygon):
                return True
            if self.children[1].addPolygon(polygon):
                return True
            if self.children[2].addPolygon(polygon):
                return True
            if self.children[3].addPolygon(polygon):
                return True
        for p in polygon[0]:
            if p[0] < self.left or p[0] > self.right or p[1] < self.top or p[1] > self.bottom:
                return False
        self.polygons.append(polygon)
        return True

    def getPolygons(self, point):
        """Gives a list of all polygons in the quadtree that may contain the point"""
        node = self
        while True:
            for polygon in node.polygons:
                yield polygon
            if not node.children[0]:
                break
            if point[0] < node.children[0].right:
                c = 0
            else:
                c = 1
            if point[1] > node.children[0].bottom:
                c += 2
            node = node.children[c]
        

def buildQuadtree(depth = 2, left = 0.0, top = 0.0, right = 1.0, bottom = 1.0):
    """Builds a new quadtree recursively with the given depth."""
    node = Quadtree_node(left, top, right, bottom)
    if depth > 0:
        v = (top + bottom) / 2
        h = (left + right) / 2
        node.children[0] = buildQuadtree(depth - 1, left, top, h, v)
        node.children[1] = buildQuadtree(depth - 1, h, top, right, v)
        node.children[2] = buildQuadtree(depth - 1, left, v, h, bottom)
        node.children[3] = buildQuadtree(depth - 1, h, v, right, bottom)
    return node

def buildUVQuadtreeFromObject(obj, depth = 2):
    left  = 0.0
    right = 1.0
    top = 0.0
    bot = 1.0

    polygons = []
    for p in obj.data.polygons:
        uvs = ([obj.data.uv_layers.active.data[li].uv for li in p.loop_indices], [obj.data.vertices[p.vertices[i]].co for i in range(len(p.loop_indices))])
        polygons.append(uvs)
        for uv in uvs[0]:
            left = min(left, uv[0])
            right = max(right, uv[0])
            top = min(top, uv[1])
            bot = max(bot, uv[1])
    qtree = buildQuadtree(depth, left = left, right = right, top = top, bottom = bot)
    for polygon in polygons:
        qtree.addPolygon(polygon)
    return qtree