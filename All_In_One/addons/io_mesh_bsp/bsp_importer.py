#  ***** GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#  ***** GPL LICENSE BLOCK *****


import bpy, bmesh
import struct
import os
import re
from collections import namedtuple
from math import radians


# type definitions
BSPHeader = namedtuple('BSPHeader',
    ("version,"
    "entities_ofs,  entities_size,"
    "planes_ofs,    planes_size,"
    "miptex_ofs,    miptex_size,"
    "verts_ofs,     verts_size,"
    "visilist_ofs,  visilist_size,"
    "nodes_ofs,     nodes_size,"
    "texinfo_ofs,   texinfo_size,"
    "faces_ofs,     faces_size,"
    "lightmaps_ofs, lightmaps_size,"
    "clipnodes_ofs, clipnodes_size,"
    "leaves_ofs,    leaves_size,"
    "lface_ofs,     lface_size,"
    "edges_ofs,     edges_size,"
    "ledges_ofs,    ledges_size,"
    "models_ofs,    models_size")
    )
fmt_BSPHeader = '<31i'

BSPModel = namedtuple('BSPModel',
    ("bbox_min_x,  bbox_min_y,  bbox_min_z,"
    "bbox_max_x,   bbox_max_y,  bbox_max_z,"
    "origin_x,     origin_y,    origin_z,"
    "node_id0, node_id1, node_id2, node_id3,"
    "numleafs,"
    "face_id,"
    "face_num")
    )
fmt_BSPModel = '<9f7i'

BSPFace = namedtuple('BSPFace',
    ("plane_id,"
    "size,"
    "ledge_id,"
    "ledge_num,"
    "texinfo_id,"
    "lighttype,"
    "lightlevel,"
    "light0, light1,"
    "lightmap")
    )
fmt_BSPFace = '<HHiHHBBBBi'

BSPVertex = namedtuple('BSPVertex', 'x, y, z')
fmt_BSPVertex = '<fff'

BSPEdge = namedtuple('BSPEdge', 'vertex0, vertex1')
fmt_BSPEdge = '<HH'

BSPTexInfo = namedtuple('BSPTexInfo',
    ("s_x,  s_y,    s_z,    s_dist,"
    "t_x,   t_y,    t_z,    t_dist,"
    "texture_id,"
    "animated")
    )
fmt_BSPTexInfo = '<8f2I'

BSPMipTex = namedtuple('BSPMipTex', 'name, width, height, ofs1, ofs2, ofs4, ofs8')
fmt_BSPMipTex = '<16s6I'


# functions
def print_debug(string):
    debug = False
    if debug:
        print_debug(string)

def load_palette(filepath, pixel_type):
    with open(filepath, 'rb') as file:
        colors_byte = struct.unpack('<768B', file.read(768))
        if(pixel_type == 'BYTE'):
            return colors_byte
        else:
            colors_float = [float(c)/255.0 for c in colors_byte]
            return colors_float

def load_textures(context, filepath):
    with open(filepath, 'rb') as file:
        # read file header
        header_data = file.read(struct.calcsize(fmt_BSPHeader))
        header = BSPHeader._make(struct.unpack(fmt_BSPHeader, header_data))

        # get the list of miptex in the miptex lump (basically a simplified .WAD file inside the bsp)
        if header.miptex_size == 0:
            return []
        file.seek(header.miptex_ofs)
        num_miptex = struct.unpack('<i', file.read(4))[0]
        miptex_ofs_list = struct.unpack('<%di' % num_miptex, file.read(4*num_miptex))

        # load the palette colours (will be converted to RGB float format)
        script_path = os.path.dirname(os.path.abspath(__file__)) + "/"
        colors = load_palette(script_path + "palette.lmp", "FLOAT")

        # return a list of texture information and image data
        # entry format: dict(name, width, height, image)
        texture_data = []

        # load each mip texture
        for miptex_id in range(num_miptex):
            ofs = miptex_ofs_list[miptex_id]
            # get the miptex header
            file.seek(header.miptex_ofs + ofs)
            miptex_data = file.read(struct.calcsize(fmt_BSPMipTex))
            miptex = BSPMipTex._make(struct.unpack(fmt_BSPMipTex, miptex_data))
            miptex_size = miptex.width * miptex.height
            # because some map compilers do not pad strings with 0s, need to handle that
            for i, b in enumerate(miptex.name):
                if b == 0:
                    miptex_name = miptex.name[0:i].decode('ascii')
                    break
            print_debug("[%d] \'%s\' (%dx%d %dbytes)\n" % (miptex_id, miptex_name, miptex.width, miptex.height, miptex_size))

            # get the paletized image pixels
            # if the miptex list is corrupted, make an empty texture to keep id's in order
            try:
                file.seek(header.miptex_ofs + ofs + miptex.ofs1)
                pixels_pal = struct.unpack('<%dB' % miptex_size, file.read(miptex_size))
            except:
                texture_data.append(dict(name=miptex_name, width=0, height=0, image=0))
                print_debug("seek failed")
                continue

            # convert the paletized pixels into regular rgba pixels
            # note that i is fiddled with in order to reverse Y
            pixels = []
            for y in reversed(range(miptex.height)):
                i = miptex.width * y
                for x in range(miptex.width):
                    c = pixels_pal[i+x] * 3
                    pixels.append(colors[c])    # red
                    pixels.append(colors[c+1])  # green
                    pixels.append(colors[c+2])  # blue
                    pixels.append(1.0)          # alpha

            # create an image and save it
            image = bpy.data.images.new(miptex_name, width=miptex.width, height=miptex.height)
            image.pixels = pixels
            texture_data.append(dict(name=miptex_name, width=miptex.width, height=miptex.height, image=image))
            # image.filepath_raw = "/tmp/%s.png" % miptex_name
            # image.file_format = 'PNG'
            # image.save()

        # used by the import_bsp function to set texture mapping for faces
        # and optionally to create materials in the scene
        return texture_data

def mesh_add(mesh_id):
    if bpy.context.scene.objects.active:
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.add(type='MESH', enter_editmode=True)
    obj = bpy.context.object
    obj.name = "bsp_model_%d" % mesh_id
    obj.show_name = True
    obj_mesh = obj.data
    obj_mesh.name = obj.name + "_mesh"
    return obj

def create_materials(texture_data, options):
    for texture in texture_data:
        name = texture['name']
        image = texture['image']
        if image == 0:
            continue

        # pack image data in .blend
        image.pack(as_png = True)
        # create texture from image
        texture = bpy.data.textures.new(name, type='IMAGE')
        texture.image = image
        texture.use_alpha = False
        # create material
        mat = bpy.data.materials.new(name)
        if options['use cycles']:
            mat.use_nodes = True
            ntree = mat.node_tree
            imageNode = ntree.nodes.new('ShaderNodeTexImage')
            imageNode.image = image
            ntree.links.new(imageNode.outputs['Color'], ntree.nodes['Diffuse BSDF'].inputs['Color'])
        mat.diffuse_intensity = 1.0
        mat.specular_intensity = 0.0
        mat.preview_render_type = 'CUBE'
        # assign texture to material
        mtex = mat.texture_slots.add()
        mtex.texture = texture
        mtex.texture_coords = 'UV'

def import_bsp(context, filepath, options):
    # TODO: Clean this up; Perhaps by loading everything into lists to begin with
    header = 0 # scope header variable outside with block
    with open(filepath, 'rb') as file:
        header_data = file.read(struct.calcsize(fmt_BSPHeader))
        header = BSPHeader._make(struct.unpack(fmt_BSPHeader, header_data))

        num_models = int(header.models_size / struct.calcsize(fmt_BSPModel))
        num_faces = int(header.faces_size / struct.calcsize(fmt_BSPFace))
        num_edges = int(header.edges_size / struct.calcsize(fmt_BSPEdge))
        num_verts = int(header.verts_size / struct.calcsize(fmt_BSPVertex))

        print_debug("-- IMPORTING BSP --")
        print_debug("Source file: %s (bsp %d)" % (filepath, header.version))
        print_debug("bsp contains %d models (faces = %d, edges = %d, verts = %d)" % (num_models, num_faces, num_edges, num_verts))

        # read models, faces, edges and vertices into buffers
        file.seek(header.models_ofs)
        model_data = file.read(header.models_size)
        file.seek(header.faces_ofs)
        face_data = file.read(header.faces_size)
        file.seek(header.edges_ofs) # actual edges
        edge_data = file.read(header.edges_size)
        file.seek(header.texinfo_ofs)
        texinfo_data = file.read(header.texinfo_size)

        # read in the list of edges and store in readable form (flat list of ints)
        file.seek(header.ledges_ofs)
        edge_index_list = struct.unpack('<%di' % int(header.ledges_size/4), file.read(header.ledges_size))
        # do the same with vertices (flat list of floats)
        file.seek(header.verts_ofs)
        vertex_list = struct.unpack('<%df' % int(header.verts_size/4), file.read(header.verts_size))

    # load texture data (name, width, height, image)
    print_debug("-- LOADING TEXTURES --")
    texture_data = load_textures(context, filepath)
    if options['create_materials']:
        if options['use cycles']:
            bpy.context.scene.render.engine = 'CYCLES'
        create_materials(texture_data, options)

    # create some structs for storing data
    model_size = struct.calcsize(fmt_BSPModel)
    model_struct = struct.Struct(fmt_BSPModel)
    face_size = struct.calcsize(fmt_BSPFace)
    face_struct = struct.Struct(fmt_BSPFace)
    edge_size = struct.calcsize(fmt_BSPEdge)
    edge_struct = struct.Struct(fmt_BSPEdge)
    texinfo_size = struct.calcsize(fmt_BSPTexInfo)
    texinfo_struct = struct.Struct(fmt_BSPTexInfo)

    print_debug("-- LOADING MODELS --")
    start_model = 0
    if options['worldspawn_only'] == True:
        end_model = 1
    else:
        end_model = num_models


    for m in range(start_model, end_model):
        model_ofs = m * model_size
        model = BSPModel._make(model_struct.unpack_from(model_data[model_ofs:model_ofs+model_size]))
        # create new mesh
        obj = mesh_add(m)

        scale = options['scale']
        obj.scale.x = scale
        obj.scale.y = scale
        obj.scale.z = scale
        bm = bmesh.from_edit_mesh(obj.data)
        # create all verts in bsp
        meshVerts = []
        usedVerts = {}
        for v in range(0, num_verts):
            dex = v * 3
            usedVerts[v] = False
            meshVerts.append( bm.verts.new( [vertex_list[dex], vertex_list[dex+1], vertex_list[dex+2] ] ) )
        print_debug("[%d] %d faces" % (m, model.face_num))
        duplicateFaces = 0
        for f in range(0, model.face_num):
            face_ofs = (model.face_id + f) * face_size
            face = BSPFace._make(face_struct.unpack_from(face_data[face_ofs:face_ofs+face_size]))
            texinfo_ofs = face.texinfo_id * texinfo_size
            texinfo = BSPTexInfo._make(texinfo_struct.unpack_from(texinfo_data[texinfo_ofs:texinfo_ofs+texinfo_size]))
            if not texture_data:
                texture_specs = dict(width=64, height=64) # dummy
            else:
                texture_specs = texture_data[texinfo.texture_id]
            texS = texinfo[0:3]
            texT = texinfo[4:7]

            # populate a list with vertices
            face_vertices = []
            face_uvs = []

            for i in range(0,face.ledge_num):
                edge_index = edge_index_list[face.ledge_id+i]
                # assuming vertex order is 0->1
                edge_ofs = edge_index * edge_size
                vert_id = 0
                if edge_index < 0:
                    # vertex order is 1->0
                    edge_ofs = -edge_index * edge_size
                    vert_id = 1

                edge = BSPEdge._make(edge_struct.unpack_from(edge_data[edge_ofs:edge_ofs+edge_size]))
                vofs = edge[vert_id]
                face_vertices.append(meshVerts[vofs])
                usedVerts[vofs] = True

            # find or append material for this face
            material_id = -1
            if options['create_materials'] and texture_data:
                texture_name = texture_data[texinfo.texture_id]['name']
                try:
                    material_names = [ m.name for m in obj.data.materials ]
                    material_id = material_names.index(texture_name)
                except: #ValueError:
                    obj.data.materials.append(bpy.data.materials[texture_name])
                    material_id = len(obj.data.materials) - 1
            # try to add face to mesh
            # note that there is a little faff to get the face normals in the correct order
            face = 0
            try:
                face = bm.faces.new((face_vertices[i] for i in reversed(range(-len(face_vertices), 0))))
            except:
                duplicateFaces += 1

            # calculate UVs
            if face != 0:
                uv_layer = bm.loops.layers.uv.verify()
                bm.faces.layers.tex.verify()
                bm.faces.ensure_lookup_table()
                face = bm.faces[-1] # local bmesh face gets deleted by one of the preceding lines
                for loopElement in face.loops:
                    luvLayer = loopElement[uv_layer]
                    luvLayer.uv[0] =  (loopElement.vert.co.dot(texS) + texinfo.s_dist)/texture_specs['width']
                    luvLayer.uv[1] = -(loopElement.vert.co.dot(texT) + texinfo.t_dist)/texture_specs['height']

                # assign material
                if options['create_materials'] and material_id != -1:
                    face.material_index = material_id
        if duplicateFaces > 0:
            print_debug("%d duplicate faces not created in model %d" % (duplicateFaces, m))

        # remove unused vertices from this model
        for vi in range(0, num_verts):
            if not usedVerts[vi]:
                bm.verts.remove(meshVerts[vi])
        # update the mesh with data from the bmesh
        bmesh.update_edit_mesh(obj.data)

    bpy.ops.object.mode_set(mode='OBJECT')

    # add lights and other camera from the entities text
    lights = []
    infoStart = 0
    with open(filepath, 'r') as file:
        file.seek(header.entities_ofs)
        lines = file.read(header.entities_size).splitlines()
        startRE = re.compile('^{')
        endRE = re.compile('^}')
        keyRE = re.compile('"([^"]+)"\s+"([^"]+)"')
        lightRE = re.compile('light.*')
        playerRE = re.compile('info')
        i=0
        len_lines = len(lines)
        # parse the entities text line by line
        while i < len_lines:
            # found a new entity
            if startRE.match(lines[i]):
                i += 1
                ent = {}
                while i < len_lines:
                    pair = keyRE.match(lines[i])
                    if pair:
                        ent[pair.group(1)] = pair.group(2)
                    # at the end of this entity
                    if endRE.match(lines[i]):
                        break
                    i += 1
                # remember certain entities for later
                if 'classname' in ent and lightRE.match(ent['classname']):
                    lights.append(ent)
                if 'classname' in ent and ent['classname'] == 'info_player_start':
                    infoStart = ent
            i += 1
    coodRE = re.compile('(-?\d+)\s+(-?\d+)\s+(-?\d+)') # TODO fix for decimal point
    print_debug("there are %d lights in the file" % (len(lights)))
    scale = options['scale']
    if not options['create lamps']:
        lights = []
    if options['use cycles'] and len(lights) > 0:
        bpy.context.scene.render.engine = 'CYCLES'
    curseLoc = bpy.context.scene.cursor_location
    for lightInfo in lights:
        bright = 200
        if 'light' in lightInfo:
            bright = float(lightInfo['light'])
        # parse and scale location of this light
        co = coodRE.match(lightInfo['origin'])
        if co:
            x = float(co.group(1)) * scale + curseLoc.x
            y = float(co.group(2)) * scale + curseLoc.y
            z = float(co.group(3)) * scale + curseLoc.z
            bpy.ops.object.lamp_add(location=(x,y,z))
            if options['use cycles']:
                bpy.data.lamps[-1].node_tree.nodes['Emission'].inputs['Strength'].default_value = bright
                # bpy.data.lamps[-1].node_tree.nodes['Emission'].inputs['Color'].default_value = (0.8, 0.8, 0.8, 1)
            else:
                bpy.data.lamps[-1].energy = bright/50
                bpy.data.lamps[-1].use_shadow = True
                bpy.data.lamps[-1].falloff_type = 'LINEAR_QUADRATIC_WEIGHTED'
                bpy.data.lamps[-1].distance = 5
    # add and set a camera at level start, if info_player_start defined
    if infoStart != 0 and options['create spawn']:
        co = coodRE.match(infoStart['origin'])
        rot = radians(float(infoStart['angle'])-90)
        if co:
            x = float(co.group(1)) * scale + curseLoc.x
            y = float(co.group(2)) * scale + curseLoc.y
            z = float(co.group(3)) * scale + curseLoc.z
            bpy.ops.object.camera_add(location=(x,y,z),rotation=(radians(90),0,rot))
            # 90 degree FOV, set camera active
            bpy.context.active_object.data.lens = 16
            bpy.context.scene.camera = bpy.context.active_object

    print_debug("-- IMPORT COMPLETE --")
