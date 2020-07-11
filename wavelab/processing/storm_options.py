"""
Class to interface between StormGUI and StormData to properly
extract data from input netCDF files and output
netCDF, CSV, and visualizations
"""
from wavelab.processing.storm_data import StormData
from wavelab.processing import pressure_to_depth as p2d
import numpy as np
from wavelab.utilities import nc, unit_conversion as uc


class StormOptions(StormData):
    """options to interface between main gui and storm operations"""

    def __init__(self):
        
        super().__init__()
        self.netCDF = {
                       'Storm Tide with Unfiltered Water Level': None,
                       'Storm Tide Water Level': None,
                       'Wave Statistics': None
                       }
        
        self.csv = {
                    'Storm Tide with Unfiltered Water Level': None,
                    'Storm Tide Water Level': None,
                    'Atmospheric Pressure': None,
                    'Stats': None,
                    'PSD': None
                    }
        
        self.graph = {
                    'Storm Tide with Unfiltered Water Level': None,
                    'Storm Tide Water Level': None,
                    'Atmospheric Pressure': None
                      }
        
        self.statistics = {
             'H1/3': None,
#                     'H10%': None,
#                     'H1%': None,
#                     'RMS': None,
#                     'Median': None,
#                     'Maximum': None,
#                     'Average': None,
#                      'T1/3': None,
                     'Average Z Cross': None,
#                      'Mean Wave Period': None,
#                      'Crest': None,
                    'Peak Wave': None,
                     'PSD Contour': None
        }

        
        #not using the formatted time properties thus far...
        self.sea_fname = None
        self.air_fname = None
        self.wind_fname = None
        self.output_fname = None
        self.sea_time = None
        self.formatted_sea_time = None
        self.air_time = None
        self.formatted_air_time = None
        self.wind_time = None
        self.formatted_wind_time = None
        self.wind_time = None
        self.timezone = None
        self.daylight_savings = None
        self.raw_air_pressure = None
        self.raw_sea_pressure = None
        self.corrected_sea_pressure = None
        self.interpolated_air_pressure = None
        self.sea_pressure_mean = None
        self.surge_sea_pressure = None
        self.wave_sea_pressure = None
        self.raw_water_level = None
        self.surge_water_level = None
        self.wave_water_level = None
        self.chunked = False
        self.wave_water_level_chunks = None
        self.elevation_chunks = None
        self.wave_time_chunks = None
        self.pressure_chunks = None
        self.wind_speed_chunks = None
        self.sensor_orifice_chunks = None
        self.sensor_orifice_elevation = None
        self.land_surface_elevation = None
        self.wind_direction = None
        self.u = None
        self.v = None
        self.wind_speed = None
        self.surge_peak = None
        self.wave_peak = None
        self.total_peak = None
        self.datum = None
        self.latitude = None
        self.longitude = None
        self.stn_station_number = None
        self.air_latitude = None
        self.air_longitude = None
        self.air_stn_station_number = None
        self.wind_latitude = None
        self.wind_longitude = None
        self.wind_stn_station_number = None
        self.sliced = False
        self.wind_sliced = False
        self.begin = None
        self.end = None
        self.baroYLims = None
        self.wlYLims = None
        self.stat_dictionary = None
        self.upper_stat_dictionary = None
        self.lower_stat_dictionary = None
        self.stn_instrument_id = None
        self.air_stn_instrument_id = None
        self.international_units = False
        self.salinity = None
        self.clip = None
        self.clip_query = None
        self.elev_test = False
        self.low_cut = None
        self.high_cut = None
        self.from_water_level_file = False
        self.level_troll = False
        self.reference_name = None
        self.reference_elevation = None
        self.combined_level_accuracy_in_meters = None
        self.info_dict = None
        
    def get_sea_time(self):
        if self.sea_time is None:
            self.sea_time = self.extract_time(self.sea_fname)
            
        return self.sea_time
    
    def get_formatted_sea_time(self):
        if self.formatted_sea_time is None:
            
            self.get_sea_time()
                
            self.formatted_sea_time = self.convert_formatted_time(self.sea_time,
                                                                  self.timezone,
                                                                  self.daylight_savings)
    
    def get_air_time(self):
        if self.air_time is None:
            self.air_time = self.extract_time(self.air_fname)
            
    #focus
    def get_wind_time(self):
        if self.wind_time is None:
            self.wind_time = self.extract_time(self.wind_fname) 
            
    def get_salinity(self):
        if self.salinity is None:
            self.salinity = self.extract_salinity(self.sea_fname)
   
    def get_sea_pressure(self):
        if self.raw_sea_pressure is None:
            self.get_salinity()
            self.raw_sea_pressure = self.extract_raw_sea_pressure(self.sea_fname)
            
    def get_raw_air_pressure(self):
        if self.raw_air_pressure is None:
            self.raw_air_pressure = self.extract_raw_air_pressure(self.air_fname)
            
    def get_interpolated_air_pressure(self):
        if self.interpolated_air_pressure is None:
            
            self.get_sea_time()
            self.get_air_time()
            self.get_raw_air_pressure()
            self.interpolated_air_pressure = self.interpolate_air_pressure(self.sea_time,
                                                                           self.air_time,
                                                                           self.raw_air_pressure)

    def get_wind_speed(self):
        if self.u is None:
            self.u = self.extract_wind_u(self.wind_fname)
            self.v = self.extract_wind_v(self.wind_fname)
            self.wind_speed = self.derive_wind_speed(self.u, self.v)
 
    def get_sensor_orifice_elevation(self):
        if self.sensor_orifice_elevation is None:
            
            self.get_sea_pressure()
            self.sensor_orifice_elevation = np.array(self.extract_sensor_orifice_elevation(self.sea_fname,
                                                                                           len(self.raw_sea_pressure)))
            
    def get_land_surface_elevation(self):
        if self.land_surface_elevation is None:
            
            self.get_sea_pressure()
            self.land_surface_elevation = self.extract_land_surface_elevation(self.sea_fname,
                                                                              len(self.raw_sea_pressure))

    def get_corrected_pressure(self):
        if self.corrected_sea_pressure is None:
            if self.level_troll == True:
                self.slice_series()
                self.corrected_sea_pressure = self.raw_sea_pressure
            elif self.from_water_level_file == False:
                self.slice_series()
                self.corrected_sea_pressure = self.raw_sea_pressure - self.interpolated_air_pressure
            else:
                self.sea_time = self.extract_time(self.sea_fname)
                self.raw_water_level = nc.get_variable_data(self.sea_fname
                                                            , 'unfiltered_water_surface_height_above_reference_datum')
                self.interpolated_air_pressure = nc.get_air_pressure(self.sea_fname)
                self.sensor_orifice_elevation = np.array(self.extract_sensor_orifice_elevation(self.sea_fname,
                                                                                               len(self.sea_time)))
                self.land_surface_elevation = np.array(self.extract_land_surface_elevation(self.sea_fname,
                                                                                           len(self.sea_time)))
                self.corrected_sea_pressure = p2d.hydrostatic_pressure(self.raw_water_level -
                                                                       self.sensor_orifice_elevation)

            self.get_pressure_mean()
            
    def get_pressure_mean(self):
        if self.sea_pressure_mean is None:
            
            self.get_corrected_pressure()
            self.sea_pressure_mean = np.mean(self.corrected_sea_pressure)

    def get_combined_level_accuracy(self):
        sea_accuracy = self.extract_level_accuracy(self.sea_fname, 'sea_pressure')
        air_accuracy = self.extract_level_accuracy(self.air_fname, 'air_pressure')
        self.combined_level_accuracy_in_meters = sea_accuracy + air_accuracy
    
    def slice_all(self):
        self.sea_time[np.where(self.sea_time < 1475806770000)] = np.NaN
        self.sea_time[np.where(self.sea_time > 1475867310000)] = np.NaN
        sea_itemindex = np.where(~np.isnan(self.sea_time))
        
        begin = sea_itemindex[0][0]
        end = sea_itemindex[0][-1]
        self.sea_time = self.sea_time[begin:end]
        self.raw_water_level = self.raw_water_level[begin:end]
        self.surge_water_level = self.surge_water_level[begin:end]
        self.interpolated_air_pressure = self.interpolated_air_pressure[begin:end]
        self.sensor_orifice_elevation =  self.sensor_orifice_elevation[begin:end]
        self.land_surface_elevation = self.land_surface_elevation[begin:end]

    def slice_series(self):
        if self.sliced is False:
            if self.level_troll is False:
                self.get_interpolated_air_pressure()
            else:
                self.interpolated_air_pressure = nc.get_air_pressure(self.air_fname)
            self.get_sea_time()
            self.get_sea_pressure()
            self.get_sensor_orifice_elevation()
            self.get_land_surface_elevation()
            #g et the indexes for the first and last point which the sea and air times overlap
            
            
            itemindex = np.where(~np.isnan(self.interpolated_air_pressure))
            self.begin = begin = itemindex[0][0]
            self.end = end = itemindex[0][len(itemindex[0]) - 1]
            
            # slice all data to include all instances where the times overlap
            self.interpolated_air_pressure = self.interpolated_air_pressure[begin:end]
            self.raw_sea_pressure = self.raw_sea_pressure[begin:end]
            self.sea_time = self.sea_time[begin:end]
            self.sensor_orifice_elevation = self.sensor_orifice_elevation[begin:end]
            self.land_surface_elevation = self.land_surface_elevation[begin:end]

            self.sliced = True
            
    
    def slice_wind_data(self):
        """Slice off portions of the wind time that do not overlap with the sea time
        *I may want to make sure ALL data is sliced together in the future"""

        if self.wind_sliced == False:
            self.get_wind_time()
            self.get_wind_speed()
#             self.get_wind_direction()
            
            self.wind_time[np.where(self.wind_time < self.sea_time[0])] = np.NaN
            self.wind_time[np.where(self.wind_time > self.sea_time[-1])] = np.NaN
            wind_itemindex = np.where(~np.isnan(self.wind_time))
            
            wind_begin = wind_itemindex[0][0]
            wind_end = wind_itemindex[0][len(wind_itemindex[0]) - 1]
            
            self.wind_time = self.wind_time[wind_begin:wind_end]
            self.wind_speed = self.wind_speed[wind_begin:wind_end]
            self.u = self.u[wind_begin:wind_end]
            self.v = self.v[wind_begin:wind_end]
#             self.wind_direction = self.wind_direction[wind_begin:wind_end]
            self.wind_sliced = True

    def get_surge_sea_pressure(self):
        if self.surge_sea_pressure is None:
            
            if self.from_water_level_file is False:
                self.slice_series()
                
            self.get_corrected_pressure()
            
            difference = (self.sea_time[1] - self.sea_time[0]) / 1000
            self.fs = 1/difference
            
            self.surge_sea_pressure = self.derive_surge_sea_pressure(self.corrected_sea_pressure,
                                                                     self.sea_pressure_mean)

    def get_wave_sea_pressure(self):
        if self.wave_sea_pressure is None:
            self.get_surge_sea_pressure()
            self.wave_sea_pressure = (self.corrected_sea_pressure - self.sea_pressure_mean) 
            - self.surge_sea_pressure
            
    def get_raw_water_level(self):
        if self.raw_water_level is None:
            self.get_corrected_pressure()
            self.get_sensor_orifice_elevation()
            self.get_combined_level_accuracy()
            
            if self.raw_water_level is None:
                self.raw_water_level = np.array(self.derive_raw_water_level(self.corrected_sea_pressure,
                                                                             self.sensor_orifice_elevation,
                                                                             self.salinity))
            
    def get_surge_water_level(self): 
        if self.surge_water_level is None:
            self.get_corrected_pressure()
            self.get_sensor_orifice_elevation()
            self.get_pressure_mean()
            self.get_surge_sea_pressure()
            
            if self.from_water_level_file:
                self.surge_water_level = nc.get_variable_data(self.sea_fname,
                                                              "water_surface_height_above_reference_datum")
            else:
                self.surge_water_level = np.array(self.derive_filtered_water_level(self.surge_sea_pressure, 
                                                                      self.sea_pressure_mean, 
                                                                      self.sensor_orifice_elevation,
                                                                      self.salinity))
            
    def test_water_elevation_below_sensor_orifice_elevation(self):
        if self.elev_test is False:
            if self.international_units is True:
                clip_scale = .1 / uc.METER_TO_FEET
            else:
                clip_scale = .1
                
            if self.clip is None or self.clip is False:
                clip_scale = 0

            surge_query = np.where(self.surge_water_level < self.sensor_orifice_elevation[0] + clip_scale)
            raw_query = np.where(self.raw_water_level < self.sensor_orifice_elevation[0] + clip_scale)

            if len(surge_query[0]) == 0 or np.nanmax(surge_query[0]) == np.nan:
                self.clip_query = raw_query[0]
                self.raw_water_level[raw_query[0]] = np.nan
            else:
                self.clip_query = np.union1d(surge_query[0], raw_query[0])
                self.surge_water_level[surge_query[0]] = np.nan
                self.raw_water_level[raw_query[0]] = np.nan

            self.elev_test = True

    def get_wave_water_level(self, method = 'hyrdostatic'):
        if self.wave_water_level_chunks is None:
            self.get_raw_water_level()
            self.get_surge_water_level()
                
#             if method == 'hyrdostatic':
            self.wave_water_level = self.raw_water_level - self.surge_water_level
                
    def chunk_data(self):
        """Created a chunked time series with 50% overlap (About 17 mins with 4hz data)"""

        if self.chunked is False:
            start_index = 0
            end_index = 4096
            increment = 2048
            self.wave_time_chunks, \
                self.pressure_chunks, self.wind_speed_chunks = [], [], []
            self.elevation_chunks, self.sensor_orifice_chunks = [], []
            
            '''WIND SPEED MAY PROVE USEFUL WHEN CALCULATED WITH FETCH FOR FUTURE JONSWAP DATA
            DISSEMINATION'''
            if self.wind_speed is not None:
                ws = np.interp(self.sea_time,self.wind_time,self.wind_speed)
            else:
                self.wind_speed_chunks = None
                
            c_pressure = self.corrected_sea_pressure

#             c_pressure[self.clip_query] = np.NaN
            
            while end_index <= len(c_pressure):
                self.wave_time_chunks.append(self.sea_time[start_index:end_index] / 1000)
                self.pressure_chunks.append(c_pressure[start_index:end_index])
                self.elevation_chunks.append(np.mean(self.land_surface_elevation[start_index:end_index]))
                self.sensor_orifice_chunks.append(np.mean(self.sensor_orifice_elevation[start_index:end_index]))
                
                if self.wind_speed is not None:
                    self.wind_speed_chunks.append(ws[start_index:end_index] / 
                                                  uc.METERS_PER_SECOND_TO_MILES_PER_HOUR)
                
                
                start_index += increment
                end_index += increment
                
            self.chunked = True

    def get_wave_statistics(self):

        if self.stat_dictionary is None:
            
            self.get_corrected_pressure()
            self.chunk_data()
            
            self.stats.low_cut = self.low_cut
            self.stats.high_cut = self.high_cut
            
            self.stat_dictionary, self.upper_stat_dictionary, self.lower_stat_dictionary = \
                self.derive_statistics(self.pressure_chunks,
                                       self.wave_time_chunks,
                                       self.elevation_chunks,
                                       self.sensor_orifice_chunks,
                                       meters=self.international_units,
                                       instrument_error=self.combined_level_accuracy_in_meters)
            
    def check_file_types(self):
        try:
            nc.get_air_pressure(self.air_fname)
            nc.get_pressure(self.sea_fname)
        except:
            return False
        
        return True

    def check_selected(self):
        for x in self.netCDF:
            if self.netCDF[x].get() is True:
                return True
            
        for x in self.csv:
            if self.csv[x].get() is True:
                return True
            
        for x in self.graph:
            if self.graph[x].get() is True:
                return True
            
        for x in self.statistics:
            if self.statistics[x].get() is True:
                return True
            
        return False
    
    def air_check_selected(self):
        for x in self.netCDF:
            if self.netCDF[x].get() is True:
                return True
            
        for x in self.csv:
            if x != 'Atmospheric Pressure' and self.csv[x].get() is True:
                return True
            
        for x in self.graph:
            if x != 'Atmospheric Pressure' and self.graph[x].get() is True:
                return True
            
        return False  

    def wind_check_selected(self):
        for x in self.graph:
            if x == 'Storm Tide with Wind Data' and self.graph[x].get() is True:
                return True
            
        return False
    
    def stat_check_selected(self):
        count = 0
        for x in self.statistics:
            if self.statistics[x].get() is True:
                count += 1
                
        if count > 2:
            return False
        else:
            return True
    
    def time_comparison(self):
        """Checks to see the overlap of the two pressure files.  Returns 1 if there is some overlap,
        2 if none, 0 if all overlaps"""

        self.get_sea_time()
        self.get_air_time()
        
        if self.air_time[-1] < self.sea_time[0] or self.air_time[0] > self.sea_time[-1]:
            return 2
        
        elif self.air_time[0] > self.sea_time[0] or self.air_time[-1] < self.sea_time[-1]:
            return 1
            
        return 0
    
    def format_output_fname(self, og_fname):
        if og_fname is not None and og_fname != '':
            og_fname = og_fname.replace('..','*')
            last_index = og_fname.rfind('.')
            og_fname = og_fname.replace('*','..')
            if last_index != -1:
                self.output_fname = og_fname[0:last_index]
            else:
                self.output_fname = og_fname
        else:
            self.output_fname = 'output'

    def get_meta_data(self):
        if self.datum is None:
            self.datum = nc.get_geospatial_vertical_reference(self.sea_fname)
            self.latitude = nc.get_variable_data(self.sea_fname, 'latitude')
            self.longitude = nc.get_variable_data(self.sea_fname, 'longitude')
            self.stn_station_number = nc.get_global_attribute(self.sea_fname, 'stn_station_number')
            self.stn_instrument_id = nc.get_global_attribute(self.sea_fname, 'stn_instrument_id')
            
    def get_air_meta_data(self):
        if self.air_latitude is None:
            
            if self.from_water_level_file is False:
                self.air_latitude = nc.get_variable_data(self.air_fname, 'latitude')
                self.air_longitude = nc.get_variable_data(self.air_fname, 'longitude')
                self.air_stn_station_number = nc.get_global_attribute(self.air_fname, 'stn_station_number')
                self.air_stn_instrument_id = nc.get_global_attribute(self.air_fname, 'stn_instrument_id')
            else:
                self.air_latitude = nc.get_variable_data(self.air_fname, 'latitude')
                self.air_longitude = nc.get_variable_data(self.air_fname, 'longitude')
                self.air_stn_station_number = nc.get_global_attribute(self.air_fname, 'stn_station_number')
                self.air_stn_instrument_id = nc.get_variable_attr(self.air_fname, 'air_pressure', 'instrument_serial_number')
            
    def get_wind_meta_data(self):
        if self.wind_latitude is None:
            
            try:
                self.wind_latitude = nc.get_variable_data(self.wind_fname, 'latitude')
                self.wind_longitude = nc.get_variable_data(self.wind_fname, 'longitude')
                self.wind_stn_station_number = nc.get_global_attribute(self.wind_fname, 'stn_station_number')
            except:
                self.wind_latitude = 0
                self.wind_longitude = 0
                self.wind_stn_station_number = 'na'

    def convert_to_dict(self):
        self.info_dict = {}
        self.info_dict['air_fname'] = self.air_fname
        self.info_dict['sea_fname'] = self.sea_fname
        self.info_dict['output_fname'] = self.output_fname
        self.info_dict['level_troll'] = self.level_troll
        self.info_dict['timezone'] = self.timezone
        self.info_dict['daylight_savings'] = self.daylight_savings
        self.info_dict['reference_name'] = self.reference_name
        self.info_dict['reference_elevation'] = self.reference_elevation
        self.info_dict['clip'] = self.clip
        self.info_dict['baroYLims'] = self.baroYLims
        self.info_dict['wlYLims'] = self.wlYLims
        self.info_dict['low_cut'] = self.low_cut
        self.info_dict['hight_cut'] = self.high_cut
        self.info_dict['international_units'] =self.international_units

        self.info_dict['netCDF'] = {
            'Storm Tide with Unfiltered Water Level': self.netCDF['Storm Tide with Unfiltered Water Level'].get(),
            'Storm Tide Water Level': self.netCDF['Storm Tide Water Level'].get(),
            'Wave Statistics': self.netCDF['Wave Statistics'].get()
        }
        self.info_dict['csv'] = {
            'Storm Tide with Unfiltered Water Level': self.csv['Storm Tide with Unfiltered Water Level'].get(),
            'Storm Tide Water Level': self.csv['Storm Tide Water Level'].get(),
            'Atmospheric Pressure': self.csv['Atmospheric Pressure'].get(),
            'Stats': self.csv['Stats'].get(),
            'PSD': self.csv['PSD'].get()
        }

        self.info_dict['graph'] = {
            'Storm Tide with Unfiltered Water Level': self.graph['Storm Tide with Unfiltered Water Level'].get(),
            'Storm Tide Water Level': self.graph['Storm Tide Water Level'].get(),
            'Atmospheric Pressure': self.graph['Atmospheric Pressure'].get()
        }

        self.info_dict['statistics'] = {
            'H1/3': self.statistics['H1/3'].get(),
            'Average Z Cross': self.statistics['Average Z Cross'].get(),
            'Peak Wave': self.statistics['Peak Wave'].get(),
            'PSD Contour': self.statistics['PSD Contour'].get()
        }

    def extract_from_dict(self):
        self.air_fname = self.info_dict['air_fname']
        self.sea_fname = self.info_dict['sea_fname']
        self.output_fname = self.info_dict['output_fname']
        self.level_troll = self.info_dict['level_troll']
        self.timezone = self.info_dict['timezone']
        self.daylight_savings = self.info_dict['daylight_savings']
        self.reference_name = self.info_dict['reference_name']
        self.reference_elevation = self.info_dict['reference_elevation']
        self.clip = self.info_dict['clip']
        self.baroYLims = self.info_dict['baroYLims']
        self.wlYLims = self.info_dict['wlYLims']
        self.low_cut = self.info_dict['low_cut']
        self.high_cut = self.info_dict['hight_cut']
        self.international_units = self.info_dict['international_units']
        self.netCDF = {
            'Storm Tide with Unfiltered Water Level': Bool(self.info_dict['netCDF']['Storm Tide with Unfiltered Water Level']),
            'Storm Tide Water Level': Bool(self.info_dict['netCDF']['Storm Tide Water Level']),
            'Wave Statistics': Bool(self.info_dict['netCDF']['Wave Statistics'])
        }
        self.csv = {
            'Storm Tide with Unfiltered Water Level': Bool(self.info_dict['csv']['Storm Tide with Unfiltered Water Level']),
            'Storm Tide Water Level': Bool(self.info_dict['csv']['Storm Tide Water Level']),
            'Atmospheric Pressure': Bool(self.info_dict['csv']['Atmospheric Pressure']),
            'Stats': Bool(self.info_dict['csv']['Stats']),
            'PSD': Bool(self.info_dict['csv']['PSD'])
        }

        self.graph = {
            'Storm Tide with Unfiltered Water Level': Bool(self.info_dict['graph']['Storm Tide with Unfiltered Water Level']),
            'Storm Tide Water Level': Bool(self.info_dict['graph']['Storm Tide Water Level']),
            'Atmospheric Pressure': Bool(self.info_dict['graph']['Atmospheric Pressure'])
        }

        self.statistics = {
            'H1/3': Bool(self.info_dict['statistics']['H1/3']),
            'Average Z Cross': Bool(self.info_dict['statistics']['Average Z Cross']),
            'Peak Wave': Bool(self.info_dict['statistics']['Peak Wave']),
            'PSD Contour': Bool(self.info_dict['statistics']['PSD Contour'])
        }

    def clear_data(self):
        self.sea_fname = None
        self.air_fname = None
        self.wind_fname = None
        self.output_fname = None
        self.sea_time = None
        self.formatted_sea_time = None
        self.air_time = None
        self.formatted_air_time = None
        self.wind_time = None
        self.formatted_wind_time = None
        self.wind_time = None
        self.timezone = None
        self.daylight_savings = None
        self.raw_air_pressure = None
        self.raw_sea_pressure = None
        self.corrected_sea_pressure = None
        self.interpolated_air_pressure = None
        self.sea_pressure_mean = None
        self.surge_sea_pressure = None
        self.wave_sea_pressure = None
        self.raw_water_level = None
        self.surge_water_level = None
        self.wave_water_level = None
        self.chunked = False
        self.wave_water_level_chunks = None
        self.elevation_chunks = None
        self.pressure_chunks = None
        self.wave_time_chunks = None
        self.sensor_orifice_chunks = None
        self.sensor_orifice_elevation = None
        self.land_surface_elevation = None
        self.wind_direction = None
        self.u = None
        self.v = None
        self.wind_speed = None
        self.surge_peak = None
        self.wave_peak = None
        self.total_peak = None
        self.datum = None
        self.latitude = None
        self.longitude = None
        self.stn_station_number = None
        self.air_latitude = None
        self.air_longitude = None
        self.air_stn_station_number = None
        self.wind_latitude = None
        self.wind_longitude = None
        self.wind_stn_station_number = None
        self.sliced = False
        self.wind_sliced = False
        self.begin = None
        self.end = None
        self.baroYLims = None
        self.wlYLims = None
        self.stat_dictionary = None
        self.upper_stat_dictionary = None
        self.lower_stat_dictionary = None
        self.stn_instrument_id = None
        self.air_stn_instrument_id = None
        self.international_units = False
        self.salinity = None
        self.clip = None
        self.clip_query = None
        self.elev_test = False
        self.low_cut = None
        self.high_cut = None
        self.from_water_level_file = False
        self.level_troll = False
        self.reference_name = None
        self.reference_elevation = None
        self.combined_level_accuracy_in_meters = None
        self.info_dict = None


class Bool(object):

    def __init__(self, val):
        self.val = val

    def get(self):
        return self.val

