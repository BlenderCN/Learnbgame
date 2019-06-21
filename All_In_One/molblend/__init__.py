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


#  Author: Florian Altvater (florian.altvater@gmail.com
#
#  Start of project              : 2014-03-28

#  Acknowledgements/Inspirations
#  =============================
#  Fluid Designer scripts
#  pbd/xyz-import addons by Clemens Barth
#  cellblender

bl_info = {
    "name": "MolBlend",
    "description": "Work with chemical structures",
    "author": "Florian Brown-Altvater",
    "version": (0,1),
    "blender": (2,7,9),
    "location": "View3D > Tool Shelf > MolBlend",
    "warning": "under heavy development",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Add Mesh"
}

if "bpy" in locals():
    import importlib
    importlib.reload(mb_datastructure)
    importlib.reload(mb_operators)
else:
    from molblend import mb_datastructure
    from molblend import mb_operators

import logging
import os
import subprocess
import json

import bpy
from bpy.types import Panel, AddonPreferences
from bpy.props import (StringProperty,
                       BoolProperty,
                       EnumProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       PointerProperty,
                       CollectionProperty)
from bpy.app.handlers import persistent
from mathutils import Vector, Matrix

log_path = os.path.join(bpy.context.user_preferences.filepaths.temporary_directory, "molblend_log.txt")
log_is_writeable = True

try:
    test_writing = open(log_path, 'w')
    test_writing.close()
except:
    print("WARNING: Writing permission error for {0}".format(log_path))
    print("The log will be redirected to the console (here)")
    log_is_writeable = False

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s:%(name)-12s:%(levelname)-8s:%(filename)-20s: %(message)s')
if logger.getEffectiveLevel() == logging.DEBUG:
    term_formatter = logging.Formatter('%(asctime)s:%(levelname)-8s:%(filename)-20s: %(message)s')
else:
    term_formatter = logging.Formatter('%(name)s: %(levelname)-8s: %(message)s')

chandler = logging.StreamHandler()
chandler.setLevel(logging.DEBUG)
chandler.setFormatter(term_formatter)

if log_is_writeable:
    fhandler = logging.FileHandler(log_path, mode ='w')
    fhandler.setLevel(logging.INFO)
    fhandler.setFormatter(file_formatter)

# avoid duplicate handlers if addon is reloaded in Blender (via F8)
if not len(logger.handlers):
    logger.addHandler(chandler)
    logger.addHandler(fhandler)

logger.info("Writing log to file {}".format(log_path))

logger.warning('name: {}'.format(__name__))

class MolBlendPreferences(AddonPreferences):
    bl_idname = __name__

    pymcubes_path = StringProperty(
            name="PyMcubes path",
            subtype='FILE_PATH',
            description='path in which pymcubes module resides'
            )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "pymcubes_path")

class MolBlendPanel():
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MolBlend"

class MolBlendPropsPanel():
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Molecule"

class MB_PT_initialize(MolBlendPanel, Panel):
    bl_label = "MolBlend"
    
    @classmethod
    def poll(cls, context):
        return not context.scene.mb.is_initialized
    
    def draw(self, context):
        layout = self.layout
        layout.operator("mb.initialize")


class MB_PT_import(MolBlendPanel, Panel):
    bl_label = "Import"
    
    @classmethod
    def poll(cls, context):
        return context.scene.mb.is_initialized
    
    def draw(self, context):
        initialized = len(context.scene.mb.elements) > 0
        
        mb = context.scene.mb.globals
        layout = self.layout
        layout.operator("mb.import_molecules")
        layout.operator("mb.import_cube_iso")


class MB_PT_tools(MolBlendPanel, Panel):
    bl_label = "Tools"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return context.scene.mb.is_initialized
    
    def draw(self, context):
        layout = self.layout
       
        modal = mb_operators.MB_OT_modal_add.is_running()
        label = "ESC to stop" if modal == True else "Draw atoms"
        layout.operator("mb.modal_add", text=label)
        #--- tools -----------------------------------------------------------#
        split = layout.split(0.4)
        col = split.column()
        col.label("Add")
        col.label("Geometry")
        col = split.column()
        col.prop(context.scene.mb.globals, "element_to_add", text="")
        col.prop(context.scene.mb.globals, "geometry_to_add", text="")
        layout.operator("mb.select_bonded")
        layout.operator("mb.select_molecule")
        layout.operator("mb.combine_molecules")
        layout.prop(context.scene.mb.globals, "show_bond_lengths")
        layout.prop(context.scene.mb.globals, "bond_length_font_size",
                    text="Font size")
        
        layout.separator()
        layout.operator("mb.make_static")
        layout.operator("mb.apply_scale")


class MB_PT_molecule_properties(MolBlendPropsPanel, Panel):
    bl_label = "Molecule properties"
    
    @classmethod
    def poll(cls, context):
        active_ob = context.object or context.scene.mb.modal_last_active
        return (context.scene.mb.is_initialized 
                and hasattr(active_ob, 'mb') and active_ob.mb.get_molecule())
    
    def draw(self, context):
        layout = self.layout
        active_ob = context.object or context.scene.mb.modal_last_active
        mol = active_ob.mb.get_molecule()
        mol.draw_properties(layout)


class MB_PT_molecule_draw_styles(MolBlendPropsPanel, Panel):
    bl_label = "Draw styles"
    
    @classmethod
    def poll(cls, context):
        active_ob = context.object or context.scene.mb.modal_last_active
        return (context.scene.mb.is_initialized
                and hasattr(active_ob, 'mb') and active_ob.mb.get_molecule())
    
    def draw(self, context):
        layout = self.layout
        active_ob = context.object or context.scene.mb.modal_last_active
        mol = active_ob.mb.get_molecule()
        mol.draw_styles(layout)


class MB_PT_atom(MolBlendPropsPanel, Panel):
    bl_label = "Atom properties"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        active_ob = context.object or context.scene.mb.modal_last_active
        return (context.scene.mb.is_initialized
                and hasattr(active_ob, 'mb') and active_ob.mb.type == 'ATOM')
   
    def draw(self, context):
        layout = self.layout
        active_ob = context.object or context.scene.mb.modal_last_active
        active_ob.mb.draw_properties(context, layout, active_ob)


class MB_PT_molecule_dipole(MolBlendPropsPanel, Panel):
    bl_label = "Dipole"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        active_ob = context.object or context.scene.mb.modal_last_active
        return (context.scene.mb.is_initialized 
                and hasattr(active_ob, 'mb') and active_ob.mb.get_molecule())
    
    def draw(self, context):
        layout = self.layout
        active_ob = context.object or context.scene.mb.modal_last_active
        mol = active_ob.mb.get_molecule()
        mol.draw_dipole_props(layout)


class MB_PT_molecule_unit_cell(MolBlendPropsPanel, Panel):
    bl_label = "Unit cell"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        active_ob = context.object or context.scene.mb.modal_last_active
        return (context.scene.mb.is_initialized 
                and hasattr(active_ob, 'mb') and active_ob.mb.get_molecule())
    
    def draw(self, context):
        layout = self.layout
        active_ob = context.object or context.scene.mb.modal_last_active
        mol = active_ob.mb.get_molecule()
        mol.draw_unit_cell_props(layout)


class MB_PT_vibration_properties(MolBlendPropsPanel, Panel):
    bl_label = "Vibrations"
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        active_ob = context.object or context.scene.mb.modal_last_active
        return (context.scene.mb.is_initialized
                and hasattr(active_ob, 'mb') and active_ob.mb.get_molecule())
    
    def draw(self, context):
        layout = self.layout
        active_ob = context.object or context.scene.mb.modal_last_active
        mol = active_ob.mb.get_molecule()
        mol.draw_vibrations(layout)


class MB_PT_view(MolBlendPanel, Panel):
    bl_label = "View"
    
    def draw(self, context):
        layout = self.layout
        #row.label("View")
        row = layout.row()
        row.label(icon='AXIS_TOP')
        row.operator("view3d.viewnumpad", text="Top").type = 'TOP'
        row.operator("view3d.viewnumpad", text="Bottom").type = 'BOTTOM'
        row = layout.row()
        row.label(icon='AXIS_FRONT')
        row.operator("view3d.viewnumpad", text="Front").type = 'FRONT'
        row.operator("view3d.viewnumpad", text="Back").type = 'BACK'
        row = layout.row()
        row.label(icon='AXIS_SIDE')
        row.operator("view3d.viewnumpad", text="Right").type = 'RIGHT'
        row.operator("view3d.viewnumpad", text="Left").type = 'LEFT'
        row = layout.row()
        row.label(icon='MANIPUL')
        row.operator("screen.region_quadview", text="Quadview")


class MB_PT_info(MolBlendPanel, Panel):
    global git_commit_id, git_timestamp, git_date
    bl_label = "Info"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        
        gc = context.scene.mb.info.git_commits
        
        layout = self.layout
        box = layout.box()
        box.label("Current git commit:")
        split = box.split(0.3)
        col = split.column()
        col.label("ID:")
        col.label("date:")
        col = split.column()
        col.label(git_commit_id[:6])
        col.label(git_date)
        if len(gc):
            box.label("Saved git commit:")
            split = box.split(0.3)
            col = split.column()
            col.label("ID:")
            col.label("date:")
            col = split.column()
            col.label(gc[-1].commit_id[:6])
            col.label(gc[-1].date)


def add_handler(handler_list, handler_function):
    """ Only add a handler if it's not already in the list """
    if not handler_function in handler_list:
        handler_list.append(handler_function)


def remove_handler(handler_list, handler_function):
    """ Only remove a handler if it's in the list """
    if handler_function in handler_list:
        handler_list.remove(handler_function)


def _minimal_ext_cmd(cmd):
    script_file = os.path.realpath(__file__)
    cwd = os.path.dirname(script_file)
    # construct minimal environment
    env = {}
    for k in ['SYSTEMROOT', 'PATH']:
        v = os.environ.get(k)
        if v is not None:
            env[k] = v
    # LANGUAGE is used on win32
    env['LANGUAGE'] = 'C'
    env['LANG'] = 'C'
    env['LC_ALL'] = 'C'
    pop = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env, cwd=cwd)
    out = pop.communicate()[0]
    return out


def git_version():
    # Return the git revision as a string
    try:
        out = _minimal_ext_cmd(['git', 'rev-parse', 'HEAD'])
        GIT_REVISION = out.strip().decode('ascii')
    except OSError:
        GIT_REVISION = "Unknown"
    return GIT_REVISION


def git_date():
    # Return the git commit date as a unix time stamp string.
    try:
        out = _minimal_ext_cmd(['git', 'show', '-s', '--format=%ct', 'HEAD'])
        GIT_TIMESTAMP = out.strip().decode('ascii')
        out = _minimal_ext_cmd(['git', 'show', '-s', '--format=%cd', 
                                '--date=short', 'HEAD'])
        GIT_DATE = out.strip().decode('ascii')
    except OSError:
        GIT_DATE = "Unknown"
        GIT_TIMESTAMP = "Unknown"
    return GIT_TIMESTAMP, GIT_DATE


git_commit_id = git_version()
git_timestamp, git_date = git_date()
logger.debug("git commit: {}, {}".format(git_commit_id[:6], git_date))


@persistent
def load_handler(dummy):
    global git_commit_id, git_timestamp, git_date
    for scn in bpy.data.scenes:
        if scn.mb.is_initialized:
            gc = bpy.context.scene.mb.info.git_commits
            if len(gc) == 0 or git_commit_id != gc[-1].commit_id:
                msg = "The current git commit is {} than the last one this"
                msg += " scene has seen."
                msg = msg.format("newer" if not len(gc) or gc[-1].time_stamp < git_timestamp
                                 else "older")
                logger.warning(msg)
                if len(gc):
                    msg = "last:    {}, {}".format(gc[-1].commit_id[:6], 
                                                   gc[-1].date)
                    logger.warning(msg)
                else:
                    logger.warning("last: this version didn't save commit id")
                logger.warning("current: {}, {}".format(git_commit_id[:6],
                                                        git_date))


@persistent
def save_handler(dummy):
    global git_commit_id, git_timestamp, git_date
    for scn in bpy.data.scenes:
        if scn.mb.is_initialized:
            commits = scn.mb.info.git_commits
            if len(commits) == 0 or git_commit_id != commits[-1].commit_id:
                c = commits.add()
                c.commit_id = git_commit_id
                c.time_stamp = git_timestamp
                c.date = git_date
                msg = "Added commit {} to scn.mb.info.git_commits"
                logger.debug(msg.format(git_commit_id))
    
    mb_cleanup()

def mb_cleanup():
    logger.debug("Cleaning up")
    delete = []
    for ob in bpy.data.objects:
        if ob.mb.type == 'PARENT':
            for scn in bpy.data.scenes:
                if ob.name in scn.objects:
                    break
            else:
                all_obs = ob.mb.molecule.objects.get_all_objects(with_parent=False)
                if not all_obs:
                    name = ob.name
                    for qv in ob.mb.qvecs:
                        if qv.mode_txt:
                            bpy.data.texts.remove(qv.mode_txt)
                    delete.append(ob)
                    logger.debug("Will delete molecule parent {}".format(name))
                else:
                    msg = "Parent {} not in scene, but still has objects:"
                    logger.debug(msg.format(ob.name))
                    for cob in all_obs:
                        logger.debug("{}".format(cob.name))
        elif ob.mb.type != "NONE" and not ob.mb.parent:
            logger.debug("{} has no mb.parent".format(ob.name))
    for ob in delete:
        for scn in bpy.data.scenes:
            if ob.name in scn.objects:
                scn.objects.unlink(ob)
        bpy.data.objects.remove(ob)
    # TODO handle objects whose parent got deleted
    for txt in bpy.data.texts:
        if txt.mb.type == "MODES" and not txt.mb.parent:
            bpy.data.texts.remove(txt)


def register():
    
    bpy.utils.register_module(__name__)
    mb_datastructure.register()
    
    add_handler(bpy.app.handlers.load_post, load_handler)
    add_handler(bpy.app.handlers.save_pre, save_handler)
    bpy.app.driver_namespace['Vector'] = Vector

def unregister():
    bpy.utils.unregister_module(__name__)
    mb_datastructure.unregister()
    
    remove_handler(bpy.app.handlers.load_post, load_handler)
    remove_handler(bpy.app.handlers.save_pre, save_handler)


if __name__ == "__main__":
    register()
