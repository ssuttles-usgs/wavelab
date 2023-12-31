#!/usr/bin/env python3
"""
Contains a GUI that interfaces with this package's netCDF-writing
modules. Also contains some convenience methods for other GUIs.
"""

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
import traceback
import sys
import pathlib
import os
from collections import OrderedDict
from wavelab.processing.pressure_script import convert_to_netcdf
from wavelab.utilities.utils import MessageDialog
import json
import re
from wavelab.utilities import unit_conversion as uc

# Save history JSON files at a location: ex. C:\Users\username\WaveLab
HISTFILEPATH = os.environ['USERPROFILE'] + r'\WaveLab'
pathlib.Path(HISTFILEPATH).mkdir(parents=True, exist_ok=True) # Create WaveLab folder if it doesn't already exist
GLOBAL_HISTFILE = os.path.join(HISTFILEPATH, 'history.json') 
LOCAL_HISTFILE = os.path.join(HISTFILEPATH, 'history2_sea.json')
GLOBAL_FIELDS = OrderedDict([
    ('creator_name', ['Your full name:', '']),
    ('creator_email', ['Your email address:', '']),
    ('creator_url', ['Your personal url:', ''])])
LOCAL_FIELDS = OrderedDict([
    ('instrument_name', ['Instrument:', [
        'MS TruBlue 255', 'Onset Hobo U20', 'LevelTroll', 'RBRSolo',
        'VanEssen', # 'Generic' , 'USGS Homebrew'
        ], True]),
    ('stn_station_number', ['STN Site Id:', '']),
    ('stn_instrument_id', ['STN Instrument Id:', '']),
    ('latitude', ['Latitude (decimal degrees):', '', True]),
    ('longitude', ['Longitude (decimal degrees):', '', True]),
    ('tz_info', ['Time zone the instrument recorded time in:', ['GMT',
                'US/Aleutian',
                'US/Central',
                'US/Eastern',
                'US/Hawaii',
                'US/Mountain',
                'US/Pacific'], True]),
    ('daylight_savings', ['Daylight Savings',False]),
    ('datum', ['Datum:', ['NAVD88',
                            'NGVD29',
                            'PRVD2002',
                            'Above Ground Level',
                            'Local Control Point'], True])])
WATER_ONLY_FIELDS = OrderedDict([
    
    ('salinity', ['Salinity:', [
        'Salt Water (> 30 ppt)', 'Brackish Water (.5 - 30 ppt)',
        'Fresh Water (< .5 ppt)'], False]),
    ('initial_land_surface_elevation', ['Initial land surface elevation (feet):', '', False]),
    ('final_land_surface_elevation', ['Final land surface elevation (feet):', '', False]),
    ('initial_sensor_orifice_elevation', ['Sensor orifice elevation at deployment time(feet):', '', False]),
    ('final_sensor_orifice_elevation', ['Sensor orifice elevation at retrieval time(feet):', '', False]),
    ('deployment_time', ['Deployment time (YYYYMMDD HHMM) (24 hour clock):', '', False]),
    ('retrieval_time', ['Retrieval time (YYYYMMDD HHMM) (24 hour clock):', '', False]),
    ('sea_name', ['Sea Name:', [
        'Chesapeake Bay', 'Great Lakes', 'Gulf of Alaska', 'Gulf of California',
        'Gulf of Maine', 'Gulf of Mexico', 'Hudson Bay', 'Massachusetts Bay',
        'NE Atlantic (limit-40 W)', 'NE Pacific (limit-180)',
        'North American Coastline-North', 'North American Coastline-South',
        'North Atlantic Ocean', 'North Pacific Ocean',
        'NW Atlantic (limit-40 W)', 'NW Pacific (limit-180)',
        'SE Atlantic (limit-20 W)', 'SE Pacific (limit-140 W)',
        'SW Atlantic (limit-20 W)', 'SW Pacific (limit-147 E to 140 W)'],
                  False]),
    ])


class SeaPressureGUI:
    """ GUI for csv-to-netCDF conversion. """

    def __init__(self, parent, air_pressure=False):
        self.parent = parent
        self.parent.focus_force()
        self.air_pressure = air_pressure
        self.local_fields = LOCAL_FIELDS
        if not air_pressure:
            self.local_fields.update(WATER_ONLY_FIELDS)
        parent.title("Sea GUI (CSV -> NetCDF)")
        self.air_pressure = air_pressure
        self.datafiles = OrderedDict()
        self.book = ttk.Notebook(self.parent)
        self.book.grid(row=1, column=0)
        self.global_form = Form(self.parent, list(GLOBAL_FIELDS.values()),
                                GLOBAL_HISTFILE)
        self.global_form.grid(row=2, column=0)
        self.summary = "These data were collected by an unvented pressure logger deployed in the water."
        add = lambda: [self.add_file(fname)
                       for fname in askopenfilename(multiple=True)]
        self.error_message = ""
        
        buttons = [
            ("Add File(s)", add),
            ("Save Globals", self.global_form.dump),
            ("Load Globals", self.global_form.load),
            ("Process Files", self.process_files),
            ("Quit", self.parent.destroy)]
        ButtonBar(self.parent, buttons).grid(row=3, column=0)

    def add_file(self, fname):
        """Add a new file tab to the file frame."""
        tab = tk.Frame(self.book)
        self.book.add(tab, text=os.path.basename(fname))
        datafile = Form(tab, list(LOCAL_FIELDS.values()), LOCAL_HISTFILE)
        datafile.pack()
        self.datafiles[fname] = datafile
        removef = lambda: self.remove_file(fname)
        ButtonBar(tab, (('Remove File', removef),
                        ('Save Entries', datafile.dump),
                        ('Load Entries', datafile.load))).pack()
        self.parent.update()
        self.parent.focus_force()

    def process_files(self):
        """Run the csv to netCDF conversion on the selected files."""

        message = ('Working, this may take a few minutes.')

        dialog = None

        #  If no file is selected yet
        if len(self.datafiles) == 0:
            MessageDialog(self.parent, message='No file selected. Please select a file before running.',
                                  title='No file selected!')
        # Run if there is a file
        else:
            try:
                dialog = MessageDialog(self.parent, message=message,
                                    title='Processing...', buttons=0, wait=False)
                globs = dict(zip(GLOBAL_FIELDS.keys(),
                                self.global_form.export_entries()))
                bad_data = None

                for fname, datafile in self.datafiles.items():
                    inputs = dict(zip(LOCAL_FIELDS.keys(), datafile.export_entries()))
                    inputs.update(globs)

                    if self.air_pressure == False:
                        inputs['pressure_type'] = 'Sea Pressure'
                    else:
                        inputs['pressure_type'] = 'Air Pressure'
                    inputs['sea_pressure'] = not self.air_pressure
                    inputs['in_filename'] = fname
                    inputs['out_filename'] = fname + '.nc'

                    process_files = self.validate_entries(inputs)

                    inputs['deployment_time'] = uc.datestring_to_ms(inputs['deployment_time'], '%Y%m%d %H%M', \
                                                                    inputs['tz_info'],
                                                                    inputs['daylight_savings'])

                    inputs['retrieval_time'] = uc.datestring_to_ms(inputs['retrieval_time'], '%Y%m%d %H%M', \
                                                                    inputs['tz_info'],
                                                                    inputs['daylight_savings'])

                    if process_files == True:
                        bad_data, message = convert_to_netcdf(inputs)
                        self.remove_file(fname)
                        dialog.destroy()
                        if bad_data == True:
                            MessageDialog(self.parent, message=message,
                                    title='Data Issues!')
                        else:
                            MessageDialog(self.parent, message="There were no bad data points in the file",
                                    title='No Data Issues!')

                            MessageDialog(self.parent, message="Success! Files saved.",
                                        title='Success!')
                    else:
                        dialog.destroy()
                        MessageDialog(self.parent, message= self.error_message,
                                    title='Error')

                    self.error_message = ''

            except:
                if dialog is not None:
                    dialog.destroy()
                MessageDialog(self.parent, message="Could not process files, please check file type.",
                            title='Error')
                exc_type, exc_value, exc_traceback = sys.exc_info()
    #
                message = traceback.format_exception(exc_type, exc_value,
                                            exc_traceback)

                MessageDialog(self.parent, message=message,
                                title='Error')
    
    def validate_entries(self, inputs):
        """Check if the GUI entries are filled out and in the proper format"""

        ignore = [
                  'in_filename',
                  'tzinfo', 
                  'sea_name',
                  'sea_pressure',
                  'salinity',
                  'out_filename',
                  'datum',
                  'instrument_name'
                  ]
        
        message_names = {
            "creator_name": "Full Name",
            "creator_email": "Email Address",
            "creator_url": "Personal Url",
            "latitude": "Latitude",
            "longitude": "Longitude",
            "stn_station_number": "STN Station Number",
            "stn_instrument_id": "STN Instrument Id",
            "initial_land_surface_elevation": "Initial Land Surface Elevation",
            "final_land_surface_elevation": "Final Land Surface Elevation",
            "initial_sensor_orifice_elevation": "Sensor Orifice Elevation at Deployment Time",
            "final_sensor_orifice_elevation": "Sensor Orifice Elevation at Retrieval Time",
            "deployment_time": "Deployment Time",
            "retrieval_time": "Retrieval Time"
         }
        
        #Iterate through all of the dictionary inputs, check if blank or check proper ret/deploy time format
        for x in sorted(inputs):
            if x not in ignore:
                if inputs[x] is not None:
                    if x == 'deployment_time' or x == 'retrieval_time':
                       
                        if re.fullmatch('^[0-9]{8}\s[0-9]{4}$', str(inputs[x])) is None:
                            self.error_message += "%s input invalid \n" % message_names[x]
                    else:
                        if inputs[x] == '':
                            self.error_message += "%s input invalid \n" % message_names[x]
                else:
                    self.error_message += "%s input invalid \n" % message_names[x]
                    
        if self.error_message != '':
            return False
        else:
            return True
        
    def remove_file(self, fname):
        """Remove the current file's tab from the window."""

        self.book.forget('current')
        self.datafiles.pop(fname)

    
class Form(tk.Frame):
    """A widget that contains form fields that users can fill"""

    def __init__(self, root, fields, histfile):
        """Create all the tk.Entry widgets and populate the widget with them."""

        tk.Frame.__init__(self, root)
        self.root = root
        self.histfile = histfile
       
        self.entries = [self.make_entry_row(field, row)
                        for row, field in enumerate(fields)]
        
        self.menu = tk.Menu(root, tearoff=0)
        self.menu.add_command(label="Cut")
        self.menu.add_command(label="Copy")
        self.menu.add_command(label="Paste")
        
    def show_menu(self,e):

        w = e.widget
        self.menu.entryconfigure("Cut",
                                 command=lambda: w.event_generate("<<Cut>>"))
        self.menu.entryconfigure("Copy",
                                 command=lambda: w.event_generate("<<Copy>>"))
        self.menu.entryconfigure("Paste",
                                 command=lambda: w.event_generate("<<Paste>>"))
        self.menu.tk.call("tk_popup", self.menu, e.x_root, e.y_root)

    def make_entry_row(self, field, row):
        """Create an Entry based on a field and return its StringVar."""

        label = tk.Label(self, text=field[0], width=45, anchor='w')
        label.grid(row=row, column=0, sticky='W')
        
        value = field[1]
         
        if isinstance(value, bool):
            content = tk.BooleanVar()
        else:
            content = tk.StringVar()
            
        if isinstance(value, str):
            content.set(value)
            widget = tk.Entry(self, textvariable=content, width=40)
            widget.bind_class("Entry", "<Button-3><ButtonRelease-3>", self.show_menu)
        elif isinstance(value, bool):
            content.set(value)
            widget = tk.Checkbutton(self, variable=content, width=40)
        else:
            content.set(value[0])
            widget = tk.OptionMenu(self, content, *value)
        widget.grid(row=row, column=1, sticky=('W', 'E'))
        return content

    def export_entries(self):
        """Export the user's input as a list of strings."""

        return [entry.get() for entry in self.entries]

    def import_entries(self, in_entries):
        """Populate the form fields with a list of strings."""

        for ein, current in zip(in_entries, self.entries):
            current.set(ein)

    def dump(self):
        """Write the user's inputs to a file."""

        with open(self.histfile, 'w') as fname:
            json.dump(self.export_entries(), fname)

    def load(self):
        """Populate the form fields with a list from a file."""

        try:
            with open(self.histfile) as fname:
                self.import_entries(json.load(fname))
        except:
            MessageDialog(self.root, message="No entry file found, fill in fields and click save to create one.",
                      title='Error')


class ButtonBar(tk.Frame):
    """A widget containing buttons arranged horizontally."""

    def __init__(self, root, buttonlist):
        """Create a Button for each entry in buttonlist"""

        tk.Frame.__init__(self, root)
        for i, props in enumerate(buttonlist):
            button = tk.Button(self, text=props[0], command=props[1], width=12)
            button.grid(row=0, column=i, sticky=('W', 'E'))


if __name__ == '__main__':
    root = tk.Tk()
    gui = SeaPressureGUI(root, air_pressure=False)
    root.mainloop()
