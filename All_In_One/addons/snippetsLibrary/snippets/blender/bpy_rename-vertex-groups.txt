for ob in bpy.context.selected_objects:
    for vg in ob.vertex_groups:
        if vg.name.endswith('_back'):
            vg.name= vg.name.replace('_back','_3-4back.L')