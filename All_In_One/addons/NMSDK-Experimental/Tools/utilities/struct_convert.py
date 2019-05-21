# struct converter
# gonna be pretty quick and nasty...

from os.path import join, exists

# change this to the absolute path where the structs are located (make sure you have the most recent version from github!!!)
STRUCTPATH = "E:\\NMS modding\\mod tool sources\\LibMBIN-1.3-atlasrises\\MBINCompiler\\libMBIN\\Source\\Models\\Structs"
BASEPATH = "../classes"

# name of the file all the entity panel stuff will get written to:
OUTPUT = "custom_panels_out.py"

NAMEMAP = {'int': 'IntProperty', 'float': 'FloatProperty', 'bool': 'BoolProperty', 'string': 'StringProperty', 'enum': 'EnumProperty'}
DEFAULTS = {'int': 0, 'float': 0, 'bool': 'False', 'string':"''", 'enum':'NEED DEFAULT VALUE!!!', 'list':'List()'}


class data():
    def __init__(self, line):
        self.type_ = line[0]
        self.name = line[1].replace(';', '').replace('\n', '')
        # self.name = self.name.rst

    def __str__(self):
        return '{0}, {1}'.format(self.type_, self.name)


def struct_init(name):
    pass


class struct_data():
    def __init__(self, name):
        self.name = name
        self.data = []
        self.substructs = dict()

        # strings for the layout and property data
        self.LayoutData = ''

        with open(join(STRUCTPATH, '{0}.cs'.format(self.name)), 'r') as struct:
            for line in struct:
                if 'public' in line:
                    # we only want lines that contain data
                    l = line.split(' ')
                    a = l[l.index('public') + 1:]       # a is a list with 2 values: first is the data type and second is the name
                    if a[0] != 'class':
                        if 'Values()' in a[1]:
                            # in this case we need to ret-con the previous value added :/
                            # this is actually an enum...
                            self.data[-1] = data(['enum', self.data[-1].name])
                        elif a[0] != 'byte[]':
                            self.add(data(a))

    def add(self, other):
        self.data.append(other)

    def run(self):
        # this will run all the methods
        self.ListToStruct()
        # all the structs need to be converted before doing layouts and such as we require the self.substructs dictionary to be populated
        self.ListToLayout()

        self.ListToProperty()

        # let's just do the property registering/unregistering here I think...
        s = self.get_substructs()
        rev_s = list(s)
        rev_s.reverse()
        #s.reverse()     # need to reverse to go from inner-most outwards to ensure registration occurs in the right order
        with open('_{0}_properties.py'.format(self.name), 'a') as f:
            f.write('\n# Registration stuff:\n\n')
            f.write('        bpy.utils.register_class(NMS_{0}_Properties)\n'.format(self.name))
            for etype in rev_s:
                f.write('        bpy.utils.register_class(NMS_{0}_Properties)\n'.format(etype))
            f.write('\n        bpy.types.Object.NMS_{0}_props = PointerProperty(type=NMS_{0}_Properties)\n'.format(self.name))
            f.write('\n\n')
            f.write('        bpy.utils.unregister_class(NMS_{0}_Properties)\n'.format(self.name))
            for etype in rev_s:
                f.write('        bpy.utils.unregister_class(NMS_{0}_Properties)\n'.format(etype))
            f.write('\n        del bpy.types.Object.NMS_{0}_props\n'.format(self.name))

    def get_substructs(self):
        # get all the structs all the way down
        s = list(self.substructs.keys())
        for struct in self.substructs:
            s += self.substructs[struct].get_substructs()
        return s

    def ListToProperty(self, child = False):
        # takes the list and produces python code for the EntityPanels.py file to create a new property
        pre = '    '        # set as 4 spaces

        print('generating property for {0}'.format(self.name))
        
        output = 'class NMS_{0}_Properties(bpy.types.PropertyGroup):\n'.format(self.name)
        output += pre + '""" Properties for {0} """\n'.format(self.name)

        additional_output = []

        for entry in self.data:
            if entry.type_ in NAMEMAP.keys():
                output += pre + '{0} = {1}(name = "{0}")\n'.format(entry.name, NAMEMAP[entry.type_])
                continue
            elif 'List' not in entry.type_:
                etype = entry.type_
                output += pre + '{0} = PointerProperty(type = NMS_{1}_Properties)\n'.format(entry.name, entry.type_)
            else:
                etype = entry.type_.replace('List<', '').rstrip('>')
                output += pre + '{0} = CollectionProperty(type = NMS_{1}_Properties)\n'.format(entry.name, etype)
            # if this code is read then we have a struct as the object type and need to make it's properties too
            additional_output += self.substructs[etype].ListToProperty(child = True)

        if additional_output == []:
            if child:
                return [output, '\n\n']
            else:
                with open('_{0}_properties.py'.format(self.name), 'w') as f:
                    f.write(output)
        else:
            if child:
                return additional_output + ['\n\n', output, '\n\n']
            else:
                with open('_{0}_properties.py'.format(self.name), 'w') as f:
                    f.write(output)
                    f.writelines(additional_output)

    def ListToLayout(self, parent = None, ctx = 'r', inlist = '', listparent = ''):
        # parent is a given string to write to so that we can call this recursively
        # ctx is the current depth of recursion (effectively). It's the variable name for the current layout level.
        # inlist is the sub elements of the listparent. ie. the Name in listparent_prop
        # listparent is the parent class that all the variables are derived from.
        pre = '    '        # set as 4 spaces

        if parent is None:
            if inlist != '':
                output = pre + 'def {0}(self, layout, obj, index = 0):\n'.format(self.name)
                # need to fix up listparent a bit...
                s = listparent.split('.')
                name = s[0] + "_props"
                for i in s[1:]:
                    name += '.{0}'.format(i)
                output += 2*pre + 'r = RowGen(obj.NMS_{0}_props{1}[index], layout)\n'.format(name, inlist)
            else:
                output = pre + 'def {0}(self, layout, obj):\n'.format(self.name)
                output += 2*pre + 'r = RowGen(obj.NMS_{0}_props, layout)\n'.format(self.name)
                listparent = self.name
        else:
            self.ListToStruct()
            output = parent
        for entry in self.data:
            if entry.type_ in NAMEMAP.keys():
                output += 2*pre + '{0}.row("{1}")\n'.format(ctx, entry.name)
            elif 'List' not in entry.type_:
                box_num = 'b1' if ctx == 'r' else 'b{0}'.format(int(ctx[1:])+1)
                output += 2*pre + '{0} = {1}.box("{2}")\n'.format(box_num, ctx, entry.name)
                output = self.substructs[entry.type_].ListToLayout(output, box_num, listparent = listparent + '.' + entry.name)
            else:
                etype = entry.type_.replace('List<', '').rstrip('>')
                output += 2*pre + '{0}.listbox(self, obj, "NMS_{1}_props", "{2}", "{3}")\n'.format(ctx, listparent, entry.name, etype)          """ need to remove the _props ??? """
                # we also need to call the ListToLayout method on the sub class so it can be generated
                # in this case we will not pass output as the parent, as we need an entirely new layout
                self.substructs[etype].ListToLayout(inlist = inlist + '.{0}'.format(entry.name), listparent = listparent)

        if parent is None:
            # in this case we just want to assign the data locally
            self.LayoutData = output
            with open('_{0}_layoutdata.py'.format(self.name), 'w') as f:
                f.write(self.LayoutData)
        else:
            # if we have a parent, we need to return the output as the data is passed by value to the function
            return output

    def ListToStruct(self):
        pre = '    '        # set as 4 spaces

        # need to pre-parse the list to find any dependences
        # can also tack on the recusion here as we are checking for classes
        import_needs = set()
        for entry in self.data:
            if 'List' in entry.type_:
                import_needs.add('List')
                # determine the actual type and then call this method on a newly created struct_data class object:
                etype = entry.type_.replace('List<', '').rstrip('>')
            elif entry.type_ not in DEFAULTS.keys():
                etype = entry.type_
                import_needs.add(entry.type_)
            else:
                # in this case move onto the next case and don't run the code after this in the loop
                continue
            # now create a new class for this etype and call it's ListToStruct method to map all structs that haven't already been mapped
            cls = struct_data(etype)
            self.substructs[etype] = cls
            if not exists(join(BASEPATH, '{0}.py'.format(etype))):
                cls.ListToStruct()
        if not exists(join(BASEPATH, '{0}.py'.format(self.name))):
            with open(join(BASEPATH, '{0}.py'.format(self.name)), 'w') as f:
                f.writelines(['# {0} struct\n\n'.format(self.name),
                              'from .Struct import Struct\n'])
                for s in import_needs:
                    f.writelines(['from .{0} import {0}\n'.format(s)])
                f.writelines(["\nSTRUCTNAME = '{0}'\n\n".format(self.name),
                              'class {0}(Struct):\n'.format(self.name),
                              pre + 'def __init__(self, **kwargs):\n',
                              2*pre + 'super({0}, self).__init__()\n\n'.format(self.name),
                              2*pre + '""" Contents of the struct """\n'])
                for entry in self.data:
                    if entry.type_ in DEFAULTS.keys():
                        f.writelines([2*pre + "self.data['{0}'] = kwargs.get('{0}', {1})\n".format(entry.name, DEFAULTS[entry.type_])])
                        if entry.type_ == 'enum':
                            print('The file {0}.py has one or more values that need to be entered manually!'.format(self.name))
                    elif 'List' not in entry.type_:
                        f.writelines([2*pre + "self.data['{0}'] = kwargs.get('{0}', {1}())\n".format(entry.name, entry.type_)])
                    else:
                        f.writelines([2*pre + "self.data['{0}'] = kwargs.get('{0}', {1})\n".format(entry.name, 'List()')])
                f.writelines([2*pre + '""" End of the struct contents"""\n\n',
                              2*pre + '# Parent needed so that it can be a SubElement of something\n',
                              2*pre + 'self.parent = None\n',
                              2*pre + 'self.STRUCTNAME = STRUCTNAME\n'])

        # we also want to add the file to the list of imported file in __init__.py
        # first, check whether or not the file is already in it
        found = False
        with open(join(BASEPATH, '__init__.py'), 'r') as file:
            for line in file:
                if self.name in line:
                    found = True
                    break
        if not found:
            with open(join(BASEPATH, '__init__.py'), 'a') as file:
                file.writelines(['from .{0} import {0}\n'.format(self.name)])


if __name__ == "__main__":

    fname = input('enter the filename: ')
    #fname = "GcInteractionComponentData"

    cls = struct_data(fname)
    cls.run()

    """

    #for d in cls.data:
    #    print(d)
    print(cls.ListToProperty())
    print('\n\n\n\n')
    print(cls.ListToLayout())
    cls.ListToStruct()"""
