for ob in bpy.context.selected_objects:
    print(ob.name)

for b in bpy.context.selected_bones:
    print(b.name)

for eb in bpy.context.selected_editable_bones:
    print(eb.name)

for pb in bpy.context.selected_pose_bones:
    print(pb.name)