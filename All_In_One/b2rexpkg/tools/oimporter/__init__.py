"""
Ogre Importer
"""

import sys
import struct
if sys.version_info[0] == 2:
    from StringIO import StringIO
else:
    from io import BytesIO as StringIO
from  .oserializer import Serializer
from .otypes import MeshChunkID, MeshCids, GeomCids, SubMeshCids

import logging
logger = logging.getLogger("b2rex.oimporter")

class MeshImporter(oserializer.Serializer):
    """
    Mesh Reader
    """
    def ReadGeometryVertexElement(self, reader):
        """
        Read a Geometry Vertex Element.
        """
        source = self.ReadShort(reader)
        VertexElementType = self.ReadShort(reader)
        semantic = self.ReadShort(reader)
        offset = self.ReadShort(reader)
        index = self.ReadShort(reader)
        return [source, offset, VertexElementType, semantic, index]

    def ReadGeometryVertexBuffer(self, reader, vertexCount):
        """
        Read a Geometry Vertex Buffer.
        """
        bindIdx = self.ReadShort(reader)
        vertexSize = self.ReadShort(reader)
        cid = self.ReadChunk(reader)
        if cid != MeshChunkID.GeometryVertexBufferData:
            raise Exception("Missing vertex buffer data")
        return self.ReadBytes(reader, vertexSize*vertexCount)

    def ReadGeometryVertexDeclaration(self, reader):
        """
        Read a Geometry Vertex Declaration.
        """
        vertex = []
        if not self.IsEOF(reader):
            cid = self.ReadChunk(reader)
            while cid in [MeshChunkID.GeometryVertexElement] and not self.IsEOF(reader):
                if cid == MeshChunkID.GeometryVertexElement:
                    vertex.append(self.ReadGeometryVertexElement(reader))
                if not self.IsEOF(reader):
                    cid = self.ReadChunk(reader)
            if not self.IsEOF(reader):
                self.Seek(reader, -self.ChunkOverheadSize)
        return vertex

    def ReadGeometry(self, reader):
        """
        Read a Geometry Declaration.
        """
        vertexStart = 0
        vertexCount = self.ReadInt(reader)
        vertex = None
        vbuffer = None
        if not self.IsEOF(reader):
            cid = self.ReadChunk(reader)
            while cid in GeomCids and not self.IsEOF(reader):
                if cid == MeshChunkID.GeometryVertexDeclaration:
                    vertex = self.ReadGeometryVertexDeclaration(reader)
                elif cid == MeshChunkID.GeometryVertexBuffer:
                    vbuffer = self.ReadGeometryVertexBuffer(reader, vertexCount)
                if not self.IsEOF(reader):
                    cid = self.ReadChunk(reader)
            if not self.IsEOF(reader):
                self.Seek(reader, -self.ChunkOverheadSize)
        return vertex, vbuffer

    def ReadSubMesh(self, reader):
        """
        Read a SubMesh Declaration.
        """
        cid = None
        materialName = self.ReadString(reader)
        useSharedVertices = self.ReadBool(reader)
        indexCount = self.ReadInt(reader)
        idx32bit = self.ReadBool(reader)
        vertex = None
        vbuffer = None
        if idx32bit:
            indices = int(self.ReadInts(reader, indexCount))
        else:
            indices = self.ReadShorts(reader, indexCount)
        if not useSharedVertices:
            cid = self.ReadChunk(reader)
            if cid != MeshChunkID.Geometry:
                raise Exception("Missing geometry data")
            vertex, vbuffer = self.ReadGeometry(reader)
        else:
            vertex = vertex = self.vertex
            vbuffer = self.vbuffer
            logger.debug("shared!")
        cid = self.ReadChunk(reader)
        while not self.IsEOF(reader) and cid in SubMeshCids:
            if cid == MeshChunkID.SubMeshOperation:
                #sys.stderr.write("o")
                #sys.stderr.flush()
                self.ReadShort(reader)
            elif cid == MeshChunkID.SubMeshBoneAssignment:
                self.ReadInt(reader)
                self.ReadUShort(reader)
                self.ReadFloat(reader)
            if not self.IsEOF(reader):
                cid = self.ReadChunk(reader)
        if not self.IsEOF(reader):
            self.Seek(reader, -self.ChunkOverheadSize)
        return vertex, vbuffer, indices, materialName

    def ReadMesh(self, reader):
        """
        Read a Mesh Declaration.
        """
        SkelAnimed = self.ReadBool(reader)
        cid = self.ReadChunk(reader)
        submeshes = []
        while cid in MeshCids and not self.IsEOF(reader):
            if cid == MeshChunkID.SubMesh:
                #sys.stderr.write("s")
                submeshes.append(self.ReadSubMesh(reader))
            elif cid == MeshChunkID.Geometry:
                #sys.stderr.write("g")
                vertex, vbuffer = self.ReadGeometry(reader)
                self.vertex = vertex
                self.vbuffer = vbuffer
            else:
                #print("unhandled chunk", cid)
                #sys.stderr.write("i")
                self.IgnoreCurrentChunk(reader)
            cid = self.ReadChunk(reader)
        if not self.IsEOF(reader):
            self.Seek(reader, -self.ChunkOverheadSize)
        return submeshes

    def ParseData(self, data):
        """
        Parse the given raw ogre mesh data into python.
        """
        reader = StringIO(data)
        meshes = []
        if self.ReadShort(reader) == MeshChunkID.Header:
            fileVersion = self.ReadString(reader)
            while not self.IsEOF(reader):
                try:
                    cid = self.ReadChunk(reader)
                except:
                    print("hit end of file while reading!!")
                    if meshes:
                        return meshes[0]
                if cid == MeshChunkID.Mesh:
                    meshes.append(self.ReadMesh(reader))
                else:
                    # print("ignoring", cid)
                    self.IgnoreCurrentChunk(reader)
                    #else:
                        #print "incorrect cid", cid
        else:
            #raise Exception("no header found")
            pass
        if meshes:
            return meshes[0]
       
def parse(data):
    """
    Parse the given raw ogre mesh data into python.
    """
    serializer = MeshImporter()
    return serializer.ParseData(data)

