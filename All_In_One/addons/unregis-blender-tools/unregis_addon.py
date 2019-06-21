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
bl_info = {
    "name": "unregis AddOn",
    "author": "unregi Resident",
    "description": "Tools for merging and simplifying multiple objects to fit OpenSim / SL",
    "version": (0, 2),
    "category": "Learnbgame",
    "blender": (2, 80, 0),
}

import bpy

import bmesh
import math
import random

icons_dict = {
        "main": {"icon": 'OUTLINER_DATA_CAMERA'},
        "view": {"icon": 'PARTICLEMODE'},
        "merge": {"icon": 'MOD_SOLIDIFY'},
        "physics": {"icon": 'MESH_ICOSPHERE'},
        "cleanup": {"icon": 'MOD_WAVE'},
        "import": {"icon": 'IMPORT'},
}

class UNREGI_OT_slMergeMeshes(bpy.types.Operator):
    """Merge slecte objects"""
    bl_idname = "unregi.mergemesh"
    bl_label = "Merge selected objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        meshlist = [o for o in context.selected_objects if o.type == 'MESH']
        if len(meshlist) <= 1:
            self.report({'WARNING'}, "No multiple meshes to merge selected")
            return {'CANCELLED'}
        ctx = context.copy()
        #rename UV maps
        salt = str(random.randint(100, 999))
        uvname = 'UVMap' + salt
        for o in meshlist:
            for uvmap in  o.data.uv_layers :
                uvmap.name = uvname
        #join into active object
        ctx['acive_object'] = meshlist[0]
        ctx['selected_objects'] = meshlist
        #TODO do we really not need this in 2.80?
        #ctx['selected_editable_bases'] = [context.scene.object_bases[o.name] for o in meshlist]
        bpy.ops.object.join(ctx)
        self.report({'INFO'}, "%d meshes joined" % (len(meshlist),))
        return {'FINISHED'}

class UNREGI_OT_slMergeMaterials(bpy.types.Operator):
    """Merge Materialslots with same texture"""
    bl_idname = "unregi.mergematslot"
    bl_label = "Merge Material slots that use same textures"
    bl_options = {'REGISTER', 'UNDO'}
    diffuse: bpy.props.BoolProperty(name="Unique Diffuse Colors", default=True)

    def getDiffuseColorOfMaterialSlot(self, matslot):
        color = matslot.material.diffuse_color
        return (str(color.r) + str(color.g) + str(color.b))
    
    def getTextureOfMaterialSlot(self, matslot):
        nodes = matslot.material.node_tree.nodes
        if 'Image Texture' in nodes:
            return nodes['Image Texture'].image.name

    def execute(self, context):
        mobject = context.view_layer.objects.active 
        textures = []
        slot = 0
        before_nummat = len(mobject.material_slots)
        nummat = len(mobject.material_slots)
        print("Checking " + str(nummat) + " materials for possible merge")
        while slot < nummat:
            if mobject.material_slots[slot].material is None:
                print("No material assigned in slot " + str(slot) + " removing it")
                context.object.active_material_index = slot
                bpy.ops.object.material_slot_remove()
                nummat -= 1
                continue
            texture = self.getTextureOfMaterialSlot(mobject.material_slots[slot])
            if self.diffuse:
                #if we should care about the color too, just add it to the string
                if texture is None:
                    texture = ""
                texture = texture + self.getDiffuseColorOfMaterialSlot(mobject.material_slots[slot])
            if texture not in textures:
                textures.append(texture)
                slot += 1
            else:
                context.object.active_material_index = slot
                targetslot = textures.index(texture) + 1
                if targetslot != slot:
                    print("Have to move slot " + str(slot) + " to " + str(targetslot))
                    for _ in range(slot - targetslot):
                        bpy.ops.object.material_slot_move(direction='UP')
                print("Merge slot " + str(targetslot) + " with " + str(targetslot - 1))
                bpy.ops.object.material_slot_remove()
                nummat -= 1
        new_nummat = len(mobject.material_slots)
        self.report({'INFO'}, "%d materials merged, %d materials left" % (before_nummat - new_nummat, new_nummat))
        return {'FINISHED'}

class UNREGI_OT_slDeleteUnusedMaterials(bpy.types.Operator):
    """Remove unused Materials"""
    bl_idname = "unregi.remmat"
    bl_label = "Remove Materials that are not used"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        num_deleted = 0
        for material in bpy.data.materials:
            if not material.users:
                num_deleted += 1
                bpy.data.materials.remove(material)
        self.report({'INFO'}, "%d Materials removed" % (num_deleted))
        return {'FINISHED'}

class UNREGI_OT_slDeleteUnusedMaterialslots(bpy.types.Operator):
    """Remove unused Materialslots"""
    bl_idname = "unregi.remmatslot"
    bl_label = "Remove Materialslots that are not used"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        objects = [o for o in context.selected_objects if o.type == 'MESH']
        if not objects:
            self.report({'WARNING'}, "No meshes selected")
            return {'CANCELLED'}
        num_deleted = 0
        for obj in objects:
            faces = obj.data.polygons
            used_material_indices = [0 for n in range(len(faces))]
            faces.foreach_get('material_index', used_material_indices)
            used_material_indices = set(used_material_indices)
            all_slots = set(n for n in range(len(obj.material_slots)))
            unused_slot_indices = all_slots - used_material_indices
            ctx = context.copy()
            ctx['object'] = obj
            unused_slot_indices = list(unused_slot_indices)
            unused_slot_indices.sort(reverse=True)
            for slot_index in unused_slot_indices:
                obj.active_material_index = slot_index
                bpy.ops.object.material_slot_remove(ctx)
                num_deleted += 1
        self.report({'INFO'}, "%d Materialslots removed" % (num_deleted))
        return {'FINISHED'}

class UNREGI_OT_slCleanup(bpy.types.Operator):
    """CleanUp Objects"""
    bl_idname = "unregi.cleanup"
    bl_label = "Remove Doubles and dissolve degenerates in all selected objects"
    bl_options = {'REGISTER', 'UNDO'}
    distance: bpy.props.FloatProperty(name="Distance", default=0.01, min=0.001, max=1.0)

    def execute(self, context):
        objects = [o.data for o in context.selected_objects if o.type == 'MESH']
        if not objects:
            self.report({'WARNING'}, "No meshes selected")
            return {'CANCELLED'}
        num_before = sum(len(m.vertices) for m in objects)
        distance = self.distance / 1000
        bm = bmesh.new()
        for o in objects:
            bm.from_mesh(o)
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=distance)
            bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=distance)
            bm.to_mesh(o)
            o.update()
            bm.clear()
        bm.free()
        num_deleted = num_before - sum(len(m.vertices) for m in objects)
        self.report({'INFO'}, "%d from %d vertices removed" % (num_deleted, num_before))
        return {'FINISHED'}

class UNREGI_OT_slConvexHull(bpy.types.Operator):
    """Convert objects to Convex Hulls"""
    bl_idname = "unregi.convexhull"
    bl_label = "Convert selected objects to Convex Hulls"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    
    def execute(self, context):
        objects = [o for o in context.selected_objects if o.type == 'MESH']
        if not objects:
            self.report({'WARNING'}, "No meshes selected")
            return {'CANCELLED'}
        for obj in objects:
            context.view_layer.objects.active = obj
            #make convex
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.convex_hull()
            bpy.ops.object.mode_set(mode='OBJECT')
            #delete materials
            slot = 0
            nummat = len(obj.material_slots)
            while slot < nummat:
                bpy.ops.object.material_slot_remove()
                slot += 1
        return {'FINISHED'}

class UNREGI_OT_slMakeTris(bpy.types.Operator):
    """Convert to Triangles"""
    bl_idname = "unregi.maketris"
    bl_label = "Convert selected objects to triangles"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    
    def execute(self, context):
        objects = [o for o in context.selected_objects if o.type == 'MESH']
        if not objects:
            self.report({'WARNING'}, "No meshes selected")
            return {'CANCELLED'}
        num_before = sum(len(m.data.polygons) for m in objects)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.quads_convert_to_tris()
        bpy.ops.object.mode_set(mode='OBJECT')
        num_after = sum(len(m.data.polygons) for m in objects)
        self.report({'INFO'}, "Conversion from %d to %d faces" % (num_before, num_after))
        return {'FINISHED'}
    
class UNREGI_OT_slMakeQuads(bpy.types.Operator):
    """Convert Triangles to Quads"""
    bl_idname = "unregi.makequads"
    bl_label = "Convert selected objects to quads"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    
    def execute(self, context):
        objects = [o for o in context.selected_objects if o.type == 'MESH']
        if not objects:
            self.report({'WARNING'}, "No meshes selected")
            return {'CANCELLED'}
        num_before = sum(len(m.data.polygons) for m in objects)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.tris_convert_to_quads()
        bpy.ops.object.mode_set(mode='OBJECT')
        num_after = sum(len(m.data.polygons) for m in objects)
        self.report({'INFO'}, "Conversion from %d to %d faces" % (num_before, num_after))
        return {'FINISHED'}

class UNREGI_OT_slDeleteLoose(bpy.types.Operator):
    """Delete Loose Vertices / Edges / Faces"""
    bl_idname = "unregi.deleteloose"
    bl_label = "Delete loose vertices, edges and faces"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    
    def execute(self, context):
        objects = [o for o in context.selected_objects if o.type == 'MESH']
        if not objects:
            self.report({'WARNING'}, "No meshes selected")
            return {'CANCELLED'}
        num_before = sum(len(m.data.vertices) for m in objects)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.delete_loose(use_faces=True)
        bpy.ops.object.mode_set(mode='OBJECT')
        num_deleted = num_before - sum(len(m.data.vertices) for m in objects)
        self.report({'INFO'}, "%d from %d vertices removed" % (num_deleted, num_before))
        return {'FINISHED'}

class UNREGI_OT_slPlanarDecimate(bpy.types.Operator):
    """Planar Decimate Objects"""
    bl_idname = "unregi.planardec"
    bl_label = "Planar Decimate over selected objects"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    angle: bpy.props.IntProperty(name="Max Angle", default=5, min=0, max=25)
    
    def execute(self, context):
        angle_radian = self.angle * 2 * math.pi / 360
        objects = [o for o in context.selected_objects if o.type == 'MESH']
        if not objects:
            self.report({'WARNING'}, "No meshes selected")
            return {'CANCELLED'}
        num_before = 0
        num_after = 0
        for obj in objects:
            num_before += len(obj.data.vertices)
            context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.dissolve_limited(angle_limit=angle_radian, delimit={'NORMAL'})
            bpy.ops.object.mode_set(mode='OBJECT')
            num_after += len(obj.data.vertices)
        self.report({'INFO'}, "%d from %d vertices removed" % (num_before - num_after, num_before))
        return {'FINISHED'}

class UNREGI_OT_slDecimate(bpy.types.Operator):
    """Decimate Objects"""
    bl_idname = "unregi.decimate"
    bl_label = "Decimate over selected objects"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    ratio: bpy.props.FloatProperty(name="Ratio", default=0.2, min=0.0, max=1.0)

    def cleanAllDecimateModifiers(self, obj):
        for m in obj.modifiers:
            if(m.type=="DECIMATE"):
                obj.modifiers.remove(modifier=m)
 
    def execute(self, context):
        objects = [o for o in context.selected_objects if o.type == 'MESH']
        if not objects:
            self.report({'WARNING'}, "No meshes selected")
            return {'CANCELLED'}
        num_before = 0
        num_after = 0
        for obj in objects:
            num_before += len(obj.data.vertices)
            context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.decimate(ratio=self.ratio, use_vertex_group=False)
            bpy.ops.object.mode_set(mode='OBJECT')
            num_after += len(obj.data.vertices)
        self.report({'INFO'}, "%d from %d vertices removed" % (num_before - num_after, num_before))
        return {'FINISHED'}

class UNREGI_OT_slDaeImport(bpy.types.Operator):
    """Import Collada File"""
    bl_idname = "unregi.daeimport"
    bl_label = "Import Collada"
    bl_options = {'UNDO', 'INTERNAL'}
    import_units: bpy.props.BoolProperty(name="Import Units", default=False)
    fix_orientation: bpy.props.BoolProperty(name="Fix orientation", default=False)
    find_chains: bpy.props.BoolProperty(name="Find chains", default=False)
    auto_connect: bpy.props.BoolProperty(name="Auto connect", default=False)
    min_chain_length: bpy.props.IntProperty(name="min chain length", default=0, min=0)
    keep_bind_info: bpy.props.BoolProperty(name="Keep bind info", default=False)

    filename_ext = ".dae"
    filepath: bpy.props.StringProperty(name = "Filepath", subtype = "FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.dae", options={'HIDDEN'})

    def execute(self, context):
        bpy.ops.wm.collada_import(filepath=self.filepath, keep_bind_info=self.keep_bind_info, import_units=self.import_units, fix_orientation=self.fix_orientation, find_chains=self.find_chains, auto_connect=self.auto_connect, min_chain_length=self.min_chain_length)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class UNREGI_PT_menuButton(bpy.types.Panel):
    bl_idname = "UNREGI_PT_menuButton"
    bl_label = "unregis Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout
        layout.menu('UNREGI_MT_mainMenu', **icons_dict["main"],  text='unregis Tools')

class UNREGI_MT_mainMenu(bpy.types.Menu):
    bl_idname = "UNREGI_MT_mainMenu"
    bl_label = "unregis Tools"

    def draw(self, context):
        layout = self.layout
        layout.label(text='unregis Tools')
        layout.separator()
        layout.label(text='View', **icons_dict["view"])
        num_mesh_selected = sum(1 for o in context.selected_objects if o.type == 'MESH')
        if num_mesh_selected:
            layout.operator('unregi.remmatslot', text='Remove unused Materialslots')
            layout.label(text='Merge', **icons_dict["merge"])
            if num_mesh_selected > 1:
                layout.operator('unregi.mergemesh', text='Merge Objects')
            layout.operator('unregi.mergematslot', text='Merge Same Materials')
            layout.label(text='Physics Shape', **icons_dict["physics"])
            layout.operator('unregi.convexhull', text='Create Convex Hulls')
            layout.operator('unregi.decimate', text='Decimate')
            layout.label(text='CleanUp', **icons_dict["cleanup"])
            layout.operator('unregi.cleanup', text='Remove Doubles and Degenerates')
            layout.operator('unregi.deleteloose', text='Delete Loose')
            layout.operator('unregi.planardec', text='Planar Decimate')
            layout.operator('unregi.maketris', text='Convert to Triangles')
            layout.operator('unregi.makequads', text='Triangles to Quads')
        else:
            layout.operator('unregi.remmat', text='Remove unused Materials')
            layout.label(text='Import/Export', **icons_dict["import"])
            layout.operator('unregi.daeimport', text='Import Collada')

classes = (
    UNREGI_OT_slMakeTris,
    UNREGI_OT_slMakeQuads,
    UNREGI_OT_slCleanup,
    UNREGI_OT_slPlanarDecimate,
    UNREGI_OT_slMergeMaterials,
    UNREGI_OT_slDeleteUnusedMaterials,
    UNREGI_OT_slDeleteUnusedMaterialslots,
    UNREGI_OT_slMergeMeshes,
    UNREGI_OT_slConvexHull,
    UNREGI_OT_slDecimate,
    UNREGI_OT_slDeleteLoose,
    UNREGI_OT_slDaeImport,
    UNREGI_MT_mainMenu,
    UNREGI_PT_menuButton,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == '__main__':
    register()

