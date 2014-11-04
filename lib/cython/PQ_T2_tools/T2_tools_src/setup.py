from distutils.core import setup
from distutils.extension import Extension
import build_ext
reload(build_ext)
import numpy
reload(numpy)

setup(cmdclass = {'build_ext': build_ext.build_ext},
        ext_modules = [Extension("T2_tools_bell_BS", ["T2_tools_bell_BS.pyx"])],
        include_dirs = [numpy.get_include()])