# =============================================================================
# (C) Copyright 2014
# Australian Centre for Microscopy & Microanalysis
# The University of Sydney
# =============================================================================
# File:   operatorexec.py
# Date:   2014-07-03
# Author: Varvara Efremova
#
# Description:
# AtomBlend operator execution function definitions.
# =============================================================================

import bpy
import numpy as np
import ntpath

from .aptread import aptload as APTloader
from . import blend
from . import analysis

# === Operator execute functions ===
def analysis_isosurface_gen(self, context):
    """Perform isosurface analysis on current dataset"""
    # Get POS xyz data
    props = context.scene.pos_panel_props
    # Get user specified isorange
    isorange = [props.analysis_isosurf_rangefrom, props.analysis_isosurf_rangeto]
    
    #Get vertices of object from Blender
    for item in bpy.context.selected_objects:
        if item.type == 'MESH':
          pointcloud=[vertex.co for vertex in item.data.vertices]

    pointcloud=np.asarray(pointcloud)        
    
    try: 
        print('START')
        print("Calculating voxelisation")
        voxarray, min_ = analysis.voxelisation.voxelise(pointcloud)
        print("Calculating isosurface for isovalue", isorange[0])
        verts, faces = analysis.isosurface.generate(voxarray, isorange, min_)
            
        print("Calculating isosurface done! \n \n")    
        edges = []
    
        # Draw object
        blend.object.object_add_from_pydata("Isosurface", verts, edges, faces)
    except ValueError:
        print('Isovalue entered not valid \n\n')

    return {'FINISHED'}

def animation_add(self, context):
    """Add animation to selected object"""
    # Get POS xyz data
    props = context.scene.pos_panel_props
    # FIXME don't load this again!!! save as global var for now?
    data = APTloader.ReadAPTData(props.pos_filename, props.rng_filename)
    data_centre = np.average(data.xyz, axis=0)

    # Set camera location and offset from dataset (user)
    cam_target = data_centre
    cam_offset = list(data_centre)
    cam_offset[0] += props.animation_offsetx
    cam_offset[2] += props.animation_offsetz

    blend.animation.add(target=cam_target,
                        offset=cam_offset,
                        cam_orth_scale=props.animation_scale,
                        cam_clip_dist=props.animation_clip_dist,
                        time=props.animation_time,
                        fps=props.animation_fps,
                        )
    return {'FINISHED'}

def scale_child(self, context):
    obj = context.object
    child = obj.children[0]

    # select child and deselect obj
    blend.object.select(obj, False)
    blend.object.select(child, True)
    return blend.object.selected_resize()

def position_active_camera_on(self, context):
    blend.space.camera_position_on()
    return {'FINISHED'}

def position_active_camera_off(self, context):
    blend.space.camera_position_off()
    return {'FINISHED'}

def make_camera_active(self, context):
    cam = context.object
    blend.space.camera_set_active(cam)
    return {'FINISHED'}

def add_bounding_box(self, context):
    """Calculate and add a bounding box to the current data"""
    props = context.scene.pos_panel_props
    padding = props.boundbox_padding
    #padding = self.padding

    # FIXME don't load this again!!! save as global var for now?
    data = APTloader.ReadAPTData(props.pos_filename, props.rng_filename)

    pointlist = data.xyz
    xyzmax = np.amax(pointlist, axis=0) # max locations in data
    xyzmin = np.amin(pointlist, axis=0) # min locations in data

    # add padding to extremal xyz coords
    xyzmax += padding
    xyzmin -= padding

    # define vertices of cube, clockwise, starting from bottom
    coords = [[-1, -1, -1],
             [-1,  1, -1],
             [ 1,  1, -1],
             [ 1, -1, -1],
             [-1, -1,  1],
             [-1,  1,  1],
             [ 1,  1,  1],
             [ 1, -1,  1]]
    coords = np.array(coords)
    # numpy where is awesome
    # (replaces -ves with respective min values, +ves with max values)
    verts = np.where(coords > 0, xyzmax, xyzmin)

    # create bounding box and draw as wireframe
    name = "Bound"
    origin = (0.0, 0.0, 0.0)
    bound = blend.object.cube_add_from_verts(name, origin, verts)
    boundmat = blend.material.surface_add(name+"_mat", shadeless=True)
    blend.material.set(bound, boundmat)
    blend.object.modifier_add_wireframe(bound)

    grp = blend.space.group_get("Bounds")
    if not grp:
        grp = blend.space.group_add("Bounds")
    blend.space.group_add_object(grp, bound)

    bound.datatype = 'BOUND'
    return {'FINISHED'}

def add_lamp_view(self, context):
    props = context.scene.pos_panel_props

    # FIXME temp hack
    cam, lamp = blend.space.camlamp_add_to_view(ltype='SUN')
    blend.object.delete(cam)
    context.scene.objects.active = lamp
    # end temp hack

    # proper code ...
    #drawing.add_lamp_to_view(name="Lamp", ltype='SUN', color=color)

    # Add to lamp group
    grp = blend.space.group_get("Lamps")
    if not grp:
        grp = blend.space.group_add("Lamps")
    blend.space.group_add_object(grp, lamp)
    return {'FINISHED'}

def pointcloud_add(self, context):
    props = context.scene.pos_panel_props
    color = props.ptcld_color
    emit = props.ptcld_emit

    obj = context.object

    # Get list of verts from active object
    verts = blend.object.vertices_get(obj)

    # Create pointcloud from these verts and set its parent to active obj
    ptcld = blend.object.pointcloud_add(verts, obj.name+"_pointcloud")
    blend.object.parent_set(obj, ptcld)

    # Add wireframe material
    # TODO FIXME
    mat = drawing.create_material_wire(ptcld.name+"_mat", color=color, emit=emit)
    blend.material.set(ptcld, mat)
    return {'FINISHED'}

def add_camera_view(self, context):
    cam = blend.space.camera_add_to_view(name="Camera", clip_start=0.1, clip_end=1000.0)

    # Add to camera group
    grp = blend.space.group_get("Cameras")
    if not grp:
        grp = blend.space.group_add("Cameras")
    blend.space.group_add_object(grp, cam)
    return {'FINISHED'}

def add_halo_material(self, context):
    obj = context.object

    mat = blend.material.halo_add(obj.name+"_halo", use_tex=True)
    tex = blend.material.texture_add_img(obj.name+"_tex", path=self.halo_img_path)
    blend.material.texture_add(mat, tex)
    blend.material.set(obj, mat)

    obj.vistype = 'HALO'
    return{'FINISHED'}

def remove_halo_material(self, context):
    obj = context.object
    blend.object.active_material_delete(obj)

    obj.vistype = 'NONE'
    return{'FINISHED'}

def dupli_vert(self, context):
    # Applies vertex duplication with icospheres to currently selected objects
    # select object to add mesh child to (props)
    # create desired mesh (props)

    # active object is parent
    obj = context.object

    # create child icosphere
    vertobj = blend.object.icosphere_add(name=obj.name+"_vert")

    # create material for child icosphere, link to child
    vertmat = blend.material.surface_add(name=obj.name+"_mat")
    blend.material.set(vertobj, vertmat)

    blend.object.parent_set(obj, vertobj)
    blend.object.dupli_set(obj, 'VERTS')

    obj.vistype = 'DUPLI'
    return {'FINISHED'}

def remove_duplivert(self, context):
    obj = context.object
    blend.object.delete_children(obj)
    blend.object.dupli_set(obj, 'NONE')

    obj.vistype = 'NONE'
    return{'FINISHED'}

def clear(self, context):
    # Clear all objects and meshes in scene
    blend.space.delete_all()
    return {'FINISHED'}

def bake(self, context):
    """Draws currently selected pos file"""
    props     = context.scene.pos_panel_props

    # Get user selections
    apid      = props.apdata_list   # Selected AP data ID to load
                                    # (as in C.scene.apdata dict)
    plot_type = props.plot_type     # Selected plot type
                                    # Atomic/Ionic/Isotopic

    if apid:
        data = context.scene.apdata[apid]
    else:
        self.report({'ERROR'}, "No files loaded yet")
        return {'CANCELLED'}

    if plot_type == 'ISO':
        groupname = apid+" isotopic"
        listfunc = "rangelist"
        getfunc = "getrange"
    elif plot_type == 'EA':
        groupname = apid+" atomic"
        listfunc = "atomlist"
        getfunc = "getatom"
    elif plot_type == 'ION':
        groupname = apid+" ionic"
        listfunc = "ionlist"
        getfunc = "getion"

    # Populate item names and point locations
    itemlist = getattr(data.rng, listfunc)

    namelist = []
    pointlist = []
    for item in itemlist:
        # Convert item to string name if needed
        namelist.append(str(item))
        # Get points (vertices) for current item and append
        pointlist.append(getattr(data.rng, getfunc)(item))

    # Create group for meshes of same type
    grp = blend.space.group_add(groupname)

    # Draw all meshes in pointlist and link to group
    for ind, (name, verts) in enumerate(zip(namelist, pointlist)):
        obj = blend.object.object_add_from_verts(verts, name, trunc=None)

        obj.datatype = 'DATA'

        obj.apid     = apid     # AP ID name used in C.scene.apdata dict
        obj.apfunc   = getfunc  # AP function used to build dataset (eg "getion")
        obj.apname   = name     # Name of imported atom/ion/range (eg "Si")

        blend.space.group_add_object(grp, obj)

    # Centre view on created group
    blend.space.view_selected_group(groupname)

    self.report({'INFO'}, "Loaded %s data into %s group" % (apid, groupname))
    return {'FINISHED'}

def load_posrng(self, context):
    """
    Load APT pos/rng data to apdata scene variable
    """
    props = context.scene.pos_panel_props
    pospath = props.pos_filename
    rngpath = props.rng_filename

    try:
        data = APTloader.APData(pospath, rngpath)
        print("Loaded rng data: ", data.rng.atomlist)
        self.report({'INFO'}, "Loaded %s as POS, %s as RNG" % \
                (props.pos_filename, props.rng_filename))
    except APTloader.APReadError:
        self.report({'ERROR'}, "Error reading pos or rng file. Double check file names.")
        return {'CANCELLED'}

    # Add reference to scene.apdata
    dataname = ntpath.basename(props.pos_filename)
    context.scene.apdata[dataname] = data
    return {'FINISHED'}
