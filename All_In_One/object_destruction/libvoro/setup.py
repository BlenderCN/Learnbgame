from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import platform
import shutil
import os

extname = "voronoi"

if platform.architecture()[0] == "64bit" and platform.architecture()[1] == "WindowsPE":
    setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension(extname, [ "voro/src/voro++.cc", "voronoi.pyx"], language="c++",
                             extra_compile_args=["/fp:strict"])]
    )
else:
    setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [Extension(extname, [ "voro/src/voro++.cc", "voronoi.pyx"], language="c++")]
    )

#move to right directory
if platform.architecture()[0] == "64bit":
    if platform.architecture()[1] == "WindowsPE":
        dest = "win64/"+extname+".pyd"
        src = extname+".pyd"
    elif platform.architecture()[1] == "ELF":
        dest = "linux64/"+extname+".cpython-33m.so"
        src = extname+".cpython-33m.so"
    else:
        dest = "osx64/"+extname+".so"
        src = extname+".so"
elif platform.architecture()[0] == "32bit":
    if platform.architecture()[1] == "WindowsPE":
        dest = "win32/" + extname + ".pyd"
        src = extname + ".pyd"
    elif platform.architecture()[1] == "ELF":
        dest = "linux32/"+extname+".cpython-33m.so"
        src = extname+".cpython-33m.so"
    else:
        dest = "osx32/"+extname+".so"
        src = extname+".so"

shutil.move(src, dest)

#clean up
os.remove("voronoi.cpp")
shutil.rmtree("build")

