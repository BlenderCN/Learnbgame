from urllib import request
import bpy

from bpy.props import IntProperty, StringProperty, EnumProperty, BoolProperty

import numpy as np

import os
import tempfile
import re
import pprint


bpy.types.Scene.tilemapdownloader_zoomlevel      = IntProperty(name="ズームレベル", default=18)
bpy.types.Scene.tilemapdownloader_topleftX       = IntProperty(name="左上タイルX",  default=229732)
bpy.types.Scene.tilemapdownloader_topleftY       = IntProperty(name="左上タイルY",  default=104096)
bpy.types.Scene.tilemapdownloader_bottomrightX   = IntProperty(name="右下タイルX",  default=229740)
bpy.types.Scene.tilemapdownloader_bottomrightY   = IntProperty(name="右下タイルY",  default=104101)
bpy.types.Scene.tilemapdownloader_custom_url     = StringProperty(name="カスタムURL", default="", description="{z} がズームレベル、 {x} がX座標の値、 {y} がY座標の値に置き換えられます")
bpy.types.Scene.tilemapdownloader_use_custom_url = BoolProperty(name="カスタムURLを使用", default=False)
bpy.types.Scene.tilemapdownloader_url_preset     = EnumProperty(
        name="URLプリセット",
        items=[
            ("https://tile.openstreetmap.org/{z}/{x}/{y}.png",                     "OpenStreetMap Standard Tile Layer",       ""),
            ("https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png",           "地理院タイル 標準地図",                   ""),
            ("https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.jpg", "地理院タイル 全国最新写真（シームレス）", ""),
        ],
        default="https://tile.openstreetmap.org/{z}/{x}/{y}.png")


def main(report, urlfmt, zoomlevel, topleftX, topleftY, bottomrightX, bottomrightY):
    tiles = []

    num_tiles = (bottomrightX-topleftX+1)*(bottomrightY-topleftY+1)
    wm = bpy.context.window_manager
    wm.progress_begin(0, num_tiles)
    download_progress = 0
    wm.progress_update(download_progress)

    combined_x_px = (bottomrightX-topleftX+1)*256
    combined_y_px = (bottomrightY-topleftY+1)*256

    ext = os.path.splitext(urlfmt)[1]
    fd, tmpfname = tempfile.mkstemp(suffix=ext)

    # タイル座標は、
    # - 東方向がX正方向
    # - 南方向がY正方向
    # なので、左上からダウンロードするのが順当であるが、
    # 結合処理の都合で、左下から順にダウンロードしている
    #
    # ダウンロード順のイメージ:
    # 11 12 13 14 15
    #  6  7  8  9 10
    #  1  2  3  4  5
    #
    # タイル座標のイメージ(X,Y):
    # (0,0) (1,0) (2,0)
    # (0,1) (1,1) (2,1)
    # (0,2) (1,2) (2,2)
    for y in reversed(range(topleftY, bottomrightY+1)):
        for x in range(topleftX, bottomrightX+1):
            #print(zoomlevel, x, y)
            url = urlfmt.replace("{z}", str(zoomlevel)).replace("{x}", str(x)).replace("{y}", str(y))
            request.urlretrieve(url, tmpfname)
            img = bpy.data.images.load(tmpfname)
            tiletype = re.search("([^/]+)/\d+/\d+/\d+\.\w+$", url).group(1)
            img.name = "{}-{}-{}-{}".format(tiletype,zoomlevel,x,y)
            img.use_fake_user = True
            img.pack()
            img.filepath = ""
            tiles.append(img)
            print(img.name)
            download_progress += 1
            wm.progress_update(download_progress)

    os.close(fd)
    os.remove(tmpfname)
    wm.progress_end()

    #print(tiles)

    combined_img = bpy.data.images.new("Combined Image", combined_x_px, combined_y_px, alpha=True)
    combined_pxs = np.array(combined_img.pixels[:])
    combined_pxs.resize(combined_y_px, combined_x_px*4)

    combined_R = combined_pxs[::,0::4]
    combined_G = combined_pxs[::,1::4]
    combined_B = combined_pxs[::,2::4]
    combined_A = combined_pxs[::,3::4]

    wm.progress_begin(0, num_tiles)
    tile_idx = 0
    for yy in range(0,combined_y_px,256):
        for xx in range(0,combined_x_px,256):

            print(tile_idx, yy, xx, tiles[tile_idx])

            tile = tiles[tile_idx]
            tile_pxs = np.array(tile.pixels[:])
            tile_pxs.resize(256, 256*4)

            tile_R = tile_pxs[::,0::4]
            tile_G = tile_pxs[::,1::4]
            tile_B = tile_pxs[::,2::4]
            tile_A = tile_pxs[::,3::4]
            tile_idx += 1
            wm.progress_update(tile_idx)

            for y in range(256):
                for x in range(256):
                    combined_R[y+yy][x+xx] = tile_R[y][x]
                    combined_G[y+yy][x+xx] = tile_G[y][x]
                    combined_B[y+yy][x+xx] = tile_B[y][x]
                    combined_A[y+yy][x+xx] = tile_A[y][x]

    wm.progress_end()

    combined_pxs = combined_pxs.flatten()
    combined_img.pixels = combined_pxs
    combined_img.use_fake_user = True
    combined_img.pack(as_png=True)

    report({"INFO"}, "UV/画像エディターで {} を見てください".format(pprint.pformat(combined_img.name)))


class TileMapDownloader(bpy.types.Operator):
    bl_idname = "object.tilemapdownloader"
    bl_label = "Download and Stitching Tile Map"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        if not scene.tilemapdownloader_topleftX <= scene.tilemapdownloader_bottomrightX:
            return False
        if not scene.tilemapdownloader_topleftY <= scene.tilemapdownloader_bottomrightY:
            return False
        if scene.tilemapdownloader_use_custom_url and scene.tilemapdownloader_custom_url == "":
            return False
        return True

    def execute(self, context):
        scene = context.scene
        if scene.tilemapdownloader_use_custom_url:
            urlfmt = scene.tilemapdownloader_custom_url
        else:
            urlfmt = scene.tilemapdownloader_url_preset

        main(self.report,
                urlfmt,
                scene.tilemapdownloader_zoomlevel,
                scene.tilemapdownloader_topleftX, scene.tilemapdownloader_topleftY,
                scene.tilemapdownloader_bottomrightX, scene.tilemapdownloader_bottomrightY)
        return {"FINISHED"}


class TileMapDownloaderCustomMenu(bpy.types.Panel):
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "TOOLS"
    bl_label = "Tile Map Downloader"
    bl_category = "Tile Map"
    #bl_context = "mesh_edit"
    #bl_context = "objectmode"

    @classmethod
    def poll(cls, context):
        return True

    def draw_header(self, context):
        layout = self.layout

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene, "tilemapdownloader_use_custom_url")
        row = layout.row()
        row.prop(scene, "tilemapdownloader_custom_url")
        if not scene.tilemapdownloader_use_custom_url:
            row.enabled = False
        row = layout.row()
        row.prop(scene, "tilemapdownloader_url_preset")
        if scene.tilemapdownloader_use_custom_url:
            row.enabled = False
        layout.separator()
        layout.prop(scene, "tilemapdownloader_zoomlevel")
        layout.separator()
        layout.prop(scene, "tilemapdownloader_topleftX")
        layout.prop(scene, "tilemapdownloader_topleftY")
        layout.separator()
        layout.prop(scene, "tilemapdownloader_bottomrightX")
        layout.prop(scene, "tilemapdownloader_bottomrightY")
        layout.separator()

        topleftX = scene.tilemapdownloader_topleftX
        bottomrightX = scene.tilemapdownloader_bottomrightX
        topleftY = scene.tilemapdownloader_topleftY
        bottomrightY = scene.tilemapdownloader_bottomrightY
        num_tiles_x = bottomrightX-topleftX+1
        num_tiles_y = bottomrightY-topleftY+1
        if num_tiles_x > 0 and num_tiles_y > 0:
            layout.label(icon="INFO", text="{}x{}={} tiles".format(
                    num_tiles_x, num_tiles_y, num_tiles_x*num_tiles_y))
            layout.label(icon="INFO", text="{}x{} pixels".format(
                    num_tiles_x*256, num_tiles_y*256))
        else:
            layout.label(icon="INFO", text="0 tiles")
            layout.label(icon="INFO", text="0 pixels")

        layout.separator()
        layout.operator(TileMapDownloader.bl_idname, text=TileMapDownloader.bl_label)
