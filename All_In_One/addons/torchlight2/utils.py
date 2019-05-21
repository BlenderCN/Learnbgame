import os
import bpy
import math
import xml.dom.minidom
import subprocess
from mathutils import Vector, Matrix, Quaternion, Euler, Color
from . import __name__ as addon_name

def get_addon_pref(context, attr=None):
    return context.user_preferences.addons[addon_name].preferences

#-------------------------------- XML Utilites ---------------------------------

def child_iter(node, tagName=None):
    """ iterate over child elements and optionally filter for tag name """
    for childNode in node.childNodes:
        if (isinstance(childNode, xml.dom.minidom.Element) and
           (not tagName or tagName == childNode.tagName)):
            yield childNode

    raise StopIteration

def find(node, tagName=None):
    """ get first child element with tagName """
    for domElem in child_iter(node, tagName):
        return domElem
    else:
        return None

def children_count(node, tagName=None):
    return sum(1 for childElem in child_iter(node, tagName))

def getIntAttr(domElem, attr):
    if not (isinstance(domElem, xml.dom.minidom.Element)):
        raise ValueError("Could not get attribute %s - not a DomElement, %s" % (attr, type(domElem)))
    return int(domElem.getAttribute(attr))

def getFloatAttr(domElem, attr):
    if not (isinstance(domElem, xml.dom.minidom.Element)):
        raise ValueError("Could not get attribute %s - not a DomElement, %s" % (attr, type(domElem)))
    return float(domElem.getAttribute(attr))

def getVecAttr(domElem, attributes):
    return (getFloatAttr(domElem, attr) for attr in attributes)

def convert_to_xml(file_input, xml_output, create_directory=False, overwrite=True):
    if os.path.exists(xml_output) and not overwrite:
        return

    if not os.path.exists(file_input):
        raise FileNotFoundError(file_input)

    xml_directory = os.path.dirname(xml_output)
    if not os.path.exists(xml_directory):
        if create_directory:
            os.makedirs(xml_directory)
        else:
            raise FileNotFoundError(os.path.dirname(xml_directory))

    ogre_xml_converter = get_addon_pref(bpy.context).ogre_xml_converter
    subprocess.run([ogre_xml_converter, file_input, xml_output], check=True)


class XMLWriter:
    def __init__(self, file_object):
        self.file_object = file_object
        self.indent_level = 0

    def finish(self):
        self.file_object.close()

    def tag_format(self, fmt, **kwargs):
        self.file_object.write(4*self.indent_level*" " + fmt.format(**kwargs) + "\n")

    def tag_open_format(self, fmt, **kwargs):
        self.tag_format(fmt, **kwargs)
        self.indent_level += 1

    def tag_compose(self, tag_name, attributes):
        composed = " ".join(attributes)
        self.file_object.write(4*self.indent_level*" " + composed + " >\n")

    def tag_open(self, tag_name):
        self.file_object.write(4*self.indent_level*" " + "<%s>\n" % tag_name)
        self.indent_level +=1

    def tag_close(self, tag_name):
        self.indent_level -= 1
        self.file_object.write(4*self.indent_level*" " + "</%s>\n" % tag_name)


#----------------------------------------------------------------------------------------

class Bone(object):
    __slots__ = ("id",  "name", "parent", "children", "children_count",
                 "position", "rotation", "scale")

    def __init__(self, domElem):
        self.id = getIntAttr(domElem, "id")
        self.name = domElem.getAttribute("name")
        self.children = None
        self.parent   = None
        self.children_count = 0
        self.scale = Vector((1.0, 1.0, 1.0))

        for elem in child_iter(domElem):
            if elem.tagName == "position":
                self.position = Vector(getVecAttr(elem, "xyz"))

            elif elem.tagName == "rotation":
                angle = getFloatAttr(elem, "angle")
                axisElem = find(elem, "axis")
                axis = tuple(getVecAttr(axisElem, "xyz"))
                self.rotation = Quaternion(axis, angle)

            elif elem.tagName == "scale":
                if elem.hasAttribute("factor"):
                    self.scale = Vector(getFloatAttr(elem, "factor") for i in range(3))
                else:
                    self.scale = Vector(getVecAttr(elem, "xyz"))

def get_bone_order(armature):
    try:             return armature['tl2_id']
    except KeyError: return gen_bone_order(armature)

def is_root(bone): return bone.parent is None
def gen_bone_order(armature):
    result = []
    for root in filter(is_root, armature.bones):
        result.append(root.name)
        result.extend(child.name for child in root.children_recursive)
    return result

#----------------------------------------------------------------------------------------

def clear_scene_objects():
    objects_data  = bpy.data.objects
    objects_scene = bpy.context.scene.objects

    while(objects_scene):
        obj = objects_scene[0]
        obj.user_clear()
        objects_scene.unlink(obj)
        objects_data.remove(obj)
