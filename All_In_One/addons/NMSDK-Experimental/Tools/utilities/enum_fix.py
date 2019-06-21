# simple script to convert enum values to a list as is required for the
# EnumProperty in blender

# copy and paste the string here:
# this should look like (for example):
""" '"Default", "Terrain", "Substance", "Rock", "Asteroid", "Shield", "Creature", "Robot", "Freighter", "Cargo", "Ship", "Plant"' """
# ie. enter list as comma separated values

data = '"Traders", "Warriors", "Explorers", "Robots", "Atlas", "Diplomats", "None"'

for val in data.split(','):
    print('({0}, {0}, {0}),'.format(val.lstrip(' ')))
