#!/usr/bin/env python3
# print the cell lineage, from start to finish, given an endpoint cell lineage (all the letters)
import sys

print(__name__, file=sys.stderr)
if __name__ == '__main__':
    target_cell = sys.argv[1]
    print(target_cell)
    for line in parse_gs_epic_file(target_cell, sys.argv[2]):
        print(line)


def get_parent(celltype):
    # top level 
    if celltype == 'P1' or celltype == 'AB':  return ''

    if celltype == 'E' or celltype == 'MS':   return 'EMS'

    if celltype == 'EMS' or celltype == 'P2': return 'P1'

    if celltype == 'C' or celltype == 'P3':  return 'P2'

    if celltype == 'D' or celltype == 'P4':  return 'P3'

    if celltype == 'Z3' or celltype == 'Z2': return 'P4'

    # celltypes whose parents 
    # ARE one letter shorter
    return celltype[:-1]

def get_cell_stage_datum(cel, bd):
    cell = cel
    while cell not in bd:
        #print('searching for cell %s' % cell)
        cell = get_parent(cell)
        if len(cell) == 0:
            raise Exception('cell type %s not found and has NO PARENT' % cel)

    return cell, bd[cell]

def get_big_data(infilename):
    infile = open(infilename)
    infile.readline() # skip header

    min_time = 1
    max_time = 1
    big_data = {} # by cell, then time
    for line in infile:
        # cellTime,cell,time,none,global,local,blot,cross,z,x,y, size,gweight
        # 0        1    2    3    4      5     6    7     8 9 10 11   12
        fields = line.strip().split(',')
        cell = fields[1]
        time = int(fields[2])
        if time > max_time: max_time = time
        value = int(fields[3])
        x = int(fields[9])
        y = int(fields[10])
        z = float(fields[8])
        size = int(fields[11])

        this_thing = {
            'x': x,
            'y': y,
            'z': z,
            'cell': cell,
            'time': time,
            'value': value,
            'size': size
        }
        if cell not in big_data:
            big_data[cell] = {}

        big_data[cell][time] = this_thing

    return big_data

def load_gs_epic_file(infilename):

    infile = open(infilename)
    infile.readline() # skip header

    min_time = 1
    max_time = 1
    big_data = {} # by time, then cell

    for line in infile:
        # cellTime,cell,time,none,global,local,blot,cross,z,x,y, size,gweight
        # 0        1    2    3    4      5     6    7     8 9 10 11   12
        fields = line.strip().split(',')
        cell = fields[1]
        time = int(fields[2])
        if time > max_time: max_time = time
        value = int(fields[3])
        x = int(fields[9])
        y = int(fields[10])
        z = float(fields[8])
        size = int(fields[11])

        this_thing = {
            'x': x,
            'y': y,
            'z': z,
            'cell': cell,
            'time': time,
            'value': value,
            'size': size
        }

        if len(fields) > 13:
            this_thing['ecdf'] = float(fields[13])


        if time not in big_data:
            big_data[time] = {}

        big_data[time][cell] = this_thing
    
    print("about to return", min_time, max_time, "big_data", file=sys.stderr)
    return min_time, max_time, big_data

def search_gs_epic_file(target_cells, min_time, max_time, big_data):


    for time_pnt in range(min_time, max_time+1):
        for target_cell in target_cells:
            try:
                found_cell, k = get_cell_stage_datum( target_cell, big_data[time_pnt] )
                yield time_pnt, k, found_cell
            except:
                yield time_pnt, None, ''
    

def parse_gs_epic_file(target_cells, infilename):
    min_time, max_time, big_data = load_gs_epic_file(infilename)
    for time_pnt, k, found_cell in search_gs_epic_file(target_cells, min_time, max_time, big_data):
        yield time_pnt, k, found_cell

    

ALL_END_PNTS = [
 'ABalaaaala', 'ABalaaaalp', 'ABalaaaarl', 'ABalaaaarr', 'ABalaaapal', 'ABalaaapar', 'ABalaaappl', 'ABalaaappr', 'ABalaapaaa', 'ABalaapaap', 'ABalaapapa',
 'ABalaapapp', 'ABalaappaa', 'ABalaappap', 'ABalaapppa', 'ABalaapppp', 'ABalapaaaa', 'ABalapaaap', 'ABalapaapa', 'ABalapaapp', 'ABalapapaa', 'ABalapapap',
 'ABalapappa', 'ABalapappp', 'ABalappaaa', 'ABalappaap', 'ABalappapa', 'ABalappapp', 'ABalapppaa', 'ABalapppap', 'ABalappppa', 'ABalappppp', 'ABalpaaaaa',
 'ABalpaaaap', 'ABalpaaapa', 'ABalpaaapp', 'ABalpaapaa', 'ABalpaapap', 'ABalpaappa', 'ABalpaappp', 'ABalpapaaa', 'ABalpapaap', 'ABalpapapa', 'ABalpapapp',
 'ABalpappaa', 'ABalpappap', 'ABalpapppa', 'ABalpapppp', 'ABalppaaaa', 'ABalppaaap', 'ABalppaapa', 'ABalppaapp', 'ABalppapaa', 'ABalppapap', 'ABalppappa',
 'ABalppappp', 'ABalpppaaa', 'ABalpppaap', 'ABalpppapa', 'ABalpppapp', 'ABalppppaa', 'ABalppppap', 'ABalpppppa', 'ABalpppppp', 'ABaraaaaaa', 'ABaraaaaap',
 'ABaraaaapa', 'ABaraaaapp', 'ABaraaapaa', 'ABaraaapap', 'ABaraaappa', 'ABaraaappp', 'ABaraapaaa', 'ABaraapaap', 'ABaraapapa', 'ABaraapapp', 'ABaraappaa',
 'ABaraappap', 'ABaraapppa', 'ABaraapppp', 'ABarapaaaa', 'ABarapaaap', 'ABarapaapa', 'ABarapaapp', 'ABarapapaa', 'ABarapapap', 'ABarapappa', 'ABarapappp',
 'ABarappaaa', 'ABarappaap', 'ABarappapa', 'ABarappapp', 'ABarapppaa', 'ABarapppap', 'ABarappppa', 'ABarappppp', 'ABarpaaaaa', 'ABarpaaaap', 'ABarpaaapa',
 'ABarpaaapp', 'ABarpaapaa', 'ABarpaapap', 'ABarpaappa', 'ABarpaappp', 'ABarpapaaa', 'ABarpapaap', 'ABarpapapa', 'ABarpapapp', 'ABarpappaa', 'ABarpappap',
 'ABarpapppa', 'ABarpapppp', 'ABarppaaaa', 'ABarppaaap', 'ABarppaapa', 'ABarppaapp', 'ABarppapaa', 'ABarppapap', 'ABarppappa', 'ABarppappp', 'ABarpppaaa',
 'ABarpppaap', 'ABarpppapa', 'ABarpppapp', 'ABarppppaa', 'ABarppppap', 'ABarpppppa', 'ABarpppppp', 'ABplaaaaaa', 'ABplaaaaap', 'ABplaaaapa', 'ABplaaaapp',
 'ABplaaapaa', 'ABplaaapap', 'ABplaaappa', 'ABplaaappp', 'ABplaapaaa', 'ABplaapaap', 'ABplaapapa', 'ABplaapapp', 'ABplaappaa', 'ABplaappap', 'ABplaapppa',
 'ABplaapppp', 'ABplapaaaa', 'ABplapaaap', 'ABplapaapa', 'ABplapaapp', 'ABplapapaa', 'ABplapapap', 'ABplapappa', 'ABplapappp', 'ABplappaaa', 'ABplappaap',
 'ABplappapa', 'ABplappapp', 'ABplapppaa', 'ABplapppap', 'ABplappppa', 'ABplappppp', 'ABplpaaaaa', 'ABplpaaaap', 'ABplpaaapa', 'ABplpaaapp', 'ABplpaapaa',
 'ABplpaapap', 'ABplpaappa', 'ABplpaappp', 'ABplpapaaa', 'ABplpapaap', 'ABplpapapa', 'ABplpapapp', 'ABplpappaa', 'ABplpappap', 'ABplpapppa', 'ABplpapppp',
 'ABplppaaaa', 'ABplppaaap', 'ABplppaapa', 'ABplppaapp', 'ABplppapaa', 'ABplppapap', 'ABplppappa', 'ABplppappp', 'ABplpppaaa', 'ABplpppaap', 'ABplpppapa',
 'ABplpppapp', 'ABplppppaa', 'ABplppppap', 'ABplpppppa', 'ABplpppppp', 'ABpraaaaaa', 'ABpraaaaap', 'ABpraaaapa', 'ABpraaaapp', 'ABpraaapaa', 'ABpraaapap',
 'ABpraaappa', 'ABpraaappp', 'ABpraapaaa', 'ABpraapaap', 'ABpraapapa', 'ABpraapapp', 'ABpraappaa', 'ABpraappap', 'ABpraapppa', 'ABpraapppp', 'ABprapaaaa',
 'ABprapaaap', 'ABprapaapa', 'ABprapaapp', 'ABprapapaa', 'ABprapapap', 'ABprapappa', 'ABprapappp', 'ABprappaaa', 'ABprappaap', 'ABprappapa', 'ABprappapp',
 'ABprapppaa', 'ABprapppap', 'ABprappppa', 'ABprappppp', 'ABprpaaaaa', 'ABprpaaaap', 'ABprpaaapa', 'ABprpaaapp', 'ABprpaapaa', 'ABprpaapap', 'ABprpaappa',
 'ABprpaappp', 'ABprpapaaa', 'ABprpapaap', 'ABprpapapa', 'ABprpapapp', 'ABprpappaa', 'ABprpappap', 'ABprpapppa', 'ABprpapppp', 'ABprppaaaa', 'ABprppaaap',
 'ABprppaapa', 'ABprppaapp', 'ABprppapaa', 'ABprppapap', 'ABprppappa', 'ABprppappp', 'ABprpppaaa', 'ABprpppaap', 'ABprpppapa', 'ABprpppapp', 'ABprppppaa',
 'ABprppppap', 'ABprpppppa', 'ABprpppppp', 'MSaaaaaa', 'MSaaaaap', 'MSaaaapa', 'MSaaaapp', 'MSaaapaa', 'MSaaapap', 'MSaaapp', 'MSaapaaa',
 'MSaapaap', 'MSaapapa', 'MSaapapp', 'MSaappa', 'MSaappp', 'MSapaaaa', 'MSapaaap', 'MSapaap', 'MSapapaa', 'MSapapap', 'MSapapp',
 'MSappaa', 'MSappap', 'MSapppa', 'MSapppp', 'MSpaaaaa', 'MSpaaaap', 'MSpaaapa', 'MSpaaapp', 'MSpaapaa', 'MSpaapap', 'MSpaapp',
 'MSpapaaa', 'MSpapaap', 'MSpapapa', 'MSpapapp', 'MSpappa', 'MSpappp', 'MSppaaaa', 'MSppaaap', 'MSppaap', 'MSppapaa', 'MSppapap',
 'MSppapp', 'MSpppaa', 'MSpppap', 'MSppppa', 'MSppppp', 'Ealaa', 'Ealap', 'Ealpa', 'Ealpp', 'Earaa', 'Earap',
 'Earpa', 'Earpp', 'Eplaa', 'Eplap', 'Eplpa', 'Eplpp', 'Epraa', 'Eprap', 'Eprpa', 'Eprpp', 'Caaaaa',
 'Caaaap', 'Caaapa', 'Caaapp', 'Caapa', 'Caappd', 'Caappv', 'Capaa', 'Capap', 'Cappaa', 'Cappap', 'Capppa',
 'Capppp', 'Cpaaaa', 'Cpaaap', 'Cpaapa', 'Cpaapp', 'Cpapaa', 'Cpapap', 'Cpappd', 'Cpappv', 'Cppaaa', 'Cppaap',
 'Cppapa', 'Cppapp', 'Cpppaa', 'Cpppap', 'Cppppa', 'Cppppp', 'Daaa', 'Daap', 'Dapa', 'Dapp', 'Dpaa',
 'Dpap', 'Dppa', 'Dppp', 'Z2', 'Z3']

