# cut_mesh
Tools for mesh trimming and cutting in Blender.  
This is at a very very early stage of development.  
Work flow will change a lot.

Installation:
-Download github repository
-unzip to folder named "cut_mesh"
-place in addon's directory
-enable in user preferences

Useage:
1.  Select a Mesh object in Object Mode
2.  Call "Polytrim" from the spacebar menu

3.  Drawing the cut Outline
    -LeftClick to start polyline outline
    -LeftClick to extend polyline
    -LeftClick first point to close the loop
    
    -RightClick any point to delete, or 'X' to delete selected point
    
4. Editing the Outline
    -LeftClick any point to select it
    -'G' to grab and move the selected point
    -'X' to delete the selected point
    -'Right Click' to delete any point
    
5.  Preivew the cut, and verify it
    -'C' to preview the cut
    -Invalid segments will be drawn in red
    -Valid segments will be drawn in green
    -Cut it ready when all segments are green
    -Move the invalid points, add or delete poitns untial total outline is green
    
6.  Select the part of mesh to be removed
    -'S' and the LeftClick inside or outside of the loop.  Yellow points will appear where the click was placed.
    
7.  'D' to calculate the intermediate step behind the scenes

8.  'E' to cut and separate the mesh and finish operator.
    

