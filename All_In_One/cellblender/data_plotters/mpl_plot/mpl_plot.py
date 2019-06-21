#!/usr/bin/env python

''' Plot files '''

'''
This is the current plan for a simple plotting syntax:

 Basic Command line arguments:
  page : start a new page (new figure)
  plot : start a new plot on a page
  f=name : add file "name" to the current plot

 Additional Command line arguments that apply to all subsequent files until
 over-ridden:

  color=clr : set color
  xaxis=label : set label for x axis
  yaxis=label : set label for y axis
'''

from numpy import *
from scipy import *
from pylab import *
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter


if (len(sys.argv) < 2):
    print('')
    print('\nUsage: %s commands...' % (sys.argv[0]))
    print('  Defines plots via commands:')
    print('    defs=filename        ... Loads default parameters from a python file')
    print('    page                 ... Starts a new page (figure in MatPlotLib)')
    print('    plot                 ... Starts a new plot (subplot in MatPlotLib)')
    print('    color=#rrggbb        ... Selects a color via Red,Green,Blue values')
    print('    color=color_name     ... Selects a color via standard color names')
    print('    title=title_string   ... Sets the title for each plot')
    print('    pagetitle=string     ... Sets the title for each page')
    print('    xlabel=label_string  ... Sets the label for the x axis')
    print('    ylabel=label_string  ... Sets the label for the y axis')
    print('    legend=code          ... Adds a legend with code = 0..10 (-1=none)')
    print('    n=name               ... Name used to over-ride file name in legend')
    print('    f=filename           ... Plots the file with current settings')
    print('')
    exit(1)


def subdivide(l, sep):
    ''' Splits a list into sublists by dividing at (and removing) instances of sep '''
    nl = []
    c = []
    for s in l:
        if s == sep:
            if len(c) > 0:
                nl = nl + [c]
                c = []
        else:
            c = c + [s]
    if len(c) > 0:
        nl = nl + [c]
    return nl


# Get a list of just the parameters (excluding the program name itself)
params = sys.argv[1:]

# Execute the global defaults file (if any) and remove from parameters list

remaining_params = []

for cmd in params:
    if cmd[0:5] == "defs=":
        print("Defaults: " + cmd)
        command = cmd[5:]
        # print "Executing " + command
#        execfile(command)
        exec(open(command).read())
    else:
        remaining_params = remaining_params + [cmd]

params = remaining_params

# Remove any page or plot commands that come before the first file because they will create empty plots

remaining_params = []
found_file = False

for cmd in params:
    if cmd[0:2] == "f=":
        found_file = True
    if found_file or ((cmd != "page") and (cmd != "plot")):
        remaining_params = remaining_params + [cmd]

params = remaining_params


# Separate the commands into a list of lists (one list per page)

pages = subdivide(params, "page")

plot_cmds = []
for page in pages:
    pc = subdivide(page, "plot")
    if len(pc) > 0:
        plot_cmds = plot_cmds + [pc]


# print plot_cmds


# Draw each plot

pagetitle = ""
title = ""
xlabel = ""
ylabel = ""
color = None
legend = -1
name = None

for page in plot_cmds:
    # print "Plotting " + str(page)

    num_plots = len(page)

    print("This figure has " + str(num_plots) + " plots")

    num_cols = math.trunc(math.ceil(math.sqrt(num_plots)))
    num_rows = math.trunc(math.ceil(num_plots*1.0/num_cols))

    print("This figure will be " + str(num_rows) + "x" + str(num_cols))

    fig = plt.figure()
    fig.subplots_adjust(top=0.85)
    fig.subplots_adjust(bottom=0.15)

    row = 1
    col = 1
    plot_num = 1

    for plot in page:
        # print "  Plotting " + str(plot)

        ax = fig.add_subplot(num_rows, num_cols, plot_num)  # (r,c,n): r=num_rows, c=num_cols, n=this_plot_number

        for cmd in plot:
            if cmd[0:4] == "cmd=":
                # print "Command: " + cmd
                command = cmd[4:]
                # print "Executing " + command
                exec(command)
            if cmd[0:5] == "defs=":
                pass
            elif cmd[0:6] == "title=":
                # print "Title command: " + cmd
                title = cmd[6:]
            elif cmd[0:10] == "pagetitle=":
                # print "Page Title command: " + cmd
                pagetitle = cmd[10:]
            elif cmd[0:6] == "color=":
                # print "Color command: " + cmd
                color = cmd[6:]
            elif cmd[0:7] == "xlabel=":
                # print "x label command: " + cmd
                xlabel = cmd[7:]
            elif cmd[0:7] == "ylabel=":
                # print "y label command: " + cmd
                ylabel = cmd[7:]
            elif cmd[0:7] == "legend=":
                # print "legend command: " + cmd
                legend = int(cmd[7:])
            elif cmd[0:6] == "legend":
                # print "legend command: " + cmd
                legend = 0
            elif cmd[0:2] == "n=":
                # print "Name command: " + cmd
                name = cmd[2:]
            elif cmd[0:2] == "f=":
                # print "File command: " + cmd
                fn = cmd[2:]
                # print "    File name = " + fn
                data = fromfile(fn,sep=' ')
                x = data[0::2]
                y = data[1::2]
                if name is None:
                    name = fn
                if color is None:
                    ax.plot(x, y, label=name)
                else:
                    ax.plot(x, y, label=name, c=color)
                name = None
                ax.spines['top'].set_color('none')
                ax.spines['right'].set_color('none')
                ax.xaxis.set_ticks_position('bottom')
                ax.yaxis.set_ticks_position('left')
            else:
                print ( "Unknown command: " + cmd )

        if legend >= 0:
            ax.legend(loc=legend)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        plot_num = plot_num + 1

    fig.suptitle(pagetitle, size=25)

plt.show()
