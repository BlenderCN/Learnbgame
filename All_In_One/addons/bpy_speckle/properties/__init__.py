import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, CollectionProperty, EnumProperty

def register_speckle_object(self, context):
    if self is None:
        return
    names = [i.name for i in context.scene.speckle.objects]
    #if (self.enabled and context.object.name not in names):
    if (self.enabled and self.name not in names):
        prop = context.scene.speckle.objects.add()
        prop.name = self.name
    elif (self.name in names):
        index = list(context.scene.speckle.objects.keys()).index(self.name)
        context.scene.speckle.objects.remove(index)
    print ([i.name for i in context.scene.speckle.objects])

