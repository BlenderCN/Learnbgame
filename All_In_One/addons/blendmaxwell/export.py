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
import math
import shlex
import subprocess
import uuid
import shutil
import struct
import json
import sys
import re
import string

import bpy
from mathutils import Matrix, Vector
from bpy_extras import io_utils
import bmesh
from mathutils.geometry import barycentric_transform
from mathutils.bvhtree import BVHTree
import numpy

from .log import log, clear_log, LogStyles
from . import utils
from . import maths
from . import system
from . import rfbin
from . import mxs
from . import tmpio


AXIS_CONVERSION = Matrix(((1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, -1.0, 0.0))).to_4x4()
ROTATE_X_90 = Matrix.Rotation(math.radians(90.0), 4, 'X')
ROTATE_X_MINUS_90 = Matrix.Rotation(math.radians(-90.0), 4, 'X')


# FIXME: (IMPORTANT) simple cube with default subdivision modifier refuses to render (An edge connecting two vertices was specified more than once. It's likely that an incident face was flipped)
#        - 2.76 order of faces is different than in 2.77. this might be the problem because from 2.76 it renders fine
#        - creating mesh again from data (bot orders), the result is the same too.. and this is the same for polygons/tessfaces/bmesh.faces
#        - in 2.76 everything works, in 2.77 nothing, maxwell just don't like it. i have no idea what's going on.
#        - also it seems to be not caused by split normals, reverting to old scheme doesn't fix anything.
#        - ok, made it to work on cube and cube with one face triangulated. does not work on monkey, even though it should. what a mystery. will try again soon..

# TODO: restore instancer support for my personal use (python only)
# NOTE: grass: preview in viewport is wrong, looks like before parenting (i think), but i can't get back to modifier once is created without whole python crashing..
# NOTE: particles/cloner: problematic scenario: object with particles (particles or cloner is used) is a child of arbitrary transformed parent. the result is, one particle is misplaced far away. cloner can be fixed by putting object in scene root and changing it to use external bin (using embedded particles will not fix it). particles can be fixed by using external bin, there is no difference in hierarchy change. maybe add checkbox to fix this automatically or add warning when problematic scenario is detected. anyway, bug is reported (and hopefuly acknowledged) and now i've got two options, either write quick and dirty fix or leave it as it should be and wait for the fix. both are correct..
# TODO: do something with sharp edges, auto smooth and custom normals..
# NOTE: check hair children particles again, seems to be crashing when exporting with uvs. put there warning at least
# TODO: more standardized setting render file type and bit depth, this will require change in render workflow and that is dangerous..
# TODO: check if in case of some error during exporting, everything is cleaned up and won't cause problems during next export
# NOTE: from Maxwell 3.2.0.4 beta changelog: Studio: Fixed when exporting MXMs material names were cropped if they contained dots. - remove dot changing mechanism whet this is out. maybe not.. not very importat and will work with older version. or check version and then decide. this will require version.py to return version number instead of true/false.
# NOTE: in some cases meshes with no polygons have to be exported, e.g. mesh with particle system (already fixed), look for other examples/uses, or maybe just swap it to empty at the end
# TODO: put wireframe scene creation to special export operator, remove all wireframe related stuff from normal workflow. also when done this way, no ugly hacking is needed to put new object during render export (which might crash blender). also implement wireframe without special switches and functions. modify current scene, rewrite serialized scene data and then pass to external script as regular scene.
# NOTE: particle data with foreach_get, well, in particles there is a problem, i export only alive particles and each have to be checked first, and with hair, oh well, it was not easy to get it working and now i don't want to break it.. so i guess this will stay as it is..
# TODO: when exporting motion blur, move timeline just once per step, eg. add each step to all objects at once per timeline move.
# TODO: export group instances


class MXSExportStats():
    materials = 0
    cameras = 0
    empties = 0
    meshes = 0
    vertices = 0
    triangles = 0
    instances = 0
    particles = 0
    particles_number = 0
    hairs = 0
    hair_curves = 0
    references = 0
    volumetrics = 0
    modifiers = 0
    
    def __init__(self):
        pass
    
    def add(self, o, ):
        if(o.m_type == 'MATERIAL'):
            self.materials += 1
        elif(o.m_type == 'CAMERA'):
            self.cameras += 1
        elif(o.m_type == 'EMPTY'):
            self.empties += 1
        elif(o.m_type == 'MESH'):
            self.meshes += 1
            self.vertices += len(o.m_vertices[0])
            self.triangles += len(o.m_triangles)
        elif(o.m_type == 'MESH_INSTANCE'):
            self.instances += 1
        elif(o.m_type == 'SCENE'):
            pass
        elif(o.m_type == 'ENVIRONMENT'):
            pass
        elif(o.m_type == 'PARTICLES'):
            self.particles += 1
            self.particles_number += o.stat_num
        elif(o.m_type == 'HAIR'):
            self.hairs += 1
            self.hair_curves += o.m_data['HAIR_GUIDES_COUNT'][0]
        elif(o.m_type == 'REFERENCE'):
            self.references += 1
        elif(o.m_type == 'VOLUMETRICS'):
            self.volumetrics += 1
        elif(o.m_type == 'SUBDIVISION'):
            self.modifiers += 1
        elif(o.m_type == 'SCATTER'):
            self.modifiers += 1
        elif(o.m_type == 'GRASS'):
            self.modifiers += 1
        elif(o.m_type == 'CLONER'):
            self.modifiers += 1
        elif(o.m_type == 'SEA'):
            self.modifiers += 1
        elif(o.m_type == 'WIREFRAME_CONTAINER'):
            self.empties += 1
        elif(o.m_type == 'WIREFRAME_BASE'):
            self.meshes += 1
            self.vertices += len(o.m_vertices)
            self.triangles += len(o.m_triangles)
        elif(o.m_type == 'WIREFRAME_INSTANCES'):
            self.instances += 1
        else:
            pass
    
    def int_to_short_notation(self, n, precision=1, ):
        if(round(n / 10 ** 12, precision) >= 1):
            r = int(round(n / 10 ** 12, precision))
            return '{}t'.format(r)
        elif(round(n / 10 ** 9, precision) >= 1):
            r = int(round(n / 10 ** 9, precision))
            return '{}g'.format(r)
        elif(round(n / 10 ** 6, precision) >= 1):
            r = int(round(n / 10 ** 6, precision))
            return '{}m'.format(r)
        elif(round(n / 10 ** 3, precision) >= 1):
            r = int(round(n / 10 ** 3, precision))
            return '{}k'.format(r)
        else:
            r = round(n / 10 ** 3, precision)
            if(r >= 0.5):
                return '{}k'.format(r)
            else:
                return '{}'.format(n)
    
    def pprint(self):
        log("{}".format("-" * 30), 1, )
        log("export statistics:", 1, )
        log("materials:   {}".format(self.int_to_short_notation(self.materials)), 2, prefix="", )
        log("cameras:     {}".format(self.int_to_short_notation(self.cameras)), 2, prefix="", )
        log("empties:     {}".format(self.int_to_short_notation(self.empties)), 2, prefix="", )
        log("meshes:      {} (verts: {}, tris: {})".format(self.int_to_short_notation(self.meshes),
                                                           self.int_to_short_notation(self.vertices),
                                                           self.int_to_short_notation(self.triangles)), 2, prefix="", )
        log("instances:   {}".format(self.int_to_short_notation(self.instances)), 2, prefix="", )
        log("particles:   {} ({})".format(self.int_to_short_notation(self.particles),
                                          self.int_to_short_notation(self.particles_number)), 2, prefix="", )
        log("hairs:       {} ({})".format(self.int_to_short_notation(self.hairs),
                                          self.int_to_short_notation(self.hair_curves)), 2, prefix="", )
        log("references:  {}".format(self.int_to_short_notation(self.references)), 2, prefix="", )
        log("volumetrics: {}".format(self.int_to_short_notation(self.volumetrics)), 2, prefix="", )
        log("modifiers:   {}".format(self.int_to_short_notation(self.modifiers)), 2, prefix="", )


class MXSExport():
    def __init__(self, mxs_path, engine=None, ):
        # clear db, before we start, previous error will cause more errors
        MXSDatabase.clear()
        MXSMotionBlurHelper.clear()
        
        clear_log()
        log("{0} {1} {0}".format("-" * 30, self.__class__.__name__), 0, LogStyles.MESSAGE, prefix="", )
        
        ok = system.check_pymaxwell_version()
        if(ok):
            log("pymaxwell version >= {}".format(system.REQUIRED), 1, )
        
        self.mxs_path = os.path.realpath(mxs_path)
        log("exporting mxs: '{}'".format(self.mxs_path), 1, LogStyles.MESSAGE, )
        self.engine = engine
        
        self.progress_current = 0
        self.progress_count = 0
        
        self.context = bpy.context
        
        self.uuid = uuid.uuid1()
        
        mx = self.context.scene.maxwell_render
        self.use_instances = mx.export_use_instances
        self.use_wireframe = mx.export_use_wireframe
        self.use_subdivision = mx.export_use_subdivision
        
        self._prepare()
        self._export()
        self._finish()
        
        MXSDatabase.clear()
        MXSMotionBlurHelper.clear()
        
        for me in bpy.data.meshes:
            if(me.users == 0):
                if(not me.use_fake_user):
                    # just log it, there is no need to remove orphan meshes because all meshes created during export should be removed now.
                    # user might need those meshes in future..
                    # NOTE: this can be removed once i am sure there is no other leak. now just scare user..
                    log("orphan mesh: '{}' is it intentional?".format(me.name), 1, LogStyles.ERROR, )
                    # bpy.data.meshes.remove(me)
    
    def _progress(self, progress=0.0, ):
        if(progress == 0.0):
            progress = self.progress_current / self.progress_count
            self.progress_current += 1
        
        if(self.engine is not None):
            if(system.PLATFORM == 'Darwin'):
                # on Mac OS X report progress up to 3/4, then external script is called which will take some time
                # and better not to over complicate things reporting that too.. would be problematic..
                progress = maths.remap(progress, 0.0, 1.0, 0.0, 0.75)
            elif(system.PLATFORM == 'Linux' or system.PLATFORM == 'Windows'):
                pass
            self.engine.update_progress(progress)
    
    def _prepare(self):
        self.hierarchy = []
        
        if(system.PLATFORM == 'Darwin'):
            # Mac OS X specific
            self.data = []
            self.serialized_data = []
            
            mx = self.context.scene.maxwell_render
            self.keep_intermediates = mx.export_keep_intermediates
            
            h, t = os.path.split(self.mxs_path)
            n, e = os.path.splitext(t)
            self.tmp_dir = utils.tmp_dir(purpose='export_scene', uid=self.uuid, use_blend_name=True, )
            
            self.mesh_data_paths = []
            self.hair_data_paths = []
            self.part_data_paths = []
            self.wire_data_paths = []
            self.scene_data_name = "{0}-{1}.json".format(n, self.uuid)
            self.script_name = "{0}-{1}.py".format(n, self.uuid)
            
        elif(system.PLATFORM == 'Linux' or system.PLATFORM == 'Windows'):
            self.mxs = mxs.MXSWriter(path=self.mxs_path, append=False, )
            # self.hierarchy = []
    
    def _collect(self):
        """Collect scene objects.
        what it does (unordered):
            - Filter all scene objects and collect only objects needed for scene export. Meshes (and instances), empties, cameras and sun.
            - Remove all objects on hidden layers and with hide_render: True, substitute with an empty if needed for correct hierarchy.
            - Sort all objects by type, determine base meshes for instanced objects (if use_instances: True).
            - Try to convert non-mesh objects to mesh and if result is renderable, include them as well.
            - Covert dupli-objects to real meshes or instances.
        Return filtered scene hierarchy.
        """
        
        objs = self.context.scene.objects
        
        # sort objects
        def sort_objects():
            meshes = []
            empties = []
            cameras = []
            bases = []
            instances = []
            convertible_meshes = []
            convertible_bases = []
            convertible_instances = []
            others = []
            
            might_be_renderable = ['CURVE', 'SURFACE', 'FONT', ]
            for o in objs:
                if(o.type == 'MESH'):
                    if(self.use_instances):
                        if(o.data.users > 1):
                            instances.append(o)
                        else:
                            meshes.append(o)
                    else:
                        meshes.append(o)
                elif(o.type == 'EMPTY'):
                    empties.append(o)
                elif(o.type == 'CAMERA'):
                    cameras.append(o)
                elif(o.type in might_be_renderable):
                    # convertibles.append(o)
                    if(self.use_instances):
                        if(o.data.users > 1):
                            convertible_instances.append(o)
                        else:
                            convertible_meshes.append(o)
                    else:
                        convertible_meshes.append(o)
                else:
                    others.append(o)
            instance_groups = {}
            for o in instances:
                if(o.data.name not in instance_groups):
                    instance_groups[o.data.name] = [o, ]
                else:
                    instance_groups[o.data.name].append(o)
            bases_names = []
            for n, g in instance_groups.items():
                nms = [o.name for o in g]
                ls = sorted(nms)
                bases_names.append(ls[0])
            insts = instances[:]
            instances = []
            for o in insts:
                if(o.name in bases_names):
                    bases.append(o)
                else:
                    instances.append(o)
            
            convertible_instance_groups = {}
            for o in convertible_instances:
                if(o.data.name not in convertible_instance_groups):
                    convertible_instance_groups[o.data.name] = [o, ]
                else:
                    convertible_instance_groups[o.data.name].append(o)
            convertible_bases_names = []
            for n, g in convertible_instance_groups.items():
                nms = [o.name for o in g]
                ls = sorted(nms)
                convertible_bases_names.append(ls[0])
            convertible_insts = convertible_instances[:]
            convertible_instances = []
            for o in convertible_insts:
                if(o.name in convertible_bases_names):
                    convertible_bases.append(o)
                else:
                    convertible_instances.append(o)
            
            return {'meshes': meshes,
                    'empties': empties,
                    'cameras': cameras,
                    'bases': bases,
                    'instances': instances,
                    'convertible_meshes': convertible_meshes,
                    'convertible_bases': convertible_bases,
                    'convertible_instances': convertible_instances,
                    'others': others, }
        
        so = sort_objects()
        
        # visibility
        mx = self.context.scene.maxwell_render
        layers = self.context.scene.layers
        render_layers = self.context.scene.render.layers.active.layers
        
        def check_visibility(o):
            """Objects which are in visible layers and have hide_render: False are considered visible,
               objects which are only hidden from viewport are renderable, therefore visible."""
            # if(mx.render_use_layers == 'RENDER'):
            #     for i, l in enumerate(o.layers):
            #         if(render_layers[i] is True and l is True and o.hide_render is False):
            #             return True
            # else:
            #     for i, l in enumerate(o.layers):
            #         if(layers[i] is True and l is True and o.hide_render is False):
            #             return True
            
            if(o.hide_render is True):
                return False
            
            s = None
            r = None
            for i, l in enumerate(o.layers):
                if(layers[i] is True and l is True):
                    s = True
                    break
            for i, l in enumerate(o.layers):
                if(render_layers[i] is True and l is True):
                    r = True
                    break
            if(s and r):
                return True
            return False
        
        # export type
        might_be_renderable = ['CURVE', 'SURFACE', 'FONT', ]
        c_bases_meshes = []
        c_instance_meshes = []
        
        no_polygons_meshes = []
        
        def export_type(o):
            """determine export type, if convertible, try convert to mesh and store result"""
            t = 'EMPTY'
            m = None
            c = False
            if(o.type == 'MESH'):
                m = o.data
                if(self.use_instances):
                    if(o.data.users > 1):
                        if(o in so['bases']):
                            t = 'BASE_INSTANCE'
                        else:
                            t = 'INSTANCE'
                    else:
                        if(len(o.data.polygons) > 0):
                            t = 'MESH'
                        else:
                            # case when object has no polygons, but with modifiers applied it will have..
                            me = o.to_mesh(self.context.scene, True, 'RENDER', )
                            if(len(me.polygons) > 0):
                                t = 'MESH'
                            # remove mesh, was created only for testing..
                            bpy.data.meshes.remove(me)
                            
                            # in case mesh without polygons has particles systems to be exported
                            if(len(o.particle_systems) > 0):
                                for ps in o.particle_systems:
                                    if(ps.settings.maxwell_render.use is not 'NONE'):
                                        t = 'MESH'
                                        no_polygons_meshes.append(o)
                            
                        # else:
                        #     t = 'EMPTY'
                else:
                    if(len(o.data.polygons) > 0):
                        t = 'MESH'
                    else:
                        # case when object has no polygons, but with modifiers applied it will have..
                        me = o.to_mesh(self.context.scene, True, 'RENDER', )
                        if(len(me.polygons) > 0):
                            t = 'MESH'
                        # remove mesh, was created only for testing..
                        bpy.data.meshes.remove(me)
                        
                        # in case mesh without polygons has particles systems to be exported
                        if(len(o.particle_systems) > 0):
                            for ps in o.particle_systems:
                                if(ps.settings.maxwell_render.use is not 'NONE'):
                                    t = 'MESH'
                                    no_polygons_meshes.append(o)
                        
                    # else:
                    #     t = 'EMPTY'
            elif(o.type == 'EMPTY'):
                # t = 'EMPTY'
                if(o.maxwell_render.reference.enabled):
                    t = 'REFERENCE'
                elif(o.maxwell_render.volumetrics.enabled):
                    t = 'VOLUMETRICS'
                else:
                    pass
            elif(o.type == 'CAMERA'):
                t = 'CAMERA'
            elif(o.type in might_be_renderable):
                me = o.to_mesh(self.context.scene, True, 'RENDER', )
                if(me is not None):
                    if(self.use_instances):
                        if(len(me.polygons) > 0):
                            if(o.data.users > 1):
                                if(o in so['convertible_bases']):
                                    t = 'BASE_INSTANCE'
                                    m = me
                                    c = True
                                    c_bases_meshes.append([o, me])
                                else:
                                    # seems like those meshes are not removed when finished..
                                    c_instance_meshes.append([o, me])
                                    
                                    t = 'INSTANCE'
                                    # m = me
                                    m = None
                                    for cbmo, cbmme in c_bases_meshes:
                                        if(cbmo.data == o.data):
                                            m = cbmme
                                            break
                                    if(m is None):
                                        m = me
                                    c = True
                            else:
                                t = 'MESH'
                                m = me
                                c = True
                        else:
                            # pass
                            bpy.data.meshes.remove(me)
                    else:
                        if(len(me.polygons) > 0):
                            t = 'MESH'
                            m = me
                            c = True
                        else:
                            bpy.data.meshes.remove(me)
                
                # me = o.to_mesh(self.context.scene, True, 'RENDER', )
                # if(me is not None):
                #     if(len(me.polygons) > 0):
                #         t = 'MESH'
                #         m = me
                #         c = True
                #     # else:
                #     #     t = 'EMPTY'
                # # else:
                # #     t = 'EMPTY'
            elif(o.type == 'LAMP'):
                if(o.data.type == 'SUN'):
                    t = 'SUN'
            # else:
            #     t = 'EMPTY'
            return t, m, c
        
        # object hierarchy
        def hierarchy():
            h = []
            
            def get_object_hierarchy(o):
                r = []
                for ch in o.children:
                    t, m, c = export_type(ch)
                    p = {'object': ch,
                         'children': get_object_hierarchy(ch),
                         'export': check_visibility(ch),
                         'export_type': t,
                         'mesh': m,
                         'converted': c,
                         'parent': o,
                         'type': ch.type, }
                    r.append(p)
                return r
            
            for ob in objs:
                if(ob.parent is None):
                    t, m, c = export_type(ob)
                    p = {'object': ob,
                         'children': get_object_hierarchy(ob),
                         'export': check_visibility(ob),
                         'export_type': t,
                         'mesh': m,
                         'converted': c,
                         'parent': None,
                         'type': ob.type, }
                    h.append(p)
            return h
        
        h = hierarchy()
        
        # print(c_bases_meshes)
        # fix the leak, at last!
        for _, me in c_instance_meshes:
            bpy.data.meshes.remove(me)
        
        # particle instances with hidden bases
        class KillRecursiveFunctions(Exception):
            pass
        
        def is_psys_instances_marked_to_export(obj):
            def walk(o):
                for c in o['children']:
                    walk(c)
                ob = o['object']
                if(ob == obj):
                    if(o['export']):
                        raise KillRecursiveFunctions("here it is!")
            try:
                for o in h:
                    walk(o)
            except KillRecursiveFunctions:
                return True
        
        def is_hidden_base(hob):
            for ob in objs:
                if(len(ob.particle_systems) > 0):
                    for ps in ob.particle_systems:
                        marked = is_psys_instances_marked_to_export(ob)
                        if(marked):
                            pset = ps.settings
                            
                            # check if there are any alive particles
                            ok = False
                            for p in ps.particles:
                                if(p.alive_state == "ALIVE"):
                                    ok = True
                                    break
                            if(not ok):
                                # if there are no alive particles, it can't be hidden base because it can't be swapped to one of instances
                                return False
                            
                            if(pset.maxwell_render.use == 'PARTICLE_INSTANCES'):
                                if(pset.render_type in ['OBJECT', 'GROUP', ]):
                                    if(pset.render_type == 'GROUP' and pset.dupli_group is not None):
                                        for do in pset.dupli_group.objects:
                                            if(do == hob):
                                                return True
                                    elif(pset.render_type == 'OBJECT' and pset.dupli_object is not None):
                                        if(pset.dupli_object == hob):
                                            return True
            return False
        
        def walk(o):
            for c in o['children']:
                walk(c)
            ob = o['object']
            hidden_base = is_hidden_base(ob)
            if(hidden_base):
                o['export'] = True
                o['extra_options'] = {'hidden_base': True, }
        
        for o in h:
            walk(o)
        
        # if object is not visible and has renderable children, swap type to EMPTY and mark for export
        def renderable_children(o):
            r = False
            for c in o['children']:
                if(c['export'] is True):
                    r = True
            return r
        
        def walk(o):
            for c in o['children']:
                walk(c)
            ob = o['object']
            if(o['export'] is False and renderable_children(o)):
                o['export_type'] = 'EMPTY'
                o['export'] = True
                # if(ob.type in might_be_renderable):
                #     if(o['converted']):
                #         # log(o, style=LogStyles.ERROR, )
                #         bpy.data.meshes.remove(o['mesh'])
                try:
                    if(o['converted']):
                        # log(o, style=LogStyles.ERROR, )
                        bpy.data.meshes.remove(o['mesh'])
                except KeyError:
                    pass
        
        for o in h:
            walk(o)
        
        # mark to remove all redundant empties
        append_types = ['MESH', 'BASE_INSTANCE', 'INSTANCE', 'REFERENCE', 'VOLUMETRICS', ]
        
        def check_renderables_in_tree(oo):
            ov = []
            
            def walk(o):
                for c in o['children']:
                    walk(c)
                if((o['export_type'] in append_types) and o['export'] is True):
                    # keep instances (Maxwell 3)
                    # keep: meshes, bases - both with export: True
                    # (export: False are hidden objects, and should be already swapped to empties if needed for hierarchy)
                    # > meshes..
                    # > bases can have children, bases are real meshes
                    ov.append(True)
                else:
                    # remove: empties, bases, instances, suns, meshes and bases with export: False (hidden objects) and reference enabled: False
                    # > empties can be removed
                    # > instances are moved to base level, because with instances hierarchy is irrelevant
                    # > suns are not objects
                    # > meshes and bases, see above
                    ov.append(False)
            for o in oo['children']:
                walk(o)
            
            # keep empty if it has dupli group assigned
            if(oo['object'].dupli_type == 'GROUP'):
                if(oo['object'].dupli_group):
                    return True
            
            if(len(ov) == 0):
                # nothing found, can be removed
                return False
            if(sum(ov) == 0):
                # found only object which can be removed
                return False
            # otherwise always True
            return True
        
        def walk(o):
            for c in o['children']:
                walk(c)
            # current object is empty
            if(o['export_type'] == 'EMPTY'):
                # check all children if there are some renderable one, if so, keep current empty
                keep = check_renderables_in_tree(o)
                if(keep is False):
                    # if not, do not export it
                    o['export'] = False
        
        for o in h:
            walk(o)
        
        # split objects to lists
        instances = []
        meshes = []
        empties = []
        cameras = []
        bases = []
        suns = []
        references = []
        # asset_references = []
        volumetrics = []
        
        def walk(o):
            for c in o['children']:
                walk(c)
            if(o['export'] is not False):
                # only object marked for export..
                if(o['export_type'] == 'MESH'):
                    meshes.append(o)
                elif(o['export_type'] == 'EMPTY'):
                    empties.append(o)
                elif(o['export_type'] == 'CAMERA'):
                    cameras.append(o)
                elif(o['export_type'] == 'BASE_INSTANCE'):
                    bases.append(o)
                elif(o['export_type'] == 'INSTANCE'):
                    instances.append(o)
                elif(o['export_type'] == 'SUN'):
                    suns.append(o)
                elif(o['export_type'] == 'REFERENCE'):
                    references.append(o)
                elif(o['export_type'] == 'VOLUMETRICS'):
                    volumetrics.append(o)
            else:
                # objects that will not export/render, remove meshes if they are converted from non-mesh object
                if(o['converted']):
                    me = o['mesh']
                    # using the EAFP principle, hehe, lazy me..
                    try:
                        if(me.users == 0 and not me.use_fake_user):
                            bpy.data.meshes.remove(me)
                    except ReferenceError:
                        # already removed..
                        pass
        
        for o in h:
            walk(o)
        
        self._meshes = meshes
        self._bases = bases
        self._instances = instances
        self._empties = empties
        self._cameras = cameras
        self._references = references
        # self._asset_references = asset_references
        self._volumetrics = volumetrics
        
        # no visible camera
        if(len(self._cameras) == 0):
            log("no visible and active camera in scene!", 2, LogStyles.WARNING)
            log("trying to find hidden active camera..", 3)
            ac = self.context.scene.camera
            if(ac is not None):
                # there is one active in scene, try to find it
                def walk(o):
                    for c in o['children']:
                        walk(c)
                    ob = o['object']
                    if(ob == ac):
                        cam = o
                        cam['export'] = True
                        self._cameras.append(cam)
                        log("found active camera: '{}' and added to scene.".format(cam['object'].name), 3)
                for o in h:
                    walk(o)
        
        # dupliverts / duplifaces
        self._duplicates = []
        
        def find_dupli_object(obj):
            for o in self._meshes:
                ob = o['object']
                if(ob == obj):
                    return o
            for o in self._bases:
                ob = o['object']
                if(ob == obj):
                    return o
            return None
        
        def put_to_bases(o):
            if(o not in self._bases and o in self._meshes):
                self._meshes.remove(o)
                self._bases.append(o)
        
        # duplicate list, because i might modify it while looping it..
        
        class Unique():
            # increments its value each time it is accessed or used as string.
            # it is overkill a bit, because i can just increment an int after each of its use, but this is good practice and might be useful in future..
            
            def __init__(self, v=0, ):
                self.__v = v

            @property
            def value(self):
                v = self.__v
                # increment each time it is accessed
                self.__v += 1
                return v
            
            def __str__(self):
                return str(self.value)
        
        unique = Unique()
        meshes = self._meshes[:]
        for o in meshes:
            ob = o['object']
            if(ob.dupli_type != 'NONE'):
                if(ob.dupli_type == 'FACES' or ob.dupli_type == 'VERTS' or ob.dupli_type == 'GROUP'):
                    ob.dupli_list_create(self.context.scene, settings='RENDER')
                    for dli in ob.dupli_list:
                        do = dli.object
                        # i've just spent half an hour trying to understand why these lousy matrices does not work
                        # then suddenly i realized that calling dupli_list_clear might remove them from memory
                        # and i am just getting some garbage data..
                        # remember this in future, and do NOT use data after freeing them from memory
                        dm = dli.matrix.copy()
                        di = dli.index
                        io = find_dupli_object(do)
                        if(self.use_instances):
                            put_to_bases(io)
                        if(io is not None):
                            nm = "{}-duplicator-{}-{}-{}".format(ob.name, io['object'].name, di, unique)
                            d = {'object': do,
                                 'dupli_name': nm,
                                 'dupli_matrix': dm,
                                 'children': [],
                                 'export': True,
                                 'export_type': 'INSTANCE',
                                 'mesh': io['mesh'],
                                 'converted': False,
                                 # 'parent': None,
                                 'parent': o,
                                 'type': 'MESH', }
                            self._duplicates.append(d)
                    ob.dupli_list_clear()
            
            if(len(ob.particle_systems) > 0):
                for ps in ob.particle_systems:
                    pset = ps.settings
                    if(pset.maxwell_render.use == 'PARTICLE_INSTANCES'):
                        if(pset.render_type in ['OBJECT', 'GROUP', ]):
                            mpi = pset.maxwell_render.instances
                            
                            def process_dupli_list(ob):
                                ob.dupli_list_create(self.context.scene, settings='RENDER')
                                for dli in ob.dupli_list:
                                    do = dli.object
                                    dm = dli.matrix.copy()
                                    di = dli.index
                                    io = find_dupli_object(do)
                                    if(self.use_instances and io is not None):
                                        put_to_bases(io)
                                    if(io is not None):
                                        nm = "{}-duplicator-{}-{}-{}".format(ob.name, io['object'].name, di, unique)
                                        d = {'object': do,
                                             'dupli_name': nm,
                                             'dupli_matrix': dm,
                                             'children': [],
                                             'export': True,
                                             'export_type': 'INSTANCE',
                                             'mesh': io['mesh'],
                                             'converted': False,
                                             # 'parent': None,
                                             'extra_options': {'hide': mpi.hide, },
                                             'parent': o,
                                             'type': 'MESH', }
                                        self._duplicates.append(d)
                                    else:
                                        log("{} > {} > {}: instance base object not visible and renderable".format(ob.name, ps.name, 'PARTICLE_INSTANCES'), 2, LogStyles.WARNING, )
                                ob.dupli_list_clear()
                            
                            if(pset.render_type == 'GROUP' and pset.dupli_group is not None):
                                process_dupli_list(ob)
                            elif(pset.render_type == 'OBJECT' and pset.dupli_object is not None):
                                process_dupli_list(ob)
                            else:
                                log("{} > {} > {}: invalid settings, see 'Maxwell Particle Instances' panel.".format(ob.name, ps.name, 'PARTICLE_INSTANCES'), 2, LogStyles.WARNING, )
                            
                        else:
                            # this is user's error, is clearly visible in ui that only OBJECT and GROUP are supported
                            # no.. report it as well..
                            log("{} > {} > {}: invalid settings, see 'Maxwell Particle Instances' panel.".format(ob.name, ps.name, 'PARTICLE_INSTANCES'), 2, LogStyles.WARNING, )
        
        empties = self._empties[:]
        for o in empties:
            ob = o['object']
            # check for objects that are exported as empty (eg real empty or mesh without faces), those cas still carry duplis
            # or check for meshes with zero faces but vertex duplis
            if((ob.dupli_type == 'GROUP' and ob.dupli_group) or (ob.type == 'MESH' and len(ob.data.polygons) == 0 and ob.dupli_type == 'VERTS')):
                ob.dupli_list_create(self.context.scene, settings='RENDER')
                for dli in ob.dupli_list:
                    do = dli.object
                    dm = dli.matrix.copy()
                    di = dli.index
                    io = find_dupli_object(do)
                    if(self.use_instances):
                        put_to_bases(io)
                    if(io is not None):
                        nm = "{}-duplicator-{}-{}-{}".format(ob.name, io['object'].name, di, unique)
                        d = {'object': do,
                             'dupli_name': nm,
                             'dupli_matrix': dm,
                             'children': [],
                             'export': True,
                             'export_type': 'INSTANCE',
                             'mesh': io['mesh'],
                             'converted': False,
                             'parent': o,
                             'type': 'MESH', }
                        self._duplicates.append(d)
                ob.dupli_list_clear()
        
        # find instances without base and change first one to base, quick and dirty..
        # this case happens when object (by name chosen as base) is on hidden layer and marked to be not exported
        # also, hope this is the last change of this nasty piece of code..
        def find_base_object_name(mnm):
            for bo in self._bases:
                if(bo['mesh'].name == mnm):
                    return bo['object'].name
        
        instances2 = self._instances[:]
        for o in instances2:
            if(find_base_object_name(o['mesh'].name) is None):
                o['export_type'] = 'BASE_INSTANCE'
                self._bases.append(o)
                self._instances.remove(o)
        
        # overriden instances
        instances2 = self._instances[:]
        for o in instances2:
            m = o['object'].maxwell_render
            if(m.override_instance):
                o['export_type'] = 'MESH'
                o['override_instance'] = o['object'].data
                self._meshes.append(o)
                self._instances.remove(o)
        
        # other objects and modifiers
        particles = []
        modifiers = []
        
        def walk(o):
            for c in o['children']:
                walk(c)
            if(o['export'] is not False):
                ob = o['object']
                if(len(ob.particle_systems) != 0):
                    for ps in ob.particle_systems:
                        mx = ps.settings.maxwell_render
                        mod = None
                        for m in ob.modifiers:
                            if(m.type == 'PARTICLE_SYSTEM'):
                                if(m.particle_system == ps):
                                    mod = m
                                    break
                        if(not mod.show_render):
                            # not renderable, skip
                            continue
                        p = {'object': ps,
                             'children': [],
                             'export': mod.show_render,
                             'export_type': '',
                             'parent': ob,
                             'psys': ps,
                             'type': None, }
                        p['export_type'] = mx.use
                        
                        if(mx.use in ['PARTICLES', 'HAIR', ]):
                            particles.append(p)
                            # those two should be put into hierarchy, they are real objects.. the rest are just modifiers
                            o['children'].append(p)
                        else:
                            # in case of cloner..
                            modifiers.append(p)
                if(ob.maxwell_render.scatter.enabled):
                    p = {'object': ob, 'children': [], 'export': True, 'parent': ob, 'type': None, 'export_type': 'SCATTER', }
                    modifiers.append(p)
                if(ob.maxwell_render.subdivision.enabled):
                    p = {'object': ob, 'children': [], 'export': True, 'parent': ob, 'type': None, 'export_type': 'SUBDIVISION', }
                    modifiers.append(p)
                if(ob.maxwell_render.sea.enabled):
                    p = {'object': ob, 'children': [], 'export': True, 'parent': ob, 'type': None, 'export_type': 'SEA', }
                    modifiers.append(p)
                if(ob.maxwell_render.grass.enabled):
                    p = {'object': ob, 'children': [], 'export': True, 'parent': ob, 'type': None, 'export_type': 'GRASS', }
                    modifiers.append(p)
        
        for o in h:
            walk(o)
        
        self._particles = particles
        self._modifiers = modifiers
        
        def walk(o):
            for c in o['children']:
                walk(c)
            if(o['object'] in no_polygons_meshes and o['export'] is True):
                o['export_type'] = 'EMPTY'
                self._meshes.remove(o)
                self._empties.append(o)
        
        for o in h:
            walk(o)
        
        # handle hidden bases
        def walk(o):
            for c in o['children']:
                walk(c)
            
            ob = o['object']
            
            if('extra_options' in o):
                if('hidden_base' in o['extra_options']):
                    if(o['extra_options']['hidden_base'] is True):
                        # search for ob in self._bases
                        base = None
                        for bo in self._bases:
                            if(bo['object'] == ob):
                                base = bo
                        # find its first instance
                        instance = None
                        dos = []
                        for do in self._duplicates:
                            if(do['mesh'] == base['mesh']):
                                dos.append(do)
                        if(len(dos) > 0):
                            dos.sort(key=lambda k: k['dupli_name'])
                            instance = dos[0]
                        
                        if(base is not None and instance is not None):
                            # swap that instance with base (transformation, parent)
                            swap_base = base.copy()
                            swap_base['extra_options']['swap_matrix'] = instance['dupli_matrix']
                            swap_base['extra_options']['swap_parent'] = instance['parent']
                            if('extra_options' in instance):
                                if('hide' in instance['extra_options']):
                                    swap_base['extra_options']['hide'] = instance['extra_options']['hide']
                            self._bases.remove(base)
                            self._bases.append(swap_base)
                            # change base to empty to keep hierarchy
                            swap_empty = base.copy()
                            swap_empty['export_type'] = 'EMPTY'
                            swap_empty['extra_options']['swap_name'] = "{}-{}".format(base['object'].name, uuid.uuid1())
                            self._empties.append(swap_empty)
                            # remove instance completelly
                            self._duplicates.remove(instance)
        
        for o in h:
            walk(o)
        
        # handle particle system settings 'use_render_emitter'
        for o in self._particles:
            hide = False
            
            ob = o['parent']
            obmx = ob.maxwell_render
            pset = o['psys'].settings
            if(pset.use_render_emitter is True):
                if(obmx.hide is True):
                    # ps overrides ob
                    log("object '{}' is set to hide from render, but particle system '{}' emitter is set to render. object will render.".format(ob.name, o['psys'].name), 2, LogStyles.WARNING, )
                    hide = False
                else:
                    # ok, use ps settings
                    hide = False
                    # 'extra_options': {'hide': mpi.hide, },
            else:
                if(obmx.hide is True):
                    # ok, use os settings
                    hide = True
                else:
                    # ps overrides ob
                    log("object '{}' is set to render, but particle system '{}' emitter is set to hide from render. object will not render.".format(ob.name, o['psys'].name), 2, LogStyles.WARNING, )
                    hide = True
            
            found = False
            for i, o in enumerate(self._meshes):
                if(o['object'] == ob):
                    found = True
                    self._meshes[i]['extra_options'] = {'hide': hide, }
                    break
            if(not found):
                for i, o in enumerate(self._bases):
                    if(o['object'] == ob):
                        found = True
                        self._meshes[i]['extra_options'] = {'hide': hide, }
                        break
        
        # ----------------------------------------------------------------------------------
        # (everything above this line is pure magic, below is just standard code)
        
        # import pprint
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(h)
        
        # print("-" * 100)
        # raise Exception()
        
        return h
    
    def _export(self):
        # init stats
        self.stats = MXSExportStats()
        
        # collect all objects to be exported, split them by type. keep this dict if hierarchy would be needed
        log("collecting objects..", 1, LogStyles.MESSAGE, )
        self.tree = self._collect()
        
        ls = []
        for o in self._empties:
            ls.append(o['object'])
        for o in self._meshes:
            ls.append(o['object'])
        for o in self._bases:
            ls.append(o['object'])
        for o in self._instances:
            ls.append(o['object'])
        for o in self._duplicates:
            ls.append(o['object'])
        for o in self._references:
            ls.append(o['object'])
        for o in self._volumetrics:
            ls.append(o['object'])
        MXSDatabase.set_object_export_list(ls)
        
        # find and set active camera
        cam = None
        for c in self._cameras:
            if(bpy.context.scene.camera == c['object']):
                cam = c['object']
        MXSMotionBlurHelper.init(cam)
        
        # count all objects, will be used for progress reporting.. not quite precise, but good for now.. better than nothing
        self.progress_current = 0
        c = 0
        c += len(bpy.data.materials)
        c += len(self._cameras)
        c += len(self._empties)
        c += len(self._meshes)
        c += len(self._bases)
        c += len(self._instances)
        c += len(self._duplicates)
        c += len(self._references)
        c += len(self._particles)
        c += len(self._volumetrics)
        c += len(self._modifiers)
        c += 1  # environment
        c += 1  # scene
        self.progress_count = c
        
        if(self.use_wireframe):
            log("writing wireframe base objects..", 1, LogStyles.MESSAGE, )
            
            mx = self.context.scene.maxwell_render
            
            # correct progress counts..
            c = self.progress_count
            c += 1  # base
            c += 1  # empty
            # c += 2  # wire and clay materials
            c += len(self._meshes)
            c += len(self._bases)
            c += len(self._instances)
            c += len(self._duplicates)
            self.progress_count = c
            
            wc = MXSWireframeContainer(self.uuid)
            self._write(wc)
            self.wireframe_container_name = wc.m_name
            
            wb = MXSWireframeBase(self.uuid)
            wb.m_parent = wc.m_name
            self._write(wb)
            self.wireframe_base_name = wb.m_name
        
        log("writing materials:", 1, LogStyles.MESSAGE, )
        for mat in bpy.data.materials:
            mx = mat.maxwell_render
            # only materials with (users - fake_user) > 0
            u = mat.users
            if(mat.use_fake_user):
                u -= 1
            # count material usage as backface material and in extensions
            for d in self._empties:
                if(d['object'].maxwell_render.backface_material == mat.name):
                    u += 1
            for d in self._meshes:
                if(d['object'].maxwell_render.backface_material == mat.name):
                    u += 1
            for d in self._bases:
                if(d['object'].maxwell_render.backface_material == mat.name):
                    u += 1
            for d in self._references:
                if(d['object'].maxwell_render.reference.material == mat.name):
                    u += 1
                if(d['object'].maxwell_render.reference.backface_material == mat.name):
                    u += 1
            for d in self._particles:
                if(d['export_type'] == 'HAIR'):
                    if(d['psys'].settings.maxwell_render.hair.material == mat.name):
                        u += 1
                    if(d['psys'].settings.maxwell_render.hair.backface_material == mat.name):
                        u += 1
                if(d['export_type'] == 'PARTICLES'):
                    if(d['psys'].settings.maxwell_render.particles.material == mat.name):
                        u += 1
                    if(d['psys'].settings.maxwell_render.particles.backface_material == mat.name):
                        u += 1
            for d in self._volumetrics:
                if(d['object'].maxwell_render.volumetrics.material == mat.name):
                    u += 1
                if(d['object'].maxwell_render.volumetrics.backface_material == mat.name):
                    u += 1
            for d in self._modifiers:
                if(d['export_type'] == 'GRASS'):
                    if(d['object'].maxwell_render.grass.material == mat.name):
                        u += 1
                    if(d['object'].maxwell_render.grass.backface_material == mat.name):
                        u += 1
                if(d['export_type'] == 'SEA'):
                    if(d['object'].maxwell_render.sea.material == mat.name):
                        u += 1
                    if(d['object'].maxwell_render.sea.backface_material == mat.name):
                        u += 1
            
            if(u > 0):
                if(mx.use == 'REFERENCE'):
                    mxm = MXSMaterialMXM(mat.name, path=mx.mxm_file, embed=mx.embed, )
                    self._write(mxm)
                elif(mx.use == 'CUSTOM'):
                    cmat = MXSMaterialCustom(mat.name)
                    self._write(cmat)
                else:
                    exmat = MXSMaterialExtension(mat.name)
                    self._write(exmat)
            else:
                log("'{}' > unused material, skipping..".format(mat.name), 2, )
        
        log("writing cameras:", 1, LogStyles.MESSAGE, )
        for d in self._cameras:
            o = MXSCamera(d)
            self._write(o)
        
        log("writing empties:", 1, LogStyles.MESSAGE, )
        for d in self._empties:
            o = MXSEmpty(d)
            self._write(o)
        
        log("writing meshes:", 1, LogStyles.MESSAGE, )
        meshes = []
        for d in self._meshes:
            o = MXSMesh(d)
            self._write(o)
            meshes.append(o)
            
            if(self.use_wireframe):
                w = MXSWireframeInstances(o, self.wireframe_base_name)
                w.m_parent = self.wireframe_container_name
                self._write(w)
            
            if(self.use_subdivision):
                mod = o.subdivision_modifier
                if(mod is not None):
                    self._write(mod)
        
        log("writing instance bases:", 1, LogStyles.MESSAGE, )
        bases = []
        for d in self._bases:
            o = MXSMesh(d)
            self._write(o)
            
            bases.append(o)
            meshes.append(o)
            
            if(self.use_wireframe):
                w = MXSWireframeInstances(o, self.wireframe_base_name)
                w.m_parent = self.wireframe_container_name
                self._write(w)
            
            if(self.use_subdivision):
                mod = o.subdivision_modifier
                if(mod is not None):
                    self._write(mod)
        
        def find_base(mnm):
            for b in bases:
                if(b.mesh_name == mnm):
                    return b
        
        log("writing instances:", 1, LogStyles.MESSAGE, )
        for d in self._instances:
            if(d['converted']):
                b = find_base(d['object'].data.name)
            else:
                b = find_base(d['mesh'].name)
            o = MXSMeshInstance(d, b, )
            self._write(o)
            
            if(self.use_wireframe):
                w = MXSWireframeInstances(o, self.wireframe_base_name)
                w.m_parent = self.wireframe_container_name
                self._write(w)
        
        log("writing duplicates:", 1, LogStyles.MESSAGE, )
        for d in self._duplicates:
            if(not self.use_instances):
                o = MXSMesh(d)
                self._write(o)
            else:
                b = find_base(d['mesh'].name)
                o = MXSMeshInstance(d, b, )
                self._write(o)
            
            if(self.use_wireframe):
                w = MXSWireframeInstances(o, self.wireframe_base_name)
                w.m_parent = self.wireframe_container_name
                self._write(w)
        
        log("writing mxs references:", 1, LogStyles.MESSAGE, )
        for d in self._references:
            o = MXSReference(d)
            self._write(o)
        
        # log("writing asset references:", 1, LogStyles.MESSAGE, )
        # for d in self._asset_references:
        #     o = MXSAssetReference(d)
        #     self._write(o)
        
        log("writing particles:", 1, LogStyles.MESSAGE, )
        for d in self._particles:
            ps = d['object']
            if(ps.settings.maxwell_render.use == 'PARTICLES'):
                o = MXSParticles(d)
                self._write(o)
            if(ps.settings.maxwell_render.use == 'HAIR'):
                o = MXSHair(d)
                self._write(o)
        
        log("writing volumetrics:", 1, LogStyles.MESSAGE, )
        for d in self._volumetrics:
            o = MXSVolumetrics(d)
            self._write(o)
        
        def find_mesh(nm):
            for m in meshes:
                if(m.m_name == nm):
                    return m
        
        log("writing object modifiers:", 1, LogStyles.MESSAGE, )
        for d in self._modifiers:
            if(d['export_type'] == 'CLONER'):
                o = MXSCloner(d)
                self._write(o)
            elif(d['export_type'] == 'GRASS'):
                o = MXSGrass(d)
                self._write(o)
            elif(d['export_type'] == 'SCATTER'):
                o = MXSScatter(d)
                self._write(o)
            elif(d['export_type'] == 'SUBDIVISION'):
                me = find_mesh(d['object'].name)
                if(me):
                    qp = None
                    if(me.quad_pairs):
                        qp = me.quad_pairs
                    o = MXSSubdivision(d, qp, )
                    self._write(o)
            elif(d['export_type'] == 'SEA'):
                o = MXSSea(d)
                self._write(o)
        
        log("writing environment..", 1, LogStyles.MESSAGE, )
        o = MXSEnvironment()
        self._write(o)
        
        log("writing custom alphas:", 1, LogStyles.MESSAGE, )
        groups = []
        
        mx = bpy.context.scene.maxwell_render
        if(mx.custom_alphas_use_groups):
            # all object are processed now, i can work with all object which have made it through
            allowed = ['MESH', 'MESH_INSTANCE', 'PARTICLES', 'HAIR', 'REFERENCE', 'VOLUMETRICS', 'SEA', ]
            children = ['PARTICLES', 'HAIR', 'SEA', ]
            
            if(system.PLATFORM == 'Darwin'):
                # my humble apologies for following if-for-if-for.. loop
                for g in bpy.data.groups:
                    gmx = g.maxwell_render
                    if(gmx.custom_alpha_use):
                        a = {'name': MXSDatabase.only_sanitize_name(g.name), 'objects': [], 'opaque': gmx.custom_alpha_opaque, }
                        for o in g.objects:
                            for mo in self.serialized_data:
                                if(mo['type'] in allowed):
                                    orgnm = MXSDatabase.object_original_name_from_export_name(mo['name'])
                                    if(o.name == orgnm):
                                        a['objects'].append(mo['name'])
                                        # also add children of objects such as particles, hair, etc.. objects which are created as child of original
                                        for ch in self.serialized_data:
                                            if(ch['type'] in allowed):
                                                if(ch['parent'] == mo['name']):
                                                    if(ch['type'] in children):
                                                        a['objects'].append(ch['name'])
                                                        break
                        groups.append(a)
            elif(system.PLATFORM == 'Linux' or system.PLATFORM == 'Windows'):
                # really ugly.. i know
                for g in bpy.data.groups:
                    gmx = g.maxwell_render
                    if(gmx.custom_alpha_use):
                        a = {'name': MXSDatabase.only_sanitize_name(g.name), 'objects': [], 'opaque': gmx.custom_alpha_opaque, }
                        for o in g.objects:
                            for mo in self.hierarchy:
                                # hierarchy: (0: name, 1: parent, 2: type), ...
                                # type
                                if(mo[2] in allowed):
                                    # name
                                    orgnm = MXSDatabase.object_original_name_from_export_name(mo[0])
                                    if(o.name == orgnm):
                                        a['objects'].append(mo[0])
                                        # also add children of objects such as particles, hair, etc.. objects which are created as child of original
                                        for ch in self.hierarchy:
                                            # type
                                            if(ch[2] in allowed):
                                                # parent, name
                                                if(ch[1] == mo[0]):
                                                    # type
                                                    if(ch[2] in children):
                                                        # name
                                                        a['objects'].append(ch[0])
                                                        break
                        groups.append(a)
        else:
            alphas = mx.custom_alphas_manual.alphas
            for alpha in alphas:
                # obs = [bpy.data.objects[o.name] for o in alpha.objects]
                # mats = [bpy.data.materials[m.name] for m in alpha.materials]
                obs = []
                for o in alpha.objects:
                    if(o.name in bpy.data.objects):
                        obs.append(bpy.data.objects[o.name])
                    else:
                        log("'{}': missing object: '{}'".format(alpha.name, o.name), 3, LogStyles.WARNING, )
                mats = []
                for m in alpha.materials:
                    if(m.name in bpy.data.materials):
                        mats.append(bpy.data.materials[m.name])
                    else:
                        log("'{}': missing material: '{}'".format(alpha.name, m.name), 3, LogStyles.WARNING, )
                
                a = {'name': MXSDatabase.only_sanitize_name(alpha.name), 'opaque': alpha.opaque, 'objects': [], 'materials': [], }
                
                allowed = ['MESH', 'MESH_INSTANCE', 'PARTICLES', 'HAIR', 'REFERENCE', 'VOLUMETRICS', 'SEA', ]
                children = ['PARTICLES', 'HAIR', 'SEA', ]
                if(system.PLATFORM == 'Darwin'):
                    for o in obs:
                        for mo in self.serialized_data:
                            if(mo['type'] in allowed):
                                orgnm = MXSDatabase.object_original_name_from_export_name(mo['name'])
                                if(o.name == orgnm):
                                    a['objects'].append(mo['name'])
                                    # also add children of objects such as particles, hair, etc.. objects which are created as child of original
                                    for ch in self.serialized_data:
                                        if(ch['type'] in allowed):
                                            if(ch['parent'] == mo['name']):
                                                if(ch['type'] in children):
                                                    a['objects'].append(ch['name'])
                                                    break
                elif(system.PLATFORM == 'Linux' or system.PLATFORM == 'Windows'):
                    for o in obs:
                        for mo in self.hierarchy:
                            if(mo[2] in allowed):
                                orgnm = MXSDatabase.object_original_name_from_export_name(mo[0])
                                if(o.name == orgnm):
                                    a['objects'].append(mo[0])
                                    for ch in self.hierarchy:
                                        if(ch[2] in allowed):
                                            if(ch[1] == mo[0]):
                                                if(ch[2] in children):
                                                    a['objects'].append(ch[0])
                                                    break
                for mat in mats:
                    # only materials with (users - fake_user) > 0
                    u = mat.users
                    if(mat.use_fake_user):
                        u -= 1
                    if(u > 0):
                        a['materials'].append(mat.name)
                groups.append(a)
        
        if(mx.custom_alphas_use_groups):
            for g in groups:
                log("{} > {}".format(g['name'], g['objects']), 2)
        else:
            for g in groups:
                log("{} > objects: {}, materials: {}".format(g['name'], g['objects'], g['materials']), 2)
        
        log("writing scene properties..", 1, LogStyles.MESSAGE, )
        o = MXSScene(self.mxs_path, groups, )
        self._write(o)
        
        if(self.use_wireframe):
            utils.wipe_out_object(bpy.data.objects[self.wireframe_base_name], and_data=True, )
            utils.wipe_out_object(bpy.data.objects[self.wireframe_container_name], and_data=True, )
    
    def _write(self, o, ):
        # add to stats
        if(not o.skip):
            self.stats.add(o)
        
        self._progress()
        
        if(system.PLATFORM == 'Darwin'):
            # skip marked
            if(o.skip):
                return
            
            # mesh, particles and hair have their own file format, have to split data
            if(o.m_type == 'MESH' or o.m_type == 'WIREFRAME_BASE'):
                nm = "{}-{}".format(o.m_name, uuid.uuid1())
                
                # split data to mesh / properties
                md = {'name': o.m_name,
                      'num_positions': o.m_num_positions,
                      'vertices': o.m_vertices,
                      'normals': o.m_normals,
                      'triangles': o.m_triangles,
                      'triangle_normals': o.m_triangle_normals,
                      'uv_channels': o.m_uv_channels,
                      'num_materials': o.m_num_materials,
                      'triangle_materials': o.m_triangle_materials, }
                p = os.path.join(self.tmp_dir, "{0}.binmesh".format(nm))
                w = tmpio.MXSBinMeshWriter(p, **md)
                
                d = {'name': o.m_name,
                     'num_vertexes': len(o.m_vertices[0]),
                     # 'num_normals': len(o.m_normals[0]) + len(o.m_triangles),
                     'num_normals': len(o.m_normals[0]) + len(o.m_triangle_normals[0]),
                     'num_triangles': len(o.m_triangles),
                     'num_positions_per_vertex': o.m_num_positions,
                     'mesh_data': nm,
                     'parent': o.m_parent,
                     'opacity': o.m_opacity,
                     'hidden_camera': o.m_hidden_camera,
                     'hidden_camera_in_shadow_channel': o.m_hidden_camera_in_shadow_channel,
                     'hidden_global_illumination': o.m_hidden_global_illumination,
                     'hidden_reflections_refractions': o.m_hidden_reflections_refractions,
                     'hidden_zclip_planes': o.m_hidden_zclip_planes,
                     'object_id': o.m_object_id,
                     'blocked_emitters': o.m_blocked_emitters,
                     
                     'num_materials': o.m_num_materials,
                     'materials': o.m_materials,
                     'backface_material': o.m_backface_material,
                     
                     'hide': o.m_hide,
                     'mesh_data_path': p,
                     'base': o.m_base,
                     'pivot': o.m_pivot,
                     'location': o.m_location,
                     'rotation': o.m_rotation,
                     'scale': o.m_scale,
                     
                     'sea_ext': None,
                     'scatter_ext': None,
                     'subdiv_ext': None,
                     
                     'motion_blur': o.m_motion_blur,
                     
                     # 'type': 'MESH',
                     'type': o.m_type, }
                
                self.mesh_data_paths.append(p)
                self.serialized_data.append(d)
                
            elif(o.m_type == 'HAIR'):
                nm = "{}-{}".format(o.m_name, uuid.uuid1())
                p = os.path.join(self.tmp_dir, "{0}.binhair".format(nm))
                w = tmpio.MXSBinHairWriter(p, o.data_locs)
                a = o._repr()
                a['hair_data_path'] = p
                self.hair_data_paths.append(p)
                
                self.serialized_data.append(a)
            elif(o.m_type == 'PARTICLES'):
                if(o.mxex.source != 'EXTERNAL_BIN'):
                    # not existing external .bin
                    if(o.m_embed):
                        # and data will be embedded in mxs (no external bin created)
                        nm = "{}-{}".format(o.m_name, uuid.uuid1())
                        p = os.path.join(self.tmp_dir, "{0}.binpart".format(nm))
                        w = tmpio.MXSBinParticlesWriter(p, o.m_pdata)
                        o.m_pdata = p
                        self.part_data_paths.append(p)
                a = o._repr()
                self.serialized_data.append(a)
            elif(o.m_type == 'CLONER'):
                if(o.mxex.source != 'EXTERNAL_BIN'):
                    if(o.m_embed):
                        nm = "{}-{}".format(o.m_name, uuid.uuid1())
                        p = os.path.join(self.tmp_dir, "{0}.binpart".format(nm))
                        w = tmpio.MXSBinParticlesWriter(p, o.m_pdata)
                        o.m_pdata = p
                        self.part_data_paths.append(p)
                a = o._repr()
                self.serialized_data.append(a)
            elif(o.m_type == 'WIREFRAME_INSTANCES'):
                n = "{}-{}".format(o.m_name, uuid.uuid1())
                p = os.path.join(self.tmp_dir, "{0}.binwire".format(n))
                w = tmpio.MXSBinWireWriter(p, o.m_wire_matrices)
                self.wire_data_paths.append(p)
                a = o._repr()
                a['wire_matrices'] = p
                self.serialized_data.append(a)
            else:
                a = o._repr()
                self.serialized_data.append(a)
            
            allowed = ['EMPTY', 'MESH', 'MESH_INSTANCE', 'PARTICLES', 'HAIR', 'REFERENCE', 'VOLUMETRICS', 'SEA', ]
            if(o.m_type in allowed):
                self.hierarchy.append((o.m_name, o.m_parent, o.m_type))
            
        elif(system.PLATFORM == 'Linux' or system.PLATFORM == 'Windows'):
            if(o.skip):
                return
            
            def pack_object_props(o):
                return (o.m_hide, o.m_opacity, o.m_object_id, o.m_hidden_camera, o.m_hidden_camera_in_shadow_channel,
                        o.m_hidden_global_illumination, o.m_hidden_reflections_refractions, o.m_hidden_zclip_planes,
                        o.m_blocked_emitters, )
            
            def pack_matrix(o):
                return (o.m_base, o.m_pivot, o.m_location, o.m_rotation, o.m_scale, )
            
            def pack_prefix(o, prefix, rm=True, ):
                d = o._repr()
                r = {}
                l = len(prefix)
                for k, v in d.items():
                    if(k.startswith(prefix)):
                        if(not rm):
                            r[k] = v
                        else:
                            r[k[l:]] = v
                return r
            
            if(o.m_type == 'MATERIAL'):
                self.mxs.material(o._repr())
            elif(o.m_type == 'CAMERA'):
                props = (o.m_name, o.m_number_of_steps, o.m_shutter, o.m_film_width, o.m_film_height, o.m_iso, o.m_aperture, o.m_diaphragm_angle,
                         o.m_diaphragm_blades, o.m_frame_rate, o.m_resolution_x, o.m_resolution_y, o.m_pixel_aspect, o.m_lens, )
                steps = o.m_steps
                lens_extra = None
                if(o.m_lens != 0):
                    if(o.m_lens == 3):
                        lens_extra = o.m_fov
                    elif(o.m_lens == 4):
                        lens_extra = o.m_azimuth
                    elif(o.m_lens == 5):
                        lens_extra = o.m_angle
                    elif(o.m_lens == 6):
                        lens_extra = (o.m_lls_type, o.m_lls_fovv, o.m_lls_fovh, o.m_lls_flip_ray_x, o.m_lls_flip_ray_y,
                                      o.m_lls_parallax_distance, o.m_lls_zenith_mode, o.m_lls_separation, o.m_lls_separation_map, )
                    elif(o.m_lens == 7):
                        lens_extra = (o.m_fs_type, o.m_fs_fov, o.m_fs_separation, o.m_fs_separation_map, o.m_fs_vertical_mode, o.m_fs_dome_radius,
                                      o.m_fs_head_turn_map, o.m_fs_dome_tilt_compensation, o.m_fs_dome_tilt, o.m_fs_head_tilt_map, )
                screen_region = None
                if(o.m_screen_region != 'NONE'):
                    screen_region = o.m_screen_region_xywh
                    screen_region = screen_region + (o.m_screen_region, )
                custom_bokeh = None
                if(o.m_custom_bokeh):
                    custom_bokeh = (o.m_bokeh_ratio, o.m_bokeh_angle, o.m_custom_bokeh)
                cut_planes = None
                if(o.m_set_cut_planes[2] != 0):
                    cut_planes = o.m_set_cut_planes
                shift_lens = None
                if(o.m_set_shift_lens != (0.0, 0.0)):
                    shift_lens = o.m_set_shift_lens
                self.mxs.camera(props, steps, o.m_active, lens_extra, o.m_response, screen_region, custom_bokeh, cut_planes, shift_lens, )
            elif(o.m_type == 'EMPTY'):
                self.mxs.empty(o.m_name, pack_matrix(o), o.m_motion_blur, pack_object_props(o), )
                self.hierarchy.append((o.m_name, o.m_parent, o.m_type))
            elif(o.m_type == 'MESH'):
                self.mxs.mesh(o.m_name, pack_matrix(o), o.m_motion_blur, o.m_num_positions,
                              o.m_vertices, o.m_normals, o.m_triangles, o.m_triangle_normals,
                              o.m_uv_channels, pack_object_props(o), o.m_num_materials,
                              o.m_materials, o.m_triangle_materials, o.m_backface_material, )
                self.hierarchy.append((o.m_name, o.m_parent, o.m_type))
            elif(o.m_type == 'MESH_INSTANCE'):
                self.mxs.instance(o.m_name, o.m_instanced, pack_matrix(o), o.m_motion_blur, pack_object_props(o), o.m_materials, o.m_backface_material, )
                self.hierarchy.append((o.m_name, o.m_parent, o.m_type))
            elif(o.m_type == 'SCENE'):
                other = {'protect': o.m_export_protect_mxs,
                         'extra_sampling_enabled': o.m_extra_sampling_enabled,
                         'extra_sampling_sl': o.m_extra_sampling_sl,
                         'extra_sampling_mask': o.m_extra_sampling_mask,
                         'extra_sampling_custom_alpha': o.m_extra_sampling_custom_alpha,
                         'extra_sampling_user_bitmap': o.m_extra_sampling_user_bitmap,
                         'extra_sampling_invert': o.m_extra_sampling_invert, }
                
                self.mxs.parameters(pack_prefix(o, 'scene_', ),
                                    pack_prefix(o, 'materials_', ),
                                    pack_prefix(o, 'globals_', ),
                                    pack_prefix(o, 'tone_', ),
                                    pack_prefix(o, 'simulens_', ),
                                    pack_prefix(o, 'illum_caustics_', ),
                                    other,
                                    pack_prefix(o, 'overlay_', ), )
                
                mxi = None
                if(o.m_output_mxi_enabled):
                    mxi = bpy.path.abspath(o.m_output_mxi)
                image = None
                image_depth = None
                if(o.m_output_image_enabled):
                    image = bpy.path.abspath(o.m_output_image)
                    image_depth = o.m_output_depth
                if(mxi is not None):
                    h, t = os.path.split(mxi)
                    n, e = os.path.splitext(t)
                    base_path = os.path.join(h, n)
                elif(image is not None):
                    h, t = os.path.split(image)
                    n, e = os.path.splitext(t)
                    base_path = os.path.join(h, n)
                else:
                    h, t = os.path.split(self.mxs_path)
                    n, e = os.path.splitext(t)
                    base_path = os.path.join(h, n)
                channels_output_mode = o.m_channels_output_mode
                channels_render = o.m_channels_render
                channels_render_type = o.m_channels_render_type
                
                self.mxs.channels(base_path, mxi, image, image_depth, channels_output_mode, channels_render, channels_render_type, pack_prefix(o, 'channels_', False, ), )
                
                self.mxs.custom_alphas(o.m_channels_custom_alpha_groups)
                
            elif(o.m_type == 'ENVIRONMENT'):
                env_type = o.m_env_type
                if(env_type == 'NONE'):
                    self.mxs.environment(None)
                    return
                
                sky_type = o.m_sky_type
                sky = pack_prefix(o, 'sky_', False, )
                dome = pack_prefix(o, 'dome_', False, )
                sun_type = o.m_sun_type
                sun = None
                if(sun_type != 'DISABLED'):
                    sun = pack_prefix(o, 'sun_', False, )
                    v = Vector((o.m_sun_dir_x, o.m_sun_dir_y, o.m_sun_dir_z))
                    sun['sun_dir_x'] = v.x
                    sun['sun_dir_y'] = v.y
                    sun['sun_dir_z'] = v.z
                ibl = None
                if(env_type == 'IMAGE_BASED'):
                    ibl = pack_prefix(o, 'ibl_', False, )
                
                self.mxs.environment(env_type, sky_type, sky, dome, sun_type, sun, ibl, )
            elif(o.m_type == 'PARTICLES'):
                properties = pack_prefix(o, 'bin_', )
                properties['embed'] = o.m_embed
                properties['pdata'] = o.m_pdata
                self.mxs.ext_particles(o.m_name, properties, pack_matrix(o), o.m_motion_blur, pack_object_props(o), o.m_material, o.m_backface_material, )
                self.hierarchy.append((o.m_name, o.m_parent, o.m_type))
            elif(o.m_type == 'HAIR'):
                if(o.m_extension == 'MGrassP'):
                    rr = o.m_grass_root_width
                    tr = o.m_grass_tip_width
                    dm = o.m_display_max_blades
                else:
                    rr = o.m_hair_root_radius
                    tr = o.m_hair_tip_radius
                    dm = o.m_display_max_hairs
                
                data = o.m_data
                data['HAIR_POINTS'] = o.data_locs
                
                self.mxs.ext_hair(o.m_name, o.m_extension, pack_matrix(o), o.m_motion_blur,
                                  rr, tr, o.m_data, pack_object_props(o), o.m_display_percent,
                                  dm, o.m_material, o.m_backface_material, )
                self.hierarchy.append((o.m_name, o.m_parent, o.m_type))
            elif(o.m_type == 'REFERENCE'):
                flags = (o.m_flag_override_hide, o.m_flag_override_hide_to_camera, o.m_flag_override_hide_to_refl_refr, o.m_flag_override_hide_to_gi, )
                self.mxs.reference(o.m_name, o.m_path, flags, pack_matrix(o), o.m_motion_blur, pack_object_props(o), o.m_material, o.m_backface_material, )
                self.hierarchy.append((o.m_name, o.m_parent, o.m_type))
            elif(o.m_type == 'VOLUMETRICS'):
                properties = (o.m_vtype, o.m_density, o.m_noise_seed, o.m_noise_low, o.m_noise_high, o.m_noise_detail, o.m_noise_octaves, o.m_noise_persistence)
                self.mxs.ext_volumetrics(o.m_name, properties, pack_matrix(o), o.m_motion_blur, pack_object_props(o), o.m_material, o.m_backface_material, )
                self.hierarchy.append((o.m_name, o.m_parent, o.m_type))
            elif(o.m_type == 'SUBDIVISION'):
                self.mxs.mod_subdivision(o.m_object, o.m_level, o.m_scheme, o.m_interpolation, o.m_crease, o.m_smooth, o.m_quad_pairs, )
            elif(o.m_type == 'SCATTER'):
                density = (o.m_density, o.m_density_map, )
                scale = (o.m_scale_x, o.m_scale_y, o.m_scale_z, o.m_scale_map, o.m_scale_variation_x, o.m_scale_variation_y, o.m_scale_variation_z, o.m_scale_uniform, )
                rotation = (o.m_rotation_x, o.m_rotation_y, o.m_rotation_z, o.m_rotation_map,
                            o.m_rotation_variation_x, o.m_rotation_variation_y, o.m_rotation_variation_z, o.m_rotation_direction, )
                lod = (o.m_lod, o.m_lod_min_distance, o.m_lod_max_distance, o.m_lod_max_distance_density, )
                angle = (o.m_direction_type, o.m_initial_angle, o.m_initial_angle_variation, o.m_initial_angle_map, )
                self.mxs.mod_scatter(o.m_object, o.m_scatter_object, o.m_inherit_objectid, o.m_remove_overlapped, density, o.m_seed, scale, rotation, lod, angle, o.m_display_percent, o.m_display_max_blades, )
            elif(o.m_type == 'GRASS'):
                properties = {'density': o.m_density,
                              'density_map': o.m_density_map,
                              'length': o.m_length,
                              'length_map': o.m_length_map,
                              'length_variation': o.m_length_variation,
                              'root_width': o.m_root_width,
                              'tip_width': o.m_tip_width,
                              'direction_type': o.m_direction_type,
                              'initial_angle': o.m_initial_angle,
                              'initial_angle_map': o.m_initial_angle_map,
                              'initial_angle_variation': o.m_initial_angle_variation,
                              'start_bend': o.m_start_bend,
                              'start_bend_map': o.m_start_bend_map,
                              'start_bend_variation': o.m_start_bend_variation,
                              'bend_radius': o.m_bend_radius,
                              'bend_radius_map': o.m_bend_radius_map,
                              'bend_radius_variation': o.m_bend_radius_variation,
                              'bend_angle': o.m_bend_angle,
                              'bend_angle_map': o.m_bend_angle_map,
                              'bend_angle_variation': o.m_bend_angle_variation,
                              'cut_off': o.m_cut_off,
                              'cut_off_map': o.m_cut_off_map,
                              'cut_off_variation': o.m_cut_off_variation,
                              'points_per_blade': o.m_points_per_blade,
                              'primitive_type': o.m_primitive_type,
                              'seed': o.m_seed,
                              'lod': o.m_lod,
                              'lod_max_distance': o.m_lod_max_distance,
                              'lod_max_distance_density': o.m_lod_max_distance_density,
                              'lod_min_distance': o.m_lod_min_distance,
                              'display_max_blades': o.m_display_max_blades,
                              'display_percent': o.m_display_percent, }
                self.mxs.mod_grass(o.m_object, properties, o.m_material, o.m_backface_material, )
            elif(o.m_type == 'CLONER'):
                self.mxs.mod_cloner(o.m_parent, o.m_cloned_object, o.m_render_emitter, o.m_pdata, o.m_radius, o.m_mb_factor,
                                    o.m_load_percent, o.m_start_offset, o.m_extra_npp, o.m_extra_p_dispersion, o.m_extra_p_deformation,
                                    o.m_align_to_velocity, o.m_scale_with_radius, o.m_inherit_obj_id, o.m_frame, o.m_fps,
                                    o.m_display_percent, o.m_display_max, )
            elif(o.m_type == 'SEA'):
                geometry = (o.m_reference_time, o.m_resolution, o.m_ocean_depth, o.m_vertical_scale, o.m_ocean_dim, o.m_ocean_seed,
                            o.m_enable_choppyness, o.m_choppy_factor, o.m_enable_white_caps, )
                wind = (o.m_ocean_wind_mod, o.m_ocean_wind_dir, o.m_ocean_wind_alignment, o.m_ocean_min_wave_length, o.m_damp_factor_against_wind, )
                self.mxs.ext_sea(o.m_name, pack_matrix(o), o.m_motion_blur, pack_object_props(o), geometry, wind, o.m_material, o.m_backface_material, )
                self.hierarchy.append((o.m_name, o.m_parent, o.m_type))
            elif(o.m_type == 'WIREFRAME_CONTAINER'):
                self.mxs.empty(o.m_name, pack_matrix(o), pack_object_props(o), )
                self.hierarchy.append((o.m_name, o.m_parent, o.m_type))
            elif(o.m_type == 'WIREFRAME_BASE'):
                self.mxs.mesh(o.m_name, pack_matrix(o), o.m_num_positions,
                              o.m_vertices, o.m_normals, o.m_triangles, o.m_triangle_normals,
                              o.m_uv_channels, pack_object_props(o), o.m_num_materials,
                              o.m_materials, o.m_triangle_materials, o.m_backface_material, )
                self.hierarchy.append((o.m_name, o.m_parent, o.m_type))
            elif(o.m_type == 'WIREFRAME_INSTANCES'):
                e = self.wireframe_base_name
                c = self.wireframe_container_name
                p = pack_object_props(o)
                wm = bpy.context.scene.maxwell_render.export_wire_wire_material
                for i, m in enumerate(o.m_wire_matrices):
                    n = "{0}-{1}".format(o.m_name, i)
                    self.mxs.instance(n, e, m, p, wm, None, )
                    self.hierarchy.append((n, c, 'MESH_INSTANCE'))
            else:
                raise TypeError("{0} is unknown type".format(o.m_type))
    
    def _finish(self):
        if(system.PLATFORM == 'Darwin'):
            # Mac OS X specific
            log("writing serialized scene data..".format(), 1, LogStyles.MESSAGE, )
            p = self._serialize(self.serialized_data, self.scene_data_name)
            self.scene_data_path = p
            # generate and execute py32 script
            log("running pymaxwell..".format(), 1, LogStyles.MESSAGE, )
            self._pymaxwell()
            # remove all generated files
            log("removing intermediates..".format(), 1, LogStyles.MESSAGE, )
            self._cleanup()
            log("mxs saved in: {0}".format(self.mxs_path), 1, LogStyles.MESSAGE, )
        elif(system.PLATFORM == 'Linux' or system.PLATFORM == 'Windows'):
            log("setting object hierarchy..".format(), 1, LogStyles.MESSAGE, )
            self.mxs.hierarchy(self.hierarchy)
            
            if(self.use_wireframe):
                mx = bpy.context.scene.maxwell_render
                if(mx.export_clay_override_object_material):
                    self.mxs.wireframe_override_object_materials(mx.export_wire_clay_material, self.wireframe_base_name, )
                self.mxs.wireframe_zero_scale_base(self.wireframe_base_name)
            
            log("writing .mxs file..".format(), 1, LogStyles.MESSAGE, )
            if(bpy.context.scene.maxwell_render.export_remove_unused_materials):
                log("removing unused materials..".format(), 1, LogStyles.MESSAGE, )
                self.mxs.erase_unused_materials()
            self.mxs.write()
            log("mxs saved in: {0}".format(self.mxs_path), 1, LogStyles.MESSAGE, )
        
        self._progress(1.0)
    
    def _serialize(self, d, n, ):
        if(not n.endswith(".json")):
            n = "{}.json".format(n)
        p = os.path.join(self.tmp_dir, n)
        with open("{0}.tmp".format(p), 'w', encoding='utf-8', ) as f:
            json.dump(d, f, skipkeys=False, ensure_ascii=False, indent=4, )
        if(os.path.exists(p)):
            os.remove(p)
        shutil.move("{0}.tmp".format(p), p)
        return p
    
    def _pymaxwell(self, append=False, ):
        # generate script
        self.script_path = os.path.join(self.tmp_dir, self.script_name)
        with open(self.script_path, mode='w', encoding='utf-8') as f:
            # read template
            with open(system.check_for_template(), encoding='utf-8') as t:
                code = "".join(t.readlines())
            # write template to a new file
            f.write(code)
        
        system.python34_run_script_helper(self.script_path, self.scene_data_path, self.mxs_path, append, self.use_wireframe, )
    
    def _cleanup(self):
        """Remove all intermediate products."""
        if(self.keep_intermediates):
            return
        
        # remove script, data files and temp directory
        def rm(p):
            if(os.path.exists(p)):
                os.remove(p)
            else:
                log("_cleanup(): {} does not exist?".format(p), 1, LogStyles.WARNING, )
        
        rm(self.script_path)
        rm(self.scene_data_path)
        
        if(hasattr(self, 'mesh_data_paths')):
            for p in self.mesh_data_paths:
                rm(p)
        
        if(hasattr(self, 'wire_base_data')):
            rm(self.wire_base_data)
            for p in self.wire_data_paths:
                rm(p)
        
        if(hasattr(self, 'hair_data_paths')):
            for p in self.hair_data_paths:
                rm(p)
        
        if(hasattr(self, 'part_data_paths')):
            for p in self.part_data_paths:
                rm(p)
        
        if(hasattr(self, 'wire_data_paths')):
            for p in self.wire_data_paths:
                rm(p)
        
        if(os.path.exists(self.tmp_dir)):
            os.rmdir(self.tmp_dir)
        else:
            log("_cleanup(): {} does not exist?".format(self.tmp_dir), 1, LogStyles.WARNING, )


class MXSDatabase():
    """Maxwell object names are not case sensitive, so naming in blender one
    object 'Cube' and other 'cube' is perfectly alright, but in Maxwell it
    causes problems, Maxwell will fix name of second object to 'cube1',
    but then asking for 'cube' object reference will return 'Cube' and not
    'cube', now named 'cube1'..
    
    All objects which defines m_name and m_parent variable should include this:
    self.m_name = MXSDatabase.object_name(self.b_object, self.b_name)
    self.m_parent = MXSDatabase.object_name(self.b_parent, self.b_parent.name)
    Also all extension which use some other object must use the final name.
    """
    
    # TODO: use similar mechanism for materials to skip unused before actual export, this will require to check all materials possible uses, like in extensions.
    
    __objects = []
    __valid_chars = "-_ {}{}".format(string.ascii_letters, string.digits)
    
    __objects_marked_to_export = []
    
    @classmethod
    def set_object_export_list(cls, ls, ):
        cls.__objects_marked_to_export = ls
    
    @classmethod
    def is_in_object_export_list(cls, ob, ):
        for o in cls.__objects_marked_to_export:
            if(ob == o):
                return True
        return False
    
    @classmethod
    def object_name(cls, ob, nm, ):
        orig = nm
        for o, n, onm in cls.__objects:
            if(o == ob and onm == orig):
                return n
        
        nm = cls.__sanitize_name(nm)
        if(cls.__object_name_exists(nm)):
            nm = cls.__check_lowercase_duplicate(nm)
            log("Maxwell is not case sensitive: renamed to '{}'".format(nm), 3, LogStyles.WARNING, )
            
        cls.__objects.append((ob, nm, orig, ))
        
        return nm
    
    @classmethod
    def __object_name_exists(cls, nm, ):
        for _, n, _ in cls.__objects:
            if(n.lower() == nm.lower()):
                return True
        return False
    
    @classmethod
    def __check_lowercase_duplicate(cls, nm, ):
        ok = False
        i = 1
        while(not ok):
            n = "{}-{}".format(nm, i, )
            i += 1
            if(not cls.__object_name_exists(n)):
                ok = True
                nm = n
        return nm
    
    @classmethod
    def __sanitize_name(cls, nm, ):
        nm = ''.join(c if c in cls.__valid_chars else '_' for c in nm)
        return nm
    
    @classmethod
    def only_sanitize_name(cls, nm, ):
        nm = ''.join(c if c in cls.__valid_chars else '_' for c in nm)
        return nm
    
    @classmethod
    def object_original_name(cls, ob, ):
        for o, n, onm in cls.__objects:
            if(o == ob):
                return onm
    
    @classmethod
    def object_original_name_from_export_name(cls, name, ):
        for o, n, onm in cls.__objects:
            if(name == n):
                return onm
    
    @classmethod
    def clear(cls):
        cls.__objects = []
        cls.__objects_marked_to_export = []


class MXSMotionBlurHelper():
    sc = None
    camera = None
    motion_blur = False
    sub = 0
    off = 0.0
    ang = 360
    
    @classmethod
    def init(cls, camera, ):
        cls.sc = bpy.context.scene
        smx = cls.sc.maxwell_render
        
        cls.motion_blur = smx.globals_motion_blur
        if(not cls.motion_blur):
            # no motion blur at all, export only one step
            return
        
        cls.sub = smx.globals_motion_blur_num_substeps
        cls.off = smx.globals_motion_blur_shutter_open_offset
        cls.camera = camera
        try:
            cls.ang = math.degrees(cls.camera.data.maxwell_render.shutter_angle)
        except AttributeError:
            # active camera was not set, i can't get shutter_angle, no motion blur, export only one step
            cls.camera = None
    
    @classmethod
    def default(cls):
        return [(cls.sc.frame_current, 0.0), ]
    
    @classmethod
    def object_steps(cls, obj, ):
        if(not cls.motion_blur):
            return cls.default()
        if(cls.camera is None):
            return cls.default()
        
        mx = obj.maxwell_render
        if(not mx.movement and not mx.deformation):
            return cls.default()
        
        sub = cls.sub
        if(mx.custom_substeps):
            sub = mx.substeps
        
        fl = 1 * (cls.ang / 360)
        sl = fl / sub
        steps = [i * sl for i in range(sub + 1)]
        
        ol = fl * cls.off
        fs = []
        for s in steps:
            fs.append(s - ol)
        
        cf = cls.sc.frame_current
        frames = []
        for n in fs:
            a = 0
            if(n > 1.0):
                a = int(n)
            elif(n < 0.0):
                a = int(n) - 1
            # don't return step 1.0, move frame + 1 instead with step 0.0
            if(n - a == 1.0):
                a += 1
            frames.append((cf + a, n - a))
        
        return frames
    
    @classmethod
    def camera_steps(cls, cam, ):
        if(not cls.motion_blur):
            return cls.default(), [0.0, ]
        if(cls.camera is None):
            return cls.default(), [0.0, ]
        
        mx = cam.maxwell_render
        if(not mx.movement):
            return cls.default(), [0.0, ]
        
        sub = cls.sub
        if(mx.custom_substeps):
            sub = mx.substeps
        
        fl = 1 * (cls.ang / 360)
        sl = fl / sub
        steps = [i * sl for i in range(sub + 1)]
        
        ol = fl * cls.off
        fs = []
        for s in steps:
            fs.append(s - ol)
        
        cf = cls.sc.frame_current
        frames = []
        for n in fs:
            a = 0
            if(n > 1.0):
                a = int(n)
            elif(n < 0.0):
                a = int(n) - 1
            # don't return step 1.0, move frame + 1 instead with step 0.0
            if(n - a == 1.0):
                a += 1
            frames.append((cf + a, n - a))
        
        return frames, fs
    
    @classmethod
    def clear(cls):
        cls.sc = None
        cls.camera = None
        cls.motion_blur = False
        cls.sub = 0
        cls.off = 0.0
        cls.ang = 360


class Serializable():
    def __init__(self):
        self.skip = False
    
    def _fields(self):
        r = list(self.__dict__.keys())
        r = [i for i in r if i.startswith('m_')]
        return r
    
    def _dict(self):
        d = {}
        fs = self._fields()
        for f in fs:
            d[f] = getattr(self, f)
        return d
    
    def _repr(self):
        d = self._dict()
        a = {}
        for k, v in d.items():
            a[k[2:]] = v
        return a


class MXSScene(Serializable):
    def __init__(self, mxs_path, groups, ):
        super().__init__()
        
        mx = bpy.context.scene.maxwell_render
        
        self.m_type = 'SCENE'
        self.m_scene_time = mx.scene_time
        self.m_scene_sampling_level = mx.scene_sampling_level
        self.m_scene_multilight = int(mx.scene_multilight[-1:])
        self.m_scene_multilight_type = int(mx.scene_multilight_type[-1:])
        self.m_scene_cpu_threads = mx.scene_cpu_threads
        self.m_scene_quality = mx.scene_quality
        self.m_output_depth = mx.output_depth
        self.m_output_image_enabled = mx.output_image_enabled
        
        bp = bpy.path.abspath(bpy.context.blend_data.filepath)
        h, t = os.path.split(bp)
        n, e = os.path.splitext(t)
        
        if(mx.output_image != ''):
            self.m_output_image = bpy.path.abspath(mx.output_image)
        else:
            self.m_output_image = os.path.join(h, "{}.png".format(n))
        self.m_output_mxi_enabled = mx.output_mxi_enabled
        if(mx.output_mxi != ''):
            self.m_output_mxi = bpy.path.abspath(mx.output_mxi)
        else:
            self.m_output_mxi = os.path.join(h, "{}.mxi".format(n))
        
        self.m_materials_override = mx.materials_override
        self.m_materials_override_path = bpy.path.abspath(mx.materials_override_path)
        self.m_materials_search_path = bpy.path.abspath(mx.materials_search_path)
        self.m_materials_default_material = bpy.path.abspath(mx.materials_default_material)
        self.m_globals_motion_blur = mx.globals_motion_blur
        self.m_globals_diplacement = mx.globals_diplacement
        self.m_globals_dispersion = mx.globals_dispersion
        self.m_channels_output_mode = int(mx.channels_output_mode[-1:])
        self.m_channels_render = mx.channels_render
        self.m_channels_render_type = int(mx.channels_render_type[-1:])
        self.m_channels_alpha = mx.channels_alpha
        self.m_channels_alpha_file = mx.channels_alpha_file
        self.m_channels_alpha_opaque = mx.channels_alpha_opaque
        self.m_channels_z_buffer = mx.channels_z_buffer
        self.m_channels_z_buffer_file = mx.channels_z_buffer_file
        self.m_channels_z_buffer_near = mx.channels_z_buffer_near
        self.m_channels_z_buffer_far = mx.channels_z_buffer_far
        self.m_channels_shadow = mx.channels_shadow
        self.m_channels_shadow_file = mx.channels_shadow_file
        self.m_channels_material_id = mx.channels_material_id
        self.m_channels_material_id_file = mx.channels_material_id_file
        self.m_channels_object_id = mx.channels_object_id
        self.m_channels_object_id_file = mx.channels_object_id_file
        self.m_channels_motion_vector = mx.channels_motion_vector
        self.m_channels_motion_vector_file = mx.channels_motion_vector_file
        self.m_channels_roughness = mx.channels_roughness
        self.m_channels_roughness_file = mx.channels_roughness_file
        self.m_channels_fresnel = mx.channels_fresnel
        self.m_channels_fresnel_file = mx.channels_fresnel_file
        self.m_channels_normals = mx.channels_normals
        self.m_channels_normals_file = mx.channels_normals_file
        self.m_channels_normals_space = int(mx.channels_normals_space[-1:])
        self.m_channels_position = mx.channels_position
        self.m_channels_position_file = mx.channels_position_file
        self.m_channels_position_space = int(mx.channels_position_space[-1:])
        self.m_channels_deep = mx.channels_deep
        self.m_channels_deep_file = mx.channels_deep_file
        self.m_channels_deep_type = int(mx.channels_deep_type[-1:])
        self.m_channels_deep_min_dist = mx.channels_deep_min_dist
        self.m_channels_deep_max_samples = mx.channels_deep_max_samples
        self.m_channels_uv = mx.channels_uv
        self.m_channels_uv_file = mx.channels_uv_file
        self.m_channels_custom_alpha = mx.channels_custom_alpha
        self.m_channels_custom_alpha_file = mx.channels_custom_alpha_file
        self.m_channels_custom_alpha_groups = groups
        
        self.m_channels_reflectance = mx.channels_reflectance
        self.m_channels_reflectance_file = mx.channels_reflectance_file
        
        self.m_tone_color_space = int(mx.tone_color_space.split('_')[1])
        self.m_tone_whitepoint = mx.tone_whitepoint
        self.m_tone_tint = mx.tone_tint
        self.m_tone_burn = mx.tone_burn
        self.m_tone_gamma = mx.tone_gamma
        self.m_tone_sharpness = mx.tone_sharpness
        self.m_tone_sharpness_value = mx.tone_sharpness_value / 100.0
        self.m_simulens_aperture_map = bpy.path.abspath(mx.simulens_aperture_map)
        self.m_simulens_obstacle_map = bpy.path.abspath(mx.simulens_obstacle_map)
        self.m_simulens_diffraction = mx.simulens_diffraction
        self.m_simulens_diffraction_value = maths.remap(mx.simulens_diffraction_value, 0.0, 2500.0, 0.0, 1.0)
        self.m_simulens_frequency = maths.remap(mx.simulens_frequency, 0.0, 2500.0, 0.0, 1.0)
        self.m_simulens_scattering = mx.simulens_scattering
        self.m_simulens_scattering_value = maths.remap(mx.simulens_scattering_value, 0.0, 2500.0, 0.0, 1.0)
        self.m_simulens_devignetting = mx.simulens_devignetting
        self.m_simulens_devignetting_value = mx.simulens_devignetting_value / 100.0
        self.m_illum_caustics_illumination = int(mx.illum_caustics_illumination[-1:])
        self.m_illum_caustics_refl_caustics = int(mx.illum_caustics_refl_caustics[-1:])
        self.m_illum_caustics_refr_caustics = int(mx.illum_caustics_refr_caustics[-1:])
        
        self.m_overlay_enabled = mx.overlay_enabled
        self.m_overlay_text = mx.overlay_text
        self.m_overlay_position = int(mx.overlay_position[-1:])
        self.m_overlay_color = self._gamma_uncorrect(mx.overlay_color)
        self.m_overlay_background = mx.overlay_background
        self.m_overlay_background_color = self._gamma_uncorrect(mx.overlay_background_color)
        
        self.m_export_protect_mxs = mx.export_protect_mxs
        self.m_export_remove_unused_materials = mx.export_remove_unused_materials
        
        self.m_extra_sampling_enabled = mx.extra_sampling_enabled
        self.m_extra_sampling_sl = mx.extra_sampling_sl
        self.m_extra_sampling_mask = int(mx.extra_sampling_mask[-1:])
        self.m_extra_sampling_custom_alpha = mx.extra_sampling_custom_alpha
        self.m_extra_sampling_user_bitmap = bpy.path.abspath(mx.extra_sampling_user_bitmap)
        self.m_extra_sampling_invert = mx.extra_sampling_invert
        
        # write these too, nothing will be done if just present in data, will be used only when needed..
        self.m_export_use_wireframe = mx.export_use_wireframe
        self.m_export_clay_override_object_material = mx.export_clay_override_object_material
        self.m_export_wire_wire_material = mx.export_wire_wire_material
        self.m_export_wire_clay_material = mx.export_wire_clay_material
        
        self.m_plugin_id = utils.get_plugin_id()
    
    def _gamma_uncorrect(self, c, ):
        g = 1 / 2.2
        c = [v ** g for v in c]
        return c


class MXSEnvironment(Serializable):
    def __init__(self):
        super().__init__()
        # maybe split this to world / sun (/ ibl) classes?
        
        mx = bpy.context.scene.world.maxwell_render
        self.m_type = 'ENVIRONMENT'
        
        self.m_env_type = mx.env_type
        
        self.m_sky_type = mx.sky_type
        self.m_sky_use_preset = mx.sky_use_preset
        self.m_sky_preset = bpy.path.abspath(mx.sky_preset)
        self.m_sky_intensity = mx.sky_intensity
        self.m_sky_planet_refl = mx.sky_planet_refl / 100.0
        self.m_sky_ozone = mx.sky_ozone
        self.m_sky_water = mx.sky_water
        self.m_sky_turbidity_coeff = mx.sky_turbidity_coeff
        self.m_sky_wavelength_exp = mx.sky_wavelength_exp
        self.m_sky_reflectance = mx.sky_reflectance / 100.0
        self.m_sky_asymmetry = mx.sky_asymmetry
        
        self.m_dome_intensity = mx.dome_intensity
        self.m_dome_zenith = self._gamma_uncorrect(mx.dome_zenith)
        self.m_dome_horizon = self._gamma_uncorrect(mx.dome_horizon)
        self.m_dome_mid_point = math.degrees(mx.dome_mid_point)
        
        # self.m_sun_lamp_priority = mx.sun_lamp_priority
        self.m_sun_type = mx.sun_type
        self.m_sun_power = mx.sun_power
        self.m_sun_radius_factor = mx.sun_radius_factor
        self.m_sun_temp = mx.sun_temp
        self.m_sun_color = self._gamma_uncorrect(mx.sun_color)
        self.m_sun_location_type = mx.sun_location_type
        self.m_sun_latlong_lat = mx.sun_latlong_lat
        self.m_sun_latlong_lon = mx.sun_latlong_lon
        self.m_sun_date = mx.sun_date
        self.m_sun_time = mx.sun_time
        self.m_sun_latlong_gmt = mx.sun_latlong_gmt
        self.m_sun_latlong_ground_rotation = mx.sun_latlong_ground_rotation
        self.m_sun_angles_zenith = mx.sun_angles_zenith
        self.m_sun_angles_azimuth = mx.sun_angles_azimuth
        
        v = Vector((mx.sun_dir_x, mx.sun_dir_y, mx.sun_dir_z))
        v = AXIS_CONVERSION * v
        self.m_sun_dir_x = v.x
        self.m_sun_dir_y = v.y
        self.m_sun_dir_z = v.z
        
        if(mx.env_type == 'IMAGE_BASED'):
            if(mx.ibl_bg_type == 'HDR_IMAGE'):
                if(mx.ibl_bg_map == ''):
                    log("IBL environment: Background map file is empty", 3, LogStyles.WARNING, )
                else:
                    if(not os.path.exists(bpy.path.abspath(mx.ibl_bg_map))):
                        log("IBL environment: Background map file '{}' does not exist".format(mx.ibl_bg_map), 3, LogStyles.WARNING, )
            if(mx.ibl_refl_type == 'HDR_IMAGE'):
                if(mx.ibl_refl_map == ''):
                    log("IBL environment: Reflection map file is empty", 3, LogStyles.WARNING, )
                else:
                    if(not os.path.exists(bpy.path.abspath(mx.ibl_refl_map))):
                        log("IBL environment: Reflection map file '{}' does not exist".format(mx.ibl_refl_map), 3, LogStyles.WARNING, )
            if(mx.ibl_refr_type == 'HDR_IMAGE'):
                if(mx.ibl_refr_map == ''):
                    log("IBL environment: Refraction map file is empty", 3, LogStyles.WARNING, )
                else:
                    if(not os.path.exists(bpy.path.abspath(mx.ibl_refr_map))):
                        log("IBL environment: Refraction map file '{}' does not exist".format(mx.ibl_refr_map), 3, LogStyles.WARNING, )
            if(mx.ibl_illum_type == 'HDR_IMAGE'):
                if(mx.ibl_illum_map == ''):
                    log("IBL environment: Illumination map file is empty", 3, LogStyles.WARNING, )
                else:
                    if(not os.path.exists(bpy.path.abspath(mx.ibl_illum_map))):
                        log("IBL environment: Illumination map file '{}' does not exist".format(mx.ibl_illum_map), 3, LogStyles.WARNING, )
        
        self.m_ibl_intensity = mx.ibl_intensity
        self.m_ibl_interpolation = mx.ibl_interpolation
        self.m_ibl_screen_mapping = mx.ibl_screen_mapping
        self.m_ibl_bg_type = mx.ibl_bg_type
        self.m_ibl_bg_map = bpy.path.abspath(mx.ibl_bg_map)
        self.m_ibl_bg_intensity = mx.ibl_bg_intensity
        self.m_ibl_bg_scale_x = mx.ibl_bg_scale_x
        self.m_ibl_bg_scale_y = mx.ibl_bg_scale_y
        self.m_ibl_bg_offset_x = mx.ibl_bg_offset_x
        self.m_ibl_bg_offset_y = mx.ibl_bg_offset_y
        self.m_ibl_refl_type = mx.ibl_refl_type
        self.m_ibl_refl_map = bpy.path.abspath(mx.ibl_refl_map)
        self.m_ibl_refl_intensity = mx.ibl_refl_intensity
        self.m_ibl_refl_scale_x = mx.ibl_refl_scale_x
        self.m_ibl_refl_scale_y = mx.ibl_refl_scale_y
        self.m_ibl_refl_offset_x = mx.ibl_refl_offset_x
        self.m_ibl_refl_offset_y = mx.ibl_refl_offset_y
        self.m_ibl_refr_type = mx.ibl_refr_type
        self.m_ibl_refr_map = bpy.path.abspath(mx.ibl_refr_map)
        self.m_ibl_refr_intensity = mx.ibl_refr_intensity
        self.m_ibl_refr_scale_x = mx.ibl_refr_scale_x
        self.m_ibl_refr_scale_y = mx.ibl_refr_scale_y
        self.m_ibl_refr_offset_x = mx.ibl_refr_offset_x
        self.m_ibl_refr_offset_y = mx.ibl_refr_offset_y
        self.m_ibl_illum_type = mx.ibl_illum_type
        self.m_ibl_illum_map = bpy.path.abspath(mx.ibl_illum_map)
        self.m_ibl_illum_intensity = mx.ibl_illum_intensity
        self.m_ibl_illum_scale_x = mx.ibl_illum_scale_x
        self.m_ibl_illum_scale_y = mx.ibl_illum_scale_y
        self.m_ibl_illum_offset_x = mx.ibl_illum_offset_x
        self.m_ibl_illum_offset_y = mx.ibl_illum_offset_y
        
        if(mx.use_sun_lamp and mx.sun_location_type == 'DIRECTION'):
            # use selected sun lamp
            if(mx.sun_lamp != ''):
                sun_lamp = None
                try:
                    sun_lamp = bpy.data.lamps[mx.sun_lamp]
                except KeyError:
                    log("specified Sun lamp cannot be found, using location vector..", 2, LogStyles.WARNING)
                if(sun_lamp is not None):
                    sun_obj = None
                    for o in bpy.data.objects:
                        if(o.type == 'LAMP'):
                            if(o.data == sun_lamp):
                                sun_obj = o
                                break
                    if(sun_obj is not None):
                        # direction from matrix
                        mw = sun_obj.matrix_world
                        loc, rot, sca = mw.decompose()
                        v = Vector((0.0, 0.0, 1.0))
                        v.rotate(rot)
                        v = AXIS_CONVERSION * v
                        # mx.sun_dir_x = v.x
                        # mx.sun_dir_y = v.y
                        # mx.sun_dir_z = v.z
                        self.m_sun_location_type = 'DIRECTION'
                        self.m_sun_dir_x = v.x
                        self.m_sun_dir_y = v.y
                        self.m_sun_dir_z = v.z
                        log("using Sun lamp object: '{}'".format(sun_obj.name), 2)
                    else:
                        log("Sun lamp object cannot be found, using location vector..", 2, LogStyles.WARNING)
            else:
                log("no Sun specified, using location vector..", 2, LogStyles.WARNING)
        else:
            # use_sun_lamp is false, use already processed environment options
            pass
        
        '''
        if(mx.sun_lamp_priority):
            # extract suns from objects
            objs = bpy.context.scene.objects
            suns = []
            for o in objs:
                if(o.type == 'LAMP'):
                    if(o.data.type == 'SUN'):
                        suns.append(o)
            
            # use just one sun. decide which one here..
            def get_sun(suns):
                if(len(suns) == 0):
                    return None
                if(len(suns) == 1):
                    return suns[0]
                else:
                    log("more than one sun in scene!", 2, LogStyles.WARNING)
                    nm = []
                    for o in suns:
                        nm.append(o.name)
                    snm = sorted(nm)
                    n = snm[0]
                    for o in suns:
                        if(o.name == n):
                            log("using '{}' as sun..".format(n), 2, LogStyles.WARNING)
                            return o
            
            sun = get_sun(suns)
            if(sun is None):
                log("'Sun Lamp Priority' is True, but there is no Sun object in scene. using World settings..", 1, LogStyles.WARNING)
                self.m_sun_lamp_priority = False
            else:
                # direction from matrix
                mw = sun.matrix_world
                loc, rot, sca = mw.decompose()
                v = Vector((0.0, 0.0, 1.0))
                v.rotate(rot)
                v = AXIS_CONVERSION * v
                mx.sun_dir_x = v.x
                mx.sun_dir_y = v.y
                mx.sun_dir_z = v.z
                
                self.m_sun_location_type = 'DIRECTION'
                self.m_sun_dir_x = v.x
                self.m_sun_dir_y = v.y
                self.m_sun_dir_z = v.z
        else:
            # sun_lamp_priority is false, use already processed environment options
            pass
        '''
        
        # and change this, just in case..
        import datetime
        n = datetime.datetime.now()
        if(self.m_sun_date == "DD.MM.YYYY"):
            if(mx is not None):
                mx.sun_date = n.strftime('%d.%m.%Y')
                self.m_sun_date = mx.sun_date
            else:
                self.m_sun_date = n.strftime('%d.%m.%Y')
        if(self.m_sun_time == "HH:MM"):
            if(mx is not None):
                mx.sun_time = n.strftime('%H:%M')
                self.m_sun_time = mx.sun_time
            else:
                self.m_sun_time = n.strftime('%H:%M')
    
    def _gamma_uncorrect(self, c, ):
        g = 1 / 2.2
        c = [v ** g for v in c]
        return c


class MXSCamera(Serializable):
    def __init__(self, o, ):
        log("'{}'".format(o['object'].name), 2)
        
        super().__init__()
        
        ob = o['object']
        self.b_object = ob
        self.b_matrix_world = ob.matrix_world.copy()
        cd = ob.data
        rp = bpy.context.scene.render
        mx = ob.data.maxwell_render
        
        # object
        self.m_name = MXSDatabase.object_name(ob, ob.name)
        self.m_type = 'CAMERA'
        self.m_parent = None
        self.m_active = (bpy.context.scene.camera == ob)
        self.m_hide = mx.hide
        
        # optics
        self.m_lens = int(mx.lens[-1:])
        self.m_shutter = 1 / mx.shutter
        self.m_fov = mx.fov
        self.m_azimuth = mx.azimuth
        self.m_angle = mx.angle
        
        # sensor
        self.m_iso = mx.iso
        self.m_response = mx.response
        self.m_resolution_x = int(rp.resolution_x * rp.resolution_percentage / 100.0)
        self.m_resolution_y = int(rp.resolution_y * rp.resolution_percentage / 100.0)
        self.m_pixel_aspect = rp.pixel_aspect_x / rp.pixel_aspect_y
        self.m_screen_region = mx.screen_region
        self.m_screen_region_xywh = ()
        if(self.m_screen_region != 'NONE'):
            x = int(self.m_resolution_x * rp.border_min_x)
            h = self.m_resolution_y - int(self.m_resolution_y * rp.border_min_y)
            w = int(self.m_resolution_x * rp.border_max_x)
            y = self.m_resolution_y - int(self.m_resolution_y * rp.border_max_y)
            self.m_screen_region_xywh = (x, y, w, h)
        
        # options
        self.m_aperture = mx.aperture
        self.m_diaphragm_blades = mx.diaphragm_blades
        self.m_diaphragm_angle = mx.diaphragm_angle
        self.m_custom_bokeh = mx.custom_bokeh
        self.m_bokeh_ratio = mx.bokeh_ratio
        self.m_bokeh_angle = mx.bokeh_angle
        self.m_shutter_angle = mx.shutter_angle
        self.m_frame_rate = mx.frame_rate
        self.m_set_cut_planes = (cd.clip_start, cd.clip_end, int(mx.zclip))
        self.m_set_shift_lens = (cd.shift_x * 10.0, cd.shift_y * 10.0)
        
        def _texture_to_data(name):
            if(name == ''):
                return None
            t = MXSTexture(name)
            a = t._repr()
            return a
        
        # stereo extensions
        self.m_lls_type = int(mx.lls_type[-1:])
        self.m_lls_fovv = math.degrees(mx.lls_fovv)
        self.m_lls_fovh = math.degrees(mx.lls_fovh)
        self.m_lls_flip_ray_x = mx.lls_flip_ray_x
        self.m_lls_flip_ray_y = mx.lls_flip_ray_y
        self.m_lls_parallax_distance = math.degrees(mx.lls_parallax_distance)
        self.m_lls_zenith_mode = mx.lls_zenith_mode
        self.m_lls_separation = mx.lls_separation
        self.m_lls_separation_map = _texture_to_data(mx.lls_separation_map)
        self.m_fs_type = int(mx.fs_type[-1:])
        self.m_fs_fov = math.degrees(mx.fs_fov)
        self.m_fs_separation = mx.fs_separation
        self.m_fs_separation_map = _texture_to_data(mx.fs_separation_map)
        self.m_fs_vertical_mode = int(mx.fs_vertical_mode[-1:])
        self.m_fs_dome_radius = mx.fs_dome_radius
        self.m_fs_head_turn_map = _texture_to_data(mx.fs_head_turn_map)
        self.m_fs_dome_tilt_compensation = int(mx.fs_dome_tilt_compensation[-1:])
        self.m_fs_dome_tilt = mx.fs_dome_tilt
        self.m_fs_head_tilt_map = _texture_to_data(mx.fs_head_tilt_map)
        
        # film width / height: width / height ratio a ==  x_res / y_res ratio
        # x_res / y_res is more important than sensor size, depending on sensor fit the other one is calculated
        sf = cd.sensor_fit
        film_height = cd.sensor_height / 1000.0
        film_width = cd.sensor_width / 1000.0
        if(sf == 'AUTO'):
            if(self.m_resolution_x > self.m_resolution_y):
                # horizontal
                film_width = cd.sensor_width / 1000.0
                sf = 'HORIZONTAL'
            else:
                # vertical
                film_height = cd.sensor_width / 1000.0
                sf = 'VERTICAL'
        if(sf == 'VERTICAL'):
            film_width = (film_height * self.m_resolution_x) / self.m_resolution_y
        else:
            film_height = (film_width * self.m_resolution_y) / self.m_resolution_x
        
        self.m_film_width = film_width
        self.m_film_height = film_height
        
        self.m_steps = []
        
        if(not mx.movement):
            self.set_step()
        else:
            sc = bpy.context.scene
            cf = sc.frame_current
            sf = sc.frame_subframe
            
            steps, times = MXSMotionBlurHelper.camera_steps(ob)
            if(len(steps) == 1):
                if(steps[0][0] == cf and steps[0][1] == sf):
                    self.set_step(step_number=0, step_time=0.0, )
                else:
                    raise Exception("What's that? Something, somewhere is missing..")
            else:
                for i, (frame, sub) in enumerate(steps):
                    # move timeline
                    sc.frame_set(frame, subframe=sub, )
                    self.set_step(step_number=i, step_time=times[i], )
                    
                    log("movement: frame: {}, step: {}".format(frame, round(sub, 6)), 3, )
                # move timeline back where i started..
                sc.frame_set(cf, subframe=sf, )
    
    def set_step(self, step_number=0, step_time=0.0, ):
        ob = self.b_object
        cd = ob.data
        rp = bpy.context.scene.render
        mx = ob.data.maxwell_render
        
        mw_loc, mw_rot, _ = ob.matrix_world.decompose()
        mw_location = Matrix.Translation(mw_loc).to_4x4()
        mw_rotation = mw_rot.to_matrix().to_4x4()
        mw_scale = Matrix.Identity(4)
        mw = mw_location * mw_rotation * mw_scale
        origin = mw.to_translation()
        if(ob.data.dof_object):
            dof_distance = (origin - ob.data.dof_object.matrix_world.to_translation()).length
        else:
            dof_distance = ob.data.dof_distance
            if(dof_distance == 0.0):
                dof_distance = 1.0
        if(mx.lens == 'TYPE_ORTHO_2'):
            dof_distance = cd.ortho_scale
        
        focal_point = mw * Vector((0.0, 0.0, -dof_distance))
        up = mw * Vector((0.0, 1.0, 0.0)) - origin
        
        origin = Vector(AXIS_CONVERSION * origin).to_tuple()
        focal_point = Vector(AXIS_CONVERSION * focal_point).to_tuple()
        up = Vector(AXIS_CONVERSION * up).to_tuple()
        
        # step, Cvector origin, Cvector focalPoint, Cvector, up, focalLenght, fStop, stepTime, focalLengthNeedCorrection = 1
        self.m_steps.append((step_number, origin, focal_point, up, cd.lens / 1000.0, mx.fstop, step_time, 1, ))
        self.m_number_of_steps = len(self.m_steps)


class MXSObject(Serializable):
    def __init__(self, o, do_not_set_anything_yet=False, ):
        super().__init__()
        
        self.m_type = '__OBJECT__'
        self.o = o
        
        if(do_not_set_anything_yet):
            return
        
        # regular objects: EMPTY, MESH, MESH_INSTANCE, REFERENCE
        self.b_object = self.o['object']
        self.b_name = self.b_object.name
        self.b_matrix_world = self.b_object.matrix_world.copy()
        self.b_parent = None
        self.b_parent_matrix_world = None
        self.b_parent_type = None
        
        self.m_name = MXSDatabase.object_name(self.b_object, self.b_name)
        self.m_parent = None
        
        if(self.b_object.parent):
            self.b_parent = self.b_object.parent
            self.b_parent_matrix_world = self.b_parent.matrix_world.copy()
            self.b_parent_type = self.b_object.parent_type
            
            self.m_parent = MXSDatabase.object_name(self.b_parent, self.b_parent.name)
        
        self.mx = self.b_object.maxwell_render
        
        self._object_properties()
        self._transformation()
    
    def _object_properties(self):
        mx = self.mx
        self.m_hide = mx.hide
        self.m_opacity = mx.opacity
        self.m_hidden_camera = mx.hidden_camera
        self.m_hidden_camera_in_shadow_channel = mx.hidden_camera_in_shadow_channel
        self.m_hidden_global_illumination = mx.hidden_global_illumination
        self.m_hidden_reflections_refractions = mx.hidden_reflections_refractions
        self.m_hidden_zclip_planes = mx.hidden_zclip_planes
        self.m_object_id = self._gamma_uncorrect(mx.object_id)
        
        self.m_blocked_emitters = []
        for be in mx.blocked_emitters.emitters:
            n = be.name
            o = bpy.data.objects[n]
            if(not MXSDatabase.is_in_object_export_list(o)):
                log("blocked emitter '{}', but this emitter will not be exported. skipping..".format(be.name), 3, LogStyles.WARNING, )
            else:
                self.m_blocked_emitters.append(MXSDatabase.object_name(o, n, ))
    
    def _matrix_to_base_and_pivot(self, m, ):
        """Convert Matrix to Base and Pivot and Position, Rotation and Scale for Studio"""
        cm = Matrix(((1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, -1.0, 0.0))).to_4x4()
        mm = m.copy()
        
        l, r, s = mm.decompose()
        # location
        ml = cm * l
        # rotate
        e = r.to_euler()
        e.rotate(cm)
        mr = e.to_matrix()
        # scale
        ms = Matrix(((s.x, 0.0, 0.0), (0.0, s.y, 0.0), (0.0, 0.0, s.z)))
        # combine rotation + scale
        rs = mr * ms
        rs.transpose()
        # convert data
        bx = rs.row[0].to_tuple()
        by = rs.row[1].to_tuple()
        bz = rs.row[2].to_tuple()
        b = (ml.to_tuple(), ) + (bx, by, bz)
        p = ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), )
        
        l = ml.to_tuple()
        r = (math.degrees(e[0]), math.degrees(e[1]), math.degrees(e[2]), )
        s = s.to_tuple()
        
        return (b, p, l, r, s, )
    
    def _transformation(self):
        m = self.b_matrix_world.copy()
        if(self.b_parent):
            m = self.b_parent_matrix_world.copy().inverted() * m
        m *= ROTATE_X_90
        b, p, l, r, s = self._matrix_to_base_and_pivot(m)
        
        self.mx_matrix_world = m.copy()
        
        self.m_base = b
        self.m_pivot = p
        self.m_location = l
        self.m_rotation = r
        self.m_scale = s
        
        sc = bpy.context.scene
        cf = sc.frame_current
        sf = sc.frame_subframe
        
        self.m_motion_blur = []
        steps = MXSMotionBlurHelper.object_steps(self.b_object)
        if(self.mx.movement):
            if(len(steps) == 1):
                if(steps[0][0] == cf and steps[0][1] == sf):
                    # [(substep_time, position, base, pivot), ]
                    self.m_motion_blur = [(0.0, 0, self.m_base, self.m_pivot), ]
                else:
                    raise Exception("What's that? Something, somewhere is missing..")
            else:
                position = 0
            
                for i, (frame, sub) in enumerate(steps):
                    # move timeline
                    sc.frame_set(frame, subframe=sub, )
                    # base / pivot
                    m = self.b_object.matrix_world.copy()
                    if(self.b_parent):
                        m = self.b_parent.matrix_world.copy().inverted() * m
                    m *= ROTATE_X_90
                    b, p, l, r, s = self._matrix_to_base_and_pivot(m)
                    self.m_motion_blur.append((sub, position, b, p))
                
                    log("movement: frame: {}, step: {}".format(frame, round(sub, 6)), 3, )
            
                sc.frame_set(cf, subframe=sf, )
        else:
            self.m_motion_blur = []
    
    def _materials(self):
        self.m_num_materials = len(self.b_object.material_slots)
        self.m_materials = []
        for i, s in enumerate(self.b_object.material_slots):
            if(s.material is not None):
                self.m_materials.append(s.material.name)
            else:
                log("slot '{}' has no material assigned, material placeholder will be used..".format(i), 3, LogStyles.WARNING, )
        
        self.m_backface_material = self.b_object.maxwell_render.backface_material
    
    def _gamma_uncorrect(self, c, ):
        g = 1 / 2.2
        c = [v ** g for v in c]
        return c


class MXSEmpty(MXSObject):
    def __init__(self, o, ):
        swap_name = None
        if('extra_options' in o):
            if('swap_name' in o['extra_options']):
                swap_name = o['extra_options']['swap_name']
        
        if(swap_name is not None):
            log("'{}'".format(swap_name), 2)
        else:
            log("'{}'".format(o['object'].name), 2)
        
        super().__init__(o)
        self.m_type = 'EMPTY'
        
        if(swap_name is not None):
            self.m_name = MXSDatabase.only_sanitize_name(swap_name)


class MXSMesh(MXSObject):
    def __init__(self, o, ):
        log("'{}'".format(o['object'].name), 2)
        
        super().__init__(o)
        self.m_type = 'MESH'
        
        # dupli overrides when self.use_instances = False
        self.dupli = False
        if('dupli_matrix' in self.o):
            self.dupli = True
        
        if(self.dupli):
            # dupli overrides when self.use_instances = False
            
            self.m_name = MXSDatabase.object_name(self.b_object, self.o['dupli_name'])
            
            mw = self.o['dupli_matrix'].copy()
            m = self.o['parent']['object'].matrix_world.inverted() * mw
            m *= ROTATE_X_90
            b, p, l, r, s = self._matrix_to_base_and_pivot(m)
            
            self.m_base = b
            self.m_pivot = p
            self.m_location = l
            self.m_rotation = r
            self.m_scale = s
        
        # handle hidden base objects for particle duplicators
        swap_parent = None
        if('extra_options' in o):
            if('swap_parent' in o['extra_options']):
                swap_parent = o['extra_options']['swap_parent']
        if(swap_parent is not None):
            self.m_parent = MXSDatabase.object_name(swap_parent['object'], swap_parent['object'].name)
        swap_matrix = None
        if('extra_options' in o and swap_parent is not None):
            if('swap_matrix' in o['extra_options']):
                swap_matrix = o['extra_options']['swap_matrix']
        if(swap_matrix is not None):
            m = swap_parent['object'].matrix_world.inverted() * swap_matrix
            m *= ROTATE_X_90
            b, p, l, r, s = self._matrix_to_base_and_pivot(m)
            self.m_base = b
            self.m_pivot = p
            self.m_location = l
            self.m_rotation = r
            self.m_scale = s
        # this can be property of swapped instance
        if('extra_options' in self.o):
            if('hide' in self.o['extra_options']):
                # if(self.o['extra_options']['hide'] is True):
                #     self.m_hide = True
                self.m_hide = self.o['extra_options']['hide']
        
        self.m_num_positions = 0
        self.m_vertices = []
        self.m_normals = []
        self.m_triangles = None
        self.m_triangle_normals = []
        self.m_uv_channels = None
        self.m_triangle_materials = None
        
        # deformation blur
        sc = bpy.context.scene
        cf = sc.frame_current
        sf = sc.frame_subframe
        steps = MXSMotionBlurHelper.object_steps(self.b_object)
        
        if(self.mx.deformation):
            if(len(steps) == 1):
                if(steps[0][0] == cf and steps[0][1] == sf):
                    me = self._prepare_mesh()
                    # about 5x faster. tested on 3.8m tris mesh with one uv map, 2.196191s (_mesh_to_data2) x 11.303212s (_mesh_to_data)
                    # self._mesh_to_data(me)
                    self._mesh_to_data2(me)
                    
                    self._materials()
                    # cleanup
                    bpy.data.meshes.remove(me)
                else:
                    raise Exception("What's that? Something, somewhere is missing..")
            else:
                for position, (frame, sub) in enumerate(steps):
                    # move timeline
                    sc.frame_set(frame, subframe=sub, )
                    # mesh
                    me = self._prepare_mesh(pos=position, )
                    
                    # self._mesh_to_data(me)
                    self._mesh_to_data2(me)
                    
                    log("deformation: frame: {}, step: {}, position: {}".format(frame, round(sub, 6), position), 3, )
                    
                    self._materials()
                    
                    bpy.data.meshes.remove(me)
                
                sc.frame_set(cf, subframe=sf, )
        else:
            me = self._prepare_mesh()
            # self._mesh_to_data(me)
            self._mesh_to_data2(me)
            
            self._materials()
            # cleanup
            bpy.data.meshes.remove(me)
    
    def _prepare_mesh(self, pos=0, ):
        ob = self.b_object
        mx = ob.maxwell_render
        o = self.o
        
        self.mesh_name = ob.data.name
        
        extra_subdiv = False
        
        if(o['converted'] is True and pos == 0):
            # get to-mesh-conversion result (curves, texts, etc..)
            me = o['mesh']
        else:
            use_subdivision = bpy.context.scene.maxwell_render.export_use_subdivision
            if(use_subdivision):
                if(len(ob.modifiers) > 0):
                    last_modifier = ob.modifiers[-1]
                    if(last_modifier.type == 'SUBSURF' and last_modifier.show_render and last_modifier.subdivision_type == 'CATMULL_CLARK'):
                        extra_subdiv = True
                        # if using auto subdivision modifiers in Maxwell, disable last modifier if conditions are met
                        last_modifier.show_render = False
                    else:
                        if(last_modifier.type == 'SUBSURF'):
                            log("'{}': (auto subdivision modifiers) last subdivision modifier can't be used".format(ob.name), 3, LogStyles.WARNING, )
            
            # or make new flattened mesh (regular meshes, with modifiers applied)
            me = ob.to_mesh(bpy.context.scene, True, 'RENDER', )
            
            if(extra_subdiv):
                # and enable it again
                last_modifier.show_render = True
        
        # transform
        me.transform(ROTATE_X_MINUS_90)
        
        # here, in triangulating, i experienced crash from not so well mesh, validating before prevents it..
        me.validate()
        
        bm = bmesh.new()
        bm.from_mesh(me)
        # store quads if needed
        subd = ob.maxwell_render.subdivision
        # do this only when subdivision is enabled and set to catmull-clark scheme
        if((subd.enabled and subd.scheme == '0') or extra_subdiv):
            # make list if vertex indices lists, only for quads, for other polygons put empty list
            fvixs = [[v.index for v in f.verts] if len(f.verts) == 4 else [] for f in bm.faces]
        
        # triangulate now in bmesh
        only_tris = True
        for f in bm.faces:
            # determine if triangulating is needed first.
            # look through polygons if they have more than 3 vertices and if, break and triangulate
            # shouldn't be as cpu expensive as triangulating everything even if not needed..
            if(len(f.verts) > 3):
                only_tris = False
                break
        
        if(not only_tris):
            # onf = len(bm.faces)
            # bmesh.ops.triangulate(bm, faces=bm.faces)
            # bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method=0, ngon_method=0)
            
            # bm.faces.ensure_lookup_table()
            # self.existing_triangles = [f.index for f in bm.faces if len(f.verts) == 3]
            
            rv = bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method=0, ngon_method=0)
            # print(rv)
            
            # FIXME: disabled Subdivision until fixed
            
            # import pprint
            # pp = pprint.PrettyPrinter(indent=4)
            # pp.pprint(rv)
            
            # TODO: determining quads would be much easier with edges returned from triangulate
            # for e in rv['edges']:
            #     print(e.link_faces[:])
            
            # triangulated_faces = []
            # for e in rv['edges']:
            #     triangulated_faces.append(e.link_faces[:])
            # print(triangulated_faces)
            
            # for f in former_quads:
            #     print(f[0].index, f[1].index)
            
            # # new triangles have indexes after number original faces, so i can identify new triangles and spin indexes
            # for f in bm.faces:
            #     print(f.index, [v.index for v in f.verts])
            
            # bm.faces.ensure_lookup_table()
            # self.created_faces_indexes = []
            # for i in range(onf, len(bm.faces), 1):
            #     self.created_faces_indexes.append(bm.faces[i].index)
            # # print(self.created_faces_indexes)
        
        # quads again: list of lists of triangle indices which were quads before
        quad_pairs = None
        # do this only when subdivision is enabled and set to catmull-clark scheme
        if((subd.enabled and subd.scheme == '0') or extra_subdiv):
            quadix = []
            for f in bm.faces:
                vixs = [v.index for v in f.verts]
                for qi, q in enumerate(fvixs):
                    c = 0
                    for i in q:
                        if(i in vixs):
                            c += 1
                        if(c == 3):
                            # has 3 verts from ex-quad, is one of the pair
                            quadix.append([qi, f.index])
                            break
            # make pairs
            quadd = {}
            for qi, fi in quadix:
                if(str(qi) not in quadd):
                    quadd[str(qi)] = [fi, ]
                else:
                    quadd[str(qi)].append(fi)
            # quad pairs dict to list
            quad_pairs = []
            for k, v in quadd.items():
                if(len(v) > 2):
                    log("{}: triangulation result is non-manifold, Catmull-Clark subdivision will not work".format(ob.name), 3, LogStyles.WARNING, )
                    v = v[:2]
                quad_pairs.append(v)
        
        self.quad_pairs = quad_pairs
        
        bm.to_mesh(me)
        bm.free()
        
        me.calc_tessface()
        me.calc_normals()
        if(me.use_auto_smooth):
            me.calc_normals_split()
        
        self.subdivision_modifier = None
        if(extra_subdiv):
            sd = self.b_object.maxwell_render.subdivision
            # store old settings
            old = (sd.enabled, sd.level, sd.scheme, sd.interpolation, sd.crease, sd.smooth, )
            # set modifier settings
            sd.enabled = True
            sd.level = last_modifier.render_levels
            sd.scheme = '0'
            if(last_modifier.use_subsurf_uv):
                sd.interpolation = '2'
            else:
                sd.interpolation = '0'
            sd.crease = 0.0
            sd.smooth = math.radians(90.000)
            d = {'type': None,
                 'object': self.b_object,
                 'parent': self.b_parent,
                 'export': True,
                 'children': [],
                 'export_type': 'SUBDIVISION', }
            o = MXSSubdivision(d, self.quad_pairs, )
            self.subdivision_modifier = o
            # restore old settings
            sd.enabled = old[0]
            sd.level = old[1]
            sd.scheme = old[2]
            sd.interpolation = old[3]
            sd.crease = old[4]
            sd.smooth = old[5]
        
        return me
    
    def _mesh_to_data(self, me, ):
        # vertices
        vertices = [v.co.to_tuple() for v in me.vertices]
        # vertex normals
        normals = [v.normal.to_tuple() for v in me.vertices]
        # triangles and triangle normals
        triangles = []
        triangle_normals = []
        ni = len(me.vertices) - 1
        tns = []
        for fi, f in enumerate(me.tessfaces):
            ni = ni + 1
            tns.append(f.normal.to_tuple())
            fv = f.vertices
            # smoothing
            if(f.use_smooth):
                # vertex normals
                nix = (fv[0], fv[1], fv[2], )
            else:
                # face normal
                nix = (ni, ni, ni, )
            t = tuple(fv) + nix
            triangles.append(t)
        
        triangle_normals = tns
        # uv channels
        uv_channels = []
        for tix, uvtex in enumerate(me.tessface_uv_textures):
            uv = []
            for fi, f in enumerate(me.tessfaces):
                duv = uvtex.data[fi].uv
                uv.append((duv[0][0], 1.0 - duv[0][1], 0.0, duv[1][0], 1.0 - duv[1][1], 0.0, duv[2][0], 1.0 - duv[2][1], 0.0, ))
            uv_channels.append(uv)
        # triangle materials
        triangle_materials = []
        for fi, f in enumerate(me.tessfaces):
            triangle_materials.append((fi, f.material_index, ))
        
        self.m_num_positions += 1
        self.m_vertices.append(vertices)
        self.m_normals.append(normals)
        self.m_triangles = triangles
        self.m_triangle_normals.append(triangle_normals)
        self.m_uv_channels = uv_channels
        self.m_triangle_materials = triangle_materials
    
    def _mesh_to_data2(self, me, ):
        import numpy as np
        
        def verts(me):
            l = len(me.vertices)
            vs = np.zeros((l * 3), dtype=np.float, )
            ns = np.zeros((l * 3), dtype=np.float, )
            me.vertices.foreach_get('co', vs)
            me.vertices.foreach_get('normal', ns)
            return (np.reshape(vs, (l, 3), ),
                    np.reshape(ns, (l, 3), ), )
        
        def triangles(me):
            l = len(me.polygons)
            ts = np.zeros((l * 3), dtype=np.int, )
            ns = np.zeros((l * 3), dtype=np.float, )
            ms = np.zeros(l, dtype=np.int, )
            fs = np.zeros(l, dtype=np.int, )
            me.polygons.foreach_get('vertices', ts)
            me.polygons.foreach_get('normal', ns)
            me.polygons.foreach_get('material_index', ms)
            me.polygons.foreach_get('use_smooth', fs)
            
            vl = len(me.vertices)
            ni = np.arange(vl, vl + l, dtype=np.int, )
            ni = np.reshape(ni, (-1, 1))
            ni = np.concatenate((ni, ni, ni), axis=1)
            
            # smooth faces > use vertex normals
            ts = np.reshape(ts, (l, 3))
            for i, b in enumerate(fs):
                if(b):
                    # same indices as vertex locations, so just copy that
                    ni[i] = ts[i]
            
            ts = np.concatenate((ts, ni), axis=1)
            
            ti = np.zeros(l, dtype=np.int, )
            me.polygons.foreach_get('index', ti)
            ti = np.reshape(ti, (-1, 1))
            ms = np.reshape(ms, (-1, 1))
            ms = np.concatenate((ti, ms), axis=1)
            
            # FIXME: disabled Subdivision until fixed
            '''
            # warning: ugly hacking starts here.. from 2.76b to 2.77a there was a slight change in vertex order in faces after triangulating
            # the result of this is, subdivision modifier stopped to work. even though the mesh is exactly the same, subdivision throws error
            
            # swap columns
            ps = self.b_object.data.polygons
            n = len(ps)
            n0 = n
            # print(n)
            nt = n - sum([1 for f in ps if len(f.vertices) == 3])
            # print(nt)
            n = nt
            # print(n)
            # print(self.existing_triangles)
            # print(ts)
            backup = np.copy(ts)
            a = np.copy(ts[:n, 0])
            b = np.copy(ts[:n, 1])
            c = np.copy(ts[:n, 2])
            ts[:n, 0] = c
            ts[:n, 1] = a
            ts[:n, 2] = b
            
            # print(ts)
            # for i in self.existing_triangles:
            #     ts[i] = backup[i]
            # print(ts)
            
            a = np.copy(ts[:n0 - (n0 - n)])
            b = np.copy(ts[n0:])
            c = np.copy(ts[n0 - (n0 - n):n0])
            # print(a)
            # print(b)
            # print(c)
            
            ts = np.concatenate((b, c, a, ), axis=0, )
            # print(ts)
            
            # # default quad cube
            # a = ([3, 2, 0],
            #      [7, 6, 2],
            #      [5, 4, 6],
            #      [1, 0, 4],
            #      [2, 6, 4],
            #      [7, 3, 1],
            #      [1, 3, 0],
            #      [3, 7, 2],
            #      [7, 5, 6],
            #      [5, 1, 4],
            #      [0, 2, 4],
            #      [5, 7, 1], )
            # for b in a:
            #     print(b)
            
            # # 2.76b cube with top quad trianglated
            # [[ 3  2  0  8  8  8]
            #  [ 7  6  2  9  9  9]
            #  [ 5  4  6 10 10 10]
            #  [ 1  0  4 11 11 11]
            #  [ 2  6  4 12 12 12]
            #  [ 7  1  5 13 13 13] * 5
            #  [ 7  3  1 14 14 14] * 6
            #  [ 1  3  0 15 15 15]
            #  [ 3  7  2 16 16 16]
            #  [ 7  5  6 17 17 17]
            #  [ 5  1  4 18 18 18]
            #  [ 0  2  4 19 19 19]]
            
            # warning: ugly hacking ends here..
            '''
            
            return (ts, np.reshape(ns, (l, 3)), ms, )
        
        def triangles1(me):
            l = len(me.polygons)
            ts = np.zeros((l * 3), dtype=np.int, )
            ns = np.zeros((l * 3), dtype=np.float, )
            ms = np.zeros(l, dtype=np.int, )
            fs = np.zeros(l, dtype=np.int, )
            me.polygons.foreach_get('vertices', ts)
            me.polygons.foreach_get('normal', ns)
            me.polygons.foreach_get('material_index', ms)
            me.polygons.foreach_get('use_smooth', fs)
            
            vl = len(me.vertices)
            ni = np.arange(vl, vl + l, dtype=np.int, )
            ni = np.reshape(ni, (-1, 1))
            ni = np.concatenate((ni, ni, ni), axis=1)
            
            # smooth faces > use vertex normals
            ts = np.reshape(ts, (l, 3))
            for i, b in enumerate(fs):
                if(b):
                    # same indices as vertex locations, so just copy that
                    ni[i] = ts[i]
            
            ts = np.concatenate((ts, ni), axis=1)
            
            ti = np.zeros(l, dtype=np.int, )
            me.polygons.foreach_get('index', ti)
            ti = np.reshape(ti, (-1, 1))
            ms = np.reshape(ms, (-1, 1))
            ms = np.concatenate((ti, ms), axis=1)
            
            # return (ts, np.reshape(ns, (l, 3)), ms, )
            
            # split normals
            # TODO: remove old normals code and use face loop normals for everything or make a switch on mesh to use split normals or not (better solution i guess, and faster as well)
            vnn = len(me.vertices)
            ll = len(me.loops)
            lns = np.zeros((ll * 3), dtype=np.float, )
            me.loops.foreach_get('normal', lns)
            lns = np.reshape(lns, (ll, 3))
            sn = np.zeros((l, 3, 3), dtype=np.float, )
            tsa = np.array(ts, copy=True)
            for i, p in enumerate(me.polygons):
                a = p.loop_start
                b = a + p.loop_total
                sn[p.index] = lns[a:b]
                for j in range(3):
                    tsa[i][j + 3] = vnn + a + j
            
            return (tsa, np.reshape(sn, (ll, 3)), ms)
        
        def triangles2(me):
            l = len(me.polygons)
            ts = np.zeros((l * 3), dtype=np.int, )
            ms = np.zeros(l, dtype=np.int, )
            me.polygons.foreach_get('vertices', ts)
            me.polygons.foreach_get('material_index', ms)
            
            # normals
            vnn = len(me.vertices)
            ll = len(me.loops)
            # loop indices
            ni = np.arange(vnn, vnn + ll, 1, dtype=np.int, )
            ni = np.reshape(ni, (l, 3))
            ts = np.reshape(ts, (l, 3))
            ts = np.concatenate((ts, ni), axis=1)
            # loops normals
            lns = np.zeros((ll * 3), dtype=np.float, )
            me.loops.foreach_get('normal', lns)
            sn = np.reshape(lns, (l, 3, 3))
            
            # materials
            ti = np.zeros(l, dtype=np.int, )
            me.polygons.foreach_get('index', ti)
            ti = np.reshape(ti, (-1, 1))
            ms = np.reshape(ms, (-1, 1))
            ms = np.concatenate((ti, ms), axis=1)
            
            return (ts, np.reshape(sn, (ll, 3)), ms)
        
        def triangles3(me):
            l = len(me.tessfaces)
            ts = np.zeros((l * 3), dtype=np.int, )
            ms = np.zeros(l, dtype=np.int, )
            me.tessfaces.foreach_get('vertices', ts)
            me.tessfaces.foreach_get('material_index', ms)
            
            # normals
            vnn = len(me.vertices)
            ll = len(me.loops)
            # loop indices
            ni = np.arange(vnn, vnn + ll, 1, dtype=np.int, )
            ni = np.reshape(ni, (l, 3))
            ts = np.reshape(ts, (l, 3))
            ts = np.concatenate((ts, ni), axis=1)
            # loops normals
            lns = np.zeros((ll * 3), dtype=np.float, )
            me.loops.foreach_get('normal', lns)
            sn = np.reshape(lns, (l, 3, 3))
            
            # materials
            ti = np.zeros(l, dtype=np.int, )
            me.tessfaces.foreach_get('index', ti)
            ti = np.reshape(ti, (-1, 1))
            ms = np.reshape(ms, (-1, 1))
            ms = np.concatenate((ti, ms), axis=1)
            
            return (ts, np.reshape(sn, (ll, 3)), ms)
        
        def tess_uvs(tuv):
            l = len(tuv.data)
            e = 6
            uv = np.zeros((l * e), dtype=np.float, )
            tuv.data.foreach_get('uv', uv)
            uv = np.reshape(uv, (l * 3, 2), )
            z = np.zeros((l * 3, 1), dtype=uv.dtype)
            uv = np.c_[uv, z]
            uv = np.reshape(uv, (l * 9), )
            a = np.zeros(uv.shape, dtype=uv.dtype)
            a[2 - 1::3] = 1.0
            uv[2 - 1::3] = a[2 - 1::3] - uv[2 - 1::3]
            r = np.reshape(uv, (l, 9), )
            return r
        
        vertices, normals = verts(me)
        if(me.use_auto_smooth):
            triangles, triangle_normals, triangle_materials = triangles3(me)
        else:
            triangles, triangle_normals, triangle_materials = triangles(me)
        
        uv_channels = []
        for tix, uvtex in enumerate(me.tessface_uv_textures):
            uv = tess_uvs(uvtex)
            uv_channels.append(uv)
        
        self.m_num_positions += 1
        self.m_vertices.append(vertices)
        self.m_normals.append(normals)
        self.m_triangles = triangles
        self.m_triangle_normals.append(triangle_normals)
        self.m_uv_channels = uv_channels
        self.m_triangle_materials = triangle_materials


class MXSMeshInstance(MXSObject):
    def __init__(self, o, base, ):
        # log("'{}'".format(o['object'].name), 2)
        if('dupli_matrix' in o):
            log("'{}'".format(o['dupli_name']), 2, )
        else:
            log("'{}'".format(o['object'].name), 2, )
        
        super().__init__(o)
        self.m_type = 'MESH_INSTANCE'
        self.m_instanced = base.m_name
        self.base_b_object = base.b_object
        
        self._materials()
        
        self.dupli = False
        if('dupli_matrix' in self.o):
            self.dupli = True
        
        if(self.dupli):
            # parent will be always the one set in _collect(), in dupli groups dupli object don't have to be parented and result is wrong transformation
            self.m_name = MXSDatabase.object_name(self.b_object, self.o['dupli_name'])
            dpo = bpy.data.objects[self.o['parent']['object'].name]
            self.m_parent = MXSDatabase.object_name(dpo, dpo.name)
            
            mw = self.o['dupli_matrix'].copy()
            m = self.o['parent']['object'].matrix_world.inverted() * mw
            m *= ROTATE_X_90
            b, p, l, r, s = self._matrix_to_base_and_pivot(m)
            
            self.m_base = b
            self.m_pivot = p
            self.m_location = l
            self.m_rotation = r
            self.m_scale = s
            
            if('extra_options' in self.o):
                if('hide' in self.o['extra_options']):
                    # if(self.o['extra_options']['hide'] is True):
                    #     self.m_hide = True
                    self.m_hide = self.o['extra_options']['hide']


class MXSReference(MXSObject):
    def __init__(self, o, ):
        log("'{}' > '{}'".format(o['object'].name, bpy.path.abspath(o['object'].maxwell_render.reference.path), ), 2)
        
        super().__init__(o)
        self.m_type = 'REFERENCE'
        
        ob = self.b_object
        mx = ob.maxwell_render.reference
        
        self.ref = mx
        
        if(mx.path == ""):
            log("mxs file path is empty, skipping..", 3, LogStyles.WARNING)
            self.skip = True
        elif(not os.path.exists(bpy.path.abspath(mx.path))):
            log("mxs file: '{}' does not exist, skipping..".format(bpy.path.abspath(mx.path)), 3, LogStyles.WARNING)
            self.skip = True
        
        self.m_path = bpy.path.abspath(bpy.path.abspath(mx.path))
        
        self.m_flag_override_hide = mx.flag_override_hide
        self.m_flag_override_hide_to_camera = mx.flag_override_hide_to_camera
        self.m_flag_override_hide_to_refl_refr = mx.flag_override_hide_to_refl_refr
        self.m_flag_override_hide_to_gi = mx.flag_override_hide_to_gi
        
        self._materials()
    
    def _materials(self):
        self.m_material = ''
        self.m_backface_material = ''
        if(self.ref.material != ''):
            try:
                self.m_material = bpy.data.materials[self.ref.material].name
            except:
                log("material '{}' does not exist.".format(self.ref.material, ), 3, LogStyles.WARNING, )
        if(self.ref.backface_material != ''):
            try:
                self.m_backface_material = bpy.data.materials[self.ref.backface_material].name
            except:
                log("material '{}' does not exist.".format(self.ref.backface_material, ), 3, LogStyles.WARNING, )


class MXSParticles(MXSObject):
    def __init__(self, o, ):
        log("'{}' > '{}' ({})".format(o['parent'].name, o['object'].name, 'PARTICLES', ), 2)
        
        super().__init__(o, True, )
        
        self.m_type = 'PARTICLES'
        
        self.b_object = self.o['parent']
        self.b_name = self.b_object.name
        self.b_matrix_world = Matrix.Identity(4)
        
        self.b_parent = None
        self.b_parent_matrix_world = self.b_object.matrix_world.copy()
        self.b_parent_type = 'OBJECT'
        
        self.m_parent = MXSDatabase.object_name(self.b_object, self.b_object.name)
        self.m_name = MXSDatabase.object_name(self.b_object, "{}-{}".format(self.m_parent, self.o['object'].name))
        
        self.mx = self.b_object.maxwell_render
        
        self.ps = self.o['object']
        self.mxex = self.ps.settings.maxwell_render.particles
        
        self._object_properties()
        if(not self.mxex.hide):
            self.m_hide = False
        
        self._transformation()
        
        self._to_data()
        self._materials()
    
    def _to_data(self):
        mxex = self.mxex
        ps = self.ps
        
        has_uvs = False
        pdata = {}
        self.stat_num = 0
        
        if(mxex.source == 'BLENDER_PARTICLES'):
            def check(ps):
                if(len(ps.particles) == 0):
                    # raise ValueError("particle system {} has no particles".format(ps.name))
                    log("particle system {} has no particles".format(ps.name), 3, LogStyles.WARNING, )
                    self.skip = True
                ok = False
                for p in ps.particles:
                    if(p.alive_state == "ALIVE"):
                        ok = True
                        break
                if(not ok):
                    # raise ValueError("particle system {} has no 'ALIVE' particles".format(ps.name))
                    log("particle system {} has no 'ALIVE' particles".format(ps.name), 3, LogStyles.WARNING, )
                    self.skip = True
            
            check(ps)
            
            # i get particle locations in global coordinates, so need to fix that
            mat = self.b_parent_matrix_world.copy()
            mat.invert()
            
            locs = []
            vels = []
            sizes = []
            
            for part in ps.particles:
                if(part.alive_state == "ALIVE"):
                    l = part.location.copy()
                    l = mat * l
                    locs.append(l)
                    if(mxex.bl_use_velocity):
                        v = part.velocity.copy()
                        v = mat * v
                        vels.append(v)
                    else:
                        vels.append(Vector((0.0, 0.0, 0.0)))
                    # size per particle
                    if(mxex.bl_use_size):
                        sizes.append(part.size / 2)
                    else:
                        sizes.append(mxex.bl_size / 2)
            
            # # fix rotation of .bin
            # for i, l in enumerate(locs):
            #     locs[i] = Vector(l * ROTATE_X_90).to_tuple()
            # if(mxex.bl_use_velocity):
            #     for i, v in enumerate(vels):
            #         vels[i] = Vector(v * ROTATE_X_90).to_tuple()
            
            rfms = Matrix.Scale(1.0, 4)
            rfms[0][0] = -1.0
            rfmr = Matrix.Rotation(math.radians(-90.0), 4, 'Z')
            rfm = rfms * rfmr * ROTATE_X_90
            
            mry90 = Matrix.Rotation(math.radians(90.0), 4, 'Y')
            
            for i, l in enumerate(locs):
                if(mxex.embed):
                    locs[i] = Vector(l * ROTATE_X_90).to_tuple()
                else:
                    # locs[i] = Vector(l * ROTATE_X_90 * mry90).to_tuple()
                    locs[i] = Vector(l * rfm).to_tuple()
            
            if(mxex.bl_use_velocity):
                for i, v in enumerate(vels):
                    if(mxex.embed):
                        vels[i] = Vector(v * ROTATE_X_90).to_tuple()
                    else:
                        # vels[i] = Vector(v * ROTATE_X_90 * mry90).to_tuple()
                        vels[i] = Vector(v * rfm).to_tuple()
            
            # particle uv
            if(mxex.uv_layer is not ""):
                if(not mxex.embed):
                    log("particles uvs are supported only for embedded particles", 3, LogStyles.WARNING, )
                
                o = self.b_object
                
                uv_no = 0
                for i, uv in enumerate(o.data.uv_textures):
                    if(mxex.uv_layer == uv.name):
                        uv_no = i
                        break
                
                uv_locs = tuple()
                
                if(len(ps.child_particles) > 0):
                    log("child particles uvs are not supported yet..", 3, LogStyles.WARNING, )
                else:
                    # no child particles, use 'uv_on_emitter'
                    nc0 = len(ps.particles)
                    nc1 = len(ps.child_particles) - nc0
                    uv_no = 0
                    for i, uv in enumerate(o.data.uv_textures):
                        if(mxex.uv_layer == uv.name):
                            uv_no = i
                            break
                    mod = None
                    for m in o.modifiers:
                        if(m.type == 'PARTICLE_SYSTEM'):
                            if(m.particle_system == ps):
                                mod = m
                                break
                    uv_locs = tuple()
                    for i, p in enumerate(ps.particles):
                        co = ps.uv_on_emitter(mod, p, particle_no=i, uv_no=uv_no, )
                        # (x, y, 0.0, )
                        t = co.to_tuple() + (0.0, )
                        # uv_locs += (t[0], t[1] * -1.0, t[2], )
                        uv_locs += (t[0], 1.0 - t[1], t[2], )
                    if(nc1 != 0):
                        ex = int(nc1 / nc0)
                    for i in range(ex):
                        uv_locs += uv_locs
                has_uvs = True
            else:
                uv_locs = [0.0] * (len(ps.particles) * 3)
                log("emitter has no UVs or no UV is selected to be used.. root UVs will be exported all roots will be set to (0.0, 0.0)".format(self.mxex.material, ), 3, LogStyles.WARNING, )
            
            flip_xy = Matrix(((-1.0, 0.0, 0.0, 0.0), (0.0, -1.0, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)))
            fv = Vector((-1.0, -1.0, 0.0))
            particles = []
            for i, ploc in enumerate(locs):
                # normal from velocity
                pnor = Vector(vels[i])
                pnor.normalize()
                # particles.append((i, ) + tuple(ploc[:3]) + pnor.to_tuple() + tuple(vels[i][:3]) + (sizes[i], ) + uv_locs[i * 3:(i * 3) + 3], )
                # particles.append((i, ) + tuple(ploc[:3]) + pnor.to_tuple() + tuple(vels[i][:3]) + (sizes[i], ))
                uv = uv_locs[i * 3:(i * 3) + 3]
                uvv = Vector(uv).reflect(fv) * flip_xy
                uvt = (uvv.z, uvv.x, uvv.y, )
                particles.append((i, ) + tuple(ploc[:3]) + pnor.to_tuple() + tuple(vels[i][:3]) + (sizes[i], ) + uvt, )
            
            if(mxex.embed):
                plocs = [v for v in locs]
                pvels = [v for v in vels]
                pnors = []
                for i, v in enumerate(pvels):
                    n = Vector(v)
                    n.normalize()
                    pnors.append(n)
                
                pdata = {'PARTICLE_POSITIONS': [v for l in plocs for v in l],
                         'PARTICLE_SPEEDS': [v for l in pvels for v in l],
                         'PARTICLE_RADII': [v for v in sizes],
                         'PARTICLE_IDS': [i for i in range(len(locs))],
                         'PARTICLE_NORMALS': [v for l in pnors for v in l],
                         # 'PARTICLE_FLAG_COLORS', [0], 0, 0, '8 BYTEARRAY', 1, 1, True)
                         # 'PARTICLE_COLORS', [0.0], 0.0, 0.0, '6 FLOATARRAY', 4, 1, True)
                         'PARTICLE_UVW': uv_locs,
                         }
                
            else:
                if(os.path.exists(bpy.path.abspath(mxex.bin_directory)) and not mxex.bin_overwrite):
                    raise OSError("file: {} exists".format(bpy.path.abspath(mxex.bin_directory)))
                
                cf = bpy.context.scene.frame_current
                prms = {'directory': bpy.path.abspath(mxex.bin_directory),
                        'name': "{}".format(self.m_name),
                        'frame': cf,
                        'particles': particles,
                        'fps': bpy.context.scene.render.fps,
                        'size': 1.0 if mxex.bl_use_size else mxex.bl_size / 2,
                        'log_indent': 3, }
                rfbw = rfbin.RFBinWriter(**prms)
                mxex.bin_filename = rfbw.path
                
                self.stat_num = len(particles)
                
        else:
            mxex.embed = False
            
            # external particles
            if(mxex.bin_type == 'SEQUENCE'):
                # sequence
                cf = bpy.context.scene.frame_current
                if(mxex.seq_limit):
                    # get frame number from defined range
                    rng = [i for i in range(mxex.seq_start, mxex.seq_end + 1)]
                    try:
                        gf = rng[cf - 1]
                    except IndexError:
                        # current frame is out of limits, skip
                        skip = True
                        gf = -1
                else:
                    gf = cf
                if(gf >= 0):
                    # try to find correct bin
                    mxex.private_bin_filename = mxex.bin_filename
                    sqpath = bpy.path.abspath(mxex.bin_filename)
                    fnm_re = r'^.*\d{5}\.bin$'
                    dnm, fnm = os.path.split(sqpath)
                    if(re.match(fnm_re, fnm)):
                        bnm = fnm[:-10]
                        sqbp = os.path.join(dnm, "{}-{}.bin".format(bnm, str(gf).zfill(5)))
                        if(os.path.exists(sqbp)):
                            mxex.bin_filename = sqbp
                        else:
                            # skip if not found
                            log("cannot find .bin file for frame: {} at path: '{}'. skipping..".format(gf, sqbp), 3, LogStyles.WARNING, )
                            skip = True
                    else:
                        # skip if not found
                        log("cannot find .bin file for frame: {} at path: '{}'. skipping..".format(gf, sqpath), 3, LogStyles.WARNING, )
                        skip = True
                else:
                    skip = True
            else:
                # static particles, just take what is on path
                pass
        
        self.m_bin_filename = bpy.path.abspath(mxex.bin_filename)
        self.m_bin_radius_multiplier = mxex.bin_radius_multiplier
        self.m_bin_motion_blur_multiplier = mxex.bin_motion_blur_multiplier
        self.m_bin_shutter_speed = mxex.bin_shutter_speed
        self.m_bin_load_particles = mxex.bin_load_particles
        self.m_bin_axis_system = int(mxex.bin_axis_system[-1:])
        self.m_bin_frame_number = mxex.bin_frame_number
        self.m_bin_fps = mxex.bin_fps
        self.m_bin_extra_create_np_pp = mxex.bin_extra_create_np_pp
        self.m_bin_extra_dispersion = mxex.bin_extra_dispersion
        self.m_bin_extra_deformation = mxex.bin_extra_deformation
        self.m_bin_load_force = int(mxex.bin_load_force)
        self.m_bin_load_vorticity = int(mxex.bin_load_vorticity)
        self.m_bin_load_normal = int(mxex.bin_load_normal)
        self.m_bin_load_neighbors_num = int(mxex.bin_load_neighbors_num)
        self.m_bin_load_uv = int(mxex.bin_load_uv)
        if(has_uvs and mxex.embed is False):
            # set this the hard way
            self.m_bin_load_uv = True
        self.m_bin_load_age = int(mxex.bin_load_age)
        self.m_bin_load_isolation_time = int(mxex.bin_load_isolation_time)
        self.m_bin_load_viscosity = int(mxex.bin_load_viscosity)
        self.m_bin_load_density = int(mxex.bin_load_density)
        self.m_bin_load_pressure = int(mxex.bin_load_pressure)
        self.m_bin_load_mass = int(mxex.bin_load_mass)
        self.m_bin_load_temperature = int(mxex.bin_load_temperature)
        self.m_bin_load_id = int(mxex.bin_load_id)
        self.m_bin_min_force = mxex.bin_min_force
        self.m_bin_max_force = mxex.bin_max_force
        self.m_bin_min_vorticity = mxex.bin_min_vorticity
        self.m_bin_max_vorticity = mxex.bin_max_vorticity
        self.m_bin_min_nneighbors = mxex.bin_min_nneighbors
        self.m_bin_max_nneighbors = mxex.bin_max_nneighbors
        self.m_bin_min_age = mxex.bin_min_age
        self.m_bin_max_age = mxex.bin_max_age
        self.m_bin_min_isolation_time = mxex.bin_min_isolation_time
        self.m_bin_max_isolation_time = mxex.bin_max_isolation_time
        self.m_bin_min_viscosity = mxex.bin_min_viscosity
        self.m_bin_max_viscosity = mxex.bin_max_viscosity
        self.m_bin_min_density = mxex.bin_min_density
        self.m_bin_max_density = mxex.bin_max_density
        self.m_bin_min_pressure = mxex.bin_min_pressure
        self.m_bin_max_pressure = mxex.bin_max_pressure
        self.m_bin_min_mass = mxex.bin_min_mass
        self.m_bin_max_mass = mxex.bin_max_mass
        self.m_bin_min_temperature = mxex.bin_min_temperature
        self.m_bin_max_temperature = mxex.bin_max_temperature
        self.m_bin_min_velocity = mxex.bin_min_velocity
        self.m_bin_max_velocity = mxex.bin_max_velocity
        self.m_embed = mxex.embed
        self.m_pdata = pdata
        # self.m_hide_parent = mxex.hide_parent
        self.m_type = 'PARTICLES'
        
        if(mxex.private_bin_filename != ''):
            mxex.bin_filename = mxex.private_bin_filename
            mxex.private_bin_filename = ''
    
    def _materials(self):
        self.m_material = ''
        self.m_backface_material = ''
        if(self.mxex.material != ''):
            try:
                self.m_material = bpy.data.materials[self.mxex.material].name
            except:
                log("material '{}' does not exist.".format(self.mxex.material, ), 3, LogStyles.WARNING, )
        if(self.mxex.backface_material != ''):
            try:
                self.m_backface_material = bpy.data.materials[self.mxex.backface_material].name
            except:
                log("material '{}' does not exist.".format(self.mxex.backface_material, ), 3, LogStyles.WARNING, )


class MXSHair(MXSObject):
    def __init__(self, o, ):
        log("'{}' > '{}' ({})".format(o['parent'].name, o['object'].name, 'HAIR', ), 2)
        
        super().__init__(o, True, )
        
        self.m_type = 'HAIR'
        
        self.b_object = self.o['parent']
        self.b_name = self.b_object.name
        self.b_matrix_world = Matrix.Identity(4)
        
        self.b_parent = None
        self.b_parent_matrix_world = self.b_object.matrix_world.copy()
        self.b_parent_type = 'OBJECT'
        
        self.m_parent = MXSDatabase.object_name(self.b_object, self.b_object.name)
        self.m_name = MXSDatabase.object_name(self.b_object, "{}-{}".format(self.m_parent, self.o['object'].name))
        
        self.mx = self.b_object.maxwell_render
        
        self.ps = self.o['object']
        self.mxex = self.ps.settings.maxwell_render.hair
        
        self._object_properties()
        if(not self.mxex.hide):
            self.m_hide = False
        
        self._transformation()
        
        self._to_data()
        self._materials()
    
    def _to_data(self):
        mxex = self.mxex
        ps = self.ps
        o = self.b_object
        
        # self.m_hide_parent = mxex.hide_parent
        self.m_display_percent = int(mxex.display_percent)
        
        pmw = o.matrix_world
        if(mxex.hair_type == 'GRASS'):
            self.m_extension = 'MGrassP'
            # divide by two, because maxwell works with radius, but setting diameter is more convenient, you know, better to imagine
            self.m_grass_root_width = maths.real_length_to_relative(pmw, mxex.grass_root_width) / 1000 / 2
            self.m_grass_tip_width = maths.real_length_to_relative(pmw, mxex.grass_tip_width) / 1000 / 2
            self.m_display_max_blades = mxex.display_max_blades
        else:
            self.m_extension = 'MaxwellHair'
            # divide by two, because maxwell works with radius, but setting diameter is more convenient, you know, better to imagine
            self.m_hair_root_radius = maths.real_length_to_relative(pmw, mxex.hair_root_radius) / 1000 / 2
            self.m_hair_tip_radius = maths.real_length_to_relative(pmw, mxex.hair_tip_radius) / 1000 / 2
            self.m_display_max_hairs = mxex.display_max_hairs
        
        ps.set_resolution(bpy.context.scene, o, 'RENDER')
        
        mat = Matrix.Rotation(math.radians(-90.0), 4, 'X')
        transform = o.matrix_world.inverted()
        omw = o.matrix_world
        
        steps = 2 ** ps.settings.render_step
        # steps = 2 ** ps.settings.render_step + 1
        num_curves = len(ps.particles) if len(ps.child_particles) == 0 else len(ps.child_particles)
        points = []
        for p in range(0, num_curves):
            seg_length = 1.0
            curve = []
            
            for step in range(0, steps):
                co = ps.co_hair(o, p, step)
                
                # get distance between last and this point
                if(step > 0):
                    seg_length = (co - omw * curve[len(curve) - 1]).length_squared
                if(len(curve) == 0 and co.length_squared == 0):
                    # in case the first curve part is exactly in 0,0,0
                    co = Vector((0.000001, 0.000001, 0.000001))
                if not (co.length_squared == 0 or seg_length == 0):
                    # if it is not zero append as new point
                    v = transform * co
                    v = mat * v
                    curve.append(v)
            
            points.append(curve)
        
        if(mxex.uv_layer is not ""):
            uv_no = 0
            for i, uv in enumerate(o.data.uv_textures):
                if(mxex.uv_layer == uv.name):
                    uv_no = i
                    break
            
            uv_locs = tuple()
            
            if(len(ps.child_particles) > 0):
                # object to mesh the same way as when exporting
                me = o.to_mesh(bpy.context.scene, True, 'RENDER', )
                bm = bmesh.new()
                bm.from_mesh(me)
                # apply matrix_world to calculate all in global coords
                bm.transform(o.matrix_world)
                # triangulate, the same way as when exporting mesh
                bmesh.ops.triangulate(bm, faces=bm.faces)
                tree = BVHTree.FromBMesh(bm)
                # put to mesh again..
                bm.to_mesh(me)
                uv_layers = me.uv_layers
                
                # blender 2.77 api change
                bvhtree_find = tree.find if bpy.app.version < (2, 77, 0) else tree.find_nearest
                
                for p in range(0, num_curves):
                    # global hair root location
                    root_co = ps.co_hair(o, p, 0)
                    # find closest polygon
                    polyloc, polynor, polyind, distance = bvhtree_find(root_co)
                    poly = me.polygons[polyind]
                    # loop indexes
                    pl = me.loops[poly.loop_start:poly.loop_start + poly.loop_total]
                    pli = [pl[i].vertex_index for i in range(len(pl))]
                    uvl = uv_layers[uv_layers.active_index].data[poly.loop_start:poly.loop_start + poly.loop_total]
                    # uv locs for triangle
                    uvv = []
                    for l in uvl:
                        uvv.append(l.uv)
                    
                    # mesh triangle locs
                    def get_vert(index):
                        for vi in poly.vertices:
                            if(me.vertices[vi].index == index):
                                return me.vertices[vi]
                    
                    x = get_vert(pli[0]).co
                    y = get_vert(pli[1]).co
                    z = get_vert(pli[2]).co
                    # triangle uv locs, flip y
                    ux = Vector((uvv[0].x, uvv[0].y * -1, 0.0, ))
                    uy = Vector((uvv[1].x, uvv[1].y * -1, 0.0, ))
                    uz = Vector((uvv[2].x, uvv[2].y * -1, 0.0, ))
                    # transform
                    v = barycentric_transform(root_co, x, y, z, ux, uy, uz, )
                    # add just (x, y)
                    uv_locs += v.to_tuple()[:2]
                # cleanup
                bm.free()
                bpy.data.meshes.remove(me)
            else:
                # no child particles, use 'uv_on_emitter'
                nc0 = len(ps.particles)
                nc1 = len(ps.child_particles) - nc0
                uv_no = 0
                for i, uv in enumerate(o.data.uv_textures):
                    if(mxex.uv_layer == uv.name):
                        uv_no = i
                        break
                mod = None
                for m in o.modifiers:
                    if(m.type == 'PARTICLE_SYSTEM'):
                        if(m.particle_system == ps):
                            mod = m
                            break
                uv_locs = tuple()
                for i, p in enumerate(ps.particles):
                    co = ps.uv_on_emitter(mod, p, particle_no=i, uv_no=uv_no, )
                    uv_locs += co.to_tuple()
                if(nc1 != 0):
                    ex = int(nc1 / nc0)
                for i in range(ex):
                    uv_locs += uv_locs
            
            root_uvs = 1
        else:
            # always export root uvs so it will not render as strange stripes, but warn user there is not root uv created
            root_uvs = 1
            uv_locs = [0.0] * (num_curves * 2)
            
            log("emitter has no UVs or no UV is selected to be used.. root UVs will be exported, but all coordinates will be set to (0.0, 0.0)".format(self.mxex.material, ), 3, LogStyles.WARNING, )
        
        ps.set_resolution(bpy.context.scene, o, 'PREVIEW')
        
        # fill gaps with last location, confirm it has no negative effect in rendering..
        for l in points:
            if(len(l) < steps):
                e = [l[-1]] * (steps - len(l))
                l.extend(e)
        # flatten curves
        points = [v for l in points for v in l]
        # 3 float tuples from vectors
        points = [v.to_tuple() for v in points]
        # just list of floats
        locs = [v for l in points for v in l]
        # locs = [round(v, 6) for v in locs]
        
        data = {'HAIR_MAJOR_VER': [1, 0, 0, 0],
                'HAIR_MINOR_VER': [0, 0, 0, 0],
                'HAIR_FLAG_ROOT_UVS': [root_uvs],
                'HAIR_GUIDES_COUNT': [num_curves],
                'HAIR_GUIDES_POINT_COUNT': [steps],
                # 'HAIR_POINTS': locs,
                'HAIR_ROOT_UVS': uv_locs,
                'HAIR_NORMALS': [1.0], }
        
        self.m_data = data
        self.data_locs = locs
    
    def _materials(self):
        self.m_material = ''
        self.m_backface_material = ''
        if(self.mxex.material != ''):
            try:
                self.m_material = bpy.data.materials[self.mxex.material].name
            except:
                log("material '{}' does not exist.".format(self.mxex.material, ), 3, LogStyles.WARNING, )
        if(self.mxex.backface_material != ''):
            try:
                self.m_backface_material = bpy.data.materials[self.mxex.backface_material].name
            except:
                log("material '{}' does not exist.".format(self.mxex.backface_material, ), 3, LogStyles.WARNING, )


class MXSVolumetrics(MXSObject):
    def __init__(self, o, ):
        log("'{}' ({})".format(o['object'].name, 'VOLUMETRICS', ), 2)
        
        super().__init__(o)
        self.m_type = 'VOLUMETRICS'
        
        mxex = self.b_object.maxwell_render.volumetrics
        self.mxex = mxex
        self.m_vtype = int(mxex.vtype[-1:])
        self.m_density = mxex.density
        self.m_noise_seed = mxex.noise_seed
        self.m_noise_low = mxex.noise_low
        self.m_noise_high = mxex.noise_high
        self.m_noise_detail = mxex.noise_detail
        self.m_noise_octaves = mxex.noise_octaves
        self.m_noise_persistence = mxex.noise_persistence
        
        self._materials()
        
        # repeat transformation with new data
        mw = self.b_matrix_world.copy()
        f = 2
        mw = mw * Matrix.Scale(f, 4)
        f = self.b_object.empty_draw_size
        mw = mw * Matrix.Scale(f, 4)
        self.b_matrix_world = mw
        self._transformation()
    
    def _materials(self):
        self.m_material = ''
        self.m_backface_material = ''
        if(self.mxex.material != ''):
            try:
                self.m_material = bpy.data.materials[self.mxex.material].name
            except:
                log("material '{}' does not exist.".format(self.mxex.material, ), 3, LogStyles.WARNING, )
        if(self.mxex.backface_material != ''):
            try:
                self.m_backface_material = bpy.data.materials[self.mxex.backface_material].name
            except:
                log("material '{}' does not exist.".format(self.mxex.backface_material, ), 3, LogStyles.WARNING, )


class MXSModifier(Serializable):
    def __init__(self, o, ):
        super().__init__()
        
        self.m_type = '__MODIFIER__'
        self.o = o
        self.b_object = self.o['object']
        self.m_object = MXSDatabase.object_name(self.b_object, self.b_object.name)
        self.m_name = self.m_object
        self.m_parent = self.m_object
    
    def _texture_to_data(self, name, ):
        if(name == ''):
            return None
        t = MXSTexture(name)
        a = t._repr()
        return a


class MXSGrass(MXSModifier):
    def __init__(self, o, ):
        log("'{}' ({})".format(o['object'].name, 'GRASS', ), 2)
        
        super().__init__(o)
        self.m_type = 'GRASS'
        self.mxex = self.b_object.maxwell_render.grass
        
        mxex = self.mxex
        
        self.m_density = int(mxex.density)
        self.m_density_map = self._texture_to_data(mxex.density_map)
        self.m_length = mxex.length
        self.m_length_map = self._texture_to_data(mxex.length_map)
        self.m_length_variation = mxex.length_variation
        self.m_root_width = mxex.root_width
        self.m_tip_width = mxex.tip_width
        self.m_direction_type = mxex.direction_type
        self.m_initial_angle = math.degrees(mxex.initial_angle)
        self.m_initial_angle_variation = mxex.initial_angle_variation
        self.m_initial_angle_map = self._texture_to_data(mxex.initial_angle_map)
        self.m_start_bend = mxex.start_bend
        self.m_start_bend_variation = mxex.start_bend_variation
        self.m_start_bend_map = self._texture_to_data(mxex.start_bend_map)
        self.m_bend_radius = mxex.bend_radius
        self.m_bend_radius_variation = mxex.bend_radius_variation
        self.m_bend_radius_map = self._texture_to_data(mxex.bend_radius_map)
        self.m_bend_angle = math.degrees(mxex.bend_angle)
        self.m_bend_angle_variation = mxex.bend_angle_variation
        self.m_bend_angle_map = self._texture_to_data(mxex.bend_angle_map)
        self.m_cut_off = mxex.cut_off
        self.m_cut_off_variation = mxex.cut_off_variation
        self.m_cut_off_map = self._texture_to_data(mxex.cut_off_map)
        self.m_points_per_blade = int(mxex.points_per_blade)
        self.m_primitive_type = int(mxex.primitive_type)
        self.m_seed = mxex.seed
        self.m_lod = mxex.lod
        self.m_lod_min_distance = mxex.lod_min_distance
        self.m_lod_max_distance = mxex.lod_max_distance
        self.m_lod_max_distance_density = mxex.lod_max_distance_density
        self.m_display_percent = int(mxex.display_percent)
        self.m_display_max_blades = int(mxex.display_max_blades)
        
        self._materials()
    
    def _materials(self):
        self.m_material = ''
        self.m_backface_material = ''
        if(self.mxex.material != ''):
            try:
                self.m_material = bpy.data.materials[self.mxex.material].name
            except:
                log("material '{}' does not exist.".format(self.mxex.material, ), 3, LogStyles.WARNING, )
        if(self.mxex.backface_material != ''):
            try:
                self.m_backface_material = bpy.data.materials[self.mxex.backface_material].name
            except:
                log("material '{}' does not exist.".format(self.mxex.backface_material, ), 3, LogStyles.WARNING, )


class MXSCloner(MXSModifier):
    def __init__(self, o, ):
        log("'{}' > '{}' ({})".format(o['parent'].name, o['object'].name, 'CLONER', ), 2)
        
        super().__init__(o)
        self.m_type = 'CLONER'
        
        self.b_object = self.o['parent']
        self.ps = self.o['object']
        self.mxex = self.ps.settings.maxwell_render.cloner
        
        # parent is object with particle system (emitter) even when cloned object is not child of it.
        # cloner is excluded from hierarchy and parent property is only used when use_render_emitter is False
        self.m_parent = MXSDatabase.object_name(self.b_object, self.b_object.name)
        
        # # cloner is not an object, it is modifier, so no name is required and no need to check for duplicate,
        # # for compatibility, default name ( from MXSModifier.__init__) is enough..
        # self.m_parent = MXSDatabase.object_name(self.b_object, self.b_object.name)
        # self.m_name = MXSDatabase.object_name(self.b_object, "{}-{}".format(self.m_parent, self.ps.name))
        
        self._to_data()
    
    def _to_data(self):
        o = self.b_object
        mxex = self.mxex
        ps = self.ps
        
        pdata = {}
        if(mxex.source == 'BLENDER_PARTICLES'):
            def check(ps):
                if(len(ps.particles) == 0):
                    # raise ValueError("particle system {} has no particles".format(ps.name))
                    log("particle system {} has no particles".format(ps.name), 3, LogStyles.WARNING, )
                    self.skip = True
                ok = False
                for p in ps.particles:
                    if(p.alive_state == "ALIVE"):
                        ok = True
                        break
                if(not ok):
                    # raise ValueError("particle system {} has no 'ALIVE' particles".format(ps.name))
                    log("particle system {} has no 'ALIVE' particles".format(ps.name), 3, LogStyles.WARNING, )
                    self.skip = True
            
            check(ps)
            
            locs = []
            vels = []
            sizes = []
            
            for part in ps.particles:
                if(part.alive_state == "ALIVE"):
                    l = part.location.copy()
                    locs.append(l)
                    if(mxex.bl_use_velocity):
                        v = part.velocity.copy()
                        vels.append(v)
                    else:
                        vels.append(Vector((0.0, 0.0, 0.0)))
                    # size per particle
                    # if(mxex.bl_use_size):
                    #     sizes.append(part.size / 2)
                    # else:
                    #     sizes.append(mxex.bl_size / 2)
                    if(mxex.bl_use_size):
                        sizes.append(part.size)
                    else:
                        sizes.append(mxex.bl_size)
            
            rfms = Matrix.Scale(1.0, 4)
            rfms[0][0] = -1.0
            rfmr = Matrix.Rotation(math.radians(-90.0), 4, 'Z')
            rfm = rfms * rfmr * ROTATE_X_90
            
            mry90 = Matrix.Rotation(math.radians(90.0), 4, 'Y')
            
            for i, l in enumerate(locs):
                if(mxex.embed):
                    locs[i] = Vector(l * ROTATE_X_90).to_tuple()
                else:
                    # locs[i] = Vector(l * ROTATE_X_90 * mry90).to_tuple()
                    locs[i] = Vector(l * rfm).to_tuple()
            
            if(mxex.bl_use_velocity):
                for i, v in enumerate(vels):
                    if(mxex.embed):
                        vels[i] = Vector(v * ROTATE_X_90).to_tuple()
                    else:
                        # vels[i] = Vector(v * ROTATE_X_90 * mry90).to_tuple()
                        vels[i] = Vector(v * rfm).to_tuple()
            
            particles = []
            for i, ploc in enumerate(locs):
                # normal from velocity
                pnor = Vector(vels[i])
                pnor.normalize()
                particles.append((i, ) + tuple(ploc[:3]) + pnor.to_tuple() + tuple(vels[i][:3]) + (sizes[i], ) + (0.0, 0.0, 0.0, ))
            
            if(mxex.embed):
                plocs = [v for v in locs]
                pvels = [v for v in vels]
                pnors = []
                for i, v in enumerate(pvels):
                    n = Vector(v)
                    n.normalize()
                    pnors.append(n)
                
                uv_locs = [0.0] * (len(ps.particles) * 3)
                
                pdata = {'PARTICLE_POSITIONS': [v for l in plocs for v in l],
                         'PARTICLE_SPEEDS': [v for l in pvels for v in l],
                         'PARTICLE_RADII': [v for v in sizes],
                         'PARTICLE_IDS': [i for i in range(len(locs))],
                         'PARTICLE_NORMALS': [v for l in pnors for v in l],
                         'PARTICLE_UVW': uv_locs, }
            else:
                if(os.path.exists(bpy.path.abspath(mxex.directory)) and not mxex.overwrite):
                    raise OSError("file: {} exists".format(bpy.path.abspath(mxex.directory)))
                
                cf = bpy.context.scene.frame_current
                prms = {'directory': bpy.path.abspath(mxex.directory),
                        'name': "{}".format(self.m_name),
                        'frame': cf,
                        'particles': particles,
                        'fps': bpy.context.scene.render.fps,
                        # 'size': 1.0 if mxex.bl_use_size else mxex.bl_size / 2,
                        'size': 1.0 if mxex.bl_use_size else mxex.bl_size,
                        'log_indent': 3, }
                rfbw = rfbin.RFBinWriter(**prms)
                mxex.filename = rfbw.path
                pdata = rfbw.path
        else:
            pass
        
        cloned = None
        try:
            cloned = MXSDatabase.object_name(ps.settings.dupli_object, ps.settings.dupli_object.name)
        except AttributeError:
            log("{}: {}: Maxwell Cloner: cloned object is not available. Skipping..".format(o.name, ps.name), 3, LogStyles.WARNING, )
            self.skip = True
        
        self.m_filename = bpy.path.abspath(mxex.filename)
        self.m_radius = mxex.radius
        self.m_mb_factor = mxex.mb_factor
        self.m_load_percent = mxex.load_percent
        self.m_start_offset = mxex.start_offset
        self.m_extra_npp = mxex.extra_npp
        self.m_extra_p_dispersion = mxex.extra_p_dispersion
        self.m_extra_p_deformation = mxex.extra_p_deformation
        self.m_align_to_velocity = mxex.align_to_velocity
        self.m_scale_with_radius = mxex.scale_with_radius
        self.m_inherit_obj_id = mxex.inherit_obj_id
        self.m_frame = bpy.context.scene.frame_current
        self.m_fps = bpy.context.scene.render.fps
        self.m_display_percent = int(mxex.display_percent)
        self.m_display_max = int(mxex.display_max)
        if(cloned is not None):
            # self.m_cloned_object = ps.settings.dupli_object.name
            
            co = bpy.data.objects[MXSDatabase.object_original_name(ps.settings.dupli_object)]
            if(not MXSDatabase.is_in_object_export_list(co)):
                log("'{}': cloned object is hidden, skipping..".format(self.b_object.name), 3, LogStyles.WARNING, )
                self.skip = True
            
            self.m_cloned_object = cloned
        else:
            self.m_cloned_object = ''
        self.m_render_emitter = ps.settings.use_render_emitter
        self.m_embed = mxex.embed
        self.m_pdata = pdata


class MXSScatter(MXSModifier):
    def __init__(self, o, ):
        log("'{}' ({})".format(o['object'].name, 'SCATTER', ), 2)
        
        super().__init__(o)
        self.m_type = 'SCATTER'
        self.mxex = self.b_object.maxwell_render.scatter
        
        mxex = self.mxex
        
        if(mxex.scatter_object == ''):
            log("'{}': no scatter object, skipping Maxwell Scatter modifier..".format(self.b_object.name), 3, LogStyles.WARNING, )
            self.skip = True
            self.m_scatter_object = ""
        else:
            so = bpy.data.objects[mxex.scatter_object]
            # check if object is marked to export, and if not, warn user and skip it
            if(not MXSDatabase.is_in_object_export_list(so)):
                log("'{}': scatter object is hidden, skipping Maxwell Scatter modifier..".format(self.b_object.name), 3, LogStyles.WARNING, )
                self.skip = True
                self.m_scatter_object = ""
            else:
                self.m_scatter_object = MXSDatabase.object_name(so, so.name)
        
        self.m_inherit_objectid = mxex.inherit_objectid
        self.m_density = mxex.density
        self.m_density_map = self._texture_to_data(mxex.density_map)
        self.m_seed = int(mxex.seed)
        
        self.m_remove_overlapped = mxex.remove_overlapped
        
        self.m_direction_type = mxex.direction_type
        self.m_initial_angle = math.degrees(mxex.initial_angle)
        self.m_initial_angle_variation = mxex.initial_angle_variation
        self.m_initial_angle_map = self._texture_to_data(mxex.initial_angle_map)
        
        self.m_scale_x = mxex.scale_x
        self.m_scale_y = mxex.scale_y
        self.m_scale_z = mxex.scale_z
        
        self.m_scale_uniform = mxex.scale_uniform
        
        self.m_scale_map = self._texture_to_data(mxex.scale_map)
        self.m_scale_variation_x = mxex.scale_variation_x
        self.m_scale_variation_y = mxex.scale_variation_y
        self.m_scale_variation_z = mxex.scale_variation_z
        self.m_rotation_x = math.degrees(mxex.rotation_x)
        self.m_rotation_y = math.degrees(mxex.rotation_y)
        self.m_rotation_z = math.degrees(mxex.rotation_z)
        self.m_rotation_map = self._texture_to_data(mxex.rotation_map)
        self.m_rotation_variation_x = mxex.rotation_variation_x
        self.m_rotation_variation_y = mxex.rotation_variation_y
        self.m_rotation_variation_z = mxex.rotation_variation_z
        self.m_rotation_direction = int(mxex.rotation_direction)
        self.m_lod = mxex.lod
        self.m_lod_min_distance = mxex.lod_min_distance
        self.m_lod_max_distance = mxex.lod_max_distance
        self.m_lod_max_distance_density = mxex.lod_max_distance_density
        self.m_display_percent = int(mxex.display_percent)
        self.m_display_max_blades = int(mxex.display_max_blades)


class MXSSubdivision(MXSModifier):
    def __init__(self, o, quad_pairs, ):
        log("'{}' ({})".format(o['object'].name, 'SUBDIVISION', ), 2)
        
        # FIXME: disabled Subdivision until fixed
        log("Disabled due to changes in 2.77", 3, LogStyles.WARNING, )
        self.skip = True
        return
        
        super().__init__(o)
        self.m_type = 'SUBDIVISION'
        self.mxex = self.b_object.maxwell_render.subdivision
        
        mxex = self.mxex
        self.m_level = int(mxex.level)
        self.m_scheme = int(mxex.scheme)
        self.m_interpolation = int(mxex.interpolation)
        self.m_crease = mxex.crease
        self.m_smooth = math.degrees(mxex.smooth)
        self.m_quad_pairs = quad_pairs
        
        # do check if mesh is non-manifold, if not warn user and skip modifier
        def is_non_manifold(me):
            # [Extension SubdivisionModifier] A non-manifold edge incident to more than 2 faces was found
            # [Extension SubdivisionModifier] This object cannot be subdivided.
            bm = bmesh.new()
            bm.from_mesh(me)
            # for v in bm.verts:
            #     if(not v.is_manifold):
            #         bm.free()
            #         return False
            # seems like mesh with one nonemanifold edge or vertex works ok, the problem is non manifold face
            for e in bm.edges:
                if(not e.is_manifold):
                    if(len(e.link_faces) > 2):
                        bm.free()
                        return False
            bm.free()
            return True
        
        if(self.m_scheme == 0):
            types = ['CURVE', 'SURFACE', 'FONT', ]
            if(self.b_object.type in types):
                # # those are always non manifold (i think)
                # me = self.b_object.to_mesh(bpy.context.scene, True, 'RENDER', )
                # nm = is_non_manifold(me)
                # bpy.data.meshes.remove(me)
                
                # self.m_scheme = 1
                nm = True
                log("{}: Subdivision modifier on non-mesh object, Catmull-Clark subdivision may not work, if so, switch to Loop Subdivision".format(self.b_object.name), 3, LogStyles.WARNING, )
            else:
                nm = is_non_manifold(self.b_object.data)
            if(not nm):
                log("{}: Subdivision modifier on non-manifold object, a non-manifold edge incident to more than 2 faces was found, Catmull-Clark subdivision will not work, switching it off.".format(self.b_object.name), 3, LogStyles.WARNING, )
                self.skip = True
            
            def some_quads(me):
                for p in me.polygons:
                    if(len(p.vertices) == 4):
                        return True
                return False
            
            q = some_quads(self.b_object.data)
            if(not q):
                log("{}: Catmull-Clark subdivision option selected but the mesh does not contain quads, switching to Loop is recommended if results are not good.".format(self.b_object.name), 3, LogStyles.WARNING, )


class MXSSea(MXSObject):
    def __init__(self, o, ):
        log("'{}' ({})".format(o['object'].name, 'SEA', ), 2)
        
        super().__init__(o, True, )
        self.m_type = 'SEA'
        
        self.b_object = self.o['object']
        self.b_name = self.b_object.name
        self.b_matrix_world = Matrix.Identity(4)
        
        self.b_parent = self.b_object
        self.b_parent_matrix_world = Matrix.Identity(4)
        self.b_parent_type = 'OBJECT'
        
        self.m_parent = MXSDatabase.object_name(self.b_object, self.b_object.name)
        self.m_name = MXSDatabase.object_name(self.b_object, "{}-{}".format(self.m_parent, 'MaxwellSea', ))
        
        self.mx = self.b_object.maxwell_render
        self.mxex = self.b_object.maxwell_render.sea
        
        self._object_properties()
        if(not self.mxex.hide):
            self.m_hide = False
        
        self._transformation()
        
        mxex = self.mxex
        
        # self.m_hide_parent = mxex.hide_parent
        
        self.m_resolution = int(mxex.resolution)
        self.m_reference_time = mxex.reference_time
        self.m_ocean_wind_mod = mxex.ocean_wind_mod
        self.m_ocean_wind_dir = math.degrees(mxex.ocean_wind_dir)
        self.m_vertical_scale = mxex.vertical_scale
        self.m_damp_factor_against_wind = mxex.damp_factor_against_wind
        self.m_ocean_wind_alignment = mxex.ocean_wind_alignment
        self.m_ocean_min_wave_length = mxex.ocean_min_wave_length
        self.m_ocean_dim = mxex.ocean_dim
        self.m_ocean_depth = mxex.ocean_depth
        self.m_ocean_seed = mxex.ocean_seed
        self.m_enable_choppyness = mxex.enable_choppyness
        self.m_choppy_factor = mxex.choppy_factor
        self.m_enable_white_caps = mxex.enable_white_caps
        
        self._materials()
    
    def _materials(self):
        self.m_material = ''
        self.m_backface_material = ''
        if(self.mxex.material != ''):
            try:
                self.m_material = bpy.data.materials[self.mxex.material].name
            except:
                log("material '{}' does not exist.".format(self.mxex.material, ), 3, LogStyles.WARNING, )
        if(self.mxex.backface_material != ''):
            try:
                self.m_backface_material = bpy.data.materials[self.mxex.backface_material].name
            except:
                log("material '{}' does not exist.".format(self.mxex.backface_material, ), 3, LogStyles.WARNING, )


class MXSMaterial(Serializable):
    def __init__(self, name='Material', ):
        self.m_name = name
        
        self.m_type = 'MATERIAL'
        self.skip = False
    
    def _texture_to_data(self, name, ):
        if(name == ''):
            return None
        t = MXSTexture(name)
        a = t._repr()
        return a
    
    def _gamma_uncorrect(self, c, ):
        g = 1 / 2.2
        c = [v ** g for v in c]
        return c


class MXSMaterialMXM(MXSMaterial):
    def __init__(self, name, path='', embed=True, ):
        log("'{}' > '{}'".format(name, bpy.path.abspath(path), ), 2)
        
        super().__init__(name)
        self.m_subtype = 'EXTERNAL'
        if(path == ''):
            log("mxm path is empty.".format(), 3, LogStyles.WARNING, )
        else:
            path = bpy.path.abspath(path)
            if(not os.path.exists(path)):
                log("mxm ('{}') does not exist.".format(path), 3, LogStyles.WARNING, )
                path = ''
        self.m_path = path
        self.m_embed = embed
        
        mat = bpy.data.materials[name]
        m = mat.maxwell_render
        self.m_override = m.override_global_properties
        if(self.m_override):
            self.m_override_map = self._texture_to_data(m.global_override_map)
            
            self.m_bump = m.global_bump
            self.m_bump_map_enabled = m.global_bump_map_enabled
            self.m_bump_map = self._texture_to_data(m.global_bump_map)
            self.m_bump_map_use_normal = m.global_bump_map_use_normal
            self.m_bump_normal = m.global_bump_normal
            
            self.m_dispersion = m.global_dispersion
            self.m_shadow = m.global_shadow
            self.m_matte = m.global_matte
            self.m_priority = m.global_priority
            self.m_id = self._gamma_uncorrect(m.global_id)


class MXSMaterialExtension(MXSMaterial):
    def __init__(self, name, ):
        log("'{}' > '{}'".format(name, bpy.data.materials[name].maxwell_render.use, ), 2)
        
        super().__init__(name)
        self.m_subtype = 'EXTENSION'
        
        mat = bpy.data.materials[name]
        m = mat.maxwell_render
        mx = mat.maxwell_render.extension
        
        self.m = m
        self.mx = mx
        
        self.m_override_map = self._texture_to_data(m.global_override_map)
        
        self.m_bump = m.global_bump
        self.m_bump_map_enabled = m.global_bump_map_enabled
        self.m_bump_map = self._texture_to_data(m.global_bump_map)
        self.m_bump_map_use_normal = m.global_bump_map_use_normal
        self.m_bump_normal = m.global_bump_normal
        
        self.m_dispersion = m.global_dispersion
        self.m_shadow = m.global_shadow
        self.m_matte = m.global_matte
        self.m_priority = m.global_priority
        self.m_id = self._gamma_uncorrect(m.global_id)
        
        self.m_use = m.use
        
        if(self.m_use == 'EMITTER'):
            self._emitter()
        elif(self.m_use == 'AGS'):
            self._ags()
        elif(self.m_use == 'OPAQUE'):
            self._opaque()
        elif(self.m_use == 'TRANSPARENT'):
            self._transparent()
        elif(self.m_use == 'METAL'):
            self._metal()
        elif(self.m_use == 'TRANSLUCENT'):
            self._translucent()
        elif(self.m_use == 'CARPAINT'):
            self._carpaint()
        elif(self.m_use == 'HAIR'):
            self._hair()
        else:
            raise TypeError("{}: Unsupported extension material type: {}".format(self.m_name, self.m_use, ))
        
        self.m_active_display_map = self._texture_to_data(m.active_display_map)
        
        dtypes = ['AGS', 'OPAQUE', 'TRANSPARENT', 'METAL', 'TRANSLUCENT', 'CARPAINT', 'HAIR', ]
        if(self.m_use in dtypes):
            self._displacement()
    
    def _emitter(self):
        mx = self.mx
        self.m_emitter_type = int(mx.emitter_type)
        self.m_emitter_ies_data = bpy.path.abspath(mx.emitter_ies_data)
        self.m_emitter_ies_intensity = mx.emitter_ies_intensity
        self.m_emitter_spot_map_enabled = mx.emitter_spot_map_enabled
        self.m_emitter_spot_map = self._texture_to_data(mx.emitter_spot_map)
        self.m_emitter_spot_cone_angle = math.degrees(mx.emitter_spot_cone_angle)
        self.m_emitter_spot_falloff_angle = math.degrees(mx.emitter_spot_falloff_angle)
        self.m_emitter_spot_falloff_type = int(mx.emitter_spot_falloff_type)
        self.m_emitter_spot_blur = mx.emitter_spot_blur
        self.m_emitter_emission = int(mx.emitter_emission)
        self.m_emitter_color = self._gamma_uncorrect(mx.emitter_color)
        self.m_emitter_color_black_body_enabled = mx.emitter_color_black_body_enabled
        self.m_emitter_color_black_body = mx.emitter_color_black_body
        self.m_emitter_luminance = int(mx.emitter_luminance)
        self.m_emitter_luminance_power = mx.emitter_luminance_power
        self.m_emitter_luminance_efficacy = mx.emitter_luminance_efficacy
        self.m_emitter_luminance_output = mx.emitter_luminance_output
        self.m_emitter_temperature_value = mx.emitter_temperature_value
        self.m_emitter_hdr_map = self._texture_to_data(mx.emitter_hdr_map)
        self.m_emitter_hdr_intensity = mx.emitter_hdr_intensity
    
    def _ags(self):
        mx = self.mx
        self.m_ags_color = self._gamma_uncorrect(mx.ags_color)
        self.m_ags_reflection = mx.ags_reflection
        self.m_ags_type = int(mx.ags_type)
    
    def _opaque(self):
        mx = self.mx
        self.m_opaque_color_type = mx.opaque_color_type
        self.m_opaque_color = self._gamma_uncorrect(mx.opaque_color)
        self.m_opaque_color_map = self._texture_to_data(mx.opaque_color_map)
        self.m_opaque_shininess_type = mx.opaque_shininess_type
        self.m_opaque_shininess = mx.opaque_shininess
        self.m_opaque_shininess_map = self._texture_to_data(mx.opaque_shininess_map)
        self.m_opaque_roughness_type = mx.opaque_roughness_type
        self.m_opaque_roughness = mx.opaque_roughness
        self.m_opaque_roughness_map = self._texture_to_data(mx.opaque_roughness_map)
        self.m_opaque_clearcoat = mx.opaque_clearcoat
    
    def _transparent(self):
        mx = self.mx
        self.m_transparent_color_type = mx.transparent_color_type
        self.m_transparent_color = self._gamma_uncorrect(mx.transparent_color)
        self.m_transparent_color_map = self._texture_to_data(mx.transparent_color_map)
        self.m_transparent_ior = mx.transparent_ior
        self.m_transparent_transparency = mx.transparent_transparency
        self.m_transparent_roughness_type = mx.transparent_roughness_type
        self.m_transparent_roughness = mx.transparent_roughness
        self.m_transparent_roughness_map = self._texture_to_data(mx.transparent_roughness_map)
        self.m_transparent_specular_tint = mx.transparent_specular_tint
        self.m_transparent_dispersion = mx.transparent_dispersion
        self.m_transparent_clearcoat = mx.transparent_clearcoat
    
    def _metal(self):
        mx = self.mx
        self.m_metal_ior = int(mx.metal_ior)
        self.m_metal_tint = mx.metal_tint
        self.m_metal_color_type = mx.metal_color_type
        self.m_metal_color = self._gamma_uncorrect(mx.metal_color)
        self.m_metal_color_map = self._texture_to_data(mx.metal_color_map)
        self.m_metal_roughness_type = mx.metal_roughness_type
        self.m_metal_roughness = mx.metal_roughness
        self.m_metal_roughness_map = self._texture_to_data(mx.metal_roughness_map)
        self.m_metal_anisotropy_type = mx.metal_anisotropy_type
        self.m_metal_anisotropy = mx.metal_anisotropy
        self.m_metal_anisotropy_map = self._texture_to_data(mx.metal_anisotropy_map)
        self.m_metal_angle_type = mx.metal_angle_type
        self.m_metal_angle = math.degrees(mx.metal_angle)
        self.m_metal_angle_map = self._texture_to_data(mx.metal_angle_map)
        self.m_metal_dust_type = mx.metal_dust_type
        self.m_metal_dust = mx.metal_dust
        self.m_metal_dust_map = self._texture_to_data(mx.metal_dust_map)
        self.m_metal_perforation_enabled = mx.metal_perforation_enabled
        self.m_metal_perforation_map = self._texture_to_data(mx.metal_perforation_map)
    
    def _translucent(self):
        mx = self.mx
        self.m_translucent_scale = mx.translucent_scale
        self.m_translucent_ior = mx.translucent_ior
        self.m_translucent_color_type = mx.translucent_color_type
        self.m_translucent_color = self._gamma_uncorrect(mx.translucent_color)
        self.m_translucent_color_map = self._texture_to_data(mx.translucent_color_map)
        self.m_translucent_hue_shift = mx.translucent_hue_shift
        self.m_translucent_invert_hue = mx.translucent_invert_hue
        self.m_translucent_vibrance = mx.translucent_vibrance
        self.m_translucent_density = mx.translucent_density
        self.m_translucent_opacity = mx.translucent_opacity
        self.m_translucent_roughness_type = mx.translucent_roughness_type
        self.m_translucent_roughness = mx.translucent_roughness
        self.m_translucent_roughness_map = self._texture_to_data(mx.translucent_roughness_map)
        self.m_translucent_specular_tint = mx.translucent_specular_tint
        self.m_translucent_clearcoat = mx.translucent_clearcoat
        self.m_translucent_clearcoat_ior = mx.translucent_clearcoat_ior
    
    def _carpaint(self):
        mx = self.mx
        self.m_carpaint_color = self._gamma_uncorrect(mx.carpaint_color)
        self.m_carpaint_metallic = mx.carpaint_metallic
        self.m_carpaint_topcoat = mx.carpaint_topcoat
    
    def _hair(self):
        mx = self.mx
        self.m_hair_color_type = mx.hair_color_type
        self.m_hair_color = self._gamma_uncorrect(mx.hair_color)
        self.m_hair_color_map = self._texture_to_data(mx.hair_color_map)
        self.m_hair_root_tip_map = self._texture_to_data(mx.hair_root_tip_map)
        self.m_hair_root_tip_weight_type = mx.hair_root_tip_weight_type
        self.m_hair_root_tip_weight = mx.hair_root_tip_weight
        self.m_hair_root_tip_weight_map = self._texture_to_data(mx.hair_root_tip_weight_map)
        self.m_hair_primary_highlight_strength = mx.hair_primary_highlight_strength
        self.m_hair_primary_highlight_spread = mx.hair_primary_highlight_spread
        self.m_hair_primary_highlight_tint = self._gamma_uncorrect(mx.hair_primary_highlight_tint)
        self.m_hair_secondary_highlight_strength = mx.hair_secondary_highlight_strength
        self.m_hair_secondary_highlight_spread = mx.hair_secondary_highlight_spread
        self.m_hair_secondary_highlight_tint = self._gamma_uncorrect(mx.hair_secondary_highlight_tint)
    
    def _displacement(self):
        mx = self.mx
        displacementd = {'enabled': False, 'map': "", 'type': 1, 'subdivision': 5, 'adaptive': False, 'subdivision_method': 0,
                         'offset': 0.5, 'smoothing': True, 'uv_interpolation': 2, 'height': 2.0, 'height_units': 0,
                         'v3d_preset': 0, 'v3d_transform': 0, 'v3d_rgb_mapping': 0, 'v3d_scale': (1.0, 1.0, 1.0), }
        
        if(mx.displacement.enabled):
            displacement = mx['displacement'].to_dict()
            for k, v in displacementd.items():
                if(k not in displacement):
                    displacement[k] = v
            
            # converting..
            cmap = ['map', ]
            cenum = ['type', 'subdivision_method', 'uv_interpolation', 'height_units', 'v3d_preset', 'v3d_transform', 'v3d_rgb_mapping', ]
            for k, v in displacement.items():
                if(k in cmap):
                    displacement[k] = self._texture_to_data(v)
                if(k in cenum):
                    displacement[k] = int(v)
            
            if(displacement['height_units'] == 1):
                displacement['height'] = displacement['height'] / 100
            
            self.m_displacement = displacement
        else:
            self.m_displacement = displacementd.copy()


class MXSProceduralTexture(Serializable):
    def __init__(self, p, ):
        self.m_brick_brick_width = p.brick_brick_width
        self.m_brick_brick_height = p.brick_brick_height
        self.m_brick_brick_offset = p.brick_brick_offset
        self.m_brick_random_offset = p.brick_random_offset
        self.m_brick_double_brick = p.brick_double_brick
        self.m_brick_small_brick_width = p.brick_small_brick_width
        self.m_brick_round_corners = p.brick_round_corners
        self.m_brick_boundary_sharpness_u = p.brick_boundary_sharpness_u
        self.m_brick_boundary_sharpness_v = p.brick_boundary_sharpness_v
        self.m_brick_boundary_noise_detail = p.brick_boundary_noise_detail
        self.m_brick_boundary_noise_region_u = p.brick_boundary_noise_region_u
        self.m_brick_boundary_noise_region_v = p.brick_boundary_noise_region_v
        self.m_brick_seed = p.brick_seed
        self.m_brick_random_rotation = p.brick_random_rotation
        self.m_brick_color_variation = p.brick_color_variation
        self.m_brick_brick_color_0 = self._gamma_uncorrect(p.brick_brick_color_0)
        self.m_brick_brick_texture_0 = self._texture_to_data(p.brick_brick_texture_0)
        self.m_brick_sampling_factor_0 = p.brick_sampling_factor_0
        self.m_brick_weight_0 = p.brick_weight_0
        self.m_brick_brick_color_1 = self._gamma_uncorrect(p.brick_brick_color_1)
        self.m_brick_brick_texture_1 = self._texture_to_data(p.brick_brick_texture_1)
        self.m_brick_sampling_factor_1 = p.brick_sampling_factor_1
        self.m_brick_weight_1 = p.brick_weight_1
        self.m_brick_brick_color_2 = self._gamma_uncorrect(p.brick_brick_color_2)
        self.m_brick_brick_texture_2 = self._texture_to_data(p.brick_brick_texture_2)
        self.m_brick_sampling_factor_2 = p.brick_sampling_factor_2
        self.m_brick_weight_2 = p.brick_weight_2
        self.m_brick_mortar_thickness = p.brick_mortar_thickness
        self.m_brick_mortar_color = self._gamma_uncorrect(p.brick_mortar_color)
        self.m_brick_mortar_texture = self._texture_to_data(p.brick_mortar_texture)
        
        self.m_checker_number_of_elements_u = p.checker_number_of_elements_u
        self.m_checker_number_of_elements_v = p.checker_number_of_elements_v
        self.m_checker_color_0 = self._gamma_uncorrect(p.checker_color_0)
        self.m_checker_color_1 = self._gamma_uncorrect(p.checker_color_1)
        self.m_checker_transition_sharpness = p.checker_transition_sharpness
        self.m_checker_falloff = int(p.checker_falloff)
        
        self.m_circle_background_color = self._gamma_uncorrect(p.circle_background_color)
        self.m_circle_circle_color = self._gamma_uncorrect(p.circle_circle_color)
        self.m_circle_radius_u = p.circle_radius_u
        self.m_circle_radius_v = p.circle_radius_v
        self.m_circle_transition_factor = p.circle_transition_factor
        self.m_circle_falloff = int(p.circle_falloff)
        
        self.m_gradient3_gradient_u = p.gradient3_gradient_u
        self.m_gradient3_color0_u = self._gamma_uncorrect(p.gradient3_color0_u)
        self.m_gradient3_color1_u = self._gamma_uncorrect(p.gradient3_color1_u)
        self.m_gradient3_color2_u = self._gamma_uncorrect(p.gradient3_color2_u)
        self.m_gradient3_gradient_type_u = int(p.gradient3_gradient_type_u)
        self.m_gradient3_color1_u_position = p.gradient3_color1_u_position
        self.m_gradient3_gradient_v = p.gradient3_gradient_v
        self.m_gradient3_color0_v = self._gamma_uncorrect(p.gradient3_color0_v)
        self.m_gradient3_color1_v = self._gamma_uncorrect(p.gradient3_color1_v)
        self.m_gradient3_color2_v = self._gamma_uncorrect(p.gradient3_color2_v)
        self.m_gradient3_gradient_type_v = int(p.gradient3_gradient_type_v)
        self.m_gradient3_color1_v_position = p.gradient3_color1_v_position
        
        self.m_gradient_gradient_u = p.gradient_gradient_u
        self.m_gradient_color0_u = self._gamma_uncorrect(p.gradient_color0_u)
        self.m_gradient_color1_u = self._gamma_uncorrect(p.gradient_color1_u)
        self.m_gradient_gradient_type_u = int(p.gradient_gradient_type_u)
        self.m_gradient_transition_factor_u = p.gradient_transition_factor_u
        self.m_gradient_gradient_v = p.gradient_gradient_v
        self.m_gradient_color0_v = self._gamma_uncorrect(p.gradient_color0_v)
        self.m_gradient_color1_v = self._gamma_uncorrect(p.gradient_color1_v)
        self.m_gradient_gradient_type_v = int(p.gradient_gradient_type_v)
        self.m_gradient_transition_factor_v = p.gradient_transition_factor_v
        
        self.m_grid_horizontal_lines = p.grid_horizontal_lines
        self.m_grid_vertical_lines = p.grid_vertical_lines
        self.m_grid_cell_width = p.grid_cell_width
        self.m_grid_cell_height = p.grid_cell_height
        self.m_grid_boundary_thickness_u = p.grid_boundary_thickness_u
        self.m_grid_boundary_thickness_v = p.grid_boundary_thickness_v
        self.m_grid_transition_sharpness = p.grid_transition_sharpness
        self.m_grid_cell_color = self._gamma_uncorrect(p.grid_cell_color)
        self.m_grid_boundary_color = self._gamma_uncorrect(p.grid_boundary_color)
        self.m_grid_falloff = int(p.grid_falloff)
        
        self.m_marble_coordinates_type = int(p.marble_coordinates_type)
        self.m_marble_color0 = self._gamma_uncorrect(p.marble_color0)
        self.m_marble_color1 = self._gamma_uncorrect(p.marble_color1)
        self.m_marble_color2 = self._gamma_uncorrect(p.marble_color2)
        self.m_marble_frequency = p.marble_frequency
        self.m_marble_detail = p.marble_detail
        self.m_marble_octaves = p.marble_octaves
        self.m_marble_seed = p.marble_seed
        
        self.m_noise_coordinates_type = int(p.noise_coordinates_type)
        self.m_noise_noise_color = self._gamma_uncorrect(p.noise_noise_color)
        self.m_noise_background_color = self._gamma_uncorrect(p.noise_background_color)
        self.m_noise_detail = p.noise_detail
        self.m_noise_persistance = p.noise_persistance
        self.m_noise_octaves = p.noise_octaves
        self.m_noise_low_value = p.noise_low_value
        self.m_noise_high_value = p.noise_high_value
        self.m_noise_seed = p.noise_seed
        
        self.m_voronoi_coordinates_type = int(p.voronoi_coordinates_type)
        self.m_voronoi_color0 = self._gamma_uncorrect(p.voronoi_color0)
        self.m_voronoi_color1 = self._gamma_uncorrect(p.voronoi_color1)
        self.m_voronoi_detail = p.voronoi_detail
        self.m_voronoi_distance = int(p.voronoi_distance)
        self.m_voronoi_combination = int(p.voronoi_combination)
        self.m_voronoi_low_value = p.voronoi_low_value
        self.m_voronoi_high_value = p.voronoi_high_value
        self.m_voronoi_seed = p.voronoi_seed
        
        self.m_tiled_filename = os.path.realpath(bpy.path.abspath(p.tiled_filename))
        self.m_tiled_token_mask = p.tiled_token_mask
        self.m_tiled_base_color = self._gamma_uncorrect(p.tiled_base_color)
        self.m_tiled_use_base_color = p.tiled_use_base_color
        
        self.m_wireframe_fill_color = self._gamma_uncorrect(p.wireframe_fill_color)
        self.m_wireframe_edge_color = self._gamma_uncorrect(p.wireframe_edge_color)
        self.m_wireframe_coplanar_edge_color = self._gamma_uncorrect(p.wireframe_coplanar_edge_color)
        self.m_wireframe_edge_width = p.wireframe_edge_width
        self.m_wireframe_coplanar_edge_width = p.wireframe_coplanar_edge_width
        self.m_wireframe_coplanar_threshold = p.wireframe_coplanar_threshold
        
        self.m_enabled = p.enabled
        self.m_blending_factor = p.blending_factor
        self.m_name = p.name
        self.m_index = p.index
        self.m_use = p.use
    
    def _texture_to_data(self, name, ):
        if(name == ''):
            return None
        t = MXSTexture(name)
        a = t._repr()
        return a
    
    def _gamma_uncorrect(self, c, ):
        g = 1 / 2.2
        c = [v ** g for v in c]
        return c


class MXSTexture(Serializable):
    def __init__(self, name, ):
        self.invalid = False
        self.procedural_only = False
        try:
            # KeyError if not such texture
            tex = bpy.data.textures[name]
            image = tex.image
            # AttributeError if not image is loaded
            image_path = image.filepath
            log("'{}' ({}: {}) '{}'".format(name, 'TEXTURE', 'IMAGE', bpy.path.abspath(image_path), ), 3, )
            self.invalid = False
        except KeyError:
            log("'{}' ({}: {}) does not exist!".format(name, 'TEXTURE', 'IMAGE', ), 3, LogStyles.WARNING, )
            self.invalid = True
            return
        except AttributeError:
            if(len(tex.maxwell_render.procedural.textures) > 0):
                # when procedural textures are present, image don't have to be loaded
                self.procedural_only = True
            else:
                log("'{}' ({}: {}) image not loaded!".format(name, 'TEXTURE', 'IMAGE', ), 3, LogStyles.WARNING, )
                self.invalid = True
                return
        
        self.m_name = name
        self.m_type = 'TEXTURE'
        self.m_subtype = 'IMAGE'
        
        if(tex.type != 'IMAGE'):
            raise TypeError("{}: Unsupported texture type: {}".format(self.m_name, tex.type, ))
        m = tex.maxwell_render
        
        self.m_path = ""
        if(not self.procedural_only):
            self.m_path = bpy.path.abspath(tex.image.filepath)
            
            if(self.m_path == ""):
                log("image path is empty..", 4, LogStyles.WARNING, )
                self.invalid = True
            elif(not os.path.exists(self.m_path)):
                log("image file '{}' does not exist..".format(self.m_path), 4, LogStyles.WARNING, )
                self.invalid = True
        
        self.m_use_global_map = m.use_global_map
        self.m_channel = m.channel
        self.m_tile_method_units = int(m.tiling_units[-1:])
        self.m_repeat = (m.repeat[0], m.repeat[1], )
        self.m_mirror = (m.mirror_x, m.mirror_y, )
        self.m_offset = (m.offset[0], m.offset[1], )
        self.m_rotation = m.rotation
        self.m_invert = m.invert
        self.m_alpha_only = m.use_alpha
        self.m_interpolation = m.interpolation
        self.m_brightness = m.brightness
        self.m_contrast = m.contrast
        self.m_saturation = m.saturation
        self.m_hue = m.hue
        self.m_rgb_clamp = (m.clamp[0], m.clamp[1], )
        
        self.m_normal_mapping_flip_red = m.normal_mapping_flip_red
        self.m_normal_mapping_flip_green = m.normal_mapping_flip_green
        self.m_normal_mapping_full_range_blue = m.normal_mapping_full_range_blue
        
        if(m.tiling_method == 'NO_TILING'):
            tm = (False, False, )
        elif(m.tiling_method == 'TILE_X'):
            tm = (True, False, )
        elif(m.tiling_method == 'TILE_Y'):
            tm = (False, True, )
        else:
            tm = (True, True, )
        self.m_tile_method_type = tm
        
        self.m_procedural = []
        
        pt = m.procedural.textures
        if(len(pt) > 0):
            for p in pt:
                if(p.enabled):
                    t = MXSProceduralTexture(p)
                    self.m_procedural.append(t._repr())
    
    def _repr(self):
        if(self.invalid):
            return None
        
        d = self._dict()
        a = {}
        for k, v in d.items():
            a[k[2:]] = v
        return a


class MXSMaterialCustom(MXSMaterial):
    def __init__(self, name, ):
        log("'{}' > '{}'".format(name, 'CUSTOM', ), 2)
        super().__init__(name)
        self.m_subtype = 'CUSTOM'
        
        mat = bpy.data.materials[name]
        m = mat.maxwell_render
        
        bsdfd = {'visible': True, 'weight': 100.0, 'weight_map_enabled': False, 'weight_map': "", 'ior': 0, 'complex_ior': "",
                 'reflectance_0': (0.6, 0.6, 0.6, ), 'reflectance_0_map_enabled': False, 'reflectance_0_map': "",
                 'reflectance_90': (1.0, 1.0, 1.0, ), 'reflectance_90_map_enabled': False, 'reflectance_90_map': "",
                 'transmittance': (0.0, 0.0, 0.0), 'transmittance_map_enabled': False, 'transmittance_map': "",
                 'attenuation': 1.0, 'attenuation_units': 0, 'nd': 3.0, 'force_fresnel': False, 'k': 0.0, 'abbe': 1.0,
                 'r2_enabled': False, 'r2_falloff_angle': math.radians(75.0), 'r2_influence': 0.0,
                 'roughness': 100.0, 'roughness_map_enabled': False, 'roughness_map': "",
                 'bump': 30.0, 'bump_map_enabled': False, 'bump_map': "", 'bump_map_use_normal': False, 'bump_normal': 100.0,
                 'anisotropy': 0.0, 'anisotropy_map_enabled': False, 'anisotropy_map': "",
                 'anisotropy_angle': math.radians(0.0), 'anisotropy_angle_map_enabled': False, 'anisotropy_angle_map': "",
                 'scattering': (0.5, 0.5, 0.5, ), 'coef': 0.0, 'asymmetry': 0.0,
                 'single_sided': False, 'single_sided_value': 1.0, 'single_sided_map_enabled': False, 'single_sided_map': "", 'single_sided_min': 0.001, 'single_sided_max': 10.0, }
        coatingd = {'enabled': False,
                    'thickness': 500.0, 'thickness_map_enabled': False, 'thickness_map': "", 'thickness_map_min': 100.0, 'thickness_map_max': 1000.0,
                    'ior': 0, 'complex_ior': "",
                    'reflectance_0': (0.6, 0.6, 0.6, ), 'reflectance_0_map_enabled': False, 'reflectance_0_map': "",
                    'reflectance_90': (1.0, 1.0, 1.0, ), 'reflectance_90_map_enabled': False, 'reflectance_90_map': "",
                    'nd': 3.0, 'force_fresnel': False, 'k': 0.0, 'r2_enabled': False, 'r2_falloff_angle': math.radians(75.0), }
        displacementd = {'enabled': False, 'map': "", 'type': 1, 'subdivision': 5, 'adaptive': False, 'subdivision_method': 0,
                         'offset': 0.5, 'smoothing': True, 'uv_interpolation': 2, 'height': 2.0, 'height_units': 0,
                         'v3d_preset': 0, 'v3d_transform': 0, 'v3d_rgb_mapping': 0, 'v3d_scale': (1.0, 1.0, 1.0), }
        emitterd = {'enabled': False, 'type': 0, 'ies_data': "", 'ies_intensity': 1.0,
                    'spot_map_enabled': False, 'spot_map': "", 'spot_cone_angle': math.radians(45.0), 'spot_falloff_angle': math.radians(10.0), 'spot_falloff_type': 0, 'spot_blur': 1.0,
                    'emission': 0, 'color': (1.0, 1.0, 1.0, ), 'color_black_body_enabled': False, 'color_black_body': 6500.0,
                    'luminance': 0, 'luminance_power': 40.0, 'luminance_efficacy': 17.6, 'luminance_output': 100.0, 'temperature_value': 6500.0,
                    'hdr_map': "", 'hdr_intensity': 1.0, }
        layerd = {'visible': True, 'opacity': 100.0, 'opacity_map_enabled': False, 'opacity_map': "", 'blending': 0, }
        
        structure = []
        for i, l in enumerate(m.custom_layers.layers):
            lb = []
            for j, b in enumerate(l.layer.bsdfs.bsdfs):
                lb.append([b['name'], l.layer.bsdfs.bsdfs[j]])
            structure.append([l['name'], m.custom_layers.layers[i], lb, ])
        
        layers = []
        for i, sl in enumerate(structure):
            lpd = sl[1]['layer'].to_dict()
            del lpd['bsdfs']
            # del lpd['emitter']
            for k, v in layerd.items():
                if(k not in lpd):
                    lpd[k] = v
            
            # converting..
            cmap = ['opacity_map', ]
            cenum = ['blending', ]
            for k, v in lpd.items():
                if(k in cmap):
                    lpd[k] = self._texture_to_data(v)
                if(k in cenum):
                    lpd[k] = int(v)
            
            # epd = sl[1]['layer']['emitter'].to_dict()
            epd = sl[1]['emitter'].to_dict()
            for k, v in emitterd.items():
                if(k not in epd):
                    epd[k] = v
            
            # converting..
            cmap = ['spot_map', 'hdr_map', ]
            cangle = ['spot_cone_angle', 'spot_falloff_angle', ]
            cenum = ['type', 'spot_falloff_type', 'emission', 'luminance', ]
            cpath = ['ies_data', ]
            cgamma = ['color', ]
            for k, v in epd.items():
                if(k in cmap):
                    epd[k] = self._texture_to_data(v)
                if(k in cangle):
                    epd[k] = math.degrees(v)
                if(k in cenum):
                    epd[k] = int(v)
                if(k in cpath):
                    if(v == ""):
                        epd[k] == ""
                    else:
                        epd[k] = os.path.realpath(bpy.path.abspath(v))
                if(k in cgamma):
                    epd[k] = self._gamma_uncorrect(v)
            
            bsdfs = []
            for j, bl in enumerate(sl[2]):
                bpd = bl[1]['bsdf'].to_dict()
                for k, v in bsdfd.items():
                    if(k not in bpd):
                        bpd[k] = v
                
                # converting..
                cmap = ['weight_map', 'reflectance_0_map', 'reflectance_90_map', 'transmittance_map', 'roughness_map', 'bump_map', 'anisotropy_map', 'anisotropy_angle_map', 'single_sided_map', ]
                cangle = ['r2_falloff_angle', 'anisotropy_angle', ]
                cenum = ['ior', 'attenuation_units', ]
                cpath = ['complex_ior', ]
                cmm = ['single_sided_value', 'single_sided_min', 'single_sided_max', ]
                cgamma = ['reflectance_0', 'reflectance_90', 'transmittance', 'scattering', ]
                for k, v in bpd.items():
                    if(k in cmap):
                        bpd[k] = self._texture_to_data(v)
                    if(k in cangle):
                        bpd[k] = math.degrees(v)
                    if(k in cenum):
                        bpd[k] = int(v)
                    if(k in cpath):
                        if(v == ""):
                            bpd[k] == ""
                        else:
                            bpd[k] = os.path.realpath(bpy.path.abspath(v))
                    if(k in cmm):
                        bpd[k] = v / 1000
                    if(k in cgamma):
                        bpd[k] = self._gamma_uncorrect(v)
                
                cpd = bl[1]['coating'].to_dict()
                for k, v in coatingd.items():
                    if(k not in cpd):
                        cpd[k] = v
                
                # converting..
                cmap = ['thickness_map', 'reflectance_0_map', 'reflectance_90_map', ]
                cangle = ['r2_falloff_angle', ]
                cenum = ['ior', ]
                cpath = ['complex_ior', ]
                cnm = ['thickness', 'thickness_map_min', 'thickness_map_max', ]
                cgamma = ['reflectance_0', 'reflectance_90', ]
                for k, v in cpd.items():
                    if(k in cmap):
                        cpd[k] = self._texture_to_data(v)
                    if(k in cangle):
                        cpd[k] = math.degrees(v)
                    if(k in cenum):
                        cpd[k] = int(v)
                    if(k in cpath):
                        if(v == ""):
                            cpd[k] == ""
                        else:
                            cpd[k] = os.path.realpath(bpy.path.abspath(v))
                    if(k in cnm):
                        cpd[k] = v / 1000000000
                    if(k in cgamma):
                        cpd[k] = self._gamma_uncorrect(v)
                
                bsdf = {'name': bl[0],
                        'bsdf_props': bpd,
                        'coating': cpd, }
                bsdfs.append(bsdf)
            
            if(len(bsdfs) == 0):
                log("material has no bsdfs in layer '{}'".format(sl[0]), 3, LogStyles.WARNING, )
            
            layer = {'name': sl[0],
                     'layer_props': lpd,
                     'bsdfs': bsdfs,
                     'emitter': epd, }
            layers.append(layer)
        
        if(len(layers) == 0):
            # material has no layers and therefore no displacement..
            displacement = displacementd.copy()
            log("material has no layers..", 3, LogStyles.WARNING, )
            
        else:
            displacement = m['custom_displacement'].to_dict()
            for k, v in displacementd.items():
                if(k not in displacement):
                    displacement[k] = v
            
            # converting..
            cmap = ['map', ]
            cenum = ['type', 'subdivision_method', 'uv_interpolation', 'height_units', 'v3d_preset', 'v3d_transform', 'v3d_rgb_mapping', ]
            for k, v in displacement.items():
                if(k in cmap):
                    displacement[k] = self._texture_to_data(v)
                if(k in cenum):
                    displacement[k] = int(v)
            
            if(displacement['height_units'] == 1):
                displacement['height'] = displacement['height'] / 100
        
        global_props = {'override_map': self._texture_to_data(m.global_override_map),
                        
                        'bump': m.global_bump,
                        'bump_map_enabled': m.global_bump_map_enabled,
                        'bump_map': self._texture_to_data(m.global_bump_map),
                        'bump_map_use_normal': m.global_bump_map_use_normal,
                        'bump_normal': m.global_bump_normal,
                        
                        'dispersion': m.global_dispersion,
                        'shadow': m.global_shadow,
                        'matte': m.global_matte,
                        'priority': m.global_priority,
                        'id': self._gamma_uncorrect(m.global_id),
                        'active_display_map': self._texture_to_data(m.active_display_map), }
        
        self.m_data = {'global_props': global_props,
                       'displacement': displacement,
                       'layers': layers, }
        
        # import pprint
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(self.m_data)


class MXSWireframeBase(MXSMesh):
    def __init__(self, euuid, ):
        n = 'WIREFRAME_BASE_{}'.format(euuid)
        mx = bpy.context.scene.maxwell_render
        gen = utils.CylinderMeshGenerator(height=1, radius=mx.export_wire_edge_radius, sides=mx.export_wire_edge_resolution, enhanced=True, )
        me = bpy.data.meshes.new(n)
        v, e, f = gen.generate()
        me.from_pydata(v, [], f)
        for p in me.polygons:
            p.use_smooth = True
        ob = utils.add_object2(n, me)
        
        o = {'type': 'MESH', 'export': True, 'object': ob, 'mesh': me, 'export_type': 'MESH', 'parent': None, 'children': [], 'converted': False, }
        super().__init__(o)
        
        self.m_type = 'WIREFRAME_BASE'
        self.wipe_out_object = ob
        
        # self.m_num_materials = 1
        # self.m_materials = [wire_material_name]


class MXSWireframeContainer(MXSEmpty):
    def __init__(self, euuid, ):
        n = 'WIREFRAME_CONTAINER_{}'.format(euuid)
        ob = utils.add_object2(n, None, )
        
        o = {'parent': None, 'type': 'EMPTY', 'object': ob, 'export_type': 'EMPTY', 'mesh': None, 'converted': False, 'children': [], 'export': True, }
        super().__init__(o)
        
        self.m_type = 'WIREFRAME_CONTAINER'
        self.wipe_out_object = ob


class MXSWireframeInstances(MXSObject):
    def __init__(self, o, wire_base_name, ):
        # log("wireframe: '{}'".format(o.m_name), 3, )
        log("wireframe..", 3, )
        
        d = {'parent': None,
             'type': 'MESH',
             'object': bpy.data.objects[wire_base_name],
             'export_type': 'INSTANCE',
             'mesh': bpy.data.objects[wire_base_name].data,
             'converted': False,
             'children': [],
             'export': True, }
        
        super().__init__(d)
        
        self.m_type = 'WIREFRAME_INSTANCES'
        self.m_instanced = wire_base_name
        self.base_b_object = bpy.data.objects[wire_base_name]
        
        ob = o.b_object
        me = ob.to_mesh(bpy.context.scene, True, 'RENDER', )
        mw = ob.matrix_world
        try:
            # duplicates are handled differently
            mw = o.o['dupli_matrix']
        except KeyError:
            pass
        
        me.transform(mw)
        
        vs = tuple([v.co.copy() for v in me.vertices])
        es = tuple([tuple([i for i in e.vertices]) for e in me.edges])
        ms = self._calc_marices(vs=vs, es=es, )
        
        dt = []
        for m in ms:
            b, p, l, r, s = self._transformation2(m)
            dt.append((b, p, l, r, s, ))
        
        bpy.data.meshes.remove(me)
        
        self.m_num_wires = len(dt)
        self.m_wire_matrices = dt
        
        self.m_name = MXSDatabase.object_name(self.b_object, 'wireframe-{}'.format(o.m_name))
        
        # self.m_num_materials = 1
        # self.m_materials = [wire_material_name]
    
    def _calc_marices(self, vs, es, ):
        """Calculate wire matrices."""
        
        def distance(a, b):
            return ((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2) ** 0.5
        
        matrices = []
        up = Vector((0, 0, 1))
        for i, e in enumerate(es):
            a = vs[e[0]]
            b = vs[e[1]]
            d = distance(a, b)
            
            # v1
            quat = maths.rotation_to(Vector((0, 0, 1)), b - a)
            mr = quat.to_matrix().to_4x4()
            mt = Matrix.Translation(a)
            mtr = mt * mr
            
            # # v2
            # mtr = maths.look_at_matrix(a, Vector(maths.shift_vert_along_normal(a, b-a, -1.0)), up, )
            
            # add scale as well
            ms = Matrix.Scale(d, 4, up)
            m = mtr * ms
            matrices.append(m)
        
        return matrices
    
    def _transformation2(self, m, ):
        if(self.b_parent):
            m = self.b_parent_matrix_world.copy().inverted() * m
        m *= ROTATE_X_90
        b, p, l, r, s = self._matrix_to_base_and_pivot(m)
        return (b, p, l, r, s, )
