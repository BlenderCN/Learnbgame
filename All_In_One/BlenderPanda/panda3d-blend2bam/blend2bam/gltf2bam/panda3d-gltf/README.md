[![Build Status](https://travis-ci.org/Moguri/panda3d-gltf.svg?branch=master)](https://travis-ci.org/Moguri/panda3d-gltf)

# panda3d-gltf
This project is a glTF to BAM converter based on code from [BlenderPanda](https://github.com/Moguri/BlenderPanda)

## Goals
* Full glTF 2.0 support
* Extension support:
  * BLENDER_gltf
  * KHR_lights/KHR_lights_punctual
* Continue to support the needs of BlenderPanda
* Blaze the trail for a native glTF loader

## Roadmap
* Improve glTF support using [Khronos sample models](https://github.com/KhronosGroup/glTF-Sample-Models/tree/master/2.0)
* Switch BlenderPanda over to using this project as a submodule
* Add binary glTF support
* Use this project as a guide for writting a native glTF loader for Panda3D
* Put this project into maintenance mode for projects that want glTF support on older versions of Panda3D

## Installation
```pip install git+https://github.com/Moguri/panda3d-gltf.git```

## Usage
```gltf2bam source.gltf output.bam```

## Running tests
```python setup.py test```
