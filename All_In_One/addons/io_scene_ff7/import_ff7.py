import struct

from .utils import debug, setDebug

def load(properties):
    '''Fuction to initiate the loading process for files. Used to establish file type and which load fuction that should be used.'''

    setDebug(properties.debug)
    
    filepath = properties.filepath
    filepath = filepath.replace('\\', '/') #just in case we are on a windows machine
    
    filename = filepath.split('/')[-1] #gives us something that looks like 'hello.txt'
    filetype = filename.split('.')[-1] #gives us something that looks like 'txt'

    debug("Beginning Final Fantasy Import")

    #elementary filetype testing
    if filetype == 'p':
        load_p(filepath)
        
    if filetype == 'hrc':
        load_hrc(filepath)

    #will add more filetypes when I add a bit more functionality

    # Secondary filetype tests: battle models--which do not have file extentions
    # Need to be examined to decided which they are.

    return {'FINISHED'}

def load_p(filepath):
    '''A function for importing polygon files from Final Fantasy VII'''
    debug('Starting load_p()')

    with open(filepath, 'rb') as f:
        header = struct.unpack('llllllllllllllll', f.read(64)) #convert binary headers to integers

        data = {'VERSION': header[0],
                'VERTEX TYPE': header[2]}

    debug('Finished load_p()')


def load_rsd():
    '''A function for importing resource files from Final Fantasy VII'''
    pass

def load_hrc():
    '''A function for importing heiarcy files from Final Fantasy VII'''
    pass

def load_tex():
    '''A function for importing texture files from Final Fantasy VII'''
    pass

def load_a():
    '''A function for importing animation files from Final Fantasy VII'''
    pass