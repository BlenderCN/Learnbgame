# this script convert setting to monochrome lineart for comics
import bpy
# set white materials whole objects, then set edge and freestyle line
def makeLineart(name="lineartWhite"):

    edge_threshold = 200
    line_thickness = 1.1

    s = bpy.context.scene
    percentage = s.render.resolution_percentage
    x = s.render.resolution_x * percentage / 100
    y = s.render.resolution_y * percentage / 100
    size = x if x >= y else y

    edge_threshold += int( size / 500) * 40
    line_thickness += int( size / 2000)

    # apply white material and edge
    for item in bpy.data.objects:
        if item.type == 'MESH':
            item.data.materials.append(bpy.data.materials[name])

    s.render.layers.active.freestyle_settings.crease_angle = 1.2

    bpy.context.scene.render.use_edge_enhance = True
    bpy.context.scene.render.edge_threshold = edge_threshold

    bpy.context.scene.render.use_freestyle = True
    bpy.data.linestyles["LineStyle"].panel = "THICKNESS"
    bpy.data.linestyles["LineStyle"].thickness = line_thickness
    bpy.data.linestyles["LineStyle"].thickness_position = 'RELATIVE'
    bpy.data.linestyles["LineStyle"].thickness_ratio = 0

    # background tranceparency
    bpy.context.scene.render.alpha_mode = 'TRANSPARENT'
    # bpy.context.scene.color_mode = 'RGBA'   # not work
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'
    return


# add lineart white material
def addLineartMaterial(name="lineartWhite"):
    mat = bpy.data.materials.new(name)
    mat.use_shadeless = True
    mat.diffuse_color = (float(1), float(1), float(1))
    return


# import lineart white material from blend file, if you'd like to use
def appendMaterial(name="lineartWhite"):

    desktop = os.path.expanduser("~/Desktop")
    whiteCubeMaterial = desktop + "/blend/material_test/whitecube.blend/Material/"

    # material append
    bpy.ops.wm.link_append(directory=whiteCubeMaterial, link=False, filename=name)
    return


# clear lamps and materials exist
def clearObjects():

    scn = bpy.context.scene
    for ob in scn.objects:
        if ob.type == 'LAMP':
        #    if ob.type == 'CAMERA' or ob.type == 'LAMP':
            scn.objects.unlink(ob)

    for item in bpy.data.objects:
        if item.type == 'MESH':
            while item.data.materials:
                item.data.materials.pop(0, update_data=True)
    return

# set nodes for image file
def outputFile():
    s = bpy.context.scene
    s.use_nodes = True

    r = s.render.layers.active
    n = s.node_tree.nodes
    l = s.node_tree.links
    

    render = n["Render Layers"]
    render.layer = 'RenderLayer'
    render.location = (0, 0)

    import os
    mergeout = n.new("CompositorNodeOutputFile")
    mergeout.name = "merge out"
    mergeout.location = (400, 100)
    mergeout.base_path = os.path.expanduser("~/Desktop/rendering/w")
    mergeout.file_slots.new("rendering")
    l.new(render.outputs[0], mergeout.inputs[-1])


# join objects to clear non-manified edges
def objectJoin():

    for ob in bpy.context.scene.objects:
        if ob.type == 'MESH':
            ob.select = True
            bpy.context.scene.objects.active = ob
        else:
            ob.select = False
    bpy.ops.object.join()

################### add on setting section###########################
bl_info = {
    "name": "Conver Comic Lineart",
    "category": "Learnbgame",
}

import bpy


class ComicLineart(bpy.types.Operator):
    """lineart converter"""
    bl_idname = "lineart.comic"
    bl_label = "comic lineart"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):    
        clearObjects()
        addLineartMaterial()
        makeLineart()
        #objectJoin()
        outputFile()
        return {'FINISHED'}


def register():
    bpy.utils.register_class(ComicLineart)


def unregister():
    bpy.utils.unregister_class(ComicLineart)


if __name__ == "__main__":
    register()
