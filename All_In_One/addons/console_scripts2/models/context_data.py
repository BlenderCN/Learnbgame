# --------------   --------------
# |context data| = |area & space|
# --------------   --------------
class ContextData:
    def __init__(self, area=None, space=None):
        """ Create a new area-space collection """
        if (area == None):
            self.space = bpy.types.Space()
        else:
            self.space = space
        if (area == None):
            self.area = bpy.types.Area()
        else:
            self.area = area

