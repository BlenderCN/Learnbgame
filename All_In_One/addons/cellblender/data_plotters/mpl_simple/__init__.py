import os
import subprocess
import sys
import shutil


def get_name():
    return("Simple Plotter")


def requirements_met():
    ok = True
    required_modules = ['matplotlib', 'matplotlib.pyplot', 'pylab', 'numpy',
                        'scipy']
    python_command = shutil.which("python", mode=os.X_OK)
    if python_command is None:
        print("  Python is needed for \"%s\"" % (get_name()))
        ok = False
    else:
        import_test_program = ''
        for plot_mod in required_modules:
            import_test_program = import_test_program + 'import %s\n' % (plot_mod)
        
        import_test_program = import_test_program + 'print("Found=OK")\n'
        process = subprocess.Popen(
            [python_command, '-c', import_test_program],
            shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        process.poll()
        output = process.stdout.readline()
        strout = str(output)
        if (strout is not None) & (strout.find("Found=OK") >= 0):
            # print("  ", plot_mod,
            #       "is available through external python interpreter")
            pass
        else:
            print("  One or more equired modules " + required_modules + 
                  " are not available through the external python interpreter")
            ok = False
    return ok


def plot(data_path, plot_spec):
    program_path = os.path.dirname(__file__)
    # print("Simple Plotter called with %s, %s" % (data_path, plot_spec))
    # print("Plotter-specific files are located here: %s" %(program_path))

    # mpl_simple.py expects plain file names so translate:

    python_cmd = shutil.which("python", mode=os.X_OK)
    plot_cmd = []
    plot_cmd.append(python_cmd)

    if plot_cmd is None:
        print("Unable to plot: python not found in path")
    else:
        plot_cmd.append(os.path.join(program_path, "mpl_simple.py"))
        for generic_param in plot_spec.split():
            if generic_param[0:2] == "f=":
                plot_cmd.append(generic_param[2:])
        print ( "Plotting from: " + data_path )
        print ( "Plot Command:  " + " ".join(plot_cmd) )
        pid = subprocess.Popen(plot_cmd, cwd=data_path)
