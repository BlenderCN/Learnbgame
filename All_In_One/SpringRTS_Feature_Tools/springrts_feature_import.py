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
import bpy,os,re
from . import slpp

def load(context, filepath):

    #find base path
    dirname = os.path.dirname(filepath)
    dirname = os.path.dirname(dirname)

    # parse the featuredef data structures
    print("LOG: Open and read featuredef")
    f = open(filepath)
    data = "{" + f.read() + "}"
    f.close()
    
    lua = slpp.slpp()
    featuredef = lua.decode(text=data)

    # pull the object name before disposing of the extra table.
    name = featuredef['objectname']
    featuredef = featuredef['featureDef']

    #build other file paths
    meshpath = dirname + "/objects3d/" + featuredef['object']
    meshdefpath = re.sub('obj$','lua',meshpath)

    # parse the meshdef data structures
    print("LOG: Open and read meshdef")
    f = open(meshdefpath)
    data = "{" + f.read() + "}"
    f.close()
    
    lua = slpp.slpp()
    meshdef = lua.decode(text=data)
    meshdef = meshdef[meshdef[1]]

    # import object file
    print("LOG: importing obj mesh")
    print("LOG: %s" % meshpath)

    bpy.ops.import_scene.obj('EXEC_DEFAULT', filepath=meshpath)
    #bpy.ops.object.transform_apply(rotation=True)

    # Select the root object
    root_object_name = list(meshdef['pieces'].keys())[0]
    root_object = context.scene.objects[root_object_name]
    context.scene.objects.active = root_object

    # Get spring feature properties
    sfp = bpy.context.object.sfp

    #load up all the properties from the slpp data structure.
    sfp.name = name
    for key in featuredef:
        if key.lower() == 'name':
            sfp.name = featuredef[key]
        elif key.lower()  == 'description':
            sfp.description = featuredef[key]
        elif key.lower()  == 'damage':
            sfp.damage = featuredef[key]
        elif key.lower()  == 'metal':
            sfp.metal = featuredef[key]
        elif key.lower()  == 'energy':
            sfp.energy = featuredef[key]
        elif key.lower()  == 'mass':
            sfp.mass = featuredef[key]
        elif key.lower()  == 'crushresistance':
            sfp.crushResistance = featuredef[key]
        elif key.lower()  == 'reclaimtime':
            sfp.reclaimTime = featuredef[key]
        elif key.lower()  == 'indestructible':
            sfp.indestructible = bool(featuredef[key])
        elif key.lower()  == 'flammable':
            sfp.flammable = featuredef[key]
        elif key.lower()  == 'reclaimable':
            sfp.reclaimable = featuredef[key]
        elif key.lower()  == 'autoreclaimable':
            sfp.autoReclaimable = featuredef[key]
        elif key.lower()  == 'featuredead':
            sfp.featureDead = featuredef[key]
        elif key.lower()  == 'smoketime':
            sfp.smokeTime = featuredef[key]
        elif key.lower()  == 'upright':
            sfp.upright = featuredef[key]
        elif key.lower()  == 'floating':
            sfp.floating = featuredef[key]
        elif key.lower()  == 'geothermal':
            sfp.geothermal = featuredef[key]
        elif key.lower()  == 'noselect':
            sfp.noSelect = featuredef[key]
        elif key.lower()  == 'blocking':
            sfp.blocking = featuredef[key]
        elif key.lower()  == 'footprintx':
            sfp.footprintX = featuredef[key]
        elif key.lower()  == 'footprintz':
            sfp.footprintZ = featuredef[key]
        elif key.lower()  == 'collisionvolumescales':
            sfp.collisionVolumeScales = featuredef[key]
        elif key.lower()  == 'collisionvolumeoffsets':
            sfp.collisionVolumeOffsets = featuredef[key]
        elif key.lower()  == 'resurrectable':
            if featuredef[key] == -1:
                sfp.resurrectable = 'first'
            elif featuredef[key] == 0:
                sfp.resurrectable = 'no'
            elif featuredef[key] == 1:
                sfp.resurrectable = 'yes'
        elif key.lower()  == 'collisionvolumetype':
            if featuredef[key] == 'box':
                sfp.collisionVolumeType = 'SME_box'
            if featuredef[key] == 'ellipse':
                sfp.collisionVolumeType = 'SME_ellipsoid'
            if featuredef[key] == 'cylX':
                sfp.collisionVolumeType = 'SME_cylX'
            if featuredef[key] == 'cylY':
                sfp.collisionVolumeType = 'SME_cylY'
            if featuredef[key] == 'cylZ':
                sfp.collisionVolumeType = 'SME_cylZ'
        else:
            print("WARN: Unrecognised Attribute: " + key)

    for key in meshdef:
        if key.lower()  == 'tex1':
            sfp.tex1 = meshdef[key]
        elif key.lower()  == 'tex2':
            sfp.tex2 = meshdef[key]
        elif key.lower()  == 'radius':
            sfp.radius = meshdef[key]
        elif key.lower()  == 'midpos':
            sfp.midpos = meshdef[key]
        else:
            print("WARN: Unrecognised Attribute: " + key)

    #find the beginning of the pieces subtable
    load_heirarchy_r(context, meshdef['pieces'])

    #Load images into blender
#    imagefilepath = dirname + "/unittextures/"
#    if sfp.tex1 != '':
#        bpy.ops.image.open(filepath=imagefilepath+sfp.tex1)
#    if sfp.tex2 != '':
#        bpy.ops.image.open(filepath=imagefilepath+sfp.tex2)

    return {'FINISHED'}

def load_heirarchy_r(context, pieces, parent = None):
    obj = None
    for i,j in pieces.items():
        bpy.ops.object.select_all(action='DESELECT')
        if i == 'offset':
            parent.select=True
            context.scene.objects.active = parent
            # set origin to correct location
            cursor = context.scene.cursor_location
            cursor[0] = j[0]
            cursor[1] = j[2] * -1
            cursor[2] = j[1]
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
            bpy.ops.object.transform_apply(rotation=True)

        else:
            obj = context.scene.objects[i]
            if parent != None:
                obj.select = True
                context.scene.objects.active = parent
                bpy.ops.object.parent_set()

            load_heirarchy_r( context, j, obj )
