#!/usr/bin/env python3
"""
Note:  This module contains code for two GUIs.
To eliminate memory leaks from matplotlib, a separate process needs to be
stood up and tore down completely.  With that said, the reason for having two GUIs
in one module is multiprocessing is complicated for windows operating systems.
Calls to fork need to be done within the __name__ == "__main__" block. So the StormGUI needed to be contained
in this main block in order to fork another process.  Any alterations in the future are welcome.

The Master module is the menu for the program, containing all of the available GUIs for
processing the pressure data and getting output water level and wave statistics.

The Storm GUI takes the sea and air pressure netCDF files and creates output netCDFs, CSVs, and
visualizations for water level and wave statistics.
"""

from tkinter import (Tk,
                     Label,
                     Button,
                     Frame,
                     StringVar,
                     BooleanVar,
                     filedialog,
                     ttk,
                     messagebox,
                     Entry,
                     LEFT,
                     RIGHT,
                     Checkbutton,
                     OptionMenu,
                     Toplevel,
                     DISABLED,
                     BOTH)
from tkinter.constants import W, E, N
from PIL import Image, ImageTk
import gc
import cftime
import multiprocessing as mp
import wavelab.gui.chopper_gui as chopper
import wavelab.gui.sea_pressure_gui as script1
import wavelab.gui.baro_pressure_gui as script1_air
from wavelab.utilities.get_image import get_image
import wavelab.gui.sea_pressure_gui as sea_gui
from wavelab.processing.storm_options import StormOptions
from wavelab.processing.storm_graph import StormGraph
from wavelab.processing.storm_csv import StormCSV
from wavelab.processing.storm_netCDF import Storm_netCDF
from wavelab.processing.storm_statistics import StormStatistics


def storm_processing(data_dict, queue):

    # try:
    so = StormOptions()
    so.info_dict = data_dict
    so.extract_from_dict()

    snc = Storm_netCDF()
    snc.process_netCDFs(so)
    snc = None
    del snc
    gc.collect()

    scv = StormCSV()
    scv.int_units = so.international_units
    scv.process_csv(so)
    scv = None
    del scv
    gc.collect()

    sg = StormGraph()
    sg.international_units = so.international_units
    sg.process_graphs(so)
    sg = None
    del sg
    gc.collect()

    s_stat = StormStatistics()
    s_stat.int_units = so.international_units
    s_stat.process_graphs(so)
    s_stat = None
    del s_stat
    gc.collect()

    queue.put(0)

    # except:
    #
    #     queue.put(1)


if __name__ == '__main__':

    mp.freeze_support()

    class StormGui:

        def __init__(self, root):

            # root and selection dialogs for sea and air netCDF files
            self.root = root

            self.top = Frame(self.root)
            root.title('Storm Surge GUI (Pressure -> Water Level)')
            self.root.focus_force()

            self.sea_fname = ''
            self.sea_var = StringVar()
            self.sea_var.set('File containing water pressure...')
            self.air_fname = ''
            self.air_var = StringVar()
            self.air_var.set('File containing air pressure...')

            self.make_fileselect(self.top, 'Water file:',
                                 self.sea_var, 'sea_fname')
            self.make_fileselect(self.top, 'Air file:',
                                 self.air_var, 'air_fname')

            c3 = lambda: self.select_output_file(self.root)

            self.so = StormOptions()

            self.top.grid(row=0, columnspan=3, sticky=W, padx = 15, pady=10)

            self.side1 = Frame(self.root)
            self.side3 = Frame(self.root)

            # Check boxes for output variables
            self.netCDFLabel = Label(self.side1, text='netCDF Options:')
            self.netCDFLabel.pack(anchor=W, padx=2, pady=2)

            for x in sorted(self.so.netCDF):
                self.so.netCDF[x] = BooleanVar()
                button = Checkbutton(self.side1, text=x, variable=self.so.netCDF[x])
                button.pack(anchor=W, padx=0, pady=2)

            self.csvLabel = Label(self.side1, text='CSV Options:')
            self.csvLabel.pack(anchor=W, padx=2, pady=2)

            for x in sorted(self.so.csv):
                self.so.csv[x] = BooleanVar()
                button = Checkbutton(self.side1, text=x, variable=self.so.csv[x])
                button.pack(anchor=W, padx=0, pady=2)

            self.graphLabel = Label(self.side1, text='Data Graph Options:')
            self.graphLabel.pack(anchor=W, padx=2, pady=2)

            for x in sorted(self.so.graph):
                self.so.graph[x] = BooleanVar()
                button = Checkbutton(self.side1, text=x, variable=self.so.graph[x])
                button.pack(anchor=W, padx=0, pady=2)

            self.TzLabel = Label(self.side3, text='Time zone to display dates in:')
            self.TzLabel.pack(anchor=W, padx=15, pady=2)

            options = ('GMT',
                       'US/Aleutian',
                       'US/Central',
                       'US/Eastern',
                       'US/Hawaii',
                       'US/Mountain',
                       'US/Pacific')
            self.tzstringvar = StringVar()
            self.tzstringvar.set(options[0])

            self.datePickFrame = Frame(self.side3)

            OptionMenu(self.datePickFrame, self.tzstringvar, *options).pack(side=LEFT, pady=2, padx=15)
            self.daylightSavings = BooleanVar()
            Checkbutton(self.datePickFrame, text="Daylight Savings", variable=self.daylightSavings).pack(side=RIGHT)
            self.datePickFrame.pack(anchor=W)

            self.emptyLabel4 = Label(self.side3, text='', font=("Helvetica", 2))
            self.emptyLabel4.pack(anchor=W, padx=15, pady=0)

            # variables and text boxes for air pressure limits
            self.BaroPickLabel = Label(self.side3, text='Barometric Pressure Y Axis Limits: (optional)')
            self.BaroPickLabel.pack(anchor=W, padx=15, pady=0)

            self.baroPickFrame = Frame(self.side3)
            self.bLowerLabel = Label(self.baroPickFrame, text="lower:").pack(side=LEFT, pady=10, padx=2)
            self.baroYlim1 = Entry(self.baroPickFrame, width=5)
            self.baroYlim1.pack(side=LEFT, pady=2, padx=15)
            self.baroYlim2 = Entry(self.baroPickFrame, width=5)
            self.baroYlim2.pack(side=RIGHT, pady=2, padx=15)
            self.bUpperLabel = Label(self.baroPickFrame, text="upper:").pack(side=RIGHT, pady=10, padx=2)
            self.baroPickFrame.pack(anchor=W, padx = 15)

            # tkinter spacing
            self.emptyLabel4 = Label(self.side3, text='', font=("Helvetica", 2))
            self.emptyLabel4.pack(anchor=W, padx=15, pady=0)

            # variables and textboxes for water level limits
            self.WaterLevelLabel = Label(self.side3, text='Water Level Y Axis Limits: (optional)')
            self.WaterLevelLabel.pack(anchor=W, padx=15, pady=0)

            self.wlPickFrame = Frame(self.side3)
            self.wlLowerLabel = Label(self.wlPickFrame, text="lower:").pack(side=LEFT, pady=10, padx=2)
            self.wlYlim1 = Entry(self.wlPickFrame, width=5)
            self.wlYlim1.pack(side=LEFT, pady=2, padx=15)
            self.wlYlim2 = Entry(self.wlPickFrame, width=5)
            self.wlYlim2.pack(side=RIGHT, pady=2, padx=15)
            self.wlUpperLabel = Label(self.wlPickFrame, text="upper:").pack(side=RIGHT, pady=10, padx=2)
            self.wlPickFrame.pack(anchor=W, padx = 15)

            # tkinter spacing
            self.emptyLabel5 = Label(self.side3, text='', font=("Helvetica", 2))
            self.emptyLabel5.pack(anchor=W, padx=15, pady=0)

            self.ReferenceLabel = Label(self.side3, text='Reference for Water Depth: (optional)')
            self.ReferenceLabel.pack(anchor=W, padx=15, pady=0)

            self.ReferencePickFrame = Frame(self.side3)
            self.ReferenceNameLabel = Label(self.ReferencePickFrame, text="Reference Name:").pack(side=LEFT, pady=10,
                                                                                                  padx=2)
            self.ReferenceName = Entry(self.ReferencePickFrame, width=20)
            self.ReferenceName.pack(side=LEFT, pady=2, padx=15)

            self.ReferencePickFrame.pack(anchor=W, padx=15)

            self.ReferencePickFrame2 = Frame(self.side3)

            self.ReferenceElevationLabel = Label(self.ReferencePickFrame2, text="Reference Elevation:").pack(side=LEFT,
                                                                                                            pady=2,
                                                                                                            padx=2)
            self.ReferenceElevation = Entry(self.ReferencePickFrame2, width=20)
            self.ReferenceElevation.pack(side=LEFT, pady=2, padx=15)

            self.ReferencePickFrame2.pack(anchor=W, padx=15)

            self.side1.grid(row=1, column=0, sticky=W, padx = 15)

            self.side2 = Frame(self.root)

            self.TzLabel = Label(self.side2, text='Statistics Graph Options:')
            self.TzLabel.pack(padx = 2,pady = 2)

            for x in sorted(self.so.statistics):
                self.so.statistics[x] = BooleanVar()
                button = Checkbutton(self.side2, text=x, variable=self.so.statistics[x])
                button.pack(anchor=W, padx=2, pady=2)

            self.TzLabel = Label(self.side3, text=' ')
            self.TzLabel.pack(padx=2, pady=45)

    #         self.TzLabel = Label(self.side2, text='Clip water level graph:')
    #         self.TzLabel.pack(padx = 2,pady = 2)

            # clip_options=('Yes','No')
            self.clip = 'No'
            # StringVar()
            # self.clip.set(clip_options[0])

            # OptionMenu(self.side2, self.clip, *clip_options).pack( pady=10, padx=15)

            self.TzLabel = Label(self.side3, text=' ')
            self.TzLabel.pack(padx=2, pady=10)
            self.TzLabel = Label(self.side3, text='Output Name:')
            self.TzLabel.pack(padx=2, pady=2)
    #
            self.output_name = Entry(self.side3, width=20)
            self.output_name.pack(pady=2, padx=15)

            self.TzLabel = Label(self.side3, text=' ')
            self.TzLabel.pack(padx=2, pady=10)
            self.level_troll = BooleanVar()

            self.level_troll.set(False)

            # 9-11-2018 Leave out level troll option and highcut for spectrum output
            # ------------------------------------------
    #         button = Checkbutton(self.side3, text='LevelTroll', variable=self.level_troll)
    #         button.pack(anchor=W, padx=2, pady = 2)


    #         self.high_cut = Entry(self.side2, width=5)
    #         self.high_cut.pack(pady=2, padx=15)

            self.side2.grid(row=1, column=1, sticky=N, padx = 15)
            self.side3.grid(row=1, column=2, sticky=N, padx = 15)

            self.final = Frame(self.root)
            self.b3 = ttk.Button(self.final,text="Process Files", command=c3, state=DISABLED,width=50)

            self.b3.pack(fill='both')

            self.final.grid(row=2, columnspan=2)

        def select_file(self, varname, stringvar):

            fname = filedialog.askopenfilename()
            if fname != '':
                stringvar.set(fname)
                setattr(self, varname, fname)
                if(self.air_fname != ''):
                    self.b3['state'] = 'ENABLED'
            self.root.focus_force()

        def clear_file(self, varname, stringvar):

            stringvar.set('No file selected...')
            setattr(self, varname, '')
            if(self.air_fname == ''):
                    self.b3.config(state='disabled')

        def make_button(self, root, text, command, state=None):
            """Creates a new button"""

            b = ttk.Button(root, text=text, command=command, state=state,
                           width=10)
            return b

        def make_fileselect(self, root, labeltext, stringvar, varname):
            """Creates a file selection menu"""

            command = lambda: self.select_file(varname, stringvar)
            command2 = lambda: self.clear_file(varname, stringvar)
            frame = make_frame(root)
            l = ttk.Label(frame, justify=LEFT, text=labeltext, width=10)
            l.grid(row=0, column=0, sticky=W)
            b = self.make_button(frame, 'Browse', command)
            b.grid(row=0, column=2, sticky=W)
            b2 = self.make_button(frame, 'Clear', command2)
            b2.grid(row=0, column=3, sticky=W)
            e = ttk.Label(frame, textvariable=stringvar, justify=LEFT,
                          width=32)
            e.grid(row=0, column=1, sticky=(W, E))
            frame.pack(anchor=W, fill=BOTH)

        def select_output_file(self, root):
            """Processes the selected afiles and outputs in format selected"""

            # Format the name properly based on the input of the user
            slash_index = self.sea_fname.rfind('/')
            self.final_output_name = ''.join([self.sea_fname[0:slash_index+1], self.output_name.get()])

            if self.sea_fname is None or self.sea_fname == '':
                if self.so.air_check_selected() is True:
                    message = ("Please upload a water netCDF file or uncheck options that require it")
                    sea_gui.MessageDialog(root, message=message, title='Error!')
                    return

            if self.so.check_selected() is False:
                message = ("Please select at least one option")
                sea_gui.MessageDialog(root, message=message, title='Error!')
                return

            self.so.clear_data()
            self.so.international_units = False

            try:
                self.so.air_fname = self.air_fname
                self.so.sea_fname = self.sea_fname
                self.so.output_fname = self.final_output_name

                self.so.level_troll = self.level_troll.get()

                self.so.timezone = self.tzstringvar.get()
                self.so.daylight_savings = self.daylightSavings.get()

                self.so.reference_name = self.ReferenceName.get()
                self.so.reference_elevation = self.ReferenceElevation.get()

                if self.so.reference_elevation != '':
                    if self.so.reference_name == '':
                        message = ("Enter a Reference Name.")
                        sea_gui.MessageDialog(root, message=message, title='Error!')
                        return
                    try:
                        self.so.reference_elevation = float(self.so.reference_elevation)
                    except:
                        message = ("Reference Elevation is not a number.")
                        sea_gui.MessageDialog(root, message=message, title='Error!')
                        return

                self.so.clip = False

                self.so.baroYLims = []
                try:
                    self.so.baroYLims.append(float(self.baroYlim1.get()))
                    self.so.baroYLims.append(float(self.baroYlim2.get()))
                except:
                    self.so.baroYLims = None

                self.so.wlYLims = []
                try:
                    self.so.wlYLims.append(float(self.wlYlim1.get()))
                    self.so.wlYLims.append(float(self.wlYlim2.get()))
                except:
                    self.so.wlYLims = None

                self.so.low_cut = 0.045
                self.so.high_cut = 1.0

                if self.sea_fname is not None and self.sea_fname != '':

                    overlap = self.so.time_comparison()

                    if overlap == 2:
                        message = ("Air pressure and water pressure files don't "
                                   "cover the same time period!\nPlease choose "
                                   "other files.")
                        sea_gui.MessageDialog(root, message=message, title='Error!')
                        return
                    elif overlap == 1:
                        message = ("The air pressure file doesn't span the "
                        "entire time period covered by the water pressure "
                        "file.\nThe period not covered by both files will be "
                        "chopped")
                        sea_gui.MessageDialog(root, message=message, title='Warning')

                self.so.convert_to_dict()
                data_dict = self.so.info_dict
                queue = mp.Queue()

                p = mp.Process(target=storm_processing, args=(data_dict,queue))
                p.start()
                p.join()

                return_code = queue.get()
                print(return_code)
                if return_code != 0:

                    raise(ValueError)

                sea_gui.MessageDialog(root, message="Success! Files processed.",
                                      title='Success!')

            except:
    #             exc_type, exc_value, exc_traceback = sys.exc_info()
    #
    #             message = traceback.format_exception(exc_type, exc_value,
    #                                           exc_traceback)
                message = 'Could not process files, please check file type.'
                sea_gui.MessageDialog(root, message=message,
                                 title='Error')

    def make_frame(frame, header=None):
        """Make a frame with uniform padding."""
        return ttk.Frame(frame, padding="3 3 5 5")


    class MasterGui:
        def __init__(self, root):

            self.in_file_name = ''
            self.root = root
            self.root.focus_force()

            self.root1 = None
            self.root2 = None
            self.root3 = None
            self.root4 = None
            self.root5 = None

            img = Image.open(get_image('wavelab.jpg'))
            photo = ImageTk.PhotoImage(img)

            self.panel = Label(root, image=photo)
            self.image = photo
            self.panel.pack()

            self.root.title('WaveLab')
            self.Label = Label(self.root, text='Core Programs:')
            self.Label.pack(anchor=W, padx=15, pady = 2)
            self.b1 = Button(self.root, text='Sea GUI', command=self.sea_gui)
            self.b1.pack(anchor=W, padx=15, pady = 2)
            self.b2 = Button(self.root, text='Air GUI', command=self.air_gui)
            self.b2.pack(anchor=W, padx=15, pady = 2)
            self.b3 = Button(self.root, text='Chopper', command=self.chopper)
            self.b3.pack(anchor=W, padx=15, pady = 2)
            # self.b4 = Button(self.root, text='Wind GUI', command=self.wind_gui)
            # self.b4.pack(anchor=W, padx=15, pady=2)
            self.b5 = Button(self.root, text='Storm GUI', command=self.storm_surge)
            self.b5.pack(anchor=W, padx=15, pady=2)
            self.emptyLabel2 = Label(self.root, text='', font=("Helvetica", 2))
            self.emptyLabel2.pack(anchor=W, padx=15, pady=0)

        def sea_gui(self):
            self.root1 = Toplevel(self.root)
            self.root1.iconbitmap(get_image('wavelab_icon.ico'))
            gui1 = script1.SeaPressureGUI(self.root1, air_pressure=False)
            self.root1.mainloop()

        def air_gui(self):
            self.root2 = Toplevel(self.root)
            self.root2.iconbitmap(get_image('wavelab_icon.ico'))
            gui2 = script1_air.BaroPressureGUI(self.root2)
            self.root2.mainloop()

        def chopper(self):
            self.root3 = Toplevel(self.root)
            self.root3.iconbitmap(get_image('wavelab_icon.ico'))
            gui3 = chopper.Chopper(self.root3)
            self.root3.mainloop()

        def storm_surge(self):
            self.root5 = Toplevel(self.root)
            self.root5.iconbitmap(get_image('wavelab_icon.ico'))
            gui5 = StormGui(self.root5)
            self.root5.mainloop()

        def on_closing(self):
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                self.root.destroy()

    # This call is so pyinstaller includes cftime
    arb = cftime.datetime

    root = Tk()
    root.iconbitmap(get_image('wavelab_icon.ico'))
    gui = MasterGui(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_closing)
    root.mainloop()
