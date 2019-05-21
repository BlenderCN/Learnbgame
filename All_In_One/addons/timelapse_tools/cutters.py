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

import bpy
from mathutils import Matrix, Vector, Quaternion

cutter_controls_layer = 12
cutter_meshes_layer = 13


def decide(ob):
    """ Return true of an object or it's ultimate parent is animated """
    if ob.animation_data and ob.animation_data.action and [
            fc for fc in ob.animation_data.action.fcurves
            if any(itm in fc.data_path for itm in ('location', 'rotation'))]:
        return True
    if ob.parent and decide(ob.parent): return True
    return False


def is_tile_group(group):
    """ Return True if an object is a tile group """
    name = group if type(group) == str else group.name
    if not name.startswith('T_'): return False
    if name.endswith('_C_') or not '_C_' in name: return False
    return name[2:].replace('_C_', '').isnumeric()


def tile_max():
    """ Return Next Available Tile Number"""
    groups = [group.name for group in bpy.data.groups if is_tile_group(group)]
    if not groups: return 0
    return max(int(group[2:].split('_C_')[0]) for group in groups) + 1


def cell_max(tile):
    """ Return Next Available Cell Number"""
    groups =(group.name for group in bpy.data.groups if is_tile_group(group))
    cells = [group for group in groups if int(group[2:].split('_C_')[0]) == tile]
    if not cells: return 0
    return max(int(group[2:].split('_C_')[-1]) for group in cells) + 1


def make_empty(context, name, location=(0,0,0)):
    """ Make an empty at the location required """
    empty = bpy.data.objects.new(name=name, object_data=None)
    empty.layers = context.scene.layers
    empty_base = context.scene.objects.link(empty)
    empty.location = Vector(location)
    empty_base.layers_from_view(context.area.spaces[0])
    return empty


def make_boolean_group(ob, group_name):
    """ Place object into group group_name """
    group = bpy.data.groups.new(name=group_name)
    group.objects.link(ob)
    group["main_mesh"] = ob.name
    ob["boolean_group"] = group.name
    return group


def transform_clear(ob):
    ob.matrix_parent_inverse = Matrix()
    ob.location = ob.rotation_euler = Vector((0,0,0))
    ob.rotation_quaternion = Quaternion((1,0,0,0))


def make_object_parent(context, group, ob):
    """ remap materials for selected objects to workaround boolean issues """
    if not ob.parent:
        empty = make_empty(context, "{}_parent".format(group.name))
        empty.empty_draw_type = 'ARROWS'
        empty.animation_data_create()
        if ob.animation_data and ob.animation_data.action:
            empty.animation_data.action = ob.animation_data.action
        else:
            empty.matrix_world = ob.matrix_world.copy()
        ob.animation_data_clear()
        ob.parent = empty
        transform_clear(ob)
        ob.lock_location = ob.lock_rotation = ob.lock_scale =  [True] * 3
        ob.lock_rotation_w = True
    else:
        empty = ob.parent
    group.objects.link(empty)
    group["parent"] = empty.name
    return empty


def make_object_texaco(context, group, ob):
    texaco = make_empty(context, "{}_texaco".format(group.name))
    texaco.parent = ob.parent
    texaco.empty_draw_type = 'CUBE'
    texaco.empty_draw_size = 0.081292
    texaco.parent = ob.parent
    transform_clear(texaco)
    texaco.scale = Vector([2.778307,2.778307,2.778307])
    for i, slot in enumerate(ob.material_slots):
        slot.material = slot.material.copy()
        if i == 0: slot.material.name = "surface_{}".format(group.name)
        if i == 1: slot.material.name = "broken_{}".format(group.name)
        slot.material.node_tree.nodes["Texture Coordinate"].object = texaco
    group.objects.link(texaco)
    group["texaco"] = texaco.name
    return texaco


class BooleanState(bpy.types.Operator):
    """ Change Bool modifiers to Rendered/Preview/None """

    bl_idname = "object.boolean_state"
    bl_label = "Change Boolean Modifier State"

    state = bpy.props.EnumProperty(items = [
        ("NONE", "None", "Turn Off Booleans"),
        ("PREVIEW", "Preview", "Preview Only Booleans"),
        ("RENDER", "Render", "Render mode Booleans")])

    def execute(self, context):
        state = self.properties.state
        for ob in context.selected_objects:
            for modifier in ob.modifiers:
                if modifier.type == "BOOLEAN":
                    if state == 'NONE':
                        modifier.show_viewport = False
                    elif state == 'PREVIEW':
                        modifier.show_viewport = not modifier.show_render
                    elif state == 'RENDER':
                        modifier.show_viewport = modifier.show_render
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_props_dialog(self, 250)
        return {'RUNNING_MODAL'}


def get_groups(self, context):
    ob = context.active_object
    groups = (grp.name for grp in bpy.data.groups if ob in grp.objects.values())
    return [tuple([grp] * 3) for grp in groups]


class RenameTiles(bpy.types.Operator):
    """Remap material to empty to avoid boolean glitch"""
    bl_idname = "object.rename_tiles"
    bl_label = "Rename Tile Based in Group Name"

    group = bpy.props.EnumProperty(items=get_groups)
    rename = bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        rename = self.properties.rename
        grp = bpy.data.groups[self.properties.group]
        parents = [
            ob for ob in grp.objects.values()
            if not ob.parent or ob.parent not in grp.objects.values()]
        if len(parents) != 1:
            self.report({'WARNING'}, "Parent Trap!")
            return {'CANCELLED'}
        parent = parents[0]
        if parent.type != 'EMPTY':
            self.report({'WARNING'}, "Non Empty Parent!")
            return {'CANCELLED'}
        parent.name = "{}_parent".format(grp.name) # Ultimate Parent
        grp["parent"] = parent.name
        mainblocks = [
            ob for ob in grp.objects.values()
            if ob.parent == parent and ob.type == 'MESH']
        if len(mainblocks) != 1:
            self.report({'WARNING'}, "Block Count should be 1!")
            return {'CANCELLED'}
        mainblock = mainblocks[0]
        mainblock["boolean_group"] = self.properties.group
        if rename:
            mainblock.name = mainblock.data.name = grp.name
        grp["main_mesh"] = mainblock.name
        texacos = [ob for ob in grp.objects.values() if 'texaco' in ob.name]
        if len(texacos) > 1:
            self.report({'WARNING'}, "There can only be one texaco")
            return {'CANCELLED'}
        if texacos:
            texaco = texacos[0]
            texaco.name = "texaco_{}".format(grp.name)
        else:
            texaco = make_object_texaco(context, grp, mainblock)
        grp["texaco"] = texaco.name
        cutter_datas = list(set([
            ob.data for ob in grp.objects.values()
            if ob.type == 'MESH' and ob not in (mainblock, parent)]))
        for cutter_data in cutter_datas:
            my_cutters = (
                ob for ob in grp.objects.values() if ob.data == cutter_data)
            for index, ob in enumerate(my_cutters):
                # cutter mesh HI/LO gets GROUPNAME_DATANAME_INDEX
                ob.name = "{}_{}_{}".format(grp.name, cutter_data.name, index)
                # cutter motion empty gets GROUPNAME_CUTTERNAME_time_INDEX
                ob.parent.name = "{}_{}_time_{}".format(
                    grp.name, cutter_data.name[:-3], index)
                # cutter orient empty gets GROUPNAME_CUTTERNAME_orient_INDEX
                ob.parent.parent.name = "{}_{}_orient_{}".format(
                    grp.name, cutter_data.name[:-3], index)
                ob.material_slots[0].link = 'OBJECT'
                ob.material_slots[0].material = mainblock.material_slots[1].material
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_props_dialog(self, 250)
        return {'RUNNING_MODAL'}


def fix_texture_maps(ob):
    """ fix mapping of texacos because well, they weren't good before """
    if ob.name.startswith('texaco'):
        grps = [g for g in bpy.data.groups if ob in g.objects.values()]
        if grps:
            grp = grps[0]
            meshes = [ob for ob in grp.objects if ob.type == 'MESH']
            mats = set()
            for mesh in meshes:
                for slot in mesh.material_slots:
                    if slot.material:
                        mats.add(slot.material)
            mats = {mat.name: mat for mat in mats}
            for mat in mats:
                mapnode = mats[mat].node_tree.nodes['Texture Coordinate']
                if mapnode.object == ob:
                    print('bingo')
                else:
                    matnew = mats[mat].copy()
                    matnew.node_tree.nodes['Texture Coordinate'].object = ob
                    mats[mat] = matnew
                    print('wawa')
            for mesh in meshes:
                for slot in mesh.material_slots:
                    slot.material = mats[slot.material.name]
            for mat in mats:
                if 'broken' in mat:
                    mats[mat].name = "broken_{}".format(grp.name)
                else:
                    mats[mat].name = "surface_{}".format(grp.name)


def get_cutters(self, context):
    cutters = list(set([
        ob.data.name[:-3] for ob in bpy.data.groups["CUTTERS"].objects]))
    cutters.sort()
    return [tuple([cutter] * 3 + [i]) for i, cutter in enumerate(cutters)]


class CutterAdd(bpy.types.Operator):
    """Boolean cutter, low and hi rez, parented by move and orient empties """
    bl_idname = 'object.cutter_add'
    bl_label = 'Add Boolean Cutter'

    cutter = bpy.props.EnumProperty(items=get_cutters)
    tile = bpy.props.IntProperty(
        default=0, name='tile number', description='which tile')
    digits = bpy.props.IntProperty(
        default=4, name="padding", description="how many digits to pad")
    rename = bpy.props.BoolProperty(
        default=False, name="Rename Mesh",
        description="Rename Object Mesh for Consistency")

    @classmethod
    def poll(cls, context):
        return (
            context.object and context.object.type == 'MESH' and
            context.mode == 'OBJECT')

    def execute(self, context):
        # Setup variables for later in function
        ob = context.object
        scene = context.scene
        location = context.area.spaces[0].cursor_location
        cutter_type = self.properties.cutter
        tile = self.properties.tile
        cutter_group = bpy.data.groups["CUTTERS"]
        cutters = [
            cutter for cutter in cutter_group.objects.values()
            if cutter.name[:-3] == cutter_type and
            cutter.name[-3:] in ('_HI', '_LO')]
        cutters.sort(key=lambda x: x.name[-3:]) # HI first

        if "boolean_group" in ob.keys():
            ob_group = bpy.data.groups[ob["boolean_group"]]
            parent = scene.objects[ob_group["parent"]]
            texaco = scene.objects[ob_group["texaco"]]
        else:
            group_name = "T_{0:{f}{w}d}_C_{1:{f}{w}d}".format(
                tile, cell_max(tile), f='0', w=self.digits)
            ob_group = make_boolean_group(ob, group_name)
            parent = make_object_parent(context, ob_group, ob)
            texaco = make_object_texaco(context, ob_group, ob)

        # determine broken texture from object, or create if not exist
        if len(ob.material_slots) > 1 and ob.material_slots[1].material:
            broken = ob.material_slots[1].material
        else:
            broken = cutters[0].material_slots[0].material.copy()
            broken.name = "broken_{}".format(ob_group.name)
            broken.node_tree.nodes['Texture Coordinate'].object = texaco
            bpy.ops.object.material_slot_add()
            ob.material_slots[1].material = broken
        # count existing cutters of our type:
        extant = [
            ob for ob in ob_group.objects
            if ob.type=="MESH" and ob.data == cutters[0].data]
        new_index = len(extant)
        prefix = "{}_{}".format(ob_group.name, cutter_type)
        # create orient empty and place
        orient = make_empty(
            context, "{}_orient_{}".format(prefix, new_index), location)
        orient.empty_draw_type = 'SINGLE_ARROW'
        orient.parent = parent
        orient.matrix_parent_inverse = parent.matrix_world.inverted()
        ob_group.objects.link(orient)
        # create time empty and parent to orient
        time = make_empty(
            context, "{}_time_{}".format(prefix, new_index))
        time.empty_draw_type = 'SPHERE'
        time.empty_draw_size = 0.3
        time.parent = orient
        transform_clear(time)
        time.layers = orient.layers = [
            l == cutter_controls_layer for l in range(20)]
        ob_group.objects.link(time)
        # for mesh HI and mesh LO:

        for cutter in cutters:
            suffix = cutter.name[-3:]
            nc = cutter.copy()
            if nc not in scene.objects.values():
                nc_base = scene.objects.link(nc)
                nc_base.layers_from_view(context.area.spaces[0])
            nc.layers = [l == cutter_meshes_layer for l in range(20)]
            nc.name = "{}{}_{}".format(prefix, suffix, new_index)
            nc.parent = time
            nc.matrix_basis = nc.matrix_parent_inverse = Matrix()
            for mod in nc.modifiers:
                if mod.type == 'DISPLACE':
                    mod.texture_coords_object = parent
            nc.material_slots[0].material = broken
            nc.scale = cutter.scale
            bool = ob.modifiers.new(name='', type='BOOLEAN')
            bool.object = nc
            bool.operation = 'DIFFERENCE'
            bool.name = "{}_{}".format(nc.data.name, new_index)
            # set bool settings
            if cutter.name.endswith('HI'):
                bool.show_viewport = False
                bool.show_render = True
            else:
                bool.show_viewport = True
                bool.show_render = False
            ob_group.objects.link(nc)

        # modify the context for ease of use
        ob.select = False
        orient.select = True
        scene.objects.active = orient
        scene.layers[cutter_controls_layer] =  True
        scene.layers[cutter_meshes_layer] = True
        return {'FINISHED'}

    def invoke(self, context, event):
        try:
            cutter_group = bpy.data.groups["CUTTERS"]
        except KeyError:
            self.report({'ERROR'}, "Import or create CUTTERS group!")
            return {'CANCELLED'}
        self.properties.tile = tile_max()
        context.window_manager.invoke_props_dialog(self, 250)
        return {'RUNNING_MODAL'}

def menu_func(self, context):
    layout = self.layout
    row = layout.row()
    row.operator_context = 'INVOKE_DEFAULT'
    row.operator(CutterAdd.bl_idname, text="Add Cutter", icon="PLUGIN")
    layout.separator()


def register():
    bpy.utils.register_class(BooleanState)
    bpy.utils.register_class(RenameTiles)
    bpy.utils.register_class(CutterAdd)
    bpy.types.VIEW3D_MT_add.prepend(menu_func)


def unregister():
    bpy.utils.unregister_class(BooleanState)
    bpy.utils.unregister_class(RenameTiles)
    bpy.utils.unregister_class(CutterAdd)
    bpy.types.VIEW3D_MT_add.remove(menu_func)

if __name__ == '__main__':
    register()
