# Easement curve calculator

This is a application for calculating the geometry of easement curves in Train Simulator 2016 necessary to join up tracks.

## Background

Easement curves are used to join railway tracks of different curvature, like for example a straight track (with zero curvature) and a track arc with a constant radius of curvature. They are necessary for gradual transistions in centrifugal force which act on trains as they move around curves - if there was no easement curve there would be a jerky moment as the centrifugal force is instantly applied upon entering an track arc.

Train Simulator (TS2016) has a route editor and supports creation of easement curves, but it does not have any ability to join up tracks with easement curves automatically. Route building with easement curves can be time consuming especially as easement curves change in length with radius of curvature, leading to a lot of trial and error work. This application aims to make that easier by taking in coordinates of tracks and outputting the coordinates of easement curves that fit these tracks.

## Installation

Everything is packaged in a single `.exe` file - go to releases [here](../../releases) and download the latest release. There is no need for installation.

### Compiling from source

If you want to create the executable for yourself, you need a Python 3.5 distribution which you can download from the [Python website](https://www.python.org/downloads/), and `PyInstaller`, a Python module. Once you have Python 3.5 installed, install PyInstaller by typing in the command prompt
```
pip install pyinstaller
```
`pip` is the Python package manager. It will install `PyInstaller` and other required modules.

Unzip the source code into a folder. Navigate to that folder in command prompt and type in
```
pyinstaller build_f.spec
```
The `.spec` file is an configuration file used by `PyInstaller` and included with the release. The executable will be created in the `\dist` folder.

## Usage

For more details about how to get track coordinates and implementing them, see the [guide](docs/guide.md) and the [reference](docs/reference.md). If you are interested in the mathematics behind the easement curves in this tool, take a look at the [summary PDF](docs/ec_summary.pdf).
