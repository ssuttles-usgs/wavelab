<img src="./documentation/notebooks/images/usgs.png" style="width: 100px; height: 40px; float: left"/>
<img src="./documentation/notebooks/images/WaveLabLogo.png" style="width: 100px; height: 40px; float: left"/>

# WaveLab (wavelab)

### About
This software calculates Storm-Tide water level and wave statistics (where applicable) for deployed instrument data.

### Use of Executable

For windows, download WaveLab.zip, unzip, and then double click WaveLab.exe.  the program may take a minute or more to load.

### Code Installation

Clone the repository, in the command terminal enter the root of the directory

Run the following command in the terminal

<code>pip install .</code>

This will install the package "wavelab" in your respective environment.

You will need to run the following in order to run data tests for the sea pressure data:

<code>python ./wavelab/addons/cython_setup.py build_ext --inplace</code>

To build the final executable, run the following command:

<code>pyinstaller --clean --add-data 'wavelab/images/*;./images' -F -n WaveLab --icon=wavelab/images/wavelab_icon.ico --noconsole ./wavelab/gui/master.py</code>

### Repository Structure

#### Documentation

- Reference documentation can be found <a href="https://code.usgs.gov/wavelab/wavelab/-/blob/master/documentation/notebooks/index.md">here</a>.

- The jupyter notebooks can be found in the "documentation/notebooks" directory. These can run by changing to the notebooks directory and running the following command: <code>jupyter notebook</code>.  This will provide a link to view the notebooks in your browser or automatically open in a browser window.

- The "documentation/notebook_html" directory has the html pages pre built and can be viewed in your browser by opening index.html (code.usgs.gov does not support GitLab Pages as of now).   

- Images for the readme are in the "documentation/notebooks/images" directory.

- The "documentation/references" directory has a copies of papers (where available) in our bibliography.

#### Code

- All of the main code is contained in the "wavelab" directory.

### Dependencies
#### Software

- Python >= 3.6 (3.7 reccomended)

#### Python Packages

- easygui
- matplotlib
- numpy
- scipy
- stats
- pillow
- pytz
- pandas
- uuid
- netCDF4
- defusedxml
- (juptyer to run notebooks)
- (pyinstaller to build executable)


### License

This project is licensed under the Creative Commons CC0 1.0 Universal License - see the LICENSE.md file for details


### Citation

Petrochenkov G (2020). WaveLab: Storm-Tide water level and wave statistics processing toolbox. https://code.usgs.gov/wavelab/wavelab.

<code>@Manual{,
  author = {Gregory Petrochenkov},
  title = {wavelab: Storm-Tide water level and wave statistics processing toolbox},
  publisher = {U.S. Geological Survey},
  address = {Reston, VA},
  version = {0.0.1},
  institution = {U.S. Geological Survey},
  year = {2020},
  url = {https://code.usgs.gov/wavelab/wavelab},
}</code>

##### Authors
Gregory Petrochenkov. Author, maintainer. <br />
Harry Jenter. Contributor. <br />
Chriz Mazzullo. Contributor.
