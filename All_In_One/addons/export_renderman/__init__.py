
#Blender 2.5 or later to Renderman Exporter
# Copyright (C) 2011 Sascha Fricke



#############################################################################################
#                                                                                           #
#       Begin GPL Block                                                                     #
#                                                                                           #
#############################################################################################
#                                                                                           #
#This program is free software;                                                             #
#you can redistribute it and/or modify it under the terms of the                            #
#GNU General Public License as published by the Free Software Foundation;                   #
#either version 3 of the LicensGe, or (at your option) any later version.                   #
#                                                                                           #
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;  #
#without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  #
#See the GNU General Public License for more details.                                       #
#                                                                                           #
#You should have received a copy of the GNU General Public License along with this program; #
#if not, see <http://www.gnu.org/licenses/>.                                                #
#                                                                                           #
#############################################################################################
#                                                                                           #
#       End GPL Block                                                                       #
#                                                                                           #
############################################################################################

#Thanks to: Campbell Barton, Eric Back, Nathan Vegdahl

##################################################################################################################################


bl_info = {
    'name': 'Renderman',
    'author': 'Sascha Fricke',
    'version': '0.01',
    'blender': (2, 5, 6),
    'location': 'Info Header',
    'description': 'Connects Blender to Renderman Interface',
    "category": "Learnbgame",
}
    
##################################################################################################################################
if "bpy" in locals():
    import imp
    imp.reload(rm_props)
    imp.reload(ops)
    imp.reload(ui)
    #imp.reload(export_renderman.export)
else:
    import export_renderman.rm_props
    from export_renderman import rm_props
    from export_renderman import ops
    from export_renderman import ui
    from export_renderman import export
    from export_renderman.export import *

import bpy
import os
import subprocess
import math
import mathutils
import tempfile
import time

##################################################################################################################################

from bl_ui import properties_data_mesh
from bl_ui import properties_data_camera
from bl_ui import properties_data_lamp
from bl_ui import properties_texture
from bl_ui import properties_particle
from bl_ui import properties_render

#properties_render.RENDER_PT_render.COMPAT_ENGINES.add('RENDERMAN')
properties_render.RENDER_PT_dimensions.COMPAT_ENGINES.add('RENDERMAN')
#properties_render.RENDER_PT_output.COMPAT_ENGINES.add('RENDERMAN')
#properties_render.RENDER_PT_post_processing.COMPAT_ENGINES.add('RENDERMAN')
properties_data_mesh.DATA_PT_context_mesh.COMPAT_ENGINES.add('RENDERMAN')
#properties_data_mesh.DATA_PT_settings.COMPAT_ENGINES.add('RENDERMAN')
properties_data_mesh.DATA_PT_vertex_groups.COMPAT_ENGINES.add('RENDERMAN')
properties_data_mesh.DATA_PT_shape_keys.COMPAT_ENGINES.add('RENDERMAN')
properties_data_mesh.DATA_PT_uv_texture.COMPAT_ENGINES.add('RENDERMAN')
properties_data_camera.DATA_PT_context_camera.COMPAT_ENGINES.add('RENDERMAN')
properties_data_camera.DATA_PT_camera_display.COMPAT_ENGINES.add('RENDERMAN')
properties_data_lamp.DATA_PT_context_lamp.COMPAT_ENGINES.add('RENDERMAN')

for member in dir(properties_texture):
    subclass = getattr(properties_texture, member)
    exceptions = [  "", "Colors", "Influence", "Mapping", 
                    "Image Sampling", "Image Mapping", 
                    "Environment Map Sampling", "Custom Properties",
                    "Preview", "Environment Map"]
    try:
        if not subclass.bl_label in exceptions:
            subclass.COMPAT_ENGINES.add('RENDERMAN')
    except:
        pass

for member in dir(properties_particle):
    subclass = getattr(properties_particle, member)
    exceptions = ['Render', 'Children']
    try:
        if not subclass.bl_label in exceptions:
            subclass.COMPAT_ENGINES.add('RENDERMAN')
    except:
        pass
            
del properties_texture
del properties_data_mesh
del properties_data_camera
del properties_data_lamp

##################################################################################################################################
#checking folders and creating them if necessary

def checkpaths(folderpath):
    if os.path.exists(folderpath):
        fullofcrap = True
        dir = folderpath
        while fullofcrap:
            if not os.path.exists(dir):
                fullofcrap = False
                break
            if os.listdir(dir):
                for item in os.listdir(dir):
                    if os.path.isfile(os.path.join(dir, item)):
                        os.remove(os.path.join(dir, item))
                    elif os.path.isdir(os.path.join(dir, item)):
                        dir = os.path.join(folderpath, item)
            else:
                os.rmdir(dir)
                dir = folderpath
    os.mkdir(folderpath)


##################################################################################################################################
##################################################################################################################################

##################################################################################################################################

##################################################################################################################################


#########################################################################################################
#                                                                                                       #
#       R E N D E R                                                                                     #
#                                                                                                       #
#########################################################################################################
preview_scene = False

def checksize(img):
    size = -1

    ready = False
    while not ready:
        if size != os.path.getsize(img):
            size = os.path.getsize(img)
        else:
            ready = True
            break

        time.sleep(1)
    return 0

def rm_shellscript(cmd, rm):
    if rm.shellscript_create:
        ssfile = rm.shellscript_file
    if not rm.shellscript_append or not os.path.exists(ssfile):
        file = open(ssfile, "w")
    elif rm.shellscript_append and os.path.exists(ssfile):
        file = open(ssfile, "a")
    file.write(cmd+'\n')
    file.close()

update_counter = 0
class RendermanRender(bpy.types.RenderEngine):
    bl_idname = 'RENDERMAN'
    bl_label = "Renderman"
    #bl_use_preview = True
    update = 50
    
    def rm_start_render(self, render, ribfile, current_pass, scene):
        rd = scene.render
        x = int(rd.resolution_x * rd.resolution_percentage)*0.01
        y = int(rd.resolution_y * rd.resolution_percentage)*0.01
        
        self.update_stats("", "Render ... "+current_pass.name)
    
        if current_pass.displaydrivers:
            print("Render .. "+current_pass.name)
            print(render + ' ' + ribfile)
            
            renderprocess = subprocess.Popen([render, ribfile], cwd=getdefaultribpath(scene))
           
            def image(name): return name.replace("[frame]", framepadding(scene))    

            def update_image(image):
                result = self.begin_result(0, 0, x, y)
              
                layer = result.layers[0]
                
                try:
                    layer.load_from_file(image)
                except:
                    print("can't load image")
                self.end_result(result)

            if (current_pass.renderresult != ""
                and current_pass.displaydrivers[current_pass.renderresult].displaydriver != "framebuffer"):
                img = image(current_pass.displaydrivers[current_pass.renderresult].file)
                
                while not os.path.exists(img):
                    if os.path.exists(img):
                        break                 
                   
                    if self.test_break():
                        try:
                            renderprocess.terminate()
                        except:
                            renderprocess.kill()
            
                    if renderprocess.poll() == 0:
                        self.update_stats("", "Error: Check Console")
                        break            
                                      
                prev_size = -1
                ready = False
               
                dbprint("all image files created, now load them", lvl=2, grp="renderprocess")
                dbprint("renderprocess finished?", renderprocess.poll(), lvl=2, grp="renderprocess")
                while True:
                    dbprint("Rendering ...", lvl=2, grp="renderprocess")
                    update_image(img)
#                            if renderprocess.poll():
#                                print("Finished")
#                                self.update_stats("", "Finished")
#                                update_image(layname, image)
#                                break
    
                    if self.test_break():
                        dbprint("aborting rendering", lvl=2, grp="renderprocess")
                        try:
                            renderprocess.terminate()
                        except:
                            renderprocess.kill()
                        break
              
                    if renderprocess.poll() == 0:
                        dbprint("renderprocess terminated", lvl=2, grp="renderprocess")
                        break
              
                    if os.path.getsize(img) != prev_size:
                        prev_size = os.path.getsize(img) 
                        update_image(img)                                                               
                            
            ## until the render api is fixed, load all images manually in the image editor
            try:
                for disp in current_pass.displaydrivers:
                    img = image(disp.file)
                    if not disp.displaydriver == "framebuffer":
                        if not img in bpy.data.images:
                            try:
                                imgpath = os.path.join(getdefaultribpath(scene), img)
                                bpy.data.images.load(image(imgpath))
                            except RuntimeError:
                                print("can't load image", imgpath)
                        else: bpy.data.images[img].update()
            except SystemError:
                pass

    def check_objects(self, scene):
        abort = False
        for obj in scene.objects:
            if obj.type == "LAMP" and len(obj.data.renderman) == 0:
                printmsg = "Light: "+obj.name+" has no Render Pass, cancel Rendering ..."
                self.update_stats("", printmsg)
                print(printmsg)
                abort = True
            elif obj.type == "MESH" and len(obj.renderman) == 0:
                printmsg = "Object: "+obj.name+" has no Render Pass, cancel Rendering ..."
                self.update_stats("", printmsg)
                print(printmsg)
                abort = True
        return abort

    def render(self, scene):
        rm = scene.renderman_settings
        rs = rm.rib_structure
        print("Start Rendering ...")
        if scene.name == "preview":
            global update_counter
            update_counter += 1
            if update_counter < self.update:
                return
            update_counter = 0
            mat, rndr = preview_mat()
            matrm = mat.renderman[mat.renderman_index]

            rmprdir = bpy.utils.preset_paths("renderman")[0]
            if not bpy.utils.preset_paths("renderman")[0]:
                return
            mat_preview_path = os.path.join(rmprdir, "material_previews")
            if matrm.preview_scene == "":
                return
            previewdir = os.path.join(mat_preview_path, matrm.preview_scene)
            previewdir_materialdir = os.path.join(previewdir, "Materials")
            mat_archive_file = os.path.join(previewdir_materialdir, "preview_material.rib")
            mat_archive = Archive(data_path=mat, filepath=mat_archive_file, scene=scene)
            print(mat.name)
            writeMaterial(mat, mat_archive=mat_archive, active_matpass=True)
            ribfile = os.path.join(previewdir, "material_preview.rib")
            renderprocess = subprocess.Popen([rndr, ribfile])  

            def update_image(image):
                result = self.begin_result(0, 0, 128, 128)
              
                layer = result.layers[0]
                try:
                    layer.load_from_file(image)
                    loaded = True
                except SystemError:
                    loaded = False
                self.end_result(result)
                return loaded

            img = os.path.join(previewdir, "material_preview.tiff")
            
            while not os.path.exists(img):
                if os.path.exists(img):
                    break                 
        
                if renderprocess.poll() == 0:
                    break            

            while not renderprocess.poll() == 0:
                update_image(img)
            update_image(img)

            
        else:
            if self.check_objects(scene):
                print("1")
                return
            rndr = scene.renderman_settings.renderexec
            if rndr == "":
                print("2")
                return
            
            projectFile = getname(rs.frame.filename,
                            scene=scene,
                            frame=framepadding(scene))+'.rib'
            
            filepath = os.path.join(getdefaultribpath(scene), projectFile)
                    
            active_pass = getactivepass(scene)
    
            global exported_instances, base_archive

            print("Export RIB Archives to:", filepath)
            base_archive = Archive(data_path=scene, type="Frame", scene=scene, filepath=filepath)
    
            if scene.renderman_settings.exportallpasses:
                for item in scene.renderman_settings.passes:
                    if item.export:
                        imagefolder = os.path.join(getdefaultribpath(scene), item.imagedir)
                        checkForPath(imagefolder)
                        export(item, scene)
                close_all()

                if not scene.renderman_settings.exportonly:
                    self.rm_start_render(rndr, projectFile, item, scene)
                    check_disps_processing(item, scene)
                else:
                    rndr_cmd = rndr + ' "'+base_archive.filepath+'"'
                    rm_shellscript(rndr_cmd, rm)
            else:
                export(active_pass, scene)
                close_all()
                imagefolder = os.path.join(path, active_pass.imagedir)
                checkpaths(imagefolder)
                if not scene.renderman_settings.exportonly:
                   self.rm_start_render(rndr, projectFile, active_pass, scene)
                   check_disps_processing(active_pass, scene)
                else:
                    rndr_cmd = rndr + ' "'+base_archive.filepath+'"'
                    rm_shellscript(rndr_cmd, rm)

##################################################################################################################################

##################################################################################################################################

##################################################################################################################################
##################################################################################################################################


def registerRenderCallbacks(sce=None):
    bpy.app.handlers.render_pre.append(maintain_render_passes)
    bpy.app.handlers.render_pre.append(initPasses)
    bpy.app.handlers.render_pre.append(maintain_client_passes_remove)
    bpy.app.handlers.render_pre.append(maintain_textures)

def removeRenderCallbacks(sce=None):
    bpy.app.handlers.render_pre.remove(maintain_render_passes)
    bpy.app.handlers.render_pre.remove(initPasses)
    bpy.app.handlers.render_pre.remove(maintain_client_passes_remove)
    bpy.app.handlers.render_pre.remove(maintain_textures)


##################################################################################################################################

def register():
    rm_props.register()
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_MT_object_specials.append(ui.draw_obj_specials_rm_menu)
    bpy.types.INFO_MT_add.append(ui.draw_rm_add_light)
    registerRenderCallbacks()
    bpy.app.handlers.load_post.append(registerRenderCallbacks)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.VIEW3D_MT_object_specials.remove(ui.draw_obj_specials_rm_menu)
    bpy.types.INFO_MT_add.remove(ui.draw_rm_add_light)
    removeRenderCallbacks()
    bpy.app.handlers.load_post.remove(registerRenderCallbacks)

if __name__ == "__main__":
    register()
