@echo off

REM Batch script to automate building executables with 32-bit Conda Python.
REM Environment name is 'ec32'.

set ENV=ec32
set BUILD=build_f.spec
set ENCODING=850
set VERPATCH=C:\Utilities\verpatch\verpatch

IF "%~1" == "" (
    goto build
    exit /b
)

IF "%~1" == "--add" (
    IF "%~2" == "" goto err
    IF "%~3" == "" goto err
    goto build
    goto add
    exit /b
)

:err
    @echo Need 2nd and 3rd arguments for file and product versions respectively.
    exit /b

:build
    set CONDA_FORCE_32BIT=1
    call activate %ENV%
    @echo Creating onefile executable...
    pyinstaller %BUILD%

    call deactivate
    set CONDA_FORCE_32BIT=

:add
    @echo Setting encoding to UTF-8...
    REM If using this script - be aware your PC's cmd may use a different encoding.
    REM Run 'chcp' to find out, and set ENCODING.
    chcp 65001

    set FILEDESCR=/s desc "Tool for calculating easement curves in TS"
    set FILEVER="%~2"
    set INTERNAL=/s title "ec"
    set COMPANY=/s company "macph"
    set COPYRIGHT=/s copyright "© 2016 Ewan Macpherson"
    set ORIGINAL=/s OriginalFilename "ECCalc.exe"
    set PRODUCT=/s product "Easement curve calculator"
    set PRODVER=/pv "%~3"

    @echo Adding version file...
    %VERPATCH% /va dist\ECCalc.exe %FILEVER% %FILEDESCR% %INTERNAL% %COMPANY% %COPYRIGHT% %ORIGINAL% %PRODUCT% %PRODVER%

    @echo Resetting encoding...
    chcp %ENCODING%
