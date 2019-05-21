import bmesh
import os
import os.path
import platform
import random
import re
import subprocess
import sys
import traceback
# import pyximport
# pyximport.install()
import time

import math

from BSP_DATA import *


def getpath() -> str:
    """

    Returns:
        str: path to current file
    """
    return os.path.dirname(os.path.abspath(__file__))


import progressBar

import io
from contextlib import redirect_stdout

stdout = io.StringIO()
sys.path.append(getpath())
sys.path.append('E:\\PYTHON\\BSP_reader')

import BSP_DATA

BLANK = {'textureVecs': [{'x': 0.0, 'y': 0.0, 'z': 2.857142925262451, 'offset': -63.4286003112793},
                         {'x': 0.0, 'y': -2.857142925262451, 'z': 0.0, 'offset': 98.89399719238281}],
         'lightmapVecs': [{'x': 0.0, 'y': 0.0, 'z': 0.0625, 'offset': -1.3875006437301636},
                          {'x': 0.0, 'y': -0.0625, 'z': 0.0, 'offset': 2.16330623626709}], 'flags': 2048, 'texdata': 3}
BLANK_texInfo = BSP_DATA.texinfo_t()
for k, v in BLANK.items():

    if k == 'textureVecs' or k == 'lightmapVecs':
        vt = v
        v = []
        for i in range(2):
            vv = vt[i]
            vs = BSP_DATA.textureVec()
            vs.x = vv['x']
            vs.y = vv['y']
            vs.z = vv['z']
            vs.offset = vv['offset']
            v.append(vs)
    setattr(BLANK_texInfo, k, v)


def getpath() -> str:
    """

    Returns:
        str: path to current file
    """
    return os.path.dirname(os.path.abspath(__file__))


sys.path.append(getpath())
sys.path.append('E:\\PYTHON\\BSP_reader')

import importlib

from typing import Tuple, Dict, List

if 'BSP_reader' in sys.modules:
    import BSP_reader

    importlib.reload(BSP_reader)
else:
    import BSP_reader

    importlib.reload(BSP_reader)
from mathutils import Vector, Matrix, Euler
import bpy

if BSP_reader in sys.modules:
    importlib.reload(BSP_reader)


def is_os_64bit():
    return platform.machine().endswith('64')


vtflib = 'VTF64' if is_os_64bit() else 'VTF32'


class mesh:
    def __init__(self, filepath: str, doTexture, workdir='',staticProps = False):
        self.workdir = workdir
        self.armature_object = None
        fileNameWithOutExt = ".".join(filepath.split('.')[:-1]).replace('.dx90', '')

        # print(fileNameWithOutExt)

        self.BSP = BSP_reader.BSPreader(fileNameWithOutExt + '.bsp', workdir)
        self.CreateMesh(fileNameWithOutExt.split(os.sep)[-1])
        # if doTexture:
        #     try:
        #         self.processTextures()
        #     except:
        #         print('TEXTURE IMPORT ERROR')
        if staticProps:
            self.loadStaticProps()
        self.addLights()
        self.BSP.finish()

    def getMeshMaterial(self, mat_name, model_ob):
        if '/' in mat_name:
            mat_name = mat_name.split('/')[-1]

        if mat_name:
            mat_name = mat_name
        else:
            mat_name = "Material"
        mat_ind = 0
        md = model_ob.data
        mat = None
        for candidate in bpy.data.materials:  # Do we have this material already?
            if candidate.name == mat_name:
                mat = candidate
        if mat:
            if md.materials.get(mat.name):  # Look for it on this mesh
                for i in range(len(md.materials)):
                    if md.materials[i].name == mat.name:
                        mat_ind = i
                        break
            else:  # material exists, but not on this mesh
                md.materials.append(mat)
                mat_ind = len(md.materials) - 1
        else:  # material does not exist
            # print("- New material: {}".format(mat_name))
            mat = bpy.data.materials.new(mat_name)
            md.materials.append(mat)
            # Give it a random colour
            randCol = []
            for i in range(3):
                randCol.append(random.uniform(.4, 1))
            mat.diffuse_color = randCol

            mat_ind = len(md.materials) - 1

        return mat, mat_ind

    def process_models(self, base_name, models):
        self.vets = [(vert.x, vert.y, vert.z) for vert in self.BSP.BSP.LUMPS[3]]
        self.norms = [(normal.x, normal.y, normal.z) for normal in
                      [self.BSP.BSP.LUMPS[30][normal_ind] for normal_ind in self.BSP.BSP.LUMPS[31].indexes]]
        for i, model in enumerate(models):
            types = {}  # type:Dict[List]
            displacement_faces  = []
            faces = []
            normals = []
            mats = []
            uvs = [None for _ in self.BSP.BSP.LUMPS[3]]
            mat_ind = []
            for face in self.BSP.BSP.LUMPS[7][model.firstface:model.firstface + model.numfaces]:
                layer = 2
                # face = self.BSP.BSP.LUMPS[27][face.origFace]
                texInfo = self.BSP.BSP.LUMPS[6][face.texinfo]
                if (texInfo.flags & BSP_DATA.SURF_TRIGGER) > 0:
                    type_ = 'TRIGGER'
                    if type_ not in types:
                        types[type_] = [face]
                    else:
                        types[type_].append(face)

                elif (texInfo.flags & BSP_DATA.SURF_NODRAW) > 0:
                    type_ = 'NODRAW'
                    if type_ not in types:
                        types[type_] = [face]
                    else:
                        types[type_].append(face)

                elif (texInfo.flags & BSP_DATA.SURF_SKIP) > 0:
                    type_ = 'SKIP'
                    if type_ not in types:
                        types[type_] = [face]
                    else:
                        types[type_].append(face)

                elif (texInfo.flags & BSP_DATA.SURF_SKY2D) > 0:
                    type_ = 'SKY2D'
                    if type_ not in types:
                        types[type_] = [face]
                    else:
                        types[type_].append(face)

                elif (texInfo.flags & BSP_DATA.SURF_SKY) > 0:
                    type_ = 'SKY'
                    if type_ not in types:
                        types[type_] = [face]
                    else:
                        types[type_].append(face)

                elif (texInfo.flags & BSP_DATA.SURF_HITBOX) > 0:
                    type_ = 'HITBOX'
                    if type_ not in types:
                        types[type_] = [face]
                    else:
                        types[type_].append(face)

                elif (texInfo.flags & BSP_DATA.SURF_NOCHOP) > 0:
                    type_ = 'NOCHOP'
                    if type_ not in types:
                        types[type_] = [face]
                    else:
                        types[type_].append(face)

                elif (texInfo.flags & BSP_DATA.SURF_NODECALS) > 0:
                    type_ = 'NODECALS'
                    if type_ not in types:
                        types[type_] = [face]
                    else:
                        types[type_].append(face)

                elif (texInfo.flags & BSP_DATA.SURF_NOLIGHT) > 0:
                    type_ = 'NOLIGHT'
                    if type_ not in types:
                        types[type_] = [face]
                    else:
                        types[type_].append(face)

                elif (texInfo.flags & BSP_DATA.SURF_SKIP) > 0:
                    type_ = 'SKIP'
                    if type_ not in types:
                        types[type_] = [face]
                    else:
                        types[type_].append(face)

                elif (texInfo.flags & BSP_DATA.SURF_HINT) > 0:
                    type_ = 'HINT'
                    if type_ not in types:
                        types[type_] = [face]
                    else:
                        types[type_].append(face)

                elif (texInfo.flags & BSP_DATA.SURF_TRANS) > 0:
                    type_ = 'TRANS'
                    if type_ not in types:
                        types[type_] = [face]
                    else:
                        types[type_].append(face)

                elif face.dispinfo!=-1:
                    displacement_faces.append(face)
                    type_ = 'DISP'
                    if type_ not in types:
                        types[type_] = [face]
                    else:
                        types[type_].append(face)
                else:
                    type_ = 'MESH'
                    if type_ not in types:
                        types[type_] = [face]
                    else:
                        types[type_].append(face)

            self.generate_model(base_name, i, types, model)
            self.process_displacement(base_name,displacement_faces,model)

    def process_displacement(self, base_name, faces,model):
        for face in faces:  # type: dface_t
            dispinfo = self.BSP.BSP.LUMPS[LUMP_ENUM.LUMP_DISPINFO][face.dispinfo]  # type: ddispinfo_t
            name = '{}_{}_{}'.format(base_name, 'DISP', face.dispinfo)

            model_mesh = bpy.data.objects.new(name, bpy.data.meshes.new(name))
            for i in range(20):
                model_mesh.layers[i] = (i == 7)
            model_mesh.location = (model.origin.x, model.origin.y, model.origin.z)
            model_mesh.parent = self.armature_object
            bpy.context.scene.objects.link(model_mesh)
            md = model_mesh.data
            firstedge = face.firstedge
            numedges = face.numedges
            texInfo = self.BSP.BSP.LUMPS[6][face.texinfo]
            texdata = self.BSP.BSP.LUMPS[2][texInfo.texdata]
            mat_name = self.BSP.BSP.LUMPS[43][texdata.nameStringTableID]
            faceindexes = []
            uvs = []
            edge_indexs = [self.BSP.BSP.LUMPS[13][firstedge + ind].surfedge for ind in range(numedges)]
            for edge_index in edge_indexs:
                edges = self.BSP.BSP.LUMPS[12][abs(edge_index)].v
                if edge_index < 0:
                    if edges[1] not in faceindexes:
                        faceindexes.append(edges[1])
                    if edges[0] not in faceindexes:
                        faceindexes.append(edges[0])
                else:
                    if edges[0] not in faceindexes:
                        faceindexes.append(edges[0])
                    if edges[1] not in faceindexes:
                        faceindexes.append(edges[1])

                for v in edges:
                    x, y, z = self.vets[v]
                    tv = texInfo.textureVecs
                    u = tv[0].x * x + tv[0].y * y + tv[0].z * z + tv[0].offset
                    v = tv[1].x * x + tv[1].y * y + tv[1].z * z + tv[1].offset
                    uvs.append((u, v))
            md.from_pydata(self.vets, [], [faceindexes])
            md.update()
            bpy.context.scene.objects.active = model_mesh
            with redirect_stdout(stdout):
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.delete_loose()
                bpy.ops.mesh.remove_doubles()
                bpy.ops.mesh.delete_loose()
                bpy.ops.mesh.remove_doubles()
                bpy.ops.object.mode_set(mode='OBJECT')

            mat, mat_ind_ = self.getMeshMaterial(mat_name, model_mesh)
            md.uv_textures.new()
            uv_data = md.uv_layers[0].data
            # for i in range(len(uv_data)):
            #     if uvs[md.loops[i].vertex_index] is None:
            #         continue
            #     uv_data[i].uv = uvs[md.loops[i].vertex_index]
            model_mesh.data.polygons[0].material_index = mat_ind_
            bpy.context.scene.objects.active = model_mesh
            bpy.ops.object.modifier_add(type='SUBSURF')
            bpy.context.object.modifiers["Subsurf"].levels = dispinfo.power
            bpy.context.object.modifiers["Subsurf"].subdivision_type = 'SIMPLE'
            bpy.ops.object.modifier_add(type='DISPLACE')
            bpy.context.object.modifiers["Displace"].direction = 'RGB_TO_XYZ'
            heightTex = bpy.data.textures.new(name, type='IMAGE')
            heightTex.use_clamp = False

            bpy.context.object.modifiers["Displace"].texture_coords = 'UV'
            bpy.context.object.modifiers["Displace"].texture = heightTex
            # bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subsurf")
            verts = self.BSP.BSP.LUMPS[LUMP_ENUM.LUMP_DISP_VERTS][dispinfo.DispVertStart:dispinfo.DispVertStart+dispinfo.VertexCount]
            row_size = round(sqrt(dispinfo.VertexCount))
            print(len(verts),row_size)
            image = bpy.data.images.new(name, width=row_size, height=row_size)
            image.colorspace_settings.name = 'Non-Colour Data'
            image.use_generated_float = True

            heightTex.image = image
            pixels = []
            for n,vert in enumerate(verts):
                color = color32()
                color.r = vert.m_vVector.x*vert.m_flDist
                color.g = vert.m_vVector.y*vert.m_flDist
                color.b = vert.m_vVector.z*vert.m_flDist
                # color.a = vert.m_flAlpha
                print(color.toArrayRGBA)
                # color.normalize()
                print(color.toArrayRGBA)
                print('\n')
                # color.r = color.r +1
                # color.g = color.g +1
                # color.b = color.b +1
                color.a = 1
                pixels.extend(color.toArrayRGBA)
            image.pixels = pixels

            # for vert,dvert in zip(md.vertices,verts): #type: Tuple[object,CDispVert]
            #     coos = vert.co
            #     newcoos = dvert.m_vVector
            #     vert.co = (coos.x + (newcoos.x*dvert.m_flDist),coos.y + (newcoos.y*dvert.m_flDist),coos.z + (newcoos.z*dvert.m_flDist))
            # bpy.ops.object.mode_set(mode='OBJECT')
    def generate_model(self, base_name, i, types, model):
        print('Importing map geometry:', base_name)
        for type_, faces_ in types.items():
            faces = []
            mat_ind = []
            mats = []
            uvs = [None for _ in self.BSP.BSP.LUMPS[3]]
            field = progressBar.Progress_bar('Generating {} mesh'.format('{}_{}'.format(base_name, type_)), len(faces_),20)
            for face in faces_:

                faceindexes = []
                firstedge = face.firstedge
                numedges = face.numedges
                texInfo = self.BSP.BSP.LUMPS[6][face.texinfo]
                texdata = self.BSP.BSP.LUMPS[2][texInfo.texdata]
                mat_name = self.BSP.BSP.LUMPS[43][texdata.nameStringTableID]
                mat_ind.append((texInfo.texdata, mat_name))

                edge_indexs = [self.BSP.BSP.LUMPS[13][firstedge + ind].surfedge for ind in range(numedges)]
                for edge_index in edge_indexs:
                    edges = self.BSP.BSP.LUMPS[12][abs(edge_index)].v
                    if edge_index < 0:
                        if edges[1] not in faceindexes:
                            faceindexes.append(edges[1])
                        if edges[0] not in faceindexes:
                            faceindexes.append(edges[0])
                    else:
                        if edges[0] not in faceindexes:
                            faceindexes.append(edges[0])
                        if edges[1] not in faceindexes:
                            faceindexes.append(edges[1])

                    for v in edges:
                        x, y, z = self.vets[v]
                        tv = texInfo.textureVecs
                        u = tv[0].x * x + tv[0].y * y + tv[0].z * z + tv[0].offset
                        v = tv[1].x * x + tv[1].y * y + tv[1].z * z + tv[1].offset
                        uvs.append((u, v))
                faces.append(tuple(faceindexes))
                field.increment(1)
                field.draw()
            name = '{}_{}_{}'.format(base_name, type_, i)

            model_mesh = bpy.data.objects.new(name, bpy.data.meshes.new(name))
            model_mesh.location = (model.origin.x, model.origin.y, model.origin.z)
            model_mesh.parent = self.armature_object
            bpy.context.scene.objects.link(model_mesh)
            md = model_mesh.data
            md.from_pydata(self.vets, [], faces)
            md.update()

            # try:
            #     print('NORMS', len(vert_n), len(md.loops))
            #     md.create_normals_split()
            #     md.use_auto_smooth = True
            #     md.normals_split_custom_set_from_vertices(vert_n)
            # except Exception as E:
            #     print(E)
            #     print('FAILED TO SET CUSTOM NORMALS')
            try:
                vert_n = list([(-self.BSP.BSP.LUMPS[30][vert_n].x, -self.BSP.BSP.LUMPS[30][vert_n].y,
                                -self.BSP.BSP.LUMPS[30][vert_n].z) for vert_n in self.BSP.BSP.LUMPS[31].indexes])
                md.create_normals_split()
                md.use_auto_smooth = True
                md.normals_split_custom_set_from_vertices(vert_n)

            except Exception as Ex:
                print(Ex)

            for _, mat_name in mat_ind:

                if mat_name.startswith('maps/'):
                    mat_name = mat_name.split('/')[-1]
                    mat_name = '_'.join(mat_name.split('_')[:-3])

                mat, mat_ind_ = self.getMeshMaterial(mat_name, model_mesh)
                mats.append(mat_ind_)
            md.uv_textures.new()
            uv_data = md.uv_layers[0].data
            for i in range(len(uv_data)):
                if uvs[md.loops[i].vertex_index] is None:
                    continue
                uv_data[i].uv = uvs[md.loops[i].vertex_index]
            for poly, mat_index in zip(model_mesh.data.polygons, mats):
                poly.material_index = mat_index
            bpy.ops.object.select_all(action="DESELECT")
            model_mesh.select = True
            bpy.context.scene.objects.active = model_mesh
            with redirect_stdout(stdout):
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.delete_loose()
                bpy.ops.mesh.remove_doubles()
                bpy.context.scene.objects.active.data.validate()
                bpy.ops.mesh.normals_make_consistent(inside=False)
                bpy.ops.mesh.delete_loose()
                bpy.ops.mesh.remove_doubles(threshold=0.0002)
                bpy.context.scene.objects.active.data.validate()
                bpy.ops.mesh.remove_doubles(threshold=0.0001)
                bpy.ops.mesh.normals_make_consistent(inside=False)
                bpy.ops.object.mode_set(mode='OBJECT')

                bpy.ops.object.shade_smooth()
            model_mesh.data.use_auto_smooth = True
            if type_ == 'TRIGGER':
                model_mesh.layers[1] = True
                for i in range(20):
                    model_mesh.layers[i] = (i == 1)
            if type_ == 'MESH':
                model_mesh.layers[0] = True
                for i in range(20):
                    model_mesh.layers[i] = (i == 0)
            if type_ in ['SKY', 'SKY2D']:
                model_mesh.layers[4] = True
                for i in range(20):
                    model_mesh.layers[i] = (i == 4)

    def CreateMesh(self, name):
        # faces = []
        # normals = []
        # mats = []
        # uvs = [None for _ in self.BSP.BSP.LUMPS[3]]
        # vets = [(vert.x, vert.y, vert.z) for vert in self.BSP.BSP.LUMPS[3]]
        # mat_ind = []
        # print(self.BSP.BSP.LUMPS[14])
        print('GENERATING MODEL:', name)
        if len(self.BSP.BSP.LUMPS[14]) != 0:
            self.process_models(name, self.BSP.BSP.LUMPS[14])

    def processTextures(self):
        materials = {}
        textures = []
        material_folder = os.path.join(self.workdir, 'materials')
        print('WORK DIR ', material_folder)
        model_textures_folders = [os.path.join(material_folder, path) for path in
                                  self.MDL.theMdlFileData.theTexturePaths if
                                  path != '']
        print('model_textures_folders', model_textures_folders)
        for texture in self.MDL.theMdlFileData.theTextures:  # type: GLOBALS.SourceMdlTexture
            for n, path_ in enumerate(model_textures_folders):
                file = [a for a in os.listdir(path_) if (texture.thePathFileName + '.vmt').lower() == a.lower()][0]
                materials[texture.thePathFileName] = open(os.path.join(path_, file), 'r')
        for matName, mat in materials.items():
            print('PARSING MATERIAL {}'.format(matName))
            type_ = mat.readline()
            if 'EyeRefract' in type_:
                texturePath = re.findall('\"?\$Iris\"?\s+\"([\w\d/\\\]+)\"?\s?', mat.read(), flags=re.IGNORECASE)[0]
                textures.append(os.path.join(material_folder, texturePath))
            elif 'vertexlitgeneric' in type_:
                texturePath = \
                    re.findall('\"?\$basetexture\"?\s+\"([\w\d/\\\]+)\"?\s?', mat.read(), flags=re.IGNORECASE)[0]
                textures.append(os.path.join(material_folder, texturePath))
        print('TEXTURE PATHS ', textures)
        os.system(os.path.join(getpath(), vtflib))
        for texture in textures:
            subprocess.run([os.path.join(getpath(), vtflib, 'VTFCmd.exe'), '-file', texture + '.vtf', '-output',
                            os.sep.join(texture.split(os.sep)[:-1])])
            image = bpy.data.images.load(texture + '.tga', check_existing=True)
            image.pack()
            os.remove(texture + '.tga')

    def loadStaticProps(self):
        try:
            from io_mesh_SourceMDL import MDL_import
        except Exception as Ex:
            print(Ex)
            print('No io_MDL_import addon found')
            return
        for gamelump in self.BSP.BSP.LUMPS[BSP_DATA.LUMP_ENUM.LUMP_GAME_LUMP].gamelump:  # type: dgamelump_t
            objs_len = len(gamelump.PropData)
            for n, PropData in enumerate(gamelump.PropData):  # type: StaticPropLump_t
                name = gamelump.PropDict.name[PropData.PropType].split(r'/')[-1]
                print('LOADING {} MODEL {}\\{}'.format(name, n, objs_len))
                model = self.BSP.getStaticPropsFile(gamelump.PropDict.name[PropData.PropType])
                if model == 'ERROR':
                    continue

                Orig = PropData.Origin
                Ang = PropData.Angles
                print(model)
                MDL_import.mesh(files = model, doTexture = False, coords=(Orig.x, Orig.y, Orig.z),
                                rot=(math.radians(Ang.x), math.radians(Ang.z), math.radians(Ang.y)))

                time.sleep(0.2)


    def addLights(self):
        layers = [False]*20
        layers[5] = True
        for light in self.BSP.BSP.LUMPS[BSP_DATA.LUMP_ENUM.LUMP_WORLDLIGHTS]: #type: dworldlight_t
            lamp_type = 'POINT'
            if emittype_t(light.type) == emittype_t.emit_point:
                lamp_type = 'POINT'
            elif emittype_t(light.type) == emittype_t.emit_spotlight:
                lamp_type = 'SPOT'
            bpy.ops.object.lamp_add(type=lamp_type, radius=1.0, view_align=False, location=(light.origin.x,light.origin.y,light.origin.z), rotation=(360*light.normal.x,360*light.normal.y,360*light.normal.z),)
            lamp = bpy.context.object
            lamp.layers = layers
            lamp_data = lamp.data
            light = light.intensity
            lamp_nodes = lamp_data.node_tree.nodes['Emission']
            lamp_nodes.inputs['Strength'].default_value = light.magnitude()*10
            lamp_nodes.inputs['Color'].default_value = light.normalize().toArrayRGBA
if __name__ == "__main__":
    # a = mesh(':\\SteamLibrary\\SteamApps\\common\\SourceFilmmaker\\game\\usermod\\models\\red_eye\\Yoksaharat\\fn_pyrocynical.mdl',True)
    a = mesh('E:\\PYTHON\\BSP_reader\\sfm_campsite_night.bsp', False,
             r'D:\SteamLibrary\SteamApps\common\SourceFilmmaker\game\usermod',staticProps=False)
    # print(a.VTX.theVtxFileData.theVtxBodyParts[0].theVtxModelsp[0].theVtxModelLods[0].theVtxMeshes[0].theVtxStripGroups[0])
    # pprint(a.mesh[0])
    # pprint(a.FACES)
