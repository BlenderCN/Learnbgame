#add prop
#wman=bpy.data.window_managers['WinMan']
#pal=wman.palette
#pal.add()

#call nodetree

#import bpy
#import math

#print('start')
#palette=bpy.data.window_managers['WinMan'].palette[0].palettes[0]
#size=128
## blank image
#image = bpy.data.images.new(palette.name, width=size, height=size)

#squarenb=len(palette.colors)
#rownb=math.ceil(math.sqrt(squarenb))
#sqsize=int(size/rownb)

#pixels = [None] * size * size
#ct=0
#for c in palette.colors:
#    ct+=1
#    for x in range(((ct-1)*sqsize), (ct*sqsize)):
#        for y in range(((ct-1)*sqsize), (ct*sqsize)):
#            pixels[(y * (ct*sqsize)) + x] = [1, 1, 1, 1.0]

## flatten list
#pixels = [chan for px in pixels for chan in px]

## assign pixels
#image.pixels = pixels

