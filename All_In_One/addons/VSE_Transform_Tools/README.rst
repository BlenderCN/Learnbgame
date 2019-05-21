.. raw:: html

    
    <h1 align="center">
      VSE_Transform_Tools</br>
    </h1>
    
    <h2>Installation</h2>
    
    <ol>
    <li>Go to the <a href="https://github.com/doakey3/VSE_Transform_Tools/releases">Releases</a> page and download the latest <code>VSE_Transform_Tools.zip</code></li>
    <li>Open Blender</li>
    <li>Go to File &gt; User Preferences &gt; Addons</li>
    <li>Click "Install From File" and navigate to the downloaded .zip file and install</li>
    <li>Check the box next to "VSE Transform Tools"</li>
    <li>Save User Settings so the addon remains active every time you open Blender</li>
    </ol>
    
    <h2>Operators</h2>
    <table>
        <tr>
            <td width=222px><a name="top_Add_Transform" href="#Add_Transform" title="A transform modifier must be
    added to a strip before the
    strip can be scaled or rotated
    by this addon. If you're
    planning to make keyframes to
    adjust the scale or the
    rotation, ensure that you are
    modifying a transform strip by
    adding one with this operator.">Add Transform</a></td>
            <td width=222px><a name="top_Delete" href="#Delete" title="Deletes all selected strips as
    well as any strips that are
    inputs of those strips. For
    example, deleting a transform
    strip with this operator will
    also delete the strip it was
    transforming.">Delete</a></td>
            <td width=222px><a name="top_Mouse_Track" href="#Mouse_Track" title="Select a transform strip or a
    strip with "image offset"
    enabled. Press Alt+A to play,
    hold M to continuously add
    keyframes to transform strip
    while tracking the position of
    the mouse.">Mouse Track</a></td>
            <td width=222px><a name="top_Set_Cursor_2D" href="#Set_Cursor_2D" title="Set the pivot point (point of
    origin) location. This will
    affect how strips are rotated
    and scaled.">Set Cursor 2D</a></td>
        </tr>
        <tr>
            <td width=222px><a name="top_Adjust_Alpha" href="#Adjust_Alpha" title="">Adjust Alpha</a></td>
            <td width=222px><a name="top_Duplicate" href="#Duplicate" title="Duplicates all selected strips
    and any strips that are inputs
    of those strips. Calls the Grab
    operator immediately after
    duplicating.">Duplicate</a></td>
            <td width=222px><a name="top_Pixelate" href="#Pixelate" title="Pixelate a clip by adding 2
    transform modifiers: 1
    shrinking, 1 expanding.">Pixelate</a></td>
            <td width=222px><a name="top_Track_Transform" href="#Track_Transform" title="Use a pair of track points to
    pin a strip to another. The UI
    for this tool is located in the
    menu to the right of the
    sequencer in the Tools submenu.
    To pin rotation and/or scale,
    you must use 2 tracking points.
    <br>
    ![UI](https://i.imgur.com/wEZLu8a.jpg)">Track Transform</a></td>
        </tr>
        <tr>
            <td width=222px><a name="top_Autocrop" href="#Autocrop" title="Sets the scene resolution to
    fit all visible content in the
    preview window without changing
    strip sizes.">Autocrop</a></td>
            <td width=222px><a name="top_Grab" href="#Grab" title="">Grab</a></td>
            <td width=222px><a name="top_Rotate" href="#Rotate" title="">Rotate</a></td>
            <td width=222px rowspan="3"></td>
        </tr>
        <tr>
            <td width=222px><a name="top_Call_Menu" href="#Call_Menu" title="Bring up the menu for inserting
    a keyframe. Alternatively, you
    may enable automatic
    keyframing. <br> ![Automatic
    Keyframe
    Insertion](https://i.imgur.com/kFtT1ja.jpg)">Call Menu</a></td>
            <td width=222px><a name="top_Group" href="#Group" title="">Group</a></td>
            <td width=222px><a name="top_Scale" href="#Scale" title="">Scale</a></td>
        </tr>
        <tr>
            <td width=222px><a name="top_Crop" href="#Crop" title="">Crop</a></td>
            <td width=222px><a name="top_Meta_Toggle" href="#Meta_Toggle" title="Toggles the selected strip if
    it is a META. If the selected
    strip is not a meta,
    recursively checks inputs until
    a META strip is encountered and
    toggles it. If no META is
    found, this operator does
    nothing.">Meta Toggle</a></td>
            <td width=222px><a name="top_Select" href="#Select" title="">Select</a></td>
        </tr>
    </table>
        <h3><a name="Add_Transform" href="#top_Add_Transform">Add Transform</a></h3>
    <p>A transform modifier must be added to a strip before the strip can be scaled or rotated by this addon. If you're planning to make keyframes to adjust the scale or the rotation, ensure that you are modifying a transform strip by adding one with this operator.</p>
    
    <table>
        <tr>
            <th width=208px>Shortcut</th>
            <th width=417px>Function</th>
            <th width=256px>Demo</th>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/T.png" alt="T"></td>
            <td><p>Add Transform</p>
    </td>
            <td align="center" rowspan="1"><img src="https://i.imgur.com/v4racQW.gif"></td>
        </tr>
    </table>
        <h3><a name="Adjust_Alpha" href="#top_Adjust_Alpha">Adjust Alpha</a></h3>
    <p></p>
    
    <table>
        <tr>
            <th width=208px>Shortcut</th>
            <th width=417px>Function</th>
            <th width=256px>Demo</th>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/Q.png" alt="Q"></td>
            <td><p>Begin alpha adjusting</p>
    </td>
            <td align="center" rowspan="6"><img src="https://i.imgur.com/PNsjamH.gif"></td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/CTRL.png" alt="CTRL"></td>
            <td><p>Round to nearest tenth</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/RIGHTMOUSE.png" alt="RIGHTMOUSE"></td>
            <td><p>Escape alpha adjust mode</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/LEFTMOUSE.png" alt="LEFTMOUSE"></td>
            <td><p>Set alpha, end alpha adjust mode</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/RET.png" alt="RET"></td>
            <td><p>Set Alpha, end alpha adjust mode</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/ZERO.png" alt="ZERO"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/ONE.png" alt="ONE"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/TWO.png" alt="TWO"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/THREE.png" alt="THREE"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/FOUR.png" alt="FOUR"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/FIVE.png" alt="FIVE"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/SIX.png" alt="SIX"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/SEVEN.png" alt="SEVEN"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/EIGHT.png" alt="EIGHT"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/NINE.png" alt="NINE"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/PERIOD.png" alt="PERIOD"></td>
            <td><p>Set alpha to value entered</p>
    </td>
        </tr>
    </table>
        <h3><a name="Autocrop" href="#top_Autocrop">Autocrop</a></h3>
    <p>Sets the scene resolution to fit all visible content in the preview window without changing strip sizes.</p>
    
    <table>
        <tr>
            <th width=208px>Shortcut</th>
            <th width=417px>Function</th>
            <th width=256px>Demo</th>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/SHIFT.png" alt="SHIFT"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/C.png" alt="C"></td>
            <td><p>Autocrop</p>
    </td>
            <td align="center" rowspan="1"><img src="https://i.imgur.com/IarxF14.gif"></td>
        </tr>
    </table>
        <h3><a name="Call_Menu" href="#top_Call_Menu">Call Menu</a></h3>
    <p>Bring up the menu for inserting a keyframe. Alternatively, you may enable automatic keyframing. <br> <img src="https://i.imgur.com/kFtT1ja.jpg" alt="Automatic Keyframe Insertion" /></p>
    
    <table>
        <tr>
            <th width=208px>Shortcut</th>
            <th width=417px>Function</th>
            <th width=256px>Demo</th>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/I.png" alt="I"></td>
            <td><p>Call menu</p>
    </td>
            <td align="center" rowspan="1"><img src="https://i.imgur.com/9Cx6XKj.gif"></td>
        </tr>
    </table>
        <h3><a name="Crop" href="#top_Crop">Crop</a></h3>
    <p></p>
    
    <table>
        <tr>
            <th width=208px>Shortcut</th>
            <th width=417px>Function</th>
            <th width=256px>Demo</th>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/C.png" alt="C"></td>
            <td><p>Begin/Set cropping, adding a transform if needed</p>
    </td>
            <td align="center" rowspan="5"><img src="https://i.imgur.com/k4r2alY.gif"></td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/ESC.png" alt="ESC"></td>
            <td><p>Escape crop mode</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/LEFTMOUSE.png" alt="LEFTMOUSE"></td>
            <td><p>Click the handles to drag</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/RET.png" alt="RET"></td>
            <td><p>Set crop, end cropping</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/ALT.png" alt="ALT"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/C.png" alt="C"></td>
            <td><p>Uncrop</p>
    </td>
        </tr>
    </table>
        <h3><a name="Delete" href="#top_Delete">Delete</a></h3>
    <p>Deletes all selected strips as well as any strips that are inputs of those strips. For example, deleting a transform strip with this operator will also delete the strip it was transforming.</p>
    
    <table>
        <tr>
            <th width=208px>Shortcut</th>
            <th width=417px>Function</th>
            <th width=256px>Demo</th>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/DEL.png" alt="DEL"></td>
            <td><p>Delete</p>
    </td>
            <td align="center" rowspan="2"><img src="https://i.imgur.com/B0L7XoV.gif"></td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/SHIFT.png" alt="SHIFT"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/DEL.png" alt="DEL"></td>
            <td><p>Delete strips and remove any other strips in the timeline with the same source. For scene strips, the scenes themselves will also be deleted.</p>
    </td>
        </tr>
    </table>
        <h3><a name="Duplicate" href="#top_Duplicate">Duplicate</a></h3>
    <p>Duplicates all selected strips and any strips that are inputs of those strips. Calls the Grab operator immediately after duplicating.</p>
    
    <table>
        <tr>
            <th width=208px>Shortcut</th>
            <th width=417px>Function</th>
            <th width=256px>Demo</th>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/SHIFT.png" alt="SHIFT"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/D.png" alt="D"></td>
            <td><p>Duplicate</p>
    </td>
            <td align="center" rowspan="1"><img src="https://i.imgur.com/IJh7v3z.gif"></td>
        </tr>
    </table>
        <h3><a name="Grab" href="#top_Grab">Grab</a></h3>
    <p></p>
    
    <table>
        <tr>
            <th width=208px>Shortcut</th>
            <th width=417px>Function</th>
            <th width=256px>Demo</th>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/G.png" alt="G"></td>
            <td><p>Grab</p>
    </td>
            <td align="center" rowspan="11"><img src="https://i.imgur.com/yQCFI0s.gif"></td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/SHIFT.png" alt="SHIFT"></td>
            <td><p>Hold to enable fine tuning</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/CTRL.png" alt="CTRL"></td>
            <td><p>Hold to enable snapping</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/RIGHTMOUSE.png" alt="RIGHTMOUSE"></td>
            <td><p>Escape grab mode</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/ESC.png" alt="ESC"></td>
            <td><p>Escape grab mode</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/LEFTMOUSE.png" alt="LEFTMOUSE"></td>
            <td><p>Set position, end grab mode</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/RET.png" alt="RET"></td>
            <td><p>Set position, end grab mode</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/ZERO.png" alt="ZERO"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/ONE.png" alt="ONE"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/TWO.png" alt="TWO"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/THREE.png" alt="THREE"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/FOUR.png" alt="FOUR"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/FIVE.png" alt="FIVE"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/SIX.png" alt="SIX"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/SEVEN.png" alt="SEVEN"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/EIGHT.png" alt="EIGHT"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/NINE.png" alt="NINE"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/PERIOD.png" alt="PERIOD"></td>
            <td><p>Set position by value entered</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/X.png" alt="X"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/Y.png" alt="Y"></td>
            <td><p>Constrain grabbing to the respective axis</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/MIDDLEMOUSE.png" alt="MIDDLEMOUSE"></td>
            <td><p>Constrain grabbing to axis</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/ALT.png" alt="ALT"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/G.png" alt="G"></td>
            <td><p>Set position to 0,0</p>
    </td>
        </tr>
    </table>
        <h3><a name="Group" href="#top_Group">Group</a></h3>
    <p></p>
    
    <table>
        <tr>
            <th width=208px>Shortcut</th>
            <th width=417px>Function</th>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/CTRL.png" alt="CTRL"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/G.png" alt="G"></td>
            <td><p>Group together selected sequences</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/ALT.png" alt="ALT"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/SHIFT.png" alt="SHIFT"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/G.png" alt="G"></td>
            <td><p>Ungroup selected meta strip</p>
    </td>
        </tr>
    </table>
        <h3><a name="Meta_Toggle" href="#top_Meta_Toggle">Meta Toggle</a></h3>
    <p>Toggles the selected strip if it is a META. If the selected strip is not a meta, recursively checks inputs until a META strip is encountered and toggles it. If no META is found, this operator does nothing.</p>
    
    <table>
        <tr>
            <th width=208px>Shortcut</th>
            <th width=417px>Function</th>
            <th width=256px>Demo</th>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/TAB.png" alt="TAB"></td>
            <td><p>Meta toggle</p>
    </td>
            <td align="center" rowspan="1"><img src="https://i.imgur.com/ya0nEgV.gif"></td>
        </tr>
    </table>
        <h3><a name="Mouse_Track" href="#top_Mouse_Track">Mouse Track</a></h3>
    <p>Select a transform strip or a strip with "image offset" enabled. Press Alt+A to play, hold M to continuously add keyframes to transform strip while tracking the position of the mouse.</p>
    
    <table>
        <tr>
            <th width=208px>Shortcut</th>
            <th width=417px>Function</th>
            <th width=256px>Demo</th>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/M.png" alt="M"></td>
            <td><p>Hold to add keyframes, release to stop</p>
    </td>
            <td align="center" rowspan="1"><img src="https://i.imgur.com/6091cqv.gif"></td>
        </tr>
    </table>
        <h3><a name="Pixelate" href="#top_Pixelate">Pixelate</a></h3>
    <p>Pixelate a clip by adding 2 transform modifiers: 1 shrinking, 1 expanding.</p>
    
    <table>
        <tr>
            <th width=208px>Shortcut</th>
            <th width=417px>Function</th>
            <th width=256px>Demo</th>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/P.png" alt="P"></td>
            <td><p>Pixelate</p>
    </td>
            <td align="center" rowspan="1"><img src="https://i.imgur.com/u8nUPj6.gif"></td>
        </tr>
    </table>
        <h3><a name="Rotate" href="#top_Rotate">Rotate</a></h3>
    <p></p>
    
    <table>
        <tr>
            <th width=208px>Shortcut</th>
            <th width=417px>Function</th>
            <th width=256px>Demo</th>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/R.png" alt="R"></td>
            <td><p>Begin rotating, adding transform if needed.</p>
    </td>
            <td align="center" rowspan="9"><img src="https://i.imgur.com/3ru1Xl6.gif"></td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/SHIFT.png" alt="SHIFT"></td>
            <td><p>Hold to enable fine tuning</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/CTRL.png" alt="CTRL"></td>
            <td><p>Hold to enable stepwise rotation</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/RIGHTMOUSE.png" alt="RIGHTMOUSE"></td>
            <td><p>Escape rotate mode</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/ESC.png" alt="ESC"></td>
            <td><p>Escape rotate mode</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/LEFTMOUSE.png" alt="LEFTMOUSE"></td>
            <td><p>Set rotation, end rotate mode</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/RET.png" alt="RET"></td>
            <td><p>Set rotation, end rotate mode</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/ZERO.png" alt="ZERO"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/ONE.png" alt="ONE"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/TWO.png" alt="TWO"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/THREE.png" alt="THREE"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/FOUR.png" alt="FOUR"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/FIVE.png" alt="FIVE"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/SIX.png" alt="SIX"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/SEVEN.png" alt="SEVEN"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/EIGHT.png" alt="EIGHT"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/NINE.png" alt="NINE"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/PERIOD.png" alt="PERIOD"></td>
            <td><p>Set rotation to value entered</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/ALT.png" alt="ALT"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/R.png" alt="R"></td>
            <td><p>Set rotation to 0 degrees</p>
    </td>
        </tr>
    </table>
        <h3><a name="Scale" href="#top_Scale">Scale</a></h3>
    <p></p>
    
    <table>
        <tr>
            <th width=208px>Shortcut</th>
            <th width=417px>Function</th>
            <th width=256px>Demo</th>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/S.png" alt="S"></td>
            <td><p>Begin scaling, adding transform if needed.</p>
    </td>
            <td align="center" rowspan="11"><img src="https://i.imgur.com/oAxSEYB.gif"></td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/SHIFT.png" alt="SHIFT"></td>
            <td><p>hold to enable fine tuning</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/CTRL.png" alt="CTRL"></td>
            <td><p>Hold to enable snapping</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/RIGHTMOUSE.png" alt="RIGHTMOUSE"></td>
            <td><p>Escape scaling mode</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/ESC.png" alt="ESC"></td>
            <td><p>escape scaling mode</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/LEFTMOUSE.png" alt="LEFTMOUSE"></td>
            <td><p>Set scale, end scaling mode</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/RET.png" alt="RET"></td>
            <td><p>Set scale, end scaling mode</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/ZERO.png" alt="ZERO"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/ONE.png" alt="ONE"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/TWO.png" alt="TWO"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/THREE.png" alt="THREE"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/FOUR.png" alt="FOUR"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/FIVE.png" alt="FIVE"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/SIX.png" alt="SIX"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/SEVEN.png" alt="SEVEN"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/EIGHT.png" alt="EIGHT"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/NINE.png" alt="NINE"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/PERIOD.png" alt="PERIOD"></td>
            <td><p>Set scale by value entered</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/X.png" alt="X"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/Y.png" alt="Y"></td>
            <td><p>Constrain scaling to respective axis</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/MIDDLEMOUSE.png" alt="MIDDLEMOUSE"></td>
            <td><p>Constrain scaling to axis</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/ALT.png" alt="ALT"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/S.png" alt="S"></td>
            <td><p>Unscale</p>
    </td>
        </tr>
    </table>
        <h3><a name="Select" href="#top_Select">Select</a></h3>
    <p></p>
    
    <table>
        <tr>
            <th width=208px>Shortcut</th>
            <th width=417px>Function</th>
            <th width=256px>Demo</th>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/RIGHTMOUSE.png" alt="RIGHTMOUSE"></td>
            <td><p>Select visible strip</p>
    </td>
            <td align="center" rowspan="3"><img src="https://i.imgur.com/EVzmMAm.gif"></td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/SHIFT.png" alt="SHIFT"></td>
            <td><p>Enable multi selection</p>
    </td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/A.png" alt="A"></td>
            <td><p>Toggle selection</p>
    </td>
        </tr>
    </table>
        <h3><a name="Set_Cursor_2D" href="#top_Set_Cursor_2D">Set Cursor 2D</a></h3>
    <p>Set the pivot point (point of origin) location. This will affect how strips are rotated and scaled.</p>
    
    <table>
        <tr>
            <th width=208px>Shortcut</th>
            <th width=417px>Function</th>
            <th width=256px>Demo</th>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/LEFTMOUSE.png" alt="LEFTMOUSE"></td>
            <td><p>Cusor 2D to mouse position</p>
    </td>
            <td align="center" rowspan="2"><img src="https://i.imgur.com/1uTD9C1.gif"></td>
        </tr>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/CTRL.png" alt="CTRL"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/LEFTMOUSE.png" alt="LEFTMOUSE"></td>
            <td><p>Snap cursor 2D to nearest strip corner or mid-point</p>
    </td>
        </tr>
    </table>
        <h3><a name="Track_Transform" href="#top_Track_Transform">Track Transform</a></h3>
    <p>Use a pair of track points to pin a strip to another. The UI for this tool is located in the menu to the right of the sequencer in the Tools submenu. To pin rotation and/or scale, you must use 2 tracking points. <br> <img src="https://i.imgur.com/wEZLu8a.jpg" alt="UI" /></p>
    
    <table>
        <tr>
            <th width=208px>Shortcut</th>
            <th width=417px>Function</th>
            <th width=256px>Demo</th>
        <tr>
            <td align="center"><img src="https://cdn.rawgit.com/doakey3/Keyboard-SVGs/master/images/.png" alt=""></td>
            <td><p></p>
    </td>
            <td align="center" rowspan="1"><img src="https://i.imgur.com/nWto3hH.gif"></td>
        </tr>
    </table>