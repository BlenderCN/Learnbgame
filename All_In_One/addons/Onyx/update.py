import bpy
from .object_lib import ActivateObject, FocusObject, SelectObject, RecordSelectedState, RestoreSelectedState

#//////////////////////////////// - UPDATES - ///////////////////////////
def Update_ObjectOrigin(self, context):

    if context.scene.OXScn.update_toggle is False:
        print("Updating origins..")
        context.scene.OXScn.update_toggle = True
        originType = context.active_object.OXObj.origin_point
        SetMeshOrigin(int(originType), "")
        context.scene.OXScn.update_toggle = False

    return None

def Update_ObjectVGOrigin(self, context):

    # Get the origin point and call the respective def
    context.scene.OXScn.update_toggle = True
    originType = context.active_object.OXObj.origin_point
    SetMeshOrigin(int(originType), "")
    context.scene.OXScn.update_toggle = False

    return None

def SetMeshOrigin(newInt, targetName):
    print("Setting Mesh Origin")

    # Base
    if newInt == 1:
        bpy.ops.origin.mesh_base(target=targetName)
    # Lowest
    if newInt == 2:
        bpy.ops.origin.mesh_lowest(target=targetName)
    # COM
    if newInt == 3:
        bpy.ops.origin.mesh_centerofmass(target=targetName)
    # Vertex Group
    if newInt == 4:
        bpy.ops.origin.mesh_vgroup(target=targetName)
    # Cursor
    if newInt == 5:
        bpy.ops.origin.mesh_cursor(target=targetName)
