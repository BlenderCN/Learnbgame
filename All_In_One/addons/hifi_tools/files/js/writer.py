js_flow = "flow.js"
js_flow_library = "VectorMath.js"
js_custom_writer = "//__PYTHONFILL__CUSTOM_SETS__//"


class FlowData:
    active = True
    stiffness = 0.0
    radius = 0.04
    gravity = -0.035
    damping = 0.8
    inertia = 0.8
    delta = 0.35

class Vec3Data:
    x = 0
    y = 0
    z = 0

class CollisionData:
    _type = "sphere"
    radius = 0.14
    offset = Vec3Data()

def js_writer(flow_data, collision_data):
    print("Open JS Writer")

