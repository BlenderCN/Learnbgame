# script to generate blank pythonic versions of the structs used with ModelExporter

from os.path import join

name = input('Please enter the (case sensitive!) name of the struct: ')
datacount = int(input('Enter how many lines of data you want: '))


def gen(name):
    s = '    '
    with open(join('../classes', '{0}.py'.format(name)), 'w') as f:
        f.writelines(['# {0} struct\n\n'.format(name),
                      'from .Struct import Struct\n\n',
                      "STRUCTNAME = '{0}'\n\n".format(name),
                      'class {0}(Struct):\n'.format(name),
                      s + 'def __init__(self, **kwargs):\n',
                      2*s + 'super({0}, self).__init__()\n\n'.format(name),
                      2*s + '""" Contents of the struct """\n',
                      datacount*(2*s + "self.data[''] = kwargs.get('', )\n"),
                      2*s + '""" End of the struct contents"""\n\n',
                      2*s + '# Parent needed so that it can be a SubElement of something\n',
                      2*s + 'self.parent = None\n',
                      2*s + 'self.STRUCTNAME = STRUCTNAME\n'])


if __name__ == '__main__':
    gen(name)
