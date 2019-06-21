import bpy

limits = """  LIMITS {
   { 0: -3.14159, 3.14159; }
   { 0: -3.14159, 3.14159; }
   { 0: -3.14159, 3.14159; }
  }
"""

defpos = """  DEFAULT_POSE {{
    {0},{1},{2},{3},	{4},{5},{6},{7},	{8},{9},{10},{11};
  }}
"""

def write_file(path, context):
    armature = context.active_object.data
    asf = open(path, 'w')
    asf.write('SE_SKELETON 1.01\n\n')
    asf.write('BONES {0}\n{{\n'.format(len(armature.bones)))
    
    for bone in armature.bones:
        asf.write('  NAME "{0}"\n'.format(bone.name))
        
        if bone.parent:
            m = bone.matrix
            p = bone.head
            
            asf.write('  PARENT "{0}"\n'.format(bone.parent.name))
            asf.write('  LENGTH {0}\n'.format(bone.length))
            asf.write(limits)
            asf.write(defpos.format(m[0][0], m[0][2], -m[0][1], p[0],    m[2][0], m[2][2], -m[2][1], p[2],    -m[1][0], -m[1][2], m[1][1], -(bone.parent.length + p[1]) ))
        else:
            m = bone.matrix
            p = bone.head
            
            asf.write('  PARENT ""\n')
            asf.write('  LENGTH {0}\n'.format(bone.length))
            asf.write(limits)
            asf.write(defpos.format(-m[0][0], -m[0][2], m[0][1], -p[0],    m[2][0], m[2][2], -m[2][1], p[2],    m[1][0], m[1][2], -m[1][1], p[1] ))
    
    asf.write('}')
    asf.close()
    return {'FINISHED'}