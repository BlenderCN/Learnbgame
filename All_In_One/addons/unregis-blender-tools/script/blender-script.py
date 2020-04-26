#!/usr/bin/python3
'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Dieses Programm ist Freie Software: Sie können es unter den Bedingungen
    der GNU General Public License, wie von der Free Software Foundation,
    Version 3 der Lizenz oder (nach Ihrer Wahl) jeder neueren
    veröffentlichten Version, weiter verteilen und/oder modifizieren.

    Dieses Programm wird in der Hoffnung bereitgestellt, dass es nützlich sein wird, jedoch
    OHNE JEDE GEWÄHR,; sogar ohne die implizite
    Gewähr der MARKTFÄHIGKEIT oder EIGNUNG FÜR EINEN BESTIMMTEN ZWECK.
    Siehe die GNU General Public License für weitere Einzelheiten.

    Sie sollten eine Kopie der GNU General Public License zusammen mit diesem
    Programm erhalten haben. Wenn nicht, siehe <https://www.gnu.org/licenses/>.
'''
import bpy
import bmesh
import math
import random
#we are working with a copy of context, so
#that blender doesn't do a scene update on every change
ctx = bpy.context.copy()


def cleanAllDecimateModifiers(obj):
    for m in obj.modifiers:
        if(m.type=="DECIMATE"):
            obj.modifiers.remove(modifier=m)

def mergeMeshes(meshlist):
    if len(meshlist) <= 1:
        print("No objects to join")
        if meshlist:
            return meshlist[0]
        return
    #rename UV maps
    salt = str(random.randint(100, 999))
    uvname = 'UVMap' + salt
    for o in meshlist:
        for uvmap in  o.data.uv_layers :
            uvmap.name = uvname
    #join into active object
    ctx['acive_object'] = meshlist[0]
    ctx['selected_objects'] = meshlist
    ctx['selected_editable_bases'] = [bpy.context.scene.object_bases[o.name] for o in meshlist]
    bpy.ops.object.join(ctx)
    #return joined object
    return meshlist[0]

def mergeMaterials(object):
    textures = []
    ctx['active_object'] = object
    #bpy.context.scene.objects.active  = object
    slot = 0
    nummat = len(object.material_slots)
    print("Checking " + str(nummat) + " materials for possible merge")
    while slot < nummat:
        if object.material_slots[slot].material is None:
            print("No material assigned in slot " + str(slot) + " removing it")
            #bpy.context.object.active_material_index = slot
            ctx.object.active_material_index = slot
            bpy.ops.object.material_slot_remove()
            nummat -= 1
            continue
        texture = getTextureOfMaterialSlot(object.material_slots[slot])
        if texture not in textures:
            textures.append(texture)
            slot += 1
        else:
            ctx['active_object'].active_material_index = slot
            targetslot = textures.index(texture) + 1
            if targetslot != slot:
                print("Have to move slot " + str(slot) + " to " + str(targetslot))
                for _ in range(slot - targetslot):
                    bpy.ops.object.material_slot_move(direction='UP')
            print("Merge slot " + str(targetslot) + " with " + str(targetslot - 1))
            #bpy.context.object.active_material_index = targetslot
            bpy.ops.object.material_slot_remove()
            nummat -= 1
    bpy.context.scene.update()
    return
    
def getTexturesOfObject(object):
    textures = []
    ctx['active_object'] = object
    for matslot in object.material_slots:
        texture = getTextureOfMaterialSlot(matslot)
        print(object.name, 'has material',
            matslot.material.name, 'that uses image',
            texture)
        if texture not in textures:
            textures.append(texture)
    return textures

def getTextureOfMaterialSlot(matslot):
    for texslot in matslot.material.texture_slots:
        if texslot is not None and texslot.texture.type == 'IMAGE':
            if texslot.texture.image is not None:
                return texslot.texture.image.name
                print(object.name, 'has material',
                    matslot.material.name, 'that uses image',
                    texslot.texture.image.name)

def shadeless():
    for item in bpy.data.materials:
        item.use_shadeless = True

def deleteUnusedMaterials():
    for material in bpy.data.materials:
        if not material.users:
            bpy.data.materials.remove(material)

def cleanup(objects):
    #Remove Doubles  and dissolve degenerates in all meshes
    distance = 0.0 #tolerance
    bm = bmesh.new()
    for o in objects:
        bm.from_mesh(o.data)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=distance)
        bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=distance)
        bm.to_mesh(o.data)
        o.data.update()
        bm.clear()
    bm.free()
    
def maketris(objects):
    #Convert to triangles
    for obj in objects:
        bpy.context.scene.objects.active = obj
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all()
        bpy.ops.mesh.quads_convert_to_tris()
        bpy.ops.mesh.select_all()
        bpy.ops.mesh.quads_convert_to_tris()
        bpy.ops.object.editmode_toggle()
    
def makequads(objects):
    #Convert to quads
    for obj in objects:
        bpy.context.scene.objects.active = obj
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all()
        bpy.ops.mesh.tris_convert_to_quads()
        bpy.ops.mesh.select_all()
        bpy.ops.mesh.tris_convert_to_quads()
        bpy.ops.object.editmode_toggle()

def planardec(objects):
    #Planar Decimate in all meshes
    angle = 5
    modifiers = []
    modifierName='DecimateMod'
    for o in objects:
        cleanAllDecimateModifiers(o)
        ctx['acive_object'] = o
        modifier= o.modifiers.new(modifierName,'DECIMATE')
        modifier.decimate_type = 'DISSOLVE'
        modifier.angle_limit = 6.0 * 2 * math.pi / 360
        print("Planar decimate of mesh " + o.name + " by " + str(modifier.angle_limit))
        bpy.ops.object.modifier_apply(modifier=modifier.name)




selectedobj = [o for o in bpy.context.selected_objects if o.type == 'MESH']
allobj = [o for o in bpy.context.scene.objects if o.type == 'MESH']
#shadeless()
#cleanup(allobj)
#mergeMaterials(mergeMeshes(selectedobj))
#allobj = [o for o in bpy.context.scene.objects if o.type == 'MESH']
#planardec(allobj)
#maketris(allobj)
#makequads(allobj)

bpy.context.scene.update()
