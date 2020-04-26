import sys
import pathlib
here=pathlib.Path(__file__).parent
root=here.parent
pymeshio_path= root / 'pymeshio'
sys.path.append(str(pymeshio_path.absolute()))
sys.path.append(str(root.parent.absolute())) # __init__.py

import os
import shutil
import blpymeshio
#print(blpymeshio.bl_info)


def copy_files(dst: pathlib.Path, src: pathlib.Path, excludes=[], root: pathlib.Path=None):
	if not root:
		root=src

	for x in src.iterdir():
		if x==dst:
			continue
		elif x in excludes:
			continue
		elif x.is_dir():
			copy_files(dst, x, excludes, root)
		elif x.suffix=='.py':
			if str(x.absolute())==__file__: # skip _create_zip.py
				continue
			#print(x)
			relative=x.relative_to(root)

			target=dst/relative
			print(target)

			if not target.parent.exists():
				target.parent.mkdir()

			shutil.copyfile(x, target)


def main():
	v=blpymeshio.bl_info['version']
	version_str=f'{v[0]}.{v[1]}.{v[2]}'
	archive_file=f'blpymeshio-{version_str}.zip'
	if os.path.exists(archive_file):
		os.remove(archive_file)

	dst=root / 'tmp'
	if not dst.exists():
		os.makedirs(dst)

	# dst, root, src
	copy_files(dst / 'blpymeshio', root,
            [pymeshio_path]
            )

	if not (dst/'blpymeshio/pymeshio').exists():
		os.makedirs(dst / 'blpymeshio/pymeshio')

	copy_files(dst / 'blpymeshio/pymeshio', pymeshio_path, [
            pymeshio_path / 'bench.py',
            pymeshio_path / 'setup.py',
            pymeshio_path / 'test',
            pymeshio_path / 'examples'
        ])

	shutil.make_archive(str(archive_file)[0:-4], 'zip', dst)

	shutil.rmtree(dst)

if __name__=='__main__':
	main()
