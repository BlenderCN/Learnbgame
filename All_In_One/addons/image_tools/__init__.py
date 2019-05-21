# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
# this needs nconvert to run :
# http://www.xnview.com/en/download_nc.html

# HISTORY
'''
23/10/11 0.68
  misc code changes and comments. pushed in my own git
21/10/11 0.67
. installed ubuntu 11.10 (and compiz eye candies :)
. linux os should be able to drag/resize :
  events were copied in the modal to make them available in the hud with
      self.event = event
  this works for win but absolutely not for linux : missing values and incoherencies
  like the mouse_x and y values, used for the mouseover test, thus the linux bug
. corrected modal, now as part of image tool, wait for more versatility to write apart.
  (multi instances support)
. check if the modal is still running when attempt to unregister() (with addon dep. on)

18/10/11 and past days :
. crop selection box : edition from mouseover
can be dragged
resize in every direction in every crop mode + percent mode
. some issue with linux reported by kylon

14/10/11 0.64
. corrected modal zoom
. improved ui H and W for crop width and height, deactivate everything when 'show' crop
  updates instantly after disabling 'show'
14/10/11 0.63
. first implementation of a crop box in the uv editor ('show' button in crop ui)
. work with script events 0.4 enabled (added addon dependencies field)
. noisy console

13/10/11
. big bug patch with autoupdate
13/10/11
. corrected a bug about panel registration
. added update options : 'autoupdate' check box, 'update now' button.
  autoupdate should be off for big images or slow nconvert functions or for
  large command sets sent in a row.

12/10/11 linux and mac version more reliable now. (huge thanks goes to Kilon !!)
. now in meta-svn
. fancier ui
. added noise + and -, oilify, emboss

10/10/11 linux and mac tests with Kilon.(pending)
. sh and cmd does not react the same way when receiving args from popen
http://bugs.python.org/issue6689
maybe python makedir in tmp is related to it..
sent this patched file to kilon for yet another test.
. improved nconvert_path() in order it looks for nconvert in the addon first
whatever where the addon folder is (or named in fact) :extern, contrib or regular
. an image slot name is 21 chrs max, and it needs 4 to add a '.tmp' extension
  so it needed to be shortened if len > 17. also some checks if name already exists

[...]

august 2011 initiated
'''

# TODO
'''
. img.nconvert() does not work for unsaved image (quick to fix)
. categorize nconvert features : colors, transform, FX (gimp vocables)
. better bpy support
. replace original
. presets
'''

# SOME COMMANDS
'''
# image_tools.nconvert(img0,'-rotate 86')

imtool = bpy.context.window_manager.imagetools
tempset = imtool.tempset
import image_tools

img0 = bpy.data.images['untitled']
img0.nconvert('-rotate 86')
imgtmp = bpy.data.images['untitled.tmp']
'''

bl_info = {
    "name": "image tools",
    "description": "basic image edition. needs nconvert to work ( http://www.xnview.com/ )",
    "author": "Littleneo, Kilon (linux and mac compat)",
    "version": (0, 67),
    "blender": (2, 5, 9),
    "api": 39307,
    "location": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Mesh",
    "dependencies": ""
}
#    "dependencies": "Script Events (0,4)"
import subprocess
import shutil
from sys import modules

if "bpy" in locals():
    import imp
    imp.reload(fs_tools)
    imp.reload(imgt_ui)

else :
    import bpy
    import time as _time

from . fs_tools import *
from . imgt_ui import *
import image_tools.modal

def nconvert_path() :
    exe = 'nconvert.exe' if 'Window' in bpy.app.build_platform else 'nconvert'
    #print( clean(modules['image_tools'].__path__[0]) + '/' + exe )
    paths = [
        '# local',
        clean(modules['image_tools'].__path__[0]) + '/' + exe,
        clean(modules['image_tools'].__path__[0]) + '/NConvert/' + exe,
        clean(modules['image_tools'].__path__[0]) + '/nconvert/' + exe,
        clean(modules['image_tools'].__path__[0]) + '/XnView/' + exe,
        '# windows',
        'C:/Program Files/XnView/nconvert.exe',
        'D:/Program Files/XnView/nconvert.exe'
        '# linux',
        '/usr/bin/nconvert/nconvert',
        '# user bin folder here ?',
        '# mac',
        '/applications/NConvert/nconvert',
        '/applications/nconvert/nconvert',
        ]

    for path in paths :
        if isfile(path) : return path
    else : print('%s was not found in the default app folders'%exe)

    return ''


def replace_image(img,newimg) :
    newimg.filepath_raw = img.filepath_raw
    name = img.name
    # relink any user of the source image before to remove..
    #for mat in bpy.data.materials :
    for screen in bpy.data.screens :
        for area in screen.areas :
            if area.type == 'IMAGE_EDITOR' :
                if area.spaces[0].image == img :
                    area.spaces[0].image = newimg
    img.user_clear()
    bpy.data.images.remove(img)
    newimg.name = name


def clipboard(newslot = False) :
    if newslot or 'clipboard' not in bpy.data.images :
        img = bpy.data.images.new(name = 'clipboard',width=128,height=128)
        if isdir( bpy.app.tempdir + 'imgt') == False :
            os.makedirs(bpy.app.tempdir + 'imgt')
        img.file_format = 'PNG'
        img.filepath_raw = clean(bpy.app.tempdir + 'imgt/' + 'clipboard.png')
    else :
        img = bpy.data.images['clipboard']
    img.source = 'FILE'
    return img.nconvert('-clipboard',False)

## button update proxy functions 
def update_refresh(self,context) :
    imtool = bpy.context.window_manager.imagetools
    if imtool.refresh == True :
        nconv_send('blah','blah')
        imtool.refresh = False


def update_revision_del(self,context) :
    imtool = bpy.context.window_manager.imagetools
    if imtool.rev_del == True :
        imtool.rev_del = False
        img = active()
        img.revision_del()


def update_crop(self,context) :
    imtool = bpy.context.window_manager.imagetools
    if imtool.has_helpers :
        if imtool.showcrop :
            # show image -1 as source
            if imtool.cropsource == False :
                imtool.cropsource = True
                srcimg = active().previous()
                imtool.helpers.start_crop()

        else :
            if imtool.cropsource :
                print('show current')
                imtool.cropsource = False
                img = active().next()
                imtool.helpers.stop()
                nconv_send(self,True)


def updatenow(self,context) :
    imtool = bpy.context.window_manager.imagetools
    if imtool.updatenow :
        imtool.updatenow = False
        nconv_send(self,True)


def nconv_send(self,context) :
    imtool = bpy.context.window_manager.imagetools
    now = True if context == True else False
    if imtool.autoupdate or now :

        tmpimg = active()
        tempset = tmpimg.revision()
        if tempset == False : tempset = tmpimg.revision(0)
        img = tmpimg.original()
        # brightness
        if tempset.brightness != 0 :
            command = ' -brightness %s'%tempset.brightness
        else : command = ''

        # contrast
        if tempset.autocontrast :
            command += ' -autocontrast'
        elif tempset.contrast != 0 :
            command += ' -contrast %s'%tempset.contrast

        # levels
        if tempset.autolevels :
            command += ' -autolevels'
        elif tempset.level_b != 0 or  tempset.level_w != 0 :
            command += ' -levels %s %s'%(tempset.level_b,tempset.level_w)

        # balance
        if tempset.balance_r != 0 or tempset.balance_g != 0 or tempset.balance_b != 0 :
            command += ' -balance %s %s %s'%(tempset.balance_r,tempset.balance_g,tempset.balance_b)

        # colors / colours
        if tempset.colors_nb >= 2 :
            if tempset.colors_nb in [256, 216, 128, 64, 32, 16, 8] :
                command += ' -colors %s'%(tempset.colors_nb)
            else :
                command += ' -colours %s'%(tempset.colors_nb)

        # colors / colours
        # crop/canvas
        if tempset.canvas_area != 'off' :
            if tempset.canvas_area == 'offset' :
                command += ' -crop %s %s %s %s'%(tempset.offset_x,tempset.offset_y,tempset.width,tempset.height)
            else :
                p = '%' if tempset.canvas_percent else ''
                command += ' -canvas %s%s %s%s %s'%(tempset.width,p,tempset.height,p,tempset.canvas_area)

        # resize
        if tempset.resize_percent and ( tempset.resize_x != 100 or tempset.resize_y != 100 ) :
            command += ' -resize %s%s %s%s'%(tempset.resize_x,'%',tempset.resize_y,'%')
        elif tempset.resize_percent == False and tempset.resize_x != 0 and tempset.resize_y != 0 :
            command += ' -resize %s %s'%(tempset.resize_x,tempset.resize_y)

        # sharpen
        if tempset.sharpen != 0 :
            command += ' -sharpen %s'%tempset.sharpen

        # rotate
        if tempset.degrees != 0 :
            command += ' -rotate %s'%tempset.degrees
            if tempset.smoothrot :
                command += ' -rotate_flag smooth'

        # flip
        if tempset.vflip : command += ' -xflip'
        if tempset.hflip : command += ' -yflip'
        # jpeg source :
        #    if tempset.degrees in [90,180,270] :
        #        command = '-jpegtrans %s'%tempset.degrees
        #    else :
        #if tempset.exif : command += '-jpegtrans exif'
        #else :

        # command
        if tempset.cmd != '' : command += ' '+tempset.cmd

        # noise
        if tempset.noise != 'off' :
            command += ' -noise %s'%tempset.noise
            if tempset.noise != 'reduce' : command += ' %s'%tempset.noise_value

        # emboss
        if tempset.emboss != 'off' : command += ' -%s'%tempset.emboss

        # oilify
        if tempset.oil !=0 : command += ' -oil %s'%tempset.oil

        # blur
        if tempset.blur != 0 :
            command += ' -blur %s'%tempset.blur

        img.nconvert(command)

########
## MAIN
########
class ImageToolsTempSet(bpy.types.PropertyGroup) :

    ## ui opts
    expand_colours = bpy.props.BoolProperty()
    expand_transfs = bpy.props.BoolProperty()
    expand_fx = bpy.props.BoolProperty()

    ## nconvert
    created = bpy.props.IntProperty()
    outdated = bpy.props.BoolProperty()
    id = bpy.props.IntProperty()
    source = bpy.props.IntProperty()
    path = bpy.props.StringProperty()

    degrees = bpy.props.IntProperty(
        default = 0,
        min=0,
        max=359,
        update=nconv_send
        )

    smoothrot = bpy.props.BoolProperty(
        default = True,
        name = 'smooth',
        description = 'smoothed rotations',
        update=nconv_send
        )

    vflip = bpy.props.BoolProperty(default = False, update=nconv_send)
    hflip = bpy.props.BoolProperty(default = False, update=nconv_send)
    exif = bpy.props.BoolProperty(default = False, update=nconv_send)

    blur = bpy.props.IntProperty(
        default = 0,
        min=0,
        max=100,
        update=nconv_send
        )
    sharpen = bpy.props.IntProperty(
        default = 0,
        min=0,
        max=100,
        update=nconv_send
        )
    brightness = bpy.props.IntProperty(
        default = 0,
        min=-100,
        max=100,
        update=nconv_send
        )
    contrast = bpy.props.IntProperty(
        default = 0,
        min = -100,
        max = 100,
        update = nconv_send
        )
    autocontrast = bpy.props.BoolProperty(
        default = False,
        name = 'Auto',
        update=nconv_send
        )
    level_b = bpy.props.IntProperty(
        default = 0,
        min = -1000,
        max = 1000,
        update = nconv_send
        )
    level_w = bpy.props.IntProperty(
        default = 0,
        min = -1000,
        max = 1000,
        update = nconv_send
        )
    autolevels = bpy.props.BoolProperty(
        default = False,
        name = 'Auto',
        update=nconv_send
        )
    balance_r = bpy.props.IntProperty(
        default = 0,
        name = 'R',
        min = -255,
        max = 255,
        update = nconv_send
        )
    balance_g = bpy.props.IntProperty(
        default = 0,
        name = 'G',
        min = -255,
        max = 255,
        update = nconv_send
        )
    balance_b = bpy.props.IntProperty(
        default = 0,
        name = 'B',
        min = -255,
        max = 255,
        update = nconv_send
        )
    colors_nb = bpy.props.IntProperty(
        default = 0,
        min = 0,
        max = 65536,
        update = nconv_send
        )
    cmd = bpy.props.StringProperty(
        default = '',
        update = nconv_send,
        description = "nconvert syntax. output file/format/compression can't be changed from there"
        )
    width = bpy.props.IntProperty(
        default = 0,
        name = 'W',
        min = 0,
        max = 5000,
        update = update_crop
        )
    height = bpy.props.IntProperty(
        default = 0,
        name = 'H',
        min = 0,
        max = 5000,
        update = update_crop
        )
    canvas_area = bpy.props.EnumProperty(
            name="Crop Area",
            items=(('off', "off", ""),
                   ('offset', "offset from top left", ""),
                   ('top-left', "top-left", ""),
                   ('top-center', "top-center", ""),
                   ('top-right', "top-right", ""),
                   ('center-left', "center-left", ""),
                   ('center', "center", ""),
                   ('center-right', "center-right", ""),
                   ('bottom-left', "bottom-left", ""),
                   ('bottom-center', "bottom-center", ""),
                   ('bottom-right', "bottom-right", ""),
                ),
            update = update_crop
        )
    canvas_percent = bpy.props.BoolProperty(name='%',default = False, update=update_crop)
    offset_x = bpy.props.IntProperty(
        default = 0,
        name = 'X',
        min = 0,
        max = 5000,
        update = update_crop
        )
    offset_y = bpy.props.IntProperty(
        default = 0,
        name = 'Y',
        min = 0,
        max = 5000,
        update = update_crop
        )
    resize_x = bpy.props.IntProperty(
        default = 100,
        name = 'X',
        min = 1,
        max = 6400,
        update = nconv_send
        )
    resize_y = bpy.props.IntProperty(
        default = 100,
        name = 'Y',
        min = 1,
        max = 6400,
        update = nconv_send
        )
    resize_percent = bpy.props.BoolProperty(name='%',default = True, update=nconv_send)
    noise = bpy.props.EnumProperty(
            name="Noise",
            items=(('off', "off", ""),
                   ('reduce', "Reduce", ""),
                   ('gaussian', "Gaussian", ""),
                   ('laplacian', "Laplacian", ""),
                   ('poisson', "Poisson", ""),
                ),
            update = nconv_send
        )
    noise_value = bpy.props.IntProperty(
        default = 0,
        min = 0,
        max = 100,
        update = nconv_send
        )
    emboss = bpy.props.EnumProperty(
            name="Emboss",
            items=(('off', "off", ""),
                   ('emboss', "normal", ""),
                   ('embossmore', "more", "")
                ),
            update = nconv_send
        )
    oil = bpy.props.IntProperty(
        default = 0,
        min = 0,
        max = 16,
        update = nconv_send
        )    

    def index(self) :
        return int(self.path_from_id().split('[')[1].split(']')[0])


class ImageTools(bpy.types.PropertyGroup) :

    nconvert_path =  bpy.props.StringProperty(default=nconvert_path())
    tempset =  bpy.props.CollectionProperty(type=ImageToolsTempSet)
    refresh = bpy.props.BoolProperty(default=False, update=update_refresh)
    rev_del = bpy.props.BoolProperty(default=False, update=update_revision_del)
    #modal = bpy.props.PointerProperty(type=ImageTools_modal)
    ## ui vars
    autoupdate = bpy.props.BoolProperty(default=True)
    updatenow = bpy.props.BoolProperty(default=False, update=updatenow)
    showcrop = bpy.props.BoolProperty(default=False, update=update_crop)
    cropsource = bpy.props.BoolProperty(default=False)

    ## returns the temp collection name from this image and a temp id
    def revision_name(self,rid='') :
        if rid == '' : rid = self.tempid()
        if rid == -1 : return self.name.replace('.tmp','')
        return self.name.replace('.tmp','') + str(rid)

    ## returns the temp collection member from this image and a temp id
    def revision(self,rid='') :
        imtool = bpy.context.window_manager.imagetools
        if rid == '' : rid = self.tempid()
        if rid == -1 : rid = 0
        name = self.revision_name(rid)
        #print('revision %s name %s :'%(id,name))
        if name in imtool.tempset :
            #print('  exist, returns img')
            return imtool.tempset[name]
        if rid == 0 :
            #print('  create revision 0')
            return self.revision_add(0)
        return False

    ## returns the temp revision id (int)  from this image file name
    # returns -1 if original image
    def tempid(self) :
        if '.tmp.' in self.filepath_raw :
            s = self.filepath_raw.rindex('_') + 1
            e = self.filepath_raw[s:].index('.') + s
            return int(self.filepath_raw[s:e])
        return -1
    
    ## returns the temporary image (the next revision) of an image
    # temporary slot names are img.name + '.tmp'. one slot per temp collection of an original
    # temporary file names are img.name - file extension +  '_id.tmp.png' in user temp
    # temporary collection names are img.name + id
    def temp(self,id='') :
        img = self
        if len(img.name) > 17 :
            newname = img.name[0:17]
            ni = 000
            while newname in bpy.data.images :
                newname = '%s.%03i'%(newname[:-4],ni)
                ni += 1
            img.name = newname
        imtool = bpy.context.window_manager.imagetools
        name = img.name.replace('.tmp','')
        if id == '' : id = img.tempid() + 1
        else : id = min(id,img.revision_count() - 1)
        rev = img.revision(id)

        if isdir( bpy.app.tempdir + 'imgt') == False :
            os.makedirs(bpy.app.tempdir + 'imgt')

        # source image not saved : save it in user temp
        if img.is_dirty :
            img.file_format = 'PNG'
            if '.' in name and name[name.rindex('.')+1:] in ['png','jpg','tga','dds','bmp','jp2'] :
                filename = name[:name.rindex('.')]
            else :
                filename = name
            img.filepath_raw = clean(bpy.app.tempdir + 'imgt/' + filename +'.png')
            img.save()

        # image.tmp slot is maybe missing (first creation)
        if name + '.tmp' not in bpy.data.images :
            tmpimg = img.copy()
            tmpimg.name = name + '.tmp'
        else : tmpimg = bpy.data.images[name + '.tmp']

        # retrieve path from revision or create
        if rev == False :
            rev = img.revision_add(id)

        # create file if missing
        if isfile(rev.path) == False :
            tmpimg.file_format = 'PNG'
            shutil.copy2(img.filepath_raw,rev.path)

        tmpimg.filepath_raw = rev.path

        return tmpimg
        

    def revision_add(self,id,path='') :
        img = self
        imtool = bpy.context.window_manager.imagetools
        new = imtool.tempset.add()
        new.created = _time.time()
        new.outdated = False
        new.name = img.revision_name(id)
        new.id = id
        new.source = id - 1
        if path == '' : new.path = img._tempath(id)
        else : new.path = path
        return new


    def revision_del(self) :
        img = self
        imtool = bpy.context.window_manager.imagetools
        lastid = img.revision_count() - 1
        rev = img.revision(lastid)
        actimg = active()
        if actimg and actimg.revision().id == lastid :
            if lastid > 0 :
                print(lastid - 1, img.temp(lastid - 1).name)
                actimg = img.temp(lastid - 1)
            else :
                actimg = bpy.data.images[rev.name[:-1]]
            actimg.show()
        if isfile(rev.path) : os.remove(rev.path)

        imtool.tempset.remove(rev.index())


    def revision_count(self) :
        img = self
        rev = img.revision()
        nextid = rev.id
        while rev :
            nextid += 1
            rev = img.revision(nextid)
        return nextid

    def _tempath(self,id) :
        img = self
        name = img.name.replace('.tmp','')
        if '.' in name and name[name.rindex('.')+1:] in ['png','jpg','tga','dds','bmp','jp2'] :
            filename = name[:name.rindex('.')]
        else :
            filename = name
        return clean(bpy.app.tempdir + 'imgt/'+ filename +'_' + str(id) + '.tmp.png')

    ## returns the source image of an image
    def original(self) :
        img = self
        id = img.tempid() - 1
        # user original image
        if id == -2 : return img
        elif id == -1 :
            return bpy.data.images[img.name.replace('.tmp','')]
        # tmp revision
        else :
            rev = img.revision(id)
            img.filepath_raw = rev.path
            return img
    '''
    ## enlarge and mirror existing on new 'X' or 'Y' area
    def mirror(img,dir='X') :
        dir = str(dir.upper())
        if dir not in ['X','Y'] :
            print("img.tools.rotate('180') (default) or '90' or '-90' and not %s..."%dir)
            return
        print('mirroring %s...'%img.name)
        s = _time.time()
        valuecount = len(img.pixels)
        sizex = newsizex = img.size[0]
        sizey = newsizey = img.size[1]
        srcvalues = list(img.pixels)
        cpyvalues = []
        injectvalues=[]
        for px in range(0,valuecount,4) : cpyvalues.append(srcvalues[px:px+4])

        pixelcount = valuecount / 4

        # rotate 180
        if dir == 'X' : newsizex = sizex * 2
        else : newsizey = sizey * 2

        print(sizex,sizey)
        print(newsizex,newsizey)
        
        newimg=bpy.data.images.new(name='_tmp_',width=newsizex,height=newsizey)
        
        if dir == 'X' :
            pxo = 0
            for row in range(sizey) :
                col = cpyvalues[pxo:pxo+sizex]
                for px in col :injectvalues.extend(px)
                col.reverse()
                for px in col :injectvalues.extend(px)
                pxo += sizex
        else :
            pxo = sizex * (sizey-1)
            while pxo >= 0 :
                col = cpyvalues[pxo:pxo+sizex]
                for px in col : injectvalues.extend(px)
                pxo -= sizex
            injectvalues.extend(srcvalues)

        newimg.pixels = injectvalues
        replace_image(img,newimg) 
        #print(sizex,sizey,img.name)
        #print(len(img.pixels),len(injectvalues))
        
        img.refreshPanel()
        
        print('done. (%.2f secs)'%(_time.time()-s))
    '''

    def refreshPanel(self,verbose=False):
        img, imged_id = checkUVpanels(verbose)
        if self == img and imged_id != -1 :
            bpy.context.screen.areas[imged_id].tag_redraw()

    def show(self):
        img, imged_id = checkUVpanels()
        if imged_id != -1 :
            bpy.context.screen.areas[imged_id].spaces[0].image = self
            bpy.context.screen.areas[imged_id].tag_redraw()

    def previous(self) :
        img = self.original()
        img.reload()
        img.show()
        return img

    def next(self) :
        img = self.temp()
        img.reload()
        img.show()
        return img

    def nconvert(self,args,temp = True) :
        img = self
        sce_path = img.filepath_raw
        if args != '' : args += ' -overwrite'
        if temp :
            tmpimg = img.temp()
            rev = tmpimg.revision()
            dest_path = rev.path
        else :
            tmpimg = img
            dest_path = sce_path

        #if temp and isfile(rev.path) :
        #    os.remove(rev.path)

        print('user command : %s'%(args))
        command = bpy.types.ImageTools.nconvert_path[1]['default']

        # bash and cmd react in different way when popen send the app arguments : http://bugs.python.org/issue6689
        #print(bpy.app.build_platform)
        if 'Window' in bpy.app.build_platform :
            #print('win command :')
            args = args.split(' ')
            for i in range(len(args)-1,-1,-1) :
                if args[i] == '' : del args[i]
            command = [ command ]
            command.extend(args)
            command.extend(['-out','png','-32bits','-clevel','9','-o',dest_path,sce_path])
            #print(command)
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            print(process.communicate()[0].decode(errors='replace'))

        else :
            #print('nux command :')
            command += args
            command += ' -out png -32bits -clevel 9 -o "%s" "%s"'%(dest_path,sce_path)
            command = command.replace('\\','/')
            #print(command)
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            print(process.communicate()[0].decode(errors='replace'))

        # nconvert succeeds
        if temp and isfile(rev.path) :
            rev.created = _time.time()
            rev.outdated = False
            previd = rev.id - 1
            prevrev = tmpimg.revision(previd)
            while prevrev :
                if prevrev.outdated or prevrev.created > rev.created :
                    rev.outdated = True
                    break
                previd -= 1
                #print('loop %s'%previd)
                prevrev = tmpimg.revision(previd)

            nextid = rev.id + 1
            nextrev = tmpimg.revision(nextid)
            while nextrev :
                nextrev.outdated = True
                nextid += 1
                nextrev = tmpimg.revision(nextid)
                
            tmpimg.reload()
            tmpimg.show()
            return tmpimg
        else :
            if temp :
                print('error')
            else :
                print('same')
                tmpimg.reload()
                tmpimg.show()
            return tmpimg

#############
## OPERATORS
#############

## calls from ui or bpy.ops
class OT_ImageNconvert(bpy.types.Operator):
    ''''''
    bl_idname = "image.nconvert"
    bl_label = "image convert"

    command = bpy.props.StringProperty('')

    def execute(self, context):
        if '/' in self.command :
            command,imgname = self.command.split('/')
            img = bpy.data.images(imgname)
        else :
            command = self.command
            img = active(True)
        if type(img) == bpy.types.Image :
            img.nconvert(command)
            return {'FINISHED'}
        return {'CANCELLED'}


class OT_ImageClipboard(bpy.types.Operator):
    ''''''
    bl_idname = "image.clipboard"
    bl_label = "image from clipboard"

    newslot = bpy.props.BoolProperty(default=False)

    def execute(self, context):
        img = clipboard(self.newslot)
        if type(img) == bpy.types.Image :
            img.show()
            return {'FINISHED'}
        return {'CANCELLED'}


class OT_ImagePrevious(bpy.types.Operator):
    ''''''
    bl_idname = "image.previous"
    bl_label = "image temp previous"

    def execute(self, context):
        img = active(True)
        if type(img) == bpy.types.Image :
            img.previous()
            return {'FINISHED'}
        return {'CANCELLED'}


class OT_ImageNext(bpy.types.Operator):
    ''''''
    bl_idname = "image.next"
    bl_label = "image temp next"

    def execute(self, context):
        img = active(True)
        if type(img) == bpy.types.Image :
            img.next()
            return {'FINISHED'}
        return {'CANCELLED'}

'''
class OT_ImageFlip(bpy.types.Operator):
    ''''''
    bl_idname = "image.flip"
    bl_label = "image flip"

    dir = bpy.props.StringProperty(default='X')

    def execute(self, context):
        img = active(True)
        if type(img) == bpy.types.Image :
            img.flip(self.dir)
            return {'FINISHED'}
        return {'CANCELLED'}


class OT_ImageRotate(bpy.types.Operator):
    ''''''
    bl_idname = "image.rotate"
    bl_label = "image rotate"

    dir = bpy.props.StringProperty(default='180')

    def execute(self, context):
        img = active(True)
        if type(img) == bpy.types.Image :
            img.rotate(self.dir)
            return {'FINISHED'}
        return {'CANCELLED'}


class OT_ImageMirror(bpy.types.Operator):
    ''''''
    bl_idname = "image.mirror"
    bl_label = "image mirror"

    dir = bpy.props.StringProperty(default='X')

    def execute(self, context):
        img = active(True)
        if type(img) == bpy.types.Image :
            img.mirror(self.dir)
            return {'FINISHED'}
        return {'CANCELLED'}


## proxies for space search tools
class OT_ImageFlipY(bpy.types.Operator):
    ''''''
    bl_idname = "image.flip_y"
    bl_label = "image flip (vertical)"

    def execute(self, context):
        bpy.ops.image.flip('EXEC_DEFAULT',dir='Y')
        return {'FINISHED'}


class OT_ImageRotateLeft(bpy.types.Operator):
    ''''''
    bl_idname = "image.rotate_left"
    bl_label = "image rotate left"

    def execute(self, context):
        bpy.ops.image.rotate('EXEC_DEFAULT',dir='-90')
        return {'FINISHED'}


class OT_ImageRotateRight(bpy.types.Operator):
    ''''''
    bl_idname = "image.rotate_right"
    bl_label = "image rotate right"

    def execute(self, context):
        bpy.ops.image.rotate('EXEC_DEFAULT',dir='+90')
        return {'FINISHED'}


class OT_ImageMirrorY(bpy.types.Operator):
    ''''''
    bl_idname = "image.rotate_right"
    bl_label = "image rotate right"

    def execute(self, context):
        bpy.ops.image.mirror('EXEC_DEFAULT',dir='Y')
        return {'FINISHED'}
'''

def register() :

        bpy.utils.register_class(ImageToolsTempSet)
        bpy.utils.register_class(ImageTools)
        bpy.utils.register_class(ImageTools_panel)


        bpy.utils.register_class(OT_ImageClipboard)
        bpy.utils.register_class(OT_ImagePrevious)
        bpy.utils.register_class(OT_ImageNext)

        bpy.utils.register_class(WM_OT_Panel_expand)
        #bpy.utils.register_class(OT_ImageFlip)
        #bpy.utils.register_class(OT_ImageFlipY)
        #bpy.utils.register_class(OT_ImageRotate)
        #bpy.utils.register_class(OT_ImageRotateLeft)
        #bpy.utils.register_class(OT_ImageRotateRight)
        #bpy.utils.register_class(OT_ImageMirror)
        #bpy.utils.register_class(OT_ImageMirrorY)
        #bpy.types.Image.tools = bpy.props.PointerProperty(type=ImageTools)
        bpy.utils.register_class(ImageTools_helpers)
        modal.register_modal()
        ImageTools.modal = bpy.props.PointerProperty(type=modal.ModalState)
        bpy.types.ModalState.bpy_instance_path.append('window_manager.imagetools.modal')
        ImageTools.helpers = bpy.props.PointerProperty(type=ImageTools_helpers)
        ImageTools.has_helpers = bpy.props.BoolProperty(default=True)#,is_hidden=True)

        bpy.types.WindowManager.imagetools = bpy.props.PointerProperty(type=ImageTools)

        # image collection methods
        #bpy.types.Image.rotate = ImageTools.rotate
        #bpy.types.Image.mirror = ImageTools.mirror
        #bpy.types.Image.flip = ImageTools.flip
        bpy.types.Image.temp = ImageTools.temp
        bpy.types.Image.original = ImageTools.original
        bpy.types.Image.revision = ImageTools.revision
        bpy.types.Image.revision_add = ImageTools.revision_add
        bpy.types.Image.revision_del = ImageTools.revision_del
        bpy.types.Image._tempath = ImageTools._tempath
        bpy.types.Image.revision_name = ImageTools.revision_name
        bpy.types.Image.revision_count = ImageTools.revision_count
        bpy.types.Image.nconvert = ImageTools.nconvert
        bpy.types.Image.previous = ImageTools.previous
        bpy.types.Image.next = ImageTools.next
        bpy.types.Image.tempid = ImageTools.tempid
        bpy.types.Image.refreshPanel = ImageTools.refreshPanel
        bpy.types.Image.show = ImageTools.show

def unregister() :

        ret = modal.unregister_modal()
        if type(ret) == str : return ret
    
        bpy.utils.unregister_class(ImageTools_panel)
        bpy.utils.unregister_class(ImageTools)
        bpy.utils.unregister_class(ImageToolsTempSet)
        bpy.utils.unregister_class(OT_ImageClipboard)
        bpy.utils.unregister_class(OT_ImagePrevious)
        bpy.utils.unregister_class(OT_ImageNext)

        bpy.utils.unregister_class(WM_OT_Panel_expand)
        #bpy.utils.unregister_class(OT_ImageFlip)
        #bpy.utils.unregister_class(OT_ImageFlipY)
        #bpy.utils.unregister_class(OT_ImageRotate)
        #bpy.utils.unregister_class(OT_ImageRotateLeft)
        #bpy.utils.unregister_class(OT_ImageRotateRight)
        #bpy.utils.unregister_class(OT_ImageMirror)
        #bpy.utils.unregister_class(OT_ImageMirrorY)
        bpy.utils.unregister_class(ImageTools_helpers)

        del bpy.types.WindowManager.imagetools
        #del bpy.types.Image.rotate
        #del bpy.types.Image.mirror
        #del bpy.types.Image.flip
        del bpy.types.Image.temp
        del bpy.types.Image.original
        del bpy.types.Image.revision
        del bpy.types.Image.revision_add
        del bpy.types.Image.revision_del
        del bpy.types.Image._tempath
        del bpy.types.Image.revision_name
        del bpy.types.Image.revision_count
        del bpy.types.Image.nconvert
        del bpy.types.Image.previous
        del bpy.types.Image.next
        del bpy.types.Image.tempid
        del bpy.types.Image.refreshPanel
        del bpy.types.Image.show
    
