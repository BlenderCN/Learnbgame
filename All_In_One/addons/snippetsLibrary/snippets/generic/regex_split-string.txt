'''
exemple input :
s ='WGT-CT01_01_R.001'

re.split('-|_| |\.', s) #separator separated by pipe '|'
>> ['WGT', 'CT01', '01', 'R', '001'] #doesn't include separators

re.split('(-|_| |\.)', s) #add cature group include separators
>> ['WGT', '-', 'CT01', '_', '01', '_', 'R', '.', '001']

re.split('\W', s) #split on words
>> ['WGT', 'CT01_01_R', '001']

re.split('(\W)', s) #split on words including delimiters
>> ['WGT', '-', 'CT01_01_R', '.', '001']

'''

#split on tirets, underscores, points, spaces
prefix = re.split('-|_|\.| ', ob.name)[0] #get_prefix[0]
print("prefix", prefix)#Dbg