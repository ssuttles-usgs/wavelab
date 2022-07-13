#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="wavelab",
    version="1.1.0",
    author="Gregory Petrochenkov",
    author_email="gpetrochenkov@usgs.gov",
    description="Post Storm Processing of Storm Surge and Wave Statistics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://code.usgs.gov/wavelab/wavelab",
    packages=find_packages("."),
    include_package_data=True,
    data_files=[
        ('images', ['wavelab/images/legend.png',
                    'wavelab/images/north.png',
                    'wavelab/images/usgs.png',
                    'wavelab/images/wavelab.jpg',
                    'wavelab/images/wavelab_icon.ico']),
    ],
    install_requires=['easygui==0.98.1',
                      'matplotlib==3.0.3',
                      'numpy==1.19.1',
                      'scipy==1.4.1',
                      'stats==0.1.2a0',
                      'pillow==7.2.0',
                      'pytz==2020.1',
                      'pandas==1.1.2',
                      'uuid==1.30',
                      'netCDF4==1.5.3',
                      'defusedxml==0.6.0',
                      'jupyter==1.0.0',
                      'pyinstaller==4.10']
)
