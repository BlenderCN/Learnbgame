************
Introduction
************

Introduction to OpenCV
======================

OpenCV (Open Source Computer Vision Library http://opencv.org) is an open library containing several hundred algorithms
of computer vision based on BSD. OpenCV library is divided into modules and this division is also
reflected in OpenCV Laboratory.

- `core` - a compact module defining basic data structures and containing basic functions used in the rest of the modules
- `imgproc` -  image processing module includes functions: linear and non-linear filtering, transformation, changes
     size, color hue changes, operations on histograms, etc.
- `video` -  module for video analysis includes, among others, functions: traffic estimation, background removal and object tracking
- `calib3d` - basic algorithms for calculating the geometry of multiple images, single calibration and double camera,
     image position estimation, stero correspondence algorithm and 3D reconstruction functions
- `features2d` - essential feature detectors, descriptors and matching descriptors
- `objdetect` - detection of objects and instances of predefined classes (eg face, eyes, mugs, people, cars, etc.)
- ...

Introduction to Blender
=======================
Blender is a free and open source 3D creation package. It supports entire modeling of 3D pipelines, rigging,
animation, simulation, rendering, composing, movement tracking, and even editing video and creating games. Advanced
Users use the Blender API to support scripting in Python to customize applications and
writing specialist tools; they are often included in future releases of Blender. Blender is fine
suited to individuals and small studies that benefit from a unified system and a flexible development process. Examples
of many projects based on Blender are available in the form of presentations.

For the needs of OpenCV Laboratory, the Blender node system is used, which is the basis of the application.

Introduction to OpenCV Laboratory
=================================
The laboratory is a series of preinstalled Python libraries and a set of Blender extensions. On this base
A set of OpneCV functions has been implemented in the form of convenient to connect nodes, in which we have fast and convenient
access to all parameters of the function and, in addition, an immediate preview of the result of these functions. Laboratory
in addition to the primary node equivalents of the OpenCV library has also very important input / output nodes. To this pool of
nodes include: Image Sampler, Image Viewer, ROI, Custom Input, Custom I / O, Stethoscope, TypeConvert.



Node
----
OpenCV Laboratory is a series of preinstalled Python libraries and the Blender extension kit. On this basis, a set of OpneCV functions has been implemented in the form of convenient to connect nodes in which we have fast and convenient access to all parameters of the function, and also an immediate preview of the result of these functions.

Visually, each node in the OpenCV Laboratory is represented by a rectangle with rounded corners.
Each of them has round sockets, an input socket on the left and output sockets on the opposite side.

Below is an example with a short description of different nodes.

.. image:: http://kube.pl/wp-content/uploads/2018/05/nodes_1-e1525848678402.png

1. Node name.
2. Input sockets.
3. Output socket.
4. Input parameters to which the appropriate input sockets are assigned. It is often possible to freely adjust individual arguments using sliders or by entering a specific value.
5. The output parameter is the result of operations performed by a given node.
6. Internal parameter which is a list of choice of a specific function.
7. Internal parameter in the form of buttons defining the function selection.
8. Internal parameter in the form of an acceptance field that takes into account the operation of the function.
9. Button for minimizing the node view.

Connecting nodes
----------------
Connecting nodes is nothing else but a command to perform appropriate functions by a computer program with the final result of their actions. Mutual connection of individual nodes is a relatively simple operation consisting in connecting with a line, the output socket of one of the nodes with the corresponding input socket of another node.

.. image:: http://kube.pl/wp-content/uploads/2018/05/connect-e1525853523746.png

The above operation is carried out as follows:
     1. Click with the left mouse button the output socket of the given node.
     2. Without releasing the button, route the lines to the input socket of another node.
     3. Release the mouse button.

In the presented example, no complicated operations were performed, resulting in an output image identical to the entered input image.

It's simple, right?

Invalid node data entry
-----------------------
Due to the properties and functions performed, not all nodes can be directly connected with each other. Each node requires a specific parameter for the appropriate input, some of them need to enter all relevant data. In OpenCV Laboratory, irregularities in the above cases are illustrated by a change in node color.

.. image:: http://kube.pl/wp-content/uploads/2018/05/wrong_connect-e1525862157976.png

In problematic cases, to achieve the right final result, it is often enough to fine-tune the node settings, supplement with the required data or, depending on the need, apply the compilation of other nodes.


Image Sampler
-------------
A node which task is to generate / load an image for further processing

Image Viewer
------------
This node is used to view the image. It has two built-in modes. The default thumbnail mode where the image is displayed
in the node itself, and preview mode, where we have access to all the details of the image in full screen, along with the possibility
zooming or previewing a pixel by pixel.

ROI
---
With this node, we can conveniently cut the image and select the fragment we are interested in.

Custom Input
------------
This node can generate / download data from any source based on the Python code.

Custom I/O
----------
This node can accept any data from other nodes and process them from the Python code level.

Stethoscope
-----------
It is a node taken from the Sverchok library. Used to view data in numerical form.

TypeConvert
-----------
With this node, we can quickly change the data type (uint8, float32, float64, etc.) from which the image is composed.

