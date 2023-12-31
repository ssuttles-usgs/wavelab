"""
Contains classes that parse CSV files output by pressure sensors.
"""

from datetime import datetime
from wavelab.utilities import edit_netcdf, unit_conversion as uc
import numpy as np
import pandas as pd
import pytz
import re


def find_first(fname, expr):
    """Search for the first occurrence of expr in fname, return the line no."""

    with open(fname, 'r') as text:
        for i, line in enumerate(text):
            if re.search(expr, line):
                return i + 1


def get_date_format(date):
    "Return datatime format string given a string of datetime data."
    date_formats = ['%m/%d/%Y %H:%M:%S', '%m/%d/%Y %H:%M:%S.%f', '%m/%d/%Y %I:%M:%S %p', '%m/%d/%Y %I:%M:%S.%f %p',
                '%m/%d/%Y %H:%M', '%m/%d/%Y %I:%M %p', '%m/%d/%y %I:%M:%S %p', '%m/%d/%y %I:%M:%S.%f %p',
                '%m/%d/%y %H:%M:%S', '%m/%d/%y %H:%M:%S.%f', '%m/%d/%y %H:%M', '%m/%d/%y %I:%M %p',
                '%Y/%m/%d %H:%M:%S', '%Y/%m/%d %H:%M:%S.%f', '%Y/%m/%d %I:%M:%S %p', '%Y/%m/%d %I:%M:%S.%f %p',
                '%Y/%m/%d %H:%M', '%Y/%m/%d %I:%M %p', '%m-%d-%Y %H:%M:%S', '%m-%d-%Y %H:%M:%S.%f',
                '%m-%d-%Y %I:%M:%S %p', '%m-%d-%Y %I:%M:%S.%f %p', '%m-%d-%Y %H:%M %f', '%m-%d-%Y %I:%M %p',
                '%m-%d-%y %H:%M:%S', '%m-%d-%y %H:%M:%S.%f', '%m-%d-%y %I:%M:%S %p', '%m-%d-%y %I:%M:%S.%f %p',
                '%m-%d-%y %H:%M', '%m-%d-%y %I:%M %p', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S.%f',
                '%Y-%m-%d %I:%M:%S %p', '%Y-%m-%d %I:%M:%S.%f %p', '%Y-%m-%d %H:%M', '%Y-%m-%d %I:%M %p',
                '%Y.%m.%d %H:%M:%S', '%Y.%m.%d %H:%M:%S.%f', '%Y.%m.%d %I:%M:%S %p', '%Y.%m.%d %I:%M:%S.%f %p',
                '%Y.%m.%d %H:%M', '%Y.%m.%d %I:%M %p', '%m.%d.%Y %H:%M:%S', '%m.%d.%Y %H:%M:%S.%f',
                '%m.%d.%Y %I:%M:%S %p', '%m.%d.%Y %H:%M', '%m.%d.%Y %I:%M %p', '%m.%d.%Y %I:%M:%S.%f %p',
                '%m.%d.%y %H:%M:%S', '%m.%d.%y %H:%M:%S.%f', '%m.%d.%y %I:%M:%S %p', '%m.%d.%y %I:%M:%S.%f %p',
                '%m.%d.%y %H:%M', '%m.%d.%y %I:%M %p'
               ]
    date_format_string = "None"

    for d in date_formats:
        try:
            datetime.strptime(date, d)
            date_format_string = d
            break
        except:
            pass

    return date_format_string


class Hobo(edit_netcdf.NetCDFWriter):
    """derived class for hobo csv files """

    def __init__(self):
        self.timezone_marker = "time zone"
        super().__init__()


    def read(self):
        """load the data from in_filename
        only parse the initial datetime = much faster"""

        self.get_serial()

        skip_index = find_first(self.in_filename, '"#"')
        if skip_index is None:
            skip_index = find_first(self.in_filename, '#')

        df = pd.read_table(self.in_filename, skiprows=skip_index, header=None,
                           engine='c', sep=',', usecols=(1,2,3))
        df = df.dropna()

        if isinstance(df[2][0], str):
            vals = df[3].values
            date1, date2 = df[1][0] + ' ' + df[2][0], df[1][1] + ' ' + df[2][1]
        else:
            vals = df[2].values
            date1, date2 = df[1][0], df[1][1]

        # Determine the format of the datetime
        self.date_format_string = get_date_format(date1)
        
        # If the datetime format is not recognized...
        if self.date_format_string == "None":
            self.bad_data = True
            self.error_message = 'Error! Date time format was not recognized. Try changing it to this format: mm/dd/YYYY HH:MM:SS.MS'
        
        else:
            try:
                first_stamp = uc.datestring_to_ms(date1, self.date_format_string,
                                                self.tz_info, self.daylight_savings)
                second_stamp = uc.datestring_to_ms(date2, self.date_format_string,
                                                self.tz_info, self.daylight_savings)
            except:
                try:
                    first_stamp = uc.datestring_to_ms(date1, self.date_format_string2,
                                                    self.tz_info, self.daylight_savings)
                    second_stamp = uc.datestring_to_ms(date2, self.date_format_string2,
                                                    self.tz_info, self.daylight_savings)
                except:
                    first_stamp = uc.datestring_to_ms(date1, self.date_format_string3,
                                                    self.tz_info, self.daylight_savings)
                    second_stamp = uc.datestring_to_ms(date2, self.date_format_string3,
                                                    self.tz_info, self.daylight_savings)

            timestep = second_stamp - first_stamp
            # check time step:
            if timestep <= 0:
                self.bad_data = True
                self.error_message = 'Error! Time step is zero. Check the datetime column of the input data.'

            else:
                self.frequency = 1000 / (second_stamp - first_stamp)
                
                try:
                    start_ms = uc.datestring_to_ms(date1, self.date_format_string,
                                                self.tz_info, self.daylight_savings)
                except:
                    try:
                        start_ms = uc.datestring_to_ms(date1, self.date_format_string2,
                                                    self.tz_info, self.daylight_savings)
                    except:
                        start_ms = uc.datestring_to_ms(date1, self.date_format_string3,
                                                    self.tz_info, self.daylight_savings)
                    
                self.utc_millisecond_data = uc.generate_ms(start_ms, df.shape[0], self.frequency)

                self.pressure_data = vals * uc.PSI_TO_DBAR
            
    def get_serial(self):
        self.instrument_serial = "not found"
        with open(self.in_filename, 'r') as text:
            for i, line in enumerate(text):
                if re.search('[0-9]{6}', line):
                    match = re.search('[0-9]{6}', line)
                    self.instrument_serial = match.group(0)
                    break


class House(edit_netcdf.NetCDFWriter):
    """Processes files coming out of the USGS-made sensors"""

    def __init__(self):
        self.timezone_marker = "time zone"
        self.temperature_data = None
        super(House, self).__init__()
        self.frequency = 4
        self.date_format_string = '%Y.%m.%d %H:%M:%S '

    def read(self):
        """Load the data from in_filename"""

        skip_index = find_first(self.in_filename, '^[0-9]{4},[0-9]{4}$') - 1
        df = pd.read_table(self.in_filename, skiprows=skip_index, header=None,
                           engine='c', sep=',', names=('a', 'b'))
        self.pressure_data = np.array([
            uc.USGS_PROTOTYPE_V_TO_DBAR(np.float64(x))
            for x in df[df.b.isnull() == False].a])
        self.temperature_data = [
            uc.USGS_PROTOTYPE_V_TO_C(np.float64(x))
            for x in df[df.b.isnull() == False].b]
        with open(self.in_filename, 'r') as wavelog:
            for x in wavelog:
                # second arg has extra space that is unnecessary
                if re.match('^[0-9]{4}.[0-9]{2}.[0-9]{2}', x):
                    start_ms = uc.datestring_to_ms(x, self.date_format_string)
                    self.utc_millisecond_data = uc.generate_ms(start_ms,
                                                               len(self.pressure_data),
                                                               self.frequency)
                    break


class Leveltroll(edit_netcdf.NetCDFWriter):
    """derived class for leveltroll ascii files"""
    
    def __init__(self):
        self.numpy_dtype = np.dtype([("seconds", np.float32),
                                     ("pressure", np.float32)])
        self.record_start_marker = "Date and Time,Seconds"
        self.timezone_marker = "time zone"
        super().__init__()
        self.date_format_string = "%m/%d/%Y %H:%M"
        # self.date_format_string = "%m/%d/%Y %H:%M:%S "
        self.temperature_data = None

    def read(self):
        """load the data from in_filename
        only parse the initial datetime = much faster"""
        

        self.get_serial()
        skip_index = find_first(self.in_filename, 'Date and Time,Seconds')
#         data = pd.read_table(self.in_filename, skiprows=skip_index, header=None,
#                            engine='c', sep=',', usecols=(0,1,2,3))

        data = pd.read_table(self.in_filename, skiprows=skip_index, header=None,
                            engine='c', sep=',', usecols=(0,1,2))
        
        self.data_start = uc.datestring_to_ms(data[0][1], self.date_format_string,
                                           self.tz_info, self.daylight_savings)
        # self.data_start2 = uc.datestring_to_ms(data[1][1], self.date_format_string,
        #                                    self.tz_info, self.daylight_savings)

        timestep = int(data[1][1] - data[1][0])
        # check time step:
        if timestep <= 0:
            self.bad_data = True
            self.error_message = 'Error! Time step is zero. Check the datetime column of the input data.'
        
        else:
            self.frequency = 1 / timestep
            
            self.utc_millisecond_data = uc.generate_ms(self.data_start, len(data[0]), 
                                                    self.frequency)
            self.pressure_data = (data[2].values + self.offset ) * uc.PSI_TO_DBAR
            self.pressure_data += self.offset
            
            if self.included_baro == True:
                self.air_pressure_data = data[2].values * uc.PSI_TO_DBAR
        

    def get_serial(self):
        self.instrument_serial = "not found"
        with open(self.in_filename, 'r') as text:
            for i, line in enumerate(text):
                if re.search('Serial Number', line):
                    match = re.search('[0-9]{6}', line)
                    self.instrument_serial = match.group(0)
                    break


class MeasureSysLogger(edit_netcdf.NetCDFWriter):
    """derived class for Measurement Systems cvs files"""

    def __init__(self):
        self.timezone_marker = "time zone"
        super(MeasureSysLogger, self).__init__()
        self.frequency = 4
        self.date_format_string = '%m/%d/%Y %I:%M:%S.%f %p'
        self.date_format_string2 = '%m/%d/%Y %H:%M:%S.%f'

    def read(self):
        """load the data from in_filename
        only parse the initial datetime = much faster"""

        self.get_serial()
        skip_index = find_first(self.in_filename, '^ID') - 1
        # for skipping lines in case there is calibration header data
        df = pd.read_table(self.in_filename, skiprows=skip_index + 1, header=None,
                           engine='c', sep=',', usecols=[3, 4, 5])
        
        try:
            self.data_start = uc.datestring_to_ms(df[3][3][1:],
                                                  self.date_format_string, self.tz_info, self.daylight_savings)
            second_stamp = uc.datestring_to_ms(df[3][4][1:],
                                               self.date_format_string, self.tz_info, self.daylight_savings)
            
            timestep = second_stamp - self.data_start
            # check time step:
            if timestep <= 0:
                self.bad_data = True
                self.error_message = 'Error! Time step is zero. Check the datetime column of the input data.'
            
            else:
                self.frequency = 1000 / (second_stamp - self.data_start)
                self.pressure_data = df[5].values * uc.PSI_TO_DBAR
                start_ms = uc.datestring_to_ms('%s' % df[3][0][1:], self.date_format_string, self.tz_info, self.daylight_savings)
        
        except:
            self.data_start = uc.datestring_to_ms(df[3][3][1:],
                                                  self.date_format_string2, self.tz_info, self.daylight_savings)
            second_stamp = uc.datestring_to_ms(df[3][4][1:],
                                               self.date_format_string2, self.tz_info, self.daylight_savings)
            
            timestep = second_stamp - self.data_start
            # check time step:
            if timestep <= 0:
                self.bad_data = True
                self.error_message = 'Error! Time step is zero. Check the datetime column of the input data.'
            
            else:
                self.frequency = 1000 / (second_stamp - self.data_start)
                self.pressure_data = df[5].values * uc.PSI_TO_DBAR
                start_ms = uc.datestring_to_ms('%s' % df[3][0][1:], self.date_format_string2, self.tz_info, self.daylight_savings)
            
        self.utc_millisecond_data = uc.generate_ms(start_ms, df.shape[0], self.frequency)
 
            
    def get_serial(self):
        self.instrument_serial = "not found"
        with open(self.in_filename, 'r') as text:
            for i, line in enumerate(text):
                if line.find('Transducer Serial') > -1:
                    match = re.search("[0-9]{7}", line)
                    self.instrument_serial = match.group(0)
                    break


class RBRSolo(edit_netcdf.NetCDFWriter):
    """derived class for RBR solo engineer text files, (exported via ruskin software)"""

    def __init__(self):
        self.timezone_marker = "time zone"
        super().__init__()
        self.frequency = 4
#         self.date_format_string = '%d-%b-%Y %H:%M:%S.%f'
        self.date_format_string = '%Y-%m-%d %H:%M:%S.%f'

    def read(self):
        """load the data from in_filename
        only parse the initial datetime = much faster
        """
#         skip_index = find_first(self.in_filename, '^[0-9]{2}-[A-Z]{1}[a-z]{2,8}-[0-9]{4}')
        skip_index = find_first(self.in_filename, '^[0-9]{4}-[0-9]{2}-[0-9]{2}')
        df = pd.read_csv(self.in_filename, skiprows=skip_index,
                         header=None, engine='c', usecols=[0, 1, 2], sep=',')
        
#         self.datestart = uc.datestring_to_ms('%s %s' % (df[0][0], df[1][0]), self.date_format_string)
        self.datestart = uc.datestring_to_ms('%s' % (df[0][0]),
                                             self.date_format_string,
                                             self.tz_info,
                                             self.daylight_savings)
        self.utc_millisecond_data = uc.generate_ms(self.datestart, df.shape[0] - 1,
                                                    self.frequency)
        self.pressure_data = np.array([x for x in df[1][:-1]])


class Waveguage(edit_netcdf.NetCDFWriter):
    """Reads in an ASCII file output by a Waveguage pressure sensor
    from Ocean Sensor Systems Inc.

    This class reads in data from a plaintext output file into a
    pandas Dataframe. This is then translated into numpy ndarrays
    and written to a netCDF binary file."""

    def __init__(self):
        super(Waveguage, self).__init__()

    def read(self):
        """Sets start_time to a datetime object, utc_millisecond_data
        to a numpy array of dtype=int64 and pressure_data to a numpy
        array of dtype float64."""

        data = self.get_data()
        chunks = self.get_pressure_chunks(data)
        timestamps = self.get_times(data)
        self.data_start_date = datetime.strftime(timestamps[0], "%Y-%m-%dT%H:%M:%SZ")
        self.data_duration_time = timestamps[-1] - timestamps[0]

        # check time step:
        if self.data_duration_time <= 0:
            self.bad_data = True
            self.error_message = 'Error! Time step is zero. Check the datetime column of the input data.'
        
        else:
            with open(self.in_filename) as f:
                self.frequency = f.readline()[25:27]
            self.utc_millisecond_data = self.get_ms_data(timestamps, chunks)
            raw_pressure = self.make_pressure_array(timestamps, chunks)
            self.pressure_data = raw_pressure * 10.0 + uc.ATM_TO_DBAR
            return self.pressure_data, self.utc_millisecond_data

    def make_pressure_array(self, t, chunks):
        def press_entries(t2, t1):
            seconds = (t2 - t1).total_seconds()
            return seconds * self.frequency
        final = np.zeros(0, dtype=np.float64)
        prev_stamp = None
        prev_press = None
        for stamp, press in zip(t, chunks):
            if prev_stamp:
                n = press_entries(stamp, prev_stamp) - len(prev_press)
                narr = np.zeros(n, dtype=np.float64) + self.fill_value
                final = np.hstack((final, prev_press, narr))
            prev_stamp = stamp
            prev_press = press
        final = np.hstack((final, chunks[-1]))
        return final

    def get_pressure_chunks(self, data):
        master = [[]]
        i = 0
        for e in data:
            if e.startswith('+') or e.startswith('-'):
                if len(e) == 7:
                    master[i].append(np.float64(e))
            else:
                if master[i] != []:
                    master.append([])
                    i += 1
        master.pop()
        return master

    def get_ms_data(self, timestamps, chunks):
        """Generates the time data using the initial timestamp in the
        file and the length of the pressure data array."""

        first_stamp = timestamps[0]
        last_stamp = timestamps[-1]
        def del_t_ms(t2, t1):
            return (t2 - t1).total_seconds() * 1000
        total_stamp_ms = del_t_ms(last_stamp, first_stamp)
        last_chunk = chunks[-1]
        last_chunk_ms = 1000 * len(last_chunk) / self.frequency
        total_ms = total_stamp_ms + last_chunk_ms
        first_date = timestamps[0]
        epoch_start = datetime(year=1970, month=1, day=1, tzinfo=pytz.utc)
        offset = (first_date - epoch_start).total_seconds() * 1e3
        utc_ms_data = np.arange(total_ms, step=(1000 / self.frequency),
                                dtype='int64')
        utc_ms_data += offset
        return utc_ms_data

    def _get_frequency(self):
        with open(self.in_filename) as f:
            line = f.readline()
        freq = int(line[25:27])
        return freq

    def get_times(self, p):
        """Returns the time that the device started reading as a
        datetime object."""

        def make_stamps(p):
            added = ''
            result = []
            for i, s in enumerate(p):
                added += s
                if i % 6 == 5:
                    result.append(added)
                    added = ''
            return result

        def test2(x):
            return not (x.startswith('+') or x.startswith('-'))

        c = p.map(test2)
        p = p[c]
        p = p[14:-1]
        stamps = make_stamps(p)
        date_format = 'Y%yM%mD%dH%HM%MS%S'
        stamps = [datetime.strptime(stamp, date_format).replace(tzinfo=self.tzinfo)
                  for stamp in stamps]
        return stamps

    def get_data(self):
        """Reads the pressure data from the current file and returns
        it in a numpy array of dtype float64."""

        data = pd.read_csv(self.in_filename, skiprows=0, header=None,
                           lineterminator=',', sep=',', engine='c',
                           names='p')
        data.p = data.p.apply(lambda x: x.strip())
        return data.p


class NOAA_Station(edit_netcdf.NetCDFWriter):
    """As of now for barometric pressure only
    """

    def __init__(self):
        self.timezone_marker = "time zone"
        super().__init__()
        self.frequency = 4
        self.date_format_string = '%Y/%m/%d %H:%M'

    def read(self):
        """load the data from in_filename
        only parse the initial datetime = much faster
        """

        skip_index = find_first(self.in_filename, 'Date')
        df = pd.read_csv(self.in_filename, skiprows=skip_index,
                         header=None, engine='c', sep=',')

        self.datestart = uc.datestring_to_ms(df[0][0] + ' ' + df[1][0],
                                             self.date_format_string,
                                             self.tz_info,
                                             self.daylight_savings)
        self.utc_millisecond_data = uc.generate_ms(self.datestart, df.shape[0],
                                                   self.frequency)

        df[6][:].values[df[6][:].values == '-'] = '0'
        vals = np.array(df[6][:].values).astype(np.float64) / 100
        self.pressure_data = np.interp(np.arange(len(vals)), np.arange(len(vals))[vals != 0], vals[vals != 0])


class West_Coast_Station(edit_netcdf.NetCDFWriter):
    """As of now for barometric pressure only
    """

    def __init__(self):
        self.timezone_marker = "time zone"
        super().__init__()
        self.frequency = 4
        self.date_format_string = '%m/%d/%Y %H:%M UTC'

    def read(self):
        """load the data from in_filename
        only parse the initial datetime = much faster
        """

        skip_index = find_first(self.in_filename, '.*[0-9]{2}/[0-9]{2}/[0-9]{4}.*') - 1
        df = pd.read_csv(self.in_filename, skiprows=skip_index,
                         header=None, engine='c', sep=',')

        self.datestart = uc.datestring_to_ms('%s' % (df[1][0]),
                                             self.date_format_string,
                                             self.tz_info,
                                             self.daylight_savings)
        self.utc_millisecond_data = uc.generate_ms(self.datestart, df.shape[0],
                                                   self.frequency)
        self.pressure_data = np.array([x for x in df[2][:]]) / uc.DBAR_TO_INCHES_OF_MERCURY


class VanEssen(edit_netcdf.NetCDFWriter):
    """derived class for VanEssen csv files """

    def __init__(self):
        self.timezone_marker = "time zone"
        super().__init__()
        self.date_format_string = '%Y/%m/%d %H:%M:%S'

    def read(self):
        """load the data from in_filename
        only parse the initial datetime = much faster"""

        self.get_serial()

        skip_index = find_first(self.in_filename, 'Date/time')

        df = pd.read_table(self.in_filename, skiprows=skip_index, header=None,
                           engine='c', sep=',', usecols=(0, 1))
        df = df.dropna()

        vals = df[1].values
        date1, date2 = df[0][0],  df[0][1]

        first_stamp = uc.datestring_to_ms(date1, self.date_format_string,
                                          self.tz_info, self.daylight_savings)
        second_stamp = uc.datestring_to_ms(date2, self.date_format_string,
                                           self.tz_info, self.daylight_savings)
        
        timestep = second_stamp - first_stamp
        # check time step:
        if timestep <= 0:
            self.bad_data = True
            self.error_message = 'Error! Time step is zero. Check the datetime column of the input data.'

        else:
            self.frequency = 1000 / (second_stamp - first_stamp)

            self.utc_millisecond_data = uc.generate_ms(first_stamp, df.shape[0], self.frequency)

            self.pressure_data = vals / uc.METER_TO_FEET

    def get_serial(self):
        self.instrument_serial = "not found"
        with open(self.in_filename, 'r') as text:
            for i, line in enumerate(text):
                if line.find("Serial number: ") != -1:
                    match = line.split('Serial number: ')[1]
                    self.instrument_serial = match.split(' ')[0]
                    break