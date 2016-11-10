# MIT License, copyright Ewan Macpherson, 2016; see LICENCE in root directory
# Tk graphical user interface for easement curve calculations

from abc import ABCMeta, abstractmethod
from sys import version_info
from tkinter import *
from tkinter.font import *
from tkinter.ttk import *

from . import curve, __version__

# TODO: Clean up the code and test??
# TODO: Sort out the text.
# TODO: Create an About dialog box.
# TODO: Consider changing TreeView to a grid of Text widgets.


def get_text_length(length, font='TkDefaultFont'):
    """ Retrieves the length of a string defined by number of characters
        in terms of pixels.
    """
    base_length = nametofont(font).measure('e' * 80)
    return round(base_length * length / 80)


def multi_string_var(i=4):
    """ Creates a list of multiple StringVar instances. """
    return [StringVar() for j in range(i)]


class InterfaceException(Exception):
    pass


class App(object):
    """ Main application window. """

    description = {
        '1': ("Takes two straight tracks at different angles, and creates an "
              "easement curve with set radius of curvature connecting the two "
              "tracks."),
        '2': ("Extends an easement curve onwards from a straight track to join"
              " with another straight track. The optional pair of coordinates "
              "on the first track is used to define radius of curvature - if "
              "it is left empty the first track is assumed to be straight.")
    }

    def __init__(self, parent):
        # Properties
        self._kph = None

        # Setting up window
        self.parent = parent
        self.parent.title("Easement curve calculator")
        self.parent.resizable(height=False, width=False)

        # Main frame
        self.container = Frame(self.parent, padding="5 5 5 5")
        self.container.grid(row=0, column=0)

        # Calc method select and description
        self.selected_method = StringVar()
        self.method_heading, self.method_description = None, None
        self.select_method_about(row=0)
        self.show_method_description(row=1)

        # Enter speed tolerance (in mph or km/h) and minimum radius
        self.speed, self.dim = DoubleVar(), StringVar()
        self.min_radius = IntVar()
        self.select_sr(row=2)

        # Create lists of stringvars and grid for entering data
        self.line0, self.line1, self.line2 = \
            multi_string_var(), multi_string_var(), multi_string_var()
        self.radius, self.cw = StringVar(), StringVar()
        self.entries = {'1': EntryMethod1, '2': EntryMethod2}
        self.row = 3
        self.current_entry = self.entries[self.method](
            self.container, self, row=self.row)

        # Message
        Style().configure("Red.TLabel", foreground="red")
        self.msg = None
        self.message_actions(row=4)

        # Results table
        self.result = None
        self.results(row=5)

        # Bindings
        parent.bind('<Return>', self.calculate)

    @property
    def method(self):
        """ Retrieves method selection. """
        return self.selected_method.get()

    @method.setter
    def method(self):
        raise AttributeError("Can't set method property manually.")

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

    def select_sr(self, row):
        """ LabelFrame widget with speed tolerance and minimum radius entries.
        """
        st = LabelFrame(self.container, text="Curve setup", padding="0 0 0 8")
        st.grid(column=0, row=row, sticky=(W, E))

        options = ['mph', 'km/h']
        Label(st, text="Speed tolerance ",
              padding="4 0 0 0").grid(column=0, row=0)
        speed = Entry(st, textvariable=self.speed, width=6)
        speed.grid(column=1, row=0)
        speed_dim = OptionMenu(st, self.dim, options[0], *options)
        speed_dim.grid(column=2, row=0)
        speed_dim.config(width=5)

        Label(st, text="Minimum radius of curvature ").grid(column=3, row=0)
        minimum_radius = Entry(st, textvariable=self.min_radius, width=6)
        minimum_radius.grid(column=4, row=0)
        Label(st, text="m", padding="4 0 0 0").grid(column=5, row=0)

    def select_method_about(self, row):
        """ Widget for calculation method selection. as well as About button.
        """
        sm = Frame(self.container, padding="6 0 0 0")
        sm.grid(column=0, row=row, sticky=(W, E))
        sm.columnconfigure(2, weight=1)

        Label(sm, text="Select method ").grid(column=0, row=0)

        options = ['1', '2']
        method_menu = OptionMenu(sm, self.selected_method, options[0],
                                 *options, command=self.refresh_method)
        method_menu.grid(column=1, row=0)

        about = Button(sm, text="About", command=self.open_about)
        about.grid(column=3, row=0, sticky=E)

    def open_about(self, event=None):
        AboutWindow(self.parent)

    def show_method_description(self, row):
        """ LabelFrame widget for displaying method description. """
        self.method_heading = LabelFrame(
            self.container, text="Method {} description".format(self.method))
        self.method_heading.grid(row=row, sticky=(W, E))

        self.method_description = Label(self.method_heading,
                                        text=self.description[self.method])
        self.method_description.config(
            width=82, wraplength=int(get_text_length(82)), padding="4 0 0 4")
        self.method_description.grid(sticky=(W, E))

    def refresh_method(self, event=None):
        """ Command to refresh method description and data entries depending
            on which method was selected.
        """
        self.method_heading.config(text="Method {} description".format(self.method))
        self.method_description.config(text=self.description[self.method])

        self.current_entry.destroy()
        self.current_entry = self.entries[self.method](
            self.container, self, self.row)

    def message_actions(self, row):
        """ Row for message (all OK or errors in calculations) and Calculate/
            Clear buttons.
        """
        ma = Frame(self.container, padding="0 4 0 4")
        ma.grid(column=0, row=row, sticky=(W, E))
        ma.columnconfigure(3, pad=4)
        ma.columnconfigure(1, weight=1)

        self.msg = Label(ma, text='')
        self.msg.config(width=56, wraplength=int(get_text_length(56)))
        self.msg.grid(column=0, row=0, sticky=W)

        calc = Button(ma, text="Calculate", command=self.calculate)
        calc.grid(column=2, row=0, sticky=(N, E))

        clear = Button(ma, text="Clear", command=self.clear)
        clear.grid(column=3, row=0, sticky=(N, E))

    def refresh_message(self, message, colour='black'):
        """ Command to refresh the calculation message. """
        if colour == 'red':
            self.msg.config(text=message, style='Red.TLabel')
        else:
            self.msg.config(text=message, style='TLabel')

    def results(self, row):
        """ Shows the results table. """
        self.result = Result(self.container)
        self.result.grid(column=0, row=row, sticky=(W, E))

    def clear(self):
        """ Command to clear and reset all entries/selections in data entry.
        """
        self.msg.config(text='')
        self.radius.set('')
        self.cw.set('N/A')
        for line in [self.line0, self.line1, self.line2]:
            for entry in line:
                entry.set('')

    def calculate(self, event=None):
        """ Takes data, calculates the curve geometry and passes results to
            table.
        """
        self.result.clear_table()

        if self.dim.get() == 'mph':
            self.mph = self.speed.get()
        else:
            self.kph = self.speed.get()

        try:
            result = self.current_entry.get_result()

        except AttributeError as err:
            self.refresh_message('Error: All fields must be filled in.', 'red')
            raise AttributeError from err

        except (InterfaceException, curve.CoordException, curve.TrackException,
                curve.CurveException) as err:
            err_string = {InterfaceException: "Input error: ",
                          curve.CoordException: "Coordinate error: ",
                          curve.TrackException: "Track section error: ",
                          curve.CurveException: "Curve calculation error: "}
            message = err_string[type(err)] + str(err)
            self.refresh_message(message, 'red')
            return

        else:
            self.refresh_message('All OK.')

        table = self.display_data(result)
        self.result.load_table(table)

    @staticmethod
    def display_data(result):
        """ Formats the results data to make them readable and gives correct
            decimal places.
        """
        data = []

        # Check if there are more than one section of a type
        count_static = sum(1 for ts in result if ts.org_type == 'static')
        count_ease = sum(1 for ts in result if ts.org_type == 'easement')
        s, e = 0, 0

        for i, ts in enumerate(result):
            if ts is None:
                continue

            # Creating the radius of curvature text
            if ts.org_curvature == ts.curvature or ts.org_curvature is None:
                # Only one value needed.
                if ts.curvature == 0:
                    roc_text = ts.clockwise.capitalize()
                else:
                    roc_text = '{0:.1f} {1}'.format(ts.radius, ts.clockwise)
            else:
                # Both values needed.
                if ts.org_curvature != 0 and ts.curvature != 0:
                    roc_text = '{0:.1f} to {1:.1f} {2}'.format(
                        ts.org_radius, ts.radius, ts.clockwise)
                elif ts.org_curvature == 0 and ts.curvature != 0:
                    roc_text = '{0} to {1:.1f} {2}'.format(
                        ts.org_clockwise.capitalize(), ts.radius, ts.clockwise)
                elif ts.org_curvature != 0 and ts.curvature == 0:
                    roc_text = '{0:.1f} {1} to {2}'.format(
                        ts.org_radius, ts.org_clockwise, ts.clockwise.lower())
                else:
                    raise Exception(
                        "Something went wrong here - org curvature {0} and "
                        "curvature {1}".format(ts.org_curvature, ts.curvature))

            # Setting curve names
            if i == 0 and ts.org_type is None:
                section_name = 'Start point'
            elif ts.org_type == 'static':
                if count_static > 1:
                    s += 1
                    section_name = 'Static curve {}'.format(s)
                else:
                    section_name = 'Static curve'
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
            length = '{:.1f}'.format(ts.org_length) if \
                ts.org_length is not None else ''

            # Setting position values to 3 decimal places
            pos_x, pos_z = '{:.3f}'.format(ts.pos_x), \
                           '{:.3f}'.format(ts.pos_z)

            # Setting rotation and quad values to 3 decimal places
            rotation, quad = '{:.3f}'.format(ts.quad[0]), ts.quad[1]
            if rotation in ['0.000', '360.000']:
                quad = 'N' if quad in ['NE', 'NW'] else 'S'
            elif rotation == '90.000':
                quad = 'W' if quad in ['NW', 'SW'] else 'E'

            data.append((section_name, length, roc_text,
                         pos_x, pos_z, rotation, quad))

        return data


class EntryM(LabelFrame, metaclass=ABCMeta):
    """ Common class for entry data table. Must be subclassed. """

    def __init__(self, parent, controller, row):
        super(EntryM, self).__init__(parent)
        self.config(text="Curve data", padding="0 0 0 10")
        self.grid(row=row, column=0, sticky=(N, W, E))

        for i in range(5):
            self.grid_columnconfigure(i, pad=4)
        for j in range(3):
            self.grid_rowconfigure(j, pad=4)
        self.grid_columnconfigure(0, pad=4)

        self.controller = controller
        self.curve_args = None

        self.get_table()

    def args(self):
        return {'speed': self.controller.kph,
                'minimum': self.controller.min_radius.get()}

    @staticmethod
    def get_coord(data):
        """ Takes a list with 2 or 4 variables - X and Z positions, rotation
            and quad - and converts to a TrackCoord object.
        """
        coord = [i.get() for i in data]
        try:
            if coord[3].upper() in ['NE', 'SE', 'SW', 'NW']:
                rotation = float(coord[2])
                quad = curve.Q[coord[3].upper()]
            else:
                raise AttributeError

            dict_coord = {
                'pos_x': float(coord[0]),
                'pos_z': float(coord[1]),
                'rotation': rotation,
                'quad': quad,
                'curvature': 0
            }

        except (AttributeError, ValueError):
            raise InterfaceException("The coordinates must be valid integers/"
                                     "floats with a quadrant specified.")

        return curve.TrackCoord(**dict_coord)

    @abstractmethod
    def get_table(self):
        """ Creates grid of entries and labels. """
        pass

    @abstractmethod
    def get_result(self):
        """ Takes entries and calculates the result. """
        pass

    def start_label(self, text, row, column=0):
        Label(self, text=text, width=28).grid(row=row, column=column, sticky=E)

    def entry_boxes(self, variable, it, row, column=1, width=8):
        for i in range(it):
            Entry(self, textvariable=variable[i], width=width
                  ).grid(row=row, column=i+column, sticky=W)

    def end_label(self, text, row, column=5):
        Label(self, text=text).grid(row=row, column=column, sticky=W)


class EntryMethod1(EntryM):
    """ Fits curve with set radius of curvature to a pair of straight tracks
        at an angle. Can set CW/ACW for direction the curve takes.
    """

    def get_table(self):
        self.start_label("1st straight track", 0)
        self.entry_boxes(self.controller.line1, 4, 0)
        self.end_label("X, Z, R, Q", 0)

        self.start_label("2nd straight track", 1)
        self.entry_boxes(self.controller.line2, 4, 1)
        self.end_label("X, Z, R, Q", 1)

        self.start_label("Radius of curvature", 2)
        Entry(self, textvariable=self.controller.radius, width=8
              ).grid(row=2, column=1, sticky=W)
        Label(self, text="m").grid(row=2, column=2, sticky=W)
        Label(self, text="direction", justify=RIGHT).grid(row=2, column=3, sticky=E)
        options = ['N/A', 'CW', 'ACW']
        OptionMenu(self, self.controller.cw, options[0], *options
                   ).grid(row=2, column=4, sticky=W, columnspan=2)

    def get_result(self):
        start_track = self.get_coord(self.controller.line1)
        end_track = self.get_coord(self.controller.line2)
        try:
            curve_radius = float(self.controller.radius.get())
        except ValueError:
            raise InterfaceException('Radius of curvature must be a number.')

        track = curve.TrackCurve(curve=start_track, **self.args())
        dict_cw = {'CW': True, 'ACW': False}
        clockwise = dict_cw.get(self.controller.cw.get())

        return track.curve_fit_radius(other=end_track, radius=curve_radius,
                                      clockwise=clockwise)


class EntryMethod2(EntryM):
    """ Extends curve from point on track (can be either straight or curved -
        radius of curvature is calculated from additional pair of coordinates)
        to join a straight track.
    """

    def get_table(self):
        self.start_label("Add. point on starting track", 0)
        self.entry_boxes(self.controller.line0, 2, 0)
        self.end_label("X, Z", 0)
        self.controller.line0[2].set('0')
        self.controller.line0[3].set('NE')

        self.start_label("Starting point on curved track", 1)
        self.entry_boxes(self.controller.line1, 4, 1)
        self.end_label("X, Z, R, Q", 1)

        self.start_label("Straight track to join", 2)
        self.entry_boxes(self.controller.line2, 4, 2)
        self.end_label("X, Z, R, Q", 2)

    def get_result(self):
        start_track = self.get_coord(self.controller.line1)
        end_track = self.get_coord(self.controller.line2)

        track = curve.TrackCurve(curve=start_track, **self.args())

        # Empty fields - ignore extra point and assume first track straight
        if all(k.get() == '' for k in self.controller.line0):
            return track.curve_fit_point(other=end_track)
        else:
            pre_track = self.get_coord(self.controller.line0)
            return track.curve_fit_point(other=end_track, add_point=pre_track)


class Result(Frame):
    """ Results table, based on TreeView widget. """

    def __init__(self, parent):
        super(Result, self).__init__(parent)
        self.treeview = None
        self.create_table()

    def create_table(self):
        """ Initalises table. """
        tv = Treeview(self, height=5)
        Style().configure('Treeview', rowheight=get_text_length(3.5))

        columns = ('section', 'length', 'roc', 'pos_x',
                   'pos_z', 'rotation', 'quad')
        columns_d = {'section': ('Curve section', 'w', 14),
                     'length': ('Length', 'e', 9),
                     'roc': ('Radius of curvature', 'w', 22),
                     'pos_x': ('Position x', 'e', 11),
                     'pos_z': ('Position z', 'e', 11),
                     'rotation': ('Rotation', 'e', 10),
                     'quad': ('Quad', 'w', 7)}

        tv['columns'] = columns
        # Hides the first column
        tv['show'] = 'headings'

        for col in columns:
            c = columns_d[col]
            tv.heading(col, text=c[0], anchor='w')
            tv.column(col, anchor=c[1], width=get_text_length(c[2]))

        tv.grid(sticky=(N, S, W, E))
        self.treeview = tv

    def load_table(self, data):
        """ Loads table using data (list of tuples). """
        for sec in data:
            self.treeview.insert('', 'end', text='', values=sec)

    def clear_table(self):
        """ Deletes all data from table. """
        self.treeview.delete(*self.treeview.get_children())


class AboutWindow(Toplevel):

    def __init__(self, parent):
        super(AboutWindow, self).__init__(parent)

        # Positioning the window relative to the main window
        offset = 30
        x, y = parent.winfo_rootx(), parent.winfo_rooty()
        self.geometry('+{x:d}+{y:d}'.format(x=x+offset, y=y+offset))

        # Setting up the window
        self.title('About')
        self.transient(parent)
        self.resizable(False, False)

        self.container = Frame(self, padding="5 5 5 5")
        self.container.grid(row=0, column=0)

        text = ('Easement curve calculator, version {ecv}\n'
                'Copyright Ewan Macpherson, 2016\n'
                'Python version {pyv}')
        about_text = Label(self.container, text=text.format(
            ecv=__version__, pyv='.'.join(str(i) for i in version_info[:3])))
        about_text.grid(row=0, column=1, sticky=W)

        exit_button = Button(self.container, text='Exit', command=self.withdraw)
        exit_button.grid(row=1, column=0, columnspan=2, sticky=E)


def main():
    root = Tk()
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
