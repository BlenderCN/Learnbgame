import struct

def arr2float(v):
    res = struct.unpack("f",struct.pack("cccc",v[0],v[1],v[2],v[3]))
    return res[0]

def parse_vector(text):
    text = text.strip()[1:-1]
    return list(map(lambda s: float(s.strip()), text.split(',')))

def get_vertex_legend(vertex):
    result_dict = {}
    for v in vertex:
        result_dict[v[3]] = v
    return result_dict

def get_nor(idx, vbuffer, no_offset):
    v = vbuffer[idx*32:(idx+1)*32]
    no1 = arr2float(v[no_offset+0:no_offset+4])
    no2 = arr2float(v[no_offset+4:no_offset+8])
    no3 = arr2float(v[no_offset+8:no_offset+12])
    return (no1, no2, no3)

def get_uv(idx, vbuffer, uv_offset):
    if len(vbuffer) >= (idx+1)*32:
        v = vbuffer[idx*32:(idx+1)*32]
        uv1 = arr2float(v[uv_offset+0:uv_offset+4])
        uv2 = arr2float(v[uv_offset+4:uv_offset+8])
    else:
        uv1 = 0.0
        uv2 = 1.0
    return (uv1, 1.0-uv2)

def mat_findtextures(material):
    textures = []
    lines = material["data"].split("\n")
    basemap = False
    for line in lines:
        line = line.strip()
        if "baseMap" in line:
            basemap = True
        if "texture " in line and basemap:
            split_line = line.split(" ")
            if len(split_line) == 2:
                tex = split_line[1].strip()
                textures.append(tex)
            basemap = False
    return textures

def get_vcoords(vbuffer, idx, pos_offset, stride=32):
    v = vbuffer[idx*stride:(idx+1)*stride]
    if v and len(v) >= pos_offset+12:
        v1 = arr2float(v[pos_offset+0:pos_offset+4])
        v2 = arr2float(v[pos_offset+4:pos_offset+8])
        v3 = arr2float(v[pos_offset+8:pos_offset+12])
        return (-v1, v3, v2)

