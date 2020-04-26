"""
 Object selection
"""

from .base import Handler

class SelectHandler(Handler):
    _selected = set()
    def processSelect(self, *args):
        client = self.manager.client
        selected = self._selected
        selected_cmd = set(args)
        newselected = selected_cmd.difference(selected)
        deselected = selected.difference(selected_cmd)
        for obj_id in newselected:
            obj = client.region.objects.get_object_from_store(FullID=obj_id)
            if obj:
                obj.select(client)
            else:
                print("cant find "+obj_id)
        for obj_id in deselected:
            obj = client.region.objects.get_object_from_store(FullID=obj_id)
            if obj:
                obj.deselect(client)
        self._selected = selected_cmd


