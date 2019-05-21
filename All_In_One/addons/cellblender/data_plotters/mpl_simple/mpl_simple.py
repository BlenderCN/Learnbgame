#!/usr/bin/env python

import sys
import numpy
import scipy
import pylab
import matplotlib as mpl
import matplotlib.pyplot as plt

if (__name__ == '__main__'):

    if (len(sys.argv) < 2):
        print('')
        print('\nUsage: %s f1 [f2 [f3 [...]]] ' % (sys.argv[0]))
        print('          Plot all listed files using simple defaults.')
        print('')
        exit(1)

    mpl.rcParams['figure.facecolor'] = 'white'

    fig = plt.figure()
    fig.suptitle('Reaction Data', fontsize=18.5)
    ax = fig.add_subplot(111)
    ax.spines['top'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.set_xlabel(r'Time (s)')
    ax.set_ylabel(r'Count')

    for i in range(1, len(sys.argv)):
        filename = sys.argv[i]
        print('Plotting %s' % (filename))
        data = numpy.fromfile(sys.argv[i],sep=' ')
        x = data[0::2]
        y = data[1::2]
        ax.plot(x, y, label=filename)

    ax.legend()

    plt.show()
