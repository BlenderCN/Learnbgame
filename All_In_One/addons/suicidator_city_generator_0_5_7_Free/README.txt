This program, Suicidator City Generator (SCG) is copyright Arnaud Couturier.
It allows you to quickly create 3d cities in the 3D software Blender.

Official website:
http://cgchan.com/suicidator

Licence for the free version:
You are free to use and redistribute Suicidator City Generator Free as you like, provided you keep it unaltered. 
You cannot resell it, claim it as your own, nor change this license. You are not allowed to reverse-engineer the code. 

Licence for the full (paid) version:
The copy of Suicidator City Generator Full you purchase can be used by only you. 
You cannot modify it nor redistribute it. You are not allowed to reverse-engineer the code. 

//---------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------

#######  QUICK START
In order to start using SCG, follow these 3 steps:


#######  (1) Install the latest version of Blender
Get it from http://www.blender.org/download/get-blender/
SCG will probably not run with previous versions of Blender.
If SCG is not compatible with a particular version of Blender, you will see it in the list of addons, but you won't be able to activate it.
Check the SCG website for SCG compatibility updates as new version of Blender and SCG come out.



#######  (2) Install / upgrade Java
SCG requires Java 5 minimum (sometimes also referred to as Java 1.5, JRE 5 or J2SE 1.5)
The more recent your Java version, the faster SCG will run.
Java 6 (which is the same as Java 1.6) and above is recommended.
The procedure to get Java depends on your operating system

- Windows: go to http://java.com, and download the latest version of Java. Restart your computer.
- MacOS: use your update center. See http://gephi.org/users/install-java-6-mac-os-x-leopard/
- Linux: use your package manager (example apt-get or aptitude in Ubuntu)

To check whether Java is correctly installed, open a terminal, then type "java -version".
The terminal in Windows is located in "Start menu/programs/accessories/console or terminal"
If you see the version of Java you have, you can continue to step 3 below.

If you have a message saying the Java command is unknown, then Java is not correctly installed, and SCG won't work. 
Follow the steps below to fix it.
The likely cause is your PATH environment variable is not updated.
PATH is used by your system to know where it can find many programs, including Java.

To update your PATH on Windows XP (should be somewhat identical on Vista/7),
right clic on the "My Computer" desktop icon -> properties -> advanced tab -> environment variables (bottom).
In "system variables", look for the PATH variable, select it, click "Edit".
Now, be careful not to erase anything, or not to make typing mistakes, or you may seriously break your system!
If you do a mistake, always clic "Cancel" to go back one step.
At the end of the PATH value, add a semicolon (;) as a separator, then put the full path to your Java bin folder.
The Java bin folder (bin for binary, where all the Java commands are) should be located in
C:\Program Files\Java\bin
C:\Program Files\Java\jre6\bin, or something similar.
You know you've found it when you can see lots of .exe and .dll files, including "java.exe" in that folder.
So you can search your computer for "java.exe" if you can't locate the Java bin folder.
Once you've found the java bin folder, add its path (for example C:\Program Files\Java\jre6\bin) to the PATH variable, and validate your change.
Restart your computer, and check "java -version" in a console again, and it should work.




#######  (3) Install the addon in Blender
You must copy the whole SCG folder in the Blender addons folder.
The Blender addons folder should be "Blender install directory/blender version/scripts/addons"
For example, mine on Windows XP is "C:\Program Files\Blender\2.62\scripts\addons"
So in the end, you should have something like
C:\Program Files\Blender\2.62\scripts\addons\suicidator_city_generator_0_5_1_Free

At this stage, SCG will be seen by Blender, but not enabled by default.
To enable SCG in Blender, open the Blender preferences (shortcut: CTRL+ALT+U) -> addons tab
Type "suicidator" in the search box (top left), you should see SCG listed.
Check its checkbox.

It is possible to have multiple versions of SCG (free, full, 0.5, 0.6 ...)
but only one version can be registered at a time in Blender.
You must first disable the current SCG, then enable the other version of SCG you want.
More information about Blender addons in general on the Blender wiki: http://wiki.blender.org/index.php/Doc:2.6/Manual/Extensions/Python/Add-Ons

Once the addon is registered, open the toolshelf (shortcut "t") in the 3D view.
You should see the SCG panel at the bottom.

To use SCG:
1) Set your city options
2) Launch the generation process

You'll find all the SCG output textures in your Blender temporary folder ("temp"), usually at C:\tmp (windows) or /tmp (Mac, Linux).
To know where it is located, see
http://wiki.blender.org/index.php/Doc:2.6/Manual/Preferences/File




This was just an introduction. Check the online manual for more info.

//---------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------
//---------------------------------------------------------------------------------------------------------------------------------------------

CREDITS
SCG would not be possible without the follwoing libraries (used legally)
- JTS, by the great Martin Davis!
- pyrolite, by Irmen de Jong
- Apache commons-cli
- pngEncoder, by ObjectPlanet



Happy city building :)
Arnaud Couturier (piiichan)
couturier.arnaud@gmail.com
