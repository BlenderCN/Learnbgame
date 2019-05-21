## Installing NMSDK

Put the files in the right place.

### Prerequisites

#### Blender

NMSDK requires a version of blender greater than or equal to 2.79.
This is due to the model importer component to need a shader node that only exists with Blender 2.79 and above.

NMSDK has not been tested for blender 2.80, however it is likely to not work, and support for 2.80 will not come until 2.80 is out of beta and is the latest official release.

#### MBINCompiler

For NMSDK to work, it requires [MBINCompiler](https://github.com/monkeyman192/MBINCompiler)
to generate the *.mbin* files that are read by the game.
The easiest way to have *MBINCompiler* set up is to download the most recent
release and register *MBINCompiler* to the path so that it can be picked up
anywhere by Blender.
If you already have a version of *MBINCompiler* on your computer, ensure it is
version **1.7.0.4** or above. This can be found on the [MBINCompiler releases](https://github.com/monkeyman192/MBINCompiler/releases) page.
