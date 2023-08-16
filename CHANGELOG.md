# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased](https://code.usgs.gov/wavelab/wavelab/-/tree/dev)

### Added 

- Development Workflow section to README.md
- Release Workflow section to README.md
- versionfile.txt file to add details about the WaveLab.exe
- Added Generic sensor type to Air and Sea guis. This sensor type will process data using the Hobo data class. Input data files must follow the Generic or Hobo data template.
- Added some minor data format tests to catch errors and open pop ups to explain the problem.
- Statement of Filters to README.md
- Documentation about the "Sea Name" attribute
- wavelab@usgs.gov contact email address to README.md
- Documentation about reading NetCDF files
- Additional documentation about Butterworth filter and file processing
- Additional documentation about file upload
- About GUI

### Changed  

- history.json, history2_air.json, and history2_sea.json files are now saved in a WaveLab folder under the UserProfile environment variable instead of the same directory as WaveLab.exe
- Latitude and Longitude on graphs reduced to 4 decimal places
- Improved documentation for reporting bugs and requesting new features
- Instrument Error, Combined Instrument Error, Maximum Storm Tide Water Elevation, and Maximum Unfiltered Water Elevation reduced to 2 decimal places
- Graph Explanations now say "Butterworth 6-minute Filtered" instead of "Lowpass Filtered"
- Documentation now describes how to access WaveLab via WFast

### Deprecated 

-

### Removed 

- Disabled the Generic sensor type for the time being.

### Fixed  

- Latitude and Longitude are again rounded to 4 decimal places in the graphs
- Maximum Storm Tide Water Elevation and Maximum Unfiltered Water Elevation are now rounded to 2 decimal places in the graphs
- Documentation that erroneously referred to a one-minute Butterworth filter has been changed to refer to a six-minute Butterworth filter
- sea_pressure data is no longer NaN in the stormtide_unflitered.nc output file

### Security  

- 

## [v1.2.0](https://code.usgs.gov/wavelab/wavelab/-/tags/v1.2.0) - 2022-08-24

### Added 

- Added Van Essen to the list of possible baro sensors
- Added software version statement to main GUI and all graphs
- Added software version to metadata of output netCDF files

### Changed  

- Changed all instances of `matplotlib.use()` with `warn=False` to `force=False`
- Changed pyinstaller to version 4.10
  

## [v1.1.0](https://code.usgs.gov/wavelab/wavelab/-/tags/v1.1.0) - 2022-07-12
