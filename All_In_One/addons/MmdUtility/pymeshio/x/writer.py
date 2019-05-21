# coding: utf-8
"""
"""
import io
from .. import x


def write(ios, model):
    """
    write model to ios.

    :Parameters:
        ios
            output stream (in io.IOBase)
        model
            pmx model

    >>> import pymeshio.x.writer
    >>> pymeshio.x.writer.write(io.open('out.x', 'wb'), x_model)

    """
    assert(isinstance(ios, io.IOBase))
    assert(isinstance(model, x.Model))

    # signature
    ios.write("xof 0302txt 0064\r\n")

    # templates
    for template in model.templates:
        ios.write(template)
        ios.write("\r\n")

    # header
    ios.write("Header{\r\n")
    ios.write("1;\r\n");
    ios.write("0;\r\n");
    ios.write("1;\r\n");
    ios.write("}\r\n")
    ios.write("\r\n")

    ios.write("Mesh {\r\n")

    # vertex
    ios.write(" %d;\r\n" % len(model.vertices))
    last_index=len(model.vertices)-1
    for i, v in enumerate(model.vertices):
        if i!=last_index:
            ios.write(" %.5f;%.5f;%.5f;,\r\n" % (v.x, v.y, v.z))
        else:
            ios.write(" %.5f;%.5f;%.5f;;\r\n" % (v.x, v.y, v.z))
    ios.write("\r\n")

    # faces
    ios.write(" %d;\r\n" % len(model.faces))
    def get_face_line(f):
        return ("%d;" % len(f))+",".join([str(n) for n in f])+";"
    last_index=len(model.faces)-1
    for i, f in enumerate(model.faces):
        if i!=last_index:
            ios.write( " %s,\r\n" % get_face_line(f))
        else:
            ios.write( " %s;\r\n" % get_face_line(f))
    ios.write("\r\n")

    # material list
    ios.write(" MeshMaterialList {\r\n")
    ios.write("  %d;\r\n" % len(model.materials))
    ios.write("  %d;\r\n" % len(model.faces))
    last_index=len(model.face_materials)-1
    for i, f in enumerate(model.face_materials):
        if i!=last_index:
            ios.write("  %d,\r\n" % f)
        else:
            ios.write("  %d;;\r\n" % f)
    for i, m in enumerate(model.materials):
        ios.write("  Material {\r\n")
        ios.write("   %.6f;%.6f;%.6f;%.6f;;\r\n" % (m.diffuse.r, m.diffuse.g, m.diffuse.b, m.diffuse.a))
        ios.write("   %.6f;\r\n" % m.shininess)
        ios.write("   %.6f;%.6f;%.6f;;\r\n" % (m.specular.r, m.specular.g, m.specular.b))
        ios.write("   %.6f;%.6f;%.6f;;\r\n" % (m.emit.r, m.emit.g, m.emit.b))
        ios.write("  }\r\n")
    ios.write(" }\r\n")

    # normals
    ios.write(" MeshNormals {\r\n")
    ios.write("  %d;\r\n" % len(model.normals))
    last_index=len(model.normals)-1
    for i, n in enumerate(model.normals):
        if i!=last_index:
            ios.write("  %.6f;%.6f;%.6f;,\r\n" % (n.x, n.y, n.z))
        else:
            ios.write("  %.6f;%.6f;%.6f;;\r\n" % (n.x, n.y, n.z))

    ios.write("  %d;\r\n" % len(model.face_normals))
    last_index=len(model.face_normals)-1
    def get_face_normal_line(face_normal):
        return ("%d;" % len(face_normal))+",".join([str(n) for n in face_normal])+";"
    for i, fn in enumerate(model.face_normals):
        if i!=last_index:
            ios.write( "  %s,\r\n" % get_face_normal_line(fn))
        else:
            ios.write( "  %s;\r\n" % get_face_normal_line(fn))
    ios.write(" }\r\n")

    # uv
    if len(model.uvs)>0:
        ios.write(" MeshTextureCoords {\r\n")
        ios.write("  %d;\r\n" % len(model.uvs))
        last_index=len(model.uvs)-1
        for i, uv in enumerate(model.uvs):
            if i!=last_index:
                ios.write("  %.6f;%.6f;,\r\n" % (uv.x, uv.y))
            else:
                ios.write("  %.6f;%.6f;;\r\n" % (uv.x, uv.y))
        ios.write(" }\r\n")


    ios.write("}\r\n")

