"""
Module to query WaterServices for wind data from a selected Rapid Deployment Gage
"""

import requests
import defusedxml.ElementTree as ET
from datetime import datetime
from wavelab.utilities import unit_conversion as uc
from netCDF4 import Dataset
import numpy as np
from wavelab.utilities.var_datastore import DataStore


def append_html_prefix(string, prefix_type=''):
    if prefix_type == 'gml':
        return ''.join(['{http://www.opengis.net/gml/3.2}', string])
    elif prefix_type == 'om':
        return ''.join(['{http://www.opengis.net/om/2.0}',string])
    else:
        return ''.join(['{http://www.opengis.net/waterml/2.0}',string])


def format_time(dates):
    dash_index = dates[0].rfind('+')

    if dash_index == -1:
        dash_index = dates[0].rfind('-')
    
    colon_index = dates[0].rfind(':')
    hour_difference = float(dates[0][dash_index:colon_index])
    dates = [datetime.strptime(x[0:dash_index], '%Y-%m-%dT%H:%M:%S') \
             for x in dates]
    
    dates = uc.adjust_by_hours(dates, hour_difference)
    dates = [uc.date_to_ms(x) for x in dates]
    return dates


def get_data_type(attrib, sites):
    site_len = len(sites)
    index = attrib.find(sites)
    first = int(index + site_len+1)
    last = int(index + site_len+6)
    return attrib[first:last]


def get_wind_data(file_name,sites,start_date = None, end_date = None, tz=None, ds=None):
    
    var_datastore = DataStore(0)
    dt1 = datetime.strptime(start_date,'%Y-%m-%d %H:%M')
    dt1 = uc.make_timezone_aware(dt1, tz, ds)
    dt2 = datetime.strptime(end_date,'%Y-%m-%d %H:%M')
    dt2 = uc.make_timezone_aware(dt2, tz, ds)

    params = {
        'sites': sites,
        'format': 'waterml,2.0',
        'startDT': dt1.isoformat('T'),
        'endDT': dt2.isoformat('T'),
        'parameterCd': '00035,00036,61728,00025'
    }

    r = requests.get('http://waterservices.usgs.gov/nwis/iv/', params=params)
    print(r.url)
    time, speed, u, v, gust, baro = [], [], [], [], [], []
    lat, lon, name, data_type = None, None, None, None
    
    if r.status_code not in [503, 504]:
        root = ET.fromstring(r.text)
        
        name_search = ''.join(['.//', append_html_prefix('name', prefix_type='gml')])
        for child in root.findall(name_search):
            name = child.text
    
        search = ''.join(['.//', append_html_prefix('observationMember')])
        for child in root.findall(search):
            
            search2 = ''.join(['.//', append_html_prefix('OM_Observation', prefix_type='om')])
            for y in child.findall(search2):
                data_type = get_data_type(y.attrib[append_html_prefix('id', prefix_type='gml')], sites)

            index = 0

            if lat is None:
                c = ''.join(['.//', append_html_prefix('pos', prefix_type='gml')])
                for x in child.findall(c):
                    lat_lon = x.text.split(' ')
                    lat = lat_lon[0]
                    lon = lat_lon[1]
            
            if len(time) == 0:
                a = ''.join(['.//', append_html_prefix('time')])
                for x in child.findall(a):
                    time.append(x.text)
                
            b = ''.join(['.//', append_html_prefix('value')])
            for x in child.findall(b):
                
                if data_type == '00035':
                    speed.append(float(x.text) / uc.METERS_PER_SECOND_TO_MILES_PER_HOUR)
                
                elif data_type == '00036':
                    u.append(speed[index] * np.sin(float(float(x.text) * np.pi/180)))
                    v.append(speed[index] * np.cos(float(float(x.text) * np.pi/180)))
                    index += 1
                        
                elif data_type == '00025':
                    baro.append(float(x.text) / uc.DBAR_TO_MM_OF_MERCURY)
                else:
                    gust.append(float(x.text) / uc.METERS_PER_SECOND_TO_MILES_PER_HOUR)

        time = format_time(time)
        time = time[2:]
        print(len(time), len(u), len(v))
        with Dataset(file_name, 'w', format="NETCDF4_CLASSIC") as ds:
            time_dimen = ds.createDimension("time", len(time))
            station_dimen = ds.createDimension("station_id", len(sites))
            ds.setncattr('stn_station_number',sites)
            var_datastore.global_vars_dict['stn_station_number'] = sites
            var_datastore.global_vars_dict['summary'] = name
            var_datastore.global_vars_dict['comment'] = ''
            var_datastore.global_vars_dict['datum'] = 'NAVD88'
            var_datastore.utc_millisecond_data = time
            var_datastore.latitude = lat
            var_datastore.longitude = lon
            var_datastore.u_data = u
            var_datastore.v_data = v
            var_datastore.gust_data = gust
            var_datastore.pressure_data = baro
            var_datastore.pressure_name = "air_pressure"
            var_datastore.send_wind_data(ds)
#        
    else:
        print('fail')
