# MIT License, copyright Ewan Macpherson, 2016; see LICENCE in root directory
# Command line interface for easement curve calculations

import os
import re
import sys

from . import __version__
import ec.curve as curve


help_text = """
This is the help text.
"""


class InterfaceException(Exception):
    pass


class Interface(object):

    re_speed_radius = re.compile('^([.,\d]+)\s*([/\w]+)\s+(\d+)\s*$')
    re_method_1 = re.compile('^\(([^()]+)\)[\s,]*\(([^()]+)\)[\s,]*([-.\d]+)\s*$')
    re_method_2 = re.compile('^\(([^()]+)\)[\s,]*\(([^()]+)\)\s*$')
    re_method_3 = re.compile('^\(([^()]+)\)[\s,]*\(([^()]+)\)[\s,]*\(([^()]+)\)\s*$')

    def __init__(self, *args):

        self._kph = None
        self.minimum_radius = None
        self.track0 = None
        self.track1 = None
        self.track2 = None
        self.curve_radius = None
        self.language = 'en'

        # Checks arguments
        if len(args) == 1:
            self.run()
        elif len(args) == 2 and args[1].upper() == 'HELP':
            print(help_text)
        else:
            print("Wrong arguments inputted.", help_text)
            sys.exit(2)

        sys.exit(0)

    @property
    def speed_radius(self):
        return self._kph

    @speed_radius.setter
    def speed_radius(self, value):
        """ Receives as string, in form "100kph 600" or "100 kph 600", with
            mph, kmh and km/h as alternatives. Stores value in _kph and
            minimum_radius.
        """
        # Use regex for this! And everything else.
        try:
            find_speed = self.re_speed_radius.match(value)
            speed_value = find_speed.group(1)
            speed_dim = find_speed.group(2)
            self.minimum_radius = float(find_speed.group(3))
        except ValueError:
            raise InterfaceException("Minimum radius must be a positive "
                                     "number.")
        except AttributeError:
            raise InterfaceException("Must be in format '100 mph 600'.")

        try:
            if speed_dim.upper() == 'MPH':
                self.mph = float(speed_value)
                str_speed = "{0} {1}".format(self.mph, 'mph')
            elif speed_dim.upper() in ['KPH', 'KMH', 'KM/H']:
                self.kph = float(speed_value)
                str_speed = "{0} {1}".format(self.kph, 'km/h')
            else:
                raise InterfaceException("The dimension given is incorrect - "
                                         "must be mph, kph or km/h.")
        except ValueError:
            raise InterfaceException("Speed tolerance must be a positive "
                                     "number.")

        print("\nSpeed tolerance set as {0} and minimum radius {1} m."
              "".format(str_speed, self.minimum_radius))

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

    def run(self):
        os.system('cls')
        print("", "Easement curve calculator, version {0}".format(__version__), "",
              sep='\n')
        # Get minimum radius and tolerance
        print("Start with the speed tolerance and minimum radius of curvature "
              "for the curves\nyou want to calculate, like for example "
              "'80 mph 500' or '40 kph 200'.\n")
        while True:
            input_sm = self.get_input("Enter speed & minimum radius > ")
            try:
                if input_sm is None:
                    continue
                else:
                    self.speed_radius = input_sm
            except InterfaceException as err:
                print("Values are invalid.", err)
                continue
            else:
                break

        # Now can receive main input
        print("Enter 'help' to view docs or 'quit'/'exit' to quit.")
        while True:
            input_data = self.get_input("\nEnter curve data > ")

            if input_data is None:
                continue

            elif self.re_speed_radius.match(input_data):
                try:
                    self.speed_radius = input_data
                except InterfaceException as err:
                    print("Values are invalid.", err)
                    continue

            elif self.re_method_1.match(input_data):
                try:
                    self.get_result(1, input_data)

                except InterfaceException as err:
                    print("Method 1 needs two sets of coordinates and a "
                          "radius of curvature in this format\n"
                          "\t'(x0 z0 r0 Q0) (x1 z1 r1 Q0) R',\n"
                          "with all but the quadrants as numbers.")
                    print('\n', err, sep='')
                    continue

            elif self.re_method_2.match(input_data):
                try:
                    self.get_result(2, input_data)

                except InterfaceException as err:
                    print("Method 2 needs two sets of coordinates in this "
                          "format\n\t'(x1 z1 r1 Q1) (x2 z2 r2 Q2)',\n"
                          "with all but the quadrants as numbers.")
                    print('\n', err, sep='')
                    continue

            elif self.re_method_3.match(input_data):
                try:
                    self.get_result(3, input_data)

                except InterfaceException as err:
                    print("Method 3 needs three sets of coordinates in this "
                          "format\n\t'(x0 z0 r0 Q0) (x1 z1 r1 Q0) (x2 z2 r2"
                          "Q2)',\nwith all but the quadrants as numbers.")
                    print('\n', err, sep='')
                    continue

            else:
                print("Your input was not valid. Try again? Enter 'help' for "
                      "more information.")

    def get_result(self, method, data):
        curve_args = {'speed': self.kph, 'minimum': self.minimum_radius}
        try:
            if method == 1:
                print("Method 1 picked with speed tolerance {0:.1f} mph / "
                      "{1:.1f} kph.\n".format(self.mph, self.kph))

                find_data = self.re_method_1.match(data)
                start_track = self.get_coord(find_data.group(1))
                end_track = self.get_coord(find_data.group(2))
                self.curve_radius = float(find_data.group(3))

                track = curve.TrackCurve(curve=start_track, **curve_args)
                result = track.curve_fit_radius(
                    radius=self.curve_radius, other=end_track)

            elif method == 2:
                print("Method 2 picked with speed tolerance {0:.1f} mph / "
                      "{1:.1f} kph.\n".format(self.mph, self.kph))

                find_data = self.re_method_2.match(data)
                start_track = self.get_coord(find_data.group(1))
                end_track = self.get_coord(find_data.group(2))

                track = curve.TrackCurve(curve=start_track, **curve_args)
                result = track.curve_fit_point(other=end_track)

            elif method == 3:
                print("Method 3 picked with speed tolerance {0:.1f} mph / "
                      "{1:.1f} kph.\n".format(self.mph, self.kph))

                find_data = self.re_method_3.match(data)
                pre_track = self.get_coord(find_data.group(1))
                start_track = self.get_coord(find_data.group(2))
                end_track = self.get_coord(find_data.group(3))

                track = curve.TrackCurve(curve=start_track, **curve_args)
                track.get_static_radius(pre_track)
                result = track.curve_fit_point(other=end_track)

            else:
                raise InterfaceException("An invalid method was used")

        except curve.CoordException as err:
            print("Coordinate error:", err, sep='\n')
            return
        except curve.TrackException as err:
            print("Track section error:", err, sep='\n')
            return
        except curve.CurveException as err:
            print("Curve calculation error:", err, sep='\n')
            return

        print(self.print_curve_data(result), '\n')

    @staticmethod
    def get_input(prompt):
        str_input = input(prompt)
        if str_input.upper() in ['QUIT', 'EXIT', 'EXIT()']:
            sys.exit(0)
        elif str_input.upper() == 'HELP':
            print(help_text)
        else:
            return str_input

    @staticmethod
    def get_coord(coord):
        """ Takes a string with 4 variables - x and y positions, y rotation and
            quadrant alignment - and outputs a TrackCoord object with these
            arguments.
        """
        try:
            find_coord = re.match('^(-?\d*\.?\d+)[,\s]+(-?\d*\.?\d+)[,\s]+'
                                  '(-?\d*\.?\d+)[,\s]+([enswENSW]{2})\s*$',
                                  coord)
            dict_coord = {
                'pos_x': float(find_coord.group(1)),
                'pos_z': float(find_coord.group(2)),
                'rotation': float(find_coord.group(3)),
                'quad': curve.Q[find_coord.group(4)],
                'curvature': 0
            }

        except AttributeError:
            raise InterfaceException("The coordinates must be valid integers/"
                                     "floats with a quadrant specified.")

        return curve.TrackCoord(**dict_coord)

    @staticmethod
    def print_curve_data(curve_data):
        """ Prints on screen the data obtained from creating a curve with
            easements in a table.
        """
        ls_headers = ['name', 'length', 'roc', 'position', 'bearing', 'rotation']
        headers = {
            'name': 'Curve Section', 'length': 'Length',
            'roc': 'Radius of curvature', 'position': 'Position (x, z)',
            'bearing': 'Bearing', 'rotation': 'Rotation'
        }
        labels = {'start': 'Start point', 'ec1': 'Easement curve 1',
                  'static': 'Static curve', 'ec2': 'Easement curve 2'}

        table_data = {}

        for section in ['start', 'ec1', 'static', 'ec2']:
            ts = curve_data[section]
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

            length = ts.org_length if ts.org_length is not None else ''
            bearing = '{:7.3f}'.format(ts.bearing.deg)
            rotation = '{0:7.3f} {1:.2}'.format(*ts.quad)

            row_data = [labels[section], length, roc_text, (ts.pos_x, ts.pos_z),
                        bearing, rotation]
            current_row = dict(zip(ls_headers, row_data))

            table_data[section] = current_row

        # Finding the maximum string length to fit in the position values
        pos_values = [table_data[k]['position'] for k in table_data.keys()]
        mx = max(len('{: .3f}'.format(i[0])) for i in pos_values)
        mz = max(len('{: .3f}'.format(i[1])) for i in pos_values)

        # Applying the max length to the table position values
        for k, v in table_data.items():
            x, z = v['position']
            table_data[k]['position'] = \
                '{x: {mx}.3f}  {z: {mz}.3f}'.format(x=x, z=z, mx=mx, mz=mz)

        # Finding the maximum string length to fit in the length values
        length_max = max(len('{:.1f}'.format(table_data[k]['length'])) for k in
                         table_data.keys() if table_data[k]['length'] != '')
        length_max = length_max if length_max >= 6 else 6
        for k, v in table_data.items():
            if v['length'] != '':
                table_data[k]['length'] = '{l:{ml}.1f}'.format(
                    l=v['length'], ml=length_max)

        # Calculating the max column widths
        column_width = {}
        for h in ls_headers:
            list_values = [v[h] for k, v in table_data.items()]
            column_width[h] = max(len(i) for i in [headers[h]] + list_values)

        # Creating the table
        header_row = ['{h:{m}}'.format(h=headers[h], m=column_width[h])
                      for h in ls_headers]
        table = ['  |  '.join(header_row),
                 '--+--'.join(column_width[h] * '-' for h in ls_headers)]

        for section in ['start', 'ec1', 'static', 'ec2']:
            try:
                row = table_data[section]
            except KeyError:
                continue

            row_data = ['{h:{m}}'.format(h=row[h], m=column_width[h])
                        for h in ls_headers]
            table += ['  |  '.join(row_data)]

        return ' ' + '\n '.join(table)
