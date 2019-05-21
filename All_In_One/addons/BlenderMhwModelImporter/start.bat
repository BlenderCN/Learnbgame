@echo off

echo "Version: {VERSION}"

set BLENDER_PATHS="c:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe" "d:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe" "c:\Program Files\Blender Foundation\Blender\blender.exe" "d:\Program Files\Blender Foundation\Blender\blender.exe"
set BLENDER_EXE=""
set BMHWI_FOLDER="%CD%\..\BlenderMhwModelImporter"
if not exist %BMHWI_FOLDER% (
	echo wrong folder name, please rename this folder to: BlenderMhwModelImporter
	pause
	exit
)

(for %%B in (%BLENDER_PATHS%) do (
	echo checking for %%B
	if exist %%B (
		set BLENDER_EXE=%%B
		echo %BLENDER_PATH% found
	)
))

if not exist %BLENDER_EXE% (
	echo "Blender not found inside default path!Please modify path inside start.bat!"
	pause
	exit
)
echo current folder: %CD%
echo path to blender.exe: %BLENDER_EXE%
%BLENDER_EXE% -P "%CD%\start.py"
pause