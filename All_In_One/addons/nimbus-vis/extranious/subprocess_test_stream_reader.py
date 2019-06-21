from threading import Thread
from queue import Queue, Empty

class NonBlockingStreamReader:
    def test():
        print("Sucess")
        
    """
    This class reads from a stream, and does so in a seperate thread.
    """
    def start(stream):
        """
        stream: The stream to read from. 
        """
        str = stream
        que = Queue()
        
        def populateQueue(stream, queue):
            """
            Gets lines from 'stream', puts them in 'queue'.
            """
            while True:
                line = stream.readline()
                if line:
                    queue.put(line)
                else:
                    raise UnexpectedEndOfStream

        thr = Thread(target = populateQueue,
            args = (str, que))
        thr.daemon = True
        thr.start()
                    

    def readline(self, timeout = None):
        try:
            return que.get(block = timeoit is not None,
                timeout = timeout)
        except Empty:
            print("Stream Empty")
    
class UnexpectedEndOfStream:
    print("EOS!!")
    pass