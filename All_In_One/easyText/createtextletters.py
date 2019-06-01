import bpy
from bpy.props import *

atr = bpy.types.Scene

atr.dim = FloatProperty(name="dim", default=0.0, description="y-dim of object")
atr.emptyname = StringProperty(name="Emptyname", default="Empty", description="Name of parent")


def create(content, space, ft, extrude, offset, depth, resolution, mesh, edgesplit, uv):
    make(content, space, ft, extrude, offset, depth, resolution, mesh, edgesplit, uv)
    return {'FINISHED'}


def make(content, space, ft, extrude, offset, depth, resolution, mesh, edge, uv):
    s = bpy.context.scene

    bpy.context.window.cursor_set("WAIT")
    bpy.context.space_data.cursor_location[0] = 0
    bpy.context.space_data.cursor_location[1] = 0
    bpy.context.space_data.cursor_location[2] = 0

    bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=(0, 0, 0))
    bpy.context.object.name = content
    s.emptyname = bpy.context.object.name
    em = bpy.data.objects[s.emptyname]

    for i in range(len(content)):
        bpy.ops.object.text_add()
        edit(False)
        bpy.ops.font.delete(type='ALL')
        bpy.ops.font.text_insert(text=content[i])
        edit(False)
        bpy.context.object.data.align_x = 'CENTER'
        bpy.context.object.data.font = bpy.data.fonts[ft]  # font
        if i == 0:
            s.dim = bpy.context.object.dimensions[1]
        bpy.context.object.location[0] = (-1 * space) * (len(content) / 2 - i) + (space / 2)  # x position
        bpy.context.object.rotation_euler[0] = 1.5708  # rotation
        bpy.context.object.location[2] = (s.dim / 2) * -1  # z position
        bpy.context.space_data.cursor_location[0] = bpy.context.object.location[0]  # set cursor to x-letter, 0,0
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        if i < 10:
            bpy.context.object.name = "00" + str(i)
        elif i < 100:
            bpy.context.object.name = "0" + str(i)
        else:
            bpy.context.object.name = str(i)

        # center
        bpy.context.object.data.extrude = extrude  # extrude
        bpy.context.object.data.offset = offset  # offset
        bpy.context.object.data.bevel_depth = s.depth  # bevel depth
        bpy.context.object.data.bevel_resolution = s.resolution  # bevel resolution

        if mesh == True:
            bpy.ops.object.convert(target='MESH')
            edit(True)
            bpy.ops.mesh.remove_doubles()
            edit(False)
            if edge == True:
                bpy.ops.object.modifier_add(type='EDGE_SPLIT')
                bpy.ops.object.modifier_apply(apply_as='DATA', modifier="EdgeSplit")
            if uv == True:
                edit(True)
                bpy.ops.uv.cube_project()
                edit(False)

        em.select = True
        bpy.context.scene.objects.active = em
        bpy.ops.object.parent_set()

    bpy.ops.view3d.snap_cursor_to_center()
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.window.cursor_set("DEFAULT")
    return {'FINISHED'}


def edit(selectallverts):
    bpy.ops.object.editmode_toggle()
    if selectallverts == True:
        bpy.ops.mesh.select_all(action='SELECT')
    return {'FINISHED'}


if __name__ == "__main__":
    ob = makeMesh(1)
    print(ob, "created")
