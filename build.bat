@echo off

REM Batch script to automate building executables with 32-bit Conda Python.
REM Environment name is 'ec32'.
REM     -f: Build one file executable.
REM     -d: Build executable with directory.
REM     -a: Do both.

set conda_env=ec32

IF "%~1" == "" (
    @echo No arguments inputted.
    exit /b
)

IF "%~1" == "-f" goto bf
IF "%~1" == "-d" goto bd
IF "%~1" == "-a" goto ba

REM All other arguments
@echo Wrong arguments inputted.

:bf
    set CONDA_FORCE_32BIT=1
    call activate %conda_env%
    @echo Creating onefile executable...
    pyinstaller build_f.spec
    goto finish

:bd
    set CONDA_FORCE_32BIT=1
    call activate %conda_env%
    @echo Creating directory bundle...
    pyinstaller build_d.spec
    goto finish

:ba
    set CONDA_FORCE_32BIT=1
    call activate %conda_env%
    @echo Creating directory bundle...
    pyinstaller build_d.spec
    @echo Creating onefile executable...
    pyinstaller build_f.spec
    goto finish

:finish
    @echo All done!
    call deactivate
    set CONDA_FORCE_32BIT=
    exit /b