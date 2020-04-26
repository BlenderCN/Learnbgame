cd /d %~dp0

rd /s /q _build

mkdir _build
cd _build

REM cmake .. -G "Visual Studio 15 2017 Win64" -DHFS="C:/Program Files/Side Effects Software/Houdini 17.0.416"
REM cmake --build . --config release
REM del CMakeCache.txt

REM cmake .. -G "Visual Studio 15 2017 Win64" -DHFS="C:/Program Files/Side Effects Software/Houdini 17.0.352"
REM cmake --build . --config release
REM del CMakeCache.txt

REM cmake .. -G "Visual Studio 15 2017 Win64" -DHFS="C:/Program Files/Side Effects Software/Houdini 16.5.634"
REM cmake --build . --config release
REM del CMakeCache.txt

REM cmake .. -G "Visual Studio 15 2017 Win64" -DHFS="C:/Program Files/Side Effects Software/Houdini 17.5.173"
REM cmake --build . --config release
REM del CMakeCache.txt

cmake .. -G "Visual Studio 15 2017 Win64" -DHFS="C:/Program Files/Side Effects Software/Houdini 17.5.258"
cmake --build . --config release
del CMakeCache.txt

cd ..
rd /s /q _build
