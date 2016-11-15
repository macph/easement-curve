@echo off

REM Batch script to automate building executables with 32-bit Conda Python.
REM Environment name is 'ec32'.
REM     -f: Build one file executable.
REM     -d: Build executable with directory.

set conda_env=ec32

IF "%~1" == "" (
    @echo No arguments inputted.
    exit /b
)

IF "%~1" == "-f" goto bf
IF "%~1" == "-d" goto bd

REM All other arguments
@echo Wrong arguments inputted.

:bf
    set CONDA_FORCE_32BIT=1
    call activate %conda_env%
    pyinstaller build_f.spec
    goto finish

:bd
    set CONDA_FORCE_32BIT=1
    call activate %conda_env%
    pyinstaller build_d.spec
    goto finish

:finish
    call deactivate
    set CONDA_FORCE_32BIT=
    exit /b