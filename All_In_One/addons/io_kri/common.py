__author__ = ['Dzmitry Malyshau']
__bpydoc__ = 'Settings & Writing access for KRI exporter.'

class Settings:
	showInfo	= True
	showWarning	= True
	breakError	= False
	putNormal	= True
	putTangent	= False
	putQuat		= False
	putUv		= True
	putColor	= True
	compressUv	= True
	doQuatInt	= False
	fakeQuat	= 'Auto'
	logInfo		= True
	keyBezier	= False


class Writer:
	__slots__= 'fx', 'pos'
	def __init__(self, path):
		self.fx = open(path, 'wb')
		self.pos = []
	def size_of(self, tip):
		import struct
		return struct.calcsize(tip)
	def pack(self, tip, *args):
		import struct
		self.fx.write(struct.pack('<'+tip, *args))
	def array(self, tip, ar):
		import array
		array.array(tip, ar).tofile(self.fx)
	def text(self, *args):
		for s in args:
			x = len(s)
			assert x<256
			bt = bytes(s,'ascii')
			self.pack('B%ds'%(x), x, bt)
	def begin(self, name):
		import struct
		assert len(name) < 8
		bt = bytes(name, 'ascii')
		self.fx.write(struct.pack('<8sL', bt, 0))
		self.pos.append(self.fx.tell())
	def end(self):
		import struct
		pos = self.pos.pop()
		off = self.fx.tell() - pos
		self.fx.seek(-off-4, 1)
		self.fx.write(struct.pack('<L', off))
		self.fx.seek(+off+0, 1)
	def tell(self):
		return self.fx.tell()
	def close(self):
		assert len(self.pos) == 0
		self.fx.close()


class Logger:
	tabs = ('', "\t", "\t\t", "\t\t\t")
	__slots__= 'file', 'counter', 'stop'
	def __init__(self, path):
		self.file = open(path, 'w')
		self.counter = {'':0, 'i':0, 'w':0, 'e':0}
		self.stop = False
	def log(self, indent, level, message):
		self.counter[level] += 1
		if level=='i' and not Settings.showInfo:
			return
		if level=='w' and not Settings.showWarning:
			return
		if level=='e' and Settings.breakError:
			self.stop = True
		self.file.write("%s(%c) %s\n" % (Logger.tabs[indent], level, message))
	def logu(self, indent, message):
		self.file.write( "%s%s\n" % (Logger.tabs[indent], message) )
	def conclude(self):
		c = self.counter
		self.file.write('%d errors, %d warnings, %d infos' % (c['e'],c['w'],c['i']))
		self.file.close()
		self.counter.clear()



def save_color(out, rgb):
	for c in rgb:
		out.pack('B', int(255*c) )


def save_matrix(out,mx):
	import math
	pos,rot,sca = mx.decompose()
	scale = (sca.x + sca.y + sca.z)/3.0
	if math.fabs(sca.x-sca.y) + math.fabs(sca.x-sca.z) > 0.01:
		log.log(1,'w', 'non-uniform scale: (%.1f,%.1f,%.1f)' % sca.to_tuple(1))
	out.pack('8f',
		pos.x, pos.y, pos.z, scale,
		rot.x, rot.y, rot.z, rot.w )
