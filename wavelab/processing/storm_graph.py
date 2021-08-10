"""
Module for creating Water Level visualizations
"""
import gc
import pytz
import pandas as pd
from datetime import datetime
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.gridspec as gridspec
import matplotlib.image as image
import matplotlib.ticker as ticker
from wavelab.processing.storm_options import StormOptions
from wavelab.utilities import unit_conversion as uc
from matplotlib.ticker import FormatStrFormatter
from wavelab.utilities.get_image import get_image
from wavelab.utilities.nc import get_frequency
matplotlib.use('Agg', warn=False)


class StormGraph(object):
    
    def __init__(self):
        self.canvas = None
        self.figure = None
        self.grid_spec = None
        self.time_nums = None
        self.wind_time_nums = None
        self.df = None
        self.international_units = False

    @staticmethod
    def format_date(x,arb=None):
        """Format dates so that they are padded away from the x-axis"""
        date_str = mdates.num2date(x).strftime('%b-%d-%Y \n %H:%M')
        return ''.join([' ','\n',date_str])
    
    def process_graphs(self, so):
        
        self.international_units = so.international_units

        if so.graph['Storm Tide with Unfiltered Water Level'].get() is True:
            if so.from_water_level_file is True:
                so.get_meta_data()
                so.get_air_meta_data()
                so.get_wave_water_level()
            else:
                so.get_meta_data()
                so.get_air_meta_data()
                so.get_raw_water_level()
                so.get_surge_water_level()

            so.test_water_elevation_below_sensor_orifice_elevation()

            self.create_header(so)
            self.storm_tide_and_unfiltered_water_level(so)

            plt.close('all')
            self.figure.clear()
            gc.collect()
            del self.df
            self.figure = None
            del self.figure
            self.canvas = None
            del self.canvas
            gc.collect()

        if so.graph['Storm Tide Water Level'].get() is True:
            so.get_meta_data()
            so.get_air_meta_data()
            so.get_raw_water_level()
            so.get_surge_water_level()
            so.test_water_elevation_below_sensor_orifice_elevation()
            self.create_header(so)
            self.storm_tide_water_level(so)

            self.figure.clear()
            plt.close("all")
            self.df = None
            del self.df
            self.figure = None
            del self.figure
            self.canvas = None
            del self.canvas
            gc.collect()
            
        if so.graph['Atmospheric Pressure'].get() is True:
            so.get_air_meta_data()
            so.get_air_time()
            so.get_raw_air_pressure()
            self.create_baro_header(so)
            self.atmospheric_graph(so)

            self.figure.clear()
            plt.close("all")
            self.df = None
            del self.df
            self.figure = None
            del self.figure
            self.canvas = None
            del self.canvas
            gc.collect()

    def create_header(self, so, wind=False):

        if wind is True:
            font = {'family' : 'DejaVu Sans',
                    'size'   : 10}

            matplotlib.rc('font', **font)
            plt.rcParams['figure.facecolor'] = 'white'
            self.figure = Figure(figsize=(16, 10))
            self.canvas = FigureCanvas(self.figure)
            self.figure.set_canvas(self.canvas)
        else:
            font = {'family' : 'DejaVu Sans',
                    'size'   : 14}

            matplotlib.rc('font', **font)
            plt.rcParams['figure.figsize'] = (16,10)
            plt.rcParams['figure.facecolor'] = 'white'

            self.figure = Figure(figsize=(16, 10))
            self.canvas = FigureCanvas(self.figure)
            self.figure.set_canvas(self.canvas)

        plt.rcParams['agg.path.chunksize'] = 10000

        first_date = uc.convert_ms_to_date(so.sea_time[0], pytz.UTC)
        last_date = uc.convert_ms_to_date(so.sea_time[-1], pytz.UTC)
        new_dates = uc.adjust_from_gmt([first_date, last_date], \
                                                    so.timezone, so.daylight_savings)

        first_date = mdates.date2num(new_dates[0])
        last_date = mdates.date2num(new_dates[1])

        del new_dates

        time = so.sea_time
        self.time_nums = np.linspace(first_date, last_date, len(time))
        self.time_nums2 = np.linspace(first_date, last_date, len(time))

        if so.level_troll is True:
            so.interpolated_air_pressure = np.zeros(so.surge_water_level.shape[0])

        if self.international_units is True:
            # create dataframe in meters
            graph_data = {'Pressure': pd.Series(so.interpolated_air_pressure,
                                                index=time),
                          # 'PressureQC': pd.Series(air_qc, index=time),
                          'SurgeDepth': pd.Series(so.surge_water_level,
                                                  index=time),
                          'RawDepth': pd.Series(so.raw_water_level,
                                                index=time)}
        else:
            # create dataframe
            graph_data = {'Pressure': pd.Series(so.interpolated_air_pressure * uc.DBAR_TO_INCHES_OF_MERCURY,
                                                index=time),
                          # 'PressureQC': pd.Series(air_qc, index=time),
                          'SurgeDepth': pd.Series(so.surge_water_level * uc.METER_TO_FEET,
                                                  index=time),
                          'RawDepth': pd.Series(so.raw_water_level * uc.METER_TO_FEET,
                                                index=time)
                    }

        self.df = pd.DataFrame(graph_data)

        del graph_data

        # Read images
        logo = image.imread(get_image('usgs.png'), None)

        # Create grids for section formatting
        if wind == False:
            self.grid_spec = gridspec.GridSpec(2, 2,
                                               width_ratios=[1, 2],
                                               height_ratios=[1, 4])
        else:

            first_date = uc.convert_ms_to_date(so.wind_time[0], pytz.UTC)
            last_date = uc.convert_ms_to_date(so.wind_time[-1], pytz.UTC)
            new_dates = uc.adjust_from_gmt([first_date,
                                            last_date],
                                            so.timezone,
                                            so.daylight_savings)

            first_date = mdates.date2num(new_dates[0])
            last_date = mdates.date2num(new_dates[1])

            self.wind_time_nums = np.linspace(first_date, last_date, len(so.wind_time))
            self.grid_spec = gridspec.GridSpec(3, 2,
                               width_ratios=[1,2],
                               height_ratios=[1,2,2]
                               )

        # ---------------------------------------Logo Section
        ax2 = self.figure.add_subplot(self.grid_spec[0,0])
        ax2.set_axis_off()

        ax2.axes.get_yaxis().set_visible(False)
        ax2.axes.get_xaxis().set_visible(False)
        pos1 = ax2.get_position()  # get the original position
        pos2 = [pos1.x0, pos1.y0 + .07,  pos1.width, pos1.height]
        ax2.set_position(pos2)  # set a new position
        ax2.imshow(logo)
        del logo

    def create_baro_header(self, so):
            
        font = {'family': 'DejaVu Sans',
                'size': 14}
    
        matplotlib.rc('font', **font)
        plt.rcParams['figure.figsize'] = (16, 10)
        plt.rcParams['figure.facecolor'] = 'white'
        plt.rcParams['agg.path.chunksize'] = 10000

        self.figure = Figure(figsize=(16, 10))
        self.canvas = FigureCanvas(self.figure)
        self.figure.set_canvas(self.canvas)
        
        first_date = uc.convert_ms_to_date(so.air_time[0], pytz.UTC)
        last_date = uc.convert_ms_to_date(so.air_time[-1], pytz.UTC)
        new_dates = uc.adjust_from_gmt([first_date,
                                        last_date],
                                        so.timezone,
                                        so.daylight_savings)
        
        first_date = mdates.date2num(new_dates[0])
        last_date = mdates.date2num(new_dates[1])

        del new_dates
       
        self.time_nums = np.linspace(first_date, last_date, len(so.air_time))

        # Read images
        logo = image.imread(get_image('usgs.png'), None)
    
        #Create grids for section formatting
        self.grid_spec = gridspec.GridSpec(2, 2,
                           width_ratios=[1,2],
                           height_ratios=[1,4]
                           )
    
        # ---------------------------------------Logo Section
        ax2 = self.figure.add_subplot(self.grid_spec[0,0])
        ax2.set_axis_off()
       
        ax2.axes.get_yaxis().set_visible(False)
        ax2.axes.get_xaxis().set_visible(False)
        pos1 = ax2.get_position()  # get the original position
        pos2 = [pos1.x0, pos1.y0 + .07,  pos1.width, pos1.height] 
        ax2.set_position(pos2)  # set a new position
        ax2.imshow(logo)
        del logo

    def storm_tide_and_unfiltered_water_level(self, so):

        ax = self.figure.add_subplot(self.grid_spec[1, 0:])
        pos1 = ax.get_position()  # get the original position
        pos2 = [pos1.x0, pos1.y0, pos1.width, pos1.height + .06]
        ax.set_position(pos2)  # set a new position

        graph_stormtide = get_frequency(so.sea_fname) >= 1 / 30.
        # create the second graph title

        first_title = "Storm Tide Water Elevation, Latitude: %.4f Longitude: %.4f STN Site ID: %s" \
                      % (so.latitude, so.longitude, so.stn_station_number)
        second_title = "Barometric Pressure, Latitude: %.4f Longitude: %.4f STN Site ID: %s" \
                       % (so.air_latitude, so.air_longitude, so.air_stn_station_number)

        ax.text(0.5, 1.055, first_title, \
                va='center', ha='center', transform=ax.transAxes)
        ax.text(0.5, 1.015, second_title, \
                va='center', ha='center', transform=ax.transAxes)

        ax.set_xlabel('Timezone: %s' % so.timezone)

        # get the twin axis to share the same x axis
        par1 = ax.twinx()
        pos1 = par1.get_position()  # get the original position
        pos2 = [pos1.x0, pos1.y0, pos1.width, pos1.height + .06]
        par1.set_position(pos2)  # set a new position

        if self.international_units is True:
            ax.set_ylabel('Water Elevation in Meters above Datum (%s)' % so.datum)
            par1.set_ylabel('Barometric Pressure in Decibars')
        else:
            ax.set_ylabel('Water Elevation in Feet above Datum (%s)' % so.datum)
            par1.set_ylabel('Barometric Pressure in Inches of Mercury')

        # plot major grid lines
        ax.grid(b=True, which='major', color='grey', linestyle="-")

        # x axis formatter for dates (function format_date() below)
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(self.format_date))

        # get minimum and maximum depth
        depth_min_start = np.min(self.df.RawDepth)

        depth_idx = np.nanargmax(so.raw_water_level)
        tide_idx = np.nanargmax(so.surge_water_level)

        # get the sensor min, max depth, and storm tide in max in the appropriate units
        if self.international_units is True:
            sensor_min = np.min(so.sensor_orifice_elevation)
            depth_max = so.raw_water_level[depth_idx]
            tide_max = so.surge_water_level[tide_idx]
        else:
            sensor_min = np.min(so.sensor_orifice_elevation * uc.METER_TO_FEET)
            depth_max = so.raw_water_level[depth_idx] * uc.METER_TO_FEET
            tide_max = so.surge_water_level[tide_idx] * uc.METER_TO_FEET

        # calculate and format the datetime of the unfiltered and storm tide maximum

        tide_time = mdates.num2date(self.time_nums[tide_idx], pytz.timezone('GMT'))
        depth_time = mdates.num2date(self.time_nums[depth_idx], pytz.timezone('GMT'))

        #         tide_time, depth_time = uc.adjust_from_gmt([tide_time,depth_time], \
        #                                          so.timezone,so.daylight_savings)

        tide_time = datetime.strftime(tide_time, '%Y-%m-%d %H:%M:%S')
        depth_time = datetime.strftime(depth_time, '%Y-%m-%d %H:%M:%S')

        depth_num = self.time_nums[depth_idx]
        tide_num = self.time_nums[tide_idx]

        depth_min = np.floor(depth_min_start * 100.0) / 100.0

        # scale the minimum depth to be above minimum in graph
        if depth_min > (sensor_min - .02):
            depth_min = sensor_min - .02

        lim_max = np.ceil(depth_max * 100.0) / 100.0

        # scale y axis of water level data
        # plot the pressure, depth, and min depth

        if so.wlYLims is None:
            if depth_min < 0:
                y_min = depth_min * 1.10
                ax.set_ylim([y_min, lim_max * 1.2])
            else:
                y_min = depth_min * .9
                ax.set_ylim([y_min, lim_max * 1.20])
        else:
            so.wlYLims[0] = float("{0:.2f}".format(so.wlYLims[0]))
            so.wlYLims[1] = float("{0:.2f}".format(so.wlYLims[1]))
            ax.set_ylim([so.wlYLims[0], so.wlYLims[1]])

        # changes scale so the air pressure is more readable
        if self.international_units is True:
            minY = np.min(self.df.Pressure) * .99
            maxY = np.max(self.df.Pressure) * 1.01
        else:
            minY = np.floor(np.min(self.df.Pressure))
            maxY = np.ceil(np.max(self.df.Pressure))

            # adjust the barometric pressure y axis
        if so.baroYLims is None:
            par1.set_ylim([minY, maxY])
            if self.international_units is False:
                par1.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        else:
            so.baroYLims[0] = float("{0:.1f}".format(so.baroYLims[0]))
            so.baroYLims[1] = float("{0:.1f}".format(so.baroYLims[1]))
            if so.baroYLims[1] - so.baroYLims[0] < .5:
                par1.set_yticks(np.arange(so.baroYLims[0], so.baroYLims[1], .1))

            par1.set_ylim([so.baroYLims[0], so.baroYLims[1]])

        # plot the pressure, depth, and min depth

        legend_entries = []
        legend_names = []

        def add_entry(plt_entry, name):
            legend_entries.append(plt_entry)
            legend_names.append(name)

        entry, = ax.plot(self.time_nums, self.df.RawDepth, color='#969696', alpha=.75)
        add_entry(entry, 'Unfiltered Water Elevation')

        if so.level_troll is False:
            entry, = par1.plot(self.time_nums, self.df.Pressure, color="red")
            add_entry(entry, 'Barometric Pressure')

        if graph_stormtide:
            entry, = ax.plot(self.time_nums, self.df.SurgeDepth, color="#045a8d" )
            add_entry(entry, 'Storm Tide (Lowpass Filtered) Water Elevation')

        entry, = ax.plot(self.time_nums, np.repeat(sensor_min, len(self.df.SurgeDepth)), linestyle="--",
                      color="#fd8d3c")
        add_entry(entry, "Minimum Recordable Water Elevation")

        ref = False
        legend_y = 1.399
        inst_accuracy_y = 1.13
        if so.reference_elevation is not None and so.reference_elevation != '':
            ref = True
            entry = ax.axhspan(so.reference_elevation, tide_max, alpha=0.25,
                                             color='#add8e6', linewidth=0)
            add_entry(entry, 'Water Depth Above %s' % so.reference_name)
            entry, = ax.plot(self.time_nums, np.repeat(so.reference_elevation, len(self.df.SurgeDepth)),
                                          linestyle="--", color="#000000")
            add_entry(entry, so.reference_name)
            inst_accuracy_y = 1.105
            legend_y = 1.44

        entry, = ax.plot(depth_num, depth_max, 'o', markersize=10, color='#969696', alpha=1)
        add_entry(entry, 'Maximum Unfiltered Water Elevation')
        if graph_stormtide:
            entry, = ax.plot(tide_num, tide_max, '^', markersize=10, color='#045a8d', alpha=1)
            add_entry(entry, 'Maximum Storm Tide Water Elevation')

        if self.international_units:
            max_storm_tide = "Maximum Unfiltered Water Elevation, meters above datum = %.2f at %s" \
                % (depth_max, depth_time)
            max_storm_tide += "\nMaximum Storm Tide Water Elevation, meters above datum = %.2f at %s" \
                % (tide_max, tide_time) if graph_stormtide else ""
            ax.text(0.645, inst_accuracy_y, 'Combined Instrument Error (m): %f' %
                    so.combined_level_accuracy_in_meters,
                    va='center', ha='left', transform=ax.transAxes,
                    fontsize=10)
        else:
            max_storm_tide = "Maximum Unfiltered Water Elevation, feet above datum = %.2f at %s" \
                             % (depth_max, depth_time)
            max_storm_tide += "\nMaximum Storm Tide Water Elevation, feet above datum = %.2f at %s" \
                              % (tide_max, tide_time) if graph_stormtide else ""
            ax.text(0.645, inst_accuracy_y, 'Combined Instrument Error (ft): %f' %
                    (so.combined_level_accuracy_in_meters * uc.METER_TO_FEET),
                    va='center', ha='left', transform=ax.transAxes,
                    fontsize=10)

        stringText = par1.text(0.5, 0.948, max_storm_tide, \
                               bbox={'facecolor': 'white', 'alpha': 1, 'pad': 10}, \
                               va='center', ha='center', transform=par1.transAxes)
        stringText.set_size(11)

        # Legend options not needed but for future reference
        legend = ax.legend(legend_entries,
                           legend_names,
                           bbox_to_anchor=(.95, legend_y),
                           loc=1,
                           borderaxespad=0.0,
                           prop={'size': 10.3},
                           frameon=False,
                           numpoints=1,
                           title="EXPLANATION")

        legend.get_title().set_position((-120, 0))

        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

        file_name = ''.join([so.output_fname, '_stormtide_unfiltered', '.jpg'])
        self.figure.savefig(file_name)
        for x in legend_entries:
            x = None
            del x
        gc.collect()

    def storm_tide_water_level(self, so):
        ax = self.figure.add_subplot(self.grid_spec[1,0:])
        pos1 = ax.get_position() # get the original position 
        pos2 = [pos1.x0, pos1.y0,  pos1.width, pos1.height + .06] 
        ax.set_position(pos2) # set a new position
        
        first_title = "Storm Tide Water Elevation, Latitude: %.4f Longitude: %.4f STN Site ID: %s" \
                % (so.latitude,so.longitude,so.stn_station_number)
        second_title = "Barometric Pressure, Latitude: %.4f Longitude: %.4f STN Site ID: %s" \
                % (so.air_latitude,so.air_longitude,so.air_stn_station_number)

        ax.text(0.5, 1.065,first_title,  \
                va='center', ha='center', transform=ax.transAxes)
        ax.text(0.5, 1.015,second_title,  \
                va='center', ha='center', transform=ax.transAxes)
        
        par1 = ax.twinx()
        pos1 = par1.get_position() # get the original position 
        pos2 = [pos1.x0, pos1.y0,  pos1.width, pos1.height + .06] 
        par1.set_position(pos2) # set a new position
    
        if self.international_units is True:
            ax.set_ylabel('Water Elevation in Meters above Datum (%s)' % so.datum)
            par1.set_ylabel('Barometric Pressure in Decibars')
        else:
            ax.set_ylabel('Water Elevation in Feet above Datum (%s)' % so.datum)
            par1.set_ylabel('Barometric Pressure in Inches of Mercury')
       
    
        # plot major grid lines
        ax.grid(b=True, which='major', color='grey', linestyle="-")
    
        # x axis formatter for dates (function format_date() below)
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(self.format_date))
        ax.set_xlabel('Timezone: %s' % so.timezone)
        
        # plan on rebuilding the flow of execution, ignore spaghetti for now
        depth_min_start = np.nanmin(so.surge_water_level)
        
        tide_idx = np.nanargmax(so.surge_water_level)
        
        if self.international_units is True:
            sensor_min = np.min(so.sensor_orifice_elevation)
            tide_max = so.surge_water_level[tide_idx]
        else:
            sensor_min = np.min(so.sensor_orifice_elevation * uc.METER_TO_FEET)
            tide_max = so.surge_water_level[tide_idx] * uc.METER_TO_FEET

        tide_time = mdates.num2date(self.time_nums[tide_idx], pytz.timezone('GMT'))
        
        tide_time = datetime.strftime(tide_time, '%Y-%m-%d %H:%M:%S')
        tide_num = self.time_nums[tide_idx]

        depth_min = np.floor(depth_min_start * 100.0)/100.0
       
        if depth_min > (sensor_min - .02):
            depth_min = sensor_min - .02
            
        lim_max = np.ceil(tide_max * 100.0)/100.0

        if so.wlYLims is None:
                if depth_min < 0:
                    ax.set_ylim([depth_min * 1.10,lim_max * 1.20])
                else:
                    ax.set_ylim([depth_min * .9,lim_max * 1.20])
        else:
            so.wlYLims[0] = float("{0:.2f}".format(so.wlYLims[0]))
            so.wlYLims[1] = float("{0:.2f}".format(so.wlYLims[1]))
            ax.set_ylim([so.wlYLims[0],so.wlYLims[1]])
#
        # changes scale so the air pressure is more readable
        if self.international_units is True:
            minY = np.min(self.df.Pressure)  * .99
            maxY = np.max(self.df.Pressure)  * 1.01
        else:
            minY = np.floor(np.min(self.df.Pressure))
            maxY = np.ceil(np.max(self.df.Pressure)) 
        
        # adjust the barometric pressure y axis
        if so.baroYLims is None:
                par1.set_ylim([minY,maxY])
                if self.international_units is False:
                    par1.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        else:
            so.baroYLims[0] = float("{0:.1f}".format(so.baroYLims[0]))
            so.baroYLims[1] = float("{0:.1f}".format(so.baroYLims[1]))
            if so.baroYLims[1] - so.baroYLims[0] < .5:
                par1.set_yticks(np.arange(so.baroYLims[0],so.baroYLims[1],.1))
                
            par1.set_ylim([so.baroYLims[0],so.baroYLims[1]])
    
        # plot the pressure, depth, and min depth

        if self.level_troll is False:
            p1, = par1.plot(self.time_nums,self.df.Pressure, color="red")
        p2, = ax.plot(self.time_nums,self.df.SurgeDepth, color="#045a8d")
        p3, = ax.plot(self.time_nums,np.repeat(sensor_min, len(self.df.SurgeDepth)), linestyle="--", color="#fd8d3c")
        p6,  = ax.plot(tide_num,tide_max, '^', markersize=10, color='#045a8d', alpha=1)

        ref = False
        legend_y = 1.355
        inst_accuracy_y = 1.155
        if so.reference_elevation is not None and so.reference_elevation != '':
            ref = True
            p7 = ax.axhspan(so.reference_elevation, tide_max, alpha=0.25, color='#add8e6', linewidth=0)
            p8, = ax.plot(self.time_nums, np.repeat(so.reference_elevation, len(self.df.SurgeDepth)), linestyle="--",
                          color="#000000")
            legend_y = 1.385
            inst_accuracy_y = 1.115

        if self.international_units is True:
            max_storm_tide = "Maximum Storm Tide Water Elevation, meters above datum = %.2f at %s" \
            % (tide_max, tide_time)

            ax.text(0.645, inst_accuracy_y, 'Combined Instrument Error (m): %f' %
                    so.combined_level_accuracy_in_meters,
                    va='center', ha='left', transform=ax.transAxes,
                    fontsize=10)
        else:
            max_storm_tide = "Maximum Storm Tide Water Elevation, feet above datum = %.2f at %s" \
            % (tide_max, tide_time)

            ax.text(0.645, inst_accuracy_y, 'Combined Instrument Error (ft): %f' %
                    (so.combined_level_accuracy_in_meters * uc.METER_TO_FEET),
                    va='center', ha='left', transform=ax.transAxes,
                    fontsize=10)
        
        stringText = par1.text(0.5, 0.948, max_storm_tide,
                bbox={'facecolor':'white', 'alpha': 1, 'pad': 10},
                va='center', ha='center', transform=par1.transAxes)
        stringText.set_size(11)
    
        # Legend options not needed but for future reference

        if self.level_troll is False:
            legend_entries = [p2,p3,p1,p6]
            legend_names = [
            'Storm Tide (Lowpass Filtered) Water Elevation',
            'Minimum Recordable Water Elevation',
            'Barometric Pressure',
            'Maximum Storm Tide Water Elevation'
            ]
        else:
            legend_entries = [p2, p3, p6]
            legend_names = [
                'Storm Tide (Lowpass Filtered) Water Elevation',
                'Minimum Recordable Water Elevation',
                'Maximum Storm Tide Water Elevation'
            ]

        if ref is True:
            legend_entries.append(p7)
            legend_entries.append(p8)
            legend_names.append('Water Depth Above %s' % so.reference_name)
            legend_names.append(so.reference_name)

        legend = ax.legend(legend_entries,
                           legend_names,
                           bbox_to_anchor=(.95, legend_y),
                           loc=1,
                           borderaxespad=0.0,
                           prop={'size': 10.3},
                           frameon=False,
                           numpoints=1,
                           title="EXPLANATION")

        legend.get_title().set_position((-120, 0))
        
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
         
        file_name = ''.join([so.output_fname,'_stormtide','.jpg'])
        self.figure.savefig(file_name)

        for x in legend_entries:
            x = None
            del x
        gc.collect()

    def atmospheric_graph(self, so):
        ax = self.figure.add_subplot(self.grid_spec[1,0:])
        pos1 = ax.get_position() # get the original position 
        pos2 = [pos1.x0, pos1.y0,  pos1.width, pos1.height + .06] 
        ax.set_position(pos2) # set a new position
        
        first_title = "Barometric Pressure, Latitude: %.4f Longitude: %.4f STN Site ID: %s" \
            % (so.air_latitude,so.air_longitude,so.air_stn_station_number)
   
        ax.text(0.5, 1.03, first_title,
                va='center', ha='center', transform=ax.transAxes)

        if self.international_units is True:
            ax.text(0.735, 1.26, 'Instrument Error (dbar): %f' %
                    so.extract_level_accuracy(so.air_fname, 'air_pressure'),
                    va='center', ha='left', transform=ax.transAxes,
                    fontsize=10)
        else:
            ax.text(0.735, 1.26, 'Instrument Error (inHg): %f' %
                    (so.extract_level_accuracy(so.air_fname, 'air_pressure') * uc.DBAR_TO_INCHES_OF_MERCURY),
                    va='center', ha='left', transform=ax.transAxes,
                    fontsize=10)
        
        ax.set_xlabel('Timezone: %s' % so.timezone)
  
        if self.international_units is True:
            ax.set_ylabel('Barometric Pressure in Decibars')
        else:
            ax.set_ylabel('Barometric Pressure in Inches of Mercury')
    
        # plot major grid lines
        
        ax.grid(b=True, which='major', color='grey', linestyle="-")
    
        # x axis formatter for dates (function format_date() below)
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(self.format_date))
    
        # convert to appropriate units
        if self.international_units is True:
            air_pressure = so.raw_air_pressure
        else:
            air_pressure = so.raw_air_pressure * uc.DBAR_TO_INCHES_OF_MERCURY

        # adjust the y axis
        if so.baroYLims is not None:
            so.baroYLims[0] = float("{0:.1f}".format(so.baroYLims[0]))
            so.baroYLims[1] = float("{0:.1f}".format(so.baroYLims[1]))
            if so.baroYLims[1] - so.baroYLims[0] < .5:
                    ax.set_yticks(np.arange(so.baroYLims[0],so.baroYLims[1],.1))
            ax.set_ylim([so.baroYLims[0],so.baroYLims[1]])
        else:
            ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
   
        # plot the pressure, depth, and min depth
        p1, = ax.plot(self.time_nums,air_pressure, color="red")
        
        #  options not needed but for future reference
        legend = ax.legend([p1],
                           ['Barometric Pressure'],
                           bbox_to_anchor=(.89, 1.355),
                           loc=1, borderaxespad=0.0,
                           prop={'size':10.3},
                           frameon=False,
                           numpoints=1,
                           title="EXPLANATION")
        legend.get_title().set_position((-28, 0))
         
        file_name = ''.join([so.output_fname,'_barometric_pressure','.jpg'])
        self.figure.savefig(file_name)

        p1 = None
        del p1
        gc.collect()


class Bool(object):
    
    def __init__(self, val):
        self.val = val
         
    def get(self):
        return self.val


if __name__ == '__main__':
    import os

    so = StormOptions()
    so.clip = False
    so.from_water_level_file = False

    project_path = '../../documentation/data'
    # so.air_fname = project_path + '/NCCAR12248_9983816_air.csv.nc'
    # so.sea_fname = project_path + '/NCCAR00007_1511451_sea.csv.nc'
    so.air_fname = project_path + '/1_NYRIC_bp.nc'
    so.sea_fname = project_path + '/1_NYRIC_wv.nc'

    so.from_water_level_file = False
    so.reference_name = 'Test Elev'
    so.reference_elevation = 2.5
    so.format_output_fname(project_path + '/nyric_reference')
    so.timezone = 'US/Eastern'
    so.daylight_savings = False
    so.graph['Storm Tide with Unfiltered Water Level'] = Bool(True)
    so.graph['Storm Tide Water Level'] = Bool(True)
    so.graph['Atmospheric Pressure'] = Bool(False)
    so.level_troll = False

    sg = StormGraph()
    so.international_units = False
    sg.process_graphs(so)
