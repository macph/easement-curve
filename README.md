# Easement curve calculator

This is a tool with one purpose: to calculate the geometry of easement curves in Train Simulator 2016 necessary to join up tracks.

## Installation

Everything is packaged in a single .exe file - go to releases here and download the latest release. There is no need for installation.

Alternatively, you can run the source code directly with Python. In the folder where you have downloaded the zip file, type in
```
python easement-curve-0.1
```
where `easement-curve-0.1` is the name of the .zip file you have downloaded.

### Compiling from source

To create the executable for yourself, you need a Python 3.5 distribution, which you can download from here, and `PyInstaller`, a Python module. Once you have Python 3.5 installed, run
```
pip install pyinstaller
```
`pip` is the Python package manager. It will install `PyInstaller` and other required modules.

Navigate to the folder where you downloaded the source and type in
```
pyinstaller -Fw easement-curve-0.1
```
where `easement-curve-0.1` is the name of the .zip file you have downloaded.