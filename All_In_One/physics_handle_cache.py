# ##### BEGIN GPL LICENSE BLOCK #####
#
# physics_handle_cache.py
# 'Customizabily' use information from .bobj/.bvel fluidsim cache files
# Copyright (C) 2016 Quentin Wenger
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

"""

Usage:
1) install and enable in Blender
2) load any client script into Blender's text editor
3) on an object with cached fluidsim, refresh the list of scripts
   in the physics properties / handle cache panel
4) enable the checkbox corresponding to any script
5) behavior at frame change / ... depends from the client script.

Generalities on writing client scripts:
- client scripts should define MAIN_CLASS in toplevel
- MAIN_CLASS should reference a callable taking "interfacer" and "name"
  as positional arguments and returning an instance with update(scene)
  method.
  "interfacer" is an instance with methods:
  - isActive(mname)
  - isClean()
  - getVelocity(frame)
  - getObject(frame)
  - getCurrentVelocity()
  - getCurrentObject()
  - getBlenderObject()
  "name" is a string corresponding to the name of the client script,
  to be passed into isActive if needed.

  methods get(Current)Object return an ObjectStructure instance with
  attributes
  - amount_verts    (int)
  - verts           (list of mathutils.Vector)
  - nors            (list of mathutils.Vector)
  - amount_tris     (int)
  - tris            (list of (int, int, int) tuples)
  - fname           (str or None)

  methods get(Current)Velocity return a VelocityStructure instance with
  attributes
  - amount_verts    (int)
  - vels            (list of mathutils.Vector)
  - fname           (str or None)

See ogl_velocitiesrenderer.py for an example of client script.

Limitations:
  - no handling of particles
  - only support for gzipped cache files.

Remarks:
  - if any of the .bobj/.bvel file is not found, an error message is shown;
    still one of them could return usable data, which is then available
  - if using custom file paths, specify the name without extension
    (i.e. cut before .bobj.gz/.bvel.gz); if wanted, use #'s to specify
    frame number; it will be padded with 0's to at least match the amount of #'s
  - local paths are supported.

"""


bl_info = {
    "name": "Handle cache",
    "author": "Quentin Wenger (Matpi)",
    "version": (1, 2),
    "blender": (2, 76, 0),
    "location": "Properties > Physics > Handle cache panel",
    "description": "Handle .bobj/.bvel fluidsim cache files",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}


import bpy
import gzip
import struct
import imp
import mathutils


# see also
#
# https://developer.blender.org/diffusion/B/browse/master
# /intern/elbeem/intern/ntl_blenderdumper.cpp
#
# http://www.clintons3d.com/plugins/lightwave
# /blenderfluids.html

MODULES = {}
INTERFACERS = {}
HANDLERS = {}
OBJECTS_READING_ERRORS = {}

def getAvailableModules():
    ms = {}
    for t in bpy.data.texts:
        for l in t.lines:
            if l.body.startswith("MAIN_CLASS"):
                n = t.name.strip(".py")
                try:
                    ms[n] = imp.reload(__import__(n))
                except ImportError:
                    pass
                break
    return ms

def refreshModules(context):
    ms = getAvailableModules()

    for n, m in ms.items():
        if n not in MODULES:
            MODULES[n] = m

        for mc in context.object.handle_cache_properties.modules:
            if mc.name == n:
                break
        else:
            new_m = context.object.handle_cache_properties.modules.add()
            new_m.name = n
            new_m.used = False

    for n in tuple(MODULES.keys()):
        if n not in ms:
            del MODULES[n]
            
    for i, m in enumerate(context.object.handle_cache_properties.modules):
        if m.name not in ms:
            context.object.handle_cache_properties.modules.remove(i)

def poll_fluid(context):
    return context.object and any(
        m.type == 'FLUID_SIMULATION' for m in context.object.modifiers)                 


class ObjectStructure(object):
    def __init__(self, obj, fname_obj=None):
        super(ObjectStructure, self).__init__()

        self.amount_verts = 0
        self.verts = []
        self.nors = []
        self.amount_tris = 0
        self.tris = []
        self.fname = fname_obj

        if not fname_obj:
            return

        try:
            # bobj written with comp level 1
            with gzip.open(fname_obj, 'rb', 1) as f:

                #--- amount_verts
                
                record_size = struct.calcsize('i')
                record = f.read(record_size)
                if len(record) < record_size:
                    raise IOError

                self.amount_verts = int(struct.unpack('i', record)[0])
                if self.amount_verts == 0:
                    # is this really to be treated as an error?
                    raise TypeError

                #--- verts

                record_size = struct.calcsize('fff')
                for i in range(self.amount_verts):
                    record = f.read(record_size)
                    if len(record) < record_size:
                        raise IOError
                    self.verts.append(
                        mathutils.Vector(float(x) for x in
                                  struct.unpack('fff', record)))

                #--- amount_nors (not saved in object)

                record_size = struct.calcsize('i')
                record = f.read(record_size)
                if len(record) < record_size:
                    raise IOError

                amount_nors = int(struct.unpack('i', record)[0])
                # this normally is already checked at writing
                assert amount_nors == self.amount_verts

                #--- nors

                record_size = struct.calcsize('fff')
                for i in range(self.amount_verts):
                    record = f.read(record_size)
                    if len(record) < record_size:
                        raise IOError
                    self.nors.append(
                        mathutils.Vector(float(x) for x in
                                  struct.unpack('fff', record)))

                #--- amount_tris
                
                record_size = struct.calcsize('i')
                record = f.read(record_size)
                if len(record) < record_size:
                    raise IOError

                self.amount_tris = int(struct.unpack('i', record)[0])
                if self.amount_tris == 0:
                    # is this really to be treated as an error?
                    raise TypeError

                #--- tris

                record_size = struct.calcsize('iii')
                for i in range(self.amount_tris):
                    record = f.read(record_size)
                    if len(record) < record_size:
                        raise IOError
                    self.tris.append(
                        tuple(int(x) for x in
                              struct.unpack('iii', record)))

            OBJECTS_READING_ERRORS[obj][0] = False
            
        except (FileNotFoundError, IOError, TypeError, AssertionError):
            OBJECTS_READING_ERRORS[obj][0] = True


class VelocityStructure(object):
    def __init__(self, obj, fname_vel=None):
        super(VelocityStructure, self).__init__()

        self.amount_verts = 0
        self.vels = []
        self.fname = fname_vel

        if not fname_vel:
            return

        try:
            # bvel written with normal comp level 9
            with gzip.open(fname_vel, 'rb', 9) as f:

                #--- amount_verts
                
                record_size = struct.calcsize('i')
                record = f.read(record_size)
                if len(record) < record_size:
                    raise IOError

                self.amount_verts = int(struct.unpack('i', record)[0])
                if self.amount_verts == 0:
                    # is this really to be treated as an error?
                    raise TypeError

                #--- vels

                record_size = struct.calcsize('fff')
                for i in range(self.amount_verts):
                    record = f.read(record_size)
                    if len(record) < record_size:
                        raise IOError
                    self.vels.append(
                        mathutils.Vector(float(x) for x in
                                  struct.unpack('fff', record)))

            OBJECTS_READING_ERRORS[obj][1] = False
                
        except (FileNotFoundError, IOError, TypeError, AssertionError):
            OBJECTS_READING_ERRORS[obj][1] = True


class Interfacer(object):
    def __init__(self, obj):
        super(Interfacer, self).__init__()
        self.obj = obj
        self.last_fname_obj = None
        self.last_fname_vel = None
        self.object_struct = ObjectStructure(self.obj)
        self.velocity_struct = VelocityStructure(self.obj)
        
    def isActive(self, mname):
        return self.obj.handle_cache_properties.modules[mname].used

    def isClean(self):
        return (not any(OBJECTS_READING_ERRORS[self.obj]) and
                self.object_struct.amount_verts ==
                self.velocity_struct.amount_verts)

    def cacheObject(self, fname_obj):
        if fname_obj != self.last_fname_obj:
            self.object_struct = ObjectStructure(self.obj, fname_obj)
            self.last_fname_obj = fname_obj
                
    def cacheVelocity(self, fname_vel):
        if fname_vel != self.last_fname_vel:
            self.velocity_struct = VelocityStructure(self.obj, fname_vel)
            self.last_fname_vel = fname_vel

    def cache(self, frame):
        if self.obj.handle_cache_properties.use_custom_files:
            fname = self.obj.handle_cache_properties.custom_file_base
        else:
            # only one modifier supported...
            # assume more or less default behavior
            fname = [m for m in self.obj.modifiers
                     if m.type == 'FLUID_SIMULATION'][0].settings.filepath + "/fluidsurface_final_####"

        if "#" in fname:
            # assume only at one place
            c = fname.count("#")
            fname = (fname[:fname.find("#")] +
                     str(frame).rjust(c, "0") +
                     fname[fname.rfind("#") + 1:])

        fname = bpy.path.abspath(fname)

        fname_obj = fname + ".bobj.gz"
        fname_vel = fname + ".bvel.gz"
        
        self.cacheObject(fname_obj)
        self.cacheVelocity(fname_vel)

        """
        if (any(OBJECTS_READING_ERRORS[self.obj]) or
            self.object_struct.amount_verts !=
            self.velocity_struct.amount_verts):
            # free choice: we prefer consistent states,
            # so we cleanup even if some part was ok
            self.object_struct = ObjectStructure(self.obj)
            self.velocity_struct = VelocityStructure(self.obj)
        """


    def getVelocity(self, frame):
        self.cache(frame)
        return self.velocity_struct
    
    def getObject(self, frame):
        self.cache(frame)
        return self.object_struct
                            
    def getCurrentVelocity(self):
        return self.getVelocity(bpy.context.scene.frame_current)

    def getCurrentObject(self):
        return self.getObject(bpy.context.scene.frame_current)

    def getBlenderObject(self):
        return self.obj



class PHYSICS_OT_cache_list_refresh(bpy.types.Operator):
    bl_idname = "fluid.cache_list_refresh"
    bl_label = "Refresh list"

    @classmethod
    def poll(cls, context):
        return poll_fluid(context)

    def execute(self, context):
        refreshModules(context)
        return {'FINISHED'}



class PHYSICS_UL_handlers(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon,
                  active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon='SCRIPTPLUGINS')
            layout.prop(item, "used", text="")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon='SCRIPTPLUGINS')


class PHYSICS_PT_handle_cache(bpy.types.Panel):

    bl_label = "Handle cache"
    bl_idname = "PHYSICS_PT_handle_cache"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"

    def draw(self, context):        
        layout = self.layout

        layout.prop(
            context.object.handle_cache_properties,
            "use_custom_files")

        row = layout.row(align=True)
        row.prop(
            context.object.handle_cache_properties,
            "custom_file_base",
            text="")
        row.label(text=".bobj.gz/.bvel.gz")
        row.enabled = context.object.handle_cache_properties.use_custom_files

        if (context.object in OBJECTS_READING_ERRORS and
            any(OBJECTS_READING_ERRORS[context.object])):
            layout.label(text="Could not read from file(s) on this frame.",
                         icon='ERROR')

        layout.template_list(
            PHYSICS_UL_handlers.__name__,
            "",
            context.object.handle_cache_properties,
            "modules",
            context.object.handle_cache_properties,
            "active_module",
            rows=1)

        layout.operator(PHYSICS_OT_cache_list_refresh.bl_idname,
                        icon='FILE_REFRESH')

    @classmethod
    def poll(cls, context):
        return poll_fluid(context)


def updateModuleActivity(self, context):
    # self will be an instance of ModulePropertyGroup
    if self.used:
        if context.object not in INTERFACERS:
            INTERFACERS[context.object] = Interfacer(context.object)

        if (self.name, context.object) not in HANDLERS:
            HANDLERS[(self.name, context.object)] = MODULES[self.name].MAIN_CLASS(
                INTERFACERS[context.object], self.name)

        if context.object not in OBJECTS_READING_ERRORS:
            OBJECTS_READING_ERRORS[context.object] = [False, False]

        


class ModulePropertyGroup(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty()
    used = bpy.props.BoolProperty(
        update=updateModuleActivity)


class HandleCacheProperties(bpy.types.PropertyGroup):
    use_custom_files = bpy.props.BoolProperty(
        name="Use custom files")
    custom_file_base = bpy.props.StringProperty()
    modules = bpy.props.CollectionProperty(
        type=ModulePropertyGroup,
        name="Modules")
    active_module = bpy.props.IntProperty()

    @classmethod
    def register(cls):
        bpy.types.Object.handle_cache_properties = bpy.props.PointerProperty(
            type=cls,
            name="Handle cache settings")

    @classmethod
    def unregister(cls):
        del bpy.types.Object.handle_cache_properties


@bpy.app.handlers.persistent
def changeFrameHandler(scene):
    for h in HANDLERS.values():
        h.update(scene)


def register():
    bpy.utils.register_module(__name__)
    bpy.app.handlers.frame_change_post.append(changeFrameHandler)

def unregister():
    bpy.app.handlers.frame_change_post.remove(changeFrameHandler)
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()

