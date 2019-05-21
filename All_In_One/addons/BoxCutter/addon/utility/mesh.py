import bpy

from mathutils import Vector

from . import addon, modifier, object


def duplicate(obj, clear_mods=False):
    o = object.duplicate(obj)

    if clear_mods:
        o.modifiers.clear()
        addon.log(value='Cleared duplicate modifiers', indent=2)

    dat = o.to_mesh(bpy.context.depsgraph, apply_modifiers=True)
    dat.bc.removeable = True

    addon.log(value=F'Duplicated {obj.name}\'s data as: {dat.name}', indent=2)

    return dat


class create:
    #TODO: ngon, should start from a single vert placed at 0.0, moved to mouse coords with the update modal screen/ray already
    # ngon is tricky to implement because we dont need/want a lattice for it

    def shape(ot, context, event):
        verts = [
            Vector((-0.5, -0.5, 0.0)), Vector(( 0.5, -0.5, 0.0)),
            Vector((-0.5,  0.5, 0.0)), Vector(( 0.5,  0.5, 0.0))]

        edges = [
            (0, 2), (0, 1),
            (1, 3), (2, 3)]

        faces = [(0, 1, 3, 2)]

        dat = bpy.data.meshes.new(name='Plane')
        dat.bc.removeable = True

        dat.from_pydata(verts, edges, faces)
        dat.validate()

        ot.datablock['plane'] = bpy.data.objects.new(name='Plane', object_data=dat)

        addon.log(value=F'Created normal plane', indent=2)

        if ot.shape == 'BOX':
            verts = [
                Vector((-0.5, -0.5, -0.5)), Vector((-0.5, -0.5,  0.5)),
                Vector((-0.5,  0.5, -0.5)), Vector((-0.5,  0.5,  0.5)),
                Vector(( 0.5, -0.5, -0.5)), Vector(( 0.5, -0.5,  0.5)),
                Vector(( 0.5,  0.5, -0.5)), Vector(( 0.5,  0.5,  0.5))]

            edges = [
                (0, 2), (0, 1), (1, 3), (2, 3),
                (2, 6), (3, 7), (6, 7), (4, 6),
                (5, 7), (4, 5), (0, 4), (1, 5)]

            faces = [
                (0, 1, 3, 2), (2, 3, 7, 6),
                (6, 7, 5, 4), (4, 5, 1, 0),
                (2, 6, 4, 0), (7, 3, 1, 5)]

        elif ot.shape == 'CIRCLE' and ot.mode !='MAKE':
            verts = [
                Vector((0.0, -0.5, -0.5)), Vector((0.0, -0.5,  0.5)),
                Vector((0.0,  0.0, -0.5)), Vector((0.0,  0.0,  0.5))]

            edges = [(0, 2), (0, 1), (1, 3)]

            faces = []

        dat = bpy.data.meshes.new(name='Cutter')

        dat.from_pydata(verts, edges, faces)
        dat.validate()

        ot.datablock['shape'] = bpy.data.objects.new(name='Cutter', object_data=dat)
        ot.datablock['shape'].bc.shape = True
        bpy.data.collections['Cutters'].objects.link(ot.datablock['shape'])

        if ot.mode != 'MAKE':
            ot.datablock['shape'].display_type = 'WIRE'
            ot.datablock['shape'].show_all_edges = True
            ot.datablock['shape'].show_in_front = True

        ot.datablock['shape'].hide_viewport = True

        if addon.preference().auto_smooth:
            ot.datablock['shape'].data.use_auto_smooth = True

            for face in ot.datablock['shape'].data.polygons:
                face.use_smooth = True

        if ot.shape == 'CIRCLE' and ot.mode != 'MAKE':
            dat = bpy.data.meshes.new(name='Cutter display')
            dat.bc.removeable = True

            dat.from_pydata(verts[:-2], edges[1:-1], faces)
            dat.validate()

            dat.bc.simple = True

            ot.datablock['shape_d'] = bpy.data.objects.new(name='Cutter display', object_data=dat)
            bpy.data.collections['Cutters'].objects.link(ot.datablock['shape_d'])

            ot.datablock['shape'].hide_viewport = True
            ot.datablock['shape_d'].display_type = 'WIRE'
            ot.datablock['shape_d'].show_all_edges = True
            ot.datablock['shape_d'].show_in_front = True

            mod = ot.datablock['shape'].modifiers.new(name='Screw', type='SCREW')
            mod.steps = ot.vertices
            mod.use_normal_calculate = True
            mod.use_normal_flip = True
            mod.use_smooth_shade = True
            mod.use_merge_vertices = True

            modifier.duplicate(ot.datablock['shape_d'], mod)

            addon.log(value=F'Created screw modifier for {ot.datablock["shape"].name}', indent=2)

        addon.log(value=F'Created shape type {ot.shape}', indent=2)