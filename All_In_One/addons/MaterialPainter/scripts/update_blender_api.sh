#!/bin/sh
echo "Extracting python APIs from blender and storing into lib/"
rm *.zip pycharm-blender-master -Rf
rm ../libs/blender -Rf
wget https://github.com/mutantbob/pycharm-blender/archive/master.zip
unzip master.zip
cd pycharm-blender-master
sh refresh_python_api || echo "WARNING: The refreshing blender python script terminated with some errors.."
mv python_api/pypredef/ ../../libs/blender
cd ..
rm master.zip pycharm-blender-master -Rf
echo "Script execution completed"
echo "Now add the blender python lib to pycharm as follow https://github.com/mutantbob/pycharm-blender/blob/master/pycharm-3.4-screenshot.png"
