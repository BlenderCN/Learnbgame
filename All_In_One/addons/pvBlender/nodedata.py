import bpy
import uuid

_data_dict = {}

class pvData():
    pass

class pvDataNode():
    dataId = bpy.props.StringProperty(default="")
    def init_data(self):
        print("### Running generic init_data ",self.dataId);
    def load_data(self):
        if self.dataId == "":  # no data yet
            self.dataId = str(uuid.uuid1()) + self.name
        if self.dataId not in _data_dict:
            print("[pv:DATA] Create data[",self.dataId,"]")
            self.data = pvData()
            _data_dict[self.dataId] = self.data
            self.init_data()
#        print("[pv:DATA] Getting data[",self.dataId,"]")
        self.data = _data_dict[self.dataId]
        return (self.data)
    def get_data(self):
        if self.dataId == "":  # no data yet
            return None
        if self.dataId not in _data_dict:
            raise IndexError
#        print("[pv:DATA] Getting data[",self.dataId,"]")
        return (_data_dict[self.dataId])
    def free_data(self):
        if self.dataId == "":  # no data yet
            return
        if self.dataId not in _data_dict:
            return
        print("[pv:DATA] Delete data[",self.dataId,"]")
        del _data_dict[self.dataId]
