
from mathutils import Matrix
def blender_matrix_to_gl(m):
    t = m.transposed()
    return list(t[0]) + list(t[1]) + list(t[2]) + list(t[3])

def gl_matrix_to_blender(m):
    return Matrix(m[0::4], m[1::4], m[2::4], m[3::4])

def srgb_to_linearrgb(out, color):
    for i,c in enumerate(color):
        if c < 0.04045:
            c = max(c,0) * (1.0 / 12.92)
        else:
            c = pow((c + 0.055)*(1.0/1.055), 2.4)
        out[i] = c
    return out

def linearrgb_to_srgb(out, color):
    for i,c in enumerate(color):
        if c < 0.0031308:
            c = max(c,0) * 12.92
        else:
            c = 1.055 * pow(c, 1.0/2.4) - 0.055
        out[i] = c
    return out
