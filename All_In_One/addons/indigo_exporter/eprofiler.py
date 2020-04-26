import timeit
from functools import reduce
from collections import OrderedDict

instances = OrderedDict()

class eProfiler:
    def __init__(self, name):
        self.start_time = None
        self.elapsed = 0
        self.count = 0
        
    def run(self):
        self.start_time = timeit.default_timer()
        self.count += 1
        return self
    
    def stop(self):
        self.elapsed += timeit.default_timer() - self.start_time
        return self

def start(name):
    if name in instances:
        return instances[name].run()
    
    prof = instances[name] = eProfiler(name).run()
    return prof
                
def results():
    def secondsToStr(t):
        return "%d:%02d:%02d.%03d" % \
            reduce(lambda ll,b : divmod(ll[0],b) + ll[1:],
                [(t*1000,),1000,60,60])
                
    str = "\n# Profiling:\n"
    for key, ins in instances.items():
        str += "# {:<25}: {} {}\n".format(key, secondsToStr(ins.elapsed), ins.count)
    print(str)
        
        
def reset():
    instances.clear()
    
if __name__ == "__main__":
    e = start('outside')

    for i in range(500000):
        ee = start('inside')
        # code
        ee.stop()

    e.stop()
    results()