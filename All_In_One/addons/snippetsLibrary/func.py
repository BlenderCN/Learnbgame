import bpy
import os
import textwrap


def get_addon_prefs():
    #addon_name = os.path.splitext(os.path.basename(os.path.abspath(__file__)))[0]
    #print ('abspath', os.path.abspath(__file__))
    #print ('file', __file__)
    # -> same as __name__
    #print ('addon_name', addon_name)
    #print('--name--', __name__)
    addon_name = os.path.splitext(__name__)[0]
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[addon_name].preferences
    return (addon_prefs)

def openFolder(folderpath):
    """
    open the folder at the path given
    with cmd relative to user's OS
    """
    from sys import platform
    myOS = platform
    if myOS.startswith('linux') or myOS.startswith('freebsd'):
        # linux
        cmd = 'xdg-open '
        #print("operating system : Linux")
    elif myOS.startswith('win'):
        # Windows
        #cmd = 'start '
        cmd = 'explorer '
        #print("operating system : Windows")
        if not folderpath:
            return('/')
        
    else:#elif myOS == "darwin":
        # OS X
        #print("operating system : MACos")
        cmd = 'open '

    if not folderpath:
        print ('in openFolder : no folderpath !', folderpath)
        return('//')

    #double quote the path to avoid problem with special character
    folderpath = '"' + os.path.normpath(folderpath) + '"'
    fullcmd = cmd + folderpath

    #print & launch open command
    print(fullcmd)
    os.system(fullcmd)


def locateLibrary(justGet=False):
    #addon = bpy.context.preferences.addons.get('snippetsLibrary')
    # print (addon)
    # prefs = addon.preferences
    prefs = get_addon_prefs()
    cust_path = prefs.snippets_custom_path
    cust_fp = prefs.snippets_filepath 
    if cust_path:#specified user location
        if cust_fp:
            snipDir = bpy.path.abspath(cust_fp)
        else:
            print ('!!! error with Custom file path (or empty), reading blend_directory')
            snipDir = (bpy.data.filepath)
 
    else:#default location (addon folders "snippets" subdir)
        script_file = os.path.realpath(__file__)
        directory = os.path.dirname(script_file)
        snipDir = os.path.join(directory, 'snippets/')
        if not os.path.exists(snipDir):
            try:
                os.mkdir(snipDir)
                print('snippets directory created at:', snipDir)
            except:
                print('!!! could not create snippets directory created at:', snipDir)

    if justGet:
        return(snipdir)
    else:
        if os.path.exists(snipDir):
            if os.path.isdir(snipDir):
                return(snipDir)
            else:
                return (os.path.split(snipDir)[0])
        else:
            print('error with location:', snipDir)
            return (0)



def insert_template(override, src_text):
    bpy.ops.text.insert(override, text=src_text)

def reload_folder(fp):
    '''take a filepath (location of the files) and return a list of filenames'''
    #recursive in folder
    snippetsList = []
    for root, dirs, files in os.walk(fp, topdown=True):
        for f in files:
            if f.endswith('.txt') or f.endswith('.py'):
                snippetsList.append(os.path.splitext(os.path.basename(f))[0])
    return (snippetsList)

                
def load_text(fp):
    if fp:
        with open(fp, 'r') as fd:
            text=fd.read()
        return text
    else:
        print('in load_text: no fp to read !')
        return(0)

def save_template(fp, name, text):
    if not name.endswith(('.txt', '.py')):
        name = name + '.txt'
    fd = open(os.path.join(fp, name),'w')
    fd.write(text)
    fd.close()
    return 0
 
def get_snippet(name):
    '''take a name
    and return a filepath if found in library
    '''
    library = locateLibrary()
    if library:
        for root, dirs, files in os.walk(library, topdown=True):#"."
            for f in files:
                if name.lower() == os.path.splitext(f)[0].lower():
                    return(os.path.join(root, f))
        print('in get_snippet: not found >', name)
        return (0)
    else:
        return(1)

def clipit(context):
    library = locateLibrary()
    bpy.ops.text.copy()
    clip = bpy.context.window_manager.clipboard
    if clip:
        #print (clip)
        ###kill preceding spaces before saving (allow to copy at indentation 0)
        clip = textwrap.dedent(clip)
        if context.scene.new_snippets_name:
            snipname = context.scene.new_snippets_name + '.txt'
        else:#generate Unique snipName
            from random import randrange
            import time
            snipname = 'snip'+ str(randrange(999)) + time.strftime("_%Y-%m-%d_%H-%M-%S") +'.txt'

        save_template(library, snipname, clip)
        return (snipname)
    else:
        return (0)