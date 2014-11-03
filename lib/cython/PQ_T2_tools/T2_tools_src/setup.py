from distutils.core import setup
from distutils.extension import Extension
import build_ext 
import numpy

setup(cmdclass = {'build_ext': build_ext},
        ext_modules = [Extension("T2_tools_bell", ["T2_tools_bell.pyx"])],
        include_dirs = [numpy.get_include()])