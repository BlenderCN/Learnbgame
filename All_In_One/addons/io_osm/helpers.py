# Class: Debugger
# Prints debugging information and optionally logs them to a file.
class Debugger():
    # Property: log
    # bool - Set to True to enable logfile. Default is False.
    log = False

    # Constructor: __init__
    def __init__(self):
        pass

    # Method: start
    # Starts the debugger and creates a log file, if logging is enabled.
    #
    # Parameters:
    #   bool log - Set True if log file should be written, else False
    def start(self,log):
        import time
        import os
        import bpy
#        import sys
#        import logging

        self.log = log

        if self.log:
            (name,ext) = os.path.splitext(bpy.context.blend_data.filepath)
            dir = os.path.dirname(bpy.context.blend_data.filepath)
            self.logfile = os.path.join(dir,name+'_'+time.strftime("%y-%m-%d-%H-%M-%S")+'_debugger.log')

            # touch the file
            file = open(self.logfile,"w");
            file.close()

    # Method: write
    # Writes a message to the logfile.
    #
    # Parameters:
    #   string msg - The message to write.
    def write(self,msg):
        file = open(self.logfile,"a")
        #file.seek(1,os.SEEK_END)
        file.write(msg)
        file.close()

    # Method: debug
    # Prints out a message and also writes it to the logfile if logging is enabled.
    #
    # Parameters:
    #   string msg - The message to output.
    def debug(self,msg):
        print(msg)
        if self.log:
            self.write(msg+"\n")

    # Method: end
    # Ends the debugging session.
    def end(self):
        self.log = False
        

# Class: Profiler
# Stores profiling information of processes.
class Profiler():
    # Property: times
    # dict of stored times used internally.
    times = {}
    startTime = 0
    endTime = 0

    # Constructor: __init__
    def __init__(self):
        self.startTime = 0
        self.endTime = 0
        self.times = {}

    # Method: def
    # Starts profiling of a process. If the process has already started profiling, the process counter will be increased.
    #
    # Parameters:
    #   string name - Name of the process.
    def start(self,name):
        from time import time

        if self.startTime==0:
            self.startTime = time()

        if name in self.times:
            if self.times[name][3]:
                self.times[name][0] = time()
                self.times[name][3] = False

            self.times[name][2]+=1
        else:
            self.times[name] = [time(),0.0,1,False,name,0.0]

    # Method: end
    # Ends profiling of a process.
    #
    # Parameters:
    #   string name - Name of the process.
    def end(self,name):
        from time import time

        if name in self.times:
            self.times[name][1]+=time()-self.times[name][0]
            self.times[name][3] = True

    # Method: getTime
    # Returns the time and call number for a process.
    #
    # Parameters:
    #   string name - Name of the process.
    #
    # Returns:
    #   string - Information about the the process.
    def getTime(self,name):
        return '%s: %6.4f sec (calls: %d)' % (name,self.times[name][1],self.times[name][2])

    # Method: getTimes
    # Returns the times and call numbers of all processes. Uses <getTime> internally.
    #
    # Returns:
    #   string - Information about the processes.
    def getTimes(self):
        from time import time
        import operator
        
        self.endTime = time()
        total = self.endTime - self.startTime
        tf = 1/total
        _times = ''

        unsorted_times = []

        for name in self.times:
            self.times[name][5] = self.times[name][1]*tf
            unsorted_times.append(self.times[name])

        sorted_times = sorted(unsorted_times,key=operator.itemgetter(5))

        for time in sorted_times:
            name = time[4]
            _times+=self.getTime(name)+ ' %3.2f' % (self.times[name][5]*100) + "%\n"

        return _times