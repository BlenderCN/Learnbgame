#!/usr/bin/env python
# Author: Benjamin Brieber


from xsens_mocap.mvn_streamreader import MvnStreamReader


class MvnFileWriter(MvnStreamReader):
    """
    This class can be used to store positions received by a stream from MVN studio to
    binary file
    """
    def __init__(self,output, ip='127.0.0.1',port=9763):
        MvnStreamReader.__init__(self,ip,port)
        self._output = output
        
    
    def handle_quaternion(self,data):
        if len(data) != 760:
            print("wtf")
        self._output.write(data.header)
        for seg in data.segments:
            self._output.write(seg)
        

running = True


def main():
    with open("xsens.xcap",'wb') as output:
        client = MvnFileWriter(output=output, ip='127.0.0.1',port=9763)
        client.connect()
        while running:
            client.read_data()
        client.clean_up()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        running = False
