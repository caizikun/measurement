from distutils.core import setup
from distutils.extension import Extension
import build_ext
reload(build_ext)
import numpy
reload(numpy)

setup(cmdclass = {'build_ext': build_ext.build_ext},
        ext_modules = [Extension("T2_tools_v3", ["T2_tools_v3.pyx"])],
        include_dirs = [numpy.get_include()])