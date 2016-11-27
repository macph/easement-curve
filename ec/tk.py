# MIT License, copyright Ewan Macpherson, 2016; see LICENCE in root directory
# Tk graphical user interface for easement curve calculations

from abc import ABCMeta, abstractmethod
import json
import os.path
import sys

import tkinter as tk
import tkinter.font as tkfont
import tkinter.ttk as ttk

from ec import base_path, coord, section, curve

# TODO: Add gettext support. Next version
# TODO: Consider adding speed tolerance profiles. Next version


def resource_path(relative_path):
    """ Get absolute path to resource from project root directory, works for
        dev and for PyInstaller
    """
    # stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        abs_path = sys._MEIPASS
    except AttributeError:
        # Assume that root directory is one above the module directory this
        # script resides in
        abs_path = base_path

    return os.path.join(abs_path, relative_path)


def text_length(length, font='TkDefaultFont'):
    """ Retrieves the length of a string defined by number of characters
        in pixels.
    """
    base_length = tkfont.nametofont(font).measure('e' * 80)
    return round(base_length * length / 80)


class InterfaceException(Exception):
    pass


class MainWindow(ttk.Frame):
    """ Main application window. """
    default_settings = {
        'language': 'en',
        'speed units': 'mph',
        'two decimal places': False,
        'split static curve': False,
        'results rows': 5
    }

    def __init__(self, parent, **kwargs):
        super(MainWindow, self).__init__(parent, **kwargs)
        self.config(padding='{t} {t} {t} {t}'.format(t=text_length(1)))
        self.grid(row=0, column=0)
        self.parent = parent

        self.settings, self.message = None, ''
        self.load_settings('ec_settings.json', self.default_settings)

        self._kph = None
        self._method = tk.StringVar()
        self.current_entry, self.description, self.msg, self.sr, \
            self.entries, self.minimum_radius, self.result = (None,) * 7

        self.body()

        self.parent.bind('<Return>', self.calculate)

    @property
    def method(self):
        """ Retrieves method selection. """
        return self._method.get()

    @method.setter
    def method(self):
        raise AttributeError('method property cannot be set manually.')

    @property
    def mph(self):
        """ Speed tolerance in mph. """
        return self._kph / 1.609344

    @mph.setter
    def mph(self, value):
        self._kph = value * 1.609344

    @property
    def kph(self):
        """ Speed tolerance in kph. """
        return self._kph

    @kph.setter
    def kph(self, value):
        self._kph = value

    def body(self):
        self.columnconfigure(2, weight=1)
        self.columnconfigure(4, pad=4)
        self.rowconfigure(3, pad=4)
        self.rowconfigure(4, pad=4)

        options = ['1', '2']
        ttk.Label(self, text='Select method ').grid(row=0, column=0)
        ttk.OptionMenu(self, self._method, options[0], *options,
                       command=self.refresh_method).grid(row=0, column=1)

        self.description = MethodDescription(self)
        self.description.grid(row=1, column=0, columnspan=5,
                              sticky=(tk.W, tk.E))

        self.sr = SpeedRadius(self)
        self.sr.grid(row=2, column=0, columnspan=5, sticky=(tk.W, tk.E))

        self.entries = {'1': EntryMethod1(self, row=3),
                        '2': EntryMethod2(self, row=3)}

        self.current_entry = self.entries[self.method]
        # Hiding all widgets not selected
        for k in [i for i in self.entries.keys() if i != self.method]:
            self.entries[k].grid_remove()

        ttk.Style().configure('Red.TLabel', foreground="red")
        if self.message == '':
            self.msg = ttk.Label(self, text='')
        else:
            self.msg = ttk.Label(self, text=self.message, style='Red.TLabel')
        self.msg.config(width=56, wraplength=text_length(56))
        self.msg.grid(row=4, column=0, columnspan=3, sticky=tk.W)

        ttk.Button(self, text='Calculate', command=self.calculate
                   ).grid(row=4, column=3, sticky=(tk.N, tk.E))
        ttk.Button(self, text='Clear', command=self.clear
                   ).grid(row=4, column=4, sticky=(tk.N, tk.E))

        self.result = Result(self)
        self.result.grid(row=5, column=0, columnspan=5)

    def load_settings(self, filename, defaults):
        """ Loads settings from a JSON file. If no setttings are found, will
            use predefined settings instead.
        """
        try:
            with open(filename, 'r') as jf:
                settings = json.load(jf)
        except FileNotFoundError:
            settings = defaults
            self.message = ('Settings file not found. The default options '
                            'have been selected.')
        except json.JSONDecodeError:
            settings = defaults
            self.message = ('The settings file cannot be loaded. The default '
                            'options have been selected.')

        if settings.keys() != self.default_settings.keys():
            self.settings = defaults
            self.message = ('The settings has the wrong keys. Try resaving the'
                            ' file. The default options have been selected.')
        else:
            self.settings = settings

    def refresh_method(self, event=None):
        """ Command to refresh method description and data entries depending
            on which method was selected.
        """
        # Method description changed
        self.description.refresh()

        # Hides current entry widget and shows new one
        self.current_entry.grid_remove()
        self.current_entry = self.entries[self.method]
        self.current_entry.grid_replace()

        # Lowers entry widget below message/actions to ensure correct tab order
        self.current_entry.lift(self.sr)

    def refresh_message(self, message, colour='black'):
        """ Command to refresh the calculation message. """
        if colour == 'red':
            self.msg.config(text=message, style='Red.TLabel')
        else:
            self.msg.config(text=message, style='TLabel')

    def clear(self):
        """ Command to clear and reset all entries/selections in data entry.
        """
        self.current_entry.reset_values()

    def calculate(self, event=None):
        """ Takes data, calculates the curve geometry and passes results to
            table.
        """
        self.result.clear_table()

        try:
            if self.sr.dim.get() == 'mph':
                self.mph = float(self.sr.speed.get())
            else:
                self.kph = float(self.sr.speed.get())

            self.minimum_radius = float(self.sr.minimum.get())

        except ValueError:
            self.refresh_message('Error: Speed tolerance and minimum radius '
                                 'must be valid numbers.', 'red')
            return

        try:
            result = self.current_entry.get_result()

        except AttributeError:
            self.refresh_message('Error: All fields must be filled in.', 'red')
            raise

        except (InterfaceException, coord.CoordError, section.TrackError,
                curve.CurveError) as err:
            err_string = {InterfaceException: 'Input error: ',
                          coord.CoordError: 'Coordinate error: ',
                          section.TrackError: 'Track section error: ',
                          curve.CurveError: 'Curve calculation error: '}
            self.refresh_message(err_string[type(err)] + str(err), 'red')
            return

        else:
            self.refresh_message('All OK.')

        self.result.load_table(self.display_data(result))

    def display_data(self, result):
        """ Formats the results data to make them readable and gives correct
            decimal places.
        """
        data = []

        # Check if there are more than one section of a type
        count_static = sum(1 for ts in result if ts.org_type == 'static')
        count_ease = sum(1 for ts in result if ts.org_type == 'easement')
        s, e = 0, 0

        decimal_places = 2 if \
            self.settings.get('two decimal places', False) else 1

        for i, ts in enumerate(result):
            # Creating the radius of curvature text
            if ts.org_curvature == ts.curvature or ts.org_curvature is None:
                # Only one value needed.
                if ts.curvature == 0:
                    roc_text = ts.clockwise.capitalize()
                else:
                    roc_text = '{roc:.{dp}f} {cw}' \
                               ''.format(roc=ts.radius, cw=ts.clockwise,
                                         dp=decimal_places)
            else:
                # Both values needed.
                if ts.org_curvature != 0 and ts.curvature != 0:
                    roc_text = '{st:.{dp}f} to {end:.{dp}f} {cw}' \
                               ''.format(st=ts.org_radius, end=ts.radius,
                                         cw=ts.clockwise, dp=decimal_places)
                elif ts.org_curvature == 0 and ts.curvature != 0:
                    roc_text = '{st} to {end:.{dp}f} {cw}' \
                               ''.format(st=ts.org_clockwise.capitalize(),
                                         end=ts.radius, cw=ts.clockwise,
                                         dp=decimal_places)
                elif ts.org_curvature != 0 and ts.curvature == 0:
                    roc_text = '{st:.{dp}f} {cw} to {end}' \
                               ''.format(st=ts.org_radius, cw=ts.org_clockwise,
                                         end=ts.clockwise.lower(),
                                         dp=decimal_places)
                else:
                    raise ValueError(
                        'Something went wrong here - org curvature {0} and '
                        'curvature {1}'.format(ts.org_curvature, ts.curvature))

            # Setting curve names
            if i == 0 and ts.org_type is None:
                section_name = 'Start point'
            elif ts.org_type == 'static':
                if count_static > 1:
                    s += 1
                    section_name = 'Static {}'.format(s)
                else:
                    section_name = 'Static'
            elif ts.org_type == 'easement':
                if count_ease > 1:
                    e += 1
                    section_name = 'Easement {}'.format(e)
                else:
                    section_name = 'Easement'
            else:
                raise AttributeError('Incorrect type {!r} for TrackCoord '
                                     'object {!r}.'.format(ts.org_type, ts))

            # Setting length value to 1 decimal place
            if ts.org_length is not None:
                length = '{:.{dp}f}'.format(ts.org_length, dp=decimal_places)
            else:
                length = ''

            # Setting position values to 3 decimal places
            pos_x, pos_z = '{:.3f}'.format(ts.pos_x), \
                           '{:.3f}'.format(ts.pos_z)

            # Setting rotation and quad values to 3 decimal places
            rotation, quad = '{:.3f}'.format(ts.quad[0]), ts.quad[1]
            if rotation in ['0.000', '360.000']:
                rotation = '0.000'
                quad = 'N' if quad in ['NE', 'NW'] else 'S'
            elif rotation == '90.000':
                quad = 'W' if quad in ['NW', 'SW'] else 'E'

            data.append((section_name, length, roc_text,
                         pos_x, pos_z, rotation, quad))

        return data


class MethodDescription(ttk.LabelFrame):
    """ LabelFrame widget for displaying method description. """

    description = {
        '1': ("Takes two straight tracks at different angles, and creates an "
              "easement curve with set radius of curvature connecting the two "
              "tracks."),
        '2': ("Extends an easement curve onwards from a track to join with "
              "another straight track. The optional pair of coordinates on "
              "the first track is used to define radius of curvature - if "
              "it is left empty the first track is assumed to be straight.")
    }

    def __init__(self, parent):
        super(MethodDescription, self).__init__(parent)
        self.parent = parent
        self.config(padding="0 0 0 4",
                    text='Method {} description'.format(self.parent.method))
        self.grid(sticky=(tk.W, tk.E))

        self.text = None
        self.body()

    def body(self):
        self.text = ttk.Label(self, text=self.description[self.parent.method])
        self.text.config(
            width=80, wraplength=int(text_length(80)), padding="4 0 0 4")
        self.text.grid(sticky=(tk.W, tk.E))

    def refresh(self):
        """ Refreshes the heading and text when method selection changes. """
        self.config(text='Method {} description'.format(self.parent.method))
        self.text.config(text=self.description[self.parent.method])


class SpeedRadius(ttk.LabelFrame):
    """ LabelFrame widget for setting speed tolerance and minimum radius of
        curvature.
    """

    def __init__(self, parent):
        super(SpeedRadius, self).__init__(parent)
        self.config(padding="4 0 0 8", text='Curve setup')
        self.grid(sticky=(tk.W, tk.E))
        self.columnconfigure(1, pad=4)
        self.parent = parent

        self.speed = tk.StringVar()
        self.dim = tk.StringVar()
        self.minimum = tk.StringVar()
        self.body()

    def body(self):
        ttk.Label(self, text='Speed tolerance ', width=16
                  ).grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(self, textvariable=self.speed, width=8
                  ).grid(row=0, column=1, sticky=tk.W)

        options = ['mph', 'km/h']
        dimensions = ttk.Combobox(self, textvariable=self.dim)
        dimensions.config(width=6, values=options, state='readonly')
        dimensions.set(self.parent.settings.get('speed units', 'mph'))
        dimensions.grid(row=0, column=2, sticky=tk.W)

        ttk.Label(self, text='Minimum radius of curvature ', padding="8 0 0 0"
                  ).grid(row=0, column=3, columnspan=2, sticky=tk.W)
        ttk.Entry(self, textvariable=self.minimum, width=8
                  ).grid(row=0, column=5, sticky=tk.W)
        ttk.Label(self, text='m', padding="4 0 0 0"
                  ).grid(row=0, column=6, sticky=tk.W)


class BaseEntryM(ttk.LabelFrame, metaclass=ABCMeta):
    """ Common class for entry data table. Must be subclassed. """

    quads = ['NE', 'SE', 'SW', 'NW']

    def __init__(self, parent, row):
        super(BaseEntryM, self).__init__(parent)
        self.config(text='Curve data', padding="0 0 0 10")
        self.row = row
        self.grid_replace()

        # Data entries
        self.line0 = self.coord_stringvar()
        self.line1 = self.coord_stringvar()
        self.line2 = self.coord_stringvar()
        self.radius, self.direction = tk.StringVar(), tk.StringVar()
        
        # All rows and columns in grid
        for i in range(5):
            self.grid_columnconfigure(i, pad=4)
        for j in range(4):
            self.grid_rowconfigure(j, pad=4)

        self.parent = parent
        self.get_table()

    def grid_replace(self):
        """ Restores this frame to original position. """
        self.grid(row=self.row, column=0, columnspan=5,
                  sticky=(tk.N, tk.W, tk.E))

    def args(self):
        """ Dict to be used as arguement for the TrackCurve instances. """
        return {'speed': self.parent.kph,
                'minimum': self.parent.minimum_radius,
                'split': self.parent.settings.get('split static curve', False)}

    def reset_values(self):
        """ Resets all entries to their original configuration. """
        self.radius.set('')
        self.direction.set('N/A')
        for line in [self.line0, self.line1, self.line2]:
            for entry in line.values():
                entry.set('')
        self.line0['r'].set('0')
        self.line0['q'].set('NE')

    @staticmethod
    def coord_stringvar():
        return {j: tk.StringVar() for j in 'xzrq'}

    @staticmethod
    def get_coord(data):
        """ Takes a list with 2 or 4 variables - X and Z positions, rotation
            and quad - and converts to a TrackCoord object.
        """
        coordinates = {k: v.get() for k, v in data.items()}
        try:
            if coordinates['q'].upper() in ['NE', 'SE', 'SW', 'NW']:
                rotation = float(coordinates['r'])
                quad = coord.Q[coordinates['q'].upper()]
            else:
                raise AttributeError

            dict_coord = {
                'pos_x': float(coordinates['x']),
                'pos_z': float(coordinates['z']),
                'rotation': rotation,
                'quad': quad,
                'curvature': 0
            }

        except (AttributeError, ValueError):
            raise InterfaceException('The coordinates must be valid integers/'
                                     'floats with a quadrant specified.')

        return coord.TrackCoord(**dict_coord)

    @abstractmethod
    def get_table(self):
        """ Creates grid of entries and labels. """
        pass

    @abstractmethod
    def get_result(self):
        """ Takes entries and calculates the result. """
        pass

    def header(self, text, row=0, column=0):
        ttk.Label(self, text=text).grid(row=row, column=column, sticky=tk.W)

    def start_label(self, text, row, column=0):
        ttk.Label(self, text=text, width=24
                  ).grid(row=row, column=column, sticky=tk.E)

    def coord_entry(self, variable, row, column):
        entry = ttk.Entry(self, textvariable=variable, width=10)
        entry.grid(row=row, column=column, sticky=tk.W)

    def coord_menu(self, variable, options, row, column, default=False):
        menu = ttk.Combobox(self, textvariable=variable)
        menu.config(width=8, values=options, state='readonly')
        menu.grid(row=row, column=column, sticky=tk.W)
        if default:
            # Sets first item in options list as default value
            menu.current(0)


class EntryMethod1(BaseEntryM):
    """ Fits curve with set radius of curvature to a pair of straight tracks
        at an angle. Can set CW/ACW for direction the curve takes.
    """

    def get_table(self):
        self.header('Position X', column=1)
        self.header('Position Z', column=2)
        self.header('Rotation Y', column=3)
        self.header('Quadrant', column=4)

        self.start_label('First straight track', 1)
        self.coord_entry(self.line1['x'], 1, 1)
        self.coord_entry(self.line1['z'], 1, 2)
        self.coord_entry(self.line1['r'], 1, 3)
        self.coord_menu(self.line1['q'], self.quads, 1, 4)

        self.start_label('Second straight track', 2)
        self.coord_entry(self.line2['x'], 2, 1)
        self.coord_entry(self.line2['z'], 2, 2)
        self.coord_entry(self.line2['r'], 2, 3)
        self.coord_menu(self.line2['q'], self.quads, 2, 4)

        self.start_label('Radius of curvature', 3)
        self.coord_entry(self.radius, 3, 1)
        ttk.Label(self, text='m').grid(row=3, column=2, sticky=tk.W)

        ttk.Label(self, text='direction', justify=tk.RIGHT,
                  padding="0 0 4 0").grid(row=3, column=3, sticky=tk.E)
        self.coord_menu(self.direction, ['N/A', 'CW', 'ACW'], 3, 4,
                        default=True)

    def get_result(self):
        start_track = self.get_coord(self.line1)
        end_track = self.get_coord(self.line2)
        try:
            curve_radius = float(self.radius.get())
        except ValueError:
            raise InterfaceException('Radius of curvature must be a number.')

        track = curve.TrackCurve(curve=start_track, **self.args())
        clockwise = {'CW': True, 'ACW': False}.get(self.direction.get())

        return track.curve_fit_radius(other=end_track, radius=curve_radius,
                                      clockwise=clockwise)


class EntryMethod2(BaseEntryM):
    """ Extends curve from point on track (can be either straight or curved -
        radius of curvature is calculated from additional pair of coordinates)
        to join a straight track.
    """

    def get_table(self):
        self.header('Position X', column=1)
        self.header('Position Z', column=2)
        self.header('Rotation Y', column=3)
        self.header('Quadrant', column=4)

        self.start_label('Starting point on track', 1)
        self.coord_entry(self.line1['x'], 1, 1)
        self.coord_entry(self.line1['z'], 1, 2)
        self.coord_entry(self.line1['r'], 1, 3)
        self.coord_menu(self.line1['q'], self.quads, 1, 4)

        self.start_label('Additional coordinates', 2)
        self.coord_entry(self.line0['x'], 2, 1)
        self.coord_entry(self.line0['z'], 2, 2)
        self.line0['r'].set('0')
        self.line0['q'].set('NE')

        self.start_label('Straight track to join', 3)
        self.coord_entry(self.line2['x'], 3, 1)
        self.coord_entry(self.line2['z'], 3, 2)
        self.coord_entry(self.line2['r'], 3, 3)
        self.coord_menu(self.line2['q'], self.quads, 3, 4)

    def get_result(self):
        start_track = self.get_coord(self.line1)
        end_track = self.get_coord(self.line2)
        track = curve.TrackCurve(curve=start_track, **self.args())

        # Check if first two fields are empty - if so, track is straight
        if all(self.line0[k].get() == '' for k in 'xz'):
            return track.curve_fit_point(other=end_track)
        else:
            pre_track = self.get_coord(self.line0)
            return track.curve_fit_point(other=end_track, add_point=pre_track)


class Result(ttk.Frame):
    """ Results table, based on TreeView widget. """
    # TODO: Consider changing TreeView to a grid of Text widgets.

    def __init__(self, parent):
        super(Result, self).__init__(parent)
        self.grid(sticky=(tk.W, tk.E))
        self.treeview = None
        self.parent = parent

        self.create_table()

    def create_table(self):
        """ Initalises table. """
        rows = self.parent.settings.get('results rows', 5)
        tv = ttk.Treeview(self, height=rows)
        ttk.Style().configure('Treeview', rowheight=text_length(3.5))

        columns = ('section', 'length', 'roc', 'pos_x',
                   'pos_z', 'rotation', 'quad')
        columns_d = {
            'section': ('Curve section', 'w', 14),
            'length': ('Length', 'e', 9),
            'roc': ('Radius of curvature', 'w', 22),
            'pos_x': ('Position X', 'e', 11),
            'pos_z': ('Position Z', 'e', 11),
            'rotation': ('Rotation', 'e', 10),
            'quad': ('Quad', 'w', 7)
        }

        tv['columns'] = columns
        # Hides the first column
        tv['show'] = 'headings'

        for col in columns:
            c = columns_d[col]
            tv.heading(col, text=c[0], anchor='w')
            tv.column(col, anchor=c[1], width=text_length(c[2]))

        tv.grid(sticky=(tk.N, tk.S, tk.W, tk.E))
        self.treeview = tv

    def load_table(self, data):
        """ Loads table using data (list of tuples). """
        for sec in data:
            self.treeview.insert('', 'end', text='', values=sec)

    def clear_table(self):
        """ Deletes all data from table. """
        self.treeview.delete(*self.treeview.get_children())


def main():
    root = tk.Tk()
    root.title('Easement curve calculator')
    root.resizable(height=False, width=False)
    root.iconbitmap(resource_path('resources/logo.ico'))
    MainWindow(root)

    root.mainloop()

if __name__ == "__main__":
    main()
