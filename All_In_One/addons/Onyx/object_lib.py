import bpy

#//////////////////////////////// - DEFINITIONS - ///////////////////////////
def FocusObject(target):

    # If the target isnt visible, MAKE IT FUCKING VISIBLE.
    if target.hide is True:
        target.hide = False

    if target.hide_select is True:
        target.hide_select = False

    #### Select and make target active
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = bpy.data.objects[target.name]
    bpy.ops.object.select_pattern(pattern=target.name)


def SelectObject(target):

    # If the target isnt visible, MAKE IT FUCKING VISIBLE.
    if target.hide is True:
        target.hide = False

    if target.hide_select is True:
        target.hide_select = False

    target.select = True

def ActivateObject(target):

    # If the target isnt visible, MAKE IT FUCKING VISIBLE.
    if target.hide is True:
        target.hide = False

    if target.hide_select is True:
        target.hide_select = False

    bpy.context.scene.objects.active = bpy.data.objects[target.name]

def RecordSelectedState(context):

    # Create an array to store all found objects
    sel = []
    modes = []

    # Store the active object
    active = context.active_object
    sel.append(context.active_object)
    active_mode = ''
    active_mode = context.active_object.mode
    bpy.ops.object.mode_set(mode='OBJECT')
    modes.append(active_mode)

    # Find all the selected objects in the scene and store them
    for item in context.selected_objects:
        if item.name != active.name:
            print(item.name)
            sel.append(item)
            sel_mode = ''
            sel_mode = item.mode
            modes.append(sel_mode)

            bpy.context.scene.objects.active = bpy.data.objects[item.name]
            print("OBJECT MODE =", item.mode)
            bpy.ops.object.mode_set(mode='OBJECT')
            print("NEW OBJECT MODE =", item.mode)

    record = {'objects': sel, 'modes': modes}

    return record

def RestoreSelectedState(record):
    sel = record['objects']
    modes = record['modes']

    bpy.ops.object.select_all(action='DESELECT')

    i = 1
    while i != len(sel):
        print(sel[i].name)
        bpy.context.scene.objects.active = bpy.data.objects[sel[i].name]
        sel[i].select = True

        bpy.ops.object.mode_set(mode=modes[0])
        i += 1

    bpy.context.scene.objects.active = bpy.data.objects[sel[0].name]
    bpy.ops.object.mode_set(mode=modes[0])
    ActivateObject(sel[0])
    sel[0].select = True
