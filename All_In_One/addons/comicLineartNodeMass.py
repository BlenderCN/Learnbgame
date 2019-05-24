# this script makes convert setting to monochrome lineart for comics
# use for Blender Render (no support cycles Render )

#Copyright (c) 2014 Shunnich Fujiwara
#Released under the MIT license
#http://opensource.org/licenses/mit-license.php

import bpy
from comicLineartNodeGroup import *
from comicLineartMisc import *

DEBUG = False
RENDER_VISIBLE = [2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0]


################### misc ###########################
def renderLayerSetVisible(r, suffix="", rendertype=RENDER_VISIBLE):
#    dic = {"_front":1, "_middle":2, "_back":3}
    dic = {"_" + str(i) :i for i in range(1,21) }
    rendertype =range(1,21)
    for i in range(20):
        if suffix == "" or rendertype[i] == 0:
            r.layers[i] = True
        elif rendertype[i] == dic[suffix]:
            r.layers[i] = True
        elif i >= 15:
            r.layers[i] = True
        else:
            r.layers[i] = False
    return

################### nodes parts ###########################

def comicLineartNode(g_line, num=0, suffix=""):
    '''make line art and shadow ,ao render'''
    s = bpy.context.scene

    BS_LOCATION_X = 0
    BS_LOCATION_Y = 0 + num * 1200

    def setFreestyle(name):
        # line style setting
        line_thickness = 1.1
        edge_threshold = 44

        percentage = s.render.resolution_percentage
        x = s.render.resolution_x * percentage / 100
        y = s.render.resolution_y * percentage / 100
        size = x if x >= y else y

        edge_threshold += int(size / 500) * 40
        line_thickness += int(size / 2000)

        s.render.image_settings.file_format = 'PNG'

        if "front" in suffix:
            line_ratio = 4.0
        elif "middle" in suffix:
            line_ratio = 2.5
        else:
            line_ratio = 1.5

        s.render.use_freestyle = True
        s.render.alpha_mode = 'TRANSPARENT'
        s.render.image_settings.color_mode = 'RGBA'
        s.cycles.film_transparent = True


        s.render.use_edge_enhance = True
        s.render.edge_threshold = edge_threshold

        #s.render.layers.active.freestyle_settings.crease_angle = 1.2
        style_name = "Freestyle"+suffix
        freestyle = s.render.layers[name].freestyle_settings
        freestyle.linesets["Freestyle"].linestyle.name = style_name

        freestyle.use_smoothness = True
        bpy.data.linestyles[style_name].panel = "THICKNESS"
        bpy.data.linestyles[style_name].thickness = line_thickness * line_ratio
        bpy.data.linestyles[style_name].thickness_position = 'RELATIVE'
        bpy.data.linestyles[style_name].thickness_ratio = 0
        #bpy.data.linestyles["Freestyle"].geometry_modifiers.new(name="bezier",type='BEZIER_CURVE')
        #bpy.data.linestyles["Freestyle"].thickness_modifiers.new(name="irinuki", type="ALONG_STROKE")

        # ON HOLD
        # creating curvemap object by python not supported,
        # then "irinuki" curve must create by UI or hard coding
        #bpy.data.linestyles['LineStyle'].thickness_modifiers["irinuki"].curves...

        return

    def createFreestyleRenderLayer(name="Freestyle"):
        # render layer setting
        #f = s.render.layers.active
        f = s.render.layers.new(name)
        f.name = name

        f.use_strand = False
        f.use_edge_enhance = False
        f.use_sky = False
        f.use_solid = False
        f.use_halo = False
        f.use_ztransp = False

        return f

    def createGrayRenderLayer(name="Gray"):
        r = s.render.layers.new(name)

        r.use_freestyle = False
        r.use_pass_ambient_occlusion = True
        return r

    f = createFreestyleRenderLayer(name="Freestyle"+suffix)
    f.freestyle_settings.linesets.new('Freestyle')
    setFreestyle(name="Freestyle"+suffix)

    renderLayerSetVisible(f, suffix)
    r = createGrayRenderLayer(name="Gray"+suffix)
    renderLayerSetVisible(r, suffix)

    # nodes
    s.use_nodes = True

    n = s.node_tree.nodes
    l = s.node_tree.links
    g = bpy.data.node_groups

    composite = n["Composite"]
    composite.location = (600, -600 + BS_LOCATION_Y)
    composite.use_alpha = True

    #render = n["Render Layers"]
    render = n.new("CompositorNodeRLayers")
    render.layer = 'Gray' + suffix
    render.location = (0, 0 + BS_LOCATION_Y)

    #s.render.layers["RenderLayer"].use_pass_object_index = True

    freestyleRender = n.new("CompositorNodeRLayers")
    freestyleRender.layer = 'Freestyle'+suffix
    freestyleRender.location = (0, -400 + BS_LOCATION_Y)

    #render_ao = n.new(type="CompositorNodeRLayers")
    #render_ao.location = (0, -800 + BS_LOCATION_Y)

    #render_ao.scene = bpy.data.scenes["AO"]
    #render_ao.layer = 'Gray'+suffix

    def getObjectPassIndex():
        o = bpy.data.objects
        index = [i.pass_index for i in o]
        unique = lambda x: list(set(x))
        index = unique(index)
        index.remove(0)     # ignore 0 as default value
        return index

    def makeNodeObIDMask(passIndex, count):
        import os
        objectid_mask = n.new(type='CompositorNodeIDMask')
        setMix_obj = n.new("CompositorNodeMixRGB")
        objectid_mask.index = passIndex
        objectid_mask.use_antialiasing = True

        objectid_mask.location = (800, -1000 + count*(-200))
        setMix_obj.location = (1000, -1000 + count*(-200))
        setMix_obj.inputs[2].default_value = (0.8, 0.8, 0.8, 1)
        l.new(render.outputs["IndexOB"], objectid_mask.inputs[0])
        l.new(objectid_mask.outputs[0], setMix_obj.inputs[0])

        objectMaskOut = n.new("CompositorNodeOutputFile")
        objectMaskOut.name = "ob mask out"
        objectMaskOut.location = (1200, -1000 + count*(-200))
        objectMaskOut.base_path = os.path.expanduser("~/Desktop/rendering/1")
        objectMaskOut.file_slots.new("rendering_OBmask" + str(passIndex) + "_")

        l.new(setMix_obj.outputs[0], objectMaskOut.inputs[-1])
        return

    #objectPassIndexList = getObjectPassIndex()
    #for i, v in enumerate(objectPassIndexList):
    #    makeNodeObIDMask(v, i)

    line_group = n.new("CompositorNodeGroup")
    line_group.location = (300, 0 + BS_LOCATION_Y)
    line_group.node_tree = g_line
    '''
    # output to image files
    import os
    lineout = n.new("CompositorNodeOutputFile")
    lineout.name = "line out"
    lineout.location = (600, 0 + BS_LOCATION_Y)
    lineout.base_path = os.path.expanduser("~/Desktop/rendering/1")
    lineout.file_slots.new("rendering_lineart"+suffix)

    grayout = n.new("CompositorNodeOutputFile")
    grayout.name = "gray out"
    grayout.location = (600, -200 + BS_LOCATION_Y)
    grayout.base_path = os.path.expanduser("~/Desktop/rendering/1")
    grayout.file_slots.new("rendering_shadow"+suffix)

    renderout = n.new("CompositorNodeOutputFile")
    renderout.name = "render out"
    renderout.location = (600, -400 + BS_LOCATION_Y)
    renderout.base_path = os.path.expanduser("~/Desktop/rendering/1")
    renderout.file_slots.new("rendering_render"+suffix)



    l.new(line_group.outputs[0], lineout.inputs[-1])
    l.new(line_group.outputs[3], grayout.inputs[-1])
    #l.new(line_group.outputs[2], aoout.inputs[-1])
    l.new(render.outputs[0], renderout.inputs[-1])
    '''
    l.new(render.outputs[0], line_group.inputs[0])
    l.new(render.outputs["Alpha"], line_group.inputs[1])
    l.new(freestyleRender.outputs[0], line_group.inputs[2])
    l.new(freestyleRender.outputs["Alpha"], line_group.inputs[3])

    #l.new(render_ao.outputs["AO"], line_group.inputs[4])
    #l.new(render_ao.outputs["Alpha"], line_group.inputs[5])

    if suffix=="_1":
        viewer = n.new("CompositorNodeViewer")
        viewer.location = (600, 200)
        l.new(line_group.outputs[1], composite.inputs[0])
        l.new(line_group.outputs[1], viewer.inputs[0])
    bpy.context.screen.scene = s
    return line_group

def baseLayerNode(num=0, name="BaseLayer", suffix=""):
    "base render node group by using pass index"

    s = bpy.context.scene

    def createBaseLayer(name="BaseLayer"):
        s = bpy.context.scene
        r = s.render.layers.new(name)
        r.use_pass_material_index = True
        return r

    BS_LOCATION_X = 0 + 3000
    BS_LOCATION_Y = -600 +num*320

    # nodes
    s.use_nodes = True
    m = bpy.data.materials
    n = s.node_tree.nodes
    l = s.node_tree.links
    g = bpy.data.node_groups

    # make base node tree
    g_base = createBaseGroup()

    # render layer
    r = createBaseLayer(name)
    renderLayerSetVisible(r, suffix)
    c = n.new(type="CompositorNodeRLayers")
    c.location = (BS_LOCATION_X, BS_LOCATION_Y + 2000)
    c.name = name
    c.layer = name

    base_group = n.new("CompositorNodeGroup")
    base_group.location = (BS_LOCATION_X + 300, BS_LOCATION_Y+2000)
    base_group.node_tree = g_base

    l.new(c.outputs["IndexMA"], base_group.inputs[0])
    l.new(c.outputs["Alpha"], base_group.inputs[1])
    '''
    import os
    baseout = n.new("CompositorNodeOutputFile")
    baseout.name = "base out"
    baseout.location = (600, BS_LOCATION_Y + 2000)
    baseout.base_path = os.path.expanduser("~/Desktop/rendering/1")
    baseout.file_slots.new("rendering_base"+suffix)

    l.new(base_group.outputs[1], baseout.inputs[-1])
    '''
    return base_group

################### main compositor nodes ###########################

def baseLayerNodeMass():
    bpy.context.scene.render.alpha_mode = 'TRANSPARENT'

    BS_LOCATION_X = 1000 + 3000
    BS_LOCATION_Y = -600

    # nodes
    s = bpy.context.scene

    s.use_nodes = True
    m = bpy.data.materials
    n = s.node_tree.nodes
    l = s.node_tree.links
    g = bpy.data.node_groups

    bsn = [None for i in range(0,16)]
    for i in range(1,16):
        #rdr[i] = comicLineartNode(g_line, num=i, suffix="_"+str(i))
        bsn[i] = baseLayerNode(num=i, name="BaseLayer_"+str(i), suffix="_" + str(i))


    y = 0
    before = None
    alpha = n.new("CompositorNodeAlphaOver")
    alpha.location = (300 + BS_LOCATION_X, y + BS_LOCATION_Y+ 300)
    l.new(alpha.inputs[1], bsn[2].outputs[1])
    l.new(bsn[1].outputs[1], alpha.inputs[2])

    for i in range(3,16):
        alpha2 = n.new("CompositorNodeAlphaOver")
        alpha2.location = (BS_LOCATION_X + 600, y + BS_LOCATION_Y + 300 * (i-1))
        l.new(bsn[i].outputs[1], alpha2.inputs[1])
        l.new(alpha2.inputs[2], alpha.outputs[0])
        alpha = alpha2

    import os
    baseout = n.new("CompositorNodeOutputFile")
    baseout.name = "base out"
    baseout.location = (1200 + BS_LOCATION_X, BS_LOCATION_Y + 1000)
    baseout.base_path = os.path.expanduser("~/Desktop/rendering/1")
    baseout.file_slots.new("rendering_base")

    l.new(alpha2.outputs[0], baseout.inputs[-1])

    return


def comicLineartNodeMass():
    g_line = createLineartGroup()
    rdr = [None for i in range(0,16)]
    for i in range(1,16):
        rdr[i] = comicLineartNode(g_line, num=i, suffix="_"+str(i))

    BS_LOCATION_X = 1000
    BS_LOCATION_Y = -600 + 2000

    # nodes
    s = bpy.context.scene

    s.use_nodes = True
    m = bpy.data.materials
    n = s.node_tree.nodes
    l = s.node_tree.links
    g = bpy.data.node_groups

    g_alphaline = createAlphaOverLineartGroup()
    #base_group = n.new("CompositorNodeGroup")
    #base_group.node_tree = g_alphaline

    y = 0
    before = None
    alpha = n.new("CompositorNodeGroup")
    alpha.node_tree = g_alphaline
    alpha.location = (300 + BS_LOCATION_X, y + BS_LOCATION_Y+ 300)
    l.new(rdr[2].outputs[3], alpha.inputs[2])
    l.new(rdr[1].outputs[3], alpha.inputs[3])
    l.new(rdr[1].outputs[4], alpha.inputs[0])
    l.new(rdr[2].outputs[4], alpha.inputs[1])

    l.new(rdr[2].outputs[5], alpha.inputs[4])
    l.new(rdr[1].outputs[5], alpha.inputs[5])

    for i in range(3,16):
        alpha2 = n.new("CompositorNodeGroup")
        alpha2.node_tree = g_alphaline
        alpha2.location = (BS_LOCATION_X + 300, y + BS_LOCATION_Y + 300 * (i-1))
        l.new(alpha.outputs[1], alpha2.inputs[3])
        l.new(rdr[i].outputs[4], alpha2.inputs[1])
        l.new(rdr[i].outputs[3], alpha2.inputs[2])
        l.new(alpha.outputs[0], alpha2.inputs[0])

        l.new(alpha.outputs[2], alpha2.inputs["render2"])
        l.new(rdr[i].outputs[5], alpha2.inputs["render"])
        alpha = alpha2



    # output to image files
    import os
    lineout = n.new("CompositorNodeOutputFile")
    lineout.name = "line out"
    lineout.location = (900 + BS_LOCATION_X, BS_LOCATION_Y + 700)
    lineout.base_path = os.path.expanduser("~/Desktop/rendering/1")
    lineout.file_slots.new("rendering_lineart")
    l.new(alpha2.outputs[0], lineout.inputs[-1])

    grayout = n.new("CompositorNodeOutputFile")
    grayout.name = "base out"
    grayout.location = (900 + BS_LOCATION_X, BS_LOCATION_Y + 1000)
    grayout.base_path = os.path.expanduser("~/Desktop/rendering/1")
    grayout.file_slots.new("rendering_shadow")
    l.new(alpha2.outputs[1], grayout.inputs[-1])

    renderout = n.new("CompositorNodeOutputFile")
    renderout.name = "render out"
    renderout.location = (900 + BS_LOCATION_X, BS_LOCATION_Y + 1300)
    renderout.base_path = os.path.expanduser("~/Desktop/rendering/1")
    renderout.file_slots.new("rendering_render")
    l.new(alpha2.outputs[2], renderout.inputs[-1])
    return

################### add on setting section###########################
bl_info = {
    "name": "Convert Comic Lineart　Node Mass",
    "category": "Learnbgame",
}

import bpy


class ComicLineartNodeMass(bpy.types.Operator):
    """lineart converter for mass scene"""
    bl_idname = "lineartmass.comic"
    bl_label = "comic lineart node mass"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.context.scene.render.engine = 'BLENDER_RENDER'
        removeRenderingFolder()
        useBackDrop()
        baseLayerNode()
        comicLineartNodeMass()
        baseLayerNodeMass()
        #objectJoin()
        return {'FINISHED'}


def register():
    bpy.utils.register_class(ComicLineartNodeMass)


def unregister():
    bpy.utils.unregister_class(ComicLineartNodeMass)


if __name__ == "__main__":
    register()
