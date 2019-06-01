import bpy

from math import degrees, radians
from mathutils import Vector, Matrix

from bpy.utils import register_class, unregister_class

from . import addon, data, object, lattice, modifier, screen, ray
from . view3d import location2d_to_origin3d, location2d_to_vector3d, location2d_intersect3d, location3d_to_location2d, location2d_to_location3d


class preference:


    def debug(option, context):
        if option.debug: print(F'\n{addon.name} (DEBUG)')
        else: print(F'\n{addon.name} (EXIT)\n')


class property:


    def toolbar(context, prop, value):
        for tool in context.workspace.tools:
            if tool.name == 'BoxCutter':
                setattr(tool.operator_properties('bc.draw_shape'), prop, value)

        context.workspace.tools.update()


class modal:


    def __init__(self, ot, context, event):
        if context.window_manager.bc.running:

            if ot.operation in {'DRAW', 'EXTRUDE', 'OFFSET'}:
                self.lattice(ot, context, event)

            elif ot.operation != 'NONE':
                getattr(self, ot.operation.lower())(ot, context, event)

            if modifier.shape_bool(ot, ot.datablock['targets'][0]):
                self.display_modifiers(ot)

            self.bevel_clamp(ot)


    @staticmethod
    def display_modifiers(ot, display=False):
        if ot.datablock['lattice'].dimensions[2] > 0.01:
            for obj in ot.datablock['targets']:
                if modifier.shape_bool(ot, obj):
                    modifier.shape_bool(ot, obj).show_viewport = ot.live if not display else display

            for obj in ot.datablock['slices']:
                if modifier.shape_bool(ot, obj):
                    modifier.shape_bool(ot, obj).show_viewport = ot.live if not display else display

        else:
            for obj in ot.datablock['targets']:
                if modifier.shape_bool(ot, obj):
                    modifier.shape_bool(ot, obj).show_viewport = display

            for obj in ot.datablock['slices']:
                if modifier.shape_bool(ot, obj):
                    modifier.shape_bool(ot, obj).show_viewport = display


    # TODO replace with shortest bound box 'edge' approach
    # dimensions seems to produce slightly inaccurate results
    @staticmethod
    def bevel_clamp(ot):
        if ot.datablock['lattice'].dimensions[2] > 0.01 and ot.datablock['shape'].data.bc.q_beveled:
            max_distance = (min(ot.datablock['lattice'].dimensions[:]) * 0.5)
        else:
            max_distance = (min(ot.datablock['lattice'].dimensions[:-1]) * 0.5)

        for mod in reversed(ot.datablock['shape'].modifiers):
            if mod.type == 'BEVEL' and ot.operation != 'BEVEL':
                mod.width = ot.last['modifier']['width']

                if mod.width > max_distance:
                    mod.width = max_distance - 0.002 if max_distance > 0.002 else 0.0004

                break

    @staticmethod
    def screen(ot, context, event):
        verts = [Vector((-1000.0, -1000.0, 0.0)), Vector(( 1000.0, -1000.0, 0.0)),
                 Vector((-1000.0,  1000.0, 0.0)), Vector(( 1000.0,  1000.0, 0.0))]

        edges = [(0, 2), (0, 1),
                 (1, 3), (2, 3)]

        faces = [(0, 1, 3, 2)]

        dat = bpy.data.meshes.new(name='Box')
        dat.bc.removeable = True

        dat.from_pydata(verts, edges, faces)
        dat.validate()

        ot.datablock['box'] = bpy.data.objects.new(name='Box', object_data=dat)
        ot.datablock['box'].data.bc.removeable = True

        mod = ot.datablock['box'].modifiers.new(name='Solidify', type='SOLIDIFY')
        mod.thickness = max(dimension for dimension in ot.datablock['dimensions']) * 1.75
        mod.offset = 0

        modifier.apply(obj=ot.datablock['box'], mod=mod)

        ot.datablock['box'].data.transform(context.region_data.view_rotation.to_euler().to_matrix().to_4x4())

        matrix = Matrix()
        matrix.translation = object.center(ot.datablock['duplicate'])

        ot.datablock['box'].data.transform(matrix)

        addon.log(value=F'Created alignment plane', indent=2)

        ot.ray['location'], ot.ray['normal'], ot.ray['index'], ot.ray['distance'] = ray.cast.object(ot, *ot.mouse, objects=[ot.datablock['box']])

        ot.datablock['lattice'].matrix_world = context.region_data.view_rotation.to_euler().to_matrix().to_4x4()
        ot.datablock['lattice'].matrix_world.translation = ot.ray['location']

        ot.datablock['plane'].matrix_world = ot.datablock['lattice'].matrix_world
        ot.datablock['shape'].matrix_world = ot.datablock['lattice'].matrix_world

        if ot.shape == 'CIRCLE' and ot.mode !='MAKE':
            ot.datablock['shape_d'].matrix_world = ot.datablock['lattice'].matrix_world

        if ot.expand:
            for point in getattr(lattice, 'front'):
                ot.datablock['lattice'].data.points[point].co_deform.z -= max(dimension for dimension in ot.datablock['dimensions']) * 1.75

        modal.lattice(ot, context, event, override=True)

        addon.log(value='Moved lattice to screen coords', indent=2)


    @staticmethod
    def ray(ot, context, event):
        track_quat = ot.datablock['duplicate'].data.polygons[ot.ray['index']].normal.to_track_quat('Z', 'Y')
        track_mat = track_quat.to_matrix().to_4x4()
        track_mat.translation = ot.datablock['duplicate'].data.polygons[ot.ray['index']].center

        ot.datablock['lattice'].matrix_world = ot.datablock['duplicate'].matrix_world @ track_mat
        ot.datablock['lattice'].matrix_world.translation = ot.ray['location']

        ot.datablock['plane'].matrix_world = ot.datablock['lattice'].matrix_world
        ot.datablock['shape'].matrix_world = ot.datablock['lattice'].matrix_world

        if ot.shape == 'CIRCLE' and ot.mode !='MAKE':
            ot.datablock['shape_d'].matrix_world = ot.datablock['lattice'].matrix_world

        ot.ray['matrix'] = ot.datablock['lattice'].matrix_world.to_3x3() @ ot.datablock['plane'].data.polygons[0].normal

        addon.log(value='Moved lattice to ray coords', indent=2)

        modal.lattice(ot, context, event, override=True)


    #XXX: needs to be the front corner not rear
    #TODO: mouse offset from target side/origin
    #TODO: break into draw and expand functions
    @staticmethod
    def lattice(ot, context, event, override=False):
        matrix = ot.datablock['lattice'].matrix_world.copy()
        local = matrix.inverted()
        origin = local @ matrix.translation
        offset = ot.start_offset if not ot.mode == 'JOIN' else -ot.start_offset

        location = local @ location2d_to_location3d(event.mouse_region_x, event.mouse_region_y, lattice.center(ot, matrix, side='back'))

        intersect = local @ location2d_intersect3d(
            ot.mouse.x,
            ot.mouse.y,
            lattice.center(ot, matrix, side='front'),
            ot.ray['normal'])

        location = Vector((intersect.x, intersect.y, location.z))

        if ot.operation == 'DRAW' or override:
            index1 = 0 if location.x < origin.x else 1
            sides = ('left', 'right')
            side = sides[index1]
            clear1 = sides[not index1]

            ot.expand_offset = ((0, 2), (1, 3))[index1]

            for point in getattr(lattice, side):
                ot.datablock['lattice'].data.points[point].co_deform.x = location.x

            for point in getattr(lattice, clear1):
                if ot.origin == 'CORNER':
                    ot.datablock['lattice'].data.points[point].co_deform.x = 0

            index2 = 0 if location.y > origin.y else 1 #XXX backwards?
            sides = ('bottom', 'top')
            side = sides[index2]
            clear2 = sides[not index2]

            ot.expand_offset = ot.expand_offset[index2]

            if ot.origin == 'CENTER':
                for point in getattr(lattice, clear1):
                    ot.datablock['lattice'].data.points[point].co_deform.x = -location.x

            for point in getattr(lattice, side):
                if ot.origin == 'CORNER':
                    ot.datablock['lattice'].data.points[point].co_deform.y = location.y
                else:
                    ot.datablock['lattice'].data.points[point].co_deform.y = location.x if index1 != index2 else -location.x

            for point in getattr(lattice, clear2):
                if ot.origin == 'CORNER':
                    ot.datablock['lattice'].data.points[point].co_deform.y = 0
                else:
                    ot.datablock['lattice'].data.points[point].co_deform.y = -location.x if index1 != index2 else location.x

        if ot.operation == 'EXTRUDE':
            if screen.tweak_distance(ot) > context.user_preferences.inputs.tweak_threshold or ot.modified:
                for point in lattice.front:
                    ot.datablock['lattice'].data.points[point].co_deform.z = location.z if origin.z > location.z else -0.0002


    #TODO: offset; move the shape and lattice when points are past origin to prevent flipping, points must be held in place
    # so the inverse transforms of the shape and lattice should be applied to them
    # this keeps the shape and lattice origin at the corner/front center wich is needed for rotate, scale, etc..

    @staticmethod
    def move(ot, context, event):
        matrix = ot.datablock['lattice'].matrix_world.copy()
        local = matrix.inverted()

        mouse_intersect = local @ location2d_intersect3d(
            ot.mouse.x,
            ot.mouse.y,
            lattice.center(ot, matrix, side='front'),
            ot.ray['normal'])

        location = ot.datablock['shape'].matrix_world.to_3x3() @ Vector((mouse_intersect.x, mouse_intersect.y, 0))
        ot.datablock['lattice'].matrix_world.translation += location
        ot.datablock['shape'].matrix_world.translation += location

        if ot.shape == 'CIRCLE' and ot.mode !='MAKE':
            ot.datablock['shape_d'].matrix_world.translation += location


    @staticmethod
    def rotate(ot, context, event):
        pass
        # mouse = ot.mouse - location3d_to_location2d(ot.datablock['lattice'].matrix_world.translation)
        # alpha = ot.last['track'].angle_signed(mouse)

        # ot.track += degrees(alpha)

        # angle = ot.angle
        # if abs(ot.track) > angle:
        #     multiplier = abs(ot.track)//angle
        #     angle = angle * multiplier
        #     alpha = radians(angle) if ot.track > 0 else -radians(angle)
        #     ot.angle += degrees(alpha)
        #     ot.track = 0
        # else:
        #     alpha = 0

        # ot.datablock['lattice'].matrix_world @= Matrix.Rotation(-alpha, 4, ot.axis)
        # ot.datablock['shape'].matrix_world @= Matrix.Rotation(-alpha, 4, ot.axis)

        # ot.last['track'] = mouse


    @staticmethod
    def scale(ot, context, event):
        pass


    @staticmethod
    def array(ot, context, event):
        axis_index = [ot.axis == axis for axis in 'XYZ'].index(True)

        for mod in ot.datablock['shape'].modifiers:
            if mod.type == 'ARRAY':
                break

        if not mod or mod and mod.type != 'ARRAY':
            mod = ot.datablock['shape'].modifiers.new('Array', 'ARRAY')
            mod.count = ot.last['modifier']['count']
            mod.relative_offset_displace[axis_index] = ot.last['modifier']['offset']

            modifier.sort(ot, ot.datablock['shape'])

            if ot.shape == 'CIRCLE' and ot.mode !='MAKE':
                mod = ot.datablock['shape_d'].modifiers.new('Array', 'ARRAY')
                mod.count = ot.last['modifier']['count']
                mod.relative_offset_displace[axis_index] = ot.last['modifier']['offset']

        mods = []
        objects = [ot.datablock['shape']]

        if ot.shape == 'CIRCLE' and ot.mode !='MAKE':
            objects.append(ot.datablock['shape_d'])

        for obj in objects:
            for mod in obj.modifiers:
                if mod.type == 'ARRAY':
                    mods.append(mod)
                    break

        for mod in mods:
            for index, offset in enumerate(mod.relative_offset_displace):
                if index != axis_index:
                    mod.relative_offset_displace[index] = 0

            mod.count = 2 if mod.count < 2 else mod.count
            ot.last['modifier']['count'] = mod.count

            offset = (ot.mouse.x - ot.last['mouse'].x) / screen.dpi_factor()
            factor = 0.001 if event.shift else 0.01
            offset = ot.last['modifier']['offset'] + offset * factor
            mod.relative_offset_displace[axis_index] = offset if not ot.flip else -offset


    @staticmethod
    def bevel(ot, context, event):
        width = (ot.mouse.x - ot.last['mouse'].x) / screen.dpi_factor()
        factor = 0.0001 if event.shift else 0.001


        if ot.datablock['lattice'].dimensions[2] > 0.01 and ot.datablock['shape'].data.bc.q_beveled:
            max_distance = (min(ot.datablock['lattice'].dimensions[:]) * 0.5)
        else:
            max_distance = (min(ot.datablock['lattice'].dimensions[:-1]) * 0.5)

        found = False
        for mod in ot.datablock['shape'].modifiers:
            if mod.type == 'BEVEL':
                found = True

                if mod.segments > 20:
                    mod.segments = 20

                mod.width = ot.last['modifier']['width'] + width * factor if ot.last['modifier']['width'] + width * factor > 0.0004 else 0.0004
                if mod.width > max_distance:
                    mod.width = max_distance - 0.002 if max_distance > 0.002 else 0.0004

                break

        if not found:
            mod = ot.datablock['shape'].modifiers.new(name='Bevel', type='BEVEL')

            if ot.shape == 'BOX':
                ot.datablock['shape'].data.use_customdata_edge_bevel = True

                for index in (1, 3, 6, 9):
                    ot.datablock['shape'].data.edges[index].bevel_weight = 1

                ot.datablock['shape'].data.validate()

            mod.width = ot.last['modifier']['width'] if ot.last['modifier']['width'] > 0.0004 else 0.0004

            mod.segments = ot.last['modifier']['segments']
            mod.use_clamp_overlap = True
            mod.limit_method = 'WEIGHT'


    @staticmethod
    def mode(ot, context, event, to='CUT', init=False):
        from . import modifier

        value = to if to != ot.mode else ot.last['mode']

        if value != to:
            ot.last['mode'] = value

        ot.mode = value
        property.toolbar(context, 'mode', value)

        if value in ['CUT', 'SLICE', 'JOIN']:
            modifier.create.bool(ot)

        elif value == 'KNIFE':

            for obj in ot.datablock['slices']:
                bpy.data.meshes.remove(obj.data)

            ot.datablock['slices'] = []

            for obj in ot.datablock['targets']:
                if modifier.shape_bool(ot, obj):
                    obj.modifiers.remove(modifier.shape_bool(ot, obj))

        if not init:
            modal(ot, context, event)

            ot.report({'INFO'}, '{}{}{}'.format(
                value.title()[:-1 if value in {'SLICE', 'MAKE'} else len(value)] if value != 'KNIFE' else 'Using Knife',
                't' if value == 'CUT' else '',
                'ing' if value != 'KNIFE' else ''))

            addon.log(value=F'Changed mode to {value}', indent=3)


    @staticmethod
    def operation(ot, context, event, to='NONE', modified=True, init=False):
        ot.modified = modified

        value = to

        if ot.operation == 'ARRAY':
            if ot.axis == 'NONE':
                modal.axis(ot, context, to='X')

            axis_index = [ot.axis == axis for axis in 'XYZ'].index(True)

            for mod in ot.datablock['shape'].modifiers:
                if mod.type == 'ARRAY':
                    ot.last['modifier']['offset'] = mod.relative_offset_displace[axis_index]
                    ot.last['modifier']['count'] = mod.count
                    break


        elif ot.operation == 'BEVEL':
            for mod in ot.datablock['shape'].modifiers:
                if mod.type == 'BEVEL':
                    ot.last['modifier']['width'] = mod.width
                    ot.last['modifier']['segments'] = mod.segments
                    break

            ot.last['mouse'] = ot.mouse

        ot.operation = value
        property.toolbar(context, 'operation', value)

        if value == 'ROTATE':
            ot.angle = 0
            ot.last['track'] = ot.mouse - location3d_to_location2d(ot.datablock['lattice'].matrix_world.translation)
            ot.last['mouse'] = ot.mouse
            ot.axis = 'Z' if ot.axis == 'NONE' else ot.axis

        elif value == 'ARRAY':
            if ot.axis == 'NONE':
                modal.axis(ot, context, to='Y')

            axis_index = [ot.axis == axis for axis in 'XYZ'].index(True)

            for mod in ot.datablock['shape'].modifiers:
                if mod.type == 'ARRAY':
                    ot.last['modifier']['offset'] = mod.relative_offset_displace[axis_index]
                    ot.last['modifier']['count'] = mod.count
                    break

        elif value == 'BEVEL':
            for mod in ot.datablock['shape'].modifiers:
                if mod.type == 'BEVEL':
                    ot.last['modifier']['width'] = mod.width
                    ot.last['modifier']['segments'] = mod.segments
                    break

            ot.last['mouse'] = ot.mouse

        if not init:
            if value == 'NONE':
                ot.report({'INFO'}, 'Shape Locked')

            else:
                ot.report({'INFO'}, '{}{}{}'.format(
                    'Added ' if value == 'ARRAY' else '',
                    value.title()[:-1 if value in {'MOVE', 'ROTATE', 'SCALE', 'EXTRUDE'} else len(value)],
                    'ing' if value != 'ARRAY' else ''))

            modal(ot, context, event)
            addon.log(value=F'Changed operation to {value}', indent=3)


    @staticmethod
    def behavior(ot, context, to='DESTRUCTIVE'):
        value = to

        ot.behavior = value
        property.toolbar(context, 'behavior', value)

        addon.log(value=F'Changed behavior to {value}', indent=3)


    @staticmethod
    def origin(ot, context, event, to='CORNER'):
        value = to

        ot.origin = value
        property.toolbar(context, 'origin', value)

        modal(ot, context, event)
        addon.log(value=F'Changed origin to {value}', indent=3)


    @staticmethod
    def axis(ot, context, to='NONE'):
        value = to

        ot.axis = value
        property.toolbar(context, 'axis', value)

        addon.log(value=F'Changed axis to {value}', indent=3)


    @staticmethod
    def mirror(ot, context, event, to='X'):
        value = to

        ot.mirror = True if not ot.mirror else False #TMP
        property.toolbar(context, 'mirror', ot.mirror)

        addon.log(value=F'Added mirror {value[-1].upper()}', indent=3)
