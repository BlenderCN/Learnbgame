import os
import re

houdini_search_path = [R'C:/Program Files/Side Effects Software']
m_hversion = re.compile('Houdini (\d+\.\d+\.\d+)')

def find_houdini():
	result = {}
	for x in houdini_search_path:
		arr = list(os.listdir(x))
		arr.reverse()
		for y in arr:
			m = m_hversion.search(y)
			if m:
				result[m.groups()[0]] = os.path.normpath( os.path.join(x, y) )
	return result

def append_path(HFS):
	bin_dir = os.path.join(HFS, 'bin')
	if not bin_dir in os.environ['PATH']:
		os.environ['PATH'] = ';'.join((bin_dir, os.environ['PATH']))
		print('HFS: %s' % HFS)

if __name__ == "__main__":
	k = find_houdini()
	print(k)
