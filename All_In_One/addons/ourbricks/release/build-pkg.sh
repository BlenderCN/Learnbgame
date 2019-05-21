#!/bin/bash

WORK_DIR_PARENT=/tmp
WORK_DIR_NAME=ourbricks_blender
WORK_DIR=$WORK_DIR_PARENT/$WORK_DIR_NAME
ZIP_NAME=ourbricks-blender.zip
DIR=`pwd`

# Clean out any previous files from package building
rm -rf $WORK_DIR

# Clone base repository
git clone git://github.com/ourbricks/ourbricks-blender.git $WORK_DIR

# Grab dependencies
cd $WORK_DIR
git submodule update --init --recursive
cd $DIR

# Clean out
find $WORK_DIR -name .git | xargs rm -rf

# Create zip file. We need to be in the right location to get relative
# paths right.
cd $WORK_DIR_PARENT
zip -r $ZIP_NAME $WORK_DIR_NAME
cd $DIR

# Move into current directory where we want it to land
mv $WORK_DIR_PARENT/$ZIP_NAME $DIR
