import random
from math import pi, sin
TAU = 2*pi


class SlicedWaveSurfaceGenerator(object):
    """Generate Wave Surface"""
    def __init__(self, numWaves=5, maxFreq=4):
        self.AList = []
        self.kList = []
        self.phiList = []
        for i in range(numWaves):
            phi = TAU*random.random()
            k = (random.randint(-maxFreq, maxFreq),
                 random.randint(-maxFreq, maxFreq))
            A = (random.random() - 0.5) / (numWaves * max(max(k), 1))
            self.AList.append(A)
            self.phiList.append(phi)
            self.kList.append(k)

    def getValue(self, u, v, t=0.0):
        value = 0.0
        for A, k, phi in zip(self.AList, self.kList, self.phiList):
            kx, ky = k
            value += A*sin(TAU*(t + kx*u + ky*v) + phi)

        return value
