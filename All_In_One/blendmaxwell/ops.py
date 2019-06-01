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

import os
import shlex
import subprocess
import math
import random
import uuid

import bpy
from bpy.props import PointerProperty, FloatProperty, IntProperty, BoolProperty, StringProperty, EnumProperty, FloatVectorProperty, IntVectorProperty
from bpy.types import Operator
from mathutils import Vector, Color, Matrix
from bl_operators.presets import AddPresetBase
from bpy_extras.io_utils import ImportHelper, ExportHelper
import bgl

from . import maths
from . import system
from . import impmxs
from . import export
from .log import LOG_FILE_PATH


class ImportMXS(Operator, ImportHelper):
    bl_idname = "maxwell_render.import_mxs"
    bl_label = 'Import MXS'
    bl_description = 'Import Maxwell Render Scene (.MXS)'
    
    filename_ext = ".mxs"
    filter_glob = StringProperty(default="*.mxs", options={'HIDDEN'}, )
    keep_intermediates = BoolProperty(name="Keep Intermediates", description="Keep intermediate products", default=False, )
    check_extension = True
    
    emitters = BoolProperty(name="Emitters", default=True, )
    objects = BoolProperty(name="Objects", default=True, )
    cameras = BoolProperty(name="Cameras", default=True, )
    sun = BoolProperty(name="Sun (as Sun Lamp)", default=True, )
    
    def draw(self, context):
        l = self.layout
        
        sub = l.column()
        r = sub.row()
        r.prop(self, 'emitters')
        if(self.objects):
            r.active = False
        sub.prop(self, 'objects')
        sub.prop(self, 'cameras')
        sub.prop(self, 'sun')
        
        if(system.PLATFORM == 'Darwin'):
            l.separator()
            l.prop(self, 'keep_intermediates')
    
    def execute(self, context):
        if(not self.objects and not self.cameras and not self.sun and not self.emitters):
            return {'CANCELLED'}
        
        d = {'mxs_path': os.path.realpath(bpy.path.abspath(self.filepath)),
             'emitters': self.emitters,
             'objects': self.objects,
             'cameras': self.cameras,
             'sun': self.sun, }
        if(system.PLATFORM == 'Darwin'):
            d['keep_intermediates'] = self.keep_intermediates
            im = impmxs.MXSImportMacOSX(**d)
        elif(system.PLATFORM == 'Linux' or system.PLATFORM == 'Windows'):
            im = impmxs.MXSImportWinLin(**d)
        else:
            pass
        
        return {'FINISHED'}
    
    @classmethod
    def register(cls):
        bpy.types.INFO_MT_file_import.append(menu_func_import)
    
    @classmethod
    def unregister(cls):
        bpy.types.INFO_MT_file_import.remove(menu_func_import)


class ExportMXS(Operator, ExportHelper):
    bl_idname = "maxwell_render.export_mxs"
    bl_label = 'Export MXS'
    bl_description = 'Export Maxwell Render Scene (.MXS)'
    
    filename_ext = ".mxs"
    filter_glob = StringProperty(default="*.mxs", options={'HIDDEN'}, )
    check_extension = True
    
    open_with = EnumProperty(name="Open With", items=[('STUDIO', "Studio", ""), ('MAXWELL', "Maxwell", ""), ('NONE', "None", "")], default='STUDIO', description="After export, open in ...", )
    open_log = BoolProperty(name="Open Log", default=False, description="Open export log in text editor when finished", )
    use_instances = BoolProperty(name="Instances", description="Export multi-user meshes and dupliverts as instances.", default=True, )
    keep_intermediates = BoolProperty(name="Keep Intermediates", description="Keep intermediate products", default=False, )
    
    def draw(self, context):
        l = self.layout
        
        sub = l.column()
        sub.prop(self, 'open_with')
        sub.prop(self, 'open_log')
        sub.prop(self, 'use_instances')
        
        if(system.PLATFORM == 'Darwin'):
            sub.separator()
            sub.prop(self, 'keep_intermediates')
    
    def execute(self, context):
        p = bpy.path.abspath(self.filepath)
        ex = export.MXSExport(mxs_path=p, )
        
        from .log import NUMBER_OF_WARNINGS, copy_paste_log
        if(NUMBER_OF_WARNINGS > 0):
            self.report({'ERROR'}, "There was {} warnings during export. Check log file for details.".format(NUMBER_OF_WARNINGS))
        if(self.open_log):
            h, t = os.path.split(p)
            n, e = os.path.splitext(t)
            u = ex.uuid
            log_file_path = os.path.join(h, '{}-export_log-{}.txt'.format(n, u))
            copy_paste_log(log_file_path)
            system.open_file_in_default_application(log_file_path)
        
        if(ex is not None):
            bpy.ops.maxwell_render.open_mxs(filepath=ex.mxs_path, application=self.open_with, instance_app=False, )
        
        return {'FINISHED'}
    
    @classmethod
    def register(cls):
        bpy.types.INFO_MT_file_export.append(menu_func_export)
    
    @classmethod
    def unregister(cls):
        bpy.types.INFO_MT_file_export.remove(menu_func_export)


def menu_func_import(self, context):
    self.layout.operator(ImportMXS.bl_idname, text="Maxwell Render Scene (.mxs)")


def menu_func_export(self, context):
    self.layout.operator(ExportMXS.bl_idname, text="Maxwell Render Scene (.mxs)")


class EnvironmentSetSun(Operator):
    bl_idname = "maxwell_render.set_sun"
    bl_label = "Set Sun Location Vector"
    bl_description = "Set direction from selected Sun lamp"
    
    @classmethod
    def poll(cls, context):
        o = context.active_object
        return (o and o.type == 'LAMP' and o.data.type == 'SUN')
    
    def execute(self, context):
        m = context.world.maxwell_render
        s = context.active_object
        w = s.matrix_world
        _, r, _ = w.decompose()
        v = Vector((0, 0, 1))
        v.rotate(r)
        m.sun_dir_x = v.x
        m.sun_dir_y = v.y
        m.sun_dir_z = v.z
        return {'FINISHED'}


class EnvironmentNow(Operator):
    bl_idname = "maxwell_render.now"
    bl_label = "Now"
    bl_description = "Set current date and time"
    
    def execute(self, context):
        import datetime
        
        m = context.world.maxwell_render
        d = m.sun_date
        t = m.sun_time
        n = datetime.datetime.now()
        m.sun_date = n.strftime('%d.%m.%Y')
        m.sun_time = n.strftime('%H:%M')
        return {'FINISHED'}


class CameraAutoFocus(Operator):
    bl_idname = "maxwell_render.auto_focus"
    bl_label = "Auto Focus"
    bl_description = "Auto focus camera to closest object in the middle of camera"
    
    @classmethod
    def poll(cls, context):
        o = context.active_object
        return (o and o.type == 'CAMERA')
    
    def execute(self, context):
        s = context.scene
        c = context.active_object
        mw = c.matrix_world
        d = 1000000.0
        e, t, u = maths.eye_target_up_from_matrix(mw, d)
        a = e.copy()
        b = maths.shift_vert_along_normal(a, t, d)
        
        # blender 2.77 api change
        # hit, _, _, loc, _ = s.ray_cast(a, b)
        if bpy.app.version < (2, 77, 0):
            hit, _, _, loc, _ = s.ray_cast(a, b)
        else:
            hit, loc, _, _, _, _ = s.ray_cast(a, b)
        
        if(hit):
            c.data.dof_distance = maths.distance_vectors(a, loc)
        else:
            self.report({'WARNING'}, "No object to focus to..")
            return {'CANCELLED'}
        return {'FINISHED'}


class CameraSetRegion(Operator):
    bl_idname = "maxwell_render.camera_set_region"
    bl_label = "Render Border > Region"
    bl_description = "Copy render border (x, y, width, height) to render region"
    
    def execute(self, context):
        rp = context.scene.render
        x_res = int(rp.resolution_x * rp.resolution_percentage / 100.0)
        y_res = int(rp.resolution_y * rp.resolution_percentage / 100.0)
        x = int(x_res * rp.border_min_x)
        h = y_res - int(y_res * rp.border_min_y)
        w = int(x_res * rp.border_max_x)
        y = y_res - int(y_res * rp.border_max_y)
        m = context.camera.maxwell_render
        m.screen_region_x = x
        m.screen_region_y = y
        m.screen_region_w = w
        m.screen_region_h = h
        return {'FINISHED'}


class CameraResetRegion(Operator):
    bl_idname = "maxwell_render.camera_reset_region"
    bl_label = "Reset Region"
    bl_description = "Reset render region"
    
    def execute(self, context):
        rp = context.scene.render
        w = int(rp.resolution_x * rp.resolution_percentage / 100.0)
        h = int(rp.resolution_y * rp.resolution_percentage / 100.0)
        rp.border_min_x = 0
        rp.border_min_y = 0
        rp.border_max_x = w
        rp.border_max_y = h
        m = context.camera.maxwell_render
        m.screen_region_x = 0
        m.screen_region_y = 0
        m.screen_region_w = w
        m.screen_region_h = h
        rp.use_border = False
        return {'FINISHED'}


class CreateMaterial(Operator):
    bl_idname = "maxwell_render.create_material"
    bl_label = "Create Material"
    bl_description = "Create new .MXM and open it in Mxed material editor"
    
    filepath = StringProperty(subtype='FILE_PATH', )
    filename_ext = ".mxm"
    check_extension = True
    check_existing = BoolProperty(name="", default=True, options={'HIDDEN'}, )
    remove_dots = True
    
    filter_folder = BoolProperty(name="Filter folders", default=True, options={'HIDDEN'}, )
    filter_glob = StringProperty(default="*.mxm", options={'HIDDEN'}, )
    
    backface = BoolProperty(name="", default=False, options={'HIDDEN'}, )
    
    force_preview = BoolProperty(name="Force Preview", default=True, )
    force_preview_scene = StringProperty(name="Force Preview Scene", default="", )
    
    @classmethod
    def poll(cls, context):
        return (context.material or context.object)
    
    def invoke(self, context, event):
        n = context.material.name
        if(self.remove_dots):
            # remove dots, Maxwell doesn't like it - material name is messed up..
            n = n.replace(".", "_")
        if(self.backface):
            self.filepath = os.path.join(context.scene.maxwell_render.materials_directory, "{}_backface.mxm".format(n))
        else:
            self.filepath = os.path.join(context.scene.maxwell_render.materials_directory, "{}.mxm".format(n))
        self.force_preview = context.material.maxwell_render.force_preview
        self.force_preview_scene = context.material.maxwell_render.force_preview_scene
        if(self.force_preview_scene == ' '):
            self.force_preview_scene = ''
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def check(self, context):
        change_ext = False
        check_extension = self.check_extension
        
        if(check_extension is not None):
            filepath = self.filepath
            
            if(self.remove_dots):
                h, t = os.path.split(filepath)
                n, e = os.path.splitext(t)
                n = n.replace(".", "_")
                filepath = os.path.join(h, "{}{}".format(n, e))
            
            if(os.path.basename(filepath)):
                filepath = bpy.path.ensure_ext(filepath,
                                               self.filename_ext
                                               if check_extension
                                               else "")
                if(filepath != self.filepath):
                    self.filepath = filepath
                    change_ext = True
        return change_ext
    
    def execute(self, context):
        p = os.path.abspath(bpy.path.abspath(self.filepath))
        
        if(p == ""):
            self.report({'ERROR'}, "Filepath is empty")
            return {'CANCELLED'}
        if(os.path.isdir(p)):
            self.report({'ERROR'}, "Filepath is directory")
            return {'CANCELLED'}
        
        h, t = os.path.split(p)
        n, e = os.path.splitext(t)
        if(e.lower() != ".mxm"):
            self.report({'ERROR'}, "Extension is not .mxm")
            return {'CANCELLED'}
        
        if(not os.path.exists(os.path.dirname(p))):
            self.report({'ERROR'}, "Directory does not exist")
            return {'CANCELLED'}
        
        if(not os.access(os.path.dirname(p), os.W_OK)):
            self.report({'ERROR'}, "Directory is not writeable")
            return {'CANCELLED'}
        
        system.mxed_create_material_helper(p, self.force_preview, self.force_preview_scene, )
        
        rp = bpy.path.relpath(self.filepath)
        if(system.PLATFORM == 'Windows'):
            rp = os.path.abspath(self.filepath)
        
        if(self.backface):
            context.object.maxwell_render.backface_material_file = rp
        else:
            context.material.maxwell_render.mxm_file = rp
        return {'FINISHED'}


class BrowseMaterial(Operator):
    bl_idname = "maxwell_render.browse_material"
    bl_label = "Browse With Mxed"
    bl_description = "Open Mxed in browser mode to select material"
    
    @classmethod
    def poll(cls, context):
        return (context.material or context.object)
    
    def execute(self, context):
        p = system.mxed_browse_material_helper()
        m = context.material
        mx = m.maxwell_render
        
        if(p is not None):
            ok = False
            if(os.path.exists(p)):
                h, t = os.path.split(p)
                n, e = os.path.splitext(t)
                if(e.lower() == '.mxm'):
                    ok = True
                else:
                    self.report({'ERROR'}, "Not a .MXM file: '{}'".format(p))
            else:
                self.report({'ERROR'}, "File does not exist: '{}'".format(p))
            
            if(not ok):
                return {'CANCELLED'}
            
            mx.use = 'REFERENCE'
            
            rp = bpy.path.relpath(p)
            if(system.PLATFORM == 'Windows'):
                rp = os.path.abspath(p)
            
            mx.mxm_file = rp
            
            # change something to force preview redraw
            m.preview_render_type = 'FLAT'
            m.preview_render_type = 'SPHERE'
            
            return {'FINISHED'}
        else:
            return {'CANCELLED'}


class EditMaterial(Operator):
    bl_idname = "maxwell_render.edit_material"
    bl_label = "Edit Material"
    bl_description = "Edit current material in Mxed material editor"
    
    backface = BoolProperty(name="", default=False, options={'HIDDEN'}, )
    
    @classmethod
    def poll(cls, context):
        return (context.material or context.object)
    
    def execute(self, context):
        if(self.backface):
            p = os.path.abspath(bpy.path.abspath(context.object.maxwell_render.backface_material_file))
        else:
            p = os.path.abspath(bpy.path.abspath(context.material.maxwell_render.mxm_file))
        
        if(p == ""):
            self.report({'ERROR'}, "Filepath is empty")
            return {'CANCELLED'}
        if(os.path.isdir(p)):
            self.report({'ERROR'}, "Filepath is directory")
            return {'CANCELLED'}
        
        h, t = os.path.split(p)
        n, e = os.path.splitext(t)
        if(e.lower() != ".mxm"):
            self.report({'ERROR'}, "Extension is not .mxm")
            return {'CANCELLED'}
        
        if(not os.path.exists(os.path.dirname(p))):
            self.report({'ERROR'}, "Directory does not exist")
            return {'CANCELLED'}
        
        if(not os.access(os.path.dirname(p), os.W_OK)):
            self.report({'ERROR'}, "Directory is not writeable")
            return {'CANCELLED'}
        
        f = context.material.maxwell_render.force_preview
        fs = context.material.maxwell_render.force_preview_scene
        if(fs == ' '):
            fs = ''
        system.mxed_edit_material_helper(p, f, fs, )
        
        return {'FINISHED'}


class EditExtensionMaterial(Operator):
    bl_idname = "maxwell_render.edit_extension_material"
    bl_label = "Edit Extension Material in Mxed"
    bl_description = "Create new extension .MXM and open it in Mxed material editor"
    
    filepath = StringProperty(subtype='FILE_PATH', )
    filename_ext = ".mxm"
    check_extension = True
    check_existing = BoolProperty(name="", default=True, options={'HIDDEN'}, )
    remove_dots = True
    
    filter_folder = BoolProperty(name="Filter folders", default=True, options={'HIDDEN'}, )
    filter_glob = StringProperty(default="*.mxm", options={'HIDDEN'}, )
    
    backface = BoolProperty(name="", default=False, options={'HIDDEN'}, )
    
    force_preview = BoolProperty(name="Force Preview", default=True, )
    force_preview_scene = StringProperty(name="Force Preview Scene", default="", )
    
    @classmethod
    def poll(cls, context):
        return (context.material or context.object)
    
    def invoke(self, context, event):
        n = context.material.name
        if(self.remove_dots):
            # remove dots, Maxwell doesn't like it - material name is messed up..
            n = n.replace(".", "_")
        if(self.backface):
            self.filepath = os.path.join(context.scene.maxwell_render.materials_directory, "{}_backface.mxm".format(n))
        else:
            self.filepath = os.path.join(context.scene.maxwell_render.materials_directory, "{}.mxm".format(n))
        self.force_preview = context.material.maxwell_render.force_preview
        self.force_preview_scene = context.material.maxwell_render.force_preview_scene
        if(self.force_preview_scene == ' '):
            force_preview_scene = ''
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def check(self, context):
        change_ext = False
        check_extension = self.check_extension
        
        if(check_extension is not None):
            filepath = self.filepath
            
            if(self.remove_dots):
                h, t = os.path.split(filepath)
                n, e = os.path.splitext(t)
                n = n.replace(".", "_")
                filepath = os.path.join(h, "{}{}".format(n, e))
            
            if(os.path.basename(filepath)):
                filepath = bpy.path.ensure_ext(filepath,
                                               self.filename_ext
                                               if check_extension
                                               else "")
                if(filepath != self.filepath):
                    self.filepath = filepath
                    change_ext = True
        return change_ext
    
    def execute(self, context):
        p = os.path.abspath(bpy.path.abspath(self.filepath))
        
        if(p == ""):
            self.report({'ERROR'}, "Filepath is empty")
            return {'CANCELLED'}
        if(os.path.isdir(p)):
            self.report({'ERROR'}, "Filepath is directory")
            return {'CANCELLED'}
        
        h, t = os.path.split(p)
        n, e = os.path.splitext(t)
        if(e.lower() != ".mxm"):
            self.report({'ERROR'}, "Extension is not .mxm")
            return {'CANCELLED'}
        
        if(not os.path.exists(os.path.dirname(p))):
            self.report({'ERROR'}, "Directory does not exist")
            return {'CANCELLED'}
        
        if(not os.access(os.path.dirname(p), os.W_OK)):
            self.report({'ERROR'}, "Directory is not writeable")
            return {'CANCELLED'}
        
        mat = export.MXSMaterialExtension(context.material.name)
        d = mat._repr()
        
        path = system.mxed_create_and_edit_ext_material_helper(p, d, self.force_preview, self.force_preview_scene, )
        
        m = context.material.maxwell_render
        m.use = 'REFERENCE'
        m.mxm_file = path
        
        return {'FINISHED'}


class OpenMXS(Operator):
    bl_idname = "maxwell_render.open_mxs"
    bl_label = "Open MXS"
    bl_description = ""
    
    filepath = StringProperty(name="Filepath", subtype='FILE_PATH', options={'HIDDEN'}, )
    application = EnumProperty(name="Application", items=[('STUDIO', "Studio", ""), ('MAXWELL', "Maxwell", ""), ('NONE', "", ""), ], default='STUDIO', options={'HIDDEN'}, )
    instance_app = BoolProperty(name="Open a new instance", default=False, )
    
    def execute(self, context):
        if(self.application == 'NONE'):
            return {'FINISHED'}
        
        p = os.path.abspath(bpy.path.abspath(self.filepath))
        
        if(p == ""):
            self.report({'ERROR'}, "Filepath is empty")
            return {'CANCELLED'}
        if(os.path.isdir(p)):
            self.report({'ERROR'}, "Filepath is directory")
            return {'CANCELLED'}
        
        h, t = os.path.split(p)
        n, e = os.path.splitext(t)
        if(e.lower() != ".mxs"):
            self.report({'ERROR'}, "Extension is not .mxs")
            return {'CANCELLED'}
        
        if(self.application == 'STUDIO'):
            system.studio_open_mxs_helper(p, self.instance_app)
        elif(self.application == 'MAXWELL'):
            system.maxwell_open_mxs_helper(p, self.instance_app)
        else:
            self.report({'ERROR'}, "Unknown application")
            return {'CANCELLED'}
        
        return {'FINISHED'}


class CopyActiveObjectPropertiesToSelected(Operator):
    bl_idname = "maxwell_render.copy_active_object_properties_to_selected"
    bl_label = "Copy Active Object Properties To Selected"
    bl_description = "Copy active object properties from active object to selected."
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        ob = context.active_object
        allowed = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'ARMATURE', 'LATTICE', 'EMPTY', 'LAMP', 'SPEAKER', ]
        if(ob.type not in allowed):
            return False
        obs = context.selected_objects
        return (ob and len(obs) > 0)
    
    def execute(self, context):
        allowed = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'ARMATURE', 'LATTICE', 'EMPTY', 'LAMP', 'SPEAKER', ]
        obs = context.selected_objects
        src = context.active_object.maxwell_render
        for o in obs:
            if(o.type in allowed):
                m = o.maxwell_render
                m.opacity = src.opacity
                m.hidden_camera = src.hidden_camera
                m.hidden_camera_in_shadow_channel = src.hidden_camera_in_shadow_channel
                m.hidden_global_illumination = src.hidden_global_illumination
                m.hidden_reflections_refractions = src.hidden_reflections_refractions
                m.hidden_zclip_planes = src.hidden_zclip_planes
                m.object_id = src.object_id
                m.backface_material = src.backface_material
                
                m.hide = src.hide
                m.override_instance = src.override_instance
                
                m.movement = src.movement
                m.deformation = src.deformation
                m.custom_substeps = src.custom_substeps
                m.substeps = src.substeps
                
        return {'FINISHED'}


class SetObjectIdColor(Operator):
    bl_idname = "maxwell_render.set_object_id_color"
    bl_label = "Set Object ID Color"
    bl_description = "Set Object ID to red/green/blue/white/black to all selected objects."
    bl_options = {'REGISTER', 'UNDO'}
    
    color = EnumProperty(name="Color", items=[('0', "Red", ""), ('1', "Green", ""), ('2', "Blue", ""), ('3', "White", ""), ('4', "Black", "")], default='0', description="", )
    
    @classmethod
    def poll(cls, context):
        obs = context.selected_objects
        return (len(obs) > 0)
    
    def execute(self, context):
        allowed = ['MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'ARMATURE', 'LATTICE', 'EMPTY', 'LAMP', 'SPEAKER', ]
        obs = context.selected_objects
        src = context.active_object.maxwell_render
        for o in obs:
            if(o.type in allowed):
                m = o.maxwell_render
                if(self.color == '0'):
                    c = (1.0, 0.0, 0.0, )
                elif(self.color == '1'):
                    c = (0.0, 1.0, 0.0, )
                elif(self.color == '2'):
                    c = (0.0, 0.0, 1.0, )
                elif(self.color == '3'):
                    c = (1.0, 1.0, 1.0, )
                else:
                    c = (0.0, 0.0, 0.0, )
                m.object_id = c
        return {'FINISHED'}


class BlockedEmitterAdd(Operator):
    bl_idname = "maxwell_render.blocked_emitter_add"
    bl_label = "Blocked Emitter Add"
    bl_options = {'INTERNAL', 'UNDO'}
    
    name = StringProperty(name="Name", )
    remove = BoolProperty(name="Remove", )
    
    def execute(self, context):
        o = context.object
        be = o.maxwell_render.blocked_emitters
        es = be.emitters
        i = be.index
        if(self.remove):
            try:
                es.remove(i)
                if(i >= len(es)):
                    be.index = i - 1
            except Exception as e:
                self.report(type={'WARNING'}, message=str(e), )
        else:
            i = len(es)
            e = es.add()
            e.name = self.name
            be.index = i
        return {'FINISHED'}


class BpyOpsMaterialNewOverride(Operator):
    bl_idname = "maxwell_render.material_new_override"
    bl_label = "Add a new material"
    bl_description = "Add a new material"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        # it is not drawn (clickable) when it can't be used right?
        return True
    
    def execute(self, context):
        bpy.ops.material.new()
        
        mat = context.object.active_material
        mx = mat.maxwell_render
        
        prefs = system.prefs()
        t = prefs.default_new_material_type
        if(mx.use != t):
            mx.use = t
        
        if(mx.use == 'CUSTOM'):
            # add layer with bsdf
            cl = mx.custom_layers
            ls = cl.layers
            idx = cl.index
            auto_bsdf = True
            
            item = ls.add()
            item.id = len(ls)
            item.name = 'Layer {}'.format(len(ls))
            cl.index = (len(ls) - 1)
            if(auto_bsdf):
                b = item.layer.bsdfs.bsdfs.add()
                b.id = len(ls)
                b.name = 'BSDF 1'
                item.layer.bsdfs.index = 0
        
        return {'FINISHED'}


class BpyOpsWorldNewOverride(Operator):
    bl_idname = "maxwell_render.world_new_override"
    bl_label = "Add a new world"
    bl_description = "Add a new world"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        # it is not drawn (clickable) when it can't be used right?
        return True
    
    def execute(self, context):
        bpy.ops.world.new()
        
        w = context.scene.world
        mx = w.maxwell_render
        
        prefs = system.prefs()
        t = prefs.default_new_world_type
        if(mx.env_type != t):
            mx.env_type = t
        
        return {'FINISHED'}


class BpyOpsObjectParticleSystemAddOverride(Operator):
    bl_idname = "maxwell_render.particle_system_add_override"
    bl_label = "Add a particle system"
    bl_description = "Add a particle system"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        # it is not drawn (clickable) when it can't be used right?
        return True
    
    def execute(self, context):
        bpy.ops.object.particle_system_add()
        
        o = context.object
        ps = o.particle_systems.active
        mx = ps.settings.maxwell_render
        
        prefs = system.prefs()
        t = prefs.default_new_particles_type
        if(mx.use != t):
            mx.use = t
        
        return {'FINISHED'}


class MaterialEditorAddLayer(Operator):
    bl_idname = "maxwell_render.material_editor_add_layer"
    bl_label = "Add New Layer"
    bl_description = "Add new layer"
    bl_options = {'REGISTER', 'UNDO'}
    
    auto_bsdf = BoolProperty(name="auto_bsdf", default=True, options={'HIDDEN'}, )
    add_to_top = BoolProperty(name="add_to_top", default=True, options={'HIDDEN'}, )
    
    def execute(self, context, ):
        mx = context.material.maxwell_render
        cl = mx.custom_layers
        ls = cl.layers
        idx = cl.index
        
        item = ls.add()
        item.id = len(ls)
        item.name = 'Layer {}'.format(len(ls))
        cl.index = (len(ls) - 1)
        
        if(self.auto_bsdf):
            b = item.layer.bsdfs.bsdfs.add()
            b.id = len(ls)
            b.name = 'BSDF 1'
            item.layer.bsdfs.index = 0
        
        if(self.add_to_top):
            while(cl['index'] != 0):
                bpy.ops.maxwell_render.material_editor_move_layer_up()
        
        return {'FINISHED'}


class MaterialEditorRemoveLayer(Operator):
    bl_idname = "maxwell_render.material_editor_remove_layer"
    bl_label = "Remove Selected Layer"
    bl_description = "Remove selected layer"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mx = context.material.maxwell_render
        cl = mx.custom_layers
        ls = cl.layers
        idx = cl.index
        try:
            item = ls[idx]
        except IndexError:
            return {'CANCELLED'}
        
        cl.index -= 1
        ls.remove(idx)
        if(idx == 0):
            cl.index = idx
        if(len(ls) == 0):
            cl.index = -1
        
        return {'FINISHED'}


class MaterialEditorMoveLayerUp(Operator):
    bl_idname = "maxwell_render.material_editor_move_layer_up"
    bl_label = "Move Selected Layer Up"
    bl_description = "Move selected layer up"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mx = context.material.maxwell_render
        cl = mx.custom_layers
        ls = cl.layers
        idx = cl.index
        try:
            item = ls[idx]
        except IndexError:
            return {'CANCELLED'}
        
        if(idx >= 1):
            mv = idx - 1
            ls.move(mv, idx, )
            cl.index = mv
            return {'FINISHED'}
        
        return {'PASS_THROUGH'}


class MaterialEditorMoveLayerDown(Operator):
    bl_idname = "maxwell_render.material_editor_move_layer_down"
    bl_label = "Move Selected Layer Down"
    bl_description = "Move selected layer down"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mx = context.material.maxwell_render
        cl = mx.custom_layers
        ls = cl.layers
        idx = cl.index
        try:
            item = ls[idx]
        except IndexError:
            return {'CANCELLED'}
        
        if(idx < len(ls) - 1):
            mv = idx + 1
            ls.move(idx, mv, )
            cl.index = mv
            return {'FINISHED'}
        
        return {'PASS_THROUGH'}


class MaterialEditorCloneLayer(Operator):
    bl_idname = "maxwell_render.material_editor_clone_layer"
    bl_label = "Clone Selected Layer"
    bl_description = "Clone selected layer"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mx = context.material.maxwell_render
        cl = mx.custom_layers
        ls = cl.layers
        idx = cl.index
        try:
            item = ls[idx]
        except IndexError:
            return {'CANCELLED'}
        
        d = cl['layers'][cl.index].to_dict()
        bpy.ops.maxwell_render.material_editor_add_layer()
        cl['layers'][cl.index].update(d)
        n = cl['layers'][cl.index]['name']
        cl['layers'][cl.index]['name'] = 'Clone of {}'.format(n)
        
        return {'FINISHED'}


class MaterialEditorAddBSDF(Operator):
    bl_idname = "maxwell_render.material_editor_add_bsdf"
    bl_label = "Add New BSDF"
    bl_description = "Add new BSDF"
    bl_options = {'REGISTER', 'UNDO'}
    
    add_to_top = BoolProperty(name="add_to_top", default=True, options={'HIDDEN'}, )
    
    def execute(self, context):
        mx = context.material.maxwell_render
        l = mx.custom_layers.layers[mx.custom_layers.index]
        cl = l.layer.bsdfs
        ls = l.layer.bsdfs.bsdfs
        idx = l.layer.bsdfs.index
        
        item = ls.add()
        item.id = len(ls)
        item.name = 'BSDF {}'.format(len(ls))
        cl.index = (len(ls) - 1)
        
        if(self.add_to_top):
            while(cl['index'] != 0):
                bpy.ops.maxwell_render.material_editor_move_bsdf_up()
        
        return {'FINISHED'}


class MaterialEditorRemoveBSDF(Operator):
    bl_idname = "maxwell_render.material_editor_remove_bsdf"
    bl_label = "Remove Selected BSDF"
    bl_description = "Remove selected BSDF"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mx = context.material.maxwell_render
        l = mx.custom_layers.layers[mx.custom_layers.index]
        cl = l.layer.bsdfs
        ls = l.layer.bsdfs.bsdfs
        idx = l.layer.bsdfs.index
        try:
            item = ls[idx]
        except IndexError:
            return {'CANCELLED'}
        
        cl.index -= 1
        ls.remove(idx)
        if(idx == 0):
            cl.index = idx
        if(len(ls) == 0):
            cl.index = -1
        
        return {'FINISHED'}


class MaterialEditorMoveBSDFUp(Operator):
    bl_idname = "maxwell_render.material_editor_move_bsdf_up"
    bl_label = "Move Selected BSDF Up"
    bl_description = "Move selected BSDF up"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mx = context.material.maxwell_render
        l = mx.custom_layers.layers[mx.custom_layers.index]
        cl = l.layer.bsdfs
        ls = l.layer.bsdfs.bsdfs
        idx = l.layer.bsdfs.index
        try:
            item = ls[idx]
        except IndexError:
            return {'CANCELLED'}
        
        if(idx >= 1):
            mv = idx - 1
            ls.move(mv, idx, )
            cl.index = mv
            return {'FINISHED'}
        
        return {'PASS_THROUGH'}


class MaterialEditorMoveBSDFDown(Operator):
    bl_idname = "maxwell_render.material_editor_move_bsdf_down"
    bl_label = "Move Selected BSDF Down"
    bl_description = "Move selected BSDF down"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mx = context.material.maxwell_render
        l = mx.custom_layers.layers[mx.custom_layers.index]
        cl = l.layer.bsdfs
        ls = l.layer.bsdfs.bsdfs
        idx = l.layer.bsdfs.index
        try:
            item = ls[idx]
        except IndexError:
            return {'CANCELLED'}
        
        if(idx < len(ls) - 1):
            mv = idx + 1
            ls.move(idx, mv, )
            cl.index = mv
            return {'FINISHED'}
        
        return {'PASS_THROUGH'}


class MaterialEditorCloneBSDF(Operator):
    bl_idname = "maxwell_render.material_editor_clone_bsdf"
    bl_label = "Clone Selected BSDF"
    bl_description = "Clone selected BSDF"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mx = context.material.maxwell_render
        l = mx.custom_layers.layers[mx.custom_layers.index]
        cl = l.layer.bsdfs
        ls = l.layer.bsdfs.bsdfs
        idx = l.layer.bsdfs.index
        try:
            item = ls[idx]
        except IndexError:
            return {'CANCELLED'}
        
        d = l.layer.bsdfs['bsdfs'][l.layer.bsdfs.index].to_dict()
        bpy.ops.maxwell_render.material_editor_add_bsdf()
        l.layer.bsdfs['bsdfs'][l.layer.bsdfs.index].update(d)
        n = l.layer.bsdfs['bsdfs'][l.layer.bsdfs.index]['name']
        l.layer.bsdfs['bsdfs'][l.layer.bsdfs.index]['name'] = 'Clone of {}'.format(n)
        
        return {'FINISHED'}


class SaveMaterialAsMXM(Operator):
    bl_idname = "maxwell_render.save_material_as_mxm"
    bl_label = "Save Material As MXM"
    bl_description = "Save material as .MXM and open it in Mxed material editor"
    
    filepath = StringProperty(subtype='FILE_PATH', )
    filename_ext = ".mxm"
    check_extension = True
    check_existing = BoolProperty(name="", default=True, options={'HIDDEN'}, )
    remove_dots = True
    
    filter_folder = BoolProperty(name="Filter folders", default=True, options={'HIDDEN'}, )
    filter_glob = StringProperty(default="*.mxm", options={'HIDDEN'}, )
    
    force_preview = BoolProperty(name="Force Preview", default=True, )
    force_preview_scene = StringProperty(name="Force Preview Scene", default="", )
    open_in_mxed = BoolProperty(name="Open In Mxed", default=True, )
    swap = BoolProperty(name="Swap Material Type To Reference", default=True, )
    
    @classmethod
    def poll(cls, context):
        return (context.material or context.object)
    
    def draw(self, context):
        l = self.layout
        l.prop(self, 'open_in_mxed')
        l.prop(self, 'force_preview')
    
    def invoke(self, context, event):
        n = context.material.name
        if(self.remove_dots):
            # remove dots, Maxwell doesn't like it - material name is messed up..
            n = n.replace(".", "_")
        self.filepath = os.path.join(context.scene.maxwell_render.materials_directory, "{}.mxm".format(n))
        self.force_preview = context.material.maxwell_render.force_preview
        self.force_preview_scene = context.material.maxwell_render.force_preview_scene
        self.open_in_mxed = context.material.maxwell_render.custom_open_in_mxed_after_save
        if(self.force_preview_scene == ' '):
            self.force_preview_scene = ''
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def check(self, context):
        change_ext = False
        check_extension = self.check_extension
        
        if(check_extension is not None):
            filepath = self.filepath
            
            if(self.remove_dots):
                h, t = os.path.split(filepath)
                n, e = os.path.splitext(t)
                n = n.replace(".", "_")
                filepath = os.path.join(h, "{}{}".format(n, e))
            
            if(os.path.basename(filepath)):
                filepath = bpy.path.ensure_ext(filepath,
                                               self.filename_ext
                                               if check_extension
                                               else "")
                if(filepath != self.filepath):
                    self.filepath = filepath
                    change_ext = True
        return change_ext
    
    def execute(self, context):
        p = os.path.abspath(bpy.path.abspath(self.filepath))
        
        if(p == ""):
            self.report({'ERROR'}, "Filepath is empty")
            return {'CANCELLED'}
        if(os.path.isdir(p)):
            self.report({'ERROR'}, "Filepath is directory")
            return {'CANCELLED'}
        
        h, t = os.path.split(p)
        n, e = os.path.splitext(t)
        if(e.lower() != ".mxm"):
            self.report({'ERROR'}, "Extension is not .mxm")
            return {'CANCELLED'}
        
        if(not os.path.exists(os.path.dirname(p))):
            self.report({'ERROR'}, "Directory does not exist")
            return {'CANCELLED'}
        
        if(not os.access(os.path.dirname(p), os.W_OK)):
            self.report({'ERROR'}, "Directory is not writeable")
            return {'CANCELLED'}
        
        mat = export.MXSMaterialCustom(context.material.name)
        d = mat._repr()
        
        system.mxed_create_and_edit_custom_material_helper(p, d, self.force_preview, self.force_preview_scene, self.open_in_mxed, )
        
        rp = bpy.path.relpath(self.filepath)
        if(system.PLATFORM == 'Windows'):
            rp = os.path.abspath(self.filepath)
        
        if(self.swap):
            context.material.maxwell_render.use = 'REFERENCE'
            context.material.maxwell_render.mxm_file = rp
        
        return {'FINISHED'}


class LoadMaterialFromMXM(Operator, ImportHelper):
    bl_idname = "maxwell_render.load_material_from_mxm"
    bl_label = "Load Material From MXM"
    bl_description = "Load material from existing .MXM"
    
    filename_ext = ".mxm"
    check_extension = True
    filepath = StringProperty(subtype='FILE_PATH', )
    filter_folder = BoolProperty(name="Filter folders", default=True, options={'HIDDEN'}, )
    filter_glob = StringProperty(default="*.mxm", options={'HIDDEN'}, )
    
    @classmethod
    def poll(cls, context):
        return (context.material or context.object)
    
    def draw(self, context):
        l = self.layout
    
    def execute(self, context):
        d = {'mxm_path': os.path.realpath(bpy.path.abspath(self.filepath)), }
        if(system.PLATFORM == 'Darwin'):
            im = impmxs.MXMImportMacOSX(**d)
        elif(system.PLATFORM == 'Linux' or system.PLATFORM == 'Windows'):
            im = impmxs.MXMImportWinLin(**d)
        else:
            pass
        
        self.make(context.material, context.material_slot, im.data)
        
        return {'FINISHED'}
    
    def texture(self, mat, d, n, ):
        if(d is None):
            return ""
        
        ts = mat.texture_slots
        slot = ts.add()
        tex = bpy.data.textures.new(n, 'IMAGE')
        slot.texture = tex
        image = None
        if(os.path.exists(d['path'])):
            image = bpy.data.images.load(d['path'])
        else:
            if('procedural' in d):
                if(len(d['procedural']) > 0):
                    pass
            else:
                self.report({'ERROR'}, "File '{}' does not exist.".format(d['path']))
        tex.image = image
        mx = tex.maxwell_render
        
        mx.path = d['path']
        mx.use_global_map = d['use_global_map']
        mx.channel = d['channel']
        
        tm = d['tiling_method']
        if(not tm[0] and not tm[1]):
            mx.tiling_method = 'NO_TILING'
        elif(tm[0] and not tm[1]):
            mx.tiling_method = 'TILE_X'
        elif(not tm[0] and tm[1]):
            mx.tiling_method = 'TILE_Y'
        else:
            mx.tiling_method = 'TILE_XY'
        
        mx.tiling_units = str(d['tiling_units'])
        mx.repeat = d['repeat']
        mx.mirror_x = d['mirror'][0]
        mx.mirror_y = d['mirror'][1]
        mx.offset = d['offset']
        mx.rotation = math.radians(d['rotation'])
        mx.invert = d['invert']
        mx.use_alpha = d['use_alpha']
        mx.interpolation = bool(d['interpolation'])
        mx.brightness = d['brightness']
        mx.contrast = d['contrast']
        mx.saturation = d['saturation']
        mx.hue = d['hue']
        mx.clamp = d['clamp']
        
        mx.normal_mapping_flip_red = bool(d['normal_mapping_flip_red'])
        mx.normal_mapping_flip_green = bool(d['normal_mapping_flip_green'])
        mx.normal_mapping_full_range_blue = bool(d['normal_mapping_full_range_blue'])
        
        def gamma_correct(c):
            g = 2.2
            c = [v ** g for v in c]
            return c
        
        if('procedural' in d):
            if(len(d['procedural']) > 0):
                mx.procedural
                mx.procedural.textures
                for i in range(len(d['procedural'])):
                    pd = d['procedural'][i]
                    if(pd['EXTENSION_NAME'] == 'Brick'):
                        override_context = bpy.context.copy()
                        override_context['texture'] = tex
                        bpy.ops.maxwell_render.texture_procedural_add(override_context, name='Brick', use='BRICK', )
                        td = mx.procedural.textures[len(mx.procedural.textures) - 1]
                        
                        td.brick_brick_width = pd['Brick width']
                        td.brick_brick_height = pd['Brick height']
                        td.brick_brick_offset = pd['Brick offset']
                        td.brick_random_offset = pd['Random offset']
                        td.brick_double_brick = pd['Double brick']
                        td.brick_small_brick_width = pd['Small brick width']
                        td.brick_round_corners = pd['Round corners']
                        td.brick_boundary_sharpness_u = pd['Boundary sharpness U']
                        td.brick_boundary_sharpness_v = pd['Boundary sharpness V']
                        td.brick_boundary_noise_detail = pd['Boundary noise detail']
                        td.brick_boundary_noise_region_u = pd['Boundary noise region U']
                        td.brick_boundary_noise_region_v = pd['Boundary noise region V']
                        td.brick_seed = pd['Seed']
                        td.brick_random_rotation = pd['Random rotation']
                        td.brick_color_variation = pd['Color variation']
                        td.brick_brick_color_0 = gamma_correct(pd['Brick color 0'])
                        td.brick_brick_texture_0 = self.texture(mat, pd['Brick texture 0'], 'Brick texture 0', )
                        td.brick_sampling_factor_0 = pd['Sampling factor 0']
                        td.brick_weight_0 = pd['Weight 0']
                        td.brick_brick_color_1 = gamma_correct(pd['Brick color 1'])
                        td.brick_brick_texture_1 = self.texture(mat, pd['Brick texture 1'], 'Brick texture 1', )
                        td.brick_sampling_factor_1 = pd['Sampling factor 1']
                        td.brick_weight_1 = pd['Weight 1']
                        td.brick_brick_color_2 = gamma_correct(pd['Brick color 2'])
                        td.brick_brick_texture_2 = self.texture(mat, pd['Brick texture 2'], 'Brick texture 2', )
                        td.brick_sampling_factor_2 = pd['Sampling factor 2']
                        td.brick_weight_2 = pd['Weight 2']
                        td.brick_mortar_thickness = pd['Mortar thickness']
                        td.brick_mortar_color = gamma_correct(pd['Mortar color'])
                        td.brick_mortar_texture = self.texture(mat, pd['Mortar texture'], 'Mortar texture', )
                        
                        td.blending_factor = pd['Blend procedural']
                    elif(pd['EXTENSION_NAME'] == 'Checker'):
                        override_context = bpy.context.copy()
                        override_context['texture'] = tex
                        bpy.ops.maxwell_render.texture_procedural_add(override_context, name='Checker', use='CHECKER', )
                        td = mx.procedural.textures[len(mx.procedural.textures) - 1]
                        
                        td.checker_number_of_elements_u = pd['Number of elements U']
                        td.checker_number_of_elements_v = pd['Number of elements V']
                        td.checker_color_0 = gamma_correct(pd['Color0'])
                        td.checker_color_1 = gamma_correct(pd['Color1'])
                        td.checker_transition_sharpness = pd['Transition sharpness']
                        td.checker_falloff = str(pd['Fall-off'])
                        
                        td.blending_factor = pd['Blend procedural']
                    elif(pd['EXTENSION_NAME'] == 'Circle'):
                        override_context = bpy.context.copy()
                        override_context['texture'] = tex
                        bpy.ops.maxwell_render.texture_procedural_add(override_context, name='Circle', use='CIRCLE', )
                        td = mx.procedural.textures[len(mx.procedural.textures) - 1]
                        
                        td.circle_background_color = gamma_correct(pd['Background color'])
                        td.circle_circle_color = gamma_correct(pd['Circle color'])
                        td.circle_radius_u = pd['RadiusU']
                        td.circle_radius_v = pd['RadiusV']
                        td.circle_transition_factor = pd['Transition factor']
                        td.circle_falloff = str(pd['Fall-off'])
                        
                        td.blending_factor = pd['Blend procedural']
                    elif(pd['EXTENSION_NAME'] == 'Gradient3'):
                        override_context = bpy.context.copy()
                        override_context['texture'] = tex
                        bpy.ops.maxwell_render.texture_procedural_add(override_context, name='Gradient3', use='GRADIENT3', )
                        td = mx.procedural.textures[len(mx.procedural.textures) - 1]
                        
                        td.gradient3_gradient_u = pd['Gradient U']
                        td.gradient3_color0_u = gamma_correct(pd['Color0 U'])
                        td.gradient3_color1_u = gamma_correct(pd['Color1 U'])
                        td.gradient3_color2_u = gamma_correct(pd['Color2 U'])
                        td.gradient3_gradient_type_u = str(pd['Gradient type U'])
                        td.gradient3_color1_u_position = pd['Color1 U position']
                        td.gradient3_gradient_v = pd['Gradient V']
                        td.gradient3_color0_v = gamma_correct(pd['Color0 V'])
                        td.gradient3_color1_v = gamma_correct(pd['Color1 V'])
                        td.gradient3_color2_v = gamma_correct(pd['Color2 V'])
                        td.gradient3_gradient_type_v = str(pd['Gradient type V'])
                        td.gradient3_color1_v_position = pd['Color1 V position']
                        
                        td.blending_factor = pd['Blend procedural']
                    elif(pd['EXTENSION_NAME'] == 'Gradient'):
                        override_context = bpy.context.copy()
                        override_context['texture'] = tex
                        bpy.ops.maxwell_render.texture_procedural_add(override_context, name='Gradient', use='GRADIENT', )
                        td = mx.procedural.textures[len(mx.procedural.textures) - 1]
                        
                        td.gradient_gradient_u = pd['Gradient U']
                        td.gradient_color0_u = gamma_correct(pd['Color0 U'])
                        td.gradient_color1_u = gamma_correct(pd['Color1 U'])
                        td.gradient_gradient_type_u = str(pd['Gradient type U'])
                        td.gradient_transition_factor_u = pd['Transition factor U']
                        td.gradient_gradient_v = pd['Gradient V']
                        td.gradient_color0_v = gamma_correct(pd['Color0 V'])
                        td.gradient_color1_v = gamma_correct(pd['Color1 V'])
                        td.gradient_gradient_type_v = str(pd['Gradient type V'])
                        td.gradient_transition_factor_v = pd['Transition factor V']
                        
                        td.blending_factor = pd['Blend procedural']
                    elif(pd['EXTENSION_NAME'] == 'Grid'):
                        override_context = bpy.context.copy()
                        override_context['texture'] = tex
                        bpy.ops.maxwell_render.texture_procedural_add(override_context, name='Grid', use='GRID', )
                        td = mx.procedural.textures[len(mx.procedural.textures) - 1]
                        
                        td.grid_cell_width = pd['Cell width']
                        td.grid_cell_height = pd['Cell height']
                        td.grid_boundary_thickness_u = pd['Boundary thickness U']
                        td.grid_boundary_thickness_v = pd['Boundary thickness V']
                        td.grid_transition_sharpness = pd['Transition sharpness']
                        td.grid_cell_color = gamma_correct(pd['Cell color'])
                        td.grid_boundary_color = gamma_correct(pd['Boundary color'])
                        td.grid_falloff = str(pd['Fall-off'])
                        
                        td.grid_horizontal_lines = True
                        if(td.grid_boundary_thickness_u == 0.0):
                            td.grid_horizontal_lines = False
                        td.grid_vertical_lines = True
                        if(td.grid_boundary_thickness_v == 0.0):
                            td.grid_vertical_lines = False
                        
                        td.blending_factor = pd['Blend procedural']
                    elif(pd['EXTENSION_NAME'] == 'Marble'):
                        override_context = bpy.context.copy()
                        override_context['texture'] = tex
                        bpy.ops.maxwell_render.texture_procedural_add(override_context, name='Marble', use='MARBLE', )
                        td = mx.procedural.textures[len(mx.procedural.textures) - 1]
                        
                        td.marble_coordinates_type = str(pd['Coordinates type'])
                        td.marble_color0 = gamma_correct(pd['Color0'])
                        td.marble_color1 = gamma_correct(pd['Color1'])
                        td.marble_color2 = gamma_correct(pd['Color2'])
                        td.marble_frequency = pd['Frequency']
                        td.marble_detail = pd['Detail']
                        td.marble_octaves = pd['Octaves']
                        td.marble_seed = pd['Seed']
                        
                        td.blending_factor = pd['Blend procedural']
                    elif(pd['EXTENSION_NAME'] == 'Noise'):
                        override_context = bpy.context.copy()
                        override_context['texture'] = tex
                        bpy.ops.maxwell_render.texture_procedural_add(override_context, name='Noise', use='NOISE', )
                        td = mx.procedural.textures[len(mx.procedural.textures) - 1]
                        
                        td.noise_coordinates_type = str(pd['Coordinates type'])
                        td.noise_noise_color = gamma_correct(pd['Noise color'])
                        td.noise_background_color = gamma_correct(pd['Background color'])
                        td.noise_detail = pd['Detail']
                        td.noise_persistance = pd['Persistance']
                        td.noise_octaves = pd['Octaves']
                        td.noise_low_value = pd['Low value']
                        td.noise_high_value = pd['High value']
                        td.noise_seed = pd['Seed']
                        
                        td.blending_factor = pd['Blend procedural']
                    elif(pd['EXTENSION_NAME'] == 'Voronoi'):
                        override_context = bpy.context.copy()
                        override_context['texture'] = tex
                        bpy.ops.maxwell_render.texture_procedural_add(override_context, name='Voronoi', use='VORONOI', )
                        td = mx.procedural.textures[len(mx.procedural.textures) - 1]
                        
                        td.voronoi_coordinates_type = str(pd['Coordinates type'])
                        td.voronoi_color0 = gamma_correct(pd['Color0'])
                        td.voronoi_color1 = gamma_correct(pd['Color1'])
                        td.voronoi_detail = pd['Detail']
                        td.voronoi_distance = str(pd['Distance'])
                        td.voronoi_combination = str(pd['Combination'])
                        td.voronoi_low_value = pd['Low value']
                        td.voronoi_high_value = pd['High value']
                        td.voronoi_seed = pd['Seed']
                        
                        td.blending_factor = pd['Blend procedural']
                    elif(pd['EXTENSION_NAME'] == 'TiledTexture'):
                        override_context = bpy.context.copy()
                        override_context['texture'] = tex
                        bpy.ops.maxwell_render.texture_procedural_add(override_context, name='Tiled', use='TILED', )
                        td = mx.procedural.textures[len(mx.procedural.textures) - 1]
                        
                        td.tiled_filename = pd['FileName']
                        td.tiled_token_mask = pd['Filename_mask']
                        td.tiled_base_color = gamma_correct(pd['Base Color'])
                        td.tiled_use_base_color = pd['Use base color']
                        
                        td.blending_factor = pd['Blend factor']
                    elif(pd['EXTENSION_NAME'] == 'WireframeTexture'):
                        override_context = bpy.context.copy()
                        override_context['texture'] = tex
                        bpy.ops.maxwell_render.texture_procedural_add(override_context, name='Wireframe', use='WIREFRAME', )
                        td = mx.procedural.textures[len(mx.procedural.textures) - 1]
                        
                        td.wireframe_fill_color = gamma_correct(pd['Fill Color'])
                        td.wireframe_edge_color = gamma_correct(pd['Edge Color'])
                        td.wireframe_coplanar_edge_color = gamma_correct(pd['Coplanar Edge Color'])
                        td.wireframe_edge_width = pd['Edge Width']
                        td.wireframe_coplanar_edge_width = pd['Coplanar Edge Width']
                        td.wireframe_coplanar_threshold = pd['Coplanar Threshold']
                        
                        # td.blending_factor = pd['Blend procedural']
                    else:
                        raise TypeError("{} is unknown procedural texture type".format(pd['EXTENSION_NAME']))
        
        return tex.name
    
    def extension(self, material, slot, data, ):
        def gamma_correct(c):
            g = 2.2
            c = [v ** g for v in c]
            return c
        
        material = bpy.data.materials.new(material.name)
        slot.material = material
        
        d = data
        e = data['extension']
        mx = material.maxwell_render
        
        # extension type
        enm = e['EXTENSION_NAME']
        if(enm == 'AGS'):
            mx.use = 'AGS'
        elif(enm == 'Opaque'):
            mx.use = 'OPAQUE'
        elif(enm == 'Transparent'):
            mx.use = 'TRANSPARENT'
        elif(enm == 'Metal'):
            mx.use = 'METAL'
        elif(enm == 'Translucent'):
            mx.use = 'TRANSLUCENT'
        elif(enm == 'Car Paint'):
            mx.use = 'CARPAINT'
        elif(enm == 'Hair'):
            mx.use = 'HAIR'
        else:
            raise TypeError("{}: Unsupported extension material type: {}".format(material.name, enm, ))
        
        # globals
        gp = d['global_props']
        if(gp['override_map'] is not None):
            mx.global_override_map = self.texture(material, gp['override_map'], 'override map')
        
        if(gp['bump_map'] is not None):
            mx.global_bump_map_enabled = True
            mx.global_bump = gp['bump']
            mx.global_bump_map = self.texture(material, gp['bump_map'], 'global bump map')
            mx.global_bump_map_use_normal = gp['bump_map_use_normal']
            mx.global_bump_normal = gp['bump_normal']
        else:
            mx.global_bump_map_enabled = False
            mx.global_bump = gp['bump']
            mx.global_bump_map = ''
            mx.global_bump_map_use_normal = gp['bump_map_use_normal']
            mx.global_bump_normal = gp['bump_normal']
        
        mx.global_dispersion = gp['dispersion']
        mx.global_shadow = gp['shadow']
        mx.global_matte = gp['matte']
        mx.global_priority = gp['priority']
        mx.global_id = gp['id']
        
        # extension data
        mxe = material.maxwell_render.extension
        
        # displacement
        def displacement(dp, cd):
            cd.enabled = dp['enabled']
            if(dp['map'] is not None):
                cd.map = self.texture(material, dp['map'], 'displacement map')
            cd.type = str(dp['type'])
            cd.subdivision = dp['subdivision']
            cd.adaptive = dp['adaptive']
            cd.subdivision_method = str(dp['subdivision_method'])
            cd.offset = dp['offset']
            cd.smoothing = dp['smoothing']
            cd.uv_interpolation = str(dp['uv_interpolation'])
            cd.height = dp['height'] * 100
            cd.height_units = str(int(dp['height_units']))
            cd.v3d_preset = str(dp['v3d_preset'])
            cd.v3d_transform = str(dp['v3d_transform'])
            cd.v3d_rgb_mapping = str(dp['v3d_rgb_mapping'])
            cd.v3d_scale = dp['v3d_scale']
        
        try:
            dp = d['displacement']
            cd = mxe.displacement
            displacement(dp, cd)
        except KeyError:
            pass
        
        if(mx.use == 'AGS'):
            mxe.ags_color = gamma_correct(e['Color'])
            mxe.ags_reflection = e['Reflection']
            mxe.ags_type = str(e['Type'])
        elif(mx.use == 'OPAQUE'):
            mxe.opaque_color_type = bool(e['Color Type'])
            mxe.opaque_color = gamma_correct(e['Color'])
            mxe.opaque_color_map = self.texture(material, e['Color Map'], 'color map')
            mxe.opaque_shininess_type = bool(e['Shininess Type'])
            mxe.opaque_shininess = e['Shininess']
            mxe.opaque_shininess_map = self.texture(material, e['Shininess Map'], 'shininess map')
            mxe.opaque_roughness_type = bool(e['Roughness Type'])
            mxe.opaque_roughness = e['Roughness']
            mxe.opaque_roughness_map = self.texture(material, e['Roughness Map'], 'roughness map')
            mxe.opaque_clearcoat = bool(e['Clearcoat'])
        elif(mx.use == 'TRANSPARENT'):
            mxe.transparent_color_type = bool(e['Color Type'])
            mxe.transparent_color = gamma_correct(e['Color'])
            mxe.transparent_color_map = self.texture(material, e['Color Map'], 'color map')
            mxe.transparent_ior = e['Ior']
            mxe.transparent_transparency = e['Transparency']
            mxe.transparent_roughness_type = bool(e['Roughness Type'])
            mxe.transparent_roughness = e['Roughness']
            mxe.transparent_roughness_map = self.texture(material, e['Roughness Map'], 'roughness map')
            mxe.transparent_specular_tint = e['Specular Tint']
            mxe.transparent_dispersion = e['Dispersion']
            mxe.transparent_clearcoat = bool(e['Clearcoat'])
        elif(mx.use == 'METAL'):
            mxe.metal_ior = str(e['IOR'])
            mxe.metal_tint = e['Tint']
            mxe.metal_color_type = bool(e['Color Type'])
            mxe.metal_color = gamma_correct(e['Color'])
            mxe.metal_color_map = self.texture(material, e['Color Map'], 'color map')
            mxe.metal_roughness_type = bool(e['Roughness Type'])
            mxe.metal_roughness = e['Roughness']
            mxe.metal_roughness_map = self.texture(material, e['Roughness Map'], 'roughness map')
            mxe.metal_anisotropy_type = bool(e['Anisotropy Type'])
            mxe.metal_anisotropy = e['Anisotropy']
            mxe.metal_anisotropy_map = self.texture(material, e['Anisotropy Map'], 'anisotropy map')
            mxe.metal_angle_type = bool(e['Angle Type'])
            mxe.metal_angle = e['Angle']
            mxe.metal_angle_map = self.texture(material, e['Angle Map'], 'angle map')
            mxe.metal_dust_type = bool(e['Dust Type'])
            mxe.metal_dust = e['Dust']
            mxe.metal_dust_map = self.texture(material, e['Dust Map'], 'dust map')
            mxe.metal_perforation_enabled = bool(e['Perforation Enabled'])
            mxe.metal_perforation_map = self.texture(material, e['Perforation Map'], 'perforation map')
        elif(mx.use == 'TRANSLUCENT'):
            mxe.translucent_scale = e['Scale']
            mxe.translucent_ior = e['Ior']
            mxe.translucent_color_type = bool(e['Color Type'])
            mxe.translucent_color = gamma_correct(e['Color'])
            mxe.translucent_color_map = self.texture(material, e['Color Map'], 'color map')
            mxe.translucent_hue_shift = e['Hue Shift']
            mxe.translucent_invert_hue = bool(e['Invert Hue'])
            mxe.translucent_vibrance = e['Vibrance']
            mxe.translucent_density = e['Density']
            mxe.translucent_opacity = e['Opacity']
            mxe.translucent_roughness_type = bool(e['Roughness Type'])
            mxe.translucent_roughness = e['Roughness']
            mxe.translucent_roughness_map = self.texture(material, e['Roughness Map'], 'roughness map')
            mxe.translucent_specular_tint = e['Specular Tint']
            mxe.translucent_clearcoat = bool(e['Clearcoat'])
            mxe.translucent_clearcoat_ior = e['Clearcoat Ior']
        elif(mx.use == 'CARPAINT'):
            mxe.carpaint_color = gamma_correct(e['Color'])
            mxe.carpaint_metallic = e['Metallic']
            mxe.carpaint_topcoat = e['Topcoat']
        elif(mx.use == 'HAIR'):
            mxe.hair_color_type = bool(e['Color Type'])
            mxe.hair_color = gamma_correct(e['Color'])
            mxe.hair_color_map = self.texture(material, e['Color Map'], 'color map')
            mxe.hair_root_tip_map = self.texture(material, e['Root-Tip Map'], 'root-tip map')
            mxe.hair_root_tip_weight_type = bool(e['Root-Tip Weight Type'])
            mxe.hair_root_tip_weight = e['Root-Tip Weight']
            mxe.hair_root_tip_weight_map = self.texture(material, e['Root-Tip Weight Map'], 'root-tip weight map')
            mxe.hair_primary_highlight_strength = e['Primary Highlight Strength']
            mxe.hair_primary_highlight_spread = e['Primary Highlight Spread']
            mxe.hair_primary_highlight_tint = gamma_correct(e['Primary Highlight Tint'])
            mxe.hair_secondary_highlight_strength = e['Secondary Highlight Strength']
            mxe.hair_secondary_highlight_spread = e['Secondary Highlight Spread']
            mxe.hair_secondary_highlight_tint = gamma_correct(e['Secondary Highlight Tint'])
    
    def make(self, material, slot, data, ):
        if('extension' in data):
            self.extension(material, slot, data, )
            return
        
        def gamma_correct(c):
            g = 2.2
            c = [v ** g for v in c]
            return c
        
        material = bpy.data.materials.new(material.name)
        slot.material = material
        
        d = data
        mx = material.maxwell_render
        mx.use = 'CUSTOM'
        
        # globals
        gp = d['global_props']
        if(gp['override_map'] is not None):
            mx.global_override_map = self.texture(material, gp['override_map'], 'override map')
        
        if(gp['bump_map'] is not None):
            mx.global_bump_map_enabled = True
            # mx.global_bump_abnormal_value = gp['bump']
            mx.global_bump = gp['bump']
            mx.global_bump_map = self.texture(material, gp['bump_map'], 'global bump map')
            mx.global_bump_map_use_normal = gp['bump_map_use_normal']
            mx.global_bump_normal = gp['bump_normal']
        else:
            mx.global_bump_map_enabled = False
            # mx.global_bump_abnormal_value = gp['bump']
            mx.global_bump = gp['bump']
            mx.global_bump_map = ''
            mx.global_bump_map_use_normal = gp['bump_map_use_normal']
            mx.global_bump_normal = gp['bump_normal']
        
        mx.global_dispersion = gp['dispersion']
        mx.global_shadow = gp['shadow']
        mx.global_matte = gp['matte']
        mx.global_priority = gp['priority']
        mx.global_id = gp['id']
        # displacement
        dp = d['displacement']
        cd = mx.custom_displacement
        if(dp['enabled']):
            cd.enabled = True
            if(dp['map'] is not None):
                cd.map = self.texture(material, dp['map'], 'displacement map')
            cd.type = str(dp['type'])
            cd.subdivision = dp['subdivision']
            cd.adaptive = dp['adaptive']
            cd.subdivision_method = str(dp['subdivision_method'])
            cd.offset = dp['offset']
            cd.smoothing = dp['smoothing']
            cd.uv_interpolation = str(dp['uv_interpolation'])
            cd.height = dp['height'] * 100
            cd.height_units = str(int(dp['height_units']))
            cd.v3d_preset = str(dp['v3d_preset'])
            cd.v3d_transform = str(dp['v3d_transform'])
            cd.v3d_rgb_mapping = str(dp['v3d_rgb_mapping'])
            cd.v3d_scale = dp['v3d_scale']
        # layers
        for i, ld in enumerate(d['layers']):
            # layer props
            lp = ld['layer_props']
            
            override_context = bpy.context.copy()
            override_context['material'] = material
            bpy.ops.maxwell_render.material_editor_add_layer(override_context, auto_bsdf=False, add_to_top=False, )
            layer = mx.custom_layers.layers[len(mx.custom_layers.layers) - 1]
            
            layer.name = ld['name']
            l = layer.layer
            
            l.visible = lp['visible']
            l.opacity = lp['opacity']
            if(lp['opacity_map'] is not None):
                l.opacity_map_enabled = True
                l.opacity_map = self.texture(material, lp['opacity_map'], 'opacity map')
            else:
                l.opacity_map_enabled = False
                l.opacity_map = ""
            l.blending = str(lp['blending'])
            
            # emitter
            ep = ld['emitter']
            ex = layer.emitter
            if(ep['enabled']):
                ex.enabled = ep['enabled']
                ex.type = str(ep['type'])
                ex.ies_data = ep['ies_data']
                ex.ies_intensity = ep['ies_intensity']
                ex.spot_map_enabled = ep['spot_map_enabled']
                if(ep['spot_map'] is not None):
                    ex.spot_map = self.texture(material, ep['spot_map'], 'spot map')
                ex.spot_cone_angle = math.radians(ep['spot_cone_angle'])
                ex.spot_falloff_angle = math.radians(ep['spot_falloff_angle'])
                ex.spot_falloff_type = str(ep['spot_falloff_type'])
                ex.spot_blur = ep['spot_blur']
                ex.emission = str(ep['emission'])
                ex.color = gamma_correct(ep['color'])
                ex.color_black_body_enabled = ep['color_black_body_enabled']
                ex.color_black_body = ep['color_black_body']
                ex.luminance = str(ep['luminance'])
                ex.luminance_power = ep['luminance_power']
                ex.luminance_efficacy = ep['luminance_efficacy']
                ex.luminance_output = ep['luminance_output']
                ex.temperature_value = ep['temperature_value']
                if(ep['hdr_map'] is not None):
                    ex.hdr_map = self.texture(material, ep['hdr_map'], 'hdr map')
                ex.hdr_intensity = ep['hdr_intensity']
            
            # bsdfs
            for j, bdp in enumerate(ld['bsdfs']):
                override_context = bpy.context.copy()
                override_context['material'] = material
                bpy.ops.maxwell_render.material_editor_add_bsdf(override_context, add_to_top=False, )
                # and now, some ugly line..
                b = mx.custom_layers.layers[len(mx.custom_layers.layers) - 1].layer.bsdfs.bsdfs[len(mx.custom_layers.layers[len(mx.custom_layers.layers) - 1].layer.bsdfs.bsdfs) - 1].bsdf
                
                bd = bdp['bsdf_props']
                b.visible = bd['visible']
                b.weight = bd['weight']
                
                if(bd['weight_map'] is not None):
                    b.weight_map_enabled = True
                    b.weight_map = self.texture(material, bd['weight_map'], 'weight map')
                else:
                    b.weight_map_enabled = False
                    b.weight_map = ""
                
                b.ior = str(bd['ior'])
                b.complex_ior = bd['complex_ior']
                b.reflectance_0 = gamma_correct(bd['reflectance_0'])
                
                if(bd['reflectance_0_map'] is not None):
                    b.reflectance_0_map_enabled = True
                    b.reflectance_0_map = self.texture(material, bd['reflectance_0_map'], 'reflectance 0 map')
                else:
                    b.reflectance_0_map_enabled = False
                    b.reflectance_0_map = ""
                
                b.reflectance_90 = gamma_correct(bd['reflectance_90'])
                
                if(bd['reflectance_90_map'] is not None):
                    b.reflectance_90_map_enabled = True
                    b.reflectance_90_map = self.texture(material, bd['reflectance_90_map'], 'reflectance 90 map')
                else:
                    b.reflectance_90_map_enabled = False
                    b.reflectance_90_map = ""
                
                b.transmittance = gamma_correct(bd['transmittance'])
                
                if(bd['transmittance_map'] is not None):
                    b.transmittance_map_enabled = True
                    b.transmittance_map = self.texture(material, bd['transmittance_map'], 'transmittance map')
                else:
                    b.transmittance_map_enabled = False
                    b.transmittance_map = ""
                
                b.attenuation = bd['attenuation']
                b.attenuation_units = str(bd['attenuation_units'])
                b.nd = bd['nd']
                b.force_fresnel = bd['force_fresnel']
                b.k = bd['k']
                b.abbe = bd['abbe']
                b.r2_enabled = bd['r2_enabled']
                b.r2_falloff_angle = math.radians(bd['r2_falloff_angle'])
                b.r2_influence = bd['r2_influence']
                b.roughness = bd['roughness']
                
                if(bd['roughness_map'] is not None):
                    b.roughness_map_enabled = True
                    b.roughness_map = self.texture(material, bd['roughness_map'], 'roughness map')
                else:
                    b.roughness_map_enabled = False
                    b.roughness_map = ""
                
                # b.bump_abnormal_value = bd['bump']
                b.bump = bd['bump']
                
                if(bd['bump_map'] is not None):
                    b.bump_map_enabled = True
                    b.bump_map = self.texture(material, bd['bump_map'], 'bump map')
                else:
                    b.bump_map_enabled = False
                    b.bump_map = ""
                
                b.bump_map_use_normal = bd['bump_map_use_normal']
                b.bump_normal = bd['bump_normal']
                
                b.anisotropy = bd['anisotropy']
                
                if(bd['anisotropy_map'] is not None):
                    b.anisotropy_map_enabled = True
                    b.anisotropy_map = self.texture(material, bd['anisotropy_map'], 'anisotropy map')
                else:
                    b.anisotropy_map_enabled = False
                    b.anisotropy_map = ""
                
                b.anisotropy_angle = math.radians(bd['anisotropy_angle'])
                
                if(bd['anisotropy_angle_map'] is not None):
                    b.anisotropy_angle_map_enabled = True
                    b.anisotropy_angle_map = self.texture(material, bd['anisotropy_angle_map'], 'anisotropy angle map')
                else:
                    b.anisotropy_angle_map_enabled = False
                    b.anisotropy_angle_map = ""
                
                b.scattering = gamma_correct(bd['scattering'])
                b.coef = bd['coef']
                b.asymmetry = bd['asymmetry']
                b.single_sided = bd['single_sided']
                b.single_sided_value = bd['single_sided_value'] * 1000
                
                if(bd['single_sided_map'] is not None):
                    b.single_sided_map_enabled = True
                    b.single_sided_map = self.texture(material, bd['single_sided_map'], 'single sided map')
                else:
                    b.single_sided_map_enabled = False
                    b.single_sided_map = ""
                
                b.single_sided_min = bd['single_sided_min'] * 1000
                b.single_sided_max = bd['single_sided_max'] * 1000
                
                # coating
                c = mx.custom_layers.layers[len(mx.custom_layers.layers) - 1].layer.bsdfs.bsdfs[len(mx.custom_layers.layers[len(mx.custom_layers.layers) - 1].layer.bsdfs.bsdfs) - 1].coating
                cd = bdp['coating']
                
                c.enabled = cd['enabled']
                c.thickness = cd['thickness'] * 1000000000
                
                if(cd['thickness_map'] is not None):
                    c.thickness_map_enabled = True
                    c.thickness_map = self.texture(material, cd['thickness_map'], 'coating thickness map')
                else:
                    c.thickness_map_enabled = False
                    c.thickness_map = ""
                
                c.thickness_map_min = cd['thickness_map_min'] * 1000000000
                c.thickness_map_max = cd['thickness_map_max'] * 1000000000
                c.ior = str(cd['ior'])
                c.complex_ior = cd['complex_ior']
                c.reflectance_0 = gamma_correct(cd['reflectance_0'])
                
                if(cd['reflectance_0_map'] is not None):
                    c.reflectance_0_map_enabled = True
                    c.reflectance_0_map = self.texture(material, cd['reflectance_0_map'], 'coating reflectance 0 map')
                else:
                    c.reflectance_0_map_enabled = False
                    c.reflectance_0_map = ""
                
                c.reflectance_90 = gamma_correct(cd['reflectance_90'])
                
                if(cd['reflectance_90_map'] is not None):
                    c.reflectance_90_map_enabled = True
                    c.reflectance_90_map = self.texture(material, cd['reflectance_90_map'], 'coating reflectance 90 map')
                else:
                    c.reflectance_90_map_enabled = False
                    c.reflectance_90_map = ""
                
                c.nd = cd['nd']
                c.force_fresnel = cd['force_fresnel']
                c.k = cd['k']
                c.r2_enabled = cd['r2_enabled']
                c.r2_falloff_angle = math.radians(cd['r2_falloff_angle'])


class CustomAlphasAdd(Operator):
    bl_idname = "maxwell_render.custom_alphas_add"
    bl_label = "Add Custom Alpha"
    bl_description = "Add Custom Alpha"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mx = context.scene.maxwell_render
        obs = mx.custom_alphas_manual.alphas
        
        item = obs.add()
        item.id = len(obs)
        item.name = 'Custom Alpha'
        mx.custom_alphas_manual.index = (len(obs) - 1)
        
        return {'FINISHED'}


class CustomAlphasRemove(Operator):
    bl_idname = "maxwell_render.custom_alphas_remove"
    bl_label = "Remove Custom Alpha"
    bl_description = "Remove Custom Alpha"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mx = context.scene.maxwell_render
        cam = mx.custom_alphas_manual
        obs = cam.alphas
        idx = cam.index
        try:
            item = obs[idx]
        except IndexError:
            return {'CANCELLED'}
        
        cam.index -= 1
        obs.remove(idx)
        if(idx == 0):
            cam.index = idx
        if(len(obs) == 0):
            cam.index = -1
        
        return {'FINISHED'}


class CustomAlphasObjectAdd(Operator):
    bl_idname = "maxwell_render.custom_alphas_object_add"
    bl_label = "Add Object"
    bl_description = "Add Object To Custom Alpha"
    bl_options = {'REGISTER', 'UNDO'}
    
    name = StringProperty(name="Object Name", )
    
    def execute(self, context):
        mx = context.scene.maxwell_render
        alpha = mx.custom_alphas_manual.alphas[mx.custom_alphas_manual.index]
        obs = alpha.objects
        for n in obs:
            if(self.name == n.name):
                return {'PASS_THROUGH'}
        
        item = obs.add()
        item.id = len(obs)
        item.name = self.name
        
        alpha.o_index = (len(obs) - 1)
        
        return {'FINISHED'}


class CustomAlphasObjectRemove(Operator):
    bl_idname = "maxwell_render.custom_alphas_object_remove"
    bl_label = "Remove Object"
    bl_description = "Remove Object From Custom Alpha"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mx = context.scene.maxwell_render
        alpha = mx.custom_alphas_manual.alphas[mx.custom_alphas_manual.index]
        obs = alpha.objects
        idx = alpha.o_index
        try:
            item = obs[idx]
        except IndexError:
            return {'CANCELLED'}
        
        alpha.o_index -= 1
        obs.remove(idx)
        if(idx == 0):
            alpha.o_index = idx
        if(len(obs) == 0):
            alpha.o_index = -1
        
        return {'FINISHED'}


class CustomAlphasObjectAddSelected(Operator):
    bl_idname = "maxwell_render.custom_alphas_add_selected_objects"
    bl_label = "Add Selected Objects"
    bl_description = "Add Selected Objects To Custom Alpha"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        allowed = ['MESH', 'CURVE', 'SURFACE', 'FONT', ]
        aos = []
        for o in bpy.context.selected_objects:
            if(o.type in allowed):
                aos.append(o.name)
        
        mx = context.scene.maxwell_render
        alpha = mx.custom_alphas_manual.alphas[mx.custom_alphas_manual.index]
        obs = alpha.objects
        
        def add(name):
            item = obs.add()
            item.id = len(obs)
            item.name = name
            alpha.o_index = (len(obs) - 1)
        
        for ao in aos:
            existing = [o.name for o in obs]
            if(ao not in existing):
                add(ao)
        
        return {'FINISHED'}


class CustomAlphasObjectClear(Operator):
    bl_idname = "maxwell_render.custom_alphas_object_clear"
    bl_label = "Remove All Objects"
    bl_description = "Remove All Objects From Custom Alpha"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mx = context.scene.maxwell_render
        alpha = mx.custom_alphas_manual.alphas[mx.custom_alphas_manual.index]
        while(len(alpha.objects) > 0):
            alpha.objects.remove(0)
        alpha.o_index = -1
        
        return {'FINISHED'}


class CustomAlphasMaterialAdd(Operator):
    bl_idname = "maxwell_render.custom_alphas_material_add"
    bl_label = "Add Material"
    bl_description = "Add Material To Custom Alpha"
    bl_options = {'REGISTER', 'UNDO'}
    
    name = StringProperty(name="Material Name", )
    
    def execute(self, context):
        mx = context.scene.maxwell_render
        alpha = mx.custom_alphas_manual.alphas[mx.custom_alphas_manual.index]
        mats = alpha.materials
        for n in mats:
            if(self.name == n.name):
                return {'PASS_THROUGH'}
        
        item = mats.add()
        item.id = len(mats)
        item.name = self.name
        
        alpha.m_index = (len(mats) - 1)
        
        return {'FINISHED'}


class CustomAlphasMaterialRemove(Operator):
    bl_idname = "maxwell_render.custom_alphas_material_remove"
    bl_label = "Remove Material"
    bl_description = "Remove Material From Custom Alpha"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mx = context.scene.maxwell_render
        alpha = mx.custom_alphas_manual.alphas[mx.custom_alphas_manual.index]
        mats = alpha.materials
        idx = alpha.m_index
        try:
            item = mats[idx]
        except IndexError:
            return {'CANCELLED'}
        
        alpha.m_index -= 1
        mats.remove(idx)
        if(idx == 0):
            alpha.m_index = idx
        if(len(mats) == 0):
            alpha.m_index = -1
        
        return {'FINISHED'}


class CustomAlphasMaterialClear(Operator):
    bl_idname = "maxwell_render.custom_alphas_material_clear"
    bl_label = "Remove All Materials"
    bl_description = "Remove All Materials From Custom Alpha"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mx = context.scene.maxwell_render
        alpha = mx.custom_alphas_manual.alphas[mx.custom_alphas_manual.index]
        while(len(alpha.materials) > 0):
            alpha.materials.remove(0)
        alpha.m_index = -1
        
        return {'FINISHED'}


class MaterialWizardPlastic(Operator):
    bl_idname = "maxwell_render.material_wizard_plastic"
    bl_label = "Plastic"
    bl_description = "Material wizard: Plastic"
    
    # shininess = FloatProperty(name="Shininess", default=30.0, min=0.0, max=100.0, precision=0, subtype='PERCENTAGE', )
    # roughness = FloatProperty(name="Roughness", default=0.0, min=0.0, max=100.0, precision=0, subtype='PERCENTAGE', )
    # color = FloatVectorProperty(name="Color", default=(0.07805659603547627, 0.12752978241224922, 0.26735808898200775), min=0.0, max=1.0, precision=2, subtype='COLOR', )
    
    @classmethod
    def poll(cls, context):
        # Plastic wizard is the same as Opaque extension..
        return False
    
    # def draw(self, context):
    #     l = self.layout
    #     l.prop(self, 'shininess')
    #     l.prop(self, 'roughness')
    #     l.prop(self, 'color')
    
    def execute(self, context):
        mat = context.material
        mx = mat.maxwell_render
        w = mx.wizards
        cl = mx.custom_layers
        
        while(len(cl.layers) > 0):
            bpy.ops.maxwell_render.material_editor_remove_layer()
        
        bpy.ops.maxwell_render.material_editor_add_layer()
        li = cl.layers[0]
        li.name = "Base"
        li.emitter
        l = li.layer
        bi = l.bsdfs.bsdfs[0]
        bi.coating
        b = bi.bsdf
        b.reflectance_0 = w.plastic_color
        b.reflectance_90 = w.plastic_color
        b.roughness = 97.0
        
        bpy.ops.maxwell_render.material_editor_add_layer()
        li = cl.layers[0]
        li.name = "Topcoat"
        li.emitter
        l = li.layer
        l.blending = '1'
        bi = l.bsdfs.bsdfs[0]
        bi.coating
        b = bi.bsdf
        b.reflectance_0 = (0.0, 0.0, 0.0, )
        b.reflectance_90 = (0.0, 0.0, 0.0, )
        b.nd = 1.1 + (w.plastic_shininess * 0.005)
        b.force_fresnel = True
        b.abbe = 50.0
        b.roughness = w.plastic_roughness
        
        w.types = 'NONE'
        
        return {'FINISHED'}
    
    # def invoke(self, context, event):
    #     return context.window_manager.invoke_props_dialog(self)


class MaterialWizardGreasy(Operator):
    bl_idname = "maxwell_render.material_wizard_greasy"
    bl_label = "Greasy"
    bl_description = "Material wizard: Greasy"
    
    # color = FloatVectorProperty(name="Color", default=(0.0008046585621626175, 0.0008046585621626175, 0.0008046585621626175), min=0.0, max=1.0, precision=2, subtype='COLOR', )
    
    # @classmethod
    # def poll(cls, context):
    #     return True
    #
    # def draw(self, context):
    #     l = self.layout
    #     l.prop(self, 'color')
    
    def execute(self, context):
        mat = context.material
        mx = mat.maxwell_render
        w = mx.wizards
        cl = mx.custom_layers
        
        while(len(cl.layers) > 0):
            bpy.ops.maxwell_render.material_editor_remove_layer()
        
        bpy.ops.maxwell_render.material_editor_add_layer()
        li = cl.layers[0]
        li.name = "Base"
        li.emitter
        l = li.layer
        bi = l.bsdfs.bsdfs[0]
        bi.coating
        b = bi.bsdf
        b.reflectance_0 = w.greasy_color
        b.reflectance_90 = w.greasy_color
        b.nd = 3.0
        b.roughness = 97.0
        
        bpy.ops.maxwell_render.material_editor_add_layer()
        li = cl.layers[0]
        li.name = "Topcoat"
        li.emitter
        l = cl.layers[0].layer
        l.blending = '1'
        bi = l.bsdfs.bsdfs[0]
        bi.coating
        b = bi.bsdf
        b.reflectance_0 = (0.0, 0.0, 0.0, )
        b.reflectance_90 = (0.0, 0.0, 0.0, )
        b.nd = 1.250
        b.force_fresnel = True
        b.roughness = 0
        
        bpy.ops.maxwell_render.material_editor_add_layer()
        li = cl.layers[0]
        li.name = "Scratches"
        li.emitter
        l = cl.layers[0].layer
        l.blending = '1'
        bi = l.bsdfs.bsdfs[0]
        bi.coating
        b = bi.bsdf
        b.reflectance_0 = (0.0, 0.0, 0.0, )
        b.reflectance_90 = (0.0, 0.0, 0.0, )
        b.nd = 1.250
        b.force_fresnel = True
        b.roughness = 25.0
        
        bpy.ops.maxwell_render.material_editor_add_layer()
        li = cl.layers[0]
        li.name = "Dust"
        li.emitter
        l = cl.layers[0].layer
        l.blending = '1'
        bi = l.bsdfs.bsdfs[0]
        bi.coating
        b = bi.bsdf
        b.reflectance_0 = (0.0, 0.0, 0.0, )
        b.reflectance_90 = (1.0, 1.0, 1.0, )
        b.nd = 1.150
        b.force_fresnel = False
        b.r2_enabled = True
        b.r2_falloff_angle = math.radians(76.0)
        b.roughness = 90.0
        
        w.types = 'NONE'
        
        return {'FINISHED'}
    
    # def invoke(self, context, event):
    #     return context.window_manager.invoke_props_dialog(self)


class MaterialWizardVelvet(Operator):
    bl_idname = "maxwell_render.material_wizard_velvet"
    bl_label = "Velvet"
    bl_description = "Material wizard: Velvet"
    
    # color = FloatVectorProperty(name="Color", default=(0.05112205630307245, 0.010397803645369345, 0.10114516973592808), min=0.0, max=1.0, precision=2, subtype='COLOR', )
    
    # @classmethod
    # def poll(cls, context):
    #     return True
    #
    # def draw(self, context):
    #     l = self.layout
    #     l.prop(self, 'color')
    
    def execute(self, context):
        mat = context.material
        mx = mat.maxwell_render
        w = mx.wizards
        cl = mx.custom_layers
        
        c0 = Color(w.velvet_color)
        c0.h -= 0.04166666666666667
        c1 = Color(w.velvet_color)
        c1.h -= 0.04166666666666667
        
        while(len(cl.layers) > 0):
            bpy.ops.maxwell_render.material_editor_remove_layer()
        
        bpy.ops.maxwell_render.material_editor_add_layer()
        li = cl.layers[0]
        li.name = "Base"
        li.emitter
        l = li.layer
        bi = l.bsdfs.bsdfs[0]
        bi.coating
        b = bi.bsdf
        b.reflectance_0 = c0
        b.reflectance_90 = c0
        b.nd = 3.0
        b.roughness = 97.0
        
        bpy.ops.maxwell_render.material_editor_add_layer()
        li = cl.layers[0]
        li.name = "Sheen"
        li.emitter
        l = li.layer
        l.blending = '1'
        l.opacity = 20.0
        bi = l.bsdfs.bsdfs[0]
        bi.coating
        b = bi.bsdf
        b.reflectance_0 = c1
        b.reflectance_90 = c1
        b.nd = 1.250
        b.force_fresnel = True
        b.roughness = 60.0
        b.anisotropy = 100.0
        b.anisotropy_angle = math.radians(90.0)
        
        bpy.ops.maxwell_render.material_editor_add_layer()
        li = cl.layers[0]
        li.name = "Microfiber"
        li.emitter
        l = li.layer
        l.blending = '1'
        l.opacity = 80.0
        bi = l.bsdfs.bsdfs[0]
        bi.coating
        b = bi.bsdf
        b.reflectance_0 = (0.0, 0.0, 0.0)
        b.reflectance_90 = (1.0, 1.0, 1.0)
        b.nd = 5.0
        b.force_fresnel = False
        b.r2_enabled = True
        b.r2_falloff_angle = math.radians(79.0)
        b.roughness = 90.0
        
        w.types = 'NONE'
        
        return {'FINISHED'}
    
    # def invoke(self, context, event):
    #     return context.window_manager.invoke_props_dialog(self)


class MaterialWizardTextured(Operator):
    bl_idname = "maxwell_render.material_wizard_textured"
    bl_label = "Textured"
    bl_description = "Material wizard: Textured"
    
    # diffuse = StringProperty(name="Diffuse Map", default="", subtype='FILE_PATH', )
    # specular = StringProperty(name="Specular Map", default="", subtype='FILE_PATH', )
    # bump = StringProperty(name="Bump Map", default="", subtype='FILE_PATH', )
    # bump_strength = FloatProperty(name="Bump Strength", default=20.0, min=0.0, max=200.0, precision=2, )
    # normal = StringProperty(name="Normal Map", default="", subtype='FILE_PATH', )
    # alpha = StringProperty(name="Alpha Map", default="", subtype='FILE_PATH', )
    
    # @classmethod
    # def poll(cls, context):
    #     return True
    #
    # def draw(self, context):
    #     l = self.layout
    #     l.prop(self, 'diffuse')
    #     l.prop(self, 'specular')
    #     l.prop(self, 'bump')
    #     l.prop(self, 'bump_strength')
    #     l.prop(self, 'normal')
    #     l.prop(self, 'alpha')
    
    def execute(self, context):
        mat = context.material
        mx = mat.maxwell_render
        w = mx.wizards
        cl = mx.custom_layers
        
        while(len(cl.layers) > 0):
            bpy.ops.maxwell_render.material_editor_remove_layer()
        
        def texture(m, n, p, sn):
            ts = m.texture_slots
            s = ts.create(sn)
            t = bpy.data.textures.new(n, 'IMAGE')
            s.texture = t
            i = bpy.data.images.load(p)
            t.image = i
            return t.name
        
        dmap = ""
        smap = ""
        bmap = ""
        nmap = ""
        amap = ""
        if(w.textured_diffuse):
            dmap = texture(mat, 'diffuse map', w.textured_diffuse, 0, )
        if(w.textured_specular):
            smap = texture(mat, 'specular map', w.textured_specular, 1, )
        if(w.textured_bump):
            bmap = texture(mat, 'bump map', w.textured_bump, 3, )
        if(w.textured_normal):
            nmap = texture(mat, 'normal map', w.textured_normal, 4, )
        if(w.textured_alpha):
            amap = texture(mat, 'alpha map', w.textured_alpha, 5, )
        
        if(w.textured_normal):
            mx.global_bump_map = nmap
            mx.global_bump_map_use_normal = True
            mx.global_bump_normal = 100.0
        
        bpy.ops.maxwell_render.material_editor_add_layer()
        li = cl.layers[0]
        li.name = "Base"
        li.emitter
        l = li.layer
        bi = l.bsdfs.bsdfs[0]
        bi.coating
        b = bi.bsdf
        b.reflectance_0 = (0.0, 0.0, 0.0)
        b.reflectance_90 = (0.0, 0.0, 0.0)
        if(w.textured_diffuse):
            t = dmap
            b.reflectance_0_map_enabled = True
            b.reflectance_0_map = t
            b.reflectance_90_map_enabled = True
            b.reflectance_90_map = t
        b.nd = 3.0
        b.roughness = 97.0
        if(w.textured_bump):
            b.bump = w.textured_bump_strength
            b.bump_map_enabled = True
            b.bump_map = bmap
        
        bpy.ops.maxwell_render.material_editor_add_layer()
        li = cl.layers[0]
        li.name = "Specular"
        li.emitter
        l = li.layer
        l.blending = '1'
        if(w.textured_specular):
            l.opacity = 100.0
            l.opacity_map_enabled = True
            l.opacity_map = smap
        bi = l.bsdfs.bsdfs[0]
        bi.coating
        b = bi.bsdf
        b.reflectance_0 = (0.0, 0.0, 0.0)
        b.reflectance_90 = (0.0, 0.0, 0.0)
        b.nd = 1.5
        b.force_fresnel = True
        b.roughness = 0.0
        if(w.textured_specular):
            b.roughness = 50.0
            b.roughness_map_enabled = True
            b.roughness_map = texture(mat, 'specular map inverted', w.textured_specular, 2, )
            bpy.data.textures[b.roughness_map].maxwell_render.invert = True
        if(w.textured_bump):
            b.bump = w.textured_bump_strength
            b.bump_map_enabled = True
            b.bump_map = bmap
        
        if(w.textured_alpha):
            bpy.ops.maxwell_render.material_editor_add_layer()
            li = cl.layers[0]
            li.name = "Alpha"
            li.emitter
            l = li.layer
            bi = l.bsdfs.bsdfs[0]
            bi.coating
            b = bi.bsdf
            b.reflectance_0 = (0.0, 0.0, 0.0)
            b.reflectance_90 = (0.0, 0.0, 0.0)
            b.transmittance = (1.0, 1.0, 1.0)
            b.nd = 1.0
            b.roughness = 0.0
        
        w.types = 'NONE'
        
        return {'FINISHED'}
    
    # def invoke(self, context, event):
    #     return context.window_manager.invoke_props_dialog(self)


class MXSReferenceCache():
    __cache = {}
    
    @classmethod
    def add(cls, data, ):
        cls.__cache[uuid.uuid1()] = data
    
    @classmethod
    def get(cls, path, ob, ):
        for k, v in cls.__cache.items():
            if(v['path'] == path and v['object'] == ob):
                return v
        return None
    
    @classmethod
    def set(cls, path, ob, data, ):
        for k, v in cls.__cache.items():
            if(v['path'] == path and v['object'] == ob):
                break
        cls.__cache[k] = data
    
    @classmethod
    def draw(cls, path, value, context, refresh=False, ):
        r = None
        ob = context.active_object
        if(refresh and value):
            c = bpy.context.copy()
            bpy.ops.maxwell_render.read_mxs_reference(c, refresh=True, )
            r = cls.get(path, ob)
        else:
            r = cls.get(path, ob)
            if(r is None):
                c = bpy.context.copy()
                bpy.ops.maxwell_render.read_mxs_reference(c)
                r = cls.get(path, ob)
        
        if(r is None):
            return
        
        r['draw'] = value
        cls.set(path, ob, r)
        
        if(value):
            cls.start()
        else:
            cls.stop()
    
    @classmethod
    def all(cls):
        d = {}
        for k, v in cls.__cache.items():
            d[k] = v
        return d
    
    @classmethod
    def start(cls):
        a = cls.all()
        b = [r['draw'] for p, r in a.items()]
        display = bpy.context.scene.maxwell_render.private_draw_references
        if(sum(b) > 0 and display < 1):
            bpy.ops.maxwell_render.modal_draw_mxs_references('INVOKE_DEFAULT')
    
    @classmethod
    def stop(cls):
        a = cls.all()
        b = [r['draw'] for p, r in a.items()]
        display = bpy.context.scene.maxwell_render.private_draw_references
        if(sum(b) == 0 and display == 1):
            bpy.ops.maxwell_render.modal_draw_mxs_references('INVOKE_DEFAULT')
    
    @classmethod
    def quit(cls):
        for k, r in cls.__cache.items():
            cls.__cache[k]['draw'] = False
        display = bpy.context.scene.maxwell_render.private_draw_references
        if(display == 1):
            bpy.ops.maxwell_render.modal_draw_mxs_references('INVOKE_DEFAULT')


class ReadMXSReference(Operator):
    bl_idname = "maxwell_render.read_mxs_reference"
    bl_label = 'Read MXS Reference'
    bl_description = ''
    
    refresh = BoolProperty(name="Refresh", default=False, )
    
    def _base_and_pivot_to_matrix(self, base, pivot, ):
        from bpy_extras import io_utils
        am = io_utils.axis_conversion(from_forward='-Z', from_up='Y', to_forward='Y', to_up='Z', ).to_4x4()
        
        def cbase_to_matrix4(cbase):
            o = cbase[0]
            x = cbase[1]
            y = cbase[2]
            z = cbase[3]
            m = Matrix([(x[0], y[0], z[0], o[0]),
                        (x[1], y[1], z[1], o[1]),
                        (x[2], y[2], z[2], o[2]),
                        (0.0, 0.0, 0.0, 1.0)])
            return m
        
        bm = cbase_to_matrix4(base)
        pm = cbase_to_matrix4(pivot)
        m = am * bm * pm
        return m
    
    def _process_data(self, context, data, path):
        vertices = []
        for ob in data:
            vs = [Vector(v) for v in ob['vertices']]
            m = self._base_and_pivot_to_matrix(ob['base'], ob['pivot'])
            mvs = [m * v for v in vs]
            vertices.extend(mvs)
        # shuffle point to get random points when limiting visibility
        vertices = [v.to_tuple() for v in vertices]
        random.shuffle(vertices)
        
        blocs = vertices[:]
        a = list(map(min, zip(*blocs)))
        b = list(map(max, zip(*blocs)))
        
        d = {'vertices': vertices,
             'bound_box': [[a[0], a[1], a[2]],
                           [a[0], a[1], b[2]],
                           [a[0], b[1], b[2]],
                           [a[0], b[1], a[2]],
                           [b[0], a[1], a[2]],
                           [b[0], a[1], b[2]],
                           [b[0], b[1], b[2]],
                           [b[0], b[1], a[2]], ],
             'object': context.active_object,
             'path': path,
             'draw': False, }
        return d
    
    def execute(self, context):
        o = context.active_object
        if(o is None):
            return {'CANCELLED'}
        m = o.maxwell_render.reference
        if(not m.enabled):
            return {'CANCELLED'}
        
        p = os.path.realpath(bpy.path.abspath(m.path))
        
        if(system.PLATFORM == 'Darwin'):
            if(self.refresh):
                data = system.python34_run_read_mxs_reference(p)
                d = self._process_data(context, data, p)
                MXSReferenceCache.add(d)
            else:
                if(MXSReferenceCache.get(p, o)):
                    pass
                else:
                    data = system.python34_run_read_mxs_reference(p)
                    d = self._process_data(context, data, p)
                    MXSReferenceCache.add(d)
        elif(system.PLATFORM == 'Linux' or system.PLATFORM == 'Windows'):
            from . import mxs
            if(self.refresh):
                r = mxs.MXSReferenceReader(p)
                data = r.data
                d = self._process_data(context, data, p)
                MXSReferenceCache.add(d)
            else:
                if(MXSReferenceCache.get(p, o)):
                    pass
                else:
                    r = mxs.MXSReferenceReader(p)
                    data = r.data
                    d = self._process_data(context, data, p)
                    MXSReferenceCache.add(d)
        else:
            pass
        
        return {'FINISHED'}


def mxs_reference_draw_callback(self, context):
    ao = bpy.context.active_object
    sel = [o for o in bpy.context.scene.objects if o.select]
    
    def check_visibility(o):
        if(o.hide):
            return False
        
        layers = context.scene.layers
        # if(o.hide_render is True):
        #     return False
        s = None
        r = None
        for i, l in enumerate(o.layers):
            if(layers[i] is True and l is True):
                s = True
                break
        # for i, l in enumerate(o.layers):
        #     if(render_layers[i] is True and l is True):
        #         r = True
        #         break
        # if(s and r):
        #     return True
        if(s):
            return True
        return False
    
    d = MXSReferenceCache.all()
    for k, v in d.items():
        if(not v['draw']):
            continue
        
        ob = v['object']
        if(not check_visibility(ob)):
            continue
        
        active = False
        selected = False
        if(ao == ob):
            active = True
        if(ob in sel):
            selected = True
        
        mx = ob.maxwell_render.reference
        mat = ob.matrix_world
        
        points = v['vertices']
        bound_box = v['bound_box']
        
        percent = int((len(points) / 100) * mx.display_percent)
        if(percent > mx.display_max_points):
            points = points[:mx.display_max_points]
        else:
            points = points[:percent]
        
        locs = [mat * Vector(p) for p in points]
        bbox = [mat * Vector(b) for b in bound_box]
        
        # point cloud
        bgl.glPointSize(mx.point_size)
        if(active):
            bgl.glColor3f(*mx.point_color_active)
        elif(selected):
            bgl.glColor3f(*mx.point_color_selected)
        else:
            bgl.glColor3f(*mx.point_color)
        bgl.glBegin(bgl.GL_POINTS)
        for l in locs:
            bgl.glVertex3f(*l)
        bgl.glEnd()
        
        # bounding box
        if(active):
            bgl.glColor3f(*mx.bbox_color_active)
        elif(selected):
            bgl.glColor3f(*mx.bbox_color_selected)
        else:
            bgl.glColor3f(*mx.bbox_color)
        bgl.glLineWidth(mx.bbox_line_width)
        if(mx.bbox_line_stipple):
            bgl.glEnable(bgl.GL_LINE_STIPPLE)
            bgl.glLineStipple(4, 0xAAAA)
        
        bgl.glBegin(bgl.GL_LINE_STRIP)
        bgl.glVertex3f(*bbox[0])
        bgl.glVertex3f(*bbox[1])
        bgl.glVertex3f(*bbox[2])
        bgl.glVertex3f(*bbox[3])
        bgl.glVertex3f(*bbox[0])
        bgl.glVertex3f(*bbox[4])
        bgl.glVertex3f(*bbox[5])
        bgl.glVertex3f(*bbox[6])
        bgl.glVertex3f(*bbox[7])
        bgl.glVertex3f(*bbox[4])
        bgl.glEnd()
        
        bgl.glBegin(bgl.GL_LINES)
        bgl.glVertex3f(*bbox[1])
        bgl.glVertex3f(*bbox[5])
        bgl.glVertex3f(*bbox[2])
        bgl.glVertex3f(*bbox[6])
        bgl.glVertex3f(*bbox[3])
        bgl.glVertex3f(*bbox[7])
        bgl.glEnd()
        
        # defaults..
        bgl.glLineWidth(1)
        bgl.glColor3f(0.0, 0.0, 0.0, )
        bgl.glDisable(bgl.GL_LINE_STIPPLE)
        bgl.glLineStipple(1, 0xAAAA)
        bgl.glPointSize(1.0)


class ModalDrawMXSReferences(Operator):
    bl_idname = "maxwell_render.modal_draw_mxs_references"
    bl_label = "Modal Draw MXS References"
    
    def modal(self, context, event):
        m = context.scene.maxwell_render
        if(context.area):
            context.area.tag_redraw()
        if(m.private_draw_references == -1):
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            m.private_draw_references = 0
            return {'CANCELLED'}
        return {'PASS_THROUGH'}
    
    def invoke(self, context, event):
        m = context.scene.maxwell_render
        if(context.area.type == 'VIEW_3D'):
            if(m.private_draw_references < 1):
                m.private_draw_references = 1
                self._handle = bpy.types.SpaceView3D.draw_handler_add(mxs_reference_draw_callback, (self, context, ), 'WINDOW', 'POST_VIEW')
                context.window_manager.modal_handler_add(self)
                return {'RUNNING_MODAL'}
            else:
                m.private_draw_references = -1
                return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


if(True):
    # strange, isn't it. but i want to have this piece of code folded in Textmate..
    from bpy.app.handlers import persistent
    
    @persistent
    def load_handler(dummy):
        MXSReferenceCache.quit()
    
    # pre load handler to stop drawing mxs references. loading new blend while displaying reference in viewport will crash blender
    # according to documentation, handler are removed when loading new files (https://www.blender.org/api/blender_python_api_current/bpy.app.handlers.html)
    bpy.app.handlers.load_pre.append(load_handler)


class ExecuteMaxwellPreset(Operator):
    """Execute a preset"""
    
    # https://git.blender.org/gitweb/gitweb.cgi/blender.git/blob/HEAD:/release/scripts/startup/bl_operators/presets.py
    
    bl_idname = "maxwell_render.execute_preset"
    bl_label = "Execute a Python Preset"
    
    filepath = StringProperty(subtype='FILE_PATH', options={'SKIP_SAVE'}, )
    
    def execute(self, context):
        from os.path import basename, splitext
        filepath = self.filepath
        ext = splitext(filepath)[1].lower()
        if ext == ".py":
            bpy.ops.script.python_file_run(filepath=filepath)
        else:
            self.report({'ERROR'}, "unknown filetype: %r" % ext)
            return {'CANCELLED'}
        return {'FINISHED'}


class Render_preset_add(AddPresetBase, Operator):
    """Add a new render preset."""
    bl_idname = 'maxwell_render.render_preset_add'
    bl_label = 'Add/Remove Render Preset'
    preset_menu = 'Render_presets'
    preset_subdir = 'blendmaxwell/render'
    preset_defines = ["m = bpy.context.scene.maxwell_render", ]
    preset_values = ["m.scene_time", "m.scene_sampling_level", "m.scene_multilight", "m.scene_multilight_type", "m.scene_cpu_threads",
                     "m.scene_quality", "m.output_depth", "m.output_image_enabled", "m.output_mxi_enabled", "m.materials_override",
                     "m.materials_override_path", "m.materials_search_path", "m.materials_directory", "m.globals_motion_blur",
                     "m.globals_diplacement", "m.globals_dispersion", "m.tone_color_space", "m.tone_burn", "m.tone_gamma",
                     "m.tone_sharpness", "m.tone_sharpness_value", "m.tone_whitepoint", "m.tone_tint", "m.simulens_aperture_map",
                     "m.simulens_obstacle_map", "m.simulens_diffraction", "m.simulens_diffraction_value", "m.simulens_frequency",
                     "m.simulens_scattering", "m.simulens_scattering_value", "m.simulens_devignetting", "m.simulens_devignetting_value",
                     "m.illum_caustics_illumination", "m.illum_caustics_refl_caustics", "m.illum_caustics_refr_caustics", ]


class Channels_preset_add(AddPresetBase, Operator):
    """Add a new channels preset."""
    bl_idname = 'maxwell_render.channels_preset_add'
    bl_label = 'Add/Remove Channels Preset'
    preset_menu = 'Channels_presets'
    preset_subdir = 'blendmaxwell/channels'
    preset_defines = ["m = bpy.context.scene.maxwell_render", ]
    preset_values = ["m.channels_output_mode", "m.channels_render", "m.channels_render_type", "m.channels_alpha", "m.channels_alpha_file",
                     "m.channels_alpha_opaque", "m.channels_z_buffer", "m.channels_z_buffer_file", "m.channels_z_buffer_near",
                     "m.channels_z_buffer_far", "m.channels_shadow", "m.channels_shadow_file", "m.channels_material_id",
                     "m.channels_material_id_file", "m.channels_object_id", "m.channels_object_id_file", "m.channels_motion_vector",
                     "m.channels_motion_vector_file", "m.channels_roughness", "m.channels_roughness_file", "m.channels_fresnel",
                     "m.channels_fresnel_file", "m.channels_normals", "m.channels_normals_file", "m.channels_normals_space",
                     "m.channels_position", "m.channels_position_file", "m.channels_position_space", "m.channels_deep",
                     "m.channels_deep_file", "m.channels_deep_type", "m.channels_deep_min_dist", "m.channels_deep_max_samples",
                     "m.channels_uv", "m.channels_uv_file", "m.channels_custom_alpha", "m.channels_custom_alpha_file",
                     "m.channels_reflectance", "m.channels_reflectance_file", ]


class Environment_preset_add(AddPresetBase, Operator):
    """Add a new environment preset."""
    bl_idname = 'maxwell_render.environment_preset_add'
    bl_label = 'Add/Remove Environment Preset'
    preset_menu = 'Environment_presets'
    preset_subdir = 'blendmaxwell/environment'
    preset_defines = ["m = bpy.context.world.maxwell_render", ]
    preset_values = ['m.env_type', 'm.sky_type', 'm.sky_use_preset', 'm.sky_preset', 'm.sky_intensity', 'm.sky_planet_refl', 'm.sky_ozone',
                     'm.sky_water', 'm.sky_turbidity_coeff', 'm.sky_wavelength_exp', 'm.sky_reflectance', 'm.sky_asymmetry', 'm.sun_type',
                     'm.sun_power', 'm.sun_radius_factor', 'm.sun_color', 'm.sun_temp', 'm.sun_location_type', 'm.sun_latlong_lat',
                     'm.sun_latlong_lon', 'm.sun_date', 'm.sun_time', 'm.sun_latlong_gmt', 'm.sun_latlong_gmt_auto',
                     'm.sun_latlong_ground_rotation', 'm.sun_angles_zenith', 'm.sun_angles_azimuth', 'm.sun_dir_x', 'm.sun_dir_y',
                     'm.sun_dir_z', 'm.ibl_intensity', 'm.ibl_interpolation', 'm.ibl_screen_mapping', 'm.ibl_bg_type', 'm.ibl_bg_map',
                     'm.ibl_bg_intensity', 'm.ibl_bg_scale_x', 'm.ibl_bg_scale_y', 'm.ibl_bg_offset_x', 'm.ibl_bg_offset_y',
                     'm.ibl_refl_type', 'm.ibl_refl_map', 'm.ibl_refl_intensity', 'm.ibl_refl_scale_x', 'm.ibl_refl_scale_y',
                     'm.ibl_refl_offset_x', 'm.ibl_refl_offset_y', 'm.ibl_refr_type', 'm.ibl_refr_map', 'm.ibl_refr_intensity',
                     'm.ibl_refr_scale_x', 'm.ibl_refr_scale_y', 'm.ibl_refr_offset_x', 'm.ibl_refr_offset_y', 'm.ibl_illum_type',
                     'm.ibl_illum_map', 'm.ibl_illum_intensity', 'm.ibl_illum_scale_x', 'm.ibl_illum_scale_y', 'm.ibl_illum_offset_x',
                     'm.ibl_illum_offset_y', ]


class Camera_preset_add(AddPresetBase, Operator):
    """Add a new camera preset."""
    bl_idname = 'maxwell_render.camera_preset_add'
    bl_label = 'Add/Remove Camera Preset'
    preset_menu = 'Camera_presets'
    preset_subdir = 'blendmaxwell/camera'
    preset_defines = ["m = bpy.context.camera.maxwell_render", "o = bpy.context.camera", "r = bpy.context.scene.render", ]
    preset_values = ["m.lens", "m.shutter", "m.fstop", "m.fov", "m.azimuth", "m.angle", "m.iso", "m.screen_region", "m.screen_region_x",
                     "m.screen_region_y", "m.screen_region_w", "m.screen_region_h", "m.aperture", "m.diaphragm_blades", "m.diaphragm_angle",
                     "m.custom_bokeh", "m.bokeh_ratio", "m.bokeh_angle", "m.shutter_angle", "m.frame_rate", "m.zclip", "m.hide", "m.response",
                     
                     "o.dof_distance", "o.lens", "o.sensor_width", "o.sensor_height", "o.sensor_fit", "o.clip_start",
                     "o.clip_end", "o.shift_x", "o.shift_y",
                     
                     "r.resolution_x", "r.resolution_y", "r.resolution_percentage", "r.pixel_aspect_x", "r.pixel_aspect_y",
                     "r.fps", "r.fps_base", ]


class TextureProceduralAdd(Operator):
    bl_idname = "maxwell_render.texture_procedural_add"
    bl_label = "Add Procedural Texture"
    bl_description = "Add Procedural Texture"
    bl_options = {'REGISTER', 'UNDO'}
    
    name = StringProperty(name="Name", )
    use = EnumProperty(name="Type", items=[('BRICK', "Brick", ""), ('CHECKER', "Checker", ""), ('CIRCLE', "Circle", ""), ('GRADIENT3', "Gradient3", ""),
                                           ('GRADIENT', "Gradient", ""), ('GRID', "Grid", ""), ('MARBLE', "Marble", ""), ('NOISE', "Noise", ""),
                                           ('VORONOI', "Voronoi", ""), ('TILED', "Tiled", ""), ('WIREFRAME', "Wireframe", ""), ], default='NOISE', )
    
    def execute(self, context):
        mx = context.texture.maxwell_render
        pt = mx.procedural.textures
        item = pt.add()
        item.name = self.name
        item.use = self.use
        mx.procedural.index = (len(pt) - 1)
        return {'FINISHED'}


class TextureProceduralRemove(Operator):
    bl_idname = "maxwell_render.texture_procedural_remove"
    bl_label = "Remove Procedural Texture"
    bl_description = "Remove Procedural Texture"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mx = context.texture.maxwell_render
        pt = mx.procedural.textures
        idx = mx.procedural.index
        try:
            item = pt[idx]
        except IndexError:
            return {'CANCELLED'}
        mx.procedural.index -= 1
        pt.remove(idx)
        if(idx == 0):
            mx.procedural.index = idx
        if(len(pt) == 0):
            mx.procedural.index = -1
        return {'FINISHED'}


class TextureProceduralClear(Operator):
    bl_idname = "maxwell_render.texture_procedural_clear"
    bl_label = "Remove All Procedural Textures"
    bl_description = "Remove All Procedural Textures"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mx = context.texture.maxwell_render
        pt = mx.procedural.textures
        while(len(pt) > 0):
            pt.remove(0)
        mx.procedural.index = -1
        return {'FINISHED'}


class TextureProceduralMoveUp(Operator):
    bl_idname = "maxwell_render.texture_procedural_move_up"
    bl_label = "Move Selected Procedural Texture Up"
    bl_description = "Move selected procedural texture up"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mx = context.texture.maxwell_render
        pt = mx.procedural.textures
        idx = mx.procedural.index
        
        try:
            item = pt[idx]
        except IndexError:
            return {'CANCELLED'}
        
        if(idx >= 1):
            mv = idx - 1
            pt.move(mv, idx, )
            mx.procedural.index = mv
            return {'FINISHED'}
        
        return {'PASS_THROUGH'}


class TextureProceduralMoveDown(Operator):
    bl_idname = "maxwell_render.texture_procedural_move_down"
    bl_label = "Move Selected Procedural Texture Down"
    bl_description = "Move selected procedural texture down"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        mx = context.texture.maxwell_render
        pt = mx.procedural.textures
        idx = mx.procedural.index
        try:
            item = pt[idx]
        except IndexError:
            return {'CANCELLED'}
        
        if(idx < len(pt) - 1):
            mv = idx + 1
            pt.move(idx, mv, )
            mx.procedural.index = mv
            return {'FINISHED'}
        
        return {'PASS_THROUGH'}


class ProceduralTextures_preset_add(AddPresetBase, Operator):
    """Add a new procedural texture preset."""
    bl_idname = 'maxwell_render.procedural_textures_preset_add'
    bl_label = 'Add/Remove Procedural Texture Preset'
    preset_menu = 'ProceduralTextures_presets'
    preset_subdir = 'blendmaxwell/procedural_textures'
    preset_defines = ["m = bpy.context.texture.maxwell_render.procedural.textures[bpy.context.texture.maxwell_render.procedural.index]", ]
    preset_values = ["m.brick_brick_width", "m.brick_brick_height", "m.brick_brick_offset", "m.brick_random_offset", "m.brick_double_brick", "m.brick_small_brick_width",
                     "m.brick_round_corners", "m.brick_boundary_sharpness_u", "m.brick_boundary_sharpness_v", "m.brick_boundary_noise_detail", "m.brick_boundary_noise_region_u",
                     "m.brick_boundary_noise_region_v", "m.brick_seed", "m.brick_random_rotation", "m.brick_color_variation", "m.brick_brick_color_0", "m.brick_brick_texture_0",
                     "m.brick_sampling_factor_0", "m.brick_weight_0", "m.brick_brick_color_1", "m.brick_brick_texture_1", "m.brick_sampling_factor_1", "m.brick_weight_1",
                     "m.brick_brick_color_2", "m.brick_brick_texture_2", "m.brick_sampling_factor_2", "m.brick_weight_2", "m.brick_mortar_thickness", "m.brick_mortar_color",
                     "m.brick_mortar_texture",
                     "m.checker_number_of_elements_u", "m.checker_number_of_elements_v", "m.checker_color_0", "m.checker_color_1", "m.checker_transition_sharpness", "m.checker_falloff",
                     "m.circle_background_color", "m.circle_circle_color", "m.circle_radius_u", "m.circle_radius_v", "m.circle_transition_factor", "m.circle_falloff",
                     "m.gradient3_gradient_u", "m.gradient3_color0_u", "m.gradient3_color1_u", "m.gradient3_color2_u", "m.gradient3_gradient_type_u", "m.gradient3_color1_u_position",
                     "m.gradient3_gradient_v", "m.gradient3_color0_v", "m.gradient3_color1_v", "m.gradient3_color2_v", "m.gradient3_gradient_type_v", "m.gradient3_color1_v_position",
                     "m.gradient_gradient_u", "m.gradient_color0_u", "m.gradient_color1_u", "m.gradient_gradient_type_u", "m.gradient_transition_factor_u", "m.gradient_gradient_v",
                     "m.gradient_color0_v", "m.gradient_color1_v", "m.gradient_gradient_type_v", "m.gradient_transition_factor_v",
                     "m.grid_horizontal_lines", "m.grid_vertical_lines", "m.grid_cell_width", "m.grid_cell_height", "m.grid_boundary_thickness_u", "m.grid_boundary_thickness_v",
                     "m.grid_transition_sharpness", "m.grid_cell_color", "m.grid_boundary_color", "m.grid_falloff",
                     "m.marble_coordinates_type", "m.marble_color0", "m.marble_color1", "m.marble_color2", "m.marble_frequency", "m.marble_detail", "m.marble_octaves", "m.marble_seed",
                     "m.noise_coordinates_type", "m.noise_noise_color", "m.noise_background_color", "m.noise_detail", "m.noise_persistance", "m.noise_octaves", "m.noise_low_value",
                     "m.noise_high_value", "m.noise_seed",
                     "m.voronoi_coordinates_type", "m.voronoi_color0", "m.voronoi_color1", "m.voronoi_detail", "m.voronoi_distance", "m.voronoi_combination", "m.voronoi_low_value",
                     "m.voronoi_high_value", "m.voronoi_seed",
                     "m.tiled_filename", "m.tiled_token_mask", "m.tiled_base_color", "m.tiled_use_base_color",
                     "m.wireframe_fill_color", "m.wireframe_edge_color", "m.wireframe_coplanar_edge_color", "m.wireframe_edge_width", "m.wireframe_coplanar_edge_width",
                     "m.wireframe_coplanar_threshold",
                     "m.enabled", "m.blending_factor", "m.use", ]
