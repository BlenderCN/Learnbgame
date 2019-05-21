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
    "name": "Camera backgrounder/Задники камеры",
    "version": (0, 1, 0),
    "blender": (2, 7, 9),  
    "category": "Camera",
    "author": "Nikita Gorodetskiy",
    "location": "object",
    "description": "camera background changer",
    "warning": "",
    "wiki_url": "",          
    "tracker_url": "http://www.blenderartists.org/forum/showthread.php?272679-Addon-WIP-Sverchok-parametric-tool-for-architects",  
}



import bpy
from bpy.props import StringProperty, CollectionProperty, \
                        BoolProperty
import os



class OP_SV_bgimage_remove(bpy.types.Operator):
    bl_idname = 'image.sv_bgimage_remove'
    bl_label = "remover of bgimages"
    bl_description = "remove gbimages"
    bl_options = {'REGISTER'}


    def execute(self, context):
        a = context.space_data.background_images
        obs = bpy.data.cameras
        for i in a:
            bpy.data.images[i.image.name].user_clear()
            a.remove(i)
        for o in obs:
            bpy.data.objects[o.name].bgimage = ''
        self.report({'INFO'}, 'cleared all backgrounds')
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)



class OP_SV_bgimage_remove_unused(bpy.types.Operator):
    bl_idname = 'image.sv_bgimage_remove_unused'
    bl_label = "remover of unused bgimages"
    bl_description = "remove unused gbimages"
    bl_options = {'REGISTER'}


    def execute(self, context):
        a = context.space_data.background_images
        obs = bpy.data.cameras
        obj = bpy.data.objects
        used = []
        for i in a:
            for o in obs:
                if i.image.name == obj[o.name].bgimage:
                    used.append(i.image.name)
        for i in a:
            if i.image.name not in used:
                bpy.data.images[i.image.name].user_clear()
                a.remove(i)

        self.report({'INFO'}, 'cleared unused backgrounds')
        return {'FINISHED'}



class OP_SV_bgimage_delete(bpy.types.Operator):
    bl_idname = 'image.sv_bgimage_delete'
    bl_label = "deleter of exact bgimage"
    bl_description = "delete gbimage"
    bl_options = {'REGISTER'}

    camera = StringProperty(name='camera')


    def execute(self, context):
        a = context.space_data.background_images
        cams = bpy.data.cameras
        objs = bpy.data.objects
        for i in a:
            if i.image.name == objs[self.camera]:
                bpy.data.images[i.image.name].user_clear()
                a.remove(i)
        objs[self.camera].bgimage = ''
        return {'FINISHED'}



class OP_SV_bgimage_cameraset(bpy.types.Operator):
    bl_idname = 'object.sv_bgimage_cameraset'
    bl_label = "camerasetter"
    bl_description = "set camera"
    bl_options = {'REGISTER'}

    camera = StringProperty(name='camera')


    def execute(self, context):
        context.scene.camera = bpy.data.objects[self.camera]

        bgim = bpy.data.objects[self.camera].bgimage
        bgimages = context.space_data.background_images
        if bgim:
            for bgi in bgimages:
                if bgi.image.name == bgim:
                    #print(bgi.image.name, bgim)
                    bgi.show_background_image = True
                else:
                    bgi.show_background_image = False
        else:
            for bgi in bgimages:
                print('noimage',bgi.show_background_image)
                bgi.show_background_image = False

        return {'FINISHED'}



class OP_SV_bgimage_bgimageset(bpy.types.Operator):
    bl_idname = 'image.sv_bgimage_bgimageset'
    bl_label = "bgimagesetter"
    bl_description = "set bg image"
    bl_options = {'REGISTER'}

    camera = StringProperty(name='camera')


    def execute(self, context):
        context.scene.camera = bpy.data.objects[self.camera]
        bgimages = context.space_data.background_images
        for bgi in bgimages:
            bgi.show_background_image = False
        bginame = bpy.data.objects[self.camera].bgimage
        bgi = context.space_data.background_images.new()
        bgi.image = bpy.data.images[bginame]


        return {'FINISHED'}

''' help for future text:
        for t in text:
            context.scene.mp_playlist.add()
            context.scene.mp_playlist[-1].playlist = t
'''

class OP_SV_bgimage_show(bpy.types.Operator):
    '''!!!!! Not active operator !!!!!'''
    bl_idname = 'image.sv_bgimage_show'
    bl_label = "shower of bgimage"
    bl_description = "show gbimage"
    bl_options = {'REGISTER'}

    camera = StringProperty(name='camera')


    def execute(self, context):
        for b in context.space_data.background_images:
            del(b)
        if not bpy.data.objects[self.camera].bgimage:
            bg = bpy.data.images.new(name=self.camera, width=1, height=1) #context.space_data.background_images.new()
        else:
            bg = bpy.data.images[self.camera]
        #print(dir(bg.image))
        bpy.data.objects[self.camera].bgimage = bg.name
        #row.template_ID(bg, "image", open="image.open")
        #c.bgimage = bg.name
        #context.screen.areas[2].spaces[0].background_images[0].show_background_image
        #for image in context.space_data.background_images:
        #    if not image.show_background_image:
        #        image.show_background_image = True
        #    else:
        #        image.show_background_image = False
                
        return {'FINISHED'}



class OP_SV_bgimage_import(bpy.types.Operator):
    '''Open image File'''
    bl_idname = "image.sv_bgimage_open"
    bl_label = "Open image"
    bl_description = "open gbimage"
    bl_options = {'REGISTER'}

    filename_ext = ".jpg"
    filter_glob = StringProperty(default="*.jpg;*.png;*.jpeg;*.tif;*.bmp;*.avi", options={'HIDDEN'})
    filepath = StringProperty(subtype="FILE_PATH")
    filename = StringProperty()
    files = CollectionProperty(name="File Path",type=bpy.types.OperatorFileListElement)
    directory = StringProperty(subtype='DIR_PATH')
    camera = StringProperty(name="camera")

    
    def execute(self, context):
        print('got an image called',self.filename)
        if self.files :
            bgimages = context.space_data.background_images
            for bgi in bgimages:
                bgi.show_background_image = False
                
            for sfile in self.files:
                path = os.path.join(self.directory + sfile.name)
                bg = bpy.ops.image.open(filepath=path)
                bpy.data.objects[self.camera].bgimage = sfile.name
            newbgimage = context.space_data.background_images.new()
            newbgimage.image = bpy.data.images[sfile.name]
        context.scene.camera = bpy.data.objects[self.camera]
        self.report({'INFO'}, 'new image '+sfile.name)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}



class VIEW3D_PT_camera_bgimages(bpy.types.Panel):
    bl_label = "Backgrounds / Задники"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = '1D'

    #bgimages = StringProperty(name='bgimages')#EnumProperty(items=[('','','')], 
    #                #description='existing background images')


    def draw(self, context):
        layout = self.layout

        #bpy.data.images['camera']
        #bg = context.space_data.background_images['camera']
        col = layout.column(align=True)
        
        #col.split(percentage=0.1, align=False)
        main = context.scene
        row = col.row(align=True)
        #split = row.split(percentage=0.15)
        if main.bgimage_panel:
            row.prop(main, 'bgimage_panel', text="Be carefull!", icon='DOWNARROW_HLT')
        else:
            row.prop(main, 'bgimage_panel', text="Basics", icon='RIGHTARROW')
        if main.bgimage_panel:
            row = col.row(align=True)
            row.operator("image.sv_bgimage_remove", text='clear all')
            row.operator("image.sv_bgimage_remove_unused", text='clear unused')
            row.prop(bpy.context.space_data,'show_background_images',text='ACTIVE',expand=True,toggle=True)
        col.label(text='  ')
        box = col.column(align=True)
        for c in bpy.data.cameras:
            row = box.row(align=True)
            imname = bpy.data.objects[c.name].bgimage
            #row.prop(bpy.data.objects, "lock_object", text="")
            if context.space_data.camera == bpy.data.objects[c.name]:
                row.label(text='V '+c.name)
            else:
                row.operator("object.sv_bgimage_cameraset", text=c.name).camera = c.name
                #row.label(text='. '+c.name)
            if imname:
                #row.template_ID(bpy.data.images, bpy.data.objects[c.name].bgimage, open="image.open")

                #tex = context.texture
                #layout.template_image(tex, "image", tex.image_user)

                row.operator("image.sv_bgimage_delete", text='',icon='X').camera = c.name
                row.label(text=bpy.data.objects[c.name].bgimage)
                bgimages = context.space_data.background_images
                imagebgexists = False
                for bgi in bgimages:
                    if bgi.image.name == imname:
                        imagebgexists = True
                        
                        row = box.row(align=True)
                        #row.scale_y=0.7
                        row.prop(bgi,'opacity',text='Opacity',expand=True,toggle=True)
                        row.prop(bgi,'show_on_foreground',text='',expand=True,toggle=True,icon='IMAGE_ZDEPTH')
                        box.label(text=' ')

                        #row.template_ID(bgi, "image", open="image.open")
                        #row.template_ID_preview(bgi, 'image',open="image.open", rows=2, cols=3)
                if not imagebgexists:
                    row.operator("image.sv_bgimage_bgimageset", text='',icon='TEXTURE').camera = c.name
                        
            else:
                row.prop_search(
                                bpy.data.objects[c.name], 'bgimage', 
                                #context.space_data, 'background_images', text='', icon='FILE_IMAGE')
                                bpy.data, 'images', text='', icon='FILE_IMAGE')
                row.operator("image.sv_bgimage_open", text='',icon='FILE_FOLDER').camera = c.name
                #row.operator()
                #row.operator('objects.sv_bgimage_show', text='image?').camera = c.name


 
                #for ima in bpy.data.images:
                #    if c.bgimage == ima.name: 
                        #row.label(text=c.bgimage)
                        #row.template_ID(bpy.data.images[c.bgimage], "image", open="image.open")
                        #camimage = True
                        #break
                #if not camimage:
                #row.label(text='Noimage')

class SvBgImage(bpy.types.PropertyGroup):
    object = bpy.props.PointerProperty(type=bpy.types.Object, name='object')
    bgimage = bpy.props.PointerProperty(type=bpy.types.Image, name='image')


def register():
    bpy.types.Scene.bgimage_panel = BoolProperty(
                                name="show main panel",
                                description="",
                                default = False)
    #bpy.types.Object.bgobjects = 
    bpy.types.Object.bgimage = bpy.props.StringProperty()
    bpy.utils.register_class(OP_SV_bgimage_bgimageset)
    bpy.utils.register_class(OP_SV_bgimage_cameraset)
    bpy.utils.register_class(OP_SV_bgimage_delete)
    bpy.utils.register_class(OP_SV_bgimage_remove)
    bpy.utils.register_class(OP_SV_bgimage_remove_unused)
    bpy.utils.register_class(OP_SV_bgimage_import)
    bpy.utils.register_class(OP_SV_bgimage_show)
    bpy.utils.register_class(VIEW3D_PT_camera_bgimages)


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_camera_bgimages)
    bpy.utils.unregister_class(OP_SV_bgimage_show)
    bpy.utils.unregister_class(OP_SV_bgimage_import)
    bpy.utils.unregister_class(OP_SV_bgimage_remove_unused)
    bpy.utils.unregister_class(OP_SV_bgimage_remove)
    bpy.utils.unregister_class(OP_SV_bgimage_delete)
    bpy.utils.unregister_class(OP_SV_bgimage_cameraset)
    bpy.utils.unregister_class(OP_SV_bgimage_bgimageset)

if __name__ == '__main__':
    register()