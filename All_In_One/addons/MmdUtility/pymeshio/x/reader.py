# coding: utf-8
"""
x reader
"""
import io
import re
from .. import common
from .. import x


class Reader(common.TextReader):
    """x reader
    """
    __slots__=[
            'ios',
            'eof',
            'lines',
            'model',
            ]
    def __init__(self, ios):
        super(Reader, self).__init__(ios)

    def getline(self):
        while not self.eof:
            line=super(Reader, self).getline()
            if not line:
                continue
            if line.startswith(b"//"):
                # skip comment line
                continue
            if line==b"":
                # skip empty line
                continue
            return line

    def readHeader(self):
        magic=self.ios.read(4)
        if magic!=b'xof ':
            # invalid magic
            return
        major=self.ios.read(2)
        minor=self.ios.read(2)
        type=self.ios.read(4)
        float_size=self.ios.read(4)
        self.lines+=1
        return magic, major, minor, type, float_size

    def readChunkBody(self):
        # serach close }
        body=[]        
        while not self.eof:
            line=self.getline()

            if line.strip()==b"}":
                break

            body.append(line)

        return b"\r\n".join(body)

    def readHeaderChunkBody(self):
        # serach close }
        while not self.eof:
            line=self.getline().strip()

            if line==b"}":
                break


    def readMeshChunkBody(self):
        ####################
        # vertices
        ####################
        vertex_count=int(self.getline().split(b";")[0].strip())
        print("vertex_count: %d" % vertex_count)
        def get_vertex(line):
            splited=line.split(b";")
            return common.Vector3(
                    float(splited[0]),
                    float(splited[1]),
                    float(splited[2])
                    )

        for _ in range(vertex_count):
            self.model.vertices.append(get_vertex(self.getline()))

        ####################
        # faces
        ####################
        face_count=int(self.getline().split(b";")[0].strip())
        print("face_count: %d" % face_count)
        def get_face(line):
            splited=line.split(b";")
            face_vertex_count=int(splited[0])
            face=[int(i) for i in splited[1].split(b",")]
            assert(face_vertex_count==len(face))
            return face
        for _ in range(face_count):
            self.model.faces.append(get_face(self.getline()))

        # nested chunks
        while not self.eof:
            line=self.getline()
            if not line:
                continue
            line=line.strip()

            if line==b"}":
                return

            assert(line.endswith(b"{"))
            # drop {
            line=line[0:-1].strip()

            splited=line.split()
            print(splited)
            chunk=splited[0]

            if chunk==b"MeshMaterialList":
                self.readMeshMaterialListChunkBody()
            elif chunk==b"MeshNormals":
                self.readNormalChunkBody()
            elif chunk==b"MeshTextureCoords":
                self.readUVChunkBody()
            else:
                raise "unknown chunk !: [%s]" % chunk


    def readMeshMaterialListChunkBody(self):
        material_count=int(self.getline().split(b";")[0].strip())
        print(material_count)
        face_material_count=int(self.getline().split(b";")[0].strip())

        num_p=re.compile(b"\d+")
        def get_face_material(line):
            m=num_p.search(line)
            return int(m.group(0))
        for _ in range(face_material_count):
            self.model.face_materials.append(get_face_material(self.getline()))

        def read_material():
            line=self.getline().strip()
            splited=line.split()
            chunk=splited[0]
            
            assert(chunk==b"Material")
            print(splited[1])

            material=x.Material()

            splited=self.getline().strip().split(b";")
            material.diffuse=common.RGBA(
                    float(splited[0]),
                    float(splited[1]),
                    float(splited[2]),
                    float(splited[3]),
                    )

            splited=self.getline().strip().split(b";")
            material.shininess=float(splited[0])

            splited=self.getline().strip().split(b";")
            material.specular=common.RGB(
                    float(splited[0]),
                    float(splited[1]),
                    float(splited[2])
                    )

            splited=self.getline().strip().split(b";")
            material.emit=common.RGB(
                    float(splited[0]),
                    float(splited[1]),
                    float(splited[2])
                    )
            
            line=self.getline().strip()
            if line.startswith(b"TextureFilename "):
                # todo
                line=self.getline().strip()
                line=self.getline().strip()
                line=self.getline().strip()
                #line=self.getline().strip()

            assert(line==b'}')

        for _ in range(material_count):
            self.model.materials.append(read_material())

        # serach close }
        while not self.eof:
            line=self.getline().strip()

            if line==b"}":
                break

            #print(line)


    def readNormalChunkBody(self):
        # normals
        normal_count=int(self.getline().split(b";")[0].strip())
        #print(normal_count)
        def get_normal(line):
            splited=line.split(b";")
            return common.Vector3(
                    float(splited[0]),
                    float(splited[1]),
                    float(splited[2])
                    )
        for _ in range(normal_count):
            self.model.normals.append(get_normal(self.getline()))

        # face normals
        line=self.getline()
        face_count=int(line.split(b";")[0].strip())
        #print(face_count)
        def get_face(line):
            splited=line.split(b";")
            face_vertex_count=int(splited[0])
            face=[int(i) for i in splited[1].split(b",")]
            assert(face_vertex_count==len(face))
            return face
        for _ in range(face_count):
            self.model.face_normals.append(get_face(self.getline()))

        # serach close }
        while not self.eof:
            line=self.getline().strip()

            if line==b"}":
                break

            print(line)


    def readUVChunkBody(self):
        uv_count=int(self.getline().split(b";")[0].strip())
        #print(uv_count)
        def get_uv(line):
            splited=line.split(b";")
            return common.Vector2(
                    float(splited[0]),
                    float(splited[1])
                    )
        for _ in range(uv_count):
            self.model.uvs.append(get_uv(self.getline()))

        # serach close }
        while not self.eof:
            line=self.getline().strip()

            if line==b"}":
                break

            #print(line)


    def read(self):
        magic, major, minor, type, float_size=self.readHeader()
        if not magic:
            print("no magic number")
            return

        self.model=x.Model()
        while not self.eof:
            line=self.getline()
            if not line:
                continue
            line=line.strip()

            print(line)
            assert(line.endswith(b"{"))
            # drop {
            line=line[0:-1].strip()

            splited=line.split()
            print(splited)
            chunk=splited[0]

            if chunk==b"template":
                body=self.readChunkBody()
                self.model.templates.append(
                        chunk+b" {\r\n"+
                        body+b"\r\n"+
                        b"}\r\n"
                        )
            elif chunk==b"Header":
                self.readHeaderChunkBody()
            elif chunk==b"Mesh":
                self.readMeshChunkBody()
            else:
                raise "unknown chunk !: [%s]" % chunk

        return self.model


def read(ios):
    """
    read from ios, then return the pymeshio.mqo.Model.

    :Parameters:
      ios
        input stream (in io.IOBase)
    """
    assert(isinstance(ios, io.IOBase))
    return Reader(ios).read()


def read_from_file(path):
    """
    read from file path, then return the x.Model.

    :Parameters:
      path
        file path

    >>> import x.reader
    >>> m=x.reader.read_from_file('resources/cube.x')

    """
    with io.open(path, 'rb') as ios:
        return read(ios)

