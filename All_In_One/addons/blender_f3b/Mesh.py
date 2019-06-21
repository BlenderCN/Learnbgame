
class Vertex ():
    def __init__(self):
        self.p = None
        self.n = None
        self.c = None
        self.tg = None
        self.tx = None
        self.i = None
        self.from_vertex = None
        self.from_loop = None
        self.loop_index=0

    def __hash__(self):
        return hash(
            (
                tuple(self.p) if self.p else 0,
                tuple(self.n) if self.n else 0,
                tuple(self.c) if self.c else 0,
                tuple(tuple(p) for p in self.tg) if self.tg else 0,
                tuple(tuple(p) for p in self.tx) if self.tx else 0,
                self.i
            )
        )


class Skin ():
    def __init__(self):
        self.boneCount = []
        self.boneIndex = []
        self.boneWeight = []
        
    

class Mesh ():
    def __init__(self):
        self.verts = []
        self.indexes = []
        self.skin = Skin()
        self.has_skin = False
        
    