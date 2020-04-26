#call other processes
import subprocess, os, glob, shutil

import pdb, unittest

def p2w(str):
	return str.replace('/', '\\')

def w2p(str):
	return str.replace('\\', '/')

def clear(p):
	result = w2p(p)
	return result.replace('//', '/')

def delete(path):
	if os.path.exists(path) and os.path.isfile(path):
		os.remove(path)
	else:
		print("warning: can't remove file (",path,'). It doesn\'t exist')	

def rmdir(path, cwd=".\\"):
	if os.path.exists(cwd+'/'+path):
		shutil.rmtree(cwd+'/'+path, ignore_errors=True)
	else:
		print("warning: can't remove directory ("+cwd+'/'+path+'). It doesn\'t exist')
	"""
	subprocess.call(['rmdir', 
		'/q', #quiet
		'/s', #remove empty folder
		p2w(path)], cwd=cwd, shell=True)
	"""

def mkdir(path, cwd=".\\"):
	#print("mkdir: ", path)
	if not os.path.exists(cwd+'/'+path):
		os.makedirs(cwd+'/'+path)
	else:
		print("warning: can't create directory ("+cwd+'/'+path+'). It exists already')
	"""
	folders = path.split("/")
	acc = ""
	for folder in folders:
		acc += folder
		subprocess.call(['mkdir', 
			acc], shell=True, cwd=cwd)
		acc += '\\'
	"""
def copy(source, dest):
	shutil.copyfile(source, dest)
	
def move(source, dest):
	shutil.move(source, dest)

def xcopy(source, dest):
	#print("xcopy: ", source, ', ', dest)
	shutil.copytree(source, dest)
	"""
	subprocess.call(['xcopy', 
		'/q', #quiet
		'/y', #overwrite
		'/s', #subfolders
		p2w(source), 
		p2w(dest)])
	"""


class TestMethods(unittest.TestCase):
	def test_p2w(self):
		self.assertEqual('\\', p2w('/'))
		self.assertEqual('\\folder1\\', p2w('/folder1/'))
		self.assertEqual('folder1\\asdf\\asdf', p2w('folder1/asdf/asdf'))

	def test_w2p(self):
		self.assertEqual('/', w2p('\\'))
		self.assertEqual('/folder1/', w2p('\\folder1\\'))
		self.assertEqual('folder1/asdf/asdf', w2p('folder1\\asdf\\asdf'))
	
	def test_mkdir(self):
		before = len(glob.glob('./*'))
		mkdir('test')
		after = len(glob.glob('./*'))
		self.assertEqual(before+1, after)
		
		before = len(glob.glob('./test/*'))
		mkdir('test2/test3', 'test')
		after = len(glob.glob('./test/test2/test3'))
		self.assertEqual(before+1, after)
	
	def test_rmdir(self):
		before = len(glob.glob('./test/test2/*'))
		rmdir('test3', 'test/test2/')
		after = len(glob.glob('./test/test2/*'))
		self.assertEqual(before-1, after)

		before = len(glob.glob('./test'))
		rmdir('test')
		after = len(glob.glob('./test'))
		self.assertEqual(before-1, after)

	def test_xcopy(self):
		#setup
		mkdir('test/test2/test3')
		subprocess.call(["echo", "1", ">>", 
			"test\\test2\\test3\\t.txt"], shell=True)
		#mkdir('testcopy')
		#test
		xcopy('test/test2', 'testcopy/')
		self.assertEqual(len(glob.glob('./testcopy/*')), 1)
		#clean
		rmdir('test')
		rmdir('testcopy')

if __name__ == '__main__':
    unittest.main()