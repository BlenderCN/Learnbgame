# Exporting a Blender scene into a NMS compatible format

NMSDK's primary functionality is to convert scenes created in Blender into a format that NMS can load and display in the game.
This can be anything from extra rocks or plants, to custom buildings that are scattered around on planets, new parts to be added to your base, or even new ships or freighters that can be flown or part of your fleet!

To provide this functionality a new panel has been added to the blender user interface (UI) to allow the user to enter any relevant information required to export a model to the format compatible with NMS.

## Setting up

The first thing to do is to create an empty object in Blender called `NMS_SCENE`. **All** objects to be exported **must** be a child of this object.