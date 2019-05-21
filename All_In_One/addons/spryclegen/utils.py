import bpy

def base_name(obj):
    return obj.name.split('.')[0]


def next_object(lst, current):
    ci = lst.index(current)
    ci += 1
    return lst[ci] if ci < len(lst) else lst[0]


def uvs(obj, uvs=None):
    if uvs:
        uvos = obj.data.uv_layers.active.data
        for uvo, uv in zip(uvos, uvs):
            uvo.uv = uv
    else:
        return [uvo.uv for uvo in obj.data.uv_layers.active.data]


def make_active(obj):
    scene = bpy.context.scene
    scene.objects.active.select = False
    scene.objects.active = obj
    obj.select = True
