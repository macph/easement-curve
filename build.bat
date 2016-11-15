@echo off

REM Batch script to automate building executables.
REM     -f: Build one file executable.
REM     -d: Build executable with directory.

IF "%~1" == "" (
    @echo No arguments inputted.
    exit /b
)

set CONDA_FORCE_32BIT=1
call activate ec32

IF "%~1" == "-f" (
    pyinstaller build_f.spec
    exit /b
)
IF "%~1" == "-d" (
    pyinstaller build_d.spec
    exit /b
)

@echo Wrong arguments inputted.

call deactivate
set CONDA_FORCE_32BIT=