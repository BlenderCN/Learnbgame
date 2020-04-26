import bpy

def writeData(context, filepath, use_some_setting):
    print("Running writeData")
    f = open(filepath, 'wb')
    #f.write("Hello World %s" % use_some_setting)
    for v in bpy.context.active_object[0].data.vertices:
        f.write(struct.pack('@f', v.co[0]))
        f.write(struct.pack('@f', v.co[1]))
        f.write(struct.pack('@f', v.co[2]))
    
    f.close()
    
    return {'FINISHED'}
