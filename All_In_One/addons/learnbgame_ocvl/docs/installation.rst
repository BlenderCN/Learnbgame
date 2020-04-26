************
Installation
************

Installation from a binary package
==================================

If the program is installed from a binary package, all dependencies are already in this package.
So if the system meets the minimum requirements, the program will be ready for use after installing the binary package.

Installation of the source package directly in Blender
======================================================

In case you want to install the program from the source code, we need to meet several prerequisites.

- Blender (https://www.blender.org/download/) - suggested version 2.49
- opencv-python (https://pypi.python.org/pypi/opencv-python) - suggested version 3.1.0.1
- pynput - (https://pypi.python.org/pypi/pynput/1.3.10) - suggested version 1.3.10
- tornado - (https://pypi.python.org/pypi/tornado/5.0.2) - suggested version 4.5.3
- sverchok addon - (https://github.com/nortikin/sverchok) - suggested version cae276520184c94b877ffc88e196469086e9f7eb


Belnder installation
--------------------
Blender can be downloaded from the program website http://blender.org/. OCVL works steadily on version 2.49 and it is recommended
installation of this version of Blender.

Installation of OpenCV, pynput, tornado
---------------------------------------

To install `python` packages, it is best to use `pip`. By default, 'Pip' is not included in Blenders
Python and you must install it first.
`Pip` can be downloaded from:` https: // bootstrap.pypa.io / get-pip.py`. Then just run the Python script.

Depending on the operating system and version of Blender, Python may have a different name and location.
Here's an example of Python's location in Blender:
`~/Downloads/blender-2.79-macOS-10.6/
blender.app/Contents/Resources/2.79/python/bin/python3.5m`
The Pip installation will look like:
`~/Downloads/blender-2.79-macOS-10.6/blender.app/Contents/Resources/2.79/python/bin/python3.5m ./get-pip.py`

Now with Pip you can install packages directly through it. Pip depending on the system can
install itself as a script or as a module.

Now you can install packages:
    ../python/bin/python3.5m ../python/bin/pip install pynput==1.3.10
    ../python/bin/python3.5m ../python/bin/pip install opencv-python==3.1.0.5
    ../python/bin/python3.5m ../python/bin/pip install tornado==4.5.3


    wget https://github.com/nortikin/sverchok/archive/cae276520184c94b877ffc88e196469086e9f7eb.zip
    cd ~/Downloads/blender-2.79-macOS-10.6/OpenCVLaboratory.app/Contents/Resources/2.79/scripts/

    unzip ./cae276520184c94b877ffc88e196469086e9f7eb.zip
    mv ./sverchok-cae276520184c94b877ffc88e196469086e9f7eb ./addons/sverchok
    ln -s ~/workspace/tales/ocvl-addon ocvl


Installation of OCVL addon to Blender
----------------------------------------
After downloading OCVL (https://github.com/feler404/ocvl-addon), just unpack it and copy it to the addons directory

Running Blender with addon
--------------------------
In order for Blender to be able to run all the add-ons correctly, it must be run by the command:
`./blender --addons ocvl,sverchok`