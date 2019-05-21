import os
import subprocess

def find_in_path(program_name):
    for path in os.environ.get('PATH','').split(os.pathsep):
        full_name = os.path.join(path,program_name)
        if os.path.exists(full_name) and not os.path.isdir(full_name):
            return full_name
    return None


def subdivide ( l, sep ):
  ''' Splits a list into sublists by dividing at (and removing) instances of sep '''
  nl = []
  c = []
  for s in l:
    if s==sep:
      if len(c) > 0:
        nl = nl + [c]
        c = []
    else:
      c = c + [s]
  if len(c) > 0:
    nl = nl + [c]
  return nl



def get_name():
    return ( "Java Plotter" )


def requirements_met():
    # print ( "Checking requirements for java plot" )
    path = find_in_path ( "java" )
    if path == None:
        print ( "Required program \"java\" was not found" )
        return False
    else:
        jarfile = "PlotData.jar"
        plot_path = os.path.dirname(__file__)
        # print ("plot_path = ", plot_path )
        if plot_path == '':
            pass
        else:
            jarfile = os.path.join(plot_path, jarfile)
        # print ("Checking for existence of ", jarfile )
        if os.path.exists ( jarfile ):
            return True
        else:
            print ( "Required file: PlotData.jar was not found" )
            return False


def plot ( data_path, plot_spec ):
    program_path = os.path.dirname(__file__)
    # print ( "Java Plotter called with %s, %s" % (data_path, plot_spec) )
    # print ( "Plotter-specific files are located here: %s" % ( program_path ) )
    
    # Subdivide the plot spec by "page"
    
    plot_spec = subdivide ( plot_spec.split(), "page" )
    color_spec = ""
    
    for page in plot_spec:
    
        # The java program only understands color=#rrggbb and fxy=filename parameters so find "f=":

        found = False
        for generic_param in page:
            if generic_param[0:2] == "f=":
                found = True
                break
        
        # Go through the entire plot command (whether found or not) to set other settings

        java_plot_spec = ""
        for generic_param in page:
            if generic_param[0:2] == "f=":
                java_plot_spec = java_plot_spec + " fxy=" + generic_param[2:]
            elif generic_param[0:7] == "color=#":
                java_plot_spec = java_plot_spec + " color=" + generic_param[7:]

        if found:
            plot_cmd = find_in_path("java")
            plot_cmd = plot_cmd + ' -jar ' + os.path.join ( program_path, 'PlotData.jar' ) + " "
            plot_cmd = plot_cmd + java_plot_spec
            print ( "Plotting from: " + data_path )
            print ( "Plotting with: " + plot_cmd )
            pid = subprocess.Popen ( plot_cmd.split(), cwd=data_path )

