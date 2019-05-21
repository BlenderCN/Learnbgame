active_object = bpy.context.object
selected_objects = [o for o in bpy.context.selected_objects if o != active_object and o.type == active_object.type]