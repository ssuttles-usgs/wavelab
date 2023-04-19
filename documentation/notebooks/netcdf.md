## Reading NetCDF Files

WaveLab data can be exported as NetCDF files. This documentation describes how to read NetCDF files.

### Panoply

1. Visit this URL: https://www.giss.nasa.gov/tools/panoply/download/
2. Click the download link that corresponds to your computer.
3. After the .zip file downloads to your computer, unzip the file. 
4. Open the unzipped file and locate Panoply.exe.
5. Double-click Panoply.exe.
6. If you get an error related to Java Runtime Environment, you must download Amazon Corretto 16:
     1. Visit this URL: https://docs.aws.amazon.com/corretto/latest/corretto-16-ug/downloads-list.html
     2. Click the "Download Link" that corresponds to your computer. Most USGS users will select Windows x64: https://corretto.aws/downloads/latest/amazon-corretto-16-x64-windows-jdk.msi
     3. After the file downloads to your computer, run the file to install.
7. After Panoply has opened, open a NetCDF (.nc) file with one of these options:
     - Panoply may prompt you to open a file. Select a file in the file explorer.
     - Click File > Open.... Select a file in the file explorer.
     - Drag a file onto the Panoply window.
8. Note: you can add multiple files to view them all in the "Datasets" tab.
9. Click a row on the table in the "Datasets" tab to view a variable:
     - The metadata associated with the variable will be visible in the side panel.
     - If the "Type" of the variable is "—", the value of the variable will also be visible in the side panel.
     - If the "Type" of the variable is "1D", the value of the variable will not be visible in the side panel. To view the values:
          - Create a plot:
               1. Right-click the variable and click "Create Plot..." 
               2. Select another variable to use for the horizontal or vertical axis. Usually, you will want to use "time" for the "horiztonal" axis.
               3. A plot will become visible in the "Plot" tab in a new window.
               4. Click the "Array 1" tab to view a table of the data series. 
               5. On the "Array 1" tab, click the "Val" column header and Ctrl + C to copy the data series. You can then paste the data into an Excel workbook or other software.
          - Export as CSV:
               1. Right-click the variable and click "Export CSV..."
               2. Save the CSV file to your computer. 
               3. Open the CSV file in Excel.
               4. Select the data and copy it.
               5. Right-click in a cell and click the Transpose Paste button. 
               6. The data should now appear in a vertical column. 
               7. You can only export one variable at a time, so you will likely need to repeat this process for other variables and combine the columns into one Excel seet.
               8. Time values are represented as milliseconds since 1970-01-01 00:00:00. To convert time values to readable dates, use this formula `= (CellNumber / 86400000) + DATE(1970,1,1)` and Format Cell as a Date format.
     - Please note that metadata associated with a variable will not be exported from the NetCDF file if you export the variable as a CSV.

### Programming languages

- R users: Use the [ncdf4 package](https://cran.r-project.org/web/packages/ncdf4/index.html)
- Python users: Use the [netCDF4 package](https://unidata.github.io/netcdf4-python/)


```python

```
