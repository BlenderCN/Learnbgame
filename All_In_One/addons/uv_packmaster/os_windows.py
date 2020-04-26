import os
from ctypes.util import find_library

def os_exec_extension():
    return '.exe'

def os_packer_dirname():
    return 'win'
    
def os_platform_check(packerPath):
    if find_library('MSVCP140.dll') is None:
        return False, 'Install Visual C++ 2017 Redistributable and restart Blender'
        
    return True, ''
    