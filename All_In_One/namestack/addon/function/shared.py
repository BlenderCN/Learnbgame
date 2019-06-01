
# imports
import re
from .. import storage

# main
def main(self, context, collection, option):
    '''
        Sorts recieved collection if at all based on alphabetical or positional information.
    '''

    # is sort
    if option.sort:

        # sort
        try: collection.sort(reverse=option.invert)
        except: pass

        # is positional
        if option.type == 'POSITIONAL':

            # get position
            for name in collection:

                # has location
                if hasattr(name[3][0], 'location'):

                    # is axis x
                    if option.axis == 'X':
                        name[0] = abs(name[3][0].location[0])

                    # is axis y
                    elif option.axis == 'Y':
                        name[0] = abs(name[3][0].location[1])

                    # axis z
                    else:
                        name[0] = abs(name[3][0].location[2])

            # sort
            try: collection.sort(reverse=option.invert)
            except: pass

    # is count
    if option.count:
        count(self, context, collection, option)

    # isnt count
    else:

        # batch
        batch = context.window_manager.BatchName

        # apply names
        for name in collection:

            suffix = (batch.suffix if batch.suffixLast else '') if self.bl_label == 'Batch Name' else ''

            # has name
            if hasattr(name[3][0], 'name'):

                # name
                name[1] = name[1] + suffix
                name[3][0].name = name[1]

            # has info
            if hasattr(name[3][0], 'info'):

                # info
                name[1] = name[1] + suffix
                name[3][0].info = name[1]

            # has bl_label
            if hasattr(name[3][0], 'bl_label'):

                # bl_label
                name[1] = name[1] + suffix
                name[3][0].bl_label = name[1]

            # count
            if name[1] != name[2]:
                self.count += 1

# count
def count(self, context, collection, option):
    '''
        Makes dict of names catagorizing them based on name or suffix, counts, applies and links names to the datablocks.
    '''

    # names
    names = {}

    # suffix
    suffix = r'\W([A-z]*)$|_([A-z]*)$'

    # numeral
    numeral = r'\W[0-9]*$|_[0-9]*$'

    # is option ignore
    if option.ignore:

        # process collection
        for name in collection:

            # check
            check = re.split(numeral, name[1])[0]

            # update
            name[1] = re.split(numeral, name[1])[0]

            # search suffix; sub.key
            if re.search(suffix, check):

                # check
                check = re.split(suffix, check)[0]

                # search numeral before suffix; sub.01.key
                if re.search(numeral, check):

                    # set key, sub
                    try: names.setdefault(re.split(suffix, name[1])[1], {}).setdefault(re.split(numeral, check)[0], []).append(name)
                    except: names.setdefault('main', {}).setdefault(re.split(numeral, check)[0], []).append(name)

                    # update
                    try: name[3][1] = re.split(suffix, name[1])[1]
                    except: pass
                    name[1] = re.split(numeral, check)[0]

                # isnt numeral before suffix; sub.key
                else:

                    # is in positional
                    if re.split(suffix, re.split(numeral, name[1])[0])[1].upper() in (position for position in storage.batch.positional):

                        # key
                        try: names.setdefault(re.split(suffix, name[1])[1], {}).setdefault(check, []).append(name)
                        except: names.setdefault('main', {}).setdefault(check, []).append(name)

                        # update
                        try: name[3][1] = re.split(suffix, name[1])[1]
                        except: pass
                        name[1] = check

            # isnt suffix; sub
            else:

                # main
                names.setdefault('main', {}).setdefault(check, []).append(name)

                # update
                name[1] = check

    # isnt option ignore
    else:
        for name in collection:

            # update
            name[1] = re.split(numeral, name[1])[0]

            # main
            names.setdefault('main', {})

            # set default name and add collection name item
            names['main'].setdefault(name[1], []).append(name)

    # done with collection
    collection.clear()

    # # test
    # for key in names:
    #     print('\n' + key)
    #     for sub in names[key]:
    #         print('\n' + '    ' + sub + '\n')
    #         for i, name in enumerate(names[key][sub]):
    #             print('        ' + str(name[0]))

    # count names
    for key in names:
        for sub in names[key]:
            for i, name in enumerate(names[key][sub]):

                # is more then 1
                if len(names[key][sub]) > 1:

                    # count
                    count = str((i + option.start)*option.step).zfill(len(str(len(names[key][sub])*option.step)))

                    # update
                    name[1] = name[1] + option.separator + '0'*option.pad + count

                # is suffix
                if name[3][1] != '':

                    # update
                    name[1] = name[1] + option.separator + name[3][1]

    # batch
    batch = context.window_manager.BatchName

    # apply names
    for key in names:
        for sub in names[key]:
            for name in names[key][sub]:

                # has name
                if hasattr(name[3][0], 'name'):

                    # name
                    name[1] = name[1] + batch.suffix if batch.suffixLast else name[1]
                    name[3][0].name = name[1]

                # has info
                elif hasattr(name[3][0], 'info'):

                    # name
                    name[1] = name[1] + batch.suffix if batch.suffixLast else name[1]
                    name[3][0].info = name[1]

                # has bl_label
                elif hasattr(name[3][0], 'bl_label'):

                    # name
                    name[1] = name[1] + batch.suffix if batch.suffixLast else name[1]
                    name[3][0].bl_label = name[1]

                # count
                if name[1] != name[2]:
                    self.count += 1

    # link
    if option.link:
        for key in names:
            for sub in names[key]:
                for name in names[key][sub]:

                    # is linkable
                    if len(name[3]) == 3:

                        # source
                        source = names[key][sub][0][3][0]

                        # actions
                        if name[3][0].rna_type.identifier == 'Action':

                            # link
                            name[3][2].action = source

                        # grease pencils
                        if name[3][0].rna_type.identifier == 'GreasePencil':

                            # link
                            name[3][2].grease_pencil = source

                        # cameras
                        if name[3][0].rna_type.identifier == 'Camera':

                            # link
                            name[3][2].data = source

                        # meshes
                        if name[3][0].rna_type.identifier == 'Mesh':

                            # link
                            name[3][2].data = source

                        # curves
                        if name[3][0].rna_type.identifier in {'SurfaceCurve', 'TextCurve', 'Curve'}:

                            # link
                            name[3][2].data = source

                        # lamps
                        if hasattr(name[3][0].rna_type.base, 'identifier'):
                            if name[3][0].rna_type.base.identifier == 'Lamp':

                                # link
                                name[3][2].data = source

                        # lattices
                        if name[3][0].rna_type.identifier == 'Lattice':

                            # link
                            name[3][2].data = source

                        # metaballs
                        if name[3][0].rna_type.identifier == 'MetaBall':

                            # link
                            name[3][2].data = source

                        # speakers
                        if name[3][0].rna_type.identifier == 'Speaker':

                            # link
                            name[3][2].data = source

                        # armatures
                        if name[3][0].rna_type.identifier == 'Armature':

                            # link
                            name[3][2].data = source

                        # materials
                        if name[3][0].rna_type.identifier == 'Material':

                            # link
                            name[3][2].material = source

                        # textures
                        if hasattr(name[3][0].rna_type.base, 'identifier'):
                            if name[3][0].rna_type.base.identifier == 'Texture':

                                # link
                                name[3][2].texture = source

                        # particle settings
                        if name[3][0].rna_type.identifier == 'ParticleSettings':

                            # link
                            name[3][2].settings = source

                            # line style
                        if name[3][0].rna_type.identifier == 'FreestyleLineStyle':

                            # link
                            name[3][2].linestyle = source
