"""
 Kristalli message xml parser

 see http://clb.demon.fi/knet/_kristalli_x_m_l.html
"""
import xml.etree.ElementTree as ET

class Message(object):
    """
    A kristalli message
    """
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        """
        Return a string representation of the object
        """
        name = self.name
        #desc = "KristalliMessage("+name+"\n"
        #for name in dir(self):
            #    if not name.startswith("__") and not name == 'name':
                #    desc += " "+name+" "+str(getattr(self, name))+"\n"
                #return desc+")"
        if hasattr(self, 'dynamiccomponents'):
            entityID = self.entityID
            components = self.components
            dyncomponents = self.dynamiccomponents
            return "KristalliMessage(%s, %s, %s, %s)" % (name, entityID, components,
                                                    dyncomponents)
        elif hasattr(self, 'components'):
            entityID = self.entityID
            components = self.components
            return "KristalliMessage(%s, %s, %s)" % (name, entityID, components)

        elif hasattr(self, 'componentTypeHash'):
            componentTypeHash = self.componentTypeHash
            componentName = self.componentName
            return "KristalliComponent(%s, %s)" % (componentTypeHash,
                                                 componentName)
        elif hasattr(self, 'entityID'):
            entityID = self.entityID
            return "KristalliMessage(%s, %s)" % (name, entityID)
        else:
            return "KristalliMessage(%s)" % (name,)

class MessageTemplate(object):
    """
    A kristalli message template
    """
    def __init__(self, xml):
        self._xml = xml

    def __getattr__(self, name):
        """
        Get attributes from the root xml node if they
        don't exist in this class.
        """
        return self._xml.get(name)

    def parse(self, data):
        """
        Parse the given data using the current template.
        """
        dest = self.parse_element(self._xml, data, 0)
        return dest

    def parse_list(self, xml, data, level):
        """
        Parse a list of elements.
        """
        elmt_list = []
        dynamic_count = int(xml.get('dynamicCount'))
        count = data.get_dynamic_count(dynamic_count)
        # print(" "*level, "List", xml.get('name'), count)
        for idx in range(count):
            dest = self.parse_element(xml, data, level+1)
            elmt_list.append(dest)
        return elmt_list

    def parse_element(self, xml, data, level):
        """
        Parse an xml element.
        """
        dest = Message(xml.get('name'))
        #print(" "*level, "Element", xml.get('name'))
        for elmt in xml:
            val = None
            #print(" "*(level+1), elmt.get('name'))
            if elmt.tag == 'u32':
                val = data.get_u32()
            elif elmt.tag == 'u16':
                val = data.get_u16()
            elif elmt.tag == 'u8':
                dyn_count = int(elmt.get('dynamicCount', 0))
                if dyn_count:
                    val = data.get_dyn_u8(dyn_count)
                else:
                    val = data.get_u8()
            elif elmt.tag == 's8':
                dyn_count = int(elmt.get('dynamicCount', 0))
                if dyn_count:
                    val = data.get_dyn_s8(dyn_count)
                else:
                    val = data.get_s8()
            elif elmt.tag == 'struct':
                val = self.parse_list(elmt, data, level+1)
            if val != None:
                setattr(dest, elmt.get('name'), val)
            else:
                print("Tag with no value", elmt.get('name'))
        return dest

    def __repr__(self):
        """
        Return a string representation of this object
        """
        return 'MessageTemplate(%s)'%(self.name,)


class MessageTemplateParser(object):
    """
    A parser for message templates, that works
    by adding files for it will parse.

    Maintains a dict of templates at self.templates
    and msg_ids can be queried using self.get_msg_id(msg_name)
    """
    def __init__(self):
        self.templates = {}
        self._msg_ids = {}

    def get_msg_id(self, msg_name):
        """
        Query the kristalli id for a message
        """
        return self._msg_ids[msg_name]

    def add_file(self, filename):
        """
        Add a file for parsing
        """
        f = open(filename, 'r')
        data = f.read()
        f.close()
        xml = ET.fromstring(data)
        for elmt in xml:
            id = int(elmt.get('id'))
            name = elmt.get('name')
            self.templates[id] = MessageTemplate(elmt)
            self._msg_ids[name] = id
            # print(id, self.templates[id])

    def parse(self, msg_id, data):
        """
        Parse the given data with the template for msg_id
        """
        return self.templates[msg_id].parse(data)


if __name__ == '__main__':
    from data import KristalliData
    f = open("/tmp/113.txt")
    data = KristalliData(f.read())
    f.close()
    t = MessageTemplateParser()
    t.add_file('/home/caedes/SVN/REALXTEND/tundra/TundraLogicModule/TundraMessages.xml')
    print(t.templates[113])
    msg = t.parse(113, data)
    print(msg.entityID)
    print(msg.components)
    for component in msg.components:
        print(component.componentTypeHash)

    for component in msg.dynamiccomponents:
        print(component.componentTypeHash)
    print(data._idx, len(data._data))
