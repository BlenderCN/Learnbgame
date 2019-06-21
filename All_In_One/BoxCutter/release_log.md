### 0.6.9.0
- 3D cutter
- HUD moved to center of shape
- curve mode unlocked for circle draw
- NGON can be applied to cursor with double click + alt
- holding shift will keep bevel modifier for all shapes

### 0.6.8.0
- BC can multi cut now instead of border system
- BC hotkeys added to preferences tab
- added color preferences for all modes
- cutter origin now snaps to the cursor
- added option for circle to move center to cursor - hotkey D
- added new option to define cut depth from cursor
- added new option to define gray box size
- removed old carve solver from code
- fixed gray box bug when it was not drawing while no object in scene
- new grid system
- wire no longer goes off if it was on before
- W enables/disables wire in all drawing modes
- drawing respects the regions now
- bc mode can be enabled in many 3d windows at once
- fixed curve opengl issue
- added option for drawing modes to always jump to ortho view
- click logo toggles snapping(optional)
- help toggle box
- new help display system

### 0.6.7.0
- fix for mirror selection
- fix for circle cursor placement
- fix for circle operator transformation
- mesh maker for eddit mode added (temporarily removed)
- added way to run operators from menus/calls
- curve mode (tab) for draw operators do not allow to add points now


### 0.6.6.0
- mirror is using 2d region axis now X and Y
- added projecton box(light blue); to use draw cutter in edit mode
- purple box added; allow to cut around the mesh (press Z while drawing)
- BC no longer draws in objs other then mesh
- mirror hotkeys added for curve (1/2/3 in curve modal state)
- snap axi option for curves 'move' mode (shold shift while move / W to swap axis)
- modal scale added for curve operator (press S)
- modal rotate added for curve operator (press R)
- old rotate removed for curve
- fix for gray box mirror
- fix for wire not hiding if draw operator is canceled


### 0.6.5.2
- fix for grey box


### 0.6.5.1
- fix for pie added to preferences (for builds below 2.79)


### 0.6.5.0
- view align operator in (shift+alt+MMB)
- rotation for curve/ngon added (R/shift+R)
- fix for cutting mesh with distance origin placement
- fix for cuting to cursor in local view
- boolean system redesigned:
	- booleans for bordes and box drawing are now separated
	- 'mod' options are removed, added 'apply boolean' instead
- support for new hops step workflow
- fix for 'convert to curve'
- removed fast bmesh method (after Hardops operators speedup it's no longer needed)
- fixed boolean error if just clicked
- cutter removal for booleans and draws separated
- mirror mode for all cutters added(info pie/help)
- logo indicator changed to new one
- hud options for logo and text added in UI preferences


### 0.6.0.0
- slice replaced with slash operator for yellow box cutter
- way to delate or keep cutter mesh after cutting (in D pie menu)
- new boolean option fast bmesh (doesn't support matterial cutting usefull for sculpting or bigger mesh cutts)
- matterial support for all cutters
- new grid system (relative to the zoom)
- new grid display
- ability to rotate box cutter (after drawing press R or shift R)
- new options in D pie menu to select rotation angle
- new way to use booleans with drawing frames if 2 obj are selected
- fixed pivot point for cutter
- fixed a bug with mesh creation if Algin to view or enter edit mode are used
- overlay for options and grid no longer draws when in edit mode
- hotkes blocking scorll has been removed ( we use D pie now)
