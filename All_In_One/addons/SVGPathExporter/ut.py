

def getMin(a, b):
    if a < b:
        return a
    else:
        return b

def getMax(a, b):
    if a > b:
        return a
    else:
        return b

class BBox:
    hasData = False
    b = [0, 0, 0]
    t = [0, 0, 0]
    def reset(self):
        self.hasData = False
        self.b = [0, 0, 0]
        self.t = [0, 0, 0]
    def expand(self, v):
        if not self.hasData:
            self.hasData = True
            for i in range(0, 3):
                self.b[i] = v[i]
                self.t[i] = v[i]
        else:
            for i in range(0, 3):
                self.b[i] = getMin(self.b[i], v[i])
                self.t[i] = getMax(self.t[i], v[i])
    def getW(self, idx):
        return self.t[idx] - self.b[idx]

class BBox2D:
    hasData = False
    b = [0, 0]
    t = [0, 0]
    def reset(self):
        self.hasData = False
        self.b = [0, 0]
        self.t = [0, 0]
    def expand(self, v):
        if not self.hasData:
            self.hasData = True
            for i in range(0, 2):
                self.b[i] = v[i]
                self.t[i] = v[i]
        else:
            for i in range(0, 2):
                self.b[i] = getMin(self.b[i], v[i])
                self.t[i] = getMax(self.t[i], v[i])
    def getW(self, idx):
        return self.t[idx] - self.b[idx]

