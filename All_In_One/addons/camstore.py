# -*- coding: utf-8 -*-
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


bl_info = {
    "name": "Camstore",
    "version": (0, 4, 0),
    "blender": (2, 7, 9),  
    "category": "Learnbgame",
    "author": "Nikita Gorodetskiy",
    "location": "object",
    "description": "camera background changer",
    "warning": "not works for earlier versions",
    "wiki_url": "",          
    "tracker_url": "https://vk.com/sverchok_b3d",  
}

# Link for current addon on github:
# https://github.com/nortikin/nikitron_tools/blob/master/camstore.py


import bpy
import os
import re
import collections as co
from bpy.props import StringProperty, CollectionProperty, \
                        BoolProperty, PointerProperty, \
                        IntProperty




class SvBgImage(bpy.types.PropertyGroup):
    #screen = PointerProperty(type=bpy.types.Screen, name='screen')
    #area = PointerProperty(type=bpy.types.Area, name='area')
    object = PointerProperty(type=bpy.types.Object, name='object')
    image =  PointerProperty(type=bpy.types.Image, name='image')
    # because of bpy_struct type of type is not collected in pointer property, only ID
    # bg =     PointerProperty(type=bpy.types.BackgroundImage, name='bg')
    opened = BoolProperty(name='opened',default=False)



class OP_SV_bgimage_object_picker(bpy.types.Operator):
    bl_idname = 'image.sv_bgimage_object_picker'
    bl_label = "pick selected object"
    bl_description = "pick selected object as camera and create slot"
    bl_options = {'REGISTER'}

    item = IntProperty(name='item')

    def execute(self, context):
        bgobjects = context.scene.bgobjects
        bgobjects[self.item].object = context.selected_objects[0]
        context.space_data.camera = context.selected_objects[0]
        
        bgimages = context.space_data.background_images

        for bgims in bgimages:
            if bgims.image:
                if bgims.image.name == bgobjects[self.item].image.name:
                    bgims.show_background_image = True
                else:
                    bgims.show_background_image = False
        return {'FINISHED'}



class OP_SV_bgimage_remove(bpy.types.Operator):
    bl_idname = 'image.sv_bgimage_remove'
    bl_label = "remover of bgimages"
    bl_description = "remove bgimages"
    bl_options = {'REGISTER'}


    def execute(self, context):
        bgobjects = context.scene.bgobjects
        le = len(bgobjects)
        if bgobjects:
            for i,bgo in enumerate(bgobjects):
                bpy.data.images.remove(bgo.image)
                bpy.ops.image.sv_bgimage_rem_bgimage(item=-1-i)
        else:
            bpy.ops.image.sv_bgimage_remove_unused()
        for bgo in range(bgobjects):
            bgobjects.remove(0)
        self.report({'INFO'}, 'cleared all backgrounds')
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)



class OP_SV_bgimage_remove_unused(bpy.types.Operator):
    bl_idname = 'image.sv_bgimage_remove_unused'
    bl_label = "remover of unused bgimages"
    bl_description = "remove unused bgimages"
    bl_options = {'REGISTER'}



    def execute(self, context):
        areas = bpy.data.screens[context.screen.name].areas
        used = set()
        def rem_unused(space):
            bgimages = space.background_images
            bgobjects = context.scene.bgobjects
            # first check for existance of bgs
            if bgobjects:
                for bgo in bgobjects:
                    for bgi in bgimages:
                        if bgi.image:
                            if bgo.image == bgi.image:
                                used.add(bgi)
            print('camsetter - unused remover',used)
            for bg in bgimages:
                if bg not in used:
                    if bg.image:
                        name_for_delete = bg.image.name
                        bg.image.user_clear()
                    else:
                        name_for_delete = 'None'
                    print('image %s will be unnihilated' % name_for_delete)
                    bgimages.remove(bg)
            howmuch = []
            for bg in bgimages:
                if bg.image:
                    if bg.image.name not in howmuch:
                        howmuch.append(bg.image.name)
                    else:
                        bgimages.remove(bg)
        for ar in areas:
            if ar.type == 'VIEW_3D':
                rem_unused(ar.spaces[0])

        self.report({'INFO'}, 'cleared unused backgrounds')
        return {'FINISHED'}



class OP_SV_bgimage_new_slot(bpy.types.Operator):
    bl_idname = 'object.sv_bgimage_new_slot'
    bl_label = "new slot"
    bl_description = "new slot"
    bl_options = {'REGISTER'}

    filename_ext = ".jpg"
    filter_glob = StringProperty(default="*.jpg;*.png;*.tiff;*.jpeg;*.gif", options={'HIDDEN'})
    filepath = StringProperty(subtype="FILE_PATH")
    filename = StringProperty()
    files = CollectionProperty(name="File Path",type=bpy.types.OperatorFileListElement)
    directory = StringProperty(subtype='DIR_PATH')

    

    def execute(self, context):
        '''
        Главная добавляющая функция
        '''
        obj = context.object
        bpy.ops.view3d.object_as_camera()
        bgobjects = context.scene.bgobjects
        bgimages = context.space_data.background_images
        bgob = bgobjects.add()
        bgob.object = obj
        # if len(bpy.data.images):
        bpy.ops.image.open(filepath=self.filepath, \
                            directory=self.directory, \
                            show_multiview=False)
        name = os.path.split(self.filepath)[1]
        bgob.image = bpy.data.images[name]
        bgi = bgimages.new()
        bgi.image = bgob.image
        for bgims in bgimages:
            bgims.show_background_image = False
        bgi.show_background_image = True
        bgi.view_axis = 'CAMERA'
        bgi.draw_depth = 'FRONT'

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class OP_SV_bgimage_setcamera(bpy.types.Operator):
    '''Set camera active bg. Main function, acts as initiation'''
    bl_idname = "image.sv_bgimage_set_camera"
    bl_label = "Open image"
    bl_description = "activate gbimage"
    bl_options = {'REGISTER'}

    item = IntProperty(name='item')


    def areas_set(self, context, space):
        bgimages = space.background_images
        bgobjects = context.scene.bgobjects
        item= self.item
        bgobject = bgobjects[item]
        im = False
        # first check for existance of bgs
        for bgi in bgimages:
            #print(bgi.image.name)
            if bgi.image:
                if bgi.image.name == bgobject.image.name:
                    print('image %s switched, not created + %s' % (bgobject.image.name, bgi.image.name))
                    bgi.show_background_image = True
                    im = True
                    space.camera = bgobject.object
                else:
                    bgi.show_background_image = False
        if not im:
            print('image %s not switched, created' % (bgobject.image.name))
            newbgimage = bgimages.new()
            space.camera = bgobject.object
            newbgimage.image = bgobject.image

    def execute(self, context):
        '''
        Сделать задник, если его нет.
        '''
        areas = bpy.data.screens[context.screen.name].areas
        if not context.space_data.lock_camera_and_layers:
            # if you work in not locked self space
            self.areas_set(context, context.space_data)
            print('NOT LOCKED CAMERA, changed only current 3d view camera backgrounds')
            return {'FINISHED'}
        else:
            # if you work with locked self space
            for ar in areas:
                if ar.type == 'VIEW_3D':
                    #if ar.spaces[0] == context.space_data:
                    #    self.areas_set(context, ar.spaces[0])
                    if ar.spaces[0].lock_camera_and_layers: #not own space data, but VIEW_3D
                        self.areas_set(context, ar.spaces[0])
        
                    
        return {'FINISHED'}



class OP_SV_bgimage_rem_bgimage(bpy.types.Operator):
    '''Removes background object with linked image for camera'''
    bl_idname = "image.sv_bgimage_rem_bgimage"
    bl_label = "Rem bgimage"
    bl_description = "Remove background image"
    bl_options = {'REGISTER'}

    item = IntProperty(name='item')
    im = BoolProperty(name='im', default=False)

    def rem_backgroundimage(self, bgobjects, space):
        bgimages = space.background_images
        item = self.item
        bgobject = bgobjects[item]
        # first check for existance of bgs
        for bgi in bgimages:
            #print(bgi.image.name)
            if bgi.image and bgobject.image:
                if bgi.image.name == bgobject.image.name:
                    print('image %s removed + %s' % (bgobject.image.name, bgi.image.name))
                    bgimages.remove(bgi)
                    self.im = True

    def execute(self, context):
        areas = bpy.data.screens[context.screen.name].areas
        bgobjects = context.scene.bgobjects
        item = self.item
        for ar in areas:
            if ar.type == 'VIEW_3D':
                self.rem_backgroundimage(bgobjects, ar.spaces[0])
        if not self.im:
            print('impossible thing - we canot remove item under index', str(item))
            # bgobjects[item].image1
        print('remove item under index', str(item))
        bgobjects.remove(item)
        return {'FINISHED'}



class OP_SV_bgimage_front_back(bpy.types.Operator):
    '''Set image in front or back'''
    bl_idname = "image.sv_bgimage_front_back"
    bl_label = "front back"
    bl_description = "set bg image to front or back"
    bl_options = {'REGISTER'}

    item = IntProperty(name='item')
    fb = BoolProperty(name='frontback', default=False)

    def fbact(self, bgobjects, space):
        bgimages = space.background_images
        item = self.item
        bgobject = bgobjects[item]
        # first check for existance of bgs
        for bgi in bgimages:
            if bgi.image and bgobject.image:
                if bgi.image.name == bgobject.image.name:
                    if self.fb:
                        bgi.draw_depth = 'FRONT'
                    else:
                        bgi.draw_depth = 'BACK'

    def execute(self, context):
        areas = bpy.data.screens[context.screen.name].areas
        bgobjects = context.scene.bgobjects
        item = self.item
        for ar in areas:
            if ar.type == 'VIEW_3D':
                self.fbact(bgobjects, ar.spaces[0])
        return {'FINISHED'}



class OP_SV_bgimage_load_images(bpy.types.Operator):
    '''Load images from file directory'''
    bl_idname = "object.sv_bgimage_load_images"
    bl_label = "load"
    bl_description = "load ALL images named as camera data names (i.e. 01.jpg) in current directory"
    bl_options = {'REGISTER'}


    filename_ext = ".jpg"
    filter_glob = StringProperty(default="*.jpg;*.png;*.tiff;*.jpeg;*.gif", options={'HIDDEN'})
    filepath = StringProperty(subtype="FILE_PATH")
    filename = StringProperty()
    files = CollectionProperty(name="File Path",type=bpy.types.OperatorFileListElement)
    directory = StringProperty(subtype='DIR_PATH')

    

    def execute(self, context):
        '''
        Функция добавления файлов из текучей директории,
        соответствующих по названиям камерам
        '''
        obj = bpy.data.cameras
        bpy.ops.view3d.object_as_camera()
        bgobjects = context.scene.bgobjects
        bgimages = context.space_data.background_images
        images = bpy.data.images
        if context.blend_data.is_saved:
            path = context.blend_data.filepath
            self.directory = os.path.split(path)[0]
        else:
            return {'FINISHED'}
        # if len(bpy.data.images):
        for cam in obj:
            file = ''.join(re.split(r'_',cam.name))
            filepath = os.path.join(self.directory,file)
            self.filepath = filepath
            if not cam.name in os.listdir(self.directory):
                continue
            bpy.ops.image.open(filepath=filepath, directory=self.directory, \
                               files=[{"name":file, "name":file}], \
                               relative_path=False, show_multiview=False)
            #print('WHATA ',im)
            bgob = bgobjects.add()
            for o in bpy.data.objects:
                if o.data.name == cam.name:
                    # if break, than o left as fitted object, not changed
                    break
            bgob.object = o #bpy.data.objects[cam.name]
            bgob.image = bpy.data.images[cam.name]
            bgi = bgimages.new()
            bgi.image = bgob.image

        for bgims in bgimages:
            bgims.show_background_image = False
        bgi.show_background_image = True
        bgi.view_axis = 'CAMERA'
        bgi.draw_depth = 'FRONT'

        return {'FINISHED'}

# needed only for interactive
#    def invoke(self, context, event):
#        context.window_manager.fileselect_add(self)
#        return {'RUNNING_MODAL'}



class VIEW3D_PT_camera_bgimages2(bpy.types.Panel):
    bl_label = "Camstore"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = '1D'



    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        main = context.scene

        def basic_panel(col):
            row = col.row(align=True)
            if main.bgimage_panel:
                row.prop(main, 'bgimage_panel', text="Be carefull", icon='DOWNARROW_HLT')
            else:
                row.prop(main, 'bgimage_panel', text="Basics", icon='RIGHTARROW')
            if main.bgimage_panel:
                row = col.row(align=True)
                row.operator("image.sv_bgimage_remove", text='all', icon='X')
                row.operator("image.sv_bgimage_remove_unused", text='unused', icon='X')
                row.prop(context.space_data,'show_background_images',text='Activate',expand=True,toggle=True)
                col.prop(main,'bgimage_preview', text='Preview',expand=True,toggle=True, icon='RESTRICT_VIEW_OFF')

        def main_panel(col):
            col.operator('object.sv_bgimage_load_images', text='Load All', icon='FILE_FOLDER')
            col.operator('object.sv_bgimage_new_slot', text='New', icon='ZOOMIN')
            for ind,bgo in enumerate(context.scene.bgobjects):
                row = col.row(align=True)
                if bgo.opened:
                    row.prop(bgo, 'opened', text='', icon='TRIA_DOWN')
                    try:
                        if bgo.object:
                            row.label(text=bgo.object.name)
                        row.operator('image.sv_bgimage_object_picker', text='', icon='RESTRICT_SELECT_OFF').item = ind
                        if bgo.image:
                            row.operator('image.sv_bgimage_set_camera', text='', icon='RESTRICT_VIEW_OFF').item = ind
                        row.operator('image.sv_bgimage_rem_bgimage', text='', icon='X').item = ind
                    except:
                        row.label(text='error')
                    cam = bgo.object
                    img = bgo.image
                    col.prop(bgo, "object")
                    #col.template_ID(bgo, "object", open="camera.open")

                    ####### BACK // FRONT
                    row = col.row(align=True)
                    fb = row.operator('image.sv_bgimage_front_back',text='Back')
                    fb.item = ind
                    fb.fb = False
                    fb = row.operator('image.sv_bgimage_front_back',text='Front')
                    fb.item = ind
                    fb.fb = True
                    for bi in context.area.spaces[0].background_images:
                        if bi.image == bgo.image:
                            col.prop(bi,'opacity',text='opacity')
                    if not main.bgimage_preview:
                        col.template_ID(bgo, 'image',open="image.open")
                else:
                    row.prop(bgo, 'opened', text='', icon='TRIA_RIGHT')
                    try:
                        if bgo.object:
                            row.label(text=bgo.object.name)
                        row.operator('image.sv_bgimage_object_picker', text='',icon='RESTRICT_SELECT_OFF').item = ind
                        if bgo.image:
                            row.operator('image.sv_bgimage_set_camera', text='',icon='RESTRICT_VIEW_OFF').item = ind
                        row.operator('image.sv_bgimage_rem_bgimage', text='',icon='X').item = ind
                    except:
                        row.label(text='error')
                if context.scene.bgimage_preview:
                    col.template_ID_preview(bgo, 'image',open="image.open", rows=2, cols=3)

        def debug_panel(col):
            row = col.row(align=True)
            if main.bgimage_debug:
                row.prop(main, 'bgimage_debug', text="Debug", icon='DOWNARROW_HLT')
            else:
                row.prop(main, 'bgimage_debug', text="Debug", icon='RIGHTARROW')


            if main.bgimage_debug:
                col.label(text='EXISTING BGIMAGESETS:')
                box = col.box()
                col2 = box.column(align=True)
                col2.scale_y=0.5
                row = col2.row(align=True)
                row.label(text='# IMAGE')
                row.label(text='OBJECT')
                for Y,bgo in enumerate(main.bgobjects):
                    row = col2.row(align=True)
                    if bgo.image:
                        row.label(text=str(Y)+' '+bgo.image.name)
                    else:
                        row.label(text=str(Y)+' None')
                    if bgo.object:
                        row.label(text=bgo.object.name)
                    else:
                        row.label(text='None')
                col.label(text='EXISTING BACKGROUNDS:')
                box = col.box()
                col2 = box.column(align=True)
                col2.scale_y=0.5
                row = col2.row(align=True)
                row.label(text='# IMAGE')
                for Y,bgs_existing in enumerate(context.space_data.background_images):
                    row = col2.row(align=True)
                    if bgs_existing.image:
                        row.label(text=str(Y)+' '+bgs_existing.image.name)
                    else:
                        row.label(text=str(Y)+' None')
        basic_panel(col)
        main_panel(col)
        debug_panel(col)



def register():
    bpy.types.Scene.bgimage_panel = BoolProperty(
                                name="show main panel",
                                description="",
                                default = False)
    bpy.types.Scene.bgimage_preview = BoolProperty(
                                name="preview_images",
                                description="",
                                default = False)
    bpy.types.Scene.bgimage_debug = BoolProperty(
                                name="debug",
                                description="",
                                default = False)
    bpy.utils.register_class(SvBgImage)
    bpy.types.Scene.bgobjects = CollectionProperty(type=SvBgImage)
    bpy.utils.register_class(VIEW3D_PT_camera_bgimages2)
    bpy.utils.register_class(OP_SV_bgimage_setcamera)
    bpy.utils.register_class(OP_SV_bgimage_new_slot)
    bpy.utils.register_class(OP_SV_bgimage_load_images)
    bpy.utils.register_class(OP_SV_bgimage_remove)
    bpy.utils.register_class(OP_SV_bgimage_remove_unused)
    bpy.utils.register_class(OP_SV_bgimage_rem_bgimage)
    bpy.utils.register_class(OP_SV_bgimage_object_picker)
    bpy.utils.register_class(OP_SV_bgimage_front_back)


def unregister():
    bpy.utils.unregister_class(OP_SV_bgimage_front_back)
    bpy.utils.unregister_class(OP_SV_bgimage_object_picker)
    bpy.utils.unregister_class(OP_SV_bgimage_rem_bgimage)
    bpy.utils.unregister_class(OP_SV_bgimage_remove_unused)
    bpy.utils.unregister_class(OP_SV_bgimage_remove)
    bpy.utils.unregister_class(OP_SV_bgimage_load_images)
    bpy.utils.unregister_class(OP_SV_bgimage_new_slot)
    bpy.utils.unregister_class(OP_SV_bgimage_setcamera)
    bpy.utils.unregister_class(VIEW3D_PT_camera_bgimages2)
    bpy.context.scene.bgobjects.clear()
    try:
        del bpy.types.Scene.bgobjects
        del bpy.types.Scene.bgimage_panel
        del bpy.types.Scene.bgimage_preview
        del bpy.types.Scene.bgimage_debug
    except:
        pass
    bpy.utils.unregister_class(SvBgImage)

if __name__ == '__main__':
    register()
    '''
    #test
    for k,i in enumerate(bpy.data.images):
        bpy.context.scene.bgobjects.add()
        bpy.context.scene.bgobjects[-1].object = bpy.context.object
        bpy.context.scene.bgobjects[-1].image = i
    for k,t in enumerate(bpy.context.scene.bgobjects):
        print(t.object, t.image)
    '''

