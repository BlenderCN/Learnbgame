# coding: utf-8
"""
mqo reader
"""
import io
from .. import mqo
from .. import common


class Reader(common.TextReader):
    """mqo reader
    """
    __slots__=[
            "has_mikoto",
            "materials", "objects",
            ]
    def __init__(self, ios):
        super(Reader, self).__init__(ios)

    def __str__(self):
        return "<MQO %d lines, %d materials, %d objects>" % (
                self.lines, len(self.materials), len(self.objects))

    def readObject(self, name):
        obj=mqo.Obj(name)
        while(True):
            line=self.getline()
            if line==None:
                # eof
                break;
            if line==b"":
                # empty line
                continue

            if line==b"}":
                return obj
            else:
                tokens=line.split()
                key=tokens[0]
                if key==b"vertex":
                    if not self.readVertex(obj):
                        return False
                elif key==b"face":
                    if not self.readFace(obj):
                        return False
                elif key==b"depth":
                    obj.depth=int(tokens[1])
                elif key==b"visible":
                    obj.visible=int(tokens[1])
                else:
                    print(
                            "%s#readObject" % name,
                            "unknown key: %s" % key
                            )

        self.printError("readObject", "invalid eof")
        return False

    def readFace(self, obj):
        while(True):
            line=self.getline()
            if line==None:
                # eof
                break;
            if line==b"":
                # empty line
                continue

            if line==b"}":
                return True
            else:
                # face
                tokens=line.split(b' ', 1)
                try:
                    obj.addFace(mqo.Face(int(tokens[0]), tokens[1]))
                except ValueError as ex:
                    self.printError("readFace", ex)
                    #return False

        self.printError("readFace", "invalid eof")
        return False

    def readVertex(self, obj):
        while(True):
            line=self.getline()
            if line==None:
                # eof
                break;
            if line==b"":
                # empty line
                continue

            if line==b"}":
                return True
            else:
                # vertex
                obj.addVertex(*[float(v) for v in line.split()])

        self.printError("readVertex", "invalid eof")
        return False

    def readMaterial(self):
        materials=[]
        while(True):
            line=self.getline()
            if line==None:
                # eof
                break;
            if line==b"":
                # empty line
                continue

            if line==b"}":
                return materials
            else:
                # material
                secondQuaote=line.find(b'"', 1)                
                material=mqo.Material(line[1:secondQuaote])
                try:
                    material.parse(line[secondQuaote+2:])
                except ValueError as ex:
                    self.printError("readMaterial", ex)

                materials.append(material)

        self.printError("readMaterial", "invalid eof")
        return False

    def readChunk(self):
        level=1
        while(True):
            line=self.getline()
            if line==None:
                # eof
                break;
            if line==b"":
                # empty line
                continue

            if line==b"}":
                level-=1
                if level==0:
                    return True
            elif line.find(b"{")!=-1:
                level+=1

        self.printError("readChunk", "invalid eof")
        return False

    def read(self):
        model=mqo.Model()

        line=self.getline()
        if line!=b"Metasequoia Document":
            print("invalid signature")
            return False

        line=self.getline()
        if line!=b"Format Text Ver 1.0":
            print("unknown version: %s" % line)

        while True:
            line=self.getline()
            if line==None:
                # eof
                break;
            if line==b"":
                # empty line
                continue

            tokens=line.split()
            key=tokens[0]
            if key==b"Eof":
                # success !
                return model
            elif key==b"Scene":
                if not self.readChunk():
                    return
            elif key==b"Material":
                materials=self.readMaterial()
                if not materials:
                    return
                model.materials=materials
            elif key==b"Object":
                firstQuote=line.find(b'"')
                secondQuote=line.find(b'"', firstQuote+1)
                obj=self.readObject(line[firstQuote+1:secondQuote])
                if not obj:
                    return
                model.objects.append(obj)
            elif key==b"BackImage":
                if not self.readChunk():
                    return
            elif key==b"IncludeXml":
                firstQuote=line.find(b'"')
                secondQuote=line.find(b'"', firstQuote+1)
                print("IncludeXml", line[firstQuote+1:secondQuote])
            else:
                print("unknown key: %s" % key)
                if not self.readChunk():
                    return
        # error not reach here
        raise ParseException("invalid eof")


def read_from_file(path):
    """
    read from file path, then return the pymeshio.mqo.Model.

    :Parameters:
      path
        file path
    """
    with io.open(path, 'rb') as ios:
        return read(ios)


def read(ios):
    """
    read from ios, then return the pymeshio.mqo.Model.

    :Parameters:
      ios
        input stream (in io.IOBase)
    """
    assert(isinstance(ios, io.IOBase))
    return Reader(ios).read()

