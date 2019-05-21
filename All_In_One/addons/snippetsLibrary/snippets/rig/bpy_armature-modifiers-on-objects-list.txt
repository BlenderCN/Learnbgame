def CreateArmatureModifier(ob, targetRig):
    '''
    targetRig may be an armature object or name of armature data

    Create armature modifier if necessary and place it on top of stack
    or just after the first miror modifier
    return a list of bypassed objects
    '''

    #get object from armature data with a loop (only way to get armature's owner)
    if type(targetRig) == type('str'):
        for obArm in bpy.data.objects:
            if obArm.type == 'ARMATURE':
                if obArm.data.name == targetRig or obArm.name == targetRig:
                    ArmatureObject = obArm
    else:
        ArmatureObject = bpy.data.objects['oscar-hoo-transfo-casque-moto_rig']

    #add armature modifier that points to designated rig:
    if not 'ARMATURE' in [m.type for m in ob.modifiers]:
        mod = ob.modifiers.new('Armature', 'ARMATURE')
        mod.object = ArmatureObject#bpy.data.objects[targetRig]

        #bring Armature modifier to the top of the stack
        pos = 1
        if 'MIRROR' in [m.type for m in ob.modifiers]:
            #if mirror, determine it's position
            for mod in ob.modifiers:
                if mod.type == 'MIRROR':
                    pos += 1
                    break
                else:
                    pos += 1

        if len(ob.modifiers) > 1:
            for i in range(len(ob.modifiers) - pos):
                bpy.ops.object.modifier_move_up(modifier="Armature")

    else: #armature already exist
        for m in ob.modifiers:
            if m.type == 'ARMATURE':
                m.object = ArmatureObject#bpy.data.objects[targetRig]


### iterate to create armature modifier
for ob in bpy.context.selected_objects:
    if ob.type in ('MESH', 'CURVE', 'TEXT'):
        CreateArmatureModifier(ob, 'TARGETOBJECT(ARMATURE NAME OR OBJECT)' )