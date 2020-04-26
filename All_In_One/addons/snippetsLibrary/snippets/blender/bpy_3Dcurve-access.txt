def curve3Ddata(ob):
    for spline in ob.data.splines:
        for i, pt in enumerate(spline.bezier_points):
            ## print handler types (in ['FREE', 'VECTOR', 'ALIGNED', 'AUTO', 'AUTO_CLAMPED'], default 'ALIGNED'))
            print(i, 'left:', pt.handle_left_type, '- right:', pt.handle_right_type)

            ## change points coordinates
            # pt.co
            # pt.handle_left
            # pt.handle_right

            ## change handle type
            # pt.handle_left_type = 'AUTO'
            # pt.handle_right_type = 'AUTO'

            ### select methods
            ## select the main central point
            # pt.select_control_point = 1
            # pt.select_left_handle = 1
            # pt.select_right_handle = 1


            ## tilt angle (radians) # needs import math
            # pt.tilt = math.radians(90)

            #weight softbody
            # pt.weight_softbody = 0.0 #default

            ##point radius
            # pt.radius = 1.0#(defautl)


curve3Ddata(bpy.context.object)