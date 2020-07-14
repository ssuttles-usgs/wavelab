<img src="./images/usgs.png" style=" padding-top: 26px; float: left"/>
<img src="./images/WaveLabLogo.png" style="float: left"/>

# Storm-Tide Water Level

To begin, we take a time series of sea pressure corrected by barometric pressure.


```python
from wavelab.utilities.nc import (get_pressure, 
                                  get_air_pressure, 
                                  get_time, 
                                  get_datetimes)

sea_file = '../data/NCCAR00007_1511451_sea.csv.nc'
baro_file = '../data/NCCAR12248_9983816_air.csv.nc'

# Load all of the data
sea_pressure_data = get_pressure(sea_file)
sea_milli = get_time(sea_file)
sea_date_times = get_datetimes(sea_file)

baro_pressure_data = get_air_pressure(baro_file)
baro_milli = get_time(baro_file)
baro_date_times = get_datetimes(baro_file)

# Interpolate the air pressure
baro_interp = np.interp(sea_milli, baro_milli, baro_pressure_data)

# Slice the data accordingly
itemindex = np.where(~np.isnan(baro_interp))
begin = itemindex[0][0]
end = itemindex[0][len(itemindex[0]) - 1]
corrected_pressure = sea_pressure_data[begin:end] - baro_interp[begin:end]
corrected_date_times = sea_date_times[begin:end]
```




<img src='./images/corrected_pressure.png' />



### Calculating Water Level

For assessing either storm surge or Storm-Tide, the choices are either Linear Wave Theory or the Hydrostatic method.   This software was developed in the context of our Storm-Tide monitoring program. The instruments that are depolyed are either pre-bracketed, on the side of piers for example, or installed ad-hoc to systematically capture the most useful data possible.  The sites are typically are not very deep in the associated water-bodies, therefore the most accurate method to use would be the Hydrostatic method.  The equation is straight-forward as follows:

Then calculate the water level for all frequencies (As you will see there is nearly a one to one relationship between decibar and meter units):


```python
from wavelab.processing.pressure_to_depth import hydrostatic_method

unfiltered_water_level = hydrostatic_method(corrected_pressure, density="salt")
```




<img src='./images/unfiltered_wl.png' />



### Choosing a Filter

USGS defines Storm-Tide as low-pass filtered signal including frequencies of both tide and storm surge.  There are many such filters to accomplish theis low-pass including USGS PL33 and Godin which use a kernel to attenuate the high frequencies.  This software euses a Butterworth filter which attenuates in frequency space.  It is desireable because of the minimized edge effects and steep decay in attenuation.  One of the parameters of the filter is an order which increases the steepness of the decay, (affecting less signal), however edge effects can occur and best judgement balancing the order must be used.  The best practice is to use an even number for the order of the filter because mathematicaly it is easier to resolve in frequncy space. After assessing performance of many orders a 4th order filter was chosen.

Other things to consider are:

- A one-minute cutoff was used in the low-pass filter, this ensured that by 30 seconds (the beginning of wind-wave frequencies), the signal was fully attenuated.
- The signal was filtered twice to preserve the phase angles (original position) of the water level time series.
- Although adequate for data with a wid reange of sampling frequencies, this filter was optimized for 4hz data (adjustments were mad to prepare for edge cases of 1 minute or more sampled data.)

### Calculating Storm-Tide


```python
from wavelab.processing.pressure_to_depth import lowpass_filter

storm_tide_water_level = lowpass_filter(unfiltered_water_level, 4 #frequency in hz)
```

This is the longer hand version of the above:


```python
from scipy import signal

# One minute cutoff divided by the Nyquist Frequency of 4hz
lowcut = .016666666665 / (.5 * 4)

# 4th order butterworth filter
b, a = signal.butter(4, [lowcut], btype='lowpass')

# Double filter to presever phase angles
storm_tide_water_level = signal.filtfilt(b, a, unfiltered_water_level)
```




<img src='./images/st_wl.png' />


