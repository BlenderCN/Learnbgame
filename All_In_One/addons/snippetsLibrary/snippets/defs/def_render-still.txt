def render(folder, name):
    scn = bpy.context.scene
    #scn.render.stamp_note_text = name
    #openGl render
    scn.render.filepath = folder + name + '_viewport'
    bpy.ops.render.opengl(animation=False, write_still=True, view_context=False)#view_context False > look throughcam
    #normal render
    scn.render.filepath = folder + name + '_render'
    bpy.ops.render.render(animation=False, write_still=True)