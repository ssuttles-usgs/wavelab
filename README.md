<img src="./documentation/notebooks/images/usgs.png" style="width: 100px; height: 40px; float: left"/>
<img src="./documentation/notebooks/images/WaveLabLogo.png" style="width: 100px; height: 40px; float: left"/>

# WaveLab (wavelab)

This software calculates Storm-Tide water level and wave statistics (where applicable) for deployed instrument data.

## Information for WaveLab Users

### How to run WaveLab

Windows users:

1. Vsit https://code.usgs.gov/wavelab/wavelab and click [WaveLab.zip](https://code.usgs.gov/wavelab/wavelab/-/blob/master/WaveLab.zip).
2. Click the [Download](https://code.usgs.gov/wavelab/wavelab/-/raw/master/WaveLab.zip?inline=false) button.
3. Unzip the file on your computer.
4. Double-click WaveLab.exe. The program may take a minute or more to load.

### How to use WaveLab

Please visit the [Documentation pages](https://code.usgs.gov/wavelab/wavelab/-/blob/master/documentation/notebooks/index.md) to learn to use WaveLab.

### How to request new features 

1. Visit the Issues page: https://code.usgs.gov/wavelab/wavelab/-/issues.
2. Click the "New issue" button.
3. Enter a title that describes the new feature.
4. Next to "Description", select "Feature Request" in the dropdown box.
5. Use the template to describe the feature that you would like to request.

Please note that all new feature requests must be approved by the Short-Term Network User Group.

### How to report bugs/issues

1. Visit the Issues page: https://code.usgs.gov/wavelab/wavelab/-/issues
2. Click the "New issue" button
3. Enter a title that describes the bug you have encountered.
4. Next to "Description", select "Bug" in the dropdown box.
5. Use the template to describe the bug that you wouldl ike to report.

Please note that all bug fixes must be approved by the Short-Term Network User Group.

## Information for WaveLab Developers

### Code Installation

1. Clone the repository
2. In the command prompt, enter the root of the directory.
3. Run the following command in the terminal. This will install the package "wavelab" in your environment.

`pip install .`

4. Run the following command in order to run data tests for the sea pressure data:

`python ./wavelab/addons/cython_setup.py build_ext --inplace`

5. Run the following command to build the final executable:

For Windows:

`pyinstaller --clean --add-data wavelab/images/*;./images -F -n WaveLab --icon=wavelab/images/wavelab_icon.ico --noconsole ./wavelab/gui/master.py`

For Linux:

`pyinstaller --clean --add-data wavelab/images/*:./images -F -n WaveLab --icon=wavelab/images/wavelab_icon.ico --noconsole --hidden-import='PIL._tkinter_finder' ./wavelab/gui/master.py`

Note: building an executable makes it usable for only that operating system. Consult pyinstaller docs for more info:
https://pyinstaller.readthedocs.io/en/stable/usage.html

### Repository Structure

#### Documentation

- Reference documentation can be found <a href="https://code.usgs.gov/wavelab/wavelab/-/blob/master/documentation/notebooks/index.md">here</a>.

- The jupyter notebooks can be found in the [documentation/notebooks directory](https://code.usgs.gov/wavelab/wavelab/-/tree/master/documentation/notebooks). These can run by changing to the notebooks directory and running the following command: `jupyter notebook`.  This will provide a link to view the notebooks in your browser or automatically open in a browser window.

- The [documentation/notebooks directory](https://code.usgs.gov/wavelab/wavelab/-/tree/master/documentation/notebooks) has the HTML pages pre-built and can be viewed in your browser by opening index.html (code.usgs.gov does not support GitLab Pages as of now).   

- Images for the ReadMe are in the [documentation/notebooks/images directory](https://code.usgs.gov/wavelab/wavelab/-/tree/master/documentation/notebooks/images).

- The [documentation/references directory](https://code.usgs.gov/wavelab/wavelab/-/tree/master/documentation/references) has a copies of papers (where available) in our bibliography.

#### Code

- All of the main code is contained in the [wavelab directory](https://code.usgs.gov/wavelab/wavelab/-/tree/master/wavelab).

### Dependencies
#### Software

- Python >= 3.6 (3.7 recommended)

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

## About the Software

### License

This project is licensed under the Creative Commons CC0 1.0 Universal License. See the [LICENSE.md file](https://code.usgs.gov/wavelab/wavelab/-/blob/master/LICENSE.md) for details


### Citation

Petrochenkov G (2020). WaveLab Water Level and Wave Statistics Processing Toolbox: U.S. Geological Survey Software Release, doi:10.5066/P9M6YLMN.

```
@Manual{,
  author = {Gregory Petrochenkov},
  title = {wavelab: Storm-Tide water level and wave statistics processing toolbox},
  publisher = {U.S. Geological Survey},
  address = {Reston, VA},
  version = {0.0.1},
  institution = {U.S. Geological Survey},
  year = {2020},
  url = {https://code.usgs.gov/wavelab/wavelab},
}
```

##### DOI
https://doi.org/10.5066/P9M6YLMN

##### IPDS Number
IP-121859

##### Authors
- [Gregory Petrochenkov](https://www.usgs.gov/staff-profiles/gregory-petrochenkov): Author
- [Harry Jenter](https://www.usgs.gov/staff-profiles/harry-jenter): Contributor
- Christopher Mazzullo: Contributor
- Anders Hopkins: Maintainer 
- [Andrea Medenblik](https://www.usgs.gov/staff-profiles/andrea-s-medenblik): Maintainer 

