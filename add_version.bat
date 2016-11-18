@echo off

REM Set encoding to UTF-8
set ENCODING=850
chcp 65001

set VERPATCH=C:\Utilities\verpatch\verpatch

set FILEDESCR=/s desc "Tool for calculating easement curves in TS"
set FILEVER="0.7.5.0"
set INTERNAL=/s title "ec"
set COPYRIGHT=/s company "macph" /s copyright "© 2016 Ewan Macpherson"
set ORIGINAL=/s OriginalFilename "ECCalc.exe"
set PRODINFO=/s product "Easement curve calculator" /pv "0.7.5.0 beta4"

@echo "Adding version file...
%VERPATCH% /va dist\ECCalc.exe %FILEVER% %FILEDESCR% %INTERNAL% %COPYRIGHT% %ORIGINAL% %PRODINFO%

REM Reset encoding back to 850
chcp %ENCODING%
