import os
import bpy
import subprocess
from .utils import XMLWriter, get_addon_pref

CMD_EXPORT = '{converter:s} {args:s} "{input:s}" "{output:s}"'
SHARED_GEOMETRY = "<sharedgeometry vertexcount=\"{vertexcount:d}\">"

VB_POSITION = "positions=\"{positions:s}\" "
VB_NORMAL   = "normals=\"{normals:s}\" "
VB_TEXDIM   = "texture_coord_dimensions_0=\"{tex_dim:d}\" "
VB_TEXCO    = "texture_coords=\"{tex_co:d}\""
VERTEX_BUFFER = "".join(("<vertexbuffer ", VB_POSITION, VB_NORMAL, VB_TEXDIM, VB_TEXCO, ">"))

POSITION = "<position x=\"{x:g}\" y=\"{y:g}\" z=\"{z:g}\" />"
NORMAL   =   "<normal x=\"{x:g}\" y=\"{y:g}\" z=\"{z:g}\" />"
TEXCOORD = "<texcoord u=\"{u:g}\" v=\"{v:g}\" />"

SUBMESH = ("<submesh "
             "material=\"{material:s}\" "
    "usesharedvertices=\"{shared_vertices:s}\" "
      "use32bitindexes=\"{use_32bit:s}\" "
        "operationtype=\"{op_type:s}\">")

GEOMETRY = "<geometry vertexcount=\"{vertexcount:d}\">"
FACES = "<faces count=\"{facecount:d}\">"
FACE  = "<face v1=\"{v1:d}\" v2=\"{v2:d}\" v3=\"{v3:d}\" />"

BONE_ASSIGNMENT = ("<vertexboneassignment "
    "vertexindex=\"{vertexindex:d}\" "
      "boneindex=\"{boneindex:d}\" "
         "weight=\"{weight:g}\" />")

SKELETONLINK = "<skeletonlink name=\"{name:s}\" />"

def convert_to_mesh(xml_input, mesh_output, create_directory=False):
    if not os.path.exists(xml_input):
        raise FileNotFoundError(xml_input)

    mesh_directory = os.path.dirname(mesh_output)
    if not os.path.exists(mesh_directory):
        if create_directory:
            os.makedirs(mesh_directory)
        else:
            raise FileNotFoundError(os.path.dirname(mesh_directory))

    pref = get_addon_pref(bpy.context)
    args = pref.cmd_args_mesh_export if pref.use_cmd_args else ""
    ogre_xml_converter = pref.ogre_xml_converter
    arg_list = [ogre_xml_converter]
    if not args == "":
        # might replace str.split by shlex.split
        arg_list.extend(args.split())
    arg_list.append(xml_input)
    arg_list.append(mesh_output)
    subprocess.run(arg_list, check=True)

def write_vertex_buffer(xml, mesh, vertex_indices, flags):
    (data_position,
     data_normal,
     #...
     data_uv) = flags

    xml.tag_open_format(VERTEX_BUFFER,
        positions = "true" if data_position else "false",
        normals   = "true" if data_normal   else "false",
        tex_co    =      1 if data_uv       else       0,
        tex_dim   =      2
    )

    if data_uv:
        uv_layer = mesh.uv_layers[0].data
        uv_loops = [None] * len(mesh.vertices)
        for loop in mesh.loops:
            uv_loops[loop.vertex_index] = uv_layer[loop.index]

    for index in vertex_indices:
        v = mesh.vertices[index]
        if data_uv:
            uv_loop = uv_loops[index]
            uv = uv_loop.uv.copy()
            uv.y = 1.0 - uv.y

        write_vertex(xml,
            v.undeformed_co if data_position else None,
            v.normal        if data_normal   else None,
            uv              if data_uv       else None,
        )

    xml.tag_close("vertexbuffer")

def write_vertex(xml, co, n, uv):
    xml.tag_open("vertex")
    if co: xml.tag_format(POSITION, x=co.x, y=co.y, z=co.z)
    if  n: xml.tag_format(NORMAL,   x= n.x, y= n.y, z= n.z)
    if uv: xml.tag_format(TEXCOORD, u=uv.x, v=uv.y)
    xml.tag_close("vertex")

# =============================================================================
# -----------------------------------WEAPON------------------------------------
# =============================================================================

def write_mesh_weapon(stream, mesh):
    xml = XMLWriter(stream)

    xml.tag_open("mesh")
    write_shared_geometry(xml, mesh, ((True, True, True),))

    xml.tag_open("submeshes")
    write_submesh_weapon(xml, mesh)
    xml.tag_close("submeshes")

    xml.tag_close("mesh")
    xml.finish()

def write_submesh_weapon(xml, mesh):
    xml.tag_open_format(SUBMESH,
        material=mesh.materials[0].name,
        shared_vertices="true",
        use_32bit="false",
        op_type="triangle_list"
    )

    xml.tag_open_format(FACES, facecount=len(mesh.polygons))
    for poly in mesh.polygons:
        indices = poly.vertices
        if not len(indices) == 3:
            raise ValueError("Polygon is not a triangle")
        xml.tag_format(FACE, v1=indices[0], v2=indices[1], v3=indices[2])

    xml.tag_close("faces")
    xml.tag_close("submesh")

def write_shared_geometry(xml, mesh, buffer_types):
    xml.tag_open_format(SHARED_GEOMETRY, vertexcount=len(mesh.vertices))
    for buf_type in buffer_types:
        write_vertex_buffer(xml, mesh, range(len(mesh.vertices)), buf_type)
    xml.tag_close("sharedgeometry")

# =============================================================================
# ---------------------------------WARDROBE------------------------------------
# =============================================================================

def write_mesh_wardrobe(stream, mesh, vgi_to_bi, skel_link):
    xml = XMLWriter(stream)
    xml.tag_open("mesh")
    xml.tag_open("submeshes")

    for mat_index in range(len(mesh.materials)):
        write_submesh_wardrobe(xml, mesh, vgi_to_bi, mat_index)

    xml.tag_close("submeshes")
    xml.tag_format(SKELETONLINK, name=skel_link)
    xml.tag_close("mesh")
    xml.finish()

def write_submesh_wardrobe(xml, mesh, vgi_to_bi, mat_index):
    xml.tag_open_format(SUBMESH,
        material = mesh.materials[mat_index].name,
        shared_vertices="false",
        use_32bit="false",
        op_type="triangle_list"
    )

    polys = [poly for poly in mesh.polygons if poly.material_index == mat_index]
    vertex_indices = {i for poly in polys for i in poly.vertices}
    vertex_indices = list(vertex_indices)
    vertex_indices.sort()

    xml.tag_open_format(FACES, facecount=len(polys))
    for poly in polys:
        # convert from mesh vertex index (mvi) to submesh index (smi)
        indices = [vertex_indices.index(mvi) for mvi in poly.vertices]
        xml.tag_format(FACE, v1=indices[0], v2=indices[1], v3=indices[2])
    xml.tag_close("faces")

    xml.tag_open_format(GEOMETRY, vertexcount=len(vertex_indices))
    write_vertex_buffer(xml, mesh, vertex_indices, (True,  True,  False))
    write_vertex_buffer(xml, mesh, vertex_indices, (False, False, True ))
    xml.tag_close("geometry")

    write_boneassignments(xml, mesh, vertex_indices, vgi_to_bi)

    xml.tag_close("submesh")
    return len(vertex_indices)

def write_boneassignments(xml, mesh, vertex_indices, vgi_to_bi):
    xml.tag_open("boneassignments")
    for smi, mvi in enumerate(vertex_indices):
        v = mesh.vertices[mvi]
        for g in v.groups:
            bi = vgi_to_bi[g.group]
            if bi >= 0:
                xml.tag_format(BONE_ASSIGNMENT,
                    vertexindex=smi,
                    boneindex=bi,
                    weight=g.weight
                )
    xml.tag_close("boneassignments")

# =============================================================================
# ----------------------------------MONSTER------------------------------------
# =============================================================================

def write_mesh_monster(stream, mesh, vgi_to_bi, skel_link):
    xml = XMLWriter(stream)
    xml.tag_open("mesh")
    write_shared_geometry(xml, mesh, ((True,  True, False), (False, False, True)))

    xml.tag_open("submeshes")
    for mat_index in range(len(mesh.materials)):
        write_submesh_monster(xml, mesh, mat_index)
    xml.tag_close("submeshes")

    xml.tag_format(SKELETONLINK, name=skel_link)

    write_boneassignments(xml, mesh, tuple(range(len(mesh.vertices))), vgi_to_bi)

    xml.tag_close("mesh")
    xml.finish()

def write_submesh_monster(xml, mesh, mat_index):
    xml.tag_open_format(SUBMESH,
        material=mesh.materials[mat_index].name,
        shared_vertices="true",
        use_32bit="false",
        op_type="triangle_list"
    )

    xml.tag_open_format(FACES, facecount=len(mesh.polygons))
    for poly in mesh.polygons:
        indices = poly.vertices
        if not len(indices) == 3:
            raise ValueError("Polygon is not a triangle")
        xml.tag_format(FACE, v1=indices[0], v2=indices[1], v3=indices[2])

    xml.tag_close("faces")
    xml.tag_format("<boneassignments />")
    xml.tag_close("submesh")
