How to add the custom models to the game

For this I will be assuming that you already know how to decompile all the .pak files as well as decompile/recompile mbin files, and also how to pack it all back up into a workable mod. If you don't know how to do some of these things make sure you find a tutorial on how to do that first.

Now that you have the model exported from blender into a format the game can read, the next step is to actually tell the game to load it somewhere.
By far the easiest way to do this is by adding the object (or objects) as a leveloneobject. Examples of these are the word stones, signal scanners and the random crates and stuff lying scattered around a planet.

To add objects to the list of leveloneobjects is as simple as editing one file (and another which seems to be essentially a copy of the first file)

The files we are editing are located at ~\PCBANKS\METADATA\SIMULATION\SOLARSYSTEM\BIOMES\OBJECTS\LEVELONEOBJECTS\ and are the only two files (FULL and FULLSAFE).
Open these files up with some kinds of text editor (I recommend notepad++ as you can change the language to xml which allows for good code highlighting etc).
Under the Property 'Objects' you will see a GcObjectSpawnData.xml Property, with a Filename containing the signal scanner scene file. Copy the entire Property (should be lines 7 through to 68 inclusive) and paste it above the one you just copied (ie. press 'enter' at the end of line 6 to create a new line on line 7 and paste the entire block on line 7).
Now what you want to do is change the Filename Property to the location of the scene that the model importer created. This location will start with CUSTOMMODEL/. Remember that this location is relative to the PCBANKS folder.

Pretty much everything else in this file can be safely ignored. There are however two lines that can be modified:
<Property name="PlacementCoverage" value="0.1" />
<Property name="PlacementFlatDensity" value="0.0001" />

These two lines dictate how regularly the object will get spawned. Higher values will mean more frequent spawns. You can compare the values that other objects in the file have to decide whether you want them to be more or less rare. While testing it is often a good idea to set the vluaes reasonably high (0.1 and 0.005 ish) just to make sure you can find your model easily to confirm that it is loading and rendering correctly in game.

You can now copy the entire GcObjectSpawnData.xml Property into the other file in this folder in the same place.

Recompile both exml files back into an mbin and create your mod as usual.