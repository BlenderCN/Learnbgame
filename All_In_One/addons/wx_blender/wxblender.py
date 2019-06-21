#!/usr/bin/env python

"""
wxBlender
=========
wxPython in Blender Addon

wxPython toolkit widgets running in Blender.
Menus, Frames, Dialogs, Custom Buttons, Thumbnails, etc...

![wxBlender](https://raw.github.com/Metallicow/wxBlender/master/wxBlender_Screenshot.png)


Requirements
------------
* Blender 2.65+(built with Python33+)

  http://www.blender.org/

* wxPython Project Phoenix(works with Python3)

  http://wxpython.org/Phoenix/snapshot-builds/

* wxBlender

  https://github.com/Metallicow/wxBlender


Installation
------------
1. The phoenix download might come as a python .egg.

   Python .egg files are simply a renamed .zip file,
   so in other words you can open/extract the egg
   with an compression application
   such as 7-zip, WinRAR, etc.

   Place wx directory from the phoenix download
   in Blender's `#.##/python/lib/site-packages` directory.

2. Place the wx_blender directory in your Blender User `scripts/addons` directory.

   Depending on your type of Blender build, this location may vary.
   Ex: if Blender is portable.


Running wxBlender
-----------------
1. Start up Blender.
2. Go to File>User Preferences... in the MenuBar.
3. Under the "Addons" tab of the Blender User Preferences Dialog...
   ...Check the "3D View: wxBlender" addon checkbox.
4. Click the "Save User Settings" button in the Blender User Preferences Dialog
   so the plugin starts at startup.
5. Close the Blender User Preferences Dialog.

In the properties window of the 3D View there should now be a Panel
named "wxBlender".


[Blender logo usage guidelines](http://www.blender.org/about/logo/)
-------------------------------------------------------------------
![BlenderFavicon](https://raw.github.com/Metallicow/wxBlender/master/wx_blender/images/favicon.ico)
![BlenderLogo](https://raw.github.com/Metallicow/wxBlender/master/wx_blender/images/logo.png)

The Blender logo is a copyrighted property of NaN Holding B.V, and has been licensed in 2002 to the Blender Foundation. The logo and the brand name "Blender" are not part of the GNU GPL, and can only be used commercially by the Blender Foundation on products, websites and publications.

Under the following conditions, third parties may use the Blender logo as well:

  1. The logo can only be used to point to the product Blender. When used with a link on a web page, it should point to the url [blender.org](http://www.blender.org/).
  2. You will visualize and promote your own branding more prominent than you use the Blender logo. The Blender logo only can be used as a secondary brand, which means it has to be clear for an average viewer that this is not an official Blender or Blender Foundation website, publication or product.
  3. You can use the Blender logo on promotion products, such as T-shirts or caps or trade show booths, provided it is a secondary brand as described in point 2.
  4. The logo is used unaltered, without fancy enhancements, in original colors, original typography, and always complete (logo + text blender).
  5. In case you use the logo on products you sell commercially, you always have to [contact us](http://www.blender.org/foundation/) with a picture of how it will be used, and ask for explicit permission.

If you have further questions or doubts, do not hesitate to [contact us](http://www.blender.org/foundation/).
Usage in artwork and community websites


[Usage in artwork and community websites](http://www.blender.org/about/logo/)
-----------------------------------------------------------------------------

Blender's logo has been used in hundreds of ways. This was - and still is - considered to be an honest tribute to Blender, and the guidelines are not meant to make these uses "illegal" or "officially disapproved". This page is only meant to clarify the Blender Foundation guidelines so that people know their minimum rights and where they can use the logo.

Modifying the Blender logo is really part of your own artistic freedom, and the Blender Foundation will never act against such tributes. Just don't expect us to "officially approve" of it, that's all.

Thanks,

Ton Roosendaal, Chairman of the Blender Foundation

Amsterdam, March 2009


License
-------
Anything **NOT** involving "Blender" Logos and Graphics/Images/blender16 PyEmbeddedImage is licensed

GNU GPL v2.0

http://www.gnu.org/licenses/old-licenses/gpl-2.0.html


Tested On
---------

| Operating System          | Blender Versions            | Phoenix           |
|:-------------------------:|:---------------------------:|:-----------------:|
| Windows XP SP3 32bit      | 2.65 - 2.69                 | 3.0.1.dev75563    |
| Other OS                  | TODO                        |                   |

"""

#-Imports.----------------------------------------------------------------------
#--Python Imports.
import os
import sys

## print('sys.executable', sys.executable)
# returns C:\Program Files\Blender Foundation\Blender #.##\blender.exe
## print('sys.prefix', sys.prefix)
# returns C:\Program Files\Blender Foundation\Blender #.##\#.##\python

# Add site-packages to the system path.
# Older Blenders might not have it on the sys.path.
# We need to find wx in site-packages.
sitePackPath = os.path.join(sys.prefix, 'lib', 'site-packages')
print(os.path.exists(sitePackPath))
if os.path.exists(sitePackPath) and sitePackPath in sys.path:
    pass # Ok. Good.
elif os.path.exists(sitePackPath) and sitePackPath not in sys.path:
    sys.path.insert(0, sitePackPath)
else:
    raise Exception("Can't locate %s" % sitePackPath)

#--Blender Imports.
import bpy

#--wxPython Imports.
import wx
from wx.lib.embeddedimage import PyEmbeddedImage

#--Local Plugin Imports.
from .HackRefresh import HackRefresh


#-Globals.----------------------------------------------------------------------

# Define a translation function.
_ = wx.GetTranslation

# Get version infos.
wxPythonVersion = wx.version()
major, minor, micro, release = sys.version_info[0:-1]
pythonVersion = u'%d.%d.%d-%s' %(major, minor, micro, release)

gFileDir = os.path.dirname(os.path.abspath(__file__))
gImgDir = gFileDir + os.sep + 'images'
gThumbDir = gFileDir + os.sep + 'thumbnails'

ID_SHOW_FRAME = wx.NewId()
ID_BLENDER_ORG = wx.NewId()
ID_WXBLENDER_GITHUB = wx.NewId()
ID_OPEN_WXBLENDER_PLUGINDIR = wx.NewId()
ID_HELLOBLENDER = wx.NewId()

blender16 = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAACPUlEQVR4Ac2Ra0hTYQCGD0gE"
    "bLq7bjtbBAEEBRBSgGhJJVG4hktUNKhEsMJCKSoJ2sWd4zItqYwQlYmEQkAZXZUgQAwLuhFB"
    "kaaamFGmSrbpPE+bSgSCRBD0wPvzeb/3+z7hnzFZbl6BJPaMlFve383TpP5VyetDBmdIFj+H"
    "JXH2Zk78QWE58IurFI81a+6MxaG4LQ481szwaXPau5JE96RXVKi2012kb2516XRL5G/llriw"
    "T+yixg5V0VTaFiOi+PSK4tEq+LQQ0DNwwvz4mku3fklJy+74VG+aao+crt71psTUFpPxG6G9"
    "EAbvwMcH0FEKgSTCFZYv0lb1xiUlT4uN6k+nzFJEEifwG6BLpncSDgdfkXuxh0d9P+BFPQRM"
    "9B03P6zPTFj3S0YSV0fnP4/dFTkJriSjhMdJOXkbIVlG2BTAmN3E0HgI2pzMeA08KTb4F+QK"
    "MQvZNhaTJ9yWkYjPOEtwO1OhEPb8IEJKFcKWGuLSL/BseAbuHQGvFiRbS+xkDwHb9OIrN3QW"
    "aJxzkgWq18DEWxq7htHnNbHSeZWjzS/h+wjUbSDiT2LgmPmSEKm0jYcrbfSXJXqEKDey1aaQ"
    "XxxCNkLTjqgwyNgMjE4rKOFRaHWBpOer29rb4FDvFIIO9bbaDNVm4TcaM1X75r9TNi0saXPB"
    "9RyoXct88Tk75zNUBcJy3C9IODDltvZz1gqyAaRoAhZCPutgx15NkfAndOZrtO258YV9pcbL"
    "H8pMdbdyEwq79+u0wn/FT0hkVS62vfMaAAAAAElFTkSuQmCC")


class AddMeshesPanel(bpy.types.Panel):
    """Creates a Panel in the 3D View properties window"""
    bl_label = "Add Mesh"
    bl_idname = "OBJECT_3DVIEW_AddMeshesPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"

    def draw_header(self, context):
        layout = self.layout
        # Always place the PLUGIN Icon in the header, so you know it is a plugin.
        layout.label(icon='PLUGIN')
        # Optionally you can add more than one icon to further visually describe your plugin's nature.
        # In this case the same icon as a community addon.
        layout.label(icon='POSE_DATA')

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label(text="About This Plugin", icon='HELP')

        row = layout.row()
        row.label(text="Blender Meshes", icon='BLENDER')

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("mesh.primitive_plane_add", text='Plane', icon='MESH_PLANE')
        row.operator("mesh.primitive_grid_add", text='Grid', icon='MESH_GRID')
        row = col.row(align=True)
        row.operator("mesh.primitive_cube_add", text='Cube', icon='MESH_CUBE')
        row.operator("mesh.primitive_circle_add", text='Circle', icon='MESH_CIRCLE')
        row = col.row(align=True)
        row.operator("mesh.primitive_uv_sphere_add", text='UV Sphere', icon='MESH_UVSPHERE')
        row.operator("mesh.primitive_ico_sphere_add", text='Ico Sphere', icon='MESH_ICOSPHERE')
        row = col.row(align=True)
        row.operator("mesh.primitive_cylinder_add", text='Cylinder', icon='MESH_CYLINDER')
        row.operator("mesh.primitive_cone_add", text='Cone', icon='MESH_CONE')
        row = col.row(align=True)
        row.operator("mesh.primitive_torus_add", text='Torus', icon='MESH_TORUS')
        row.operator("mesh.primitive_monkey_add", text='Monkey', icon='MESH_MONKEY')

        row = layout.row()
        row.label(icon='POSE_DATA')
        row.label(text="Extra Objects Plugin Meshes")
        row.label(icon='PLUGIN') # Add Extra Icon To Other Side of Label

        box = layout.box()
        col = box.column(align=True)
        row = col.row(align=True)
        row.operator("mesh.bolt_add", text='Bolt', icon='MOD_SCREW')
        row.operator("mesh.landscape_add", text='Landscape', icon='RNDCURVE')
        row = col.row(align=True)
        row.operator("mesh.primitive_diamond_add", text='Diamond', icon='PMARKER')
        row.operator("mesh.primitive_gem_add", text='Gem', icon='SPACE3')
        row = col.row(align=True)
        row.operator("mesh.primitive_gear", text='Gear', icon='SCRIPTWIN')
        row.operator("mesh.primitive_worm_gear", text='Worm Gear', icon='SCRIPTWIN')

        row = col.row(align=True)
        row.operator("mesh.primitive_steppyramid_add", text='Step Pyramid', icon='SORTSIZE')
        row.operator("mesh.honeycomb_add", text='Honeycomb', icon='PLUGIN')
        row = col.row(align=True)
        row.operator("mesh.primitive_teapot_add", text='Teapot+', icon='PLUGIN')


# Start wxPython Frame App -----------------------------------------------------

class wxGradientBannerPanel(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY,
                 pos=wx.DefaultPosition, size=(-1, 48),
                 style=wx.BORDER_NONE, name='panel'):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        self.parent = parent
        self.dcBmp = wx.Bitmap(gImgDir + os.sep + 'logo.png', wx.BITMAP_TYPE_PNG)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMotion)

    def DrawGradientBanner(self, dc):
        dc.GradientFillLinear(self.GetClientRect(), '#FF8000', '#FFFFFF', wx.NORTH)
        dc.DrawBitmap(self.dcBmp, 10, (self.GetSize()[1] - self.dcBmp.GetHeight()) // 2)
        dc.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        dc.SetTextForeground('#005385')
        dc.DrawText('wx', 44, 4)

    def OnPaint(self, event):
        """
        Handle the wx.EVT_PAINT event for :class: wxGradientBannerPanel.
        """
        # wx.EVT_PAINT event handlers should always use only
        # those types of DC's specific for wx.EVT_PAINT events.
        ## dc = wx.BufferedPaintDC(self)
        dc = wx.PaintDC(self)
        self.DrawGradientBanner(dc)

        event.Skip() # Very important to let any higher level handlers be called.

    def OnLeftDown(self, event):
        """
        Handle the wx.EVT_LEFT_DOWN event for :class: wxGradientBannerPanel.
        """
        self.CaptureMouse()
        x, y = self.parent.ClientToScreen(event.GetPosition())
        originx, originy = self.parent.GetPosition()
        dx = x - originx
        dy = y - originy
        self.parent.delta = ((dx, dy))

    def OnLeftUp(self, event):
        """
        Handle the wx.EVT_LEFT_UP event for :class: wxGradientBannerPanel.
        """
        if self.HasCapture():
            self.ReleaseMouse()

    def OnMotion(self, event):
        """
        Handle the wx.EVT_MOTION event for :class: wxGradientBannerPanel.
        """
        if event.Dragging() and event.LeftIsDown():
            x, y = self.parent.ClientToScreen(event.GetPosition())
            self.parent.Move((x - self.parent.delta[0], y - self.parent.delta[1]))


class wxAddMeshesPanel(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.BORDER_SUNKEN, name='panel'):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        self.parent = parent

        btn1 = wx.Button(self, -1, 'Add Meshes Panel to 3D View Properties')
        btn1.Bind(wx.EVT_BUTTON, self.OnRegisterAddMeshesPanel)

        gSizer = wx.GridSizer(rows=2, cols=2, vgap=5, hgap=5)

        dirBpyOpsMesh = dir(bpy.ops.mesh)

        btn2 = wx.BitmapButton(self, -1, wx.Bitmap(gThumbDir + os.sep + 'cube.png', wx.BITMAP_TYPE_PNG))
        btn2.SetToolTip(wx.ToolTip('bpy.ops.mesh.primitive_cube_add()'))
        btn2.Bind(wx.EVT_BUTTON, self.OnAddMeshFromToolTip)

        btn3 = wx.BitmapButton(self, -1, wx.Bitmap(gThumbDir + os.sep + 'monkey.png', wx.BITMAP_TYPE_PNG))
        btn3.SetToolTip(wx.ToolTip('bpy.ops.mesh.primitive_monkey_add()'))
        btn3.Bind(wx.EVT_BUTTON, self.OnAddMeshFromToolTip)

        btn4 = wx.BitmapButton(self, -1, wx.Bitmap(gThumbDir + os.sep + 'pyramid.png', wx.BITMAP_TYPE_PNG))
        btn4.SetToolTip(wx.ToolTip('bpy.ops.mesh.primitive_steppyramid_add()'))
        btn4.Bind(wx.EVT_BUTTON, self.OnAddMeshFromToolTip)
        if not 'primitive_steppyramid_add' in dirBpyOpsMesh:
            btn4.Enable(False)

        btn5 = wx.BitmapButton(self, -1, wx.Bitmap(gThumbDir + os.sep + 'teapot.png', wx.BITMAP_TYPE_PNG))
        btn5.SetToolTip(wx.ToolTip('bpy.ops.mesh.primitive_teapot_add()'))
        btn5.Bind(wx.EVT_BUTTON, self.OnAddMeshFromToolTip)
        if not 'primitive_teapot_add' in dirBpyOpsMesh:
            btn5.Enable(False)

        gSizer.AddMany([(btn2, 0, wx.ALIGN_TOP | wx.ALIGN_LEFT),
                        (btn3, 0, wx.ALIGN_TOP | wx.ALIGN_RIGHT),
                        (btn4, 0, wx.ALIGN_BOTTOM | wx.ALIGN_LEFT),
                        (btn5, 0, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT),
                        ])

        vbSizer = wx.BoxSizer(wx.VERTICAL)
        vbSizer.Add(btn1, 0, wx.EXPAND | wx.ALL, 5)
        vbSizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 0)

        vbSizer.Add(gSizer, 1, wx.ALIGN_CENTRE | wx.SHAPED, 5)
        self.SetSizer(vbSizer)

    def OnAddMeshFromToolTip(self, event):
        evtObj = event.GetEventObject()
        tt = evtObj.GetToolTip()
        ttStr = tt.GetTip()
        try:
            eval(ttStr)
        except AttributeError as exc:
            import traceback
            tb = traceback.format_exc()
            wx.MessageBox('%s' % tb, 'AttributeError', wx.ICON_ERROR)
        ## wx.CallAfter(HackRefresh)
        self.parent.Close() # Optional: Lets destroy after clicking.

    def OnRegisterAddMeshesPanel(self, event):
        bpy.utils.register_class(AddMeshesPanel)
        ## wx.CallAfter(HackRefresh)
        self.parent.Close() # Optional: Lets destroy after clicking.


class wxBlenderAddMeshesFrame(wx.Frame):

    def __init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 # Use these styleBits for a standard frame...
                 ## style=wx.DEFAULT_FRAME_STYLE |
                 ##       wx.STAY_ON_TOP
                 # ...Or use these styleBits for a borderless/taskbarless frame.(WinXP)
                 style=wx.STAY_ON_TOP |
                       wx.FRAME_NO_TASKBAR |
                       wx.RESIZE_BORDER
                       , name='frame'):

        wx.Frame.__init__(self, parent, id, title, pos, size, style, name)

        self.delta = (0, 0)

        ## self.SetDoubleBuffered(True)
        self.CreateStatusBar()
        self.SetStatusText('wxPython %s running on Python %s' %(wxPythonVersion, pythonVersion))

        banner_panel = wxGradientBannerPanel(self)
        panel = wxAddMeshesPanel(self)
        self.SetBackgroundColour(panel.GetBackgroundColour())

        vbSizer = wx.BoxSizer(wx.VERTICAL)
        vbSizer.Add(banner_panel, 0, wx.EXPAND | wx.ALL)
        vbSizer.Add(panel, 1, wx.EXPAND | wx.ALL)
        self.SetSizer(vbSizer)
        self.Fit()
        self.SetMinSize(self.GetSize())

        self.sizeAttr = self.GetSize()

        #### self.SetTransparent(200) # Not working out so well with the HackRefresh...

        # We want the Escape key to Close the frame, so bind the whole family tree also.
        for child in self.GetChildren():
            child.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
            for grandchild in child.GetChildren():
                grandchild.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

        self.SetIcon(wx.Icon(wx.Bitmap(gImgDir + os.sep + 'favicon.ico', wx.BITMAP_TYPE_ICO)))
        self.Bind(wx.EVT_CLOSE, self.OnDestroy)

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_MOVE, self.OnMove)

        self.Centre()
        self.SetFocus()

        # Lose focus destroy workaround.
        wx.CallAfter(self.Bind, wx.EVT_ACTIVATE, self.OnActivate)

    def OnKeyUp(self, event):
        keyCode = event.GetKeyCode()
        if keyCode == wx.WXK_ESCAPE:
            self.Close()

    def OnMove(self, event):
        HackRefresh()

    def SetSelfSizeAttr(self):
        self.sizeAttr = self.GetSize()

    def OnSize(self, event):
        self.Layout()
        # Smooth sizing(what it should be normally) when sizing the frame bigger.
        if event.GetSize()[0] < self.sizeAttr[0] or event.GetSize()[1] < self.sizeAttr[1]: # The user is decreasing the frame size.
            HackRefresh()
        wx.CallAfter(self.SetSelfSizeAttr)

    def OnActivate(self, event):
        """
        Destroy when frame loses focus to workaround Blender GUI lockup
        issue when wxapp is active.
        Ex: User has clicked back to the Blender GUI or another application.
        """
        try:
            self.Close()
        except RuntimeError:
            ###############
            ## Traceback (most recent call last):
            ##   File "....Blender\2.69\scripts\addons\wx_blender\wxblender.py", line ###, in OnActivate
            ##     self.Close()
            ## RuntimeError: wrapped C/C++ object of type wxBlenderAddMeshesFrame has been deleted
            ###############
            pass
        except Exception as exc:
            wx.Bell()
            import traceback
            tb = traceback.format_exc()
            f = open(gFileDir + os.sep + 'traceback.log', 'w')
            f.write('%s' %tb)
            f.close()

    def OnDestroy(self, event):
        self.Destroy()


class wxBlenderApp(wx.App):
    def OnInit(self):
        self.SetClassName('wxBlenderApp')
        self.SetAppName('wxBlenderApp')
        gMainWin = wxBlenderAddMeshesFrame(None)
        gMainWin.SetTitle('wxBlenderApp')
        self.SetTopWindow(gMainWin)
        gMainWin.Show()
        return True

# End wxPython Frame App -------------------------------------------------------


def OnHelloBlender(event):
    print('Hello Blender!')

def OnShowwxFrame(event):
    gMainWin = wxBlenderAddMeshesFrame(None)
    gMainWin.SetTitle('wxBlenderApp')
    gMainWin.Show()

    #### app = wxBlenderApp(False)
    #### app.MainLoop()

def OnVisitWebsite(event):
    """
    Open a website in users default webbrowser.
    """
    import webbrowser
    evtId = event.GetId()
    if evtId == ID_BLENDER_ORG:
        webbrowser.open('http://www.blender.org/')
    elif evtId == ID_WXBLENDER_GITHUB:
        webbrowser.open('https://github.com/Metallicow/wxBlender')

def OnAddMeshFromMenuItemHelpString(event):
    """
    Add mesh to scene.
    """
    evtObj = event.GetEventObject()
    evtId = event.GetId()
    eval(evtObj.GetHelpString(evtId))

def OnOpenwxBlenderPluginDir(event):
    """
    Open the local plugin dir in explorer, etc...
    """
    import webbrowser
    webbrowser.open(gFileDir)


class wxPythonFrameInBlender(bpy.types.Operator):
    """Standard wx.Frame App."""
    bl_idname = "mcow.wxblender_wxframe"
    bl_label = "wxPython Frame in Blender"

    def execute(self, context):
        gApp = wxBlenderApp(redirect=False,
                            filename=None,
                            useBestVisual=False,
                            clearSigInt=True)
        gApp.MainLoop()

        return {'FINISHED'}


class wxPythonMenuInBlender(bpy.types.Operator):
    """Simple wx.Menu PopupMenu App."""
    bl_idname = "mcow.wxblender_wxmenu"
    bl_label = "wxPython Menu in Blender"

    def execute(self, context):
        gApp = wx.App(redirect=False,
                      filename=None,
                      useBestVisual=False,
                      clearSigInt=True)

        # Even though the frame will not be shown,
        # we need to make a frame so the munu will have something to popup on.
        frame = wx.Frame(None)
        menu = wx.Menu()

        menu.Append(ID_SHOW_FRAME, 'Show wxBlender Add Meshes Frame')

        mi = wx.MenuItem(menu, ID_BLENDER_ORG, 'Visit www.blender.org')
        mi.SetBitmap(wx.Bitmap(gImgDir + os.sep + 'tango_internet_web_browser16.png', wx.BITMAP_TYPE_PNG))
        menu.Append(mi)

        mi = wx.MenuItem(menu, ID_WXBLENDER_GITHUB, 'Visit wxBlender on GitHub')
        mi.SetBitmap(wx.Bitmap(gImgDir + os.sep + 'tango_internet_web_browser16.png', wx.BITMAP_TYPE_PNG))
        menu.Append(mi)

        mi = wx.MenuItem(menu, ID_HELLOBLENDER, 'print "Hello Blender!"')
        mi.SetBackgroundColour('#393939')
        mi.SetTextColour('#FF8000')
        mi.SetBitmap(blender16.GetBitmap()) # Show how to use a PyEmbeddedImage.
        menu.Append(mi)

        mi = wx.MenuItem(menu, ID_OPEN_WXBLENDER_PLUGINDIR, 'Open wxBlender Plugin Dir')
        mi.SetBitmap(wx.Bitmap(gImgDir + os.sep + 'tango_folder_open_blue_24.png', wx.BITMAP_TYPE_PNG))
        menu.Append(mi)

        subMenu = wx.Menu()

        for name in ['Plane', 'Cube', 'Circle', 'UV Sphere', 'Icosphere',
                     'Cylinder', 'Cone', 'Grid', 'Monkey', 'Torus']:
            newid = wx.NewId()
            if name == 'Icosphere':
                subMenu.Append(newid, '%s' % name, 'bpy.ops.mesh.primitive_ico_sphere_add()')
            else:
                subMenu.Append(newid, '%s' % name, 'bpy.ops.mesh.primitive_%s_add()' % name.lower().replace(' ', '_'))
            menu.Bind(wx.EVT_MENU, OnAddMeshFromMenuItemHelpString, id=newid)

        menu.AppendSubMenu(submenu=subMenu, text='Add Mesh')

        menu.Bind(wx.EVT_MENU, OnShowwxFrame, id=ID_SHOW_FRAME)
        menu.Bind(wx.EVT_MENU, OnVisitWebsite, id=ID_BLENDER_ORG)
        menu.Bind(wx.EVT_MENU, OnVisitWebsite, id=ID_WXBLENDER_GITHUB)
        menu.Bind(wx.EVT_MENU, OnHelloBlender, id=ID_HELLOBLENDER)
        menu.Bind(wx.EVT_MENU, OnOpenwxBlenderPluginDir, id=ID_OPEN_WXBLENDER_PLUGINDIR)

        frame.PopupMenu(menu)
        menu.Destroy()

        frame.Close()
        gApp.MainLoop()

        return {'FINISHED'}


class wxBlenderPanel(bpy.types.Panel):
    """Creates a Panel in the 3D View properties window"""
    bl_label = "wxBlender"
    bl_idname = "WXBLENDER"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"

    def draw_header(self, context):
        layout = self.layout
        # Always place the PLUGIN Icon in the header, so you know it is a plugin.
        layout.label(icon='PLUG')
        layout.label(icon='PLUGIN')
        # Optionally you can add more than one icon to further visually describe your plugin's nature.
        ## layout.label(icon='FILE_BLEND')

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label(text="About This Plugin", icon='HELP')

        row = layout.row()
        row.operator("mcow.wxblender_wxmenu", text='wxPython Menu', icon='LAMP_DATA')

        row = layout.row()
        row.operator("mcow.wxblender_wxframe", text='wxPython Frame', icon='LAMP_DATA')

