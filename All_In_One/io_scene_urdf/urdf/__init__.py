from .exception import URDFException
from .collision import Collision
from .color import Color
from .dynamics import Dynamics
from .geometry import Geometry
from .inertial import Inertial
from .joint import Joint
from .link import Link
from .visual import Visual

import xml.dom.minidom
from xml.dom.minidom import Document

def add(doc, base, element):
    if element is not None:
        base.appendChild( element.to_xml(doc) )

def pfloat(x):
    return ('%f'%x).rstrip('0').rstrip('.')

def set_attribute(node, name, value):
    if value is None:
        return
    if type([]) == type(value) or type(()) == type(value):
        value = " ".join( [pfloat(a) for a in value] )
    elif type(value) == type(0.0):
        value = pfloat(value)
    elif type(value) != type(''):
        value = str(value)
    node.setAttribute(name, value)

def short(doc, name, key, value):
    element = doc.createElement(name)
    set_attribute(element, key, value)
    return element

def children(node):
    children = []
    for child in node.childNodes:
        if child.nodeType is node.TEXT_NODE or child.nodeType is node.COMMENT_NODE:
            continue
        else:
            children.append(child)
    return children

class Pose(object):
    def __init__(self, position=None, orientation=None):
        self.position = position
        self.orientation = orientation

    @staticmethod
    def parse(node):
        pose = Pose()
        if node.hasAttribute("xyz"):
            xyz = node.getAttribute('xyz').split()
            pose.position = list(map(float, xyz))
        if node.hasAttribute("rpy"):
            rpy = node.getAttribute('rpy').split()
            pose.orientation = list(map(float, rpy))
        return pose

    def to_xml(self, doc):
        xml = doc.createElement("origin")
        set_attribute(xml, 'xyz', self.position)
        if self.orientation:
            set_attribute(xml, 'rpy', self.orientation)
        return xml

class SafetyController:
    def __init__(self, velocity, position=None, lower=None, upper=None):
        self.velocity = velocity
        self.position = position
        self.lower = lower
        self.upper = upper

    @staticmethod
    def parse(node):
        sc = SafetyController( float(node.getAttribute('k_velocity')) )
        if node.hasAttribute('soft_lower_limit'):
            sc.lower = float( node.getAttribute('soft_lower_limit') )
        if node.hasAttribute('soft_upper_limit'):
            sc.upper = float( node.getAttribute('soft_upper_limit') )
        if node.hasAttribute('k_position'):
            sc.position = float( node.getAttribute('k_position') )
        return sc

    def to_xml(self, doc):
        xml = doc.createElement('safety_controller')
        set_attribute(xml, 'k_velocity', self.velocity)
        set_attribute(xml, 'k_position', self.position)
        set_attribute(xml, 'soft_upper_limit', self.upper)
        set_attribute(xml, 'soft_lower_limit', self.lower)
        return xml
        

class URDF:
    def __init__(self, name=""):
        self.name = name
        self.elements = []
        self.links = {}
        self.joints = {}
        self.joint_list = []
        self.materials = {}

        self.parent_map = {}
        self.child_map = {}

    def parse(self, xml_string):
        doc = xml.dom.minidom.parseString(xml_string)
        return self.build(doc)

    def load(self, filename):
        f = open(filename, 'r')
        return self.parse(f.read())

    def build(self, doc):
        robot = children(doc)[0]
        self.name = robot.getAttribute('name')
        for node in children(robot):
            if node.nodeType is node.TEXT_NODE:
                continue
            if node.localName == 'joint':
                self.add_joint( Joint.parse(node) )
            elif node.localName == 'link':
                self.add_link( Link.parse(node) )
            elif node.localName == 'material':
                self.elements.append( Material.parse(node) )
            elif node.localName == 'gazebo':
                None #Gazebo not implemented yet
            elif node.localName == 'transmission':
                None #transmission not implemented yet
            else:
                raise URDFException("Unknown robot element '%s'"%node.localName)
                
    def add_link(self, link):
        self.elements.append(link)
        self.links[link.name] = link

    def add_joint(self, joint):
        self.elements.append(joint)
        self.joint_list.append(joint.name)
        self.joints[joint.name] = joint

        self.parent_map[ joint.child ] = (joint.name, joint.parent)
        if joint.parent in self.child_map:
            self.child_map[joint.parent].append( (joint.name, joint.child) )
        else:
            self.child_map[joint.parent] = [ (joint.name, joint.child) ]
    

    def get_chain(self, root, tip, joints=True, links=True):
        chain = []
        if links:
            chain.append(tip)
        link = tip
        while link != root:
            (joint, parent) = self.parent_map[link]
            if joints:
                chain.append(joint)
            if links:
                chain.append(parent)
            link = parent
        chain.reverse()
        return chain

    def to_xml(self):
        doc = Document()
        root = doc.createElement("robot")
        doc.appendChild(root)
        root.setAttribute("name", self.name)

        for element in self.elements:
            root.appendChild(element.to_xml(doc))

        return doc.toprettyxml()
