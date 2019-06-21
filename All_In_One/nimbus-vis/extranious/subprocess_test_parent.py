import io
import bpy
import subprocess
from subprocess_test_stream_reader import NonBlockingStreamReader as NBSR


spipe = subprocess.Popen(
    'py',
    stdout=subprocess.PIPE, 
    stderr=subprocess.PIPE,
    )

wrappedSpipe = NBSR.start(spipe.stdout)

print(wrappedSpipe.readline())


#enables standalone support
if __name__ == "__main__":
    import os
    import bpy
    import sys
    from os.path import dirname, join
    mainPackage = dirname(bpy.data.filepath)
    if not mainPackage in sys.path:
        sys.path.append(mainPackage)
        print(mainPackage + " appended to sys path")
    library = join(mainPackage, "libs")
    if not library in sys.path:
        sys.path.append(library)
        print(library + " appended to sys path")
    os.chdir(mainPackage) ###THIS IS VERY IMPORTANT AND FIXES EVERYTHING
        
    #extra file-specific stuff
    extr = join(mainPackage, "extranious")
    if not extr in sys.path:
        sys.path.append(extr)
        print(extr + " appended  to sys path")


'''
if __name__ == "__main__":
    import bpy
    import sys
    from os.path import dirname, join, abspath, basename
    mainPackage = dirname(bpy.data.filepath) #bpy filepath is the blend file
    if not mainPackage in sys.path:
        sys.path.append(mainPackage)
    library = join(mainPackage, "libs")
    if not library in sys.path:
        sys.path.append(library)
        print(library + " appended to sys path")
    ext = join(mainPackage, "extranious")
    if not ext in sys.path:
        sys.path.append(ext)
    io = join(mainPackage, "io")
    if not io in sys.path:
        sys.path.append(io)
'''
