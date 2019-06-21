# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import os
import subprocess
import sys


# print ( "Top of data_plotters/__init__.py" )


def find_in_path(program_name):
    for path in os.environ.get('PATH','').split(os.pathsep):
        full_name = os.path.join(path,program_name)
        if os.path.exists(full_name) and not os.path.isdir(full_name):
            return full_name
    return None


module_name_list = []
module_list = []

def find_plotting_options():

    plot_path = os.path.dirname(__file__)
    if plot_path == '':
        plot_path = '.'
    # plot_path = os.path.join ( plot_path, "data_plotters" )

    inpath = True
    try:
        if sys.path.index(plot_path) < 0:
            inpath = False
    except:
        inpath = False
    if not inpath:
        # print ( "Appending %s to path"%(plot_path) )
        sys.path.append ( plot_path )


    # print ( "System path = %s" % (sys.path) ) 
    module_name_list = []
    module_list = []

    print ( "Searching for installed plotting plugins in %s"%(plot_path) )

    for f in os.listdir(plot_path):
        if (f != "__pycache__"):
            plot_plugin = os.path.join ( plot_path, f )
            if os.path.isdir(plot_plugin):
                if os.path.exists(os.path.join(plot_plugin,"__init__.py")):
                    # print ( "Adding %s " % (plot_plugin) )
                    import_name = plot_plugin
                    module_name_list = module_name_list + [f]
                    # print ( "Attempting to import %s" % (import_name) )
                    try:
                        plot_module = __import__ ( f )
                        # print ( "Checking requirements for %s" % ( plot_module.get_name() ) )
                        if plot_module.requirements_met():
                            # print ( "System requirements met for Plot Module \"%s\"" % ( plot_module.get_name() ) )
                            module_list = module_list + [ plot_module ]
                        else:
                            print ( "System requirements NOT met for Plot Module \"%s\"" % ( plot_module.get_name() ) )
                        # print ( "Imported __init__.py from %s" % (f) )
                    except:
                        print ( "Directory %s did not contain a working __init__.py file" % (f) )
    return ( module_list )


def print_plotting_options():
    print ( "This functionality has been moved to the individual plotting packages" )

def old_print_plotting_options():
    plot_executables = ['python', 'xmgrace', 'java', 'excel']
    plot_modules = ['matplotlib', 'junkTESTlib', 'matplotlib.pyplot', 'pylab', 'numpy', 'scipy']

    for plot_app in plot_executables:
        path = find_in_path ( plot_app )
        if path != None:
            print ( "  ", plot_app, "is available at", path )
        else:
            print ( "  ", plot_app, "is not found in the current path" )

    for plot_mod in plot_modules:
        try:
            __import__ ( plot_mod )
            print ( "  ", plot_mod, "is importable" )
        except:
            print ( "  ", plot_mod, "is not importable in this configuration" )

    python_command = find_in_path ( "python" )

    for plot_mod in plot_modules:
        import_test_program = 'import %s\nprint("Found=OK")'%(plot_mod)
        #print ( "Test Program:" )
        #print ( import_test_program )
        process = subprocess.Popen([python_command, '-c', import_test_program],
            shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #print ( "Back from Popen" )
        process.poll()
        #print ( "Back from poll" )
        output = process.stdout.readline()
        #print ( "Back from readline" )
        #print ( "  output =", output )
        strout = str(output)
        if (strout != None) & (strout.find("Found=OK")>=0):
            print ( "  ", plot_mod, "is available through external python interpreter" )
        else:
            print ( "  ", plot_mod, "is not available through external python interpreter" )


if __name__ == "__main__":
    print ( "Called with __name__ == __main__" )
    # register()
    pass
