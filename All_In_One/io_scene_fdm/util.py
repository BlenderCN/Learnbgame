'''
Created on 10.12.2011

@author: tom
'''
import xml.dom.minidom as dom

def float2str(val, max_acc = 3):
	'''
	@param val			The value
	@param max_acc	Maximum accuracy
	'''
	val_rounded = round(val, max_acc)
	acc = max_acc
	while acc > 0:
		if abs(val_rounded - round(val, acc - 1)) > 0:
			return str(val_rounded)
		
		acc -= 1
		val_rounded = round(val, acc)

	return str(int(val_rounded))

class XMLDocument(dom.Document):
		'''
		XML helper class to simplify dom creation
		'''

		def __init__(self, name_root_element):
				'''
				Constructor
				'''
				super().__init__()
				self.__root = self.createElement(name_root_element)
				self.appendChild(self.__root)
				
		def root(self):
				'''
				Get the root element
				'''
				return self.__root

		def createElement(self, tag_name):
				e = XMLElement(tag_name)
				e.ownerDocument = self
				return e
		
		def createChild(self, tag_name, text = ''):
				return self.root().createChild(tag_name, text)

				
class XMLElement(dom.Element):
		
		def __init__(self, tag_name):
				super().__init__(tag_name)
				
		def createChild(self, tag_name, text = ''):
				e = XMLElement(tag_name)
				e.ownerDocument = self.ownerDocument
				self.appendChild(e)
				
				if len(str(text)):
						t = e.ownerDocument.createTextNode(str(text))
						e.appendChild(t)
				return e
		
		def createPropChild(self, tag_name, value, unit=''):
				'''
				Create a xml element representing a (numeric) property with an optional
				unit attribute
				'''
				if( type(value) == float ):
						value = float2str(value)
				else:
						value = str(value)

				c = self.createChild(tag_name, value)
				if len(unit):
						c.setAttribute('unit', unit)				
				return c
			
		def createVectorChild(self, tag_name, vec, unit_suffix = ''):
				v = self.createChild(tag_name)
				v.createPropChild('x' + unit_suffix, vec[0])
				v.createPropChild('y' + unit_suffix, vec[1])
				v.createPropChild('z' + unit_suffix, vec[2])
				
				return v
			
		def createCenterChild(self, arg1, arg2 = None):
			'''
			Create a node with the center of the given object
			
			@param center	Vector3
			'''
			if not arg2:
				name = 'center'
				center = arg1
			else:
				name = arg1
				center = arg2
			return self.createVectorChild(name, center, unit_suffix = '-m')
		
		def writexml(self, writer, indent="", addindent="", newl=""):
				if (		 len(self.childNodes) == 1
								 and self.childNodes[0].nodeType == dom.Node.TEXT_NODE ):
						writer.write(indent)
						super().writexml(writer)
						writer.write(newl)
				else:
						super().writexml(writer, indent, addindent, newl)

def getAllChildren(ob, filter_type = ''):
	'''
	Get all children of the given object optionally filtered by a flightgear
	object type.
	'''
	children = []

	for child in ob.children:
		if filter_type == '' or child.fgfs.type == filter_type:
			children.append(child)
		children.extend( getAllChildren(child, filter_type) )

	return children
