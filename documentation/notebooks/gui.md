<style>

.custom-list {
    margin-left: 285px;
    font-size: 14pt;
}

.custom-list li {
    margin: 50px;
}

.custom-list li:first {
    margin: 50px;
    text-wieght: bold;
    list-style-type: none;
}

.custom-list b {
    margin-left: 30px;
}

.sea-custom-list {
    margin-left: 550px;
    margin-top: 0px;
    font-size: 10pt;
}

.sea-custom-list li {
    margin: 10px;
}

.sea-custom-list li:first {
    margin: 50px;
    text-weight: bold;
    list-style-type: none;
}

.chopper-custom-list {
    margin-left: 250px;
    margin-top: 0px;
    font-size: 14pt;
}

.chopper-custom-list li {
    margin: 50px;
}

.chopper-custom-list li:first {
    margin: 50px;
    text-wieght: bold;
    list-style-type: none;
}

.chopper-custom-list b {
    margin-left: 30px;
}


.storm-custom-list {
    margin-left: 520px;
    margin-top: 0px;
    font-size: 12pt;
}

.storm-custom-list li {
    margin: 30px;
}

.storm-custom-list li:first {
    margin: 50px;
    text-weight: bold;
    list-style-type: none;
}

.storm-custom-list b {
    margin-left: 30px;
}
</style>



<img src="images/usgs.png" style=" padding-top: 26px; float: left"/>
<img src="images/WaveLabLogo.png" style="float: left"/>

# Using the Interface

Double click WaveLab.exe, the program may take a minute or more to load.  You will then see the following screen: <br />

<div style="padding-top: 25px">
<img src="images/master_gui.png" style="float: left" />
    <ul class="custom-list">
        <b>GUIs Opened When Clicked</b>
        <li>"Sea GUI": Open sea pressure data/meatadata tool</li>
        <li>"Air GUI": Open barometric pressure data/metadata tool</li>
        <li>"Chopper": Open timeseries cropping tool</li>
        <li>"Storm GUI": Open Storm-Tide Water Level and Wave Statistics Toolbox</li>
    </ul>
</div>

If you are starting from the beginning you should go through each of these toolboxes in order.

## Sea GUI

This toolbox takes the extracted sea pressure data from the instrument and converts to netCDF format with the approriate data and metadata.  You will see the following screen when you click on "Sea GUI":

<img src="images/sea_air_begin.png" style="float:left; border:2px solid black; border-bottom: 1px solid black">

- <b>Add File(s)</b>: adds one or more files to be processed (this would be the csv or similar data files extracted from the pressure instrument of choice)
- <b>Save Globals</b>: Save the data from the three fields above to load for a future session
- <b>Load Globals</b>: Load the saved globals
- <b>Process Files</b>:  To process data after filling out all required informtion of added files 
- <b>Quit</b>: Quit Sea GUI


Enter the appropriate information in the fields and then press "Add File(s)".  You will see the following window:

<div style="padding-top: 5px">
<img src="images/sea_gui.png" style="margin-top: 17px; float: left; width: 550px; height: 550px; border: 2px solid black" />
    <ul class="sea-custom-list" >
        <b>Fields</b>
        <li> "Instrument": Choose the respective instrument used from the drop down list</li>
        <li>"STN Site id": Id of the site established in the Short Term Network</li>
        <li>"STN Instrument Id": Id of the Instrument deployed in the Short Term Newtork</li>
        <li>"Latitude": Latitude of Site</li>
        <li>"Longitude": Longitude of Site</li>
        <li>"Time zone...": Timezone data was collected in (to be converted to UTC)</li>
        <li>"Daylight Savings": Whether the data is in Daylight Savings time</li>
        <li>"Datum": Vertical Datum Of Data</li>
        <li>"Salinity": Drop-down to specify salinity of water body</li>
        <li>"Initial land surface elevation": Tape down to sea floor at deployment time</li>
        <li>"Final land surface elevation": Tape down to sea floor at retreival time</li>
        <li>"Sensor orifice elevation at deployment time": Tape down to sensor at deployment time</li>
        <li>"Sensor orifice elevation at retrieval time": Tape down to sensor at retrieval time</li>
        <li>"Deployment time": Time of instrument depolyment</li>
        <li>"Retrieval time": Time of instrument retrieval</li>
    </ul>
</div>

- <b>Remove File</b>: Revmoes the file from the list
- <b>Save entries</b>: Saves data entered for use in other windows or future sessions
- <b>Load Entries</b>: Load saved entries

After filling in all the fields click on "Process Files" to convert all added files to netCDF sea pressure files.  Files will be the original name with ".nc" appended to the end.

## Air GUI

This toolbox takes the extracted barometric pressure data from the instrument and converts to netCDF format with the approriate data and metadata.  At first you will see the same screen when you click on "Sea GUI".  After filling in the fields click "Add File(s)" and then you will see the following screen:

<div>
<img src="images/air_gui.png" style="margin-top: 5px; float: left; width: 550px; height: 400px; border: 2px solid black" />
    <ul class="sea-custom-list" >
        <b>Fields</b>
        <li> "Instrument": Choose the respective instrument used from the drop down list</li>
        <li>"STN Site id": Id of the site established in the Short Term Network</li>
        <li>"STN Instrument Id": Id of the Instrument deployed in the Short Term Newtork</li>
        <li>"Latitude": Latitude of Site</li>
        <li>"Longitude": Longitude of Site</li>
        <li>"Time zone...": Timezone data was collected in (to be converted to UTC)</li>
        <li>"Daylight Savings": Whether the data is in Daylight Savings time</li>
        <li>"Datum": Vertical Datum Of Data</li>
        <li>"Sensor orifice elevation at deployment time": Tape down to sensor at deployment time</li>
        <li>"Sensor orifice elevation at retrieval time": Tape down to sensor at retrieval time</li>
    </ul>
</div>

As with "Sea GUI", click on "Process Files" to convert all added files to barometric pressure netCDF files.  Files will be the original name with ".nc" appended to the end.

## Chopper

This tool box lets a user crop bad data out of the time series of either sea pressure or batorometric pressure netCDF files created by "Sea GUI" and "Air GUI".  You will see the following screen when click on "Chopper":

<div>
<img src="images/chopper_begin.png" style="margin-top: 0px; float: left; width: 300px; height: 400px; border: 2px solid black" />
    <ul class="chopper-custom-list" >
        <b>Steps</b>
        <li> Choose whether the file is a sea or air pressure netCDF file</li>
        <li>Choose the time zone to display the dates</li>
        <li>Select the file of interest</li>
    </ul>
</div>

After selecting the file you will see the following screen:

<img src="images/chopper.png" style="margin-top: 5px; float: left; border: 2px solid black" />
   

- The yellow portion of the graph indicates the portion of the time series to be extracted.
- To choose where to begin and end with your mouse, left-click the time step to begin the extraction, and right-click the timestep to end the extraction.
- To choose wehere to begin and end with fields: enter the date-time in both "Start Date" and "End Date" under "Define Period to Export"
- Finally click "Export Selection" to save the file.

## Storm GUI

This toolbox takes the netCDF files from "Sea GUI" and "Air GUI", (or respective chopped time series from "Chopper"), and calculates unfiltered water level, Storm-Tide water level, and wave statistics.  You will see the following when "Storm GUI" is clicked:

<div style="padding-top: 5px">
<img src="images/storm_gui.png" style="margin-top: 17px; float: left; width: 550px; height: 550px; border: 2px solid black" />
    <ul class="storm-custom-list" >
        <b>Steps</b>
        <li>Add sea pressure and baro pressure netCDF files to "Water File" and "Air File" respectively </li>
        <li>Check the boxes the output files of interest.  <b style="margin-left: 0px">Make sure to follow the SOP when choosing what files to create.</b></li>
        <li>Choose a timezone to display the times in</li>
        <li>Optionally choose y lmiits for the barometric pressure and water level visualizations</li>
        <li>Optionally choose a reference height of interest and depth of water aobve said reference height</li>
        <li>Choose an output name and click "Process files"</li>
    </ul>
</div>

All files are going to use the output name and append a suffix to describe the file.  Consult <a href="https://code.usgs.gov/wavelab/wavelab/-/blob/master/documentation/notebooks/output.md">output.md</a> to get a list of the suffixes and explanation of output.
