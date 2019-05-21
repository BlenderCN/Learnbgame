from struct import unpack

class XSensHeader:
  
  def __init__(self,input):
    #data = unpack('>6sibbib7s','\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    #data = unpack('>6sibbib7s',input[:23])
    self.data = input
    self.id , self.sample_counter , self.datagramm_counter , self.number_of_items , self.time_code , self.avatar_id , self.free = unpack('>6sibbib7s',input[:24])

  def tmp_back(self,data):
    self.id = data[0:5]
    self.sample_counter = data[6:9]
    self.datagramm_counter = data[10]
    self.number_of_items = data[11]
    self.time_code = data[12:15]
    self.avatar_id = data[16]
    self.free = data[17:23]
    
#  def print_header(self):
#    print 'id:\t\t{0}\n'.format(self.id)
#    print 'sample:\t{0}\n'.format(self.sample_counter)
#    print 'datagramms:\t{0}\n'.format(self.datagramm_counter)
#    print 'items:\t\t{0}\n'.format(self.number_of_items)
#    print 'time:\t\t{0}\n'.format(self.time_code)
#    print 'avatar_id:\t\t{0}\n'.format(self.avatar_id)
      
  def isQuaternion(self):
    return self.id[-2:] == '02'

  def isEuler(self):
    return self.id[-2:] == '01'

  def isPointData(self):
    return self.id[-2:] == '03'
  def isMotionGridData(self):
    return self.id[-2:] == '04'
  def isScaleInfo(self):
    return self.id[-2:] == '10'
  def isPropInfo(self):
    return self.id[-2:] == '11'
  def isMetaData(self):
    return self.id[-2:] == '12'
    
  def isSingleDatagram(self):
    return self.datagramm_counter != 0x80

MVN_QUAT_SIZE = 32
class XSensQuatSegment():
  """
  This class represents an XSens Datagram Element
  currently only quaternions are supported
  """
  
  def __init__(self, data):
    """
    """
    self.data = data
    self.id , self.x , self.y , self.z , self.re , self.i , self.j , self.k= unpack('>ifffffff',data[:MVN_QUAT_SIZE])
    self.position = (self.x , self.y , self.z)
    self.quat = ( self.i , self.j, self.k , self.re )
    

class XSensMessage():
  """This class represents a complete XSens message
  """
  
  def __init__(self, header,segments):
    """
    
    Arguments:
    - `header`:
    - `segments`:
    """
    self._header = header
    self._segments = segments
    
  
