import bpy
import os
import subprocess

#pageutilsからblenderに実行させるレンダリング用スクリプト
#レンダリング

selfname = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
dir = os.path.dirname(bpy.data.filepath)

#renderpath = dir + os.sep + "pageutils" + os.sep + "img" + os.sep + selfname + ".png"
renderdir = dir + os.sep + "render" + os.sep 
renderallpath = renderdir + selfname + "_layerAll_nochange.png"
renderedgepath = renderdir + selfname + "_layerAll_edge.png"

bpy.context.scene.render.use_simplify = False

bpy.context.scene.render.layers["RenderLayer"].use_solid = True
bpy.context.scene.render.layers["RenderLayer"].use_edge_enhance = False
bpy.context.scene.render.layers["RenderLayer"].use_ztransp = True
bpy.context.scene.render.use_raytrace = True
bpy.context.scene.render.use_textures = True
bpy.context.scene.render.use_antialiasing = False

bpy.context.scene.render.filepath = renderallpath
bpy.ops.render.render(write_still=True)
#終わったら画像を開く
#subprocess.Popen("EXPLORER " + renderallpath)


#線画レンダー
bpy.context.scene.use_nodes = False
bpy.context.scene.render.layers["RenderLayer"].use_edge_enhance = True
bpy.context.scene.render.use_textures = True
bpy.context.scene.render.use_antialiasing = False
bpy.context.scene.render.layers["RenderLayer"].use_solid = False
bpy.context.scene.render.layers["RenderLayer"].use_ztransp = False
bpy.context.scene.render.layers["RenderLayer"].use_freestyle = False
bpy.context.scene.render.use_freestyle = False
bpy.context.scene.render.use_edge_enhance = True
bpy.context.scene.render.edge_threshold = 255
bpy.context.scene.render.filepath = renderedgepath
bpy.ops.render.render(write_still=True)
