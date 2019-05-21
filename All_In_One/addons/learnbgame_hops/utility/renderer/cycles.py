

def hide_preview(context, obj):
    obj.cycles_visibility.camera = False
    obj.cycles_visibility.diffuse = False
    obj.cycles_visibility.glossy = False
    obj.cycles_visibility.shadow = False
    obj.cycles_visibility.scatter = False
    obj.cycles_visibility.transmission = False
