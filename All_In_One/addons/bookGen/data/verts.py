def get_verts(page_thickness, page_height, cover_depth, cover_height, cover_thickness, page_depth, hinge_inset, hinge_width, spline_curl):
    return [
    # cover right side
        [ page_thickness / 2 + cover_thickness,                -cover_depth / 2,                                                 cover_height / 2],
        [ page_thickness / 2 + cover_thickness,                 cover_depth / 2,                                                 cover_height / 2],
        [ page_thickness / 2 + cover_thickness,                -cover_depth / 2,                                                -cover_height / 2],
        [ page_thickness / 2 + cover_thickness,                 cover_depth / 2,                                                -cover_height / 2],

        [ page_thickness / 2,                                  -cover_depth / 2,                                                 cover_height / 2],
        [ page_thickness / 2,                                   cover_depth / 2,                                                 cover_height / 2],
        [ page_thickness / 2,                                  -cover_depth / 2,                                                -cover_height / 2],
        [ page_thickness / 2,                                   cover_depth / 2,                                                -cover_height / 2],

    # cover left side
        [-page_thickness / 2 - cover_thickness,                -cover_depth / 2,                                                 cover_height / 2],
        [-page_thickness / 2 - cover_thickness,                 cover_depth / 2,                                                 cover_height / 2],
        [-page_thickness / 2 - cover_thickness,                -cover_depth / 2,                                                -cover_height / 2],
        [-page_thickness / 2 - cover_thickness,                 cover_depth / 2,                                                -cover_height / 2],

        [-page_thickness / 2,                                  -cover_depth / 2,                                                 cover_height / 2],
        [-page_thickness / 2,                                   cover_depth / 2,                                                 cover_height / 2],
        [-page_thickness / 2,                                  -cover_depth / 2,                                                -cover_height / 2],
        [-page_thickness / 2,                                   cover_depth / 2,                                                -cover_height / 2],

    # pages
        [ page_thickness / 2,                                  -page_depth / 2,                                                  page_height / 2],
        [ page_thickness / 2,                                   page_depth / 2,                                                  page_height / 2],
        [ page_thickness / 2,                                  -page_depth / 2,                                                 -page_height / 2],
        [ page_thickness / 2,                                   page_depth / 2,                                                 -page_height / 2],

        [-page_thickness / 2,                                  -page_depth / 2,                                                  page_height / 2],
        [-page_thickness / 2,                                   page_depth / 2,                                                  page_height / 2],
        [-page_thickness / 2,                                  -page_depth / 2,                                                 -page_height / 2],
        [-page_thickness / 2,                                   page_depth / 2,                                                 -page_height / 2],

    # hinge right
        [ page_thickness / 2 + cover_thickness - hinge_inset,  -cover_depth / 2 - hinge_width / 2,                               cover_height / 2],
        [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width / 2,                               cover_height / 2],
        [ page_thickness / 2 + cover_thickness - hinge_inset,  -cover_depth / 2 - hinge_width / 2,                              -cover_height / 2],
        [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width / 2,                              -cover_height / 2],

        [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width,                                   cover_height / 2],
        [ page_thickness / 2 + cover_thickness,                -cover_depth / 2 - hinge_width,                                   cover_height / 2],
        [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width,                                  -cover_height / 2],
        [ page_thickness / 2 + cover_thickness,                -cover_depth / 2 - hinge_width,                                  -cover_height / 2],

    # hinge left
        [-page_thickness / 2 - cover_thickness + hinge_inset,  -cover_depth / 2 - hinge_width / 2,                               cover_height / 2],
        [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width / 2,                               cover_height / 2],
        [-page_thickness / 2 - cover_thickness + hinge_inset,  -cover_depth / 2 - hinge_width / 2,                              -cover_height / 2],
        [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width / 2,                              -cover_height / 2],

        [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width,                                   cover_height / 2],
        [-page_thickness / 2 - cover_thickness,                -cover_depth / 2 - hinge_width,                                   cover_height / 2],
        [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width,                                  -cover_height / 2],
        [-page_thickness / 2 - cover_thickness,                -cover_depth / 2 - hinge_width,                                  -cover_height / 2],

    # spline right
        [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width - cover_thickness,                 cover_height / 2],
        [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width - cover_thickness,                -cover_height / 2],

    # spline left
        [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width - cover_thickness,                 cover_height / 2],
        [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width - cover_thickness,                -cover_height / 2],

    # spline center
        [0,                                                    -cover_depth / 2 - hinge_width - spline_curl - cover_thickness,   cover_height / 2],
        [0,                                                    -cover_depth / 2 - hinge_width - spline_curl,                     cover_height / 2],
        [0,                                                    -cover_depth / 2 - hinge_width - spline_curl - cover_thickness,  -cover_height / 2],
        [0,                                                    -cover_depth / 2 - hinge_width - spline_curl,                    -cover_height / 2],

    # pages proximity loops
        [-page_thickness / 2,                                  -page_depth / 2 + page_depth / 100,                               page_height / 2],
        [ page_thickness / 2,                                  -page_depth / 2 + page_depth / 100,                               page_height / 2],
        [-page_thickness / 2,                                   page_depth / 2 - page_depth / 100,                               page_height / 2],
        [ page_thickness / 2,                                   page_depth / 2 - page_depth / 100,                               page_height / 2],

        [-page_thickness / 2,                                  -page_depth / 2 + page_depth / 100,                              -page_height / 2],
        [ page_thickness / 2,                                  -page_depth / 2 + page_depth / 100,                              -page_height / 2],
        [-page_thickness / 2,                                   page_depth / 2 - page_depth / 100,                              -page_height / 2],
        [ page_thickness / 2,                                   page_depth / 2 - page_depth / 100,                              -page_height / 2],

        [-page_thickness / 2 + page_thickness / 100,           -page_depth / 2,                                                 -page_height / 2],
        [ page_thickness / 2 - page_thickness / 100,           -page_depth / 2,                                                 -page_height / 2],
        [-page_thickness / 2 + page_thickness / 100,            page_depth / 2,                                                 -page_height / 2],
        [ page_thickness / 2 - page_thickness / 100,            page_depth / 2,                                                 -page_height / 2],

        [-page_thickness / 2 + page_thickness / 100,           -page_depth / 2,                                                  page_height / 2],
        [ page_thickness / 2 - page_thickness / 100,           -page_depth / 2,                                                  page_height / 2],
        [-page_thickness / 2 + page_thickness / 100,            page_depth / 2,                                                  page_height / 2],
        [ page_thickness / 2 - page_thickness / 100,            page_depth / 2,                                                  page_height / 2],

        [-page_thickness / 2,                                  -page_depth / 2,                                                  page_height / 2 - page_height / 100],
        [ page_thickness / 2,                                  -page_depth / 2,                                                  page_height / 2 - page_height / 100],
        [-page_thickness / 2,                                   page_depth / 2,                                                  page_height / 2 - page_height / 100],
        [ page_thickness / 2,                                   page_depth / 2,                                                  page_height / 2 - page_height / 100],

        [-page_thickness / 2,                                  -page_depth / 2,                                                 -page_height / 2 + page_height / 100],
        [ page_thickness / 2,                                  -page_depth / 2,                                                 -page_height / 2 + page_height / 100],
        [-page_thickness / 2,                                   page_depth / 2,                                                 -page_height / 2 + page_height / 100],
        [ page_thickness / 2,                                   page_depth / 2,                                                 -page_height / 2 + page_height / 100],

    # cover proximity loops
        [ page_thickness / 2 + cover_thickness,                -cover_depth / 2,                                                 cover_height / 2 - cover_height / 100],
        [ page_thickness / 2 + cover_thickness,                 cover_depth / 2,                                                 cover_height / 2 - cover_height / 100],
        [ page_thickness / 2 + cover_thickness,                -cover_depth / 2,                                                -cover_height / 2 + cover_height / 100],
        [ page_thickness / 2 + cover_thickness,                 cover_depth / 2,                                                -cover_height / 2 + cover_height / 100],

        [ page_thickness / 2,                                  -cover_depth / 2,                                                 cover_height / 2 - cover_height / 100],
        [ page_thickness / 2,                                   cover_depth / 2,                                                 cover_height / 2 - cover_height / 100],
        [ page_thickness / 2,                                  -cover_depth / 2,                                                -cover_height / 2 + cover_height / 100],
        [ page_thickness / 2,                                   cover_depth / 2,                                                -cover_height / 2 + cover_height / 100],

        [-page_thickness / 2 - cover_thickness,                -cover_depth / 2,                                                 cover_height / 2 - cover_height / 100],
        [-page_thickness / 2 - cover_thickness,                 cover_depth / 2,                                                 cover_height / 2 - cover_height / 100],
        [-page_thickness / 2 - cover_thickness,                -cover_depth / 2,                                                -cover_height / 2 + cover_height / 100],
        [-page_thickness / 2 - cover_thickness,                 cover_depth / 2,                                                -cover_height / 2 + cover_height / 100],

        [-page_thickness / 2,                                  -cover_depth / 2,                                                 cover_height / 2 - cover_height / 100],
        [-page_thickness / 2,                                   cover_depth / 2,                                                 cover_height / 2 - cover_height / 100],
        [-page_thickness / 2,                                  -cover_depth / 2,                                                -cover_height / 2 + cover_height / 100],
        [-page_thickness / 2,                                   cover_depth / 2,                                                -cover_height / 2 + cover_height / 100],

        [ page_thickness / 2 + cover_thickness - hinge_inset,  -cover_depth / 2 - hinge_width / 2,                               cover_height / 2 - cover_height / 100],
        [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width / 2,                               cover_height / 2 - cover_height / 100],
        [ page_thickness / 2 + cover_thickness - hinge_inset,  -cover_depth / 2 - hinge_width / 2,                              -cover_height / 2 + cover_height / 100],
        [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width / 2,                              -cover_height / 2 + cover_height / 100],

        [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width,                                   cover_height / 2 - cover_height / 100],
        [ page_thickness / 2 + cover_thickness,                -cover_depth / 2 - hinge_width,                                   cover_height / 2 - cover_height / 100],
        [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width,                                  -cover_height / 2 + cover_height / 100],
        [ page_thickness / 2 + cover_thickness,                -cover_depth / 2 - hinge_width,                                  -cover_height / 2 + cover_height / 100],

        [-page_thickness / 2 - cover_thickness + hinge_inset,  -cover_depth / 2 - hinge_width / 2,                               cover_height / 2 - cover_height / 100],
        [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width / 2,                               cover_height / 2 - cover_height / 100],
        [-page_thickness / 2 - cover_thickness + hinge_inset,  -cover_depth / 2 - hinge_width / 2,                              -cover_height / 2 + cover_height / 100],
        [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width / 2,                              -cover_height / 2 + cover_height / 100],

        [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width,                                   cover_height / 2 - cover_height / 100],
        [-page_thickness / 2 - cover_thickness,                -cover_depth / 2 - hinge_width,                                   cover_height / 2 - cover_height / 100],
        [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width,                                  -cover_height / 2 + cover_height / 100],
        [-page_thickness / 2 - cover_thickness,                -cover_depth / 2 - hinge_width,                                  -cover_height / 2 + cover_height / 100],

        [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width - cover_thickness,                 cover_height / 2 - cover_height / 100],
        [ page_thickness / 2,                                  -cover_depth / 2 - hinge_width - cover_thickness,                -cover_height / 2 + cover_height / 100],

        [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width - cover_thickness,                 cover_height / 2 - cover_height / 100],
        [-page_thickness / 2,                                  -cover_depth / 2 - hinge_width - cover_thickness,                -cover_height / 2 + cover_height / 100],

        [0,                                                    -cover_depth / 2 - hinge_width - spline_curl - cover_thickness,   cover_height / 2 - cover_height / 100],
        [0,                                                    -cover_depth / 2 - hinge_width - spline_curl,                     cover_height / 2 - cover_height / 100],
        [0,                                                    -cover_depth / 2 - hinge_width - spline_curl - cover_thickness,  -cover_height / 2 + cover_height / 100],
        [0,                                                    -cover_depth / 2 - hinge_width - spline_curl,                    -cover_height / 2 + cover_height / 100],

        [-page_thickness / 2 - cover_thickness,                 cover_depth / 2 - cover_depth / 100,                             cover_height / 2],
        [-page_thickness / 2 - cover_thickness,                 cover_depth / 2 - cover_depth / 100,                            -cover_height / 2],
        [-page_thickness / 2,                                   cover_depth / 2 - cover_depth / 100,                             cover_height / 2],
        [-page_thickness / 2,                                   cover_depth / 2 - cover_depth / 100,                            -cover_height / 2],

        [ page_thickness / 2 + cover_thickness,                 cover_depth / 2 - cover_depth / 100,                             cover_height / 2],
        [ page_thickness / 2 + cover_thickness,                 cover_depth / 2 - cover_depth / 100,                            -cover_height / 2],
        [ page_thickness / 2,                                   cover_depth / 2 - cover_depth / 100,                             cover_height / 2],
        [ page_thickness / 2,                                   cover_depth / 2 - cover_depth / 100,                            -cover_height / 2],

        [-page_thickness / 2 - cover_thickness,                 cover_depth / 2 - cover_depth / 100,                             cover_height / 2 - cover_height / 100],
        [-page_thickness / 2 - cover_thickness,                 cover_depth / 2 - cover_depth / 100,                            -cover_height / 2 + cover_height / 100],
        [-page_thickness / 2,                                   cover_depth / 2 - cover_depth / 100,                             cover_height / 2 - cover_height / 100],
        [-page_thickness / 2,                                   cover_depth / 2 - cover_depth / 100,                            -cover_height / 2 + cover_height / 100],

        [ page_thickness / 2 + cover_thickness,                 cover_depth / 2 - cover_depth / 100,                             cover_height / 2 - cover_height / 100],
        [ page_thickness / 2 + cover_thickness,                 cover_depth / 2 - cover_depth / 100,                            -cover_height / 2 + cover_height / 100],
        [ page_thickness / 2,                                   cover_depth / 2 - cover_depth / 100,                             cover_height / 2 - cover_height / 100],
        [ page_thickness / 2,                                   cover_depth / 2 - cover_depth / 100,                            -cover_height / 2 + cover_height / 100],

    # additional proximity loops pages
        [-page_thickness / 2 + page_thickness / 100,           -page_depth / 2 + page_depth / 100,                               page_height / 2],
        [ page_thickness / 2 - page_thickness / 100,           -page_depth / 2 + page_depth / 100,                               page_height / 2],
        [-page_thickness / 2 + page_thickness / 100,            page_depth / 2 - page_depth / 100,                               page_height / 2],
        [ page_thickness / 2 - page_thickness / 100,            page_depth / 2 - page_depth / 100,                               page_height / 2],

        [-page_thickness / 2 + page_thickness / 100,           -page_depth / 2 + page_depth / 100,                              -page_height / 2],
        [ page_thickness / 2 - page_thickness / 100,           -page_depth / 2 + page_depth / 100,                              -page_height / 2],
        [-page_thickness / 2 + page_thickness / 100,            page_depth / 2 - page_depth / 100,                              -page_height / 2],
        [ page_thickness / 2 - page_thickness / 100,            page_depth / 2 - page_depth / 100,                              -page_height / 2],

        [-page_thickness / 2 + page_thickness / 100,           -page_depth / 2,                                                 -page_height / 2 + page_height / 100],
        [ page_thickness / 2 - page_thickness / 100,           -page_depth / 2,                                                 -page_height / 2 + page_height / 100],
        [-page_thickness / 2 + page_thickness / 100,            page_depth / 2,                                                 -page_height / 2 + page_height / 100],
        [ page_thickness / 2 - page_thickness / 100,            page_depth / 2,                                                 -page_height / 2 + page_height / 100],

        [-page_thickness / 2 + page_thickness / 100,           -page_depth / 2,                                                  page_height / 2 - page_height / 100],
        [ page_thickness / 2 - page_thickness / 100,           -page_depth / 2,                                                  page_height / 2 - page_height / 100],
        [-page_thickness / 2 + page_thickness / 100,            page_depth / 2,                                                  page_height / 2 - page_height / 100],
        [ page_thickness / 2 - page_thickness / 100,            page_depth / 2,                                                  page_height / 2 - page_height / 100],

        [-page_thickness / 2,                                  -page_depth / 2 + page_depth / 100,                               page_height / 2 - page_height / 100],
        [ page_thickness / 2,                                  -page_depth / 2 + page_depth / 100,                               page_height / 2 - page_height / 100],
        [-page_thickness / 2,                                   page_depth / 2 - page_depth / 100,                               page_height / 2 - page_height / 100],
        [ page_thickness / 2,                                   page_depth / 2 - page_depth / 100,                               page_height / 2 - page_height / 100],

        [-page_thickness / 2,                                  -page_depth / 2 + page_depth / 100,                              -page_height / 2 + page_height / 100],
        [ page_thickness / 2,                                  -page_depth / 2 + page_depth / 100,                              -page_height / 2 + page_height / 100],
        [-page_thickness / 2,                                   page_depth / 2 - page_depth / 100,                              -page_height / 2 + page_height / 100],
        [ page_thickness / 2,                                   page_depth / 2 - page_depth / 100,                              -page_height / 2 + page_height / 100],
    ]
