import bpy
import os
import subprocess
import sys
args = sys.argv

identifier = args[1]

#pageutilsからblenderに実行させるレンダリング用スクリプト
#レンダリング

selfname = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
dir = os.path.dirname(bpy.data.filepath)

#renderpath = dir + os.sep + "pageutils" + os.sep + "img" + os.sep + selfname + ".png"
# renderdir = dir + os.sep + "render" + os.sep 
# renderedgepath = renderdir + selfname + "_%s_edge.png"%identifier

bpy.context.scene.render.use_simplify = False

#線画レンダー
bpy.context.scene.use_nodes = False
bpy.context.scene.render.layers["RenderLayer"].use_edge_enhance = True
bpy.context.scene.render.use_textures = True
bpy.context.scene.render.use_antialiasing = False
bpy.context.scene.render.alpha_mode = 'TRANSPARENT'
bpy.context.scene.render.layers["RenderLayer"].use_solid = False
bpy.context.scene.render.layers["RenderLayer"].use_ztransp = False
bpy.context.scene.render.layers["RenderLayer"].use_freestyle = False
bpy.context.scene.render.use_freestyle = False
bpy.context.scene.render.use_edge_enhance = True
bpy.context.scene.render.edge_threshold = 255
# レンダパスは指定されているという前提！
# bpy.context.scene.render.filepath = renderedgepath
bpy.ops.render.render(write_still=True)
