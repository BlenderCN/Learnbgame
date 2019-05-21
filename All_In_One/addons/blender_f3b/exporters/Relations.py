import f3b
import f3b.datas_pb2
import f3b.custom_params_pb2
import f3b.animations_kf_pb2
import f3b.physics_pb2
from .. import Logger as log
from ..F3bContext import *

def add(ctx:F3bContext, data:f3b.datas_pb2.Data ,ref1:str,ref2:str):
    rel = data.relations.add()
    rel.ref1 = ref1
    rel.ref2 = ref2
    log.info("add relation: '%s' to '%s'" % ( ref1, ref2))