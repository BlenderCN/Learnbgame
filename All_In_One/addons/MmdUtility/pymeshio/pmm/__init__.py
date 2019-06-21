# coding: utf-8
"""
========================
MikuMikuDance PMM format
========================

file format
~~~~~~~~~~~
http://v-nyappon.net/?m=diary&a=page_detail&target_c_diary_id=979053

"""
from .. import common


class BaseFrame(common.Diff):
    __slots__=[
            'next_frame_index',
            'prev_frame_index',
            'frame_number',
            'frame_index',
            ]
    def __init__(self, frame_index):
        self.frame_index=frame_index

    def __str__(self):
        return "<%s [%d] %d frame, [%d]<- ->[%d]>" % (
                self.__class__.__name__,
                self.frame_index, self.frame_number, 
                self.prev_frame_index, 
                self.next_frame_index)


class BoneFrame(BaseFrame):
    __slots__=[
            'pos',
            'rot',
            ]
    def __init__(self, frame_index):
        super(BoneFrame, self).__init__(frame_index)


class Bone(common.Diff):
    __slots__=[
            'frames',
            'index',
            ]
    def __init__(self, index):
        self.index=index
        self.frames=[]

    def __str__(self):
        return "<Bone "+",".join((str(f) for f in self.frames))+">"


class MorphFrame(BaseFrame):
    def __init__(self, frame_index):
        super(MorphFrame, self).__init__(frame_index)


class StateFrame(BaseFrame):
    __slots__=[
            'is_visible',
            'ik_enables',
            'is_selected',
            ]
    def __init__(self, frame_index):
        super(StateFrame, self).__init__(frame_index)


class CameraFrame(BaseFrame):
    __slots__=[
            'pos',
            'rot',
            ]
    def __init__(self, frame_index):
        super(CameraFrame, self).__init__(frame_index)


class LightFrame(BaseFrame):
    __slots__=[
            ]
    def __init__(self, frame_index):
        super(LightFrame, self).__init__(frame_index)


class Model(common.Diff):
    __slots__=[
            'name',
            'path',
            'bones',
            ]
    def __init__(self):
        self.bones=[]

    def __str__(self):
        print(self.name, len(self.name))
        print(self.path, len(self.path))
        return u"<pmm.Model %s:%s>" % (self.name, self.path)

    def get_next_bone_by_next_frame_index(self, frame_index):
        for b in self.bones:
            for f in b.frames:
                if f.next_frame_index==frame_index:
                    return b


class Project(common.Diff):
    __slots__=[
            'path',
            'screen_width',
            'screen_height',
            'timelineview_width',
            'is_camera_mode',
            'models',
            'gravity',
            ]
    def __init__(self):
        self.models=[]


