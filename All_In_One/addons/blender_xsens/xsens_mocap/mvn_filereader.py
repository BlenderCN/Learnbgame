#!/usr/bin/env python

from xsens_mocap.mvn_streamreader import MvnStreamReader
from xsens_mocap.xsens_data import XSensHeader, XSensQuatSegment, XSensMessage

MVN_HEADER_SIZE = 24
MVN_QUAT_SIZE = 32

class MvnFileReader(MvnStreamReader):
  """
  This File allows reading from files instead of a network stream
  """
  
  def __init__(self, filename="xsens.xcap"):
    """Default init function
    
    Arguments:
    - `filename`: The file name from which should be read
    """
    self._filename = filename

  def connect(self):
    self._file = open(self._filename, 'rb')
    self._file.seek(0)
    
  def get_message(self):
    try:
      data = self._file.read(MVN_HEADER_SIZE)
      header = XSensHeader(data)
      segments = []
      for n in range(header.number_of_items):
        segments.append(XSensQuatSegment(self._file.read(MVN_QUAT_SIZE)))
      return XSensMessage(header, segments)
    except:
      return 0

def main():
  reader = MvnFileReader('/home/bender/sim_scripts/xsens_mocap/xsens_session.xcap')
  reader.connect()
  count = 0
  msg = reader.get_message()
  while msg:
    msg = reader.get_message()
    print(count)
    count += 1


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        running = False