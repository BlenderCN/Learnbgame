import bpy

def invoke_individual_resizing():
    space = bpy.context.scene.tool_settings #bpy.context.space_data
    old = space.transform_pivot_point
    space.transform_pivot_point = "INDIVIDUAL_ORIGINS"
    bpy.ops.transform.resize("INVOKE_DEFAULT")
    space.transform_pivot_point = old

def locate_sharps(ssharpangle,all_sharp):
    if all_sharp:
        bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_all(action='TOGGLE')
    bpy.ops.mesh.edges_select_sharp(ssharpangle)
    
