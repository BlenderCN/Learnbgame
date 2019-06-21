# this script makes convert setting to monochrome lineart for comics

#Copyright (c) 2014 Toyofumi Fujiwara
#Released under the MIT license
#http://opensource.org/licenses/mit-license.php

import bpy
from comicLineartMisc import *


def comicLineartAOout():
    import os
    '''make line art and shadow render'''

    # regenerate scene AO

    if 'AO' in [s.name for s in bpy.data.scenes]:
        bpy.data.scenes.remove( bpy.data.scenes['AO'] )
    bpy.ops.scene.new(type="LINK_OBJECTS")
    aos = bpy.context.scene
    aos.name = "AO"

    if not 'AO' in bpy.data.worlds.keys():
        w = bpy.data.worlds.new("AO")
        w.light_settings.use_ambient_occlusion = True

        aos.world = bpy.data.worlds["AO"]

    bpy.data.screens['Default'].scene = bpy.data.scenes['Scene']
    bpy.context.screen.scene=bpy.data.scenes['Scene']

    s = bpy.context.scene
    n = s.node_tree.nodes
    l = s.node_tree.links
    if not "ao out" in n.keys():
        aoout = n.new("CompositorNodeOutputFile")
        aoout.name = "ao out"
        aoout.location = (400, -400)
        aoout.base_path = os.path.expanduser("~/Desktop/rendering/1")
        aoout.file_slots.new("rendering_ao")

        render = n["Render Layers"]
        render.scene = bpy.data.scenes["AO"]
        l.new(render.outputs[0], aoout.inputs[-1])
    # set output node if not exist
    return


################### add on setting section###########################
bl_info = {
    "name": "Convert Comic Lineart AO",
    "category": "Learnbgame",
}

import bpy


class ComicLineartAO(bpy.types.Operator):
    """lineart converter by Node"""
    bl_idname = "lineartaoout.comic"
    bl_label = "comic lineart AO out"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context): 
        bpy.context.scene.render.engine = 'BLENDER_RENDER'   
        comicLineartAOout()
        #objectJoin()
        return {'FINISHED'}


def register():
    bpy.utils.register_class(ComicLineartAO)


def unregister():
    bpy.utils.unregister_class(ComicLineartAO)


if __name__ == "__main__":
    register()
