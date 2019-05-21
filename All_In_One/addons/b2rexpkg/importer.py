"""
Import sim data into Blender.
"""

import os
import sys
import logging
from collections import defaultdict

logger = logging.getLogger("b2rex.importer")

from .tools.siminfo import GridInfo
from .tools.simconnection import SimConnection
from .tools.simtypes import AssetType
from .tools import runexternal

import xml.parsers.expat

if sys.version_info[0] == 2:
    import httplib
    import urllib2
    import Blender
    from urllib2 import HTTPError, URLError
    from urllib import urlretrieve
    from Blender import Mathutils as mathutils
    from .b24 import editor
    from .b24.editor import EditorObject, EditorMesh
    bversion = 2
    def bytes(text):
        return text
else:
    import http.client as httplib
    import urllib.request as urllib2
    from urllib.request import urlretrieve
    from urllib.error import HTTPError, URLError
    import mathutils
    from .b25 import editor
    bversion = 3
if bversion == 2:
   layerMappings = {'normalMap':'NOR',
                 'heightMap':'DISP',
                 'reflectionMap':'REF',
                 'opacityMap':'ALPHA',
                 'lightMap':'AMB',
                 'specularMap':'SPEC' }
elif bversion == 3:
   layerMappings = {'normalMap':'use_map_normal',
                 'heightMap':'use_map_displacement',
                 'reflectionMap':'use_map_reflect',
                 'opacityMap':'use_map_alpha',
                 'lightMap':'use_map_ambient',
                 'specularMap':'use_map_specular' }


import struct
import subprocess
import math
from .tools.oimporter.otypes import VES_POSITION, VES_NORMAL, VES_TEXTURE_COORDINATES
from .tools.oimporter.otypes import type2size
from .tools.oimporter.util import arr2float, parse_vector, get_vertex_legend
from .tools.oimporter.util import get_nor, get_uv, mat_findtextures, get_vcoords
from .tools.oimporter.omaterial import OgreMaterial
from .tools import oimporter

import socket
import traceback

import bpy

CONNECTION_ERRORS = (HTTPError, URLError, httplib.BadStatusLine,
                                     xml.parsers.expat.ExpatError)

default_timeout = 4

socket.setdefaulttimeout(default_timeout)

class Importer25(object):
    def __init__(self):
        self._mesh_mat_idx_empty = []
        self._material_names = {}
    def import_submesh(self, meshId, new_mesh, vertex, vbuffer, indices, materialName,
                       matIdx, materials):
        """
        Import submesh info and fill blender face and vertex information.
        """
        vertex_legend = get_vertex_legend(vertex)
        pos_offset = vertex_legend[VES_POSITION][1]
        no_offset = vertex_legend[VES_NORMAL][1]
        bmat = None
        image = None
        uvco_offset = None
        stride = 0
        for layer in vertex_legend.values():
            stride += type2size[layer[2]]
        if VES_TEXTURE_COORDINATES in vertex_legend:
            uvco_offset = vertex_legend[VES_TEXTURE_COORDINATES][1]
        indices_map = []
        new_vertices = []
        start_vert = len(new_mesh.vertices)
        # vertices
        for idx in range(max(indices)+1):
            coords = get_vcoords(vbuffer, idx, pos_offset, stride)
            if not coords:
                coords = (0.0,0.0,0.0)
            if not coords in new_vertices:
                if matIdx != 0:
                    vert = new_mesh.vertices.add(1)
                    new_mesh.vertices[len(new_mesh.vertices)-1].co = coords
                new_vertices.append(coords)
            indices_map.append(new_vertices.index(coords)+start_vert)
        if matIdx == 0:
            verts_flat = [f for v in new_vertices for f in v]
            new_mesh.vertices.add(len(new_vertices))
            new_mesh.vertices.foreach_set("co", verts_flat)
            del verts_flat
            del new_vertices
        if not len(new_mesh.vertices):
            logger.debug("mesh with no vertex!!")
            return

        start_face = len(new_mesh.faces)
        # faces
        new_mesh.faces.add(int(len(indices)/3))
        if matIdx == 0:
            # only for mat 0 because otherwise we're adding faces so
            # can't use foreach (need to check out the api)
            faces = [a for f_idx in range(0,
                     len(indices), 3) for a in [indices_map[indices[f_idx]],
                                                indices_map[indices[f_idx+1]],
                                                indices_map[indices[f_idx+2]],
                                                0]]
            new_mesh.faces.foreach_set("vertices_raw", faces)
            for face in new_mesh.faces:
                    face.material_index = matIdx
                    # why doesnt this work?
                    #new_mesh.faces.foreach_set("material_index", [matIdx])
            del faces
        else:
            faces  = []
            for idx in range(int(len(indices)/3)):
                f_idx = idx*3
                face = [indices_map[indices[f_idx]],
                                    indices_map[indices[f_idx+1]],
                                    indices_map[indices[f_idx+2]]]
                new_mesh.faces[idx+start_face].vertices = face
                new_mesh.faces[idx+start_face].material_index = matIdx
        """
            continue
            try:
                no1 = get_nor(indices[idx], vbuffer, no_offset)
            except:
                no1 = [0.0,0.0,0.0]
            try:
                no2 = get_nor(indices[idx+1], vbuffer, no_offset)
            except:
                no2 = [0.0,0.0,0.0]
            try:
                no3 = get_nor(indices[idx+2], vbuffer, no_offset)
            except:
                no3 = [0.0,0.0,0.0]
        """
        # UV
        materialPresent = False

        ogrematPresent = False
        matId = ""
        if matIdx < len(materials):
            # look by id 
            matId = str(materials[matIdx][1])
            if matId in self._key_materials:
                materialPresent = True
            else:
                materialPresent = False

        if not matId:
            # no matId, so try to find the material by name
            if not materialPresent and matIdx < len(new_mesh.materials):
                material = new_mesh.materials[matIdx]
                for slot in material.texture_slots:
                    if slot and slot.use_map_color_diffuse and slot.texture:
                        tex = slot.texture
                        if tex.type == 'IMAGE' and tex.image:
                            materialPresent = True

            if materialName in self._imported_ogre_materials:
                 ogremat = self._imported_ogre_materials[materialName]
                 if ogremat.btex and ogremat.btex.image:
                       ogrematPresent = True

            matId = 'unknown'

        if ogrematPresent or materialPresent:
            self.assign_submesh_images(materialName,
                                     vertex_legend, new_mesh, indices,
                                     vbuffer, uvco_offset, start_face, matIdx,
                                       matId)
        elif not uvco_offset:
            return
        elif matId:
            self.add_material_callback(matId, materialName, self.assign_submesh_images,
                                     vertex_legend, new_mesh, indices,
                                     vbuffer, uvco_offset, start_face, matIdx,
                                       matId)

    

    def find_diffuse_image(self, material):
        if not material:
            return
        for slot in material.texture_slots:
            if slot and slot.use_map_color_diffuse and slot.texture:
                tex = slot.texture
                if tex.type == 'IMAGE' and tex.image:
                    image = tex.image
                    return image

    def assign_submesh_images(self, materialName, vertex_legend, new_mesh,
                              indices, vbuffer, uvco_offset, start_face, matIdx,
                             matId):
        #bmat = self._imported_materials[materialName]
        image = None
        material = None
        if matId == 'unknown':
            matId = None

        if matId:
            material = self.find_with_uuid(matId, bpy.data.materials, 'materials')
            image = self.find_diffuse_image(material)
        if not image:
            # we didnt find the material by uuid so lets look by name
            if materialName in self._imported_ogre_materials:
                ogremat = self._imported_ogre_materials[materialName]
                if ogremat.btex and ogremat.btex.image:
                    image = ogremat.btex.image
                else:
                    material = self.find_with_uuid(ogremat.uuid, bpy.data.materials,
                                              'materials')
                    image = self.find_diffuse_image(material)
        if not image and matIdx < len(new_mesh.materials):
            # still didn't find it, try by material idx in the mesh
            material = new_mesh.materials[matIdx]
            image = self.find_diffuse_image(material)
        if not image:
            # shoudln't happen
            logger.warning("ASSIGN IMAGES BUT NO IMAGE!!!!! "+matId+" "+materialName)
        if material and not material.name in new_mesh.materials:
            # should be set ordered or be there since before
            new_mesh.materials.append(material)
        if VES_TEXTURE_COORDINATES in vertex_legend:
            if not len(new_mesh.uv_textures):
                uvtex = new_mesh.uv_textures.new()
                new_mesh.uv_textures.active = uvtex
            else:
                uvtex = new_mesh.uv_textures.active
            for idx in range(int(len(indices)/3)):
                fidx = idx*3
                uv1 = get_uv(indices[fidx], vbuffer, uvco_offset)
                uv2 = get_uv(indices[fidx+1], vbuffer, uvco_offset)
                uv3 = get_uv(indices[fidx+2], vbuffer, uvco_offset)

                if start_face+idx > len(uvtex.data):
                    logger.warning("insufficient faces in uvtex????")
                blender_tface = uvtex.data[start_face+idx]
                blender_tface.uv1 = uv1
                blender_tface.uv2 = uv2
                blender_tface.uv3 = uv3
                if image:
                    blender_tface.image = image
                    blender_tface.use_image = True

        if not len(new_mesh.faces):
            logger.warning("mesh with no faces!!")
        #sys.stderr.write("*")
        #sys.stderr.flush()
        return new_mesh

    def _get_local_pos(self, pos, parent):
        p_scale = parent.scale
        return (pos[0]/p_scale[0], pos[1]/p_scale[1], pos[2]/p_scale[2])
        parent_imatrix = parent.matrix_world.copy().invert()
        pos_v = mathutils.Vector(pos)
        l_pos = pos_v*parent_imatrix
        return (l_pos[0], l_pos[1], l_pos[2])

    def _get_global_pos(self, pos, parent):
        p_scale = parent.scale
        return (pos[0]*p_scale[0], pos[1]*p_scale[1], pos[2]*p_scale[2])

    def _get_local_rot(self, rot, parent):
        return rot
        parent_imatrix = parent.matrix_world.copy().invert()
        euler = mathutils.Quaternion((rot[3], rot[0], rot[1], rot[2]))
        r_mat = euler.to_matrix().to_4x4()
        l_rmat = r_mat*parent_imatrix
        try:
            rot = l_rmat.to_quaternion()
        except:
            # blender 2.56
            rot = l_rmat.to_quat()
        return (rot.w, rot.x, rot.y, rot.z)

    def _get_local_scale(self, scale, parent):
        p_scale = parent.scale
        return (scale[0]/p_scale[0], scale[1]/p_scale[1], scale[2]/p_scale[2])
        parent_imatrix = parent.matrix_world.to_euler().to_matrix()
        parent_imatrix.invert()
        p_scale = parent.scale
        scale = (scale[0]/p_scale[0], scale[1]/p_scale[1], scale[2]/p_scale[2])
        scale = mathutils.Vector(scale)
        #scale_x = mathutils.Matrix.Scale(scale[0], 3, mathutils.Vector((1,0,0)))
        #scale_y = mathutils.Matrix.Scale(scale[1], 3, mathutils.Vector((0,1,0)))
        #scale_z = mathutils.Matrix.Scale(scale[2], 3, mathutils.Vector((0,0,1)))
        #scale_m = scale_x * scale_y * scale_z
        scale = scale * parent_imatrix
        l_pos = scale
        return (l_pos[0], l_pos[1], l_pos[2])

                #p_scale = parent.scale
                #return (scale[0]/p_scale[0], scale[1]/p_scale[1], scale[2]/p_scale[2])

    def _get_global_scale(self, scale, parent):
        p_scale = parent.scale
        return (scale[0]*p_scale[0], scale[1]*p_scale[1], scale[2]*p_scale[2])

    def apply_position(self, obj, pos, offset_x=128.0, offset_y=128.0,
                       offset_z=20.0, raw=False):

        if raw:
            obj.location = pos
        else:
            if obj.parent:
                pos = self._get_local_pos(pos, obj.parent)
                obj.location = self._apply_position(pos, 0, 0, 0)
            else:
                obj.location = self._apply_position(pos, offset_x, offset_y,
                                                        offset_z)

    def apply_scale(self, obj, scale):
        if obj.parent:
            scale = self._get_local_scale(scale, obj.parent)
        obj.scale = (scale[0], scale[1], scale[2])

    def unapply_position(self, obj, pos, offset_x=128.0, offset_y=128.0,
                       offset_z=20.0):
        if obj.parent:
            pos = self._get_global_pos(pos, obj.parent)
        return self._unapply_position(pos, offset_x, offset_y, offset_z)

    def unapply_scale(self, obj, scale):
        if obj.parent:
            scale = self._get_global_scale(scale, obj.parent)
        return [scale[0], scale[1], scale[2]]


    def unapply_rotation(self, euler):
        euler = mathutils.Euler([euler[0], euler[1],
                                        euler[2]])
        try:
            q = euler.to_quaternion()
        except:
            # blender 2.56
            q = euler.to_quat()

        return [q.x, q.y, q.z, q.w]
        
    def apply_rotation(self, obj, rot, raw=False):
        if obj.parent:
            rot = self._get_local_rot(rot, obj.parent)
        if raw:
            obj.rotation_euler = rot
        else:
            obj.rotation_euler = self._apply_rotation(rot)

    def getcreate_object(self, obj_uuid, name, mesh_data):
        logger.debug("create object")
        obj = self.find_with_uuid(obj_uuid, bpy.data.objects,
                             "objects")
        if not obj:
            obj = bpy.data.objects.new(name, mesh_data)
            editor.set_loading_state(obj, 'LOADING')
        return obj

    def create_texture(self, name, filename):
        bim = bpy.data.images.load(filename)
        btex = bpy.data.textures.new(name, 'IMAGE')
        btex.image = bim
        return btex

    def get_current_scene(self):
        return bpy.context.scene

    def set_immutable(self, obj, val=True):
        obj.lock_location = (val, val, val)
        obj.lock_scale = (val, val, val)
        obj.lock_rotation = (val, val, val)
        obj.lock_rotations_4d = val
        obj.lock_rotation_w = val

    def _apply_rotation(self, rot):
        b_q = mathutils.Quaternion((rot[3], rot[0], rot[1],
                                           rot[2]))
        r = 1.0
        b_q = mathutils.Quaternion((b_q.w, b_q.x, b_q.y, b_q.z))
        euler = b_q.to_euler()
        return (euler[0]*r, euler[1]*r, (euler[2])*r)

    def find_with_uuid(self, groupid, objects, section):
        """
        Find the object with the given uuid.
        """
        if groupid in self._total[section]:
            # we get the objects by name to avoid memory corruption issues,
            # but we're not checking if the names change!
            return objects[self._total[section][groupid]]
        else:
            for obj in objects:
                obj_uuid = self.get_uuid(obj)
                if obj_uuid:
                    #self._total[section][obj_uuid] = obj.name
                    if obj_uuid == groupid:
                        return obj



class Importer24(object):
    def import_submesh(self, meshId, new_mesh, vertex, vbuffer, indices, materialName,
                       matIdx):
        """
        Import submesh info and fill blender face and vertex information.
        """
        vertex_legend = get_vertex_legend(vertex)
        pos_offset = vertex_legend[VES_POSITION][1]
        no_offset = vertex_legend[VES_NORMAL][1]
        image = None
        if materialName in self._imported_ogre_materials:
            ogremat = self._imported_ogre_materials[materialName]
            if ogremat.btex and ogremat.btex.image:
                image = ogremat.btex.image
        if VES_TEXTURE_COORDINATES in vertex_legend:
            uvco_offset = vertex_legend[VES_TEXTURE_COORDINATES][1]
        vertmaps = {}
        indices_map = []
        # vertices
        for idx in range(max(indices)+1):
            coords = get_vcoords(vbuffer, idx, pos_offset)
            if coords:
                if not coords in vertmaps:
                    new_mesh.verts.extend(*coords)
                    vertmaps[coords] = len(new_mesh.verts)-1
                indices_map.append(vertmaps[coords])
            else:
                new_mesh.verts.extend(0.0,0.0,0.0)
                indices_map.append(len(new_mesh.verts)-1)
        if not len(new_mesh.verts):
            logger.debug("mesh with no vertex!!")
        # faces
        for idx in range(len(indices)/3):
            idx = idx*3
            new_mesh.vertexUV = False
            face = [indices_map[indices[idx]],
                                indices_map[indices[idx+1]],
                                indices_map[indices[idx+2]]]
            new_mesh.faces.extend(face, ignoreDups=True)
            if len(new_mesh.faces) == 0:
                logger.debug("Degenerate face!")
                continue
            face = new_mesh.faces[len(new_mesh.faces)-1]
            if image:
                face.image = image
            try:
                no1 = get_nor(indices[idx], vbuffer, no_offset)
            except:
                no1 = [0.0,0.0,0.0]
            try:
                no2 = get_nor(indices[idx+1], vbuffer, no_offset)
            except:
                no2 = [0.0,0.0,0.0]
            try:
                no3 = get_nor(indices[idx+2], vbuffer, no_offset)
            except:
                no3 = [0.0,0.0,0.0]
            if VES_TEXTURE_COORDINATES in vertex_legend:
                uv1 = get_uv(indices[idx], vbuffer, uvco_offset)
                uv2 = get_uv(indices[idx+1], vbuffer, uvco_offset)
                uv3 = get_uv(indices[idx+2], vbuffer, uvco_offset)
                face.uv = (mathutils.Vector(uv1),
                           mathutils.Vector(uv2),
                           mathutils.Vector(uv3))
        if not len(new_mesh.faces):
            logger.warning("mesh with no faces!!")
        #sys.stderr.write("*")
        #sys.stderr.flush()
        return new_mesh

    def create_texture(self, name, filename):
        bim = Blender.Image.Load(filename)
        btex = Blender.Texture.New(name)
        btex.setType('Image')
        btex.image = bim
        return btex

    def _get_local_pos(self, pos, parent):
        p_scale = parent.getSize('localspace')
        return (pos[0]/p_scale[0], pos[1]/p_scale[1], pos[2]/p_scale[2])

    def _get_global_pos(self, pos, parent):
        p_scale = parent.getSize('localspace')
        return (pos[0]*p_scale[0], pos[1]*p_scale[1], pos[2]*p_scale[2])

    def _get_local_rot(self, rot, parent):
        return rot

    def _get_local_scale(self, scale, parent):
        p_scale = parent.getSize('localspace')
        return (scale[0]/p_scale[0], scale[1]/p_scale[1], scale[2]/p_scale[2])

    def _get_global_scale(self, scale, parent):
        p_scale = parent.getSize('localspace')
        return (scale[0]*p_scale[0], scale[1]*p_scale[1], scale[2]*p_scale[2])


    def apply_position(self, obj, pos, offset_x=128.0, offset_y=128.0,
                       offset_z=20.0, raw=False):
        if raw:
            obj.setLocation(*pos)
        else:
            if obj.getParent():
                pos = self._get_local_pos(pos, obj.getParent())
                obj.setLocation(pos[0], pos[1], pos[2])
            else:
                obj.setLocation(pos[0]-offset_x, pos[1]-offset_y, pos[2]-offset_z)

    def apply_scale(self, obj, scale):
        if obj.getParent():
            scale = self._get_local_scale(scale, obj.getParent())
        obj.setSize(scale[0], scale[1], scale[2])

    def unapply_scale(self, obj, scale):
        if obj.getParent():
            scale = self._get_global_scale(scale, obj.getParent())
        return [scale[0], scale[1], scale[2]]

    def unapply_position(self, obj, pos, offset_x=128.0, offset_y=128.0,
                       offset_z=20.0):
        if obj.getParent():
            pos = self._get_local_pos(pos, obj.getParent())
        return self._unapply_position(pos, offset_x, offset_y, offset_z)



    def unapply_rotation(self, euler):
        r = 180.0/math.pi
        euler = mathutils.Euler([euler[0]*r, euler[1]*r,
                                        (euler[2]*r)])
        q = euler.toQuat()
        return [q.x, q.y, q.z, q.w]
        
    def apply_rotation(self, obj, rot, raw=False):
        if raw:
            obj.setEuler(*rot)
        else:
            obj.setEuler(*self._apply_rotation(rot))

    def _apply_rotation(self, rot):
        b_q = mathutils.Quaternion(rot[3], rot[0], rot[1],
                                           rot[2])
        #b_q1 = b_q.cross(Blender.Mathutils.Quaternion([0,-1,0]))
        #b_q2 = b_q1.cross(Blender.Mathutils.Quaternion([-1,0,0]))
        #b_q3 = b_q2.cross(Blender.Mathutils.Quaternion([0,0,-1]))
        r = math.pi/180.0;
        if b_q:
            b_q = mathutils.Quaternion(b_q.w, b_q.x, b_q.y, b_q.z)
            euler = b_q.toEuler()
            return (euler[0]*r, euler[1]*r, (euler[2])*r)

    def getcreate_object(self, obj_uuid, name, mesh_data):
        obj = self.find_with_uuid(obj_uuid, bpy.data.objects,
                             "objects")
        if not obj:
            obj = self.wrap_object(Blender.Object.New("Mesh", name), 'objects')
        obj.link(mesh_data)
        return obj

    def get_current_scene(self):
        scene = Blender.Scene.GetCurrent ()
        return scene

    def set_immutable(self, obj, val):
        pass

    def wrap_object(self, obj, section):
        if section == 'objects':
           return EditorObject(obj)
        elif section == 'meshes':
            return EditorMesh(obj)
        else:
            return obj

    def find_with_uuid(self, groupid, objects, section):
        """
        Find the object with the given uuid.
        """
        if groupid in self._total[section]:
            # we get the objects by name to avoid memory corruption issues,
            # but we're not checking if the names change!
            return self.wrap_object(objects[self._total[section][groupid]],
                                    section)
        else:
            for obj in objects:
                obj_uuid = self.get_uuid(obj)
                if obj_uuid:
                    self._total[section][obj_uuid] = obj.name
                    if obj_uuid == groupid:
                        return self.wrap_object(obj, section)


# Common
if bversion == 3:
    ImporterBase = Importer25
else:
    ImporterBase = Importer24

class Importer(ImporterBase):
    def __init__(self, gridinfo):
        self._material_cb = defaultdict(list)
        self._mesh_cb = defaultdict(list)
        self._key_materials = {}
        self._texture_callbacks = defaultdict(list)
        ImporterBase.__init__(self)
        self.gridinfo = gridinfo
        self.init_structures()

    def init_structures(self):
        """
        Initialize importer caches.

        Can be called to avoid caching of results.
        """
        self._imported_assets = {}
        self._imported_materials = {}
        self._imported_ogre_materials = {}

        self._objects = {}
        self._found = {"objects":0,"meshes":0,"materials":0,"textures":0,"texts":0}
        self._total_server = {"objects":0,"meshes":0,"materials":0,"textures":0,"texts":0}
        self._total = {"objects":{},"meshes":{},"materials":{},"textures":{},"texts":{}}

    def add_mesh_callback(self, meshId, cb, *args):
        mesh = self.find_with_uuid(meshId, bpy.data.meshes, "meshes")
        if mesh:
            cb(*args)
        else:
            self._mesh_cb[meshId].append([cb, args])

    def trigger_mesh_callbacks(self, meshId, new_mesh):
        for cb, args in self._mesh_cb[meshId]:
            cb(new_mesh, *args)
        if meshId in self._mesh_cb:
            self._mesh_cb.pop(meshId)

    def add_material_callback(self, key, materialName, cb, *args):
        if materialName in self._imported_ogre_materials:
            ogremat = self._imported_ogre_materials[materialName]
            if ogremat.btex and ogremat.btex.image:
                cb(materialName, *args)
                return
        if key in self._key_materials:
            ogremat = self._key_materials[key]
            ogremat.name = materialName
            self._imported_ogre_materials[ogremat.name] = ogremat
            cb(materialName, *args)
            return
        self._material_cb[key].append([cb, materialName, args])

    def trigger_material_callbacks(self, slot, ogremat, matIdx):
        materialNames = set()
        for cb, _materialName, args in self._material_cb[slot]:
            ogremat.name = _materialName # hack
            self._imported_ogre_materials[ogremat.name] = ogremat # XXX hack
            cb(_materialName, *args)
            materialNames.add(_materialName)
        if slot in self._material_cb:
            self._material_cb.pop(slot)
        # add to slot - mat dict
        self._key_materials[slot] = ogremat
        materialNames.add(ogremat.name)
        for materialName in materialNames:
             self._imported_ogre_materials[materialName] = ogremat # XXX hack
        # now look for all cbs having materialName and trigger them too
        for slot, pars in self._material_cb.items():
            found = False
            idx = 0
            found_slots = []
            for cb, _materialName, args in pars:
                if _materialName in materialNames:
                    cb(_materialName, *args)
                    found_slots.append((slot, idx))
                idx += 1
            for slot, idx in reversed(found_slots):
                self._material_cb[slot].pop(idx)

    def doTextureDownloadTranscode(self, pars):
        http_url, pars, data = pars
        assetName = pars[0] # we dont get the name here
        assetId = pars[0]
        return self.decode_texture(assetId, assetName, data)
        #return self.decode_texture_fromfile(assetId, assetName, origin)

    def decode_texture(self, textureId, textureName, data):
        destpath = os.path.join(self.getExportDir(), textureId+".1.jpg")
        f = open(destpath, "wb")
        f.write(data)
        f.close()
        return self.decode_texture_fromfile(textureId, textureName,
                                     destpath)

    def decode_texture_fromfile(self, textureId, textureName, origin):
        split_name = textureName.split("/")
        if len(split_name) > 2:
            textureName = split_name[2]
        dest = os.path.join(self.getExportDir(),textureName)
        return self.convert_image_format(origin, 'png', dest)

    def convert_image_format(self, origin, ext, dest=None):
        if dest == None:
            dest = origin
        if not dest[-3:] in [ext]:
            dest = dest + "." + ext
        if os.path.exists(dest):
            # its already there.. probably should update but for now we dont
            # care
            return dest
        user_paths = []
        if self.exportSettings.tools_path:
            user_paths = [self.exportSettings.tools_path]
        try:
            subprocess.call([runexternal.find_application("convert", user_paths),
                              origin,
                              dest])
            return dest
        except:
            logger.error("error opening:" + str(dest))

    def parse_texture(self, textureId, textureName, dest):
        btex = self.create_texture(textureName, dest)
        self.set_uuid(btex, textureId)
        self.set_uuid(btex.image, textureId)
        self._imported_assets[textureId] = btex
        return btex

    def import_texture(self, texture):
        """
        Import the given texture from opensim.
        """
        logger.debug(("texture", texture))
        if texture in self._imported_assets:
            return self._imported_assets[texture]
        else:
            texture = texture.decode()
            tex = self.gridinfo.getAsset(texture)
            if "name" in tex:
                tex_name = tex["name"]
                try:
                    btex = bpy.data.textures[tex_name]
                    # XXX should update
                    return btex
                except:
                    dest = self.decode_texture(texture, tex_name, tex["data"])
                    self.parse_texture(texture, tex_name, dest)

    def create_blender_material(self, ogremat, mat, meshId, matIdx):
        """
        Create a blender material from ogre format.
        """
        logger.debug("create_blender_material")
        textures = ogremat.textures
        bmat = None
        idx = 0
        mat_name = mat["name"].split("/")[0]
        try:
            bmat = bpy.data.materials[mat_name]
            if bversion == 3:
                bmat.name = "tobedeleted"
                bmat = bpy.data.materials.new(mat_name)
        except:
            bmat = bpy.data.materials.new(mat_name)
        self.set_uuid(bmat, ogremat.uuid)
        # material base properties
        if ogremat.doambient:
            if bversion == 2:
                bmat.setAmb(ogremat.ambient)
            else:
                bmat.ambient = ogremat.ambient
        if ogremat.specular:
            if bversion == 2:
                bmat.setSpec(1.0)
                bmat.setSpecCol(ogremat.specular[:3])
                bmat.setHardness(int(ogremat.specular[3]*4.0))
            else:
                bmat.specular_intensity = 1.0
                ogremat.specular[:3]
                bmat.specular_color = ogremat.specular[:3]
                bmat.specular_hardness = int(ogremat.specular[3]*4.0)
        if ogremat.alpha < 1.0:
            bmat.alpha = ogremat.alpha
        # specular
        for layerName, textureId in ogremat.layers.items():
            if layerName == 'shadowMap':
                if bversion == 2:
                    bmat.setMode(Blender.Material.Modes['SHADOWBUF'] & bmat.getMode())
                else:
                    bmat.use_cast_buffer_shadows = True
            if textureId:
                textureId = textureId
                pars = (bmat, layerName, mat["name"], ogremat, idx, meshId,
                        matIdx)
                if textureId in self._imported_assets:
                    btex = self._imported_assets[textureId]
                    self.layer_ready(btex, *pars)
                elif self.simrt:
                   pars = (textureId,) + pars
                   if not self.Asset.downloadAsset(textureId, 0,
                                    self.texture_downloaded, 
                                    pars,
                                       main=self.doTextureDownloadTranscode):
                       self.add_texture_callback(textureId, self.layer_ready, pars[1:])
                idx += 1
        self._imported_materials[mat["name"]] = bmat
        return bmat

    def texture_downloaded(self, *args):
        self.command_queue.append(["texturearrived"]+list(args))

    def add_texture_callback(self, textureId, cb, cb_pars):
        self._texture_callbacks[textureId].append([cb, cb_pars])

    def processTextureArrived(self, image_path, textureId, bmat, layerName, mat_name,
                           ogremat, idx, meshId, matIdx):
        textureName = 'opensim'+textureId
        btex = self.parse_texture(textureId, textureName, image_path)
        self.layer_ready(btex, bmat, layerName, mat_name, ogremat, idx, meshId,
                        matIdx)
        if textureId in self._texture_callbacks:
            for cb, cb_pars in self._texture_callbacks[textureId]:
                cb(btex, *cb_pars)
            del self._texture_callbacks[textureId]

    def layer_ready(self, btex, bmat, layerName, mat_name, ogremat, idx, meshId,
                   matIdx):
        # btex = self.import_texture(textureName)
        if btex:
            if bversion == 2:
                mapto = 'COL'
            else:
                mapto = 'use_map_color_diffuse'
            if layerName in layerMappings:
                mapto = layerMappings[layerName]
            if mapto in ['use_map_color_diffuse', 'COL']:
                ogremat.btex = btex
            if bversion == 2:
                if mapto:
                    mapto = Blender.Texture.MapTo[mapto]
                bmat.setTexture(idx, btex, Blender.Texture.TexCo.ORCO, mapto) 
            if bversion == 3:
                new_slot = bmat.texture_slots.add()
                setattr(new_slot, mapto, True)
                if not mapto == 'use_map_color_diffuse':
                    new_slot.use_map_color_diffuse = False
                new_slot.texture = btex
                new_slot.texture_coords = 'UV'
                if mapto in 'use_map_normal':
                    new_slot.normal_map_space = 'TANGENT'
                    new_slot.normal_factor = 1.0
                    btex.use_normal_map = True
                    btex.use_mipmap = False
            if mapto in ['use_map_color_diffuse', 'COL']:
                self.trigger_material_callbacks(self.get_uuid(bmat), ogremat,
                                                matIdx)



    def import_material(self, matId, matIdx, retries):
        """
        Import a material from opensim.
        """
        logger.debug(("material", matId))
        btex = None
        bmat = None
        gridinfo = self.gridinfo
        try:
            bmat = self.find_with_uuid(matId, bpy.data.materials, 'materials')
            if not bmat:
            # XXX should check on library and refresh if its there
                mat = gridinfo.getAsset(matId)
                meshId = None # XXX check
                self.parse_material(matId, mat, meshId, matIdx)
        except CONNECTION_ERRORS:
            if retries > 0:
                return self.import_material(matId, matIdx, retries-1)
        return bmat

    def create_material_fromimage(self, matId, data, meshId, matIdx):
        pars = (matId, [matId], data)
        dest = self.doTextureDownloadTranscode(pars)
        btex = self.parse_texture(matId, matId, dest)

        ogremat = OgreMaterial()
        ogremat.name = matId
        ogremat.btex = btex
        ogremat.uuid = matId

        ogremat.layers['baseMap'] = matId
        ogremat.textures.append(matId)
        bmat = self.create_blender_material(ogremat, {"name":matId}, meshId, matIdx)
        #self._imported_assets[matId] = bmat


    def parse_material(self, matId, mat, meshId, matIdx):
        ogremat = OgreMaterial(mat)
        ogremat.btex = None
        ogremat.uuid = matId
        self._imported_ogre_materials[ogremat.name] = ogremat
        bmat = self.create_blender_material(ogremat, mat, meshId, matIdx)
        #self._imported_assets[matId] = bmat

    def import_mesh(self, scenegroup):
        """
        Import mesh object from opensim scene.
        """
        logger.debug(("mesh", scenegroup["asset"]))
        if scenegroup["asset"] in self._imported_assets:
            return self._imported_assets[scenegroup["asset"]]
        asset = self.gridinfo.getAsset(scenegroup["asset"])
        if not asset["type"] == str(AssetType.OgreMesh):
            logger.debug("("+asset["type"]+")")
            return
        materials = []
        if "materials" in scenegroup:
            materials = scenegroup["materials"]
        mesh = self.create_mesh_frombinary(scenegroup["asset"], asset["name"], asset["data"])
        return self.create_mesh_fromomesh(scenegroup["asset"], asset["name"],
                                          mesh, materials)

    def create_mesh_frombinary(self, meshId, meshName, data):
        mesh = oimporter.parse(data)
        return mesh

    def create_mesh_fromomesh(self, meshId, meshName, mesh, materials=[]):
        if not mesh:
            logger.error("error loading",meshId)
            return
        is_new = False
        try:
            new_mesh = bpy.data.meshes[meshName+meshId]
        except:
            new_mesh = bpy.data.meshes.new(meshName+meshId)
            is_new = True
        if not is_new:
            if bversion == 3:
                new_mesh.name = "tobedeleted"
                new_mesh = bpy.data.meshes.new(meshName+meshId)
            else:
                new_mesh.faces.delete(1, range(len(new_mesh.faces)))
                new_mesh.verts.delete(1, range(len(new_mesh.verts)))
                new_mesh.materials = []

        if materials:
            self.setMeshMaterials(new_mesh, materials)

        self._imported_assets[meshId] = new_mesh
        idx = 0
        for vertex, vbuffer, indices, materialName in mesh:
            self.import_submesh(meshId, new_mesh, vertex, vbuffer, indices,
                                materialName, idx, materials)
            idx += 1
        return new_mesh

    def import_object(self, scenegroup, new_mesh, materials=None, offset_x=128.0, offset_y=128.0,
                      offset_z=20.0):
        """
        Import object properties and create the blender mesh object.
        """
        logger.debug("import_object")
        pos = parse_vector(scenegroup["position"])
        scale = parse_vector(scenegroup["scale"])



        obj = self.getcreate_object(scenegroup["id"], scenegroup["asset"], new_mesh)

        if not scenegroup['groupid'] == '00000000-0000-0000-0000-000000000000':
            parent = self.findWithUUID(scenegroup['groupid'])
            if not parent:
                # XXX should register
                pass
            else:
                obj.parent = parent

        self.apply_position(obj, pos)
        self.apply_rotation(obj, parse_vector(scenegroup["rotation"]))
        self.apply_scale(obj, scale)
        self.set_uuid(obj, str(scenegroup["id"]))


        # new_mesh properties have to be set here otherwise blender
        # can crash!!
        self.set_uuid(new_mesh, str(scenegroup["asset"]))
        if materials:
            if bversion == 3:
                for mat in materials:
                    new_mesh.materials.append(mat)
            else:
                new_mesh.materials = materials
        scene = self.get_current_scene()
        try:
            if hasattr(obj, '_obj'):
                scene.objects.link(obj._obj)
            else:
                scene.objects.link(obj)
        except RuntimeError:
            pass # object already in scene
        editor.set_loading_state(obj, 'OK')
        #new_mesh.update()
        #obj.makeDisplayList()
        #new_mesh.hasVertexColours(True) # for now we create them as blender does

        return obj

    def import_group(self, groupid, scenegroup, retries,
                     offset_x=128.0, offset_y=128.0, offset_z=20.0,
                     load_materials=True):
        """
        Import the given group into blender.
        """
        materials = []
        if load_materials and "materials" in scenegroup:
           for idx, material in enumerate(scenegroup["materials"].keys()):
                if not material == "00000000-0000-0000-0000-000000000000":
                    bmat = self.import_material(material, idx, 10)
                    materials.append(bmat)

        try:
            new_mesh = None
            scenegroup["id"] = groupid
            if scenegroup["asset"] and not scenegroup["asset"] == "00000000-0000-0000-0000-000000000000":
                new_mesh = self.import_mesh(scenegroup)

            if new_mesh:
                sys.stderr.write(".")
                sys.stderr.flush()
                obj = self.import_object(scenegroup, new_mesh, materials, offset_x, offset_y,
                                         offset_z)
                self.queueRedraw(immediate=True)
                return obj
        except CONNECTION_ERRORS:
            if retries > 0:
                sys.stderr.write("_")
                sys.stderr.flush()
                return self.import_group(groupid, scenegroup, retries-1)
            else:
                traceback.print_exc()
                sys.stderr.write("!"+scenegroup["asset"])
                sys.stderr.flush()

    def check_uuid(self, obj, groupid):
        """
        Check if the given object has the given groupid.
        """
        if self.get_uuid(obj) == groupid:
            return True

    def get_uuid(self, obj):
        """
        Get the uuid from the given object.
        """
        if "opensim" in obj.properties:
            if "uuid" in obj.properties["opensim"]:
                return obj.properties['opensim']['uuid']

    def set_uuid(self, obj, obj_uuid):
        """
        Set the uuid for the given blender object.
        """
        if not "opensim" in obj.properties:
            obj.properties["opensim"] = {}
        obj.properties["opensim"]["uuid"] = str(obj_uuid)

    def check_group(self, groupid, scenegroup):
        """
        Run a check on the group, to see if it exists in blender.
        """
        if self.find_with_uuid(groupid, bpy.data.objects, "objects"):
            self._found["objects"] += 1
        self._total_server["objects"] += 1
        if self.find_with_uuid(scenegroup["asset"], bpy.data.meshes, "meshes"):
            self._found["meshes"] += 1
        self._total_server["meshes"] += 1

    def check_region(self, region_id, action="check"):
        """
        Run a check on the region, Checks correspondence of objects between
        Blender and OpenSim and returns a formatted result as an array.
        """
        self.init_structures()
        con = SimConnection()
        con.connect(self.gridinfo._url)
        scenedata = con._con.ogrescene_list({"RegionID":region_id})
        total = 0
        total_yes = 0
        for groupid, scenegroup in scenedata['res'].items():
            if getattr(self, action+"_group")(groupid, scenegroup):
                total_yes += 1
            total += 1
        report = []
        report.append("--. \n")
        report.append("total objects %s. \n"%(total,))
        for key in self._found.keys():
            report.append("total "+key+" %s. \n"%(self._total_server[key],))
            report.append(key+" in blend %s\n"%(self._found[key],))
        return report

    def sync_region(self, region_id):
        """
        Sync the given region. Downloads information for the given objects from
        opensim.
        """
        self.init_structures()
        con = SimConnection()
        con.connect(self.gridinfo._url)
        scenedata = con._con.ogrescene_list({"RegionID":region_id})["res"]
        objects = editor.getSelected()
        if not objects:
            objects = bpy.data.objects
        for obj in objects:
            obj_uuid = str(self.get_uuid(obj))
            if obj_uuid:
                if obj_uuid in scenedata:
                    self.import_group(obj_uuid, scenedata[obj_uuid], 10)

    def import_region(self, region_id, action="import"):
        """
        Import the given region into blender.
        """
        self.init_structures()
        con = SimConnection()
        con.connect(self.gridinfo._url)
        scenedata = con._con.ogrescene_list({"RegionID":region_id})
        for groupid, scenegroup in scenedata['res'].items():
            getattr(self, action+"_group")(groupid, scenegroup, 10)
            self.queueRedraw('VIEW3D')

    def _unapply_position(self, pos, offset_x=128.0, offset_y=128.0,
                       offset_z=20.0):
        return [pos[0]+offset_x, pos[1]+offset_y, pos[2]+offset_z]

    def _apply_position(self, pos, offset_x=128.0, offset_y=128.0,
                       offset_z=20.0):
        return (pos[0]-offset_x, pos[1]-offset_y, pos[2]-offset_z)

if __name__ == '__main__':
    base_url = "http://127.0.0.1:9000"
    gridinfo = GridInfo()
    gridinfo.connect(base_url, "caedes caedes", "XXXXXX")
    logger.debug(gridinfo.getGridInfo()["gridnick"])
    regions = gridinfo.getRegions()
    for id in regions:
        region = regions[id]
        logger.debug((" *", region["name"], region["x"], region["y"], id))
    importer = Importer(gridinfo)
    importer.import_region(id)


