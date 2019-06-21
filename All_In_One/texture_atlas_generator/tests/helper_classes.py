class Vector(object):
    def __init__(self, tpl):
        self.x = tpl[0]
        self.y = tpl[1]
    def __add__(v1, v2):
        return Vector((v1.x + v2.x, v1.y + v2.y))
    def __mul__(v1, s):
        return Vector((v1.x * s, v1.y * s))
