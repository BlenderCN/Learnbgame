from io import StringIO
from functools import cmp_to_key
from collections import OrderedDict

class Tag:
	def __init__(self, tag, attr=[], single=False):
		self.tag = tag
		self.attr = attr
		self.sub = []
		self.single = single

	def write(self, w, nice=True, level=0, indent="  ", loop=0):
		if nice:
			w(indent*level)

		w("<%s" % self.tag)

		def cmpfunc(x,y):
			if x[0]=="id":
				return -1
			if y[0]=="id":
				return 1
			#TODO order strings here?
			return 0

		for k,v in sorted(self.attr, key=cmp_to_key(cmpfunc)):
			w(" %s=\"%s\"" % (k, str(v)))

		if len(self.sub)==0 and not self.single:
			w(" />")
		else:
			if self.tag=="Object":
				w(" ")
			w(">")
		# self.sub must not be indented, as Text objects are sensitive to this under some conditions (tried on JanusVR 54.1 under Wine 1.9.23) and will result in bells.
		# Maybe that's a bug in JanusVR, maybe that's a bug in Wine, maybe that's a bug here, in any case, this works around it.
		for i,s in enumerate(self.sub):
			if isinstance(s, str):
				w(s)
			else:
				#if loop<n: prevent recursion
				if i==0:
					w("\n")
				s.write(w, nice, level+(0 if self.single else 1), indent, loop+1)

		if len(self.sub)==0 and nice and not self.single:
			w(indent*(level))
		if not len(self.sub)==0 and not self.single:
			w(indent*(level))
			w("</%s>" % self.tag)
		if nice:
			w("\n")


	def __call__(self, tag):
		#print("Adding %s to %s" % (tag.tag, self.tag))
		self.sub.append(tag)

	def __contains__(self, tag):
		return tag in self.sub

	def __repr__(self):
		s = StringIO()
		self.write(s.write)
		s.seek(0)
		return s.read()
