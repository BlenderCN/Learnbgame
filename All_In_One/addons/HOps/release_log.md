### 0.0.9.5 
    - loop slide option for Bweight added (helper)
- modal mirror operator added
    - fix for auto smooth overwrite
- default for auto smooth changed to 180
- fix for brush preview error
- MESHmachine integration in edit mode operations
    - shrinkwrap refresh is hidden for now
- boolean operators added to edit mode under operations
- mir2 cstep support
- spherecast V1 added to meshtools
- QArray supports multiple objects
- TThick supports multiple objects
- misc panel has options for Qarray and Tthick
- Boolean scroll systems added
- basic Kitops support for Csharpen

### 0.0.9.4
- tooltip update
- added hotkeys for edit mode booleans
- rewrite of mirror operator
- new operator added allowing to swap green/red boolshape status (in pie/menu when boolshape is selected)
    -red / green boolean system
        -still needs a smash all booleans bypassing the red/green system
- new boolshape status added allowing to skip applying boolean modifiers
- brush selector added to sculpt menu
- bwidth limit is unlocked for undefined meshes

### 0.0.9.3
- pie menu missing options added
- cut-in operator added
    -cut in added to Q menu. Still needs hotkey
    -context for cut in fixed no single select option
- all inserts now use principal shaders as proxies
- fixed B-width Z wire show mode
- additional icons added
- renderset1 fix for filmic official
- material helper fix for new materials
- relink mirror options added
- figet support added
- new clean mesh operator (options in helper)
- adaptive width mode addeded
- adaptive segments mode adeded

### 0.0.9.2
- hoteys can be set in options hotkey tab
- scale option for modal operators was added
- booleans solver is global now can be set helper
- ssharp, cstep, csharp work on multi objects now (old multi operators removed)
- bool options added to menu/panel
- added 'reset axis' operator
- version bump.
- all operators support step workflow fromn ow on
- s/cstep operators removed and replaced by step
- wire options added to HOPS Helper
- sharpness angle for sharp operator is now global (acces via Tpanel/helper/F6)
- mesh display toggle added to edtimode >> meshtools
- pro mode switches clean ssharp with demote for reason....
- machin3 decal support added

### 0.0.8.7
- Multiple object support for B-Width
- New operator 'bevel multiplier' added
- Hud indicator moved from text to logo by default
	1. logo in corner added
	2. text status disabled by default
	3. added preferences to enable/disable logo/statustext (logo under extra / pro mode)
	4. preferences to change logo color/placement
- new operator - sharp manager was added
- csharpen uses global sharps now
- ssharpen uses global sharps now
- set sharp uses global sharps now
- added new global way to define what sharp edges to use (T-panel/ helper-misc)
- SUB-d status removed from all operators (use global statuses now)
- bweight can now select all other bweight edges in object while in modal state by presing A
- BOOLSHAPE objects are hiden to renderer now (outliner icon)
- slash assigns boolshape status for cutters now
- panels/menus/pie updated with correct operators
- added option for slash to refresh origin of cutters (in F6)
- Slice and rebbol operators replaces with slash
- fixes for material cutting
- renderset C created (speed preset)
- fix for register bug (hotkeys duplication)
- pie menu and menu uses same hotkey now (Q) it can be chosen in preferences
