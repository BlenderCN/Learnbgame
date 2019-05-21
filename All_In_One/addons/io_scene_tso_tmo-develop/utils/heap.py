
class Heap(object):
	def __init__(self):
		self.ary = []
		self.map = {}

	def append(self, key):
		if key not in self.map:
			idx = len(self.ary)
			self.map[key] = idx
			self.ary.append(key)
		else:
			idx = self.map[key]
		return idx

	def clear(self):
		del self.ary[:]
		self.map.clear()

