# spacestation #
A procedural spacestation generator

# Results #
![01](images/01.png)
![02](images/02.png)
![03](images/03.png)

# Installation #
The script is available in two versions. One is the `add_mesh_Spacestation.zip` archive, found under releases,
the other version is the actual script itself, as it contains extra functionality to add the material. To run it,
open the empty.blend file, and load and run `spacestation.py`. Alternatively, the `spacestation.hy` script also
works with [https://github.com/chr15m/blender-hylang-live-code](https://github.com/chr15m/blender-hylang-live-code).

# What it does #
The generation is done by adding a random amout of modules to a central beam.
The modules are one of:

* Torus: A torus with two cylinders connecting it to the central beam
* Beveled Box: A beveled box
* Cylinder: A beveled cylinder
* Storage Containers: 4 beveled boxes with cylinders connecting them to the central beam

# Credits #
The background image is of the _M8 Lagoon Nebula in Sagittarius_ and
was downloaded from [wikimedia commons](https://en.wikipedia.org/wiki/File:M8HunterWilson.jpg).

The texture was created by myself using a blender freestyle render
