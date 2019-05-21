# m3addon - Blender Import-Export for `.m3` file format.

Project is still being maintained and bug reports will be taken care of. At least to the extent of my knowledge on the subject. Aswell as amount of freetime available.

Bug tracker: https://github.com/Talv/m3addon/issues

Support can be provided also through SC2Mapster Discord Server: https://discord.gg/fpY4exB

---

> Original author: Florian Köberle \
> https://github.com/flo/m3addon

## Features

The Python scripts can be used as a Blender addon.

Currently the following content can be exported and imported:

* Animations
* Meshes with up to 4 UV layers
* The following known M3 materials:
  * standard materials
  * displacement materials
  * composite materials
  * terrain materials
  * volume materials
  * creep materials
  * volume noise materials
  * splat terran bake materials
* M3 particle systems
* M3 forces
* M3 attachment points and volumes
* M3 cameras
* M3 lights
* M3 rigid bodies
* M3 projections
* M3 ribbons
* M3 billbord behaviors

The script m3ToXml.py can also be used to convert a m3 file into a XML file. It
takes a m3 file as argument and prints the XML on the command line.

The script xmlToM3.py can convert the XML files exported by m3ToXml.py
back into a m3 file.

The file structures.xml gets used by the m3.py library to parse the m3 files.
Modifying this XML file will have impact of the above scripts and the blender addon.

## Installation

1. Download most recent version: https://github.com/Talv/m3addon/archive/master.zip and extract the archive to directory named `m3addon`.
2. Move the directory into addons folder of your blender settings:
   * Example for Linux and Blender 2.69:
     * /home/$user/.blender/2.69/scripts/addons/m3addon
   * Example for Windows XP and Blender 2.69:
     * C:\Documents and Settings\%username%\Application Data\Blender Foundation\Blender\2.69\scripts\addons
   * Example for Windows 7 and Blender 2.69:
     * C:\Users\%username%\AppData\Roaming\Blender Foundation\Blender\2.69\scripts\addons
3. Activate the addon in blender (There is another M3 addon, so watch out!)

## Usage

The blender addon adds panels to the scene tab of the properties editor.

To create a particle system and preview it in the Starcraft 2 editor you can perform the following steps:

1. Add a animation sequence by clicking on "+" in the "M3 Animation Sequences" panel
2. Add a material by clicking on "+" in the "M3 Materials" panel
3. Select a diffuse image:
   3.1 Select "Diffuse" in the "M3 Materials Layer" panel
   3.2 Specify a image path like "Assets/Textures/Glow_Blue2.dds" in the "M3 Materials Layer" panel
4. Add a particle system by clicking on "+" in the "M3 Particle Systems" panel
5. Validate that your particle system has a valid material selected
6. Specifiy an absolute file path in the "M3 Quick Export" panel
7. Click on "Export As M3" in the "M3 Quick Export" panels
8. Open the previewer in the Starcraft 2 editor by using the menu "Window/Previewer"
9. Use the previewer menu "File/Add File" to preview the exported model in the SC2 Editor

## Some Blender Tipps:

* You can right click on UI elements to view the source code which displays that element.
* File/Save User Settings can be used to determine the default state of blender.
  * You can save your export path this way!
  * You can make yourself a default view which shows SC2 properties panels where you want them

## About the Implementation

* The m3.py file is a python library for reading and writing m3 files. It uses the structures.xml file to do so.
* The file structures.xml specifies how the script should parse and export a M3 file
* The importing of m3 files works like this:
  1. The method loadModel of the m3.py file gets called to create a python data structure of the m3 file content.
  2. This data structure gets then used to create corresponding blender data structures
* The exporing works the other way round:
  1. The data structures of blender gets used to create m3.py data structures that represent a m3 file.
  2. The method saveAndInvalidateModel of the m3.py file gets used to convert the latter data structure into a m3 file.

### About the m3 file format and the structure.xml file

The m3 file format is basically a list of sections. Each section contains an array of a certain structure in a certaion version.

The first section of an m3 file contains always a single structure of type MD34 in version 11. It is defined at the bottom of the structure.xml file:

```
    <structure name="MD34" version="11" size="24">
        <description>Header of a M3 file: Can be found at the start of the file.</description>
        <versions>
            <version number="11" size="24" />
        </versions>
        <fields>
            <field name="tag" type="tag" />
            <field name="indexOffset" type="uint32"/>
            <field name="indexSize" type="uint32" />
            <field name="model" type="Reference" refTo="MODL" />
        </fields>
    </structure>
```

Structures may reference other sections via a data structure called Reference (or SmallReference in some exceptions).

The MD34 structure for example has a field called model, that is referencing a `MODL` structure within another section. To which structure type a reference is pointing is indicated by the refTo field.

References typically do not however reference a single structure, but the whole section and thus an array of structures. Thus theoretically a MD34 structure could reference multiple `MODL` structures but that has never been observed in a valid m3 file.

The m3.py file requries all structures to be first defined in the structure.xml file before they get used/referenced by another structure. For this reason the structure MD34 is defiend at the bottom.

An m3 file contains also an index/overviewabout those sections it cotnains, which can be found at the location specified by indexOffset and indexSize. If you want to get a list of the sections in an m3 file programmatic wise you can use the m3.py method `loadSections(filename)`.

However usually however it is easier to just work with a tree like represenation of the `MODL` structure in which all references to structure arrays have been replaced by a a list of the section that got referenced. This is possible via the m3.py python function `loadModel(filename)`.

### Definition of structure elements in the structure.xml file

A structure definition defines a strcture for all versions that exist of it:

For the creep materail for example (structure name CREP) 2 versions exist that have differnt sizes. In the structure.xml file there is however just a single structure definition:

```
    <structure name="CREP">
        <description>Creep Material</description>
        <versions>
            <version number="0" size="24" />
            <version number="1" size="28" />
        </versions>
        <fields>
            <field name="name" type="Reference" refTo="CHAR" />
            <field name="creepLayer" type="Reference" refTo="LAYR" />
            <field name="unknownda1b4eb3" size="4" expected-value="0x00000000" since-version="1" />
        </fields>
    </structure>
```

The `<versions>` block contains a `<verson>` element for all known versions of that structure. For each structure the
size needs to be known and defined in the `<version>` element. When a m3 file contains a version of a strcuture that is not yet known, an exception will be thrown and information about the structure will be logged that contains also a guess on the size of the structure.

A newer version of a structure might have additional fields. The attribute `since-version` can be used to indicate that a field exists since a certain version. The attribute `till-version` can be used to indicate that a field exists only till a certain version of the structure.

The m3.py file checkes that the defined fields have indeed the sizes specified in the `<version>` elements. So when you add a new version you propably also need to find out what new fields got added and which fields stayed the same.

A field needs either to have a size or type attribute. The type attribute can be one of the following primitive types:

* uint32: a 32 bit unsigned integer
* int32: a 32 bit signed integer
* int16: a 16 bit signed integer
* uint8: a 8 bit unsigned integer
* uint8: a 8 bit signed integer
* float: a classical floating point type that fits in 32 bit
* tag: Up to 4 character that are used to store structure names
* fixed8: a fixed point value that gets stored in 8 bits

In addition to that all structures that got defined above the structure in the structure.xml file can be also be used as type. However a Version suffix with V + version number needs to be added to the structure name. e.g. VEC3V0 to get version 0 of the structure VEC3.

### Common Errors and how to fix them

* Error message "Exception: XYZ_V4.unknown0 has value 42 instead of the expected value int(0)":
  * In the structure.xml file it's configured what structures exists, what fields those structures have,
    and what their default or expected value is. The exceptions means, that the field "unknown0" of the structure "XYZ*" has
    been configured in the structure.xml file to be 0, but it was actually 42. For each structure exists an XML
    element in the structure.xml file. Just search for the structure name ("XYZ*" in the example) to find it. In the structure
    xml element there are field elements. To fix the given error message we would search in the structure element for the field with the name attribute "unknown0"
    and would replace the attribute expected-value="0" with default-value="0".
* Error message "Exception: There were 1 unknown sections":
  * The error message means that the m3 file contained a structure that it is unknown to the script since it has not been defined in the structure.xml file.
    You can fix the error message by defining the unknown section. To do that have a look at the log, it will contain a message like this:
    * "ERROR: Unknown section at offset 436124 with tag=XYZ* version=1 repetitions=2 sectionLengthInBytes=32 guessedUnusedSectionBytes=4 guessedBytesPerEntry=14.0"
      The error message means that it found a section in the m3 file that contains two (repetitions=2) entries of type XYZ*.
      The script guesses that 4 bytes are unused and knowns that the section is 32 bytes long. So it calculates 2\*X-4=32 where X is the number of guessed bytes per entry.
      The result of this calculation is printed at the end "guessedBytesPerEntry=14.0". So the script guesses that version 1 of the structure XYZ* is 14 bytes long.
      To fix this error you would have to define the structure XYZ* in version 1 in the structure.xml file. See the section about the structure.xml file to learn about how to do that.
* Error message "Field ABCDV7.xyz can be marked as a reference pointing to XYZ_V1":
  * To fix this example error message, we would search in the structure.xml file for a structure called "ABCD" with the attribute version="7".
    It will contain a xml element field with the attribute name="xyz". To this field we would add an attribute refTo="XYZ_V1".
* Error message "Exception: Unable to load all data: There were 1 unreferenced sections. View log for details"
  * When this error occurs, you will find in the log a message like this: "WARNING: XYZ*V1 (2 repetitions) got 0 times referenced"
    Every section in a m3 file gets usually referenced exactly 1 time(except for the header). The error message means
    that there is a section that contains 2 structures of type XYZ* in version 1, but which got not referenced from anywhere.
    Most likely there is actually a reference to this section but which hasn't been configured as such in the structure.xml file.
    If you are lucky, then there will be exactly 1 line below the former warning which looks like this:
    "-> Found a reference at offset 56 in a section of type ABCDV7". To fix the error message we need to change the structure
    definition of ABCD in version 7 to contain a field definition like this:
    `<field name="xyzData" type="Reference" refTo="XYZ_V1" />`

## License (GPL 2.0 or later)

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software Foundation,
Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
