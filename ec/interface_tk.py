# MIT License, copyright Ewan Macpherson, 2016; see LICENCE in root directory
# Tk graphical user interface for easement curve calculations

from abc import ABCMeta, abstractmethod
from tkinter import *
from tkinter.font import *
from tkinter.ttk import *

from . import curve

# TODO: Clean up the code and test??
# TODO: Sort out the text.
# TODO: Add docstrings.
# TODO: multi_string_var may be better as a dictionary, but care needs to be taken with EntryM.

instructions = """
1. Find a point with coordinates ({x0}, {z1}) on the first straight track, and cut it at that point.
2. Extend an easement curve ending with radius of curvature {roc} in the {cw} direction.
3. Extend a static curve with radius of curvature and make sure it is at least {l} long.
4. Find a point on the static curve with rotation {r} {q}, and cut it at that point.
5. Create another easement curve and straighten it out to join the second track.
"""


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

    description = {
        '1': ("Takes two straight tracks at different angles, and creates an easement curve "
              "with set radius of curvature connecting the two tracks."),
        '2': ("Extends an easement curve onwards from a straight track to join with another "
              "straight track."),
        '3': ("Extends an easement curve onwards from a curved track (defined with another "
              "pair of coordinates to give a more accurate figure) to join with a straight "
              "track.")
    }

    def __init__(self, parent):
        # Properties
        self._kph = None

        # Whole frame
        self.container = Frame(parent, padding="5 5 5 5")
        self.container.grid(row=0, column=0)

        # Calc method select and description
        self.method = StringVar()
        self.method_heading, self.method_description = None, None
        self.select_method()
        self.show_method_description()

        # Enter speed tolerance (in mph or km/h) and minimum radius
        self.speed, self.dim = DoubleVar(), StringVar()
        self.min_radius = IntVar()
        self.select_speed_radius()

        # Create lists of stringvars and grid for entering data
        self.line0, self.line1, self.line2 = \
            multi_string_var(), multi_string_var(), multi_string_var()
        self.radius, self.cw = StringVar(), StringVar()
        self.entries = {'1': EntryMethod1, '2': EntryMethod2,
                        '3': EntryMethod3}
        self.current_entry = self.entries[self.m](self.container, self)

        # Message
        Style().configure("Red.TLabel", foreground="red")
        self.msg = None
        self.actions()
        self.message()

        # 2 tabs: results table and instructions
        self.result, self.instruction = None, None
        self.results()

    @property
    def m(self):
        return self.method.get()

    @m.setter
    def m(self):
        raise AttributeError("Can't set m property manually.")

    @property
    def mph(self):
        return self._kph / 1.609344

    @mph.setter
    def mph(self, value):
        self._kph = value * 1.609344

    @property
    def kph(self):
        return self._kph

    @kph.setter
    def kph(self, value):
        self._kph = value

    def select_speed_radius(self):
        st = LabelFrame(self.container, text="Curve setup", padding="0 0 0 8")
        st.grid(column=0, row=2, sticky=(W, E))

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

    def select_method(self):
        sm = Frame(self.container)
        sm.grid(column=0, row=0, sticky=W)

        Label(sm, text="Select method ").grid(column=0, row=1)

        options = ['1', '2', '3']
        method = OptionMenu(sm, self.method, options[0], *options,
                            command=self.refresh_method)
        method.grid(column=1, row=1)

    def show_method_description(self):
        self.method_heading = LabelFrame(
            self.container, text="Method {} description".format(self.m))
        self.method_heading.grid(row=1, sticky=(W, E))

        self.method_description = Label(self.method_heading,
                                        text=self.description[self.m])
        self.method_description.config(
            width=82, wraplength=int(get_text_length(82)), padding="4 0 0 4")
        self.method_description.grid(sticky=(W, E))

    def refresh_method(self, event):
        self.method_heading.config(text="Method {} description".format(self.m))
        self.method_description.config(text=self.description[self.m])

        self.current_entry.destroy()
        self.current_entry = self.entries[self.m](self.container, self)

    def actions(self):
        ac = Frame(self.container, padding="4 0 0 0")
        ac.grid(column=1, row=3, sticky=S)
        ac.rowconfigure(0, pad=4)

        clear = Button(ac, text="Clear", command=self.clear)
        clear.grid(column=0, row=0, sticky=E)

        calc = Button(ac, text="Calculate", command=self.calculate)
        calc.grid(column=0, row=1, sticky=E)

    def message(self):
        self.msg = Label(self.container, text='', padding="4 0 0 4")
        self.msg.config(width=92, wraplength=int(get_text_length(92)))
        self.msg.grid(column=0, row=4, columnspan=2, sticky=(W, E))

    def refresh_message(self, message, colour='black'):
        if colour == 'red':
            self.msg.config(text=message, style='Red.TLabel')
        else:
            self.msg.config(text=message, style='TLabel')

    def results(self):
        self.result = Result(self.container)
        self.result.grid(column=0, row=5, sticky=(W, E), columnspan=2)

    def clear(self):
        self.radius.set('')
        self.cw.set('N/A')
        for line in [self.line0, self.line1, self.line2]:
            for entry in line:
                entry.set('')

    def calculate(self):
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

        order = ("Start point", "Easement curve 1", "Static curve",
                 "Easement curve 2")
        self.result.clear_table()
        self.result.load_table(order, self.display_data(result))

    @staticmethod
    def display_data(result):
        data = {}
        labels = {'start': 'Start point', 'ec1': 'Easement curve 1',
                  'static': 'Static curve', 'ec2': 'Easement curve 2'}
        for section in ['start', 'ec1', 'static', 'ec2']:
            ts = result[section]
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

            length = '{:.1f}'.format(ts.org_length) if \
                ts.org_length is not None else ''

            pos_x, pos_z = '{:.3f}'.format(ts.pos_x), \
                           '{:.3f}'.format(ts.pos_z)

            rotation, quad = '{:.3f}'.format(ts.quad[0]), ts.quad[1]
            if rotation == '0.000':
                quad = 'N' if quad in ['NE', 'NW'] else 'S'
            elif rotation == '90.000':
                quad = 'W' if quad in ['NW', 'SW'] else 'E'

            data[labels[section]] = (length, roc_text, pos_x, pos_z,
                                     rotation, quad)

        return data


class EntryM(LabelFrame, metaclass=ABCMeta):

    def __init__(self, parent, controller):
        super(EntryM, self).__init__(parent)
        self.config(text="Curve data", padding="0 0 0 10")
        self.grid(row=3, column=0, sticky=(N, W, E))

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
        pass

    @abstractmethod
    def get_result(self):
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

    def get_table(self):
        self.start_label("Starting point on straight track", 0)
        self.entry_boxes(self.controller.line1, 4, 0)
        self.end_label("X, Z, R, Q", 0)

        self.start_label("Straight track to join", 1)
        self.entry_boxes(self.controller.line2, 4, 1)
        self.end_label("X, Z, R, Q", 1)

        self.start_label("", 2)

    def get_result(self):
        start_track = self.get_coord(self.controller.line1)
        end_track = self.get_coord(self.controller.line2)

        track = curve.TrackCurve(curve=start_track, **self.args())
        return track.curve_fit_point(other=end_track)


class EntryMethod3(EntryM):

    def get_table(self):
        self.start_label("Starting point on curved track", 0)
        self.entry_boxes(self.controller.line1, 4, 0)
        self.end_label("X, Z, R, Q", 0)

        self.start_label("Additional point on curve", 1)
        self.entry_boxes(self.controller.line0, 2, 1)
        self.end_label("X, Z", 1)
        self.controller.line0[2].set('0')
        self.controller.line0[3].set('NE')

        self.start_label("Straight track to join", 2)
        self.entry_boxes(self.controller.line2, 4, 2)
        self.end_label("X, Z, R, Q", 2)

    def get_result(self):
        start_track = self.get_coord(self.controller.line1)
        pre_track = self.get_coord(self.controller.line0)
        end_track = self.get_coord(self.controller.line2)

        track = curve.TrackCurve(curve=start_track, **self.args())
        return track.curve_fit_point(other=end_track, add_point=pre_track)


class Result(Frame):

    def __init__(self, parent):
        super(Result, self).__init__(parent)
        self.treeview = None
        self.create_table()

    def create_table(self):
        tv = Treeview(self, height=5)
        columns = ('length', 'roc', 'pos_x', 'pos_z', 'rotation', 'quad')
        columns_d = {'length': ('Length', 'e', 10),
                     'roc': ('Radius of curvature', 'w', 24),
                     'pos_x': ('Position x', 'e', 12),
                     'pos_z': ('Position z', 'e', 12),
                     'rotation': ('Rotation', 'e', 12),
                     'quad': ('Quad', 'w', 8)}
        tv['columns'] = columns
        tv.heading("#0", text='Curve section', anchor='w')
        tv.column("#0", anchor="w", width=get_text_length(20))
        for col in columns:
            c = columns_d[col]
            tv.heading(col, text=c[0], anchor='w')
            tv.column(col, anchor=c[1], width=get_text_length(c[2]))

        tv.grid(sticky=(N, S, W, E))
        self.treeview = tv

    def load_table(self, order, data):
        for section in order:
            if data[section] is not None:
                self.treeview.insert('', 'end', text=section,
                                     values=data[section])

    def clear_table(self):
        self.treeview.delete(*self.treeview.get_children())


def main():
    root = Tk()
    root.title("Easement curve calculator")
    root.resizable(height=False, width=False)
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
