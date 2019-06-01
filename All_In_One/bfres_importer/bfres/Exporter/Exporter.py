import logging; log = logging.getLogger(__name__)
import bmesh
import bpy
import bpy_extras
import os
import os.path
import tempfile
import shutil
import struct
import math
from bfres.Exceptions import UnsupportedFileTypeError
from bfres.BinaryFile import BinaryFile
from bfres import YAZ0, FRES, BNTX
#from .ModelImporter import ModelImporter
#from .TextureImporter import TextureImporter


class Exporter:
    def __init__(self, operator, context):
        self.operator = operator
        self.context  = context


    def run(self, path):
        """Perform the export."""
        self.wm   = bpy.context.window_manager
        self.path = path
        log.info("Exporting: %s", path)

        #bpy.context.selected_objects doesn't work, lol
        objects = [o for o in bpy.context.scene.objects if o.select]
        if len(objects) == 0: objects = bpy.context.visible_objects
        if len(objects) == 0:
            raise RuntimeError("No objects selected and no objects visible.")

        self.outFile = open(self.path, 'wb')
        try:
            for i, obj in enumerate(objects):
                log.info("Exporting object %d of %d: %s",
                    i+1, len(objects), obj.name)
                self.exportObject(obj)
        except:
            log.exception("Export FAILED")
        finally:
            self.outFile.close()

        log.info("Export finished.")
        return {'FINISHED'}


    def exportTextures(self, path):
        """Export textures to specified file."""
        self.wm   = bpy.context.window_manager
        self.path = path
        log.info("TEXTURE EXPORT GOES HERE")
        raise NotImplementedError
        return {'FINISHED'}


    def exportObject(self, obj):
        """Export specified object."""
        log.debug("Export object: %s", obj.type)
        if   obj.type == 'MESH': self.exportMesh(obj)
        elif obj.type == 'ARMATURE': self.exportArmature(obj)
        else:
            log.warning("Can't export object of type %s", obj)


    def exportMesh(self, obj):
        """Export a mesh."""
        log.debug("Exporting mesh: %s", obj)
        attrs = self._makeAttrBufferDataForMesh(obj)
        faces = []
        for poly in obj.data.polygons:
            faces.append(list(poly.vertices))
        log.debug("Mesh has %d faces", len(faces))
        data = {
            'attrs': attrs,
            'faces': faces,
            'groupNames': [group.name for group in obj.vertex_groups],
        }
        data = bytes(repr(data), 'utf-8')
        log.debug("Writing %d bytes", len(data))
        self.outFile.write(data)


    def _makeAttrBufferDataForMesh(self, obj):
        """Make the attribute buffer data for a mesh."""
        positions = []
        normals   = []
        texCoords = []
        idxs      = []
        weights   = []

        # make FRES attribute dicts
        attrs = {
            '_i0': idxs,
            '_n0': normals,
            '_p0': positions,
            '_w0': weights,
        }

        # make a list of UV coordinates for each layer
        uvs = obj.data.uv_layers
        numUVs = len(uvs)
        for i in range(numUVs):
            lst = []
            attrs['_u%d' % i] = lst
            texCoords.append(lst)

        # add each vertex to attribute buffers
        for vtx in obj.data.vertices:
            # groups: Weights for the vertex groups this vertex is member of
            # index: Index of this vertex
            # normal: Vertex Normal
            x, y, z = vtx.co
            positions.append((x, y, z))

            nx, ny, nz = vtx.normal
            normals.append((nx, ny, nz))

            if len(vtx.groups) > 4:
                log.warning("Vertex has more than 4 groups: %s, %s",
                    vtx, vtx.groups)
            idx, wgt = [], []
            # export weights sorted from strongest to weakest
            for group in reversed(sorted(vtx.groups, key=lambda g:g.weight)):
                idx.append(group.group)
                wgt.append(group.weight)
            idxs.append(idx)
            weights.append(wgt)

            for uv in range(numUVs):
                u, v = uvs[uv].data[vtx.index].uv
                texCoords[uv].append((u, v))

        return attrs


    def exportArmature(self, obj):
        """Export an armature."""
        # TODO
