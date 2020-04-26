import socket


from xsens_mocap.xsens_data import XSensHeader, XSensQuatSegment, XSensMessage

class MvnStreamReader():
    """
    This is the abstract meta class for all incoming network streams from MVN studio.
    
    
    """
    def __init__(self,ip='127.0.0.1',port=9763):
        self._udp_ip = ip

        self._udp_port = port


    def connect(self):
        print('binding socket')
        self._sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self._sock.bind((self._udp_ip,self._udp_port))
        print('done')


    def get_message(self):
        recv_data =  self._sock.recv(4096)
        header  = XSensHeader(recv_data)
        #header  = XSensHeader(recv_data[:25])####TEST this line
        segments = []
        current_position = 25
        for n in range(header.number_of_items):
             segments.append(XSensQuatSegment(recv_data[current_position:]))
             #segments.append(XSensQuatSegment(recv_data[current_position:current_position+32])) ##TODO test this line
             current_position += 32
        return XSensMessage(header, segments)
        
        
    def read_data(self):
        recv_data = self.get_message()
        header = recv_data.header
        if header.isQuaternion():
            self.handle_quaternion(recv_data)
        elif header.isEuler():
            self.handle_euler(recv_data)
        elif header.isPointData():
            self.handle_pointData(recv_data)
        elif header.isMotionGridData():
            self.handle_motionGridData(recv_data)
        elif header.isScaleInfo():
            self.handle_scaleInfo(recv_data)
        elif header.isPropInfo():
            self.handle_propInfo(recv_data)
        elif header.isMetaData():
            self.handle_metaData(recv_data)
        else:
            print("FATAL ERROR: this should never happen\n continue anyway :P")


    def handle_quaternion(self,data):
        return


    def handle_euler(self,data):
        return


    def handle_pointData(self,data):
        return


    def handle_motionGridData(self,data):
        return


    def handle_scaleInfo(self,data):
        return


    def handle_propInfo(self,data):
        return


    def handle_metaData(self,data):
        return


    def clean_up(self):
        print("count: "+self.count)
