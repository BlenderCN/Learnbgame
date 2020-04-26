import os
import rvstruct
import shutil

rvgl_dir = "/home/marv/.rvgl/"

if os.path.isdir("tests"):
	shutil.rmtree("tests")

os.makedirs("tests")


def read_file(rvclass, test_path):
	print("Reading", test_path)

	with open(test_path, "rb") as f:
		try:
			rv = rvclass(f)
		except Exception as e:
			print("That did not work:\n",e)

	return rv


def write_file(rvinstance, test_path):
	print("writing", test_path)

	with open(test_path, "wb") as f:
		try:
			rvinstance.write(f)
		except Exception as e:
			print("That did not work:\n",e)


# .rim
rim = read_file(rvstruct.RIM, os.path.join(rvgl_dir, "levels/muse1/muse1.rim"))
write_file(rim, "tests/test.rim")

# hull
hull = read_file(rvstruct.Hull, os.path.join(rvgl_dir, "cars/adeon/hull.hul"))
write_file(hull, "tests/hull.hul")

print("All tests done.")