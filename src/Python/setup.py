"""
setup.py file
"""

from setuptools import setup, Extension
from setuptools.command.install import install
from subprocess import call
import numpy
import sys
import os
import platform

sse = False
# Path to CUDA on Linux and OS X
cuda_dir = "/usr/local/cuda"
# Path to CUDA library on Windows, 64 for 64 bit
win_cuda_dir = "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v7.5"

try:
    numpy_include = numpy.get_include()
except AttributeError:
    numpy_include = numpy.get_numpy_include()


arch = int(platform.architecture()[0][0:2])
cmdclass = {}
if sys.platform.startswith('win') and os.path.exists(win_cuda_dir):
    object_files = ['trottersuzuki/src/common.obj',
                    'trottersuzuki/src/cpublock.obj',
                    'trottersuzuki/src/cc2kernel.cu.obj',
                    'trottersuzuki/src/hybrid.cu.obj',                    
                    'trottersuzuki/src/trotter.obj',
                    'trottersuzuki/src/solver.obj']
    trottersuzuki_module = Extension('_trottersuzuki',
                                     sources=['trottersuzuki/trotter_wrap.cxx'],
                                     extra_objects=object_files,
                                     define_macros=[('CUDA', None)],
                                     library_dirs=[win_cuda_dir + 
                                                   "/lib/x" + str(arch)],
                                     libraries=['cudart', 'cublas'],
                                     include_dirs=[numpy_include])
elif os.path.exists(cuda_dir):
  
    class MyInstall(install):

        def run(self):
            os.chdir('trottersuzuki')
            call(["./configure", "--without-mpi", "--with-cuda=" + cuda_dir])
            call(["make", "lib"])
            os.chdir('../')
            install.run(self)

    if arch == 32:
        cuda_lib_dir = cuda_dir + "/lib"
    else:
        cuda_lib_dir = cuda_dir + "/lib64"
    object_files = ['trottersuzuki/src/common.o',
                    'trottersuzuki/src/cpublock.o',
                    'trottersuzuki/src/cc2kernel.cu.co',
                    'trottersuzuki/src/hybrid.cu.co',
                    'trottersuzuki/src/trotter.o',
                    'trottersuzuki/src/solver.o']

    if os.path.isfile('trottersuzuki/src/cpublocksse.o'):
        object_files.append('trottersuzuki/src/cpublocksse.o')

    trottersuzuki_module = Extension('_trottersuzuki',
                                     sources=['trottersuzuki/trotter_wrap.cxx'],
                                     extra_objects=object_files,
                                     define_macros=[('CUDA', None)],
                                     library_dirs=[cuda_lib_dir],
                                     libraries=['gomp', 'cudart', 'cublas'],
                                     include_dirs=[numpy_include])
    cmdclass = {'install': MyInstall}

else:
    if sys.platform.startswith('win'):
        extra_compile_args = ['-openmp', '-DWIN32']
        extra_link_args = []
    else:
        extra_compile_args = ['-fopenmp']
        if 'CC' in os.environ and 'clang-omp' in os.environ['CC']:
            extra_link_args = [
                '-liomp5'
            ]
        else:
            extra_link_args = [
                '-lgomp'
            ]
    sources_files = ['trottersuzuki/src/common.cpp',
                     'trottersuzuki/src/cpublock.cpp',
                     'trottersuzuki/src/trotter.cpp',
                     'trottersuzuki/src/solver.cpp',
                     'trottersuzuki/trotter_wrap.cxx']

    if sse:
        sources_files.append('trottersuzuki/src/cpublocksse.cpp')

    trottersuzuki_module = Extension('_trottersuzuki',
                                     sources=sources_files,
                                     include_dirs=[numpy_include, 'src'],
                                     extra_compile_args=extra_compile_args,
                                     extra_link_args=extra_link_args)

setup(name='trottersuzuki',
      version='1.4',
      license='GPL3',
      author="Peter Wittek, Luca Calderaro",
      author_email='peterwittek@users.noreply.github.com',
      url="http://trotter-suzuki-mpi.github.io/",
      platforms=["unix", "windows"],
      description="A massively parallel implementation of the Trotter-Suzuki decomposition",
      ext_modules=[trottersuzuki_module],
      py_modules=["trottersuzuki"],
      packages=["trottersuzuki"],
      install_requires=['numpy'],
      cmdclass=cmdclass
      )