#    This file is part of Korman.
#
#    Korman is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Korman is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Korman.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from pathlib import Path
from PyHSPlasma import *
import weakref

from . import explosions
from .. import korlib
from ..plasma_magic import *

# These objects have to be in the plSceneNode pool in order to be loaded...
# NOTE: We are using Factory indices because I doubt all of these classes are implemented.
_pool_types = (
    plFactory.ClassIndex("plPostEffectMod"),
    plFactory.ClassIndex("pfGUIDialogMod"),
    plFactory.ClassIndex("plMsgForwarder"),
    plFactory.ClassIndex("plClothingItem"),
    plFactory.ClassIndex("plArmatureEffectFootSound"),
    plFactory.ClassIndex("plDynaFootMgr"),
    plFactory.ClassIndex("plDynaRippleMgr"),
    plFactory.ClassIndex("plDynaBulletMgr"),
    plFactory.ClassIndex("plDynaPuddleMgr"),
    plFactory.ClassIndex("plATCAnim"),
    plFactory.ClassIndex("plEmoteAnim"),
    plFactory.ClassIndex("plDynaRippleVSMgr"),
    plFactory.ClassIndex("plDynaTorpedoMgr"),
    plFactory.ClassIndex("plDynaTorpedoVSMgr"),
    plFactory.ClassIndex("plClusterGroup"),
)


class ExportManager:
    """Friendly resource-managing helper class."""

    def __init__(self, exporter):
        self._exporter = weakref.ref(exporter)
        self.mgr = plResManager()
        self.mgr.setVer(globals()[exporter._op.version])

        self._nodes = {}
        self._pages = {}
        self._keys = {}

        # cheap inheritance
        for i in dir(self.mgr):
            if not hasattr(self, i):
                setattr(self, i, getattr(self.mgr, i))

    def AddAge(self, info):
        # There's only ever one age being exported, so hook the call and hang onto the plAgeInfo
        # We'll save from our reference later. Forget grabbing this from C++
        self._age_info = info
        self.mgr.AddAge(info)

    def AddObject(self, location, obj):
        """Overloads the plResManager AddObject so we can insert the object into our hashtable"""
        key = obj.key
        self._keys[(location, obj.__class__, key.name)] = key
        self.mgr.AddObject(location, obj)

    def add_object(self, pl, name=None, bl=None, loc=None, so=None):
        """Automates adding a converted Blender object to our Plasma Resource Manager"""
        assert (bl or loc or so)
        if loc is not None:
            location = loc
        elif so is not None:
            location = so.key.location
        else:
            location = self._pages[bl.plasma_object.page]

        # pl can be a class or an instance.
        # This is one of those "sanity" things to ensure we don't suddenly startpassing around the
        # key of an uninitialized object.
        if isinstance(pl, type(object)):
            assert name or bl or so
            if name is None:
                if bl is not None:
                    name = bl.name
                else:
                    name = so.key.name
            assert issubclass(pl, hsKeyedObject)
            pl = pl(name)

        self.AddObject(location, pl)
        node = self._nodes[location]
        if node: # All objects must be in the scene node
            if isinstance(pl, plSceneObject):
                node.addSceneObject(pl.key)
                pl.sceneNode = node.key
            elif pl.ClassIndex() in _pool_types:
                node.addPoolObject(pl.key)

        if so is None and isinstance(pl, (plObjInterface, plModifier)):
            assert bl

            # Don't use find_create_object because we want to specify the location... Also, we're
            # in a modifier, so the name we're given might be for a modifier, not the SO
            key = self.find_key(plSceneObject, bl)
            if key is None:
                so = self.add_object(plSceneObject, bl=bl, loc=location)
            else:
                so = key.object

        if isinstance(pl, plObjInterface):
            pl.owner = so.key

            # The things I do to make life easy... This is something of a God function now.
            if isinstance(pl, plAudioInterface):
                so.audio = pl.key
            elif isinstance(pl, plCoordinateInterface):
                so.coord = pl.key
            elif isinstance(pl, plDrawInterface):
                so.draw = pl.key
            elif isinstance(pl, plSimulationInterface):
                so.sim = pl.key
            else:
                so.addInterface(pl.key)
        elif isinstance(pl, plModifier):
            so.addModifier(pl.key)

        # And we're done!
        return pl

    def create_builtins(self, age, textures):
        # BuiltIn.prp
        if bpy.context.scene.world.plasma_age.age_sdl:
            self._create_builtin_pages(age)
            self._pack_agesdl_hook(age)

        # Textures.prp
        if textures:
            self.create_page(age, "Textures", -1, True)

    def _create_builtin_pages(self, age):
        builtin = self.create_page(age, "BuiltIn", -2, True)
        sdl = self.add_object(plSceneObject, name="AgeSDLHook", loc=builtin)
        pfm = self.add_object(plPythonFileMod, name="VeryVerySpecialPythonFileMod", so=sdl)
        pfm.filename = age

    def create_page(self, age, name, id, builtin=False):
        location = plLocation(self.mgr.getVer())
        location.prefix = bpy.context.scene.world.plasma_age.seq_prefix
        if builtin:
            location.flags |= plLocation.kBuiltIn
        location.page = id
        self._pages[name] = location

        # If the page ID is 0, this is the default page... Any page with an empty string name
        # is the default, so bookmark it!
        if id == 0:
            self._pages[""] = location

        info = plPageInfo()
        info.age = age
        info.page = name
        info.location = location
        self.mgr.AddPage(info)

        if not builtin:
            self._age_info.addPage((name, id, 0))
            if self.getVer() <= pvPots:
                node = plSceneNode("{}_District_{}".format(age, name))
            else:
                node = plSceneNode("{}_{}".format(age, name))
            self._nodes[location] = node
            self.mgr.AddObject(location, node)
        else:
            self._nodes[location] = None
        return location

    @property
    def _encryption(self):
        if self.mgr.getVer() == pvEoa:
            return plEncryptedStream.kEncAes
        else:
            return plEncryptedStream.kEncXtea

    def find_create_key(self, pClass, bl=None, name=None, so=None):
        key = self.find_key(pClass, bl, name, so)
        if key is None:
            key = self.add_object(pl=pClass, name=name, bl=bl, so=so).key
        return key

    def find_key(self, pClass, bl=None, name=None, so=None, loc=None):
        """Given a blender Object and a Plasma class, find (or create) an exported plKey"""
        assert loc or bl or so

        if loc is not None:
            location = loc
        elif so is not None:
            location = so.key.location
        else:
            location = self._pages[bl.plasma_object.page]

        if name is None:
            if bl is not None:
                name = bl.name
            else:
                name = so.key.name

        return self._keys.get((location, pClass, name), None)

    def find_create_object(self, pClass, bl=None, name=None, so=None):
        key = self.find_key(pClass, bl, name, so)
        if key is None:
            return self.add_object(pl=pClass, name=name, bl=bl, so=so)
        return key.object

    def find_object(self, pClass, bl=None, name=None, so=None):
        key = self.find_key(pClass, bl, name, so)
        if key is not None:
            return key.object
        return None

    def get_location(self, bl):
        """Returns the Page Location of a given Blender Object"""
        return self._pages[bl.plasma_object.page]

    def get_scene_node(self, location=None, bl=None):
        """Gets a Plasma Page's plSceneNode key"""
        assert (location is not None) ^ (bl is not None)

        if location is None:
            location = self._pages[bl.plasma_object.page]
        return self._nodes[location].key

    def get_textures_page(self, key):
        """Gets the appropriate page for a texture for a given plLayer"""
        # The point of this is to account for per-page textures...
        if "Textures" in self._pages:
            return self._pages["Textures"]
        else:
            return key.location

    def _pack_agesdl_hook(self, age):
        get_text = bpy.data.texts.get
        output = self._exporter().output

        # AgeSDL Hook Python
        fixed_agename = korlib.replace_python2_identifier(age)
        py_filename = "{}.py".format(fixed_agename)
        age_py = get_text(py_filename, None)
        if output.want_py_text(age_py):
            py_code = age_py.as_string()
        else:
            py_code = very_very_special_python.format(age_name=fixed_agename).lstrip()
        output.add_python_mod(py_filename, text_id=age_py, str_data=py_code)

        # AgeSDL
        sdl_filename = "{}.sdl".format(fixed_agename)
        age_sdl = get_text(sdl_filename)
        if age_sdl is not None:
            sdl_code = None
        else:
            sdl_code = very_very_special_sdl.format(age_name=fixed_agename).lstrip()
        output.add_sdl(sdl_filename, text_id=age_sdl, str_data=sdl_code)

    def save_age(self):
        self._write_age()
        self._write_fni()
        self._write_pages()

    def _write_age(self):
        f = "{}.age".format(self._age_info.name)
        output = self._exporter().output

        with output.generate_dat_file(f, enc=self._encryption) as stream:
            self._age_info.writeToStream(stream)

    def _write_fni(self):
        f = "{}.fni".format(self._age_info.name)
        output = self._exporter().output

        with output.generate_dat_file(f, enc=self._encryption) as stream:
            fni = bpy.context.scene.world.plasma_fni
            stream.writeLine("Graphics.Renderer.SetClearColor {} {} {}".format(*fni.clear_color))
            if fni.fog_method != "none":
                stream.writeLine("Graphics.Renderer.Fog.SetDefColor {} {} {}".format(*fni.fog_color))
            if fni.fog_method == "linear":
                stream.writeLine("Graphics.Renderer.Fog.SetDefLinear {} {} {}".format(fni.fog_start, fni.fog_end, fni.fog_density))
            elif fni.fog_method == "exp2":
                stream.writeLine("Graphics.Renderer.Fog.SetDefExp2 {} {}".format(fni.fog_end, fni.fog_density))
            stream.writeLine("Graphics.Renderer.SetYon {}".format(fni.yon))

    def _write_pages(self):
        age_name = self._age_info.name
        output = self._exporter().output
        for loc in self._pages.values():
            page = self.mgr.FindPage(loc) # not cached because it's C++ owned
            chapter = "_District_" if self.mgr.getVer() <= pvMoul else "_"
            f = "{}{}{}.prp".format(age_name, chapter, page.page)

            with output.generate_dat_file(f) as stream:
                self.mgr.WritePage(stream, page)
