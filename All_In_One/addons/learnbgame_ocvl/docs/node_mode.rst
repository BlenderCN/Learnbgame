Welcome to the OpenCV Laboratory program!
=========================================

The OpenCV Laboratory program is launched with the main view of interface, which includes: work area (1) with a welcome window (2), information panel bar (3), nodes panel (4), property panel (5) and bar of nodes editor panel (6).

.. image:: http://kube.pl/wp-content/uploads/2018/05/ocvl_window_11-e1525773857808.png

Work area and welcome window
----------------------------
The work area occupies the central part of the view, and after starting the OpenCV Laboratory program, a welcome window is additionally displayed.

The welcome window consists of four elements: Splash, History, Docs i Auth.
    - Splash - the main section contains the logo, the name of the program with information about its version, and the following options:
        - `Start with blank desk` - start work from an empty workspace.
        - `Recover last session` - as it is written.
        - `Create account` - as it is written.
        - `First steps` - tutorial.
    - History - section with the following options:
        - `Recover last session` - as it is written.
        - `Light` - "day" view display mode.
        - `Dark` - "night" view display mode.
        - `Tutorial - First steps` - linkt to tutorials about program.
    - Docs - a section with links to documentation related to the program:
        - `OCVL Web Panel`: <https://ocvl-cms.herokuapp.com/admin/login/>
        - `OCVL Blog`: <http://kube.pl/>
        - `OCVL Dacumentation`: <http://opencv-laboratory.readthedocs.io/en/latest/?badge=latest>
        - `OpenCV Documentation`: <https://docs.opencv.org/3.0-beta/index.html>
        - `Blender Documentation`: <https://docs.blender.org/manual/en/dev/editors/node_editor/introduction.html>
    - Auth - authorization section.

Information panel bar
---------------------

The information panel bar contains the panel icon (1), a menu with drop-down lists (2) and information about the program version, the number of nodes present in the work area and the memory used by the current project (3).

.. image:: http://kube.pl/wp-content/uploads/2018/05/panel_top_11-1-e1525776857599.png

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

Tools panel - nodes
-------------------
.. image:: http://kube.pl/wp-content/uploads/2018/05/panel_left.png

The tool panel - nodes located on the left side of the view screen are tabs in which individual nodes are grouped and placed in the appropriate categories:
    - Laboratory - basic nodes most often used.
    - Core - nodes related to the kernel.
    - Imgproc - nodes directly related to the visual side of the image.
    - Objdetect - nodes associated with objects in the image.
    - Groups - tab associated with grouping nodes.

.. note:: Description of individual nodes can be found in the OpenCV Laboratory documentation by clicking the link: <http://opencv-laboratory.readthedocs.io/en/latest/nodes.html>

Properties panel
----------------
.. image:: http://kube.pl/wp-content/uploads/2018/05/panel_right-1.png

The property panel located on the right side of the view screen contains a number of options related to displaying information about currently used nodes and their properties, and other additional operations:
    - Node - in the tab there is, among other things, the possibility of resetting the settings made at a given node (Reset Node), entering your own name (Level), and help related to a specific node is available.
    - Color - the ability to set any color of the node. 
    - Properties - properties that a given node has and access to additional information contained in specific documentation as well as calculation times.

The node editor panel bar
-------------------------

The node editor panel bar located at the bottom of the view screen, contains the bar icon (1), menu with drop-down lists (2), node tree viewer (3), and additional function keys (4).

.. image:: http://kube.pl/wp-content/uploads/2018/05/panel_bottom_11-e1525804151156.png

The bottom panel menu consists of lists for: view, selection, node placement and node operations.
    - View - view options:
        - `Properties` - show or hide the node properties panel.
        - `Tool Shelf` - show or hide the tools panel - nodes.
        - `Zoom In` - enlarge the view in the work area.
        - `Zoom Out` - reduce the view in the work area.
        - `View Selected` - change the size of the view so that you can see the selected nodes located in the work area.
        - `View All` - change the view size so that you can see all nodes located in the work area.
        - `Duplicate Area into New Window` - .
    - Select - selection options:
        - `Border Select` - select specific nodes within a rectangular frame.
        - `Circle Select` - select specific nodes within a circular area.
        - `(De)select All` - deselect or select all nodes.
        - `Iverse` - the inverse of the selection.
        - `Select Linked From` - select the nodes with connections that reach the selected node.
        - `Select Linked To` - select the nodes with connections coming from the selected node.
        - `Select Grouped` - select a group of nodes by: type, color, prefix, suffix.
        - `Active Same Type Previous` - activate the previous node of the same type.
        - `Active Same Type Next` - activate another node of the same type.
        - `Find Node` - Find a specific node.
    - Add - nodes grouped and deployed in the appropriate categories as in the tools - nodes panel.
    - Node - nodes options:
        - `Translate` - move the node to the desired location.
        - `Duplicate` - duplicate the node.
        - `Delete` - remove node.
        - `Delete with Reconnect` - delete with reconnection.
        - `Make Links` - create a connection between selected nodes.
        - `Make and Replace Links` - create a connection between selected nodes.
        - `Cut Link` - cut off the connection between nodes.
        - `Detach Links` - delete all connections of selected nodes and make new connections with neighboring nodes.
        - `Edit Group` - edit group of nodes.
        - `Ungroup` - ungroup the nodes.
        - `Make Group` - make group of nodes.
        - `Group Insert` - place the selected nodes in the selected group.

The following functions are located under the additional buttons on the bar of the node editor panel:

.. image:: http://kube.pl/wp-content/uploads/2018/05/panel_bottom_12-e1525804271768.png

1. Go to the "parent" of the node on the tree.
2. Automatically extend nodes after adding a new node to an existing chain.
3. Snap to the grid.
4. Pull the node to: Grid, Node X, Node Y, Node X/Y.
5. 'Copy' and ' paste' the node.