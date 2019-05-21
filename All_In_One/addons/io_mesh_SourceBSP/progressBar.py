import time, sys

# def update_progress(job_title, progress):
#     length = 20 # modify this to change the length
#     block = int(round(length*progress))
#     msg = "\r{0}: [{1}] {2}%".format(job_title, "#"*block + "-"*(length-block), round(progress*100, 2))
#     if progress >= 1: msg += " DONE\r\n"
#     sys.stdout.write(msg)
#     sys.stdout.flush()
#
# # Test
# for i in range(100):
#     time.sleep(0.1)
#     update_progress("Some job", i/100.0)
# update_progress("Some job", 1)
from typing import Tuple


class Progress_bar:


    def __init__(self,desc,max_,len_):
        self.len = len_
        self.max = max_
        self.desc = desc
        self.curr = 0

    def increment(self,val):
        self.curr+=val

    @property
    def state(self):
        return self.curr,self.max

    @property
    def isDone(self):
        return self.curr>=self.max

    @property
    def asPercent(self):
        return (self.curr/self.max)*100

    @property
    def asFloat(self):
        return self.curr / self.max


    def draw(self):
        if self.isDone:
            sys.stdout.write('\r')
            bar = '{name}  [{progress}] {curr}/{max} Done    '.format(name=self.desc, progress='#' * round(
                self.len * self.asFloat) + ' ' * round(self.len * (1 - self.asFloat)), curr=self.curr, max=self.max)
            sys.stdout.write(bar)
            sys.stdout.write('\n')

        else:
            sys.stdout.write('\r')
            bar = '{name}  [{progress}] {curr}/{max} {percent:4}%   '.format(name=self.desc, progress='#' * round(
                self.len * self.asFloat) + ' ' * round(self.len * (1 - self.asFloat)), curr=self.curr, max=self.max,
                                                                          percent=round(self.asPercent, 2))

            sys.stdout.write(bar)
        sys.stdout.flush()




if __name__ == '__main__':
    a = Progress_bar(desc ='Importing vertex indexes' ,max_ =100,len_=20)
    a2 = Progress_bar(desc ='Generating model' ,max_ =100,len_=20)
    while not a2.isDone:
        if a.isDone:
            a2.increment(1)
            a2.draw()
        else:
            a.increment(1)
            a.draw()
        time.sleep(0.02)
