import zipfile
import os

file_list = os.listdir(r'.')

for file_name in file_list:
    file_zip = file_name+".zip"
    file_zip = zipfile.ZipFile(file_zip, 'w')
    for dirpath,dirnames,filenames in os.walk(file_name):
    	for f in filenames:
    		file_zip.write(os.path.join(dirpath,f))
    file_zip.close()
