import csv

def csvToDic(file):
    ''' Opens file and converts file content to a dictionary. '''
    reader = csv.reader(open(file, newline=''),delimiter=';', quotechar='|')

    result = {}
    for row in reader:
        key = row[0]
        result[key] = row[1:]
        print (key + str(result[key]))

    return result



def dicToCsv(file, my_dict):
    '''Writes dictionary content into csv file and replaces old conent'''
    with open(file, 'w', newline='') as f:  # Just use 'w' mode in 3.x
        csv_writer = csv.writer(f, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

        for k, v in my_dict.items():
            csv_writer.writerow([k] + v)

        return True

def appendDicToCsv(file, my_dict):
    '''Adds dictionary content to the end of the file'''
    with open(file, 'a', newline='') as f:  # Just use 'w' mode in 3.x
        csv_writer = csv.writer(f, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

        for k, v in my_dict.items():
            csv_writer.writerow([k] + v)

        return True

def inCsv(file,target):
    '''Is the target input in the file'''
    data = csvToDic(file)
    if target in data:
        return target, data[target]
    return False