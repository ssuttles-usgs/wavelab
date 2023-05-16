# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased](https://code.usgs.gov/wavelab/wavelab/-/tree/dev)

### Added 

- Development Workflow section to README.md
- Release Workflow section to README.md
- versionfile.txt file to add details about the WaveLab.exe
- Statement of Filters to README.md

### Changed  

- history.json, history2_air.json, and history2_sea.json files are now saved in a WaveLab folder under the UserProfile environment variable instead of the same directory as WaveLab.exe

### Deprecated 

-

### Removed 

- 

### Fixed  

- 

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
