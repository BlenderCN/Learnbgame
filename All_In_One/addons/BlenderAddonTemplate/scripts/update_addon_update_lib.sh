#!/bin/bash
ZIP=https://github.com/CGCookie/blender-addon-updater/archive/master.zip
TARGET_ZIP=updater.zip
TARGET_DIR=../libs/addon_updater

read -n1 -p "WARNING: This operation may overwrite the configuration in $TARGET_DIR/addon_updater_ops.py. Please press Y to continue" isContinuing 
if [ "$isContinuing" = "Y" ]; then
  rm *.zip blender-addon-updater-master -f
  echo "Downloading latest code from github repo.."
  wget $ZIP -O $TARGET_ZIP
  unzip $TARGET_ZIP
  rm $TARGET_ZIP -Rf
  rm $TARGET_DIR -Rf
  mv blender-addon-updater-master/ $TARGET_DIR -f
  echo "Done. The latest code is now in $TARGET_DIR"
fi
