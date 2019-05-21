from copy import copy
import ctypes
from ctypes import c_float
import os


class DynamicStructure:

    _fields_ = None

    # TODO: change signature to make it clear that 'file_path' can be also a buffer
    def __new__(cls, file_path=None, *args, **kwargs):
        cls_dict = {'_pack_': 1}
        cls_dict.update(cls.__dict__)
        cls_dict['_fields_'] = parse_fields(cls._fields_, file_path, **kwargs)

        try:
            generated_cls = type('Gen{}'.format(cls.__name__), (ctypes.Structure,), cls_dict)
        except TypeError:
            raise RuntimeError('Error generating class. Fields: {}'.format(cls_dict['_fields_']))

        if file_path:
            instance = generated_cls()
            instance._file_path = file_path  # TODO: move to 'meta' attribute.
            try:
                with open(file_path, 'rb') as f:
                    f.readinto(instance)
            except TypeError:
                file_path.readinto(instance)
                file_path.close()
        else:
            instance = generated_cls(**kwargs)

        return instance


def parse_fields(sequence_of_tuples, file_path_or_buffer=None, **kwargs):
    ready_fields = []
    try:
        os.path.isfile(file_path_or_buffer)
        is_file = True
        buff = open(file_path_or_buffer, 'rb')
    except TypeError:
        buff = file_path_or_buffer
        is_file = False

    for t in sequence_of_tuples:
        attr_name = t[0]
        ctype_or_callable = t[1]
        try:
            ctypes.sizeof(ctype_or_callable)
            ready_fields.append(t)
        except TypeError:
            class TmpStruct(ctypes.Structure):
                _fields_ = ready_fields
                _pack_ = 1
            if buff:
                tmp_struct = TmpStruct()
                buff.readinto(tmp_struct)
                buff.seek(0)
            else:
                tmp_struct = TmpStruct(**kwargs)
            try:
                c_type = ctype_or_callable(tmp_struct)
            except TypeError:
                c_type = ctype_or_callable(tmp_struct, file_path_or_buffer)

            ready_fields.append((attr_name, c_type))

    if file_path_or_buffer and is_file:
        buff.close()

    return tuple(ready_fields)


def get_offset(struct_ob, name):
    return getattr(struct_ob.__class__, name).offset


def get_size(struct_ob, name):
    return getattr(struct_ob.__class__, name).size
