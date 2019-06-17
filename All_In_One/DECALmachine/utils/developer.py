import os
import time


chronicle = []


class Benchmark():
    def __init__(self, do_benchmark):
        if do_benchmark:
            os.system("clear")
        self.do_benchmark = do_benchmark
        self.start_time = self.time = time.time()
        self.chronicle = []

    def measure(self, name=""):
        if self.do_benchmark:
            t = time.time() - self.time
            self.time += t
            self.chronicle.append(t)

            global chronicle
            if chronicle:
                diff = self.chronicle[-1] - chronicle[len(self.chronicle) - 1]
                diff = "+ %.6f" % diff if diff > 0 else ("%.6f" % diff).replace("-", "- ")

                print("--- %f (%s) - %s" % (t, diff, name))
            else:
                print("--- %f - %s" % (t, name))

    def total(self):
        if self.do_benchmark:
            t = time.time() - self.start_time
            self.chronicle.append(t)

            global chronicle
            if chronicle:
                diff = self.chronicle[-1] - chronicle[len(self.chronicle) - 1]
                diff = "+ %.6f" % diff if diff > 0 else ("%.6f" % diff).replace("-", "- ")

                print("  » %f (%s) - %s" % (t, diff, "total"))
            else:
                print("  » %f - %s" % (t, "total"))

            chronicle = self.chronicle
