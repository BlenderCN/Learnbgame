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

import bpy,mathutils
def panel_toggle(self, context):
    sfp = context.object.sfp
    if sfp.isFeature:
        bpy.utils.register_class(SpringRTSFeatureMesh)
    else:
        bpy.utils.unregister_class(SpringRTSFeatureMesh)
def AABB_recurse(
    node,
    first = True,
    aabb = [mathutils.Vector((0.0,0.0,0.0)), mathutils.Vector((0.0,0.0,0.0))]):
    # Skip if not mesh
    if node.type != 'MESH': return aabb

    offset = mathutils.Vector(
        (node.matrix_world[0][3],
        node.matrix_world[1][3],
        node.matrix_world[2][3]))

    for i in node.data.vertices:
        if first == True:
            aabb[0] = i.co + offset
            aabb[1] = i.co + offset
            first = False
        aabb[0].x = min(aabb[0].x, i.co.x + offset.x)
        aabb[0].y = min(aabb[0].y, i.co.y + offset.y)
        aabb[0].z = min(aabb[0].z, i.co.z + offset.z)
        aabb[1].x = max(aabb[1].x, i.co.x + offset.x)
        aabb[1].y = max(aabb[1].y, i.co.y + offset.y)
        aabb[1].z = max(aabb[1].z, i.co.z + offset.z)

    for j in node.children:
        aabb = AABB_recurse(j, first, aabb)
    print("LOG: AABB_recurse = %s" % aabb)

    return aabb

def cv_scale_calc(self, context):
    # Get spring feature properties
    sfp = bpy.context.object.sfp

    aabb = AABB_recurse(context.active_object)
    mag = aabb[0] * -1 + aabb[1]
    print("LOG: cv_scale_calc = %s" % mag)
    sfp.collisionVolumeScales[0] = mag[0]
    sfp.collisionVolumeScales[1] = mag[2]
    sfp.collisionVolumeScales[2] = mag[1]
    return

def cv_offset_calc(self, context):
    # Get spring feature properties
    sfp = bpy.context.object.sfp

    aabb = AABB_recurse(context.active_object)
    centre = (aabb[0] + aabb[1]) * 0.5
    print("LOG: cv_offset_calc = %s" % centre)
    sfp.collisionVolumeOffsets[0] = centre[0] - sfp.midpos[0]
    sfp.collisionVolumeOffsets[1] = centre[2] - sfp.midpos[1]
    sfp.collisionVolumeOffsets[2] = (centre[1] * -1) - sfp.midpos[2]
    return

def ov_radius_calc(self, context):
    # Get spring feature properties
    sfp = bpy.context.object.sfp

    sfp.radius = recurse_radius(context.active_object)
    return {'FINISHED'}

def recurse_radius(node, distance=0.0):
    # Get spring feature properties
    sfp = bpy.context.object.sfp
    # Skip if not mesh
    if node.type != 'MESH': return distance    
    # If vertex distance is larger than distance
    midpos = mathutils.Vector((
        sfp.midpos[0],
        sfp.midpos[2] * -1,
        sfp.midpos[1]))
    offset = mathutils.Vector((
        node.matrix_world[0][3],
        node.matrix_world[1][3],
        node.matrix_world[2][3]))
    offset = offset - midpos

    for i in node.data.vertices:
        myvector = i.co + offset
        if myvector.length > distance:
            distance = myvector.length
    for j in node.children:
        distance = recurse_radius(j, distance)
    return distance

def ov_midpos_calc(self, context):
    # Get spring feature properties
    sfp = bpy.context.object.sfp

    aabb = AABB_recurse(context.active_object)
    centre = (aabb[0] + aabb[1]) * 0.5
    sfp.midpos[0] = centre.x
    sfp.midpos[1] = centre.z
    sfp.midpos[2] = centre.y * -1

def update_footprint(self, context):
    # Get spring feature properties
    sfp = bpy.context.object.sfp

    create_SME_objects(self, context)

    object = bpy.data.objects["SME_footprint"]

    if sfp.footprint:
        object.hide=False
    else:
        object.hide=True

    object.scale.x = sfp.footprintX * 8
    object.scale.y = sfp.footprintZ * 8
    object.location.x = (sfp.footprintX % 2) * -8
    object.location.y = (sfp.footprintZ % 2) * 8

def update_collision_volume(self, context):
    # Get spring feature properties
    sfp = bpy.context.object.sfp

    create_SME_objects(self, context)
    object = bpy.data.objects["SME_collisionvolume"]

    #Change mesh type
    if object.data.name != sfp.collisionVolumeType:
        object.data = bpy.data.meshes[sfp.collisionVolumeType] 

    #Visability
    if sfp.collisionVolume:
        object.hide=False
    else:
        object.hide=True

    if sfp.collisionEditMode == 'grab':
        #Create Drivers
        fcurve = context.object.sfp.driver_add('collisionVolumeScales')
        fcurve[0].driver.expression = "bpy.data.objects['SME_collisionvolume'].scale.x"
        fcurve[1].driver.expression = "bpy.data.objects['SME_collisionvolume'].scale.z"
        fcurve[2].driver.expression = "bpy.data.objects['SME_collisionvolume'].scale.y"
        fcurve = context.object.sfp.driver_add('collisionVolumeOffsets')
        fcurve[0].driver.expression = "bpy.data.objects['SME_collisionvolume'].location.x - bpy.context.object.sfp.midpos[0]"
        fcurve[1].driver.expression = "bpy.data.objects['SME_collisionvolume'].location.z - bpy.context.object.sfp.midpos[1]"
        fcurve[2].driver.expression = "(bpy.data.objects['SME_collisionvolume'].location.y * -1) - bpy.context.object.sfp.midpos[2]"
        #Change attributes
        object.hide_select=False
        for lock in object.lock_location:
            lock=False
        for lock in object.lock_scale:
            lock=False
    else:
        sfp.driver_remove('collisionVolumeScales')
        sfp.driver_remove('collisionVolumeOffsets')
#                context.scene.collisionVolumeOffsets[0] -= context.scene.midpos[0]
        object.select=False
        object.hide_select=True
        for lock in object.lock_location:
            lock=True
        for lock in object.lock_scale:
            lock=True
        object.scale.x = sfp.collisionVolumeScales[0]
        object.scale.y = sfp.collisionVolumeScales[2]
        object.scale.z = sfp.collisionVolumeScales[1]
        object.location.x = sfp.collisionVolumeOffsets[0] + sfp.midpos[0]
        object.location.y = (sfp.collisionVolumeOffsets[2] + sfp.midpos[2]) * -1
        object.location.z = sfp.collisionVolumeOffsets[1] + sfp.midpos[1]

def update_occlusion_volume(self, context):
    # Get spring feature properties
    sfp = bpy.context.object.sfp

    create_SME_objects(self, context)
    object = bpy.data.objects["SME_occlusion"]

    #Visability
    if sfp.occlusionVolume:
        object.hide=False
    else:
        object.hide=True

    if sfp.occlusionEditMode == 'grab':
        #Create drivers so values are updates when model is modified.
        fcurve = sfp.driver_add('radius')
        fcurve.driver.expression = "bpy.data.objects['SME_occlusion'].scale.x"
        fcurve = sfp.driver_add('midpos')
        fcurve[0].driver.expression = "bpy.data.objects['SME_occlusion'].location.x"
        fcurve[1].driver.expression = "bpy.data.objects['SME_occlusion'].location.z"
        fcurve[2].driver.expression = "bpy.data.objects['SME_occlusion'].location.y * -1"
        #change attributes
        object.hide_select = False
        for lock in object.lock_location:
            lock=False
        for lock in object.lock_scale:
            lock=False
    else:
        #Delete drivers
        sfp.driver_remove('radius')
        sfp.driver_remove('midpos')
        #Change Attributes
        object.select=False
        object.hide_select = True
        for lock in object.lock_location:
            lock=True
        for lock in object.lock_scale:
            lock=True
        # Change object transformations
        object.scale.x = object.scale.y = object.scale.z = sfp.radius
        object.location.x = sfp.midpos[0]
        object.location.y = sfp.midpos[2] * -1
        object.location.z = sfp.midpos[1]

def create_SME_objects(self, context):
    active = bpy.context.active_object
    # Get spring feature properties
    sfp = bpy.context.object.sfp

    # Occlusion Mesh and objects
    if not "SME_occlusion" in bpy.data.meshes:
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=12,
            ring_count=12,
            enter_editmode=True)
        bpy.ops.transform.rotate(value=1.5708,axis=(1,0,0))
        bpy.ops.object.editmode_toggle()
        context.active_object.data.name="SME_occlusion"
        bpy.ops.object.delete()

    if not "SME_occlusion" in context.scene.objects:
        object = bpy.data.objects.new(
            name = "SME_occlusion",
            object_data = bpy.data.meshes["SME_occlusion"])
        context.scene.objects.link(object)
        object.show_name=True
        object.draw_type='WIRE'
        object.hide_render=True
        object.hide = True
        for lock in object.lock_rotation:
            lock=True

#Collision Mesh and objects
    if not "SME_box" in bpy.data.meshes:
        bpy.ops.mesh.primitive_cube_add(enter_editmode=True)
        bpy.ops.transform.resize(value=(0.5,0.5,0.5))
        bpy.ops.object.editmode_toggle()
        context.active_object.data.name="SME_box"
        bpy.ops.object.delete()
    if not "SME_ellipsoid" in bpy.data.meshes:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=12,enter_editmode=True)
        bpy.ops.transform.rotate(value=1.5708, axis=(1,0,0))
        bpy.ops.transform.resize(value=(0.5,0.5,0.5))
        bpy.ops.object.editmode_toggle()
        context.active_object.data.name="SME_ellipsoid"
        bpy.ops.object.delete()
    if not "SME_cylX" in bpy.data.meshes:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12,enter_editmode=True)
        bpy.ops.transform.rotate(value=1.5708, axis=(0,1,0))
        bpy.ops.transform.resize(value=(0.5,0.5,0.5))
        bpy.ops.object.editmode_toggle()
        context.active_object.data.name="SME_cylX"
        bpy.ops.object.delete()
    if not "SME_cylY" in bpy.data.meshes:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12,enter_editmode=True)
        bpy.ops.transform.resize(value=(0.5,0.5,0.5))
        bpy.ops.object.editmode_toggle()
        context.active_object.data.name="SME_cylY"
        bpy.ops.object.delete()
    if not "SME_cylZ" in bpy.data.meshes:
        bpy.ops.mesh.primitive_cylinder_add(vertices=12,enter_editmode=True)
        bpy.ops.transform.rotate(value=1.5708, axis=(1,0,0))
        bpy.ops.transform.resize(value=(0.5,0.5,0.5))
        bpy.ops.object.editmode_toggle()
        context.active_object.data.name="SME_cylZ"
        bpy.ops.object.delete()


    if not "SME_collisionvolume" in context.scene.objects:
        object = bpy.data.objects.new(
            name = "SME_collisionvolume",
            object_data = bpy.data.meshes[sfp.collisionVolumeType])
        context.scene.objects.link(object)
        object.show_name=True
        object.draw_type='WIRE'
        object.hide_render=True
        object.hide = True
        for lock in object.lock_rotation:
            lock=True

#footprint Mesh and objects
    if not "SME_footprint" in bpy.data.meshes:
        bpy.ops.mesh.primitive_plane_add()
        context.active_object.data.name="SME_footprint"
        bpy.ops.object.delete()

    if not "SME_footprint" in context.scene.objects:
        object = bpy.data.objects.new(
            name="SME_footprint",
            object_data = bpy.data.meshes["SME_footprint"])
        context.scene.objects.link(object)
        object.select=False
        object.hide_select=True
        object.show_name=True
        object.hide_render=True
        object.hide = True
        for lock in object.lock_rotation:
            lock=True
        for lock in object.lock_scale:
            lock=True
        for lock in object.lock_location:
            lock=True

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.objects.active = active
    active.select = True

    return {'FINISHED'}


