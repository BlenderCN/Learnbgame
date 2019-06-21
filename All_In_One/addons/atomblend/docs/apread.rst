======
apread
======
AP data loader package.

apload
------
apload.py contains the APData wrapper class for interacting with the 
range/pos-loading classes defined in rngload/posload. APData handles
initialising the range loading class to operate a specific pos object.

AtomBlend accesses all AP data through the APData class.

In the future APData will handle loading multiple filetypes with the correct 
classes in rngload/posload.py.

.. autoclass:: atomblend.apread.apload.APData
   :members:

posload
-------
The posload module contains all classes responsible for loading pos filetypes.
New classes can be created to handle loading different pos file formats.


Interface
^^^^^^^^^
All pos loading classes must implement posload.POSInterface.

.. autoclass:: apread.posload.POSInterface
   :members:

Available pos loaders
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: apread.posload.POS
   :members: xyz, mc, _parsefile, __len__

rngload
-------
The rngload module containes all classes responsible for loading mass-to-charge
range files. New classes can be created to handle loading different range file
formats. 

Interface
^^^^^^^^^
There is no definite interface yet, but it will be similar to the RNG loader 
below!

Available range loaders
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: apread.rngload.ORNLRNG
   :members: rangelist, atomlist, ionlist, _ranges, _atoms, _ions, _parsefile, _genranges, _genions, _genatoms, _pos, _posmap, loadpos, _genposmap, getrange, getion, getatom
