#!/usr/bin/env python3
"""
This module extracts the relevant information from the StormOptions object
and creates output files in CSV format.
"""
import pandas as pd
from wavelab.utilities.nc import get_frequency
from wavelab.utilities import unit_conversion as uc
import pytz
import csv as csv_package


class StormCSV(object):
    
    def __init__(self):
        self.int_units = True
    
    def process_csv(self, so):
        
        if so.csv['Storm Tide with Unfiltered Water Level'].get() is True:
            so.get_meta_data()
            so.get_raw_water_level()
            so.get_surge_water_level()
            self.storm_tide_and_unfiltered_water_level(so)
            
        if so.csv['Storm Tide Water Level'].get() is True:
            so.get_meta_data()
            so.get_raw_water_level()
            so.get_surge_water_level()
            self.storm_tide_water_level(so)
            
        if so.csv['Atmospheric Pressure'].get() is True:
            so.get_air_meta_data()
            so.get_air_time()
            so.get_raw_air_pressure()
            self.atmospheric_pressure(so)
            
        if so.csv['Stats'].get() is True:
            if get_frequency(so.sea_fname) >= 4:
                so.get_meta_data()
                so.get_air_meta_data()
                so.get_wave_statistics()
                self.stats(so)
            
        if so.csv['PSD'].get() is True:
            if get_frequency(so.sea_fname) >= 4:
                so.get_meta_data()
                so.get_air_meta_data()
                so.get_wave_statistics()
                self.psd(so)

    @staticmethod
    def format_time(so, time_type='sea'):
        """Get the appropriate datetime string based on the user input"""
        
        if time_type == 'sea':
            format_time = [uc.convert_ms_to_date(x, pytz.utc) for x in so.sea_time]
        if time_type == 'air':
            format_time = [uc.convert_ms_to_date(x, pytz.utc) for x in so.air_time]
        if time_type == 'stat':
            format_time = [uc.convert_ms_to_date(x, pytz.utc) for x in so.stat_dictionary['time']]
            
        format_time = uc.adjust_from_gmt(format_time, so.timezone, so.daylight_savings)
        format_time = [x.strftime('%m/%d/%y %H:%M:%S')for x in format_time]
            
        return format_time  

    @staticmethod
    def write_header(out_file_name, so, air=False, write_type="normal"):
        """Write descriptive csv header"""
        
        if air is False:
            csv_header = ["","Latitude: %.4f" % so.latitude, 'Longitude: %.4f' % so.longitude, \
                'STN_Station_Number: %s' % so.stn_station_number]
                
        else:
            csv_header = ["","Latitude: %.4f" % so.air_latitude, 'Longitude: %.4f' % so.air_longitude, \
                'STN_Station_Number: %s' % so.air_stn_station_number]
        
        with open(out_file_name, 'w') as csvfile:
            writer = csv_package.writer(csvfile, delimiter=',')
            writer.writerow(csv_header) 
            if write_type == "PSD":
                writer.writerow(["","Power Spectral Density in m^2/Hz", "Frequencies in Hz"])

    @staticmethod
    def time_column_format(so):
        if so.daylight_savings is not None and so.daylight_savings is True:
            return '%s Daylight Savings Time' % so.timezone 
        else:
            return '%s Time' % so.timezone  
            
    def storm_tide_and_unfiltered_water_level(self, so):
        """csv for Storm Surge and Unfiltered Water Level"""
        
        # adjust date times to appropriate time zone
        format_time = self.format_time(so)
        
        if self.int_units is True:
            format_surge_water_level = so.surge_water_level
            format_surge_label = 'Storm Tide Water Level in Meters'
            format_unfiltered_water_level = so.raw_water_level
            format_unfiltered_label = 'Unfiltered Water Level in Meters'
            format_air_pressure = so.interpolated_air_pressure
            format_air_pressure_label = 'Air Pressure in Decibars'
        else:
            format_surge_water_level = so.surge_water_level * uc.METER_TO_FEET
            format_surge_label = 'Storm Tide Water Level in Feet'
            format_unfiltered_water_level = so.raw_water_level * uc.METER_TO_FEET
            format_unfiltered_label = 'Unfiltered Water Level in Feet'
            format_air_pressure = so.interpolated_air_pressure * uc.DBAR_TO_INCHES_OF_MERCURY
            format_air_pressure_label = 'Air Pressure in Inches of Hg'
        
        time_column = self.time_column_format(so)

        excel_file = pd.DataFrame({time_column: format_time,
                                  format_air_pressure_label: format_air_pressure,
                                  format_surge_label: format_surge_water_level,
                                  format_unfiltered_label : format_unfiltered_water_level
                                  })
        
        out_file_name = ''.join([so.output_fname,'_stormtide_unfiltered','.csv'])
            
        self.write_header(out_file_name, so)

        excel_file.to_csv(path_or_buf=out_file_name,
                          mode='a',
                          columns=[time_column,
                                   format_unfiltered_label,
                                   format_surge_label,
                                   format_air_pressure_label])
     
    def storm_tide_water_level(self, so):
        
        # adjust date times to appropriate time zone
        format_time = self.format_time(so)

        if self.int_units is True:
            format_surge_water_level = so.surge_water_level
            format_surge_label = 'Storm Tide Water Level in Meters'
            format_air_pressure = so.interpolated_air_pressure
            format_air_pressure_label = 'Air Pressure in Decibars'
        else:
            format_surge_water_level = so.surge_water_level * uc.METER_TO_FEET
            format_surge_label = 'Storm Tide Water Level in Feet'
            format_air_pressure = so.interpolated_air_pressure * uc.DBAR_TO_INCHES_OF_MERCURY
            format_air_pressure_label = 'Air Pressure in Inches of Hg'
        
        time_column = self.time_column_format(so)

        excel_file = pd.DataFrame({time_column: format_time,
                                  format_air_pressure_label: format_air_pressure,
                                  format_surge_label : format_surge_water_level,
                                  })
        
        out_file_name = ''.join([so.output_fname,'_stormtide','.csv'])
            
        self.write_header(out_file_name, so)
         
        # save excel file to path
        excel_file.to_csv(path_or_buf=out_file_name,
                          mode='a', columns=[time_column,
                                             format_surge_label,
                                             format_air_pressure_label])

    def stats(self, so):
        # adjust dates to the appropriate timezone
        format_time = self.format_time(so, time_type = 'stat')
        
        format_hm0 = so.stat_dictionary['H1/3']
        if self.int_units == True:
            format_hm0_label = 'Significant Wave Height in Meters'
        else:
            format_hm0_label = 'Significant Wave Height in Feet'
        format_tm0 = so.stat_dictionary['Average Z Cross']
        format_tm0_label = 'Average Zero-Up-Crossings Period in Seconds'
        format_tp = so.stat_dictionary['Peak Wave']
        format_tp_label = 'Peak Wave Period in Seconds'
        
        time_column = self.time_column_format(so)

        excel_file = pd.DataFrame({time_column: format_time,
                                  format_hm0_label: format_hm0,
                                  format_tm0_label : format_tm0,
                                  format_tp_label : format_tp})
        
        out_file_name = ''.join([so.output_fname,'_stats','.csv'])
            
        self.write_header(out_file_name, so)

        excel_file.to_csv(path_or_buf=out_file_name,
                          mode='a',
                          columns=[time_column,
                                   format_hm0_label,
                                   format_tm0_label,
                                   format_tp_label])
           
    def psd(self, so):
        
        columns = []
        value_dict = {}
        format_time = self.format_time(so, time_type = 'stat')
        time_column = self.time_column_format(so)
        
        columns.append(time_column)
        value_dict[time_column] = format_time
        
        # make a column for each frequency and get the energy for the respective frequency
        for x in range(0, len(so.stat_dictionary['Frequency'][0])):
            vals = []
            for y in range(0,len(so.stat_dictionary['Spectrum'])):
                vals.append(so.stat_dictionary['Spectrum'][y][x])
                
            column_name = ''.join([str(so.stat_dictionary['Frequency'][0][x])," ","Hz"])
            columns.append(column_name)
            value_dict[column_name] = vals

        excel_file = pd.DataFrame(value_dict)

        out_file_name = ''.join([so.output_fname, '_psd', '.csv'])
        self.write_header(out_file_name, so, write_type='PSD')

        excel_file.to_csv(path_or_buf=out_file_name,
                          mode='a',
                          columns=columns)
        
    def atmospheric_pressure(self, so):
        
        # adjust date times to appropriate time zone
        format_time = self.format_time(so, time_type = 'air')
        
        if self.int_units is True:
            format_air_pressure = so.raw_air_pressure
            format_air_pressure_label = 'Air Pressure in Decibars'
        else:
            format_air_pressure = so.raw_air_pressure * uc.DBAR_TO_INCHES_OF_MERCURY
            format_air_pressure_label = 'Air Pressure in Inches of Hg'

        time_column = self.time_column_format(so) 
            
        excel_file = pd.DataFrame({time_column: format_time,
                                  format_air_pressure_label: format_air_pressure})
        
        out_file_name = ''.join([so.output_fname,'_barometric_pressure','.csv'])
            
        self.write_header(out_file_name, so, air=True)

        excel_file.to_csv(path_or_buf=out_file_name,
                          mode='a',
                          columns=[time_column,
                                   format_air_pressure_label])
