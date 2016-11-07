# Easement curve calculator

This is a tool for calculating the geometry of easement curves in Train Simulator 2016 necessary to join up tracks.

## Background

Easement curves are used to join railway tracks of different curvature, like for example a straight track (with zero curvature) and a track arc with a constant radius of curvature. They are necessary for gradual transistions in centrifugal force which act on trains as they move around curves - if there was no easement curve there would be a jerky moment as the centrifugal force is instantly applied upon entering an track arc.

Train Simulator (TS2016) has a route editor and supports construction of easement curves, but it does not have any ability to join up tracks with easement curves automatically. Route building with easement curves can be time consuming especially as easement curves change in length with radius of curvature. This tool attempts to make that easier by taking in coordinates of tracks and outputting the coordinates of easement curves that fit these tracks.

## Installation

Everything is packaged in a single .exe file - go to releases here and download the latest release. There is no need for installation.

### Run with Python

Alternatively, you can run the source code directly with Python. You need a Python 3.5 distribution, which you can download [here](https://www.python.org/downloads/). Earlier Python 3 versions may work, but the program is not compatible with Python 2.7 or earlier versions.

In the folder where you have downloaded the zip file, type in
```
python easement-curve-0.1
```
where `easement-curve-0.1` is the name of the .zip file you have downloaded.

### Compiling from source

To create the executable for yourself, you need a [Python 3.5 distribution](https://www.python.org/downloads/) as above, and `PyInstaller`, a Python module. Once you have Python 3.5 installed, install PyInstaller by typing in the command prompt
```
pip install pyinstaller
```
`pip` is the Python package manager. It will install `PyInstaller` and other required modules.

Unzip the source code into a folder. Navigate to that folder in command prompt and type in
```
pyinstaller ec_build.spec
```
The `.spec` file is an configuration file used by `PyInstaller`. The executable will be created in the `\dist` folder.

## Usage

For more details about how to get track coordinates and implementing them, see the [guide](docs/reference.md). If you are interested in the mathematics behind the easement curves in TS2016, take a look at the [summary PDF](docs/ec_summary.pdf).