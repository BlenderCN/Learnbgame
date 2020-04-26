import bpy


def unlink_obj(context, obj):
    for coll in context.scene.collection.children:
            for ob in bpy.data.collections[coll.name].objects:
                if obj == bpy.data.collections[coll.name].objects[ob.name]:
                    bpy.data.collections[coll.name].objects.unlink(obj)


def link_obj(context, obj, name="Cutters"):
    if name not in bpy.data.collections:
            context.scene.collection.children.link(bpy.data.collections.new(name=name))
    bpy.data.collections[name].objects.link(obj)
