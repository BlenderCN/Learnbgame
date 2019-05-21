import bpy
from ... common_utils import select_obj_exclusive

def apply_modifiers(obj, remove_subsurf_if_last=True):
    if not hasattr(obj, "modifiers"): return None
    select_obj_exclusive(obj)
    for mod in obj.modifiers:
        try:
            if remove_subsurf_if_last and \
               len(obj.modifiers)==1 and \
               mod.type=='SUBSURF':
                bpy.ops.object.modifier_remove(modifier=mod.name)
            else:
                bpy.ops.object.modifier_apply(modifier=mod.name)
        except: #If the modifier is disabled can not be applied and Blender throws an error
            bpy.ops.object.modifier_remove(modifier=mod.name)

def append(context, optimized, high):
    append_meshes(optimized, collection=context.scene.Jet.opt_meshes, link=True)
    append_objects(optimized, collection=context.scene.Jet.opt_high_objs, link=False)

    append_meshes(high, collection=context.scene.Jet.high_meshes, link=True)

    for o in context.scene.Jet.opt_high_objs:
        o.object.Jet.opt_mesh = o.object.data
        for m in context.scene.Jet.high_meshes:
            if o.object.data.name == m.mesh.name:
                o.object.Jet.high_mesh = m.mesh


def append_meshes(blendfile, collection=None, link=False, fake_user=False):
    section = '\\' + 'Mesh' + '\\'
    imported = []

    with bpy.data.libraries.load(blendfile) as (data_from, data_to):
        files = []
        for mesh in data_from.meshes:
            files.append({'name': mesh})
            imported.append(mesh)
        bpy.ops.wm.append(directory=blendfile + section, files=files, link=link, set_fake=True)

    for m in bpy.data.meshes:
        cond = m.name in imported
        if link:
            cond = cond and (hasattr(m, "library")) and (m.library is not None) and (blendfile == m.library.filepath)
        if cond:
            if fake_user:
                m.use_fake_user = True
            if collection is not None:
                item = collection.add()
                item.mesh = m

def append_objects(blendfile, collection=None, link=False, fake_user=False):
    section = '\\' + 'Object' + '\\'
    imported = []

    with bpy.data.libraries.load(blendfile) as (data_from, data_to):
        files = []
        for obj in data_from.objects:
            files.append({'name': obj})
            imported.append(obj)
        bpy.ops.wm.append(directory=blendfile + section, files=files, link=link, set_fake=True)

    not_mesh = []
    for o in bpy.data.objects:
        cond = o.name in imported
        if link:
            cond = cond and (blendfile == o.library.filepath)
        if cond:
            if o.type != 'MESH':
                not_mesh.append(o)
                continue
            if fake_user:
                o.use_fake_user = True
            if collection is not None:
                item = collection.add()
                item.object = o

    for o in not_mesh:
        bpy.data.objects.remove(o, True)

def assign_subsurf(obj, subs=2):
    if obj is None or obj.type != "MESH": return None
    select_obj_exclusive(obj)

    subsurf_list = [m for m in obj.modifiers if m.type == "SUBSURF"]
    n = len(subsurf_list)
    subsurf = subsurf_list[n-1] if (n > 0) else obj.modifiers.new("subsurf_Jet", 'SUBSURF')

    subsurf.show_only_control_edges = True
    subsurf.levels = subs
    subsurf.render_levels = subs

def apply_transform_constraints(obj):
    if obj is None or obj.type != "MESH": return None
    select_obj_exclusive(obj)
    bpy.ops.object.visual_transform_apply()
    for c in reversed(obj.constraints):
        obj.constraints.remove(c)

def clear_parent_transform(obj):
    if obj is None or obj.type != "MESH": return None
    select_obj_exclusive(obj)
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

def assign_decimate(obj, ratio=0.1):
    if obj is None or obj.type != "MESH": return None
    select_obj_exclusive(obj)

    dec_list = [m for m in obj.modifiers if m.type == "DECIMATE"]
    n = len(dec_list)
    dec = dec_list[0] if (n > 0) else obj.modifiers.new("decimate_Jet", 'DECIMATE')

    # Collapse
    dec.decimate_type = 'COLLAPSE'
    dec.ratio = ratio

    # Un-Subdivide
    # dec.decimate_type = 'UNSUBDIV'
    # dec.iterations = 2

    # Planar
    # dec.decimate_type = 'DISSOLVE'
    # dec.angle_limit = 1.309     #75 grados en radianes

def apply_decimate(obj):
    if obj is None or obj.type != "MESH": return None
    select_obj_exclusive(obj)

    for mod in obj.modifiers:
        if mod.type == 'DECIMATE':
            bpy.ops.object.modifier_apply(modifier=mod.name)

def set_decimate_geometry(obj, ratio=0.1):
    if obj is None or obj.type != "MESH": return None
    select_obj_exclusive(obj, edit_mode=True)

    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.decimate(ratio=ratio)

    bpy.ops.object.mode_set(mode="OBJECT")

