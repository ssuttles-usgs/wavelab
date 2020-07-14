#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="wavelab",
    version="0.0.1",
    author="Gregory Petrochenkov",
    author_email="gpetrochenkov@usgs.gov",
    description="Post Storm Processing of Storm Surge and Wave Statistics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://code.usgs.gov/wavelab/wavelab",
    packages= find_packages("."),
    install_requires=['easygui',
                      'matplotlib==3.0.3',
                      'numpy',
                      'scipy==1.4.1',
                      'stats',
                      'pillow',
                      'pytz',
                      'pandas',
                      'uuid',
                      'netCDF4',
                      'defusedxml',
                      'jupyter',
                      'pyinstaller']
)