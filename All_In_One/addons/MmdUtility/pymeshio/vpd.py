# coding: utf-8
###############################################################################
# VPD
###############################################################################
class LineLoader(object):
    """
    行指向の汎用ローダ
    """
    __slots__=['path', 'io', 'end']
    def __str__(self):
        return "<%s current:%d, end:%d>" % (
                self.__class__, self.getPos(), self.getEnd())

    def getPos(self):
        return self.io.tell()

    def getEnd(self):
        return self.end

    def readline(self):
        return (self.io.readline()).strip()

    def isEnd(self):
        return self.io.tell()>=self.end

    def load(self, path, io, end):
        self.path=path
        self.io=io
        self.end=end
        return self.process()

    def process(self):
        """
        dummy. read to end.
        """
        while not self.isEnd():
            self.io.readline()
        return True


class VPDLoader(LineLoader):
    __slots__=['pose']
    def __init__(self):
        super(VPDLoader, self).__init__()
        self.pose=[]

    def __str__(self):
        return "<VPD poses:%d>" % len(self.pose)

    def process(self):
        if self.readline()!="Vocaloid Pose Data file":
            return

        RE_OPEN=re.compile('^(\w+){(.*)')
        RE_OSM=re.compile('^\w+\.osm;')
        RE_COUNT=re.compile('^(\d+);')

        bone_count=-1
        while not self.isEnd():
            line=self.readline()
            if line=='':
                continue
            m=RE_OPEN.match(line)
            if m:
                if not self.parseBone(m.group(2)):
                    raise Exception("invalid bone")
                continue

            m=RE_OSM.match(line)
            if m:
                continue

            m=RE_COUNT.match(line)
            if m:
                bone_count=int(m.group(1))
                continue

        return len(self.pose)==bone_count

    def parseBone(self, name):
        bone=MotionData(name)
        self.pose.append(bone)
        bone.pos=Vector3(*[float(token) for token in self.readline().split(';')[0].split(',')])
        bone.q=Quaternion(*[float(token) for token in self.readline().split(';')[0].split(',')])
        return self.readline()=="}"


