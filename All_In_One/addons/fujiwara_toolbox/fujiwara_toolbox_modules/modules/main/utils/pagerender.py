import bpy
import os
#pageutilsからblenderに実行させるレンダリング用スクリプト
#レンダリング

selfname = os.path.splitext(os.path.basename(bpy.data.filepath))[0]
dir = os.path.dirname(bpy.data.filepath)
renderpath = dir + os.sep + "pageutils" + os.sep + "img" + os.sep + selfname + ".png"

bpy.context.scene.render.use_simplify = True
#特にレベル変更はしない？
bpy.context.scene.render.simplify_subdivision = 2
bpy.context.scene.render.simplify_subdivision_render = 2
bpy.context.scene.render.resolution_percentage = 20

#高過ぎる奴対策：レンダ解像度をプレビュー解像度にあわせる！
for obj in bpy.data.objects:
    if obj.type == "MESH":
        bpy.context.scene.objects.active = obj
        for mod in obj.modifiers:
            if mod.type == "SUBSURF":
                mod.render_levels = mod.levels

bpy.context.scene.render.layers["RenderLayer"].use_solid = True
bpy.context.scene.render.layers["RenderLayer"].use_edge_enhance = False
bpy.context.scene.render.layers["RenderLayer"].use_ztransp = True
bpy.context.scene.render.use_raytrace = True
bpy.context.scene.render.use_textures = True
bpy.context.scene.render.use_antialiasing = False
bpy.context.scene.render.use_freestyle = False

bpy.context.scene.render.threads_mode = 'FIXED'
bpy.context.scene.render.threads = 1

bpy.data.scenes["Scene"].render.filepath = renderpath
bpy.ops.render.render(write_still=True)
