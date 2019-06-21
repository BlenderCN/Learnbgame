# this script convert setting to monochrome lineart for comics
#
#Copyright (c) 2014 Toyofumi Fujiwara
#Released under the MIT license
#http://opensource.org/licenses/mit-license.php

import bpy

# lineart , no lineart gray , merged  images
def comicLineartNode(destinationFolder,name):
     
    s = bpy.context.scene

    line_thickness = 1.1
    edge_threshold = 44

    percentage = s.render.resolution_percentage
    x = s.render.resolution_x * percentage / 100
    y = s.render.resolution_y * percentage / 100
    size = x if x >= y else y

    edge_threshold += int( size / 500) * 40
    line_thickness += int( size / 2000)

    s.render.image_settings.file_format = 'PNG'

    s.render.use_freestyle = True
    s.render.alpha_mode = 'TRANSPARENT'
    s.render.image_settings.color_mode = 'RGBA'

    s.render.use_edge_enhance = True
    s.render.edge_threshold = edge_threshold

    #s.render.layers.active.freestyle_settings.crease_angle = 1.2


    # render layer setting
    f = s.render.layers.active
    f.name ="Freestyle"
    r= s.render.layers.new( "RenderLayer")

    r.use_freestyle = False

    f.use_strand = False
    f.use_edge_enhance = False
    f.use_sky = False
    f.use_solid = False
    f.use_halo = False
    f.use_ztransp = False


    bpy.data.linestyles["LineStyle"].panel = "THICKNESS"
    bpy.data.linestyles["LineStyle"].thickness = line_thickness
    bpy.data.linestyles["LineStyle"].thickness_position = 'RELATIVE'
    bpy.data.linestyles["LineStyle"].thickness_ratio = 0


    # nodes
    s.use_nodes = True
        

    n = s.node_tree.nodes
    l = s.node_tree.links
    g = bpy.data.node_groups

    composite = n["Composite"]
    composite.location = (1200, 100)

    composite.use_alpha = True

    freestyleRender = n.new("CompositorNodeRLayers")
    freestyleRender.layer = 'Freestyle'
    freestyleRender.location=(0,500)

    l.new(freestyleRender.outputs["Image"],composite.inputs["Image"])

    saveLineImage(destinationFolder)


    render = n["Render Layers"]
    render.layer = 'RenderLayer'
    render.location = (0, 0)

    alpha = n.new("CompositorNodeAlphaOver")
    rgb2Bw = n.new("CompositorNodeRGBToBW")
    val2Rgb = n.new("CompositorNodeValToRGB")
    setAlpha = n.new("CompositorNodeSetAlpha")
    dilate = n.new("CompositorNodeDilateErode")
    viewer = n.new("CompositorNodeViewer")

    rgb2Bw.location = (200, 100)
    val2Rgb.location = (400, 100)
    alpha.location = (900,300)
    setAlpha.location = (700, 500)
    dilate.location = (400, 400)
    viewer.location = (1300, 350)

    rgb = n.new("CompositorNodeRGB")
    alphaMerge = n.new("CompositorNodeAlphaOver")
    setAlphaMerge = n.new("CompositorNodeSetAlpha")

    rgb.location = (400, -200)
    alphaMerge.location = (900, -200)
    setAlphaMerge.location= (700, -200)

    l.new(render.outputs[0], rgb2Bw.inputs[0])
    l.new(rgb2Bw.outputs[0], val2Rgb.inputs[0])
    l.new(val2Rgb.outputs[0], setAlpha.inputs[0])
    l.new(render.outputs['Alpha'], dilate.inputs[0])
    l.new(dilate.outputs[0], setAlpha.inputs[1])
    l.new(setAlpha.outputs[0],alpha.inputs[1])
    l.new(alpha.outputs[0], viewer.inputs[0])

    l.new(freestyleRender.outputs[0], alpha.inputs[2])
    l.new(alpha.outputs[0], composite.inputs[0])

    l.new(rgb.outputs[0],setAlphaMerge.inputs[0])
    l.new(dilate.outputs[0], setAlphaMerge.inputs[1])
    l.new(setAlphaMerge.outputs[0], alphaMerge.inputs[1])
    l.new(freestyleRender.outputs[0], alphaMerge.inputs[2])
    # gray setting
    val2Rgb.color_ramp.interpolation = 'CONSTANT'
    #val2Rgb.color_ramp.color_mode="HSV"
    #val2Rgb.color_ramp.hue_interpolation = 'near'

    dilate.distance = -1

    val2Rgb.color_ramp.elements[1].color = (1, 1, 1, 1)
    val2Rgb.color_ramp.elements[0].color = (0.279524, 0.279524, 0.279524, 1)
    val2Rgb.color_ramp.elements[1].position=0.08
    val2Rgb.color_ramp.elements[1].position=0.0

    rgb.outputs[0].default_value = (1,1,1,1)

    # output to image files
    # l : line art only, g : gray only, m : line art and white alpha maerged
    import os
    lineout = n.new("CompositorNodeOutputFile")
    lineout.name = "line out"
    lineout.location = (200, 600)
    path = destinationFolder
    lineout.base_path = path
    lineout.file_slots.new("_lineout")

    grayout = n.new("CompositorNodeOutputFile")
    grayout.name = "gray out"
    grayout.location = (1200, 600)
    path = destinationFolder
    grayout.base_path = path
    grayout.file_slots.new("_grayout")

    mergeout = n.new("CompositorNodeOutputFile")
    mergeout.name = "merge out"
    mergeout.location = (1200, -100)
    path = destinationFolder
    mergeout.base_path = path
    mergeout.file_slots.new("_mergeout")

    l.new(freestyleRender.outputs[0], lineout.inputs[-1])
    l.new(setAlpha.outputs[0], grayout.inputs[-1])
    l.new(alphaMerge.outputs[0], mergeout.inputs[-1])

    return


def saveLineImage(desitinationFolder):
    import os
    #path = os.path.expanduser("~/Desktop/rendering/")
    path = desitinationFolder + "/"
    bpy.data.scenes['Scene'].render.filepath = path + "_line.jpg"
    bpy.ops.render.render( write_still=True ) 
    return


# create Nodes for comic like 
def materialNodes(m,isWhite=True):
    m.use_nodes = True
    n = m.node_tree.nodes
    l = m.node_tree.links

    # create nodes
    material = n.new("ShaderNodeExtendedMaterial")
    output = n.new("ShaderNodeOutput")
    mix = n.new("ShaderNodeMixRGB")
    color=n.new("ShaderNodeRGB")

    # set location
    material.location = (0,-100)
    output.location = (600,-200)
    mix.location = (400,100)
    color.location = (0,500)


    if not isWhite:
        color.outputs[0].default_value = (0, 0, 0, 1)
    else:
        color.outputs[0].default_value = (1, 1, 1, 1)
  
    l.new(color.outputs["Color"], mix.inputs[0])
    l.new(material.outputs["Alpha"], mix.inputs[1])
    l.new(mix.outputs["Color"],output.inputs[0])

    return




# make Images
def makeComicMaterials(num):
    mats = bpy.data.materials
    t=""
    for i,v in enumerate(mats):
        if i == num:
            materialNodes(v,isWhite=False)
        else:
            materialNodes(v)
        t = t + str(i)
    return t

def saveImageFilesEachMaterials(destinationFolder,name):
    s = bpy.context.scene

    s.render.image_settings.file_format = 'PNG'

    s.render.alpha_mode = 'TRANSPARENT'
    s.render.image_settings.color_mode = 'RGBA'

    import os
    path = destinationFolder + "/"
    mats = bpy.data.materials
    for i,v in enumerate(mats):
        t =makeComicMaterials(i)
        #path = os.path.expanduser("~/Desktop/rendering/")
        bpy.data.scenes['Scene'].render.filepath = path + v.name + "_image" + str(i) + t +".png"
        bpy.ops.render.render( write_still=True ) 
        allClearNodes()

# clear Nodes and clear all Nodes
def clearNodes(m):
    m.use_nodes = True
    n = m.node_tree.nodes
    for i in n:
        n.remove(i)
    m.use_nodes = False

def allClearNodes():
    mats = bpy.data.materials
    for mb in mats:    
        clearNodes(mb)
    return

def clearCompositorNodes():
    s = bpy.context.scene
    nodes = s.node_tre.nodes
    for i in nodes:
        i.remove(i)
    s.use_nodes = False

def createFolderIncremental(destinationFolder, name):
    import os
    destinationFolder = destinationFolder + name

    if not os.path.exists(destinationFolder):
        os.makedirs(destinationFolder)
        return destinationFolder

    destinationFolder = destinationFolder + "%s"
    i=1
    while os.path.exists(destinationFolder % i):
        i+=1
    destinationFolder = destinationFolder.replace("%s", str(i))
    os.makedirs(destinationFolder)
    return destinationFolder


# main
def makeComicResource():
    import os

    # destination folder name for rendered image files
    name = "test"
    destinationFolder = os.path.expanduser("~/Desktop/rendering/") 
    destinationFolder = createFolderIncremental(destinationFolder,name) + "/"

    saveImageFilesEachMaterials(destinationFolder, name)
    comicLineartNode(destinationFolder, name)


################### add on setting section###########################
bl_info = {
    "name": "Make Comic Resource",
    "category": "Learnbgame",
    "version"    : (0, 0, 1),
    "blender"    : (2, 72, 0),
    "location"   : "Node Editor >> Tools",
    "description": "Make comic resources for clip studio paint."
}

class ComicResourcePanel(bpy.types.Panel):
    bl_idname = "comic_resources_node_panel"
    bl_label = "Comic Resources"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Generic'
    bl_options = {'DEFAULT_CLOSED'}
   
    file_name= bpy.props.StringProperty(default="aa")

    @classmethod
    def poll(cls, context):
        return bool(context.space_data.node_tree)
        
    def draw(self, context):
        layout = self.layout
        row = layout.column()
        row.label(text="custom text")
        row.prop(self, "text", text="name")
        row.prop(self, "text", text="folder")

        row.operator("comic.resource",
                        text="Comic resources").use_clipboard = True

 

class ComicResource(bpy.types.Operator):
    """Comic Resource"""
    bl_idname = "comic.resource"
    bl_label = "comic resource"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):    
        makeComicResource()
        return {'FINISHED'}


def register():
    bpy.utils.register_class(ComicResource)
    bpy.utils.register_class(ComicResourcePanel)


def unregister():
    bpy.utils.unregister_class(ComicResource)
    bpy.utils.unregister_class(ComicResourcePanel)

if __name__ == "__main__":
    register()

