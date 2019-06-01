Display mode
============
One of the work modes in the OpenCV Laboratory is the display mode of the final image of the result of the function.
It is launched from the ImageViewer node by clicking the button marked with a red box in the image below. 

.. image:: http://kube.pl/wp-content/uploads/2018/05/view_window_12.png

The display mode consists of the work area (1), the information panel bar (2), the tool panel (3), the property panel (4) and the image editor panel bar (5).

.. image:: http://kube.pl/wp-content/uploads/2018/05/view_window_11-e1525881407880.png

Work area
---------
The image of the final result of the function is displayed in the work area.

Information panel bar
---------------------

Information panel bar includes a panel icon (1), a menu with drop-down lists (2), a return button to work mode (3), and information about the program version, number of nodes present in the work area and memory used by the current project (4).

.. image:: http://kube.pl/wp-content/uploads/2018/05/panel_top_21-e1525884258593.png

The menus are lists concerning: file operations, view options and help.
    - File - traditional document-related operations used in most application programs:
        - `New` - Create new project.
        - `Open` - Open project.
        - `Open Recent...` - open one of the most recently used projects.
        - `Revent` - re-load the last saved version of the file.
        - `Recover Last Session` - as written.
        - `Recover Auto Save...` - restore the last automatic recording.
        - `Save` - save project.
        - `Save As...` - as written.
        - `Save Copy` - Save as copy of the procejt.
        - `Quit` - as written.
    - Window - options for the view:
        - `Duplicate Window` - create a duplicate of the current view in a new window.
        - `Toggle Window Fullscreen` - expand the window to the entire screen.
        - `Save Screenshot` - create a view image.
        - `Toggle System Console` - console with logs.
    - Help - mainly relevant documentation:
        - `OCVL Documentation`: <http://opencv-laboratory.readthedocs.io/en/latest/?badge=latest>
        - `OpenCV Documentation`: <http://kube.pl/>
        - `Blender Dokumentation`: <https://docs.blender.org/manual/en/dev/editors/node_editor/introduction.html>
        - `OCVL Web Panel`: <https://ocvl-cms.herokuapp.com/admin/login/>
        - `OCVL Blog`: <http://kube.pl/>
        - `Show Node Splash` - show a welcome window.
Tool panel
----------
The tool panel is located on the left side of the screen and contains the following options: Histogram, Waveform, Vectorscope, Sample Line, Scope Samples.
    - Histogram - is one of the most popular statistical charts. It serves to present distributions of empirical features, which means that with its help, we present what results we obtained for some quantitative variables.

    The histogram is included: 
       
    1. Chart screem,
    2. The channel selection panel for which the graph is to be displayed: 
        - `Luma` - brightness, 
        - `RGB` - components RGB,
        - `R` - red channel, 
        - `G` - green channel, 
        - `B` - blue channel,
        - `A` - alpha channel.
    3. Graph format selection button - linear / full. 
    4. Minimize button.
    
    .. image:: http://kube.pl/wp-content/uploads/2018/05/histogram-e1525940457158.png

    - Waveform - waveform for selected channel, luminance or brightness.

    Available options are:

    1. The determinant of points included in the chart.
    2. List of choice of specific modes:
        - `Luma`,
        - `RGB`,
        - `YCbCr (ITU 601)`, 
        - `YCbCr (ITU 709)`, 
        - `YCbCr (jpeg)`.

    .. image:: http://kube.pl/wp-content/uploads/2018/05/waveform-e1525947824105.png

    - Vectorscope - displays information about color, saturation and shade.
           
    .. image:: http://kube.pl/wp-content/uploads/2018/05/vectroscope_11-e1525944387308.png

    - Sample Line - illustrates the distribution of data on a selected section of the image. It contains the available options the same as the histogram * (see above) *, except that they only apply to the episode mentioned. The section is determined using the button `Sample Line`.

    .. image:: http://kube.pl/wp-content/uploads/2018/05/sampleline_10-e1525945011371.png
    
    - Scope Samples - determines the range of sampling. Available options:
        - `Full Sample` - determines whether any pixel of the image is to be sampled,
        - `Accuracy` - the ratio of the pixel lines of the source of the original image to the sample.

    .. image:: http://kube.pl/wp-content/uploads/2018/05/scopesamles_11-e1525946057982.png

Properties panel
----------------
The property panel is located on the right side of the display mode screen. The `Display` tab in it has two options:
    - *Aspect Ratio* - changes the size of the image in the X axis and / or in the Y axis.
    - *Coordinates* - the 'Repeat' button duplicates the image on the screen.

    .. image:: http://kube.pl/wp-content/uploads/2018/05/panel_right_21-e1525950437896.png


The image editor panel bar
--------------------------
The image editor's panel bar is located at the bottom of the screen and contains: the display mode icon (1), the menu with drop-down lists (2), image viewer (3), the channel panel for the displayed image (4).

.. image:: http://kube.pl/wp-content/uploads/2018/05/panel_bottom_21-e1525960142919.png


The menus are lists concerning the following: view and image.
    - View - view options:
        - `Properties` - show or hide the property panel,
        - `Tool Sherif` - show or hide the tool panel,
        - `View Zoom In` - zoom in gradually,
        - `View Zoom Out` - zoom out gradually,
        - `Zoom 1:8` - show in scale 1:8,
        - `Zoom 1:4` - show in scale 1:4,
        - `Zoom 1:2` - show in scale 1:2,
        - `Zoom 1:1` - show in scale 1:1,
        - `Zoom 2:1` - show in scale 2:1,
        - `Zoom 4:1` - show in scale 4:1,
        - `Zoom 8:1` - show in scale 8:1,
        - `View All` - show full screen,
        - `Duplicate Area into New Window` - .
    - Image - image options:
        - *Save As Image* - ,
        - *Invert* - invert chosen channel:
            - `Invert Image Colors` - ,
            - `Invert Red Channel` - ,
            - `Invert Green Channel` - ,
            - `Invert Blue Channel` - ,
            - `Invert Alpha Channel` - .

A set of buttons with the choice of channel options in which the image is to be displayed are:
(1) `color with alpha`, (2) `color`, (3) `alpha channel`, (4) `red channel`, (5) `green channel` and (6) `blue channel`.

.. image:: http://kube.pl/wp-content/uploads/2018/05/panel_bottom_22-e1525963458333.png