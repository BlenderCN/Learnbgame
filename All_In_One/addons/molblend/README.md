# MolBlend

This addon for Blender (>=2.79) makes it possible to import molecular 
structures of (almost) any kind as well as isosurfaces from Gaussian cube 
files.
Visualization styles can be adjusted dynamically and are highly customizable.
In addition MolBlend adds operators to add and change atoms and bonds of 
imported structures, or even draw everything from scratch.

**WARNING** This addon is still under heavy development. Future updates and 
bug fixes are not guaranteed to be backwards compatible.
Starting with the version from 2018-04-16 the addon appends the current git 
commit ID to scene.mb.info.git_commits when the file is saved.
If you need to work on a file that has been created with an older revision, 
you can look up the last commit id by entering 
`C.scene.mb.info.git_commits[-1]` in the Python console.

If you downloaded the
addon with git, navigate to the MolBlend folder in a terminal and run 
`git branch` and note the branch name with the star in front of it (probably
`master`). Then run `git checkout <commit id>` with the commit ID you saw in
the Blender Python console. When you are done, go back to the most recent 
version with `git checkout <branch with star>` with the branch name from
earlier (without the star). Note that you have to restart Blender after
running the `git checkout` commands for the different versions to take effect.

Alternatively, go to https://github.com/floaltvater/molblend, click on 
"XX commits", find the commit you need (by comparing the first 7 letters)
and click on "<>" next to the commit ID. Then download as zip file and install
as addon. Make sure Blender sees the correct version that you need (and restart
if necessary).

## Import
### File formats

The currently supported file formats are PDB, XYZ, POSCAR (VASP), Abinit
output, Quantum ESPRESSO input and output files, and Gaussian cube files.

In addition, once a structure has been imported, you can import a file
containing vibrations or phonon modes. Currently Quantum ESPRESSO, Abinit
(anaddb), phonopy and a custom "XYZ" format are supported.

MolBlend can also read the volume data in cube files to create isosurfaces.
However, to use this feature, you have to install pymcubes 
(https://github.com/pmneila/PyMCubes)
and change the path to its library in `mb_import_export.py`. Make sure that 
the python version for which you install pymcubes is the same as the one
Blender uses (for Blender 2.79 it is python 3.5). (See below for more
instructions.)

I decided to implement all file imports by myself to avoid having to install
any external dependencies.
If you would like to see a file format implemented, please don't hesitate to
ask!

### Animation

For files that support several frames (e.g., PDB, XYZ, output from relaxation
calculations), the script imports all steps and animates the atom coordinates
1 step/frame.
This is obviously meant for analysis, not to make a pretty movie. For a movie
with a more realistic frame rate, you could adjust the time remapping value in
the Render properties panel.

After importing a vibration/mode file, you can select each individual mode to
be animated. Complex valued phonon modes and off-center q-points are also 
supported.

## Drawing

The script contains a simple modal operator, that lets you draw atoms with
left-clicks. Click-and-drag when hovering over another atom will create a bond
between that atom and the new atom. 
Simple geometry constraints allow for nicer structure drawing. There is a 
drop-down menu for angle constraints, and holding Ctrl while drawing a bonded
atom enforces a length constraint according to the covalent radii.

## Representations

Representations of elements can be changed independently for each molecule. 
So one could have small green carbon atoms in one molecule, and large red 
carbon atoms in another.

You can switch between Ball-and-Stick, Stick, or Ball drawing, with
bonds colored generically or according to the bonded elements. Atom radii are
relative to the (adjustable) covalent or van der Waals radii, or just a 
constant value.

Molecules are not necessarily bonded. All atoms imported from a single file
initially belong to a single atom, no matter if they are all connected or not.
One can split a group of atoms into separate molecules manually, again whether
they are connected or not.

## Export

Exporting the structures to different file formats is planned for the future.
Please let me know if you have any preferences.

## Installing pymcubes

Blender comes with its own bundled Python and numpy. For 2.79 this is 
Python 3.5. and numpy 1.11. In order to use the isosurface import, you will
need to install the pymcubes module for these versions. Luckily this is 
possible through pip (a python package manager). Since the version 
requirements are rather strict, I recommend installation in a separate 
environment. Below I have instructions using anaconda (inspired by 
https://blender.stackexchange.com/a/76124) 
or virtualenv and Blender's python executable (thanks, Felipe!).

If you have another way to install it, or suggestions on how to improve
these instructions, please let me know!

**Disclaimer:** These are not fail-safe instructions and I take no 
responsibility if you mess up your system by following them.

### Using anaconda

First let's create the environment.
```bash
conda create --name conda-python3.5-blender python=3.5.3
```
You can use any other name besides `conda-python3.5-blender`. 
Then activate the environment to install the packages
```bash
source activate conda-python3.5-blender
```
When installing we turn the cache off so pip doesn't just use other
versions it installed previously.
```
pip install Cython
pip install numpy==1.11.2 --no-cache-dir
pip install pymcubes --no-cache-dir
```
Finally, we need to get the directory to the pymcubes module.
```
pip show pymcubes | grep Location | cut -d":" -f2
```
Now open `mb_import_export.py` with the editor of your choice and change the
`mcubes_path` variable at the very top to match the directory that was printed
out in the last step.

You can check whether or not Blender finds pymcubes by activating this addon
and typing `import mcubes` in the Blender Python console.

### Using virtualenv and Blender's python executable

(Courtesy of Felipe Jornada. This apparently worked on OSX 10.11.6 (Capitain),
where installation with the macports python installation didn't work. 

1) Use get-pip.py to install pip using the python3.5 binary shipped with 
   Blender.

2) Use this custom pip to install virtualenv, and create a new virtual 
   environment.

3) Install Cython, pymcubes + dependencies. Since Blender does not ship with
   Python3 headers, I had to use the following command to install pymcubes:
```
CC=clang CXX=clang++ CPATH="/opt/local/Library/Frameworks/Python.framework/Versions/3.5/include/python3.5m" python venv/bin/pip install pymcubes
```

4) Adjust the path to pymcubes in your molblend script.

## Known issues

- When the generic bond color is updated, the viewport color is not updated
  immediately despite drivers. Starting blender with the command line option
  `--enable-new-depsgraph` fixes this. (See [1] for a nice explanation)
  This will be the default in 2.8.
- If parts of Molecules are deleted by hand that shouldn't be (like the
  Molecule parent, parts of the unit cell, etc. things can break. I am working
  on an operator that tries to fix molecules again if that happens on accident.
- Since every atom and every bond is its own object, large structures soon
  slow down the usage of Blender. Usability depends on the machine you are on.
  To work with huge structures (like big proteins), look into Bioblender 
  (bioblender.org), or other addons that use Dupliverts etc.
- Guessing the bonds is not very efficient or stable, since it compares every
  atom pair to the sum of their covalent radii plus some tolerance.
- Unit handling is not very elegant. Currently the addon works exclusively in
  Angstrom (like guessing bonds), and converts, or tries to convert, imported
  files to that unit.
- Imported isosurfaces often have very uneven meshes, which show up as kinks
  when rendered. This is a drawback of the marching cubes algorithm used. I
  couldn't find a better algorithm that is readily available as a (relatively
  easy to install) python package. As a workaround, the script adds two 
  modifiers to each isosurface that are both disabled by default. Simply go to
  the modifiers panel and activate them (toggling the render and eye symbol on)
  if you want nicer looking isosurfaces. Be warned, however, that the result is
  not guaranteed to be sscientifically accurate. (Luckily, modifiers are non-
  destructive...)
- Currently MolBlend doesn't support double/triple bonds, or other even less
  common bonds.
- Duplication (Shift+D, Alt+D) and combining of molecules doesn't update the
  materials accordingly. I.e., when duplicating, the materials of original and
  new molecule are linked, and when combining, the materials will not be
  linked.
- Indeces that are explicitly given in files (like PDB format) are not
  preserved currently. This will probably change when export operators get 
  implemented.
- Logging is somewhat sparse and not functional for debugging.

[1] https://blender.stackexchange.com/questions/75917/why-are-my-drivers-not-updating-instantly
