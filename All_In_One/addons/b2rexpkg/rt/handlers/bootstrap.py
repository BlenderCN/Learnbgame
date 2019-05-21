"""
 Bootstrap client from previously available data
"""

from .base import Handler

class BootstrapHandler(Handler):
    def processBootstrap(self):
        print("BOOTSTRAP CLIENT")
        objects = self.manager.client.region.objects
        for obj in objects.object_store:
            obj_uuid = str(obj.FullID)
            if hasattr(obj, "pos") and hasattr(obj, "rot"):
                self.out_queue.put(['pos', obj_uuid, obj.pos, obj.rot])
            if hasattr(obj, "scale"):
                self.out_queue.put(['scale', obj_uuid, obj.scale])
            if hasattr(obj, "rexdata"):
                self.out_queue.put(['RexPrimData', obj_uuid, obj.rexdata])
            if hasattr(obj, "props"):
                self.out_queue.put(["ObjectProperties", obj_uuid, obj.props])


