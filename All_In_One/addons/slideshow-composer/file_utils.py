from os import listdir
from os.path import isfile, isdir, dirname, join, splitext
from re import match

IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff', 'tga']
MOVIE_EXTENSIONS = ['mp4', 'mpg', 'mpeg', 'avi', 'flv', 'mkv']


def find_files_recursively(path_list, extension_list=[*IMAGE_EXTENSIONS, *MOVIE_EXTENSIONS]):
    found_files = []
    pattern = '|'.join(['(' + ext_pattern + ')' for ext_pattern in ['.*\.' + ext for ext in extension_list]])
    for path in path_list:
        if isfile(path) and match(pattern, path):
            print('Found file {}'.format(path))
            found_files.append(path)
        if isdir(path):
            print('Recursively importing directory {}'.format(path))
            files_in_dir = [join(path, file) for file in listdir(path)]
            print('Files in directory: {}'.format(len(files_in_dir)))
            found_files.extend(
                find_files_recursively(path_list=files_in_dir,
                                       extension_list=extension_list))
    return found_files


def find_files_recursively_in_dir(directory, file_list, extension_list=[*IMAGE_EXTENSIONS, *MOVIE_EXTENSIONS]):
    return find_files_recursively(path_list=[join(directory, file) for file in file_list],
                                  extension_list=extension_list)


def is_image(path):
    (root, ext) = splitext(path)
    return ext.lower()[1:] in IMAGE_EXTENSIONS


def is_movie(path):
    (root, ext) = splitext(path)
    return ext.lower()[1:] in MOVIE_EXTENSIONS
