import sys
import argparse

from wavelab.processing.storm_options import StormOptions
from wavelab.processing.storm_netCDF import Storm_netCDF
from wavelab.processing.storm_statistics import StormStatistics

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('st_file', help='fname of storm-tide file')
    args = vars(parser.parse_args(sys.argv[1:]))

    class Bool(object):

        def __init__(self, val):
            self.val = val

        def get(self):
            return self.val

    so = StormOptions()
    so.clip = False
    so.air_fname = args['st_file']
    so.sea_fname = args['st_file']
    so.format_output_fname(args['st_file'])
    so.international_units = False
    so.high_cut = 1.0
    so.low_cut = 0.045
    so.from_water_level_file = True

    so.netCDF['Storm Tide with Unfiltered Water Level'] = Bool(False)
    so.netCDF['Storm Tide Water Level'] = Bool(False)
    so.netCDF['Wave Statistics'] = Bool(True)

    so.timezone = 'GMT'
    so.daylight_savings = False
    snc = Storm_netCDF()
    snc.process_netCDFs(so)

    for y in so.statistics:
        so.statistics[y] = Bool(False)

    so.statistics['H1/3'] = Bool(True)
    so.statistics['Average Z Cross'] = Bool(True)
    so.statistics['PSD Contour'] = Bool(True)
    so.statistics['Peak Wave'] = Bool(True)

    ss = StormStatistics()
    ss.process_graphs(so)