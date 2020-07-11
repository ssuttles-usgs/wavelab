#!/usr/bin/env python3
"""
Module to create cythonized datatest file.
Note that version and operating system are taken in to account
when building this file, the included file in the repository
will need to be built again based on the python version and operating
system.

Example:
    python setup.py build_ext --inplace

"""

from distutils.core import setup
from Cython.Build import cythonize
import numpy
 
setup(
    ext_modules = cythonize("DataTests.pyx"),
    include_dirs = [numpy.get_include()]
)