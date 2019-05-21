import time

class SimpleProfiler:
    def __init__(self, printOutput):
        self.startTimes = {}
        self.printOutput = printOutput
    
    # starts a clock of the given name
    def start(self, name):
        self.startTimes[name] = time.clock()
        if self.printOutput:
            print("Start: {}".format(name))
    
    # stop the clock of the given name and returns its value, or -1 if no such clock exists.
    def stop(self, name):
        if name not in self.startTimes:
            return -1
        timeTaken = time.clock() - self.startTimes[name]
        del self.startTimes[name]
        if self.printOutput:
            print("Done: {} - time taken: {:.3f}s".format(name, timeTaken))
        return timeTaken
