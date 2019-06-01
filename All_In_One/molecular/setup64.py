from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import Cython.Compiler.Options 

Cython.Compiler.Options.annotate = True

# only valid on windows
#ext_modules = [Extension("cmolcore", ["cmolcore.pyx"],extra_compile_args=['/Ox','/openmp','/GT','/arch:SSE2','/fp:fast'])]
# for *nix this should work
ext_modules = [Extension("cmolcore", ["cmolcore.pyx"],extra_compile_args=['-O2', '-I/usr/local/include', '-fopenmp', '-mfpmath=sse', '-march=corei7-avx'], extra_link_args=['-fopenmp'])]


setup(
  name = 'Molecular script',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)
