"""
A few convenience methods for quickly extracting/changing data in
netCDFs
"""
import os
from datetime import datetime
import numpy as np
from netCDF4 import Dataset
from netCDF4 import num2date
import uuid
import pytz
from wavelab.utilities import unit_conversion as uc

FILL_VALUE = -1e10


def chop_netcdf(fname, out_fname, begin, end, air_pressure = False):
    """Truncate the data in a netCDF file between two indices"""

    if os.path.exists(out_fname):
        os.remove(out_fname)
    length = end - begin
    
    if air_pressure is False:
        p = get_pressure(fname)[begin:end]
    else:
        p = get_air_pressure(fname)[begin:end]
        
    # get station id for the station_id dimension
    stn_site_id = get_global_attribute(fname, 'stn_station_number')
    
    t = get_time(fname)[begin:end]
    try:
        flags = get_flags(fname)[begin:end]
    except:
        flags = None
    alt = get_variable_data(fname, 'altitude')
    lat = get_variable_data(fname, 'latitude')
    long = get_variable_data(fname, 'longitude')
    d = Dataset(fname)
    output = Dataset(out_fname, 'w', format='NETCDF4_CLASSIC')
    output.createDimension('time', length)
    
    # copy globals
    for att in d.ncattrs():
        setattr(output, att, d.__dict__[att])
    
    og_uuid = get_global_attribute(fname, 'uuid') 
    setattr(output, 'uuid', str(uuid.uuid4()))

    # copy variables
    for key in d.variables:
        name = key
        
        if name == 'station_id':
            output.createDimension("station_id", len(stn_site_id))
            
        datatype = d.variables[key].datatype 
        
        dim = d.variables[key].dimensions
        
        if datatype == "int32":
            var = output.createVariable(name, datatype, dim)
        else:
            var = output.createVariable(name, datatype, dim, fill_value=FILL_VALUE)
        
        for att in d.variables[key].ncattrs():
            if att != '_FillValue':
                setattr(var, att, d.variables[key].__dict__[att])
                
        # add uuid of previous netCDF file to pressure variable
        if name == 'sea_pressure':
            setattr(var, 'sea_uuid', og_uuid)
        if name == 'air_pressure':
            setattr(var, 'air_uuid', og_uuid)
            
    output.variables['time'][:] = t
    
    if air_pressure == False:
        output.variables['sea_pressure'][:] = p
    else:
        output.variables['air_pressure'][:] = p

    if flags is not None:
        output.variables['pressure_qc'][:] = flags

    output.variables['altitude'][:] = alt
    output.variables['longitude'][:] = long
    output.variables['latitude'][:] = lat
    
    setattr(output,"time_coverage_start",
            uc.convert_ms_to_datestring(t[0], pytz.utc))

    setattr(output,"time_coverage_end",
            uc.convert_ms_to_datestring(t[-1], pytz.utc))

    setattr(output,"time_coverage_duration",
            uc.get_time_duration(t[-1] - t[0]))
    
    d.close()
    output.close()


def custom_copy(fname, out_fname, begin,end, mode="storm_surge", step = 1):
    if os.path.exists(out_fname):
        os.remove(out_fname)
    
    # get station id for the station_id dimension
    stn_site_id = get_global_attribute(fname, 'stn_station_number')
    
    t = get_time(fname)[begin:end:step]

    try:
        flags = get_flags(fname)[begin:end:step]
    except:
        flags = None
        print('no pressure qc')

    alt = get_variable_data(fname, 'altitude')
    lat = get_variable_data(fname, 'latitude')
    long = get_variable_data(fname, 'longitude')
    d = Dataset(fname)
    output = Dataset(out_fname, 'w', format='NETCDF4_CLASSIC')
    output.createDimension('time', len(t))
    output.createDimension("station_id", len(stn_site_id))
    
    # copy globals
    for att in d.ncattrs():
        setattr(output, att, d.__dict__[att])
    
    setattr(output, 'uuid', str(uuid.uuid4()))   
    
    has_station_id = False
    # copy variables
    for key in d.variables:
        
        # skip adding pressure qc if the mode is storm surge
        if mode == 'storm_surge' and (key == 'pressure_qc'):
            continue
        
        if key == 'station_id':
            has_station_id =True
            
        name = key
        datatype = d.variables[key].datatype 
          
        dim = d.variables[key].dimensions
        
        if datatype == "int32":
            var = output.createVariable(name, datatype, dim)
        else:
            var = output.createVariable(name, datatype, dim, fill_value=FILL_VALUE)
        
        for att in d.variables[key].ncattrs():
            if att != '_FillValue':
                setattr(var, att, d.variables[key].__dict__[att])
            
    output.variables['time'][:] = t
    
    if mode == 'storm_surge':
        if flags is not None:
            output.variables['pressure_qc'][:] = flags
        p = get_pressure(fname)[begin:end]
        output.variables['sea_pressure'][:] = p
        
    output.variables['altitude'][:] = alt
    output.variables['longitude'][:] = long
    output.variables['latitude'][:] = lat

    if has_station_id is False:
    # the following changes are essential in case the air and sea gui files are processed
    # with older versions of the script
        st_id = output.createVariable('station_id','S1',('station_id'))
        st_id.setncattr('cf_role', 'time_series_id')
        st_id.setncattr('long_name', 'station identifier')
        st_id[:] = list(stn_site_id)
    
    deployment_time = uc.convert_ms_to_datestring(t[0], pytz.utc)
    retrieval_time = uc.convert_ms_to_datestring(t[-1], pytz.utc)
    set_global_attribute(out_fname, 'deployment_time', deployment_time)
    set_global_attribute(out_fname, 'retrieval_time', retrieval_time)
    set_global_attribute(out_fname, 'salinity_ppm', 'unused')
    set_global_attribute(out_fname, 'device_depth', 'unused')
    set_global_attribute(out_fname, 'geospatial_lon_min', np.float64(-180))
    set_global_attribute(out_fname, 'geospatial_lon_max', np.float64(180))
    set_global_attribute(out_fname, 'geospatial_lat_min', np.float64(-90))
    set_global_attribute(out_fname, 'geospatial_lat_max', np.float64(90))
    set_global_attribute(out_fname, 'geospatial_vertical_min', np.float64(0))
    set_global_attribute(out_fname, 'geospatial_vertical_max', np.float64(0))
    
    first, last = get_sensor_orifice_elevation(out_fname)
    set_global_attribute(out_fname, 'sensor_orifice_elevation_at_deployment_time', \
                         np.float64("{0:.4f}".format(first)))
    set_global_attribute(out_fname, 'sensor_orifice_elevation_at_retrieval_time', \
                         np.float64("{0:.4f}".format(last)))
    set_global_attribute(out_fname, 'sensor_orifice_elevation_units', 'meters')
    
    first_land, last_land = get_land_surface_elevation(out_fname)
    set_global_attribute(out_fname, 'initial_land_surface_elevation', \
                         np.float64("{0:.4f}".format(first_land)))
    set_global_attribute(out_fname, 'final_land_surface_elevation', \
                         np.float64("{0:.4f}".format(last_land)))
    set_global_attribute(out_fname, 'land_surface_elevation_units', 'meters')

    set_global_attribute(out_fname, 'featureType', 'timeSeries')
    
    set_var_attribute(out_fname, 'latitude', 'valid_max', np.float64(90))
    set_var_attribute(out_fname, 'latitude', 'valid_min', np.float64(-90))
    set_var_attribute(out_fname, 'latitude', 'ioos_category', 'location')
    set_var_attribute(out_fname, 'latitude', 'units', 'degrees_north')
    set_var_attribute(out_fname, 'longitude', 'valid_max', np.float64(180))
    set_var_attribute(out_fname, 'longitude', 'valid_min', np.float64(-180))
    set_var_attribute(out_fname, 'longitude', 'ioos_category', 'location')
    set_var_attribute(out_fname, 'longitude', 'units', 'degrees_east')
    set_var_attribute(out_fname, 'altitude', 'valid_max', np.float64(1000))
    set_var_attribute(out_fname, 'altitude', 'valid_min', np.float64(-1000))
    set_var_attribute(out_fname, 'altitude', 'ioos_category', 'location')
    set_var_attribute(out_fname, 'altitude', 'positive', 'up')
    
    set_var_attribute(out_fname, 'time', 'ioos_category', 'time')
    set_var_attribute(out_fname, 'time', 'long_name', 'time')
    set_var_attribute(out_fname, 'altitude', 'comment', 'unused')
    # end attribute modifications
    
    d.close()
    output.close()


wave_dict = {
    'T1/3': {'name': 'significant_wave_period',
             'standard_name': 'sea_surface_wave_significant_period',
             'comment': 'Significant wave period is a statistic computed from wave measurements and '
                        'corresponds to the mean wave period of the highest one third of the waves. '
                        'A period is an interval of time, or the time-period of an oscillation. Wave '
                        'period is the interval of time between repeated features on the waveform such'
                        ' as crests, troughs or upward passes through the mean level.'
             },
    'H1/3': {'name': 'significant_wave_height',
             'standard_name': 'sea_surface_wave_significant_height',
             'alias': 'significant_height_of_wind_and_swell_waves',
             'upper_name': 'significant_wave_height_upper_ci',
             'lower_name': 'significant_wave_height_lower_ci'
             },
    'H10%': {'name': 'ten_percent_wave_height',
             'standard_name': 'sea_surface_wave_significant_height',
             'comment': 'Wave height is defined as the vertical distance from a wave trough to the '
                        'following wave crest. The height of the highest tenth is defined as the mean '
                        'of the highest ten per cent of trough to crest distances measured during the '
                        'observation period.',
             'upper_name': 'ten_percent_wave_height_upper_ci',
             'lower_name': 'ten_percent_wave_height_lower_ci'
             },
    'H1%': {'name': 'one_percent_wave_height',
            'upper_name': 'one_percent_wave_height_upper_ci',
            'lower_name': 'one_percent_wave_height_lower_ci'
            },
    'RMS': {'name': 'rms_wave_height',
            'upper_name': 'rms_wave_height_upper_ci',
            'lower_name': 'rms_wave_height_lower_ci'
            },
    'Median': {'name': 'median_wave_height',
               'upper_name': 'median_wave_height_upper_ci',
               'lower_name': 'median_wave_height_lower_ci'
               },
    'Maximum': {'name': 'maximum_wave_height',
                'standard_name': 'sea_surface_wave_maximum_height',
                'comment': 'Wave height is defined as the vertical distance from a wave trough to the following '
                           'wave crest. The maximum wave height is the greatest trough to crest distance measured'
                           ' during the observation period.',
                'alias': 'significant_height_of_wind_and_swell_waves',
                'upper_name': 'maximum_wave_height_upper_ci',
                'lower_name': 'maximum_wave_height_lower_ci'
                },
    'Average': {'name': 'mean_wave_height',
                'standard_name': 'sea_surface_wave_mean_height',
                'comment': 'Wave height is defined as the vertical distance from a wave trough to '
                           'the following wave crest. The mean wave height is the mean trough to '
                           'crest distance measured during the observation period.',
                'upper_name': 'mean_wave_height_upper_ci',
                'lower_name': 'mean_wave_height_lower_ci'
                },
    'Average Z Cross': {'name': 'average_zero_upcrossing_period',
                        'standard_name': 'sea_surface_wave_mean_period_from_variance_spectral_density_second_frequency_moment',
                        },
    'Mean Wave Period': {'name': 'mean_wave_period',
                         'standard_name': 'sea_surface_wave_mean_period_from_variance_spectral_density_first_frequency_moment',
                         },
    'Crest': {'name': 'crest_wave_period',
              'standard_name': 'sea_surface_wave_period_of_highest_wave',
              'comment': 'Wave period of the highest wave is the period determined from wave crests '
                              'corresponding to the greatest vertical distance above mean level during the '
                              'observation period. A period is an interval of time, or the time-period of an '
                              'oscillation. Wave period is the interval of time between repeated features on the '
                              'waveform such as crests, troughs or upward passes through the mean level.'
              },
    'Peak Wave': {'name': 'peak_wave_period',
                  'standard_name': 'sea_surface_wave_period_at_variance_spectral_density_maximum',
                  'comment': 'A period is an interval of time, or the time-period of an oscillation. '
                             'The sea_surface_wave_period_at_variance_spectral_density_maximum, '
                             'sometimes called peak wave period, is the period of the most energetic '
                             'waves in the total wave spectrum at a specific location.'
                  },
    'Spectrum': {'name': 'power_spectral_density',
                 'standard_name': 'sea_surface_wave_variance_spectral_density',
                 'comment': 'Sea surface wave variance spectral density is the variance of wave amplitude within a '
                            'range of wave frequency.',
                 'dims': ['time','frequency'],
                 'upper_name': 'power_spectral_density_upper_ci',
                 'lower_name': 'power_spectral_density_lower_ci'},
    'Frequency': {'name': 'frequency',
                  'comment': 'Frequency of overlapping 4096 4hz data points band averaged every 16 for 32 degrees of freedom',
                  'dims': ('frequency')},
    'time': {'name': 'time',
             'comment': "Averaged time for overlapping 4096 4hz data points (8.5 minutes)"}
    }


def wave_stats_copy(fname, out_fname, so):

    if os.path.exists(out_fname):
        os.remove(out_fname)
    
    # get station id for the station_id dimension
    stn_site_id = get_global_attribute(fname, 'stn_station_number')
    
    alt = get_variable_data(fname, 'altitude')
    lat = get_variable_data(fname, 'latitude')
    long = get_variable_data(fname, 'longitude')
    d = Dataset(fname)
    output = Dataset(out_fname, 'w', format='NETCDF4_CLASSIC')
    # print('time len %d' % len(so.stat_dictionary['time']))
    output.createDimension('time', len(so.stat_dictionary['time']))
    # print('freq len %d' % len(so.stat_dictionary['Frequency'][0]))
    output.createDimension('frequency', len(so.stat_dictionary['Frequency'][0]))
    output.createDimension("station_id", len(stn_site_id))

    # copy globals
    for att in d.ncattrs():
        setattr(output, att, d.__dict__[att])
    
    setattr(output, 'uuid', str(uuid.uuid4()))   

    # copy variables
    for key in d.variables:
        
        if key not in ['altitude', 'latitude', 'longitude', 'station_id']:
            continue
        
        name = key
        datatype = d.variables[key].datatype 
          
        dim = d.variables[key].dimensions
        
        if datatype == "int32":
            var = output.createVariable(name, datatype, dim)
        else:
            var = output.createVariable(name, datatype, dim, fill_value=FILL_VALUE)
        
        for att in d.variables[key].ncattrs():
            if att != '_FillValue':
                setattr(var, att, d.variables[key].__dict__[att])

    d.close()

    output.variables['altitude'][:] = alt
    output.variables['longitude'][:] = long
    output.variables['latitude'][:] = lat

    def pop_vars(og_name, dict_entry, so, upper=False, lower=False):
        dim = dict_entry['dims'] if 'dims' in dict_entry else ('time')
        name = dict_entry['name']

        if upper is True: name = dict_entry['upper_name']
        if lower is True: name = dict_entry['lower_name']
        var = output.createVariable(name, 'f8', dim)
        if 'standard_name' in dict_entry:
            var.standard_name = dict_entry['standard_name']
        if 'alias' in dict_entry:
            var.alias = dict_entry['alias']
        if 'comment' in dict_entry:
            var.comment = dict_entry['comment']

        if upper is True:
            try:
                var[:] = so.upper_stat_dictionary[og_name]
            except KeyError:
                var[:] = so.stat_dictionary[og_name]
        elif lower is True:
            try:
                var[:] = so.lower_stat_dictionary[og_name]
            except KeyError:
                var[:] = so.stat_dictionary[og_name]
        else:
            if og_name == 'Frequency':
                var[:] = so.stat_dictionary[og_name][0]
            else:
                var[:] = so.stat_dictionary[og_name]

    for x in wave_dict:
        pop_vars(x, wave_dict[x], so)

        if 'upper_name' in wave_dict[x]:
            pop_vars(x, wave_dict[x], so, upper=True)
            pop_vars(x, wave_dict[x], so, lower=True)


    if 'station_id' not in d.variables:
    # the following changes are essential in case the air and sea gui files are processed
    # with older versions of the script
        st_id = output.createVariable('station_id','S1', ('station_id'))
        st_id.setncattr('cf_role', 'time_series_id')
        st_id.setncattr('long_name', 'station identifier')
        st_id[:] = list(stn_site_id)
    
    # I have to keep this hunk of garbage until enought time has passed for all
    # data files to be properly formatted,
    deployment_time = get_global_attribute(fname, 'deployment_time')
    retrieval_time = get_global_attribute(fname, 'retrieval_time')
    set_global_attribute(out_fname, 'deployment_time', deployment_time)
    set_global_attribute(out_fname, 'retrieval_time', retrieval_time)
    set_global_attribute(out_fname, 'salinity_ppm', 'unused')
    set_global_attribute(out_fname, 'device_depth', 'unused')
    set_global_attribute(out_fname, 'geospatial_lon_min', np.float64(-180))
    set_global_attribute(out_fname, 'geospatial_lon_max', np.float64(180))
    set_global_attribute(out_fname, 'geospatial_lat_min', np.float64(-90))
    set_global_attribute(out_fname, 'geospatial_lat_max', np.float64(90))
    set_global_attribute(out_fname, 'geospatial_vertical_min', np.float64(0))
    set_global_attribute(out_fname, 'geospatial_vertical_max', np.float64(0))
    
    first, last = get_sensor_orifice_elevation(out_fname)
    set_global_attribute(out_fname, 'sensor_orifice_elevation_at_deployment_time', \
                         np.float64("{0:.4f}".format(first)))
    set_global_attribute(out_fname, 'sensor_orifice_elevation_at_retrieval_time', \
                         np.float64("{0:.4f}".format(last)))
    set_global_attribute(out_fname, 'sensor_orifice_elevation_units', 'meters')
    
    first_land, last_land = get_land_surface_elevation(out_fname)
    set_global_attribute(out_fname, 'initial_land_surface_elevation', \
                         np.float64("{0:.4f}".format(first_land)))
    set_global_attribute(out_fname, 'final_land_surface_elevation', \
                         np.float64("{0:.4f}".format(last_land)))
    set_global_attribute(out_fname, 'land_surface_elevation_units', 'meters')

    set_global_attribute(out_fname, 'featureType', 'timeSeries')
    
    set_var_attribute(out_fname, 'latitude', 'valid_max', np.float64(90))
    set_var_attribute(out_fname, 'latitude', 'valid_min', np.float64(-90))
    set_var_attribute(out_fname, 'latitude', 'ioos_category', 'location')
    set_var_attribute(out_fname, 'latitude', 'units', 'degrees_north')
    set_var_attribute(out_fname, 'longitude', 'valid_max', np.float64(180))
    set_var_attribute(out_fname, 'longitude', 'valid_min', np.float64(-180))
    set_var_attribute(out_fname, 'longitude', 'ioos_category', 'location')
    set_var_attribute(out_fname, 'longitude', 'units', 'degrees_east')
    set_var_attribute(out_fname, 'altitude', 'valid_max', np.float64(1000))
    set_var_attribute(out_fname, 'altitude', 'valid_min', np.float64(-1000))
    set_var_attribute(out_fname, 'altitude', 'ioos_category', 'location')
    set_var_attribute(out_fname, 'altitude', 'positive', 'up')
    
    set_var_attribute(out_fname, 'time', 'ioos_category', 'time')
    set_var_attribute(out_fname, 'time', 'long_name', 'time')
    set_var_attribute(out_fname, 'altitude', 'comment', 'unused')
    set_var_attribute(out_fname, 'time', 'standard_name', 'time')
    epoch_start = datetime(year=1970, month=1, day=1, tzinfo=pytz.utc)
    set_var_attribute(out_fname, 'time', 'units', "milliseconds since " + epoch_start.strftime("%Y-%m-%d %H:%M:%S"))
    # end attribute modifications

    output.close()


def parse_time(fname, time_name):
    """Convert a UTC offset in attribute "time_name" to a datetime."""

    timezone_str = get_global_attribute(fname, 'time_zone')
    timezone = pytz.timezone(timezone_str)
    time_str = get_global_attribute(fname, time_name)
    
    fmt_1 = '%Y%m%d %H%M'
    fmt_2 = '%Y%m%d %H:%M'
    
    try:
        time = timezone.localize(datetime.strptime(time_str, fmt_1))
    except:
        time = timezone.localize(datetime.strptime(time_str, fmt_2))
        
    epoch_start = datetime(year=1970, month=1, day=1, tzinfo=pytz.utc)
    time_ms = (time - epoch_start).total_seconds() * 1000
    return time_ms


def append_air_pressure(fname, pressure, air_fname = None):
    """Insert air pressure array into the netCDF file fname"""
    name = 'air_pressure'
    long_name = 'air pressure'
    append_variable(fname, name, pressure, comment='',
                     long_name=long_name, og_fname=air_fname)


def append_depth(fname, depth, calc_type='storm_surge'):
    """Insert depth array into the netCDF file at fname"""
    
    if calc_type == 'storm_surge':
        comment = ('Low-passed water surface elevation computed by: '
                   '1. Subtracting air pressure from the sea pressure '
                   '2. Removing the mean '
                   '3. Low-pass filtering forward using a 4th-order Butterworth filter'
                   ' with a cutoff at 1 minute '
                   '4. Filtering backward with the same filter to reduce phase errors '
                   '5. Adding the mean back in to the time series '
                   '6. Using the hydrostatic assumption to convert the pressure to water'
                   ' surface height above the sensor orifice '
                   '7. Adding surveyed-to-datum sensor orifice height'
                   ' The files for the sea pressure and air pressure used to calculate water level'
                   ' are identified by the properties sea_uuid and air_uuid respectively.')
    else:
        comment = ('The depth, computed using the variable "corrected '
                   'water pressure".')
    name = 'water_surface_height_above_reference_datum'
     
    append_variable(fname, name, depth, comment=comment,
                     long_name=name)
    
    # Get uuid (previously that of sea file), and add as property to water_level variable
    sea_uuid = get_global_attribute(fname, 'uuid')
    set_var_attribute(fname, name, 'sea_uuid', sea_uuid)
    set_global_attribute(fname, 'uuid', str(uuid.uuid4()))

def append_depth_qc(fname, sea_qc, air_qc):
    """Insert depth qc array"""

    depth_name = 'depth_qc'
    air_name = "air_qc"
    air_comment = 'The depth_qc is a binary and of the (sea)pressure_qc and air_pressure_qc if an air file is used to calculate depth'
    depth_comment = 'The depth_qc is a binary and of the (sea)pressure_qc and air_pressure_qc'
    flag_masks = '11111111 11111110 11111101 11111011 11110111'
    flag_meanings =  "no_bad_data last_five_vals_identical, outside_valid_range, invalid_rate_of_change, interpolated_data"

    if air_qc != None:
        air_qc = [int(str(x),2) for x in air_qc]
        sea_qc = [int(str(x),2) for x in sea_qc]

        depth_qc = [bin(air_qc[x] & sea_qc[x])[2:] for x in range(0,len(sea_qc))]
        
        
        append_variable(fname, air_name, [bin(x)[2:] for x in air_qc], comment=air_comment, long_name=air_name,
                            flag_masks = flag_masks, flag_meanings= flag_meanings)
            
        append_variable(fname, depth_name, depth_qc, comment=depth_comment, long_name=depth_name,
                         flag_masks = flag_masks, flag_meanings= flag_meanings)
    else:
        append_variable(fname, depth_name, sea_qc, comment=depth_comment, long_name=depth_name,
                         flag_masks = flag_masks, flag_meanings= flag_meanings)


def get_water_depth(in_fname):
    """Get the static water depth from the netCDF at fname"""

    initial_depth = get_initial_water_depth(in_fname)
    final_depth = get_final_water_depth(in_fname)
    initial_time = get_deployment_time(in_fname)
    final_time = get_retrieval_time(in_fname)
    time = get_time(in_fname)
    slope = (final_depth - initial_depth) / (final_time - initial_time)
    depth_approx = slope * (time - initial_time) + initial_depth
    return depth_approx


def get_depth(fname):
    """Get the wave height array from the netCDF at fname"""

    return get_variable_data(fname, 'water_surface_height_above_reference_datum')


def get_flags(fname):
    """Get the time array from the netCDF at fname"""

    return get_variable_data(fname, 'pressure_qc')


def get_time(fname):
    """Get the time array from the netCDF at fname"""

    return get_variable_data(fname, 'time')


def get_datetimes(fname):
    """Gets the time array and then converts them to date times"""
    time = []
    with Dataset(fname) as nc_file:
        
        time = num2date(nc_file.variables['time'][:],
                        nc_file.variables['time'].units,
                        only_use_cftime_datetimes=False,
                        only_use_python_datetimes=True)
    
    return time


def get_air_pressure(fname):
    """Get the air pressure array from the netCDF at fname"""

    return get_variable_data(fname, 'air_pressure')

def get_pressure(fname):
    """Get the water pressure array from the netCDF at fname"""
    
    try:
        return get_variable_data(fname, 'sea_pressure')
    except:
        return get_variable_data(fname, 'sea_water_pressure')


def get_pressure_qc(fname):

    return get_variable_data(fname, 'pressure_qc')


def get_air_pressure_qc(fname):

    return get_variable_data(fname, 'air_qc')


def get_depth_qc(fname):

    return get_variable_data(fname, 'depth_qc')


def get_frequency(fname):
    """Get the frequency of the data in the netCDF at fname"""

    freq_string = get_global_attribute(fname, 'time_coverage_resolution')
    return 1 / float(freq_string[1:-1])


def get_initial_water_depth(fname):
    """Get the initial water depth from the netCDF at fname"""

    return get_global_attribute(fname, 'initial_water_depth')


def get_final_water_depth(fname):
    """Get the final water depth from the netCDF at fname"""

    return get_global_attribute(fname, 'final_water_depth')


def get_deployment_time(fname):
    """Get the deployment time from the netCDF at fname"""

    return parse_time(fname, 'deployment_time')


def get_geospatial_vertical_reference(fname):
    """Get the goespatial vertical reference (datum) from the netCDF at fname"""

    return get_global_attribute(fname, 'geospatial_vertical_reference')


def get_sensor_orifice_elevation(fname):
    """Get the initial and final sensor orifice elevations from the netCDF at fname"""

    initial = get_global_attribute(fname, 'sensor_orifice_elevation_at_deployment_time')
    final = get_global_attribute(fname, 'sensor_orifice_elevation_at_retrieval_time')
    return (initial, final)


def get_land_surface_elevation(fname):
    """Get the initial and final land surface elevation from the necCDF at fname"""

    initial = get_global_attribute(fname, 'initial_land_surface_elevation')
    final = get_global_attribute(fname, 'final_land_surface_elevation')
    return (initial, final)


def get_retrieval_time(fname):
    """Get the retrieval time from the netCDF at fname"""

    return parse_time(fname, 'retrieval_time')


def get_device_depth(fname):
    """Get the retrieval time from the netCDF at fname"""

    return get_global_attribute(fname, 'device_depth')


def get_variable_data(fname, variable_name):
    """Get the values of a variable from a netCDF file."""

    with Dataset(fname) as nc_file:
        var = nc_file.variables[variable_name]
        var_data = var[:]
        return var_data


def get_variable_attr(fname, variable_name, attr):
    """Get the values of a variable from a netCDF file."""

    with Dataset(fname) as nc_file:
        var = nc_file.variables[variable_name]
        var_data = var.getncattr(attr)
        return var_data


def get_global_attribute(fname, name):
    """Get the value of a global attibute from a netCDF file."""

    with Dataset(fname) as nc_file:
        attr = getattr(nc_file, name)
        return attr
    
def set_global_attribute(fname, name, value):
    """Get the value of a global attibute from a netCDF file."""

    with Dataset(fname, 'a') as nc_file:
        setattr(nc_file, name, value)


def print_attributes(fname):
    with Dataset(fname, 'a') as nc_file:
       
        list = nc_file.ncattrs()
        for x in list:
            print(x, ':', get_global_attribute(fname, x))
            
        vars = nc_file.variables.keys()
        for x in vars:
            var = nc_file.variables[x]
            var_attrs = var.ncattrs()
            for y in var_attrs:
                print(x,':', y, ':', get_variable_attr(fname, x, y))


def set_variable_data(fname, variable_name, value):
    """Get the values of a variable from a netCDF file."""

    with Dataset(fname) as nc_file:
        var = nc_file.variables[variable_name]
        var[:] = value


def set_var_attribute(fname, var_name, name, value):
    """Get the value of a global attibute from a netCDF file."""

    with Dataset(fname, 'a') as nc_file:
        var = nc_file.variables[var_name]
        setattr(var, name, value)


def create_dimension(fname, dim_name, dim_length):
    with Dataset(fname, 'a') as nc_file:
        nc_file.create_dimension(fname, dim_name, dim_length)


def append_variable(fname, standard_name, data, comment='',
                     long_name='', flag_masks = None, flag_meanings = None, og_fname = None):
    """Append a new variable to an existing netCDF."""

    with Dataset(fname, 'a', format='NETCDF4_CLASSIC') as nc_file:
        pvar = nc_file.createVariable(standard_name, 'f8', ('time',))
        
        pvar.comment = comment
        pvar.standard_name = standard_name
        pvar.max = np.float64(1000)
        pvar.min = np.float64(-1000)
        pvar.short_name = standard_name
        pvar.ancillary_variables = ''
        pvar.add_offset = 0.0
        pvar.coordinates = 'time latitude longitude altitude'
        pvar.long_name = long_name
        pvar.scale_factor = 1.0
        if flag_masks != None:
            pvar.flags_masks = flag_masks
            pvar.flag_meanings = flag_meanings
        if standard_name == 'water_surface_height_above_reference_datum':
            pvar.units = 'meters'
            pvar.nodc_name = 'WATER LEVEL'
            pvar.ioos_category = 'sea_level'
        else:
            pvar.units = 'decibars'
            pvar.nodc_name = 'PRESSURE'
            pvar.ioos_category = 'pressure'
        pvar.compression = 'not used at this time'
        
        #get instrument data if appending air pressure
        if standard_name == 'air_pressure':
            instr_dict = get_instrument_data(og_fname, 'air_pressure')
            pvar.instrument_manufacturer = instr_dict['instrument_manufacturer']
            pvar.instrument_make = instr_dict['instrument_make']
            pvar.instrument_model = instr_dict['instrument_model']
            pvar.instrument_serial_number = instr_dict['instrument_serial_number']

        pvar[:] = data


def get_instrument_data(fname, variable_name):
    """Get the values of a variable from a netCDF file."""

    with Dataset(fname) as nc_file:
        var = nc_file.variables[variable_name]
        attr_dict = {
            'instrument_manufacturer': getattr(var,'instrument_manufacturer'),
            'instrument_make': getattr(var,'instrument_make'),
            'instrument_model': getattr(var,'instrument_model'),
            'instrument_serial_number': getattr(var, 'instrument_serial_number')
        }
        return attr_dict


def set_instrument_data(fname, variable_name, instr_dict):
    with Dataset(fname,'a', format='NETCDF4_CLASSIC') as nc_file:
        var = nc_file.variables[variable_name]
        for x in instr_dict:
            setattr(var, x, instr_dict[x])
