"""
Class to output water level and wave statistics netCDF files
"""
from wavelab.utilities import nc
from wavelab.processing.storm_options import StormOptions
import uuid
import time


class Storm_netCDF(object):
    
    def __init__(self):
        pass
    
    def process_netCDFs(self,so):

        if so.netCDF['Storm Tide with Unfiltered Water Level'].get() is True:
            so.get_meta_data()
            so.get_raw_water_level()
            so.get_surge_water_level()
            so.get_wave_water_level()
            self.storm_tide_and_unfiltered_water_level(so)

        time.sleep(2)

        if so.netCDF['Storm Tide Water Level'].get() is True:
            so.get_meta_data()
            so.get_raw_water_level()
            so.get_surge_water_level()
            self.storm_tide_water_level(so)

        time.sleep(2)

        if so.netCDF['Wave Statistics'].get() is True:
            if nc.get_frequency(so.sea_fname) >= 4:
                so.get_meta_data()
                so.get_air_meta_data()
                so.get_wave_water_level()
                so.test_water_elevation_below_sensor_orifice_elevation()
                so.get_wave_statistics()
                self.wave_statistics(so)

    @staticmethod
    def common_attributes(so, file_name, step):

        # nc.set_var_attribute(water_fname, 'sea_pressure', 'sea_uuid', sea_uuid)
        nc.set_global_attribute(file_name, 'uuid', str(uuid.uuid4()))
    
        # append air pressure
        instr_dict = nc.get_instrument_data(so.air_fname, 'air_pressure')
        nc.append_air_pressure(file_name, so.interpolated_air_pressure[::step], so.air_fname)
        nc.set_instrument_data(file_name, 'air_pressure', instr_dict)
    
        # update the lat and lon comments
        lat_comment = nc.get_variable_attr(file_name, 'latitude', 'comment')
        nc.set_var_attribute(file_name,
                             'latitude',
                             'comment',
                             ''.join([lat_comment,
                                      ' Latitude of sea pressure sensor used to derive ',
                                      'sea surface elevation.']))

        lon_comment = nc.get_variable_attr(file_name,
                                           'longitude',
                                           'comment')

        nc.set_var_attribute(file_name,
                             'longitude',
                             'comment',
                             ''.join([lon_comment,
                                      ' Longitude of sea pressure sensor used to derive ',
                                      'sea surface elevation.']))
    
        # set sea_pressure instrument data to global variables in water_level netCDF
        sea_instr_data = nc.get_instrument_data(so.sea_fname, 'sea_pressure')
        for x in sea_instr_data:
            attrname = ''.join(['sea_pressure_',x])
            nc.set_global_attribute(file_name, attrname, sea_instr_data[x])
        lat = nc.get_variable_data(file_name, 'latitude')
        lon = nc.get_variable_data(file_name, 'longitude')
   
        first_stamp = nc.get_global_attribute(file_name, 'time_coverage_start')
        last_stamp = nc.get_global_attribute(file_name, 'time_coverage_end')
        
        nc.set_global_attribute(file_name, 'title', 'Calculation of water level at %.4f latitude,'
                                ' %.4f degrees longitude from the date range of %s to %s.'
                                % (lat,lon,first_stamp,last_stamp))

    def storm_tide_and_unfiltered_water_level(self, so):

        out_fname2 = ''.join([so.output_fname,'_stormtide_unfiltered','.nc'])
        
        step = 1
        nc.custom_copy(so.sea_fname, out_fname2, so.begin, so.end, mode='storm_surge', step=step)
        self.common_attributes(so, out_fname2, step)
            
        nc.set_global_attribute(out_fname2, 'summary', 'This file contains four time series: 1)' 
                                ' air pressure 2) sea pressure 3) sea surface elevation'
                                ' 4) unfiltered sea surface elevation.'
                                ' The third was derived'
                                ' from a time series of high frequency sea pressure measurements'
                                ' adjusted using the former and then lowpass filtered to remove'
                                ' waves of period 1 second or less. The fourth is also sea surface elevation'
                                ' with no such filter.')
        
        nc.append_depth(out_fname2, so.surge_water_level[::step])
        sea_uuid = nc.get_global_attribute(so.sea_fname, 'uuid')
        air_uuid = nc.get_global_attribute(so.air_fname, 'uuid')
        nc.set_var_attribute(out_fname2, 'air_pressure', 'air_uuid', air_uuid)
        
        nc.append_variable(out_fname2,
                           'unfiltered_water_surface_height_above_reference_datum',
                           so.raw_water_level[::step],
                           'Unfiltered Sea Surface Elevation',
                           'unfiltered_water_surface_height_above_reference_datum')
        nc.set_var_attribute(out_fname2,
                             'water_surface_height_above_reference_datum',
                             'air_uuid',
                             air_uuid)
        nc.set_var_attribute(out_fname2,
                             'water_surface_height_above_reference_datum',
                             'sea_uuid',
                             sea_uuid)
        nc.set_var_attribute(out_fname2,
                             'water_surface_height_above_reference_datum',
                             'combined_level_accuracy_in_meters+-',
                             so.combined_level_accuracy_in_meters)
        nc.set_var_attribute(out_fname2,
                             'unfiltered_water_surface_height_above_reference_datum',
                             'air_uuid',
                             air_uuid)
        nc.set_var_attribute(out_fname2,
                             'unfiltered_water_surface_height_above_reference_datum',
                             'sea_uuid', sea_uuid)
        nc.set_var_attribute(out_fname2,
                             'unfiltered_water_surface_height_above_reference_datum',
                             'units',
                             'meters')
        nc.set_var_attribute(out_fname2,
                             'unfiltered_water_surface_height_above_reference_datum',
                             'nodc_name',
                             'WATER LEVEL')
        nc.set_var_attribute(out_fname2,
                             'unfiltered_water_surface_height_above_reference_datum',
                             'ioos_category',
                             'sea_level')
        nc.set_var_attribute(out_fname2,
                             'unfiltered_water_surface_height_above_reference_datum',
                             'combined_level_accuracy_in_meters+-',
                             so.combined_level_accuracy_in_meters)

    def storm_tide_water_level(self, so):

        out_fname2 = ''.join([so.output_fname,'_stormtide','.nc'])
        
        step = 1
        nc.custom_copy(so.sea_fname, out_fname2, so.begin, so.end, mode ='storm_surge', step=step)
        
        self.common_attributes(so, out_fname2, step)

        nc.set_global_attribute(out_fname2,
                                'summary',
                                'This file contains three time series: 1)' 
                                'air pressure 2) sea pressure 3) sea surface elevation.  The third was derived'
                                ' from a time series of high frequency sea pressure measurements '
                                ' adjusted using the former and then lowpass filtered to remove '
                                ' waves of period 1 second or less.')
        
        nc.append_depth(out_fname2, so.surge_water_level[::step])
        
        sea_uuid = nc.get_global_attribute(so.sea_fname, 'uuid')
        air_uuid = nc.get_global_attribute(so.air_fname, 'uuid')
        nc.set_var_attribute(out_fname2, 'air_pressure', 'air_uuid', air_uuid)
        nc.set_var_attribute(out_fname2,
                             'water_surface_height_above_reference_datum',
                             'air_uuid',
                             air_uuid)
        nc.set_var_attribute(out_fname2,
                             'water_surface_height_above_reference_datum',
                             'sea_uuid',
                             sea_uuid)
        nc.set_var_attribute(out_fname2,
                             'water_surface_height_above_reference_datum',
                             'combined_level_accuracy_in_meters+-',
                             so.combined_level_accuracy_in_meters)

    @staticmethod
    def wave_statistics(so):

        out_fname2 = ''.join([so.output_fname, '_wave_statistics', '.nc'])
        step = 1
        nc.wave_stats_copy(so.sea_fname, out_fname2, so)

        sea_uuid = nc.get_global_attribute(so.sea_fname, 'uuid')
        air_uuid = nc.get_global_attribute(so.air_fname, 'uuid')

        nc.set_global_attribute(out_fname2,
                                'sea_uuid',
                                sea_uuid)

        nc.set_global_attribute(out_fname2,
                                'air_uuid',
                                air_uuid)

        nc.set_global_attribute(out_fname2,
                                'summary',
                                'This file contains time, frequency, power spectral density, and wave statistics.'
                                '  For both wave heights and the power spectral density, the 90% confidence intervals'
                                ' were derived. Documentation can be found at '
                                'https://code.usgs.gov/wavelab/wavelab/-/blob/master/documentation/notebooks/index.md.')

        nc.set_global_attribute(out_fname2,
                                'combined_instrument_accuracy_in_meters+-',
                                so.combined_level_accuracy_in_meters)


if __name__ == '__main__':
    class Bool(object):

        def __init__(self, val):
            self.val = val

        def get(self):
            return self.val

    so = StormOptions()
    so.clip = False
    so.air_fname = '../documentation/data/NCCAR12248_9983816_air.csv.nc'
    so.sea_fname = '../documentation/data/NCCAR00007_1511451_sea.csv.nc'
    so.output_fname = '../documentation/data/stats.nc'
    so.international_units = False
    so.high_cut = 1.0
    so.low_cut = 0.045
    so.from_water_level_file = False

    so.netCDF['Storm Tide with Unfiltered Water Level'] = Bool(False)
    so.netCDF['Storm Tide Water Level'] = Bool(False)
    so.netCDF['Wave Statistics'] = Bool(True)

    so.timezone = 'GMT'
    so.daylight_savings = False
    snc = Storm_netCDF()
    snc.process_netCDFs(so)
