#!/usr/bin/env python

"""Partition: partition bone combination set into palettes
cf. Skin Splitting for Optimal Rendering
http://www.gameenginegems.net/gemsdb/article.php?id=423
"""

class Partition(object):

	def __init__(self, comb_set, nodes_len):
		self.comb_set = comb_set
		self.nodes_len = nodes_len

		# result data
		self.palettes = []
		self.comb_palette_map = {}

		self.init_bone_counts()

	def empty(self):
		return max(self.bone_counts) == 0

	def inc(self, comb):
		for i in comb:
			self.bone_counts[i] += 1

	def dec(self, comb):
		for i in comb:
			self.bone_counts[i] -= 1

	def init_bone_counts(self):
		# count bones in comb_set
		self.bone_counts = []

		# todo: nodes_len from max(comb in comb_set) ?
		for i in range(self.nodes_len):
			self.bone_counts.append(0)

		for comb in self.comb_set:
			self.inc(comb)

	def find_bone_min_combs(self):
		min_combs = len(self.comb_set)+1
		bone = -1
		for i, c in enumerate(self.bone_counts):
			if c > 0 and c < min_combs:
				min_combs = c
				bone = i
		return bone

	def reached(self):
		return len(self.palette) == 16

	def add_bone(self, bone):
		self.palette.add(bone)

	def add_bones_shared(self, selected_bone):
		for comb in self.comb_set:
			if selected_bone in comb:
				for bone in comb:
					self.add_bone(bone)
					if self.reached():
						return

	def issubset(self, comb):
		return set(comb).issubset(self.palette) 

	def assign(self, comb):
		self.comb_palette_map[comb] = len(self.palettes)
		pass

	def remove_subset_combs(self):
		# avoid RuntimeError: Set changed size during iteration
		removing_combs = []
		for comb in self.comb_set:
			if self.issubset(comb):
				self.dec(comb)
				self.assign(comb)
				removing_combs.append(comb)

		for comb in removing_combs:
			self.comb_set.remove(comb)

	def once(self):

		self.palette = set()

		while True:
			# 2. 最小combinationを持つboneをみつける
			bone = self.find_bone_min_combs()

			# 3. paletteにそのboneを追加
			self.add_bone(bone)
			if not self.reached():
				# 4. このboneとcombinationを共有するboneを上限まで追加
				self.add_bones_shared(bone)

			# 5. このpaletteに含まれたcombinationを削除
			self.remove_subset_combs()

			if self.empty():
				return {'EMPTY'}

			if self.reached():
				return {'REACHED'}


	def run(self):
		# 6. 全てのcombinationがpaletteのひとつに含まれるまで繰り返す
		status = set()
		while not 'EMPTY' in status:
			status = self.once()
			self.palettes.append(self.palette)

		return status

if __name__ == "__main__":

	comb_set = {(0,), (0, 4, 5), (0, 3, 4), (0, 1, 2), (0, 1, 3), (0, 3)}
	nodes_len = 6

	partition = Partition(comb_set, nodes_len)

	print("len bone_counts:{}".format(len(partition.bone_counts)))
	print("bone_counts:{}".format(partition.bone_counts))

	print(partition.run())

	print("len palattes:{}".format(len(partition.palettes)))
	print("palattes:{}".format(partition.palettes))

	print("comb palette map:{}".format(partition.comb_palette_map))
