import bpy
from mathutils import Vector
D = bpy.data


def tangent_vector(fcurve, frame, df=0.00001):
    v1 = Vector((frame - df, fcurve.evaluate(frame - df), 0))
    v2 = Vector((frame + df, fcurve.evaluate(frame + df), 0))

    return (v2 - v1).normalized()


def sound_surface_texture(action,
                          context,
                          frame_split=1,
                          image_size_x=1024,
                          image_size_y=1024):
    ''' Add a sound surface texture generated from fcurves '''

    scene = context.scene
    img = D.images.new('SoundSurface', image_size_x, image_size_y)

    print(img.name)
    print(len(img.pixels))
    pixels = list(img.pixels)

    # this collects every 4 items in pixels and stores them inside a tuple
    # and sticks all tuples into the grouped_list
    grouped_list = [(0, 0, 0, 1) for ipx in range(0, len(pixels), 4)]

    (rows, cols) = img.size

    print(rows, cols)

    print(action['wavfile'])
    row = []

    fcurves = len(action.fcurves)
    ppc = cols // fcurves
    print("fcurves", fcurves)
    print("ppc", ppc)

    STARTFRAME = 1
    FRAMESPLIT = frame_split
    '''
    rows is frames
    for each row create a temp fcurve
    cols is fcurves
    '''
    for r in range(rows):
        #print("row", r, "_____________________")
        # start point

        for f, fcurve in enumerate(action.fcurves):
            v = scene["xxxx"] = fcurve.evaluate(STARTFRAME + r * frame_split)
            if not f:
                pass
            # create an fcurve row

            # ok I have tan vectors for each of the fcurves
            scene.keyframe_insert('["xxxx"]', frame=ppc * (f + 0.0))

        sfc = scene.animation_data.action.fcurves[0]
        '''
        context.area.type = 'GRAPH_EDITOR'
        #bpy.ops.graph.smooth()
        #bpy.ops.graph.clean(threshold=0.05)
        context.area.type = 'TEXT_EDITOR'
        '''
        sfc.extrapolation = 'CONSTANT'
        for k in range(0, cols):
            e = round(sfc.evaluate(k), 5)
            grouped_list[r * rows + k] = (e, e, e, 1)
            #e = max(min(round(sfc.evaluate(k),5),1),0)
            vi = k // ppc  # fcurve index
            fcurve = action.fcurves[vi]
            lf = k % ppc  # fcurve index
            fac = float(lf / ppc)
            '''
            v1 = tvs[vi]
            v2 = tvs[vi+1]
            v = v1.lerp(v2, fac).normalized()
            sv = tangent_vector(sfc, r*rows+k).zxy
            v = sv.cross(v)
            print(v)
            '''

            #print(k, vi, lf, fac)
            #grouped_list[r*rows + k] = (v[0],v[1],v[2],1)

    flat_list = [i for k in grouped_list for i in k]

    print(grouped_list[0:3])

    img.pixels = flat_list

    del(flat_list)
    del(grouped_list)
action = bpy.data.actions['SoundAction.002']

sound_surface_texture(action,
                      bpy.context,
                      frame_split=1,
                      image_size_x=1024,
                      image_size_y=1024)
