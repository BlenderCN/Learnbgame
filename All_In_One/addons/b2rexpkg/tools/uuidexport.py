"""
    Utils for uuid exporting.
"""

import sys

from collections import defaultdict

import uuid

class UUIDExporter(object):
    def __init__(self):
        self.nodes = defaultdict(list)
    def add(self, section, obj_type, obj_name, obj_uuid):
        self.nodes[section].append(" <"+obj_type+" name='"+obj_name+"' uuid='"+str(obj_uuid)+"' />\n")
    def write(self, f):
        f.write("<uuids>\n")
        for obj_type in self.nodes:
            f.write("<%s>\n"%(obj_type,))
            for node in self.nodes[obj_type]:
                f.write(node)
            f.write("</%s>\n"%(obj_type,))
        f.write("</uuids>")


uuidexporter = None

def start():
    global uuidexporter
    uuidexporter = UUIDExporter()

def write(f):
    global uuidexporter
    uuidexporter.write(f)

def reset_uuids(bobjs):
    if sys.version_info[0] == 2:
        for bobj in bobjs:
            if not 'opensim' in bobj.properties:
                bobj.properties['opensim'] = {}
                bobj.properties['opensim']['uuid'] = str(uuid.uuid4())
    else:
        for bobj in bobjs:
            bobj.opensim.uuid = str(uuid.uuid4())

