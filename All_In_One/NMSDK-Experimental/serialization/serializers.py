from .formats import write_half, write_int_2_10_10_10_rev


def serialize_vertex_stream(**kwargs):
    """
    Return a serialized version of the vertex data
    """
    # determine what data we have been given:
    data_streams = ['verts', 'uvs', 'normals', 'tangents']
    fmt_map = {'verts': 0, 'uvs': 0, 'normals': 1, 'tangents': 1}
    data = bytearray()
    count = len(kwargs.get('verts', []))
    if count != 0:
        # remove any data streams that are not included
        for k in kwargs:
            if k in data_streams:
                # ensure all entries have the same number of entries
                if len(kwargs.get(k, [])) != count:
                    data_streams.remove(k)
        for i in range(count):
            for d in data_streams:
                if fmt_map[d] == 0:
                    for val in kwargs[d][i]:        # probably slow!!
                        data.extend(write_half(val))
                elif fmt_map[d] == 1:
                    data.extend(write_int_2_10_10_10_rev(kwargs[d][i]))
        return data
    else:
        # return empty data
        return b''


def serialize_index_stream(indexes):
    """
    Return a serialized version of the index data
    """
    return indexes.tobytes()


if __name__ == "__main__":
    # TODO: move to tests
    from array import array
    d = array('I')
    d.extend([1, 2, 3, 4, 5, 735536])
    print(d.tobytes())
    a = serialize_index_stream(d)
    print(a)
