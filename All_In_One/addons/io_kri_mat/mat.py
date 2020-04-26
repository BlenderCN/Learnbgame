__author__ = ['Dzmitry Malyshau']
__bpydoc__ = 'Material Library module of KRI exporter.'

import mathutils
from xml.dom.minidom	import Document
from io_kri.action	import *
from io_kri.common	import *


def save_mat(filename,context):
	# ready...
	# steady...
	print('Exporting Material Library.')
	doc = Document()
	mat = doc.createElement('kri:Material')
	mat.attributes['xmlns:kri'] = 'world'
	doc.appendChild(mat)
	meta = doc.createElement('kri:Meta')
	mat.appendChild(meta)
	meta.appendChild( doc.createTextNode('') )
	data = doc.createElement('kri:Data')
	mat.appendChild(data)
	# go!
	text = doc.toprettyxml(indent="\t")
	file = open(filename,'w')
	file.write(text)
	file.close()
	# animations
	# done
	print('Done.')
