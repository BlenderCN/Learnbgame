from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import Cython.Compiler.Options 

Cython.Compiler.Options.annotate = True

# only valid on windows
#ext_modules = [Extension("mciso", ["mciso.pyx"],extra_compile_args=['/O2','/openmp','/fp:fast'])]
# for *nix this should work
ext_modules = [Extension("mciso", ["mciso.pyx"],extra_compile_args=['-O2', '-I/usr/local/include', '-fopenmp', '-mfpmath=sse'])]


setup(
  name = 'CubeSurfer core script',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)
