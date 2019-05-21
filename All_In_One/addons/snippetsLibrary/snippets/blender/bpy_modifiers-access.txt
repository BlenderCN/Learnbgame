for ob in bpy.context.selected_objects:
    if ob.type in ('MESH', 'CURVE', 'TEXT') and len(ob.modifiers) > 0:
        print (ob.name)
        for mod in ob.modifiers:
            #mod.show_viewport = True
            #mod.show_render = True
            '''
            if mod.type == 'SUBSURF':
                mod.levels #view subdivision level
                mod.render_levels #render subdivision level

            if mod.type == 'ARMATURE':
                if mod.object:
                    print (mod.object.name)#print armatrue target
                #ob.modifiers.remove(mod) #remove modifier

            if mod.type == 'SOLIDIFY':
                mod.thickness
                mod.offset
            '''