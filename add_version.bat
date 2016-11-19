@echo off

@echo "Setting encoding to UTF-8..."
REM If using this script - be aware your PC's cmd may use a different encoding.
REM Run 'chcp' to find out, and set ENCODING.
set ENCODING=850
chcp 65001

set VERPATCH=C:\Utilities\verpatch\verpatch

set FILEDESCR=/s desc "Tool for calculating easement curves in TS"
set FILEVER="0.7.6.0"
set INTERNAL=/s title "ec"
set COPYRIGHT=/s company "macph" /s copyright "© 2016 Ewan Macpherson"
set ORIGINAL=/s OriginalFilename "ECCalc.exe"
set PRODINFO=/s product "Easement curve calculator" /pv "0.7.6.0 beta5"

@echo "Adding version file...
%VERPATCH% /va dist\ECCalc.exe %FILEVER% %FILEDESCR% %INTERNAL% %COPYRIGHT% %ORIGINAL% %PRODINFO%

@echo "Resetting encoding..."
chcp %ENCODING%
