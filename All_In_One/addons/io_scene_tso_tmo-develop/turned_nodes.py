from os import path
import re

rotation_nodes = set()
translation_nodes = set()

filename = path.join(path.dirname(__file__), "resources/turned-nodes.txt")

with open(filename) as f:
	for line in f:
		line = re.sub('\n', '', line)  # chomp
		name, r, t = line.split('\t')
		if r == 'R':
			# print('R {}'.format(name))
			rotation_nodes.add(name)
		if t == 'T':
			# print('T {}'.format(name))
			translation_nodes.add(name)

def in_rotation(name):
	return name in rotation_nodes

def in_translation(name):
	return name in translation_nodes

def turned_matrix4(m, name):
	# print("name {} R {} T {}".format(name, in_rotation(name), in_translation(name)))
	m = [ [ col for col in row ] for row in m ]

	if in_rotation(name):
		m[0][0] = -m[0][0]
		m[0][1] = -m[0][1]
		m[0][2] = -m[0][2]
		m[2][0] = -m[2][0]
		m[2][1] = -m[2][1]
		m[2][2] = -m[2][2]

	if in_translation(name):
		m[0][1] = -m[0][1]
		m[1][0] = -m[1][0]
		m[1][2] = -m[1][2]
		m[2][1] = -m[2][1]
		m[3][0] = -m[3][0]  # x
		m[3][2] = -m[3][2]  # z

	return m

if __name__ == "__main__":
	print(in_rotation('Head'))
	print(in_translation('Head'))
	print(in_rotation('face_oya'))
	print(in_translation('face_oya'))
