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
import mathutils
from PyHSPlasma import *
import weakref

from .explosions import ExportError, ExportAssertionError
from ..helpers import TemporaryObject
from . import utils

def _set_phys_prop(prop, sim, phys, value=True):
    """Sets properties on plGenericPhysical and plSimulationInterface (seeing as how they are duped)"""
    sim.setProperty(prop, value)
    phys.setProperty(prop, value)

class PhysicsConverter:
    def __init__(self, exporter):
        self._exporter = weakref.ref(exporter)

    def _convert_indices(self, mesh):
        indices = []
        for face in mesh.tessfaces:
            v = face.vertices
            if len(v) == 3:
                indices += v
            elif len(v) == 4:
                indices += (v[0], v[1], v[2],)
                indices += (v[0], v[2], v[3],)
        return indices

    def _convert_mesh_data(self, bo, physical, indices=True, mesh_func=None):
        mesh = bo.to_mesh(bpy.context.scene, True, "RENDER", calc_tessface=False)
        mat = bo.matrix_world

        with TemporaryObject(mesh, bpy.data.meshes.remove):
            if mesh_func is not None:
                mesh_func(mesh)

            # We can only use the plPhysical xforms if there is a CI...
            if self._exporter().has_coordiface(bo):
                mesh.update(calc_tessface=indices)
                physical.pos = hsVector3(*mat.to_translation())
                physical.rot = utils.quaternion(mat.to_quaternion())

                # Physicals can't have scale...
                scale = mat.to_scale()
                if scale[0] == 1.0 and scale[1] == 1.0 and scale[2] == 1.0:
                    # Whew, don't need to do any math!
                    vertices = [hsVector3(*i.co) for i in mesh.vertices]
                else:
                    # Dagnabbit...
                    vertices = [hsVector3(i.co.x * scale.x, i.co.y * scale.y, i.co.z * scale.z) for i in mesh.vertices]
            else:
                # apply the transform to the physical itself
                mesh.transform(mat)
                mesh.update(calc_tessface=indices)
                vertices = [hsVector3(*i.co) for i in mesh.vertices]

            if indices:
                return (vertices, self._convert_indices(mesh))
            else:
                return vertices

    def generate_flat_proxy(self, bo, so, z_coord=None, name=None):
        """Generates a flat physical object"""
        if so.sim is None:
            if name is None:
                name = bo.name

            simIface = self._mgr.add_object(pl=plSimulationInterface, bl=bo)
            physical = self._mgr.add_object(pl=plGenericPhysical, bl=bo, name=name)

            simIface.physical = physical.key
            physical.object = so.key
            physical.sceneNode = self._mgr.get_scene_node(bl=bo)

            mesh = bo.to_mesh(bpy.context.scene, True, "RENDER", calc_tessface=False)
            with TemporaryObject(mesh, bpy.data.meshes.remove):
                # We will apply all xform, seeing as how this is a special case...
                mesh.transform(bo.matrix_world)
                mesh.update(calc_tessface=True)

                if z_coord is None:
                    # Ensure all vertices are coplanar
                    z_coords = [i.co.z for i in mesh.vertices]
                    delta = max(z_coords) - min(z_coords)
                    if delta > 0.0002:
                        raise ExportAssertionError()
                    vertices = [hsVector3(*i.co) for i in mesh.vertices]
                else:
                    # Flatten out all points to the given Z-coordinate
                    vertices = [hsVector3(i.co.x, i.co.y, z_coord) for i in mesh.vertices]
                physical.verts = vertices
                physical.indices = self._convert_indices(mesh)
                physical.boundsType = plSimDefs.kProxyBounds
        else:
            simIface = so.sim.object
            physical = simIface.physical.object
            if name is not None:
                physical.key.name = name

        return (simIface, physical)

    def generate_physical(self, bo, so, bounds, name=None):
        """Generates a physical object for the given object pair"""
        if so.sim is None:
            if name is None:
                name = bo.name

            simIface = self._mgr.add_object(pl=plSimulationInterface, bl=bo)
            physical = self._mgr.add_object(pl=plGenericPhysical, bl=bo, name=name)

            simIface.physical = physical.key
            physical.object = so.key
            physical.sceneNode = self._mgr.get_scene_node(bl=bo)

            # Got subworlds?
            subworld = bo.plasma_object.subworld
            if self.is_dedicated_subworld(subworld, sanity_check=False):
                physical.subWorld = self._mgr.find_create_key(plHKSubWorld, bl=subworld)

            # Ensure this thing is set up properly for animations.
            # This was previously the collision modifier's postexport method, but that
            # would miss cases where we have animated detectors (subworlds!!!)
            def _iter_object_tree(bo, stop_at_subworld):
                while bo is not None:
                    if stop_at_subworld and self.is_dedicated_subworld(bo, sanity_check=False):
                        return
                    yield bo
                    bo = bo.parent

            ver = self._mgr.getVer()
            for i in _iter_object_tree(bo, ver == pvMoul):
                if i.plasma_object.has_transform_animation:
                    tree_xformed = True
                    break
            else:
                tree_xformed = False

            if tree_xformed:
                bo_xformed = bo.plasma_object.has_transform_animation

                # MOUL: only objects that have animation data are kPhysAnim
                if ver != pvMoul or bo_xformed:
                    _set_phys_prop(plSimulationInterface.kPhysAnim, simIface, physical)
                # PotS: objects inheriting parent animation only are not pinned
                # MOUL: animated objects in subworlds are not pinned
                if bo_xformed and (ver != pvMoul or subworld is None):
                     _set_phys_prop(plSimulationInterface.kPinned, simIface, physical)
                # MOUL: child objects are kPassive
                if ver == pvMoul and bo.parent is not None:
                    _set_phys_prop(plSimulationInterface.kPassive, simIface, physical)
                # FilterCoordinateInterfaces are kPassive
                if bo.plasma_object.ci_type == plFilterCoordInterface:
                    _set_phys_prop(plSimulationInterface.kPassive, simIface, physical)

                # If the mass is zero, then we will fail to animate. Fix that.
                if physical.mass == 0.0:
                    physical.mass = 1.0

            getattr(self, "_export_{}".format(bounds))(bo, physical)
        else:
            simIface = so.sim.object
            physical = simIface.physical.object
            if name is not None:
                physical.key.name = name

        return (simIface, physical)

    def _export_box(self, bo, physical):
        """Exports box bounds based on the object"""
        physical.boundsType = plSimDefs.kBoxBounds

        vertices = self._convert_mesh_data(bo, physical, indices=False)
        physical.calcBoxBounds(vertices)

    def _export_hull(self, bo, physical):
        """Exports convex hull bounds based on the object"""
        physical.boundsType = plSimDefs.kHullBounds

        # Only certain builds of libHSPlasma are able to take artist generated triangle soups and
        # bake them to convex hulls. Specifically, Windows 32-bit w/PhysX 2.6. Everything else just
        # needs to have us provide some friendlier data...
        def _bake_hull(mesh):
            # The bmesh API for doing this is trash, so we will link this temporary mesh to an
            # even more temporary object so we can use the traditional operator.
            # Unless you want to write some code to do this by hand...??? (not me)
            bo = bpy.data.objects.new("BMeshSucks", mesh)
            bpy.context.scene.objects.link(bo)
            with TemporaryObject(bo, bpy.data.objects.remove):
                bpy.context.scene.objects.active = bo
                bpy.ops.object.mode_set(mode="EDIT")
                bpy.ops.mesh.select_all(action="SELECT")
                bpy.ops.mesh.convex_hull(use_existing_faces=False)
                bpy.ops.object.mode_set(mode="OBJECT")

        physical.verts = self._convert_mesh_data(bo, physical, indices=False, mesh_func=_bake_hull)

    def _export_sphere(self, bo, physical):
        """Exports sphere bounds based on the object"""
        physical.boundsType = plSimDefs.kSphereBounds

        vertices = self._convert_mesh_data(bo, physical, indices=False)
        physical.calcSphereBounds(vertices)

    def _export_trimesh(self, bo, physical):
        """Exports an object's mesh as exact physical bounds"""
        physical.boundsType = plSimDefs.kExplicitBounds

        vertices, indices = self._convert_mesh_data(bo, physical)
        physical.verts = vertices
        physical.indices = indices

    def is_dedicated_subworld(self, bo, sanity_check=True):
        """Determines if a subworld object defines an alternate physics world"""
        if bo is None:
            return False
        subworld_mod = bo.plasma_modifiers.subworld_def
        if not subworld_mod.enabled:
            if sanity_check:
                raise ExportError("'{}' is not a subworld".format(bo.name))
            else:
                return False
        return subworld_mod.is_dedicated_subworld(self._exporter())

    @property
    def _mgr(self):
        return self._exporter().mgr
