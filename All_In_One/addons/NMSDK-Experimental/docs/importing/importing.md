### Importing models into Blender

NMSDK is capable of importing NMS *SCENE* files and loading the models.

At the moment the functionality is still in beta and has many issues, primarily due to the custom shader setup used by NMS.

Importing scenes from the game is simple. An option can be found in the `Import` drop-down menu found by selecting `File` > `Import`

![importing](/../images/import.png)

This will open up a file selection dialog which lets you select the scene you wish to import.
Keep in mind that at the moment NMSDK will import **all** of the components of a scene excepting ones that are referenced by the scene. So for a large scene such as the freighter scene it may actually take a minute or two to load all the data.