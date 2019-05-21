
import bpy
from . import xray_io


def parse_shaders():
    try:
        shadersPath = bpy.context.user_preferences.addons['io_scene_object'].preferences.engine_shaders
        file = open(shadersPath, 'rb')
        data = file.read()
        file.close()
        shaderList = []
        for chunkID, chunkData in xray_io.ChunkedReader(data):
            if chunkID == 0x3:
                pr = xray_io.PackedReader(chunkData)
                for _ in range(pr.getf('<I')[0]):
                    shaderList.append(pr.gets())
        shaderList.sort()
        return shaderList
    except:
        pass


def parse_shaders_xrlc():
    try:
        compilerPath = bpy.context.user_preferences.addons['io_scene_object'].preferences.compiler_shaders
        file = open(compilerPath, 'rb')
        data = file.read()
        file.close()
        compilerList = []
        if len(data) % (128 + 16) != 0:
            exit(1)
        pr = xray_io.PackedReader(data)
        for _ in range(len(data) // (128+16)):
            n = pr.gets()
            compilerList.append(n)
            pr.getf('{}s'.format(127 - len(n) + 16))  # skip
        compilerList.sort()
        return compilerList
    except:
        pass


def parse_game_materials():
    try:
        gameMaterialsPath = bpy.context.user_preferences.addons['io_scene_object'].preferences.game_materials
        file = open(gameMaterialsPath, 'rb')
        data = file.read()
        file.close()
        gameMaterialsList = []
        for cid, data in xray_io.ChunkedReader(data):
            if cid == 4098:
                for _, cdata in xray_io.ChunkedReader(data):
                    name = None
                    for (cccid, ccdata) in xray_io.ChunkedReader(cdata):
                        if cccid == 0x1000:
                            pr = xray_io.PackedReader(ccdata)
                            pr.getf('I')[0]
                            name = pr.gets()
                            gameMaterialsList.append(name)
        gameMaterialsList.sort()
        return gameMaterialsList
    except:
        pass
