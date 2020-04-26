"""
 Parser for InventoryString style serialization.

 inferred from Opensim/../Scenes/SceneObjectPartInventory.cs
"""

from collections import defaultdict

class InventoryStringParser(object):
    def __init__(self, data=None, titlefilter=''):
        """
        Initialize the string parser, optionally providing
        initial data and a filter for object titles.
        """
        self._titlefilter = titlefilter
        if data:
            self.parse(data)

    def parse(self, data):
        """
        Parse the given string data.
        """
        inventory = defaultdict(list)
        targets = [inventory]
        lastline = ""
        for line in data.split('\n'):
            if '\t{' in line:
                currtarget = targets[-1]
                lastline = lastline.split()[0]
                if self._titlefilter:
                    lastline = lastline.replace(self._titlefilter, '')
                newtarget = {}
                try:
                    # currtarget is a defaultdict(list)
                    currtarget[lastline].append(newtarget)
                except:
                    # other
                    currtarget[lastline] = newtarget
                targets.append(newtarget)
            elif '\t}' in line:
                targets.pop()
            elif '\t\t' in line:
                currtarget = targets[-1]
                name, value = line.strip().split('\t')
                currtarget[name] = value
            if line.strip():
                lastline = line.strip()
        self.result = inventory

    def __getattr__(self, name):
        """
        Override attribute access proxying the underlying results.
        """
        if name in self.result:
            return self.result[name]
        return getattr(self.result, name)

    def __hasattr__(self, name):
        """
        Check to see if we have some attribute proxying to underlying
        results.
        """
        return name in self.result or hasattr(self.result, name)

testdata = """
\tinv_object\t0\n\t{\n
\t\tobj_id\tfoo\n
\t\tparent_id\tfoo\n
\t\ttype\tcategory\n
\t\tname\tContents|\n
\t}\n
\tinv_item\t0\n
\t{\n
\t\titem_id\tfoo\n
\t\tparent_id\tfoo\n
\tpermissions 0\n
\t{\n
\t\tbase_mask\tfoo\n
\t\towner_mask\tfoo\n
\t}\n
\t\tasset_id\tfoo\n
\t\ttype\tfoo\n
\tsale_info 0\n
\t{\n
\t\tbase_mask\tfoo\n
\t\towner_mask\tfoo\n
\t}\n
\t\tname\tfoo\n
\t}\n
\tinv_item\t0\n
\t{\n
\t\titem_id\tfoo2\n
\t\tparent_id\tfoo2\n
\tpermissions 0\n
\t{\n
\t\tbase_mask\tfoo\n
\t\towner_mask\tfoo\n
\t}\n
\t\tasset_id\tfoo\n
\t\ttype\tfoo\n
\tsale_info 0\n
\t{\n
\t\tbase_mask\tfoo\n
\t\towner_mask\tfoo\n
\t}\n
\t\tname\tfoo\n
\t}\n

"""

if __name__ == "__main__":
    p = InventoryStringParser(testdata, 'inv_')
    print(p.result)
    print(len(p.result))
    for res in p.result:
        print(res)
    for item in p.item:
        print(item)
    for obj in p.object:
        print(obj)
