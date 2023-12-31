<img src="./images/usgs.png" style="padding-top: 26px; float: left"/>
<img src="./images/WaveLabLogo.png" style="float: left"/>

# Storm-Tide Water Level

To begin, we take a time series of sea pressure corrected by barometric pressure.


```python
from datetime import datetime
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

For assessing either storm surge or Storm-Tide, the choices are either Linear Wave Theory or the Hydrostatic method.   This software was developed in the context of our Storm-Tide monitoring program. The instruments that are deployed are either pre-bracketed, on the side of piers for example, or installed ad-hoc to systematically capture the most useful data possible.  The sites are typically are not very deep in the associated water-bodies, therefore the most accurate method to use would be the Hydrostatic method.  The equation is straight-forward as follows:

$`\Huge \frac{\psi}{\rho * \mu}`$ <br /><br />
Where: <br />
$`\psi`$ = sea pressure in decibars (dbars)<br />
$`\rho`$ = water density in parts per a million (ppm)<br />
$`\mu`$ = gravity in meters per a second squared ($`ms^{2}`$)

There are three values for density that are relevant to our process:
<ul>
    <li>Salt Water: 1027 ppm</li>
    <li>Brackish Water: 1015 ppm</li>
    <li>Fresh Water: 1000 ppm</li>
</ul>
<br />
*In this particular example the site is comprised of salt water.

Then calculate the water level for all frequencies (As you will see there is nearly a one to one relationship between decibar and meter units):


```python
from wavelab.processing.pressure_to_depth import hydrostatic_method

unfiltered_water_level = hydrostatic_method(corrected_pressure, density="salt")
```




<img src='./images/unfiltered_wl.png' />



### Choosing a Filter

USGS defines Storm-Tide as low-pass filtered signal including frequencies of both tide and storm surge. There are many such filters to accomplish this low-pass, including USGS PL33 and Godin, which use a kernel to attenuate the high frequencies.

WaveLab uses a **Butterworth filter** (low-pass filter) to attenuate high frequencies in order to remove the components of wave setup and runup to estimate the storm tide at a site. It is desirable because of the minimized edge effects and steep decay in attenuation. 

**Butterworth Filter Specifications**

- Order: The order parameter increases the steepness of the decay, affecting less signal. However, edge effects can occur, and best judgement balancing the order must be used. The best practice is to use an even number for the order of the filter because mathematically it is easier to resolve in frequency space. After assessing performance of many orders, a 4th order filter was chosen.
- Cutoff Frequency: A six-minute cutoff is used.
- The signal was filtered twice to preserve the phase angles (original position) of the water level time series.
- Although adequate for data with a wide range of sampling frequencies, this filter was optimized for 4hz data (adjustments were made to prepare for edge cases of 1 minute or more sampled data).
- WaveLab automatically adjusts for the measurement sampling rate of the provided files.

### Calculating Storm-Tide


```python
from wavelab.processing.pressure_to_depth import butterworth_filter

storm_tide_water_level = butterworth_filter(unfiltered_water_level, 4) #frequency in hz
```

This is the longer hand version of the above:


```python
from scipy import signal

# Six-minute cutoff divided by the Nyquist Frequency of 4hz
lowcut = 0.002777777777775 / (.5 * 4)

# 4th order butterworth filter
b, a = signal.butter(4, [lowcut], btype='lowpass')

# Double filter to preserve phase angles
storm_tide_water_level = signal.filtfilt(b, a, unfiltered_water_level)
```




<img src='./images/st_wl.png' />



## References (filtering)

Emery, William J. and Richard E. Thomson (2014), Data Analysis Methods in Physical Oceanography, 617-619.

Hamid, S. and Alan V. Oppenheim and Alan S. Willsky (1997), Signals and Systems.

scipy.signal.butter (2014), https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.signal.butter.html

scipy.signal.buttord (2014), https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.signal.buttord.html#scipy.signal.buttord

Oliphant, Travis, scipy.signal.filtfilt (2002), https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.signal.filtfilt.html
