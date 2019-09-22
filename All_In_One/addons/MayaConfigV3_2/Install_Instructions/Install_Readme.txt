Install Instructions for MayaConfig4Blender, by Form Affinity
--------------------------------------------------------------
You can view Video of these instructions at https://youtu.be/ZV6LqlaoQWs

Obtain Blender 2.80 (Not 2.79!) from the Blender Builds website:
https://builder.blender.org/download/
Grab the appropriate Bit (32 or 64) and Operating System for your computer.


Unzip the Blender build into a new folder (name it however you like, we named it "2.8Maya") onto your Desktop. It's important that the folder doesn't go into Program Files, rather, it must be saved to the Desktop. 

----------------------------------

Open the folder and you'll see a Folder titled 2.80. Go into folders:

2.80> scripts > startup

Take these files (listed next) from MayaConfig4Blender and drop them into the startup folder:

fa_hotkeys.py
fa_marking_menu.py
fa_quadvew.py
fapanel.py
msm_from_object_2-8.py

---------------------------------

Next, go into the "Theme" folder of the Config, and drop the files "maya_blue_theme" and "maya_theme" into this location (interface_theme) within the Blender folder:

2.80> scripts > presets > interface_theme

--------------------------------

Lastly, go back to the 2.80 folder. Drag and drop the "config" folder from the config files into the 2.80 folder. There will end up being 4 folders in there now:

config
datafiles
python
scripts

The config folder should already have the startup.blend and userpref.blend in it. 

Go back out to the root folder, and startup the blender application. 

------------------------------

Navigate to Preferences (Edit > Preferences).
Under the "Add-ons" tab, Import and enable the addons:

fa_markingmenu.py 
fa_quadview.py

They're located back in the startup file where you copied them to previously.

------------------------------

Back in Preferences, go to the Themes tab and Import the two themes if they're not already there (they're located in the interface_theme folder here --> 2.80 > scripts > presets > interface_theme):

maya_blue_theme.xml
maya_theme.xml

------------------------------

In Preferences, under the Keymap tab, import the fa_hotkey.py file (located in the script folder). Make sure FA Hotkeys are active back in Preferences under the Keymap tab. 

Do 3 checks to make sure the config and all addons are working:
1. In the 3D viewport, make sure the "Maya" display panel is showing on the left hand side and that the buttons are working.
2. In the 3D viewport, "right mouse click" should activate the marking menu.
3. In the 3D viewport, "space bar" should activate the Quad View pie menu. 

Thank you for using Form Affinity content!




