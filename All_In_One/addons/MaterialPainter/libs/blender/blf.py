'''Font Drawing (blf)
   This module provides access to blenders text drawing functions.
   
'''


CLIPPING = 2 #constant value 

KERNING_DEFAULT = 8 #constant value 

ROTATION = 1 #constant value 

SHADOW = 4 #constant value 

WORD_WRAP = 128 #constant value 

def aspect(fontid, aspect):
   '''Set the aspect for drawing text.
      
      Arguments:
      @fontid (int): The id of the typeface as returned by :func:blf.load, for default font use 0.
      @aspect (float): The aspect ratio for text drawing to use.

   '''

   pass

def blur(fontid, radius):
   '''Set the blur radius for drawing text.
      
      Arguments:
      @fontid (int): The id of the typeface as returned by :func:blf.load, for default font use 0.
      @radius (int): The radius for blurring text (in pixels).

   '''

   pass

def clipping(fontid, xmin, ymin, xmax, ymax):
   '''Set the clipping, enable/disable using CLIPPING.
      
      Arguments:
      @fontid (int): The id of the typeface as returned by :func:blf.load, for default font use 0.
      @xmin (float): Clip the drawing area by these bounds.
      @ymin (float): Clip the drawing area by these bounds.
      @xmax (float): Clip the drawing area by these bounds.
      @ymax (float): Clip the drawing area by these bounds.

   '''

   pass

def dimensions(fontid, text):
   '''Return the width and height of the text.
      
      Arguments:
      @fontid (int): The id of the typeface as returned by :func:blf.load, for default font use 0.
      @text (string): the text to draw.

      @returns ((float, float)): the width and height of the text.
   '''

   return (float, float)

def disable(fontid, option):
   '''Disable option.
      
      Arguments:
      @fontid (int): The id of the typeface as returned by :func:blf.load, for default font use 0.
      @option (int): One of ROTATION, CLIPPING, SHADOW or KERNING_DEFAULT.

   '''

   pass

def draw(fontid, text):
   '''Draw text in the current context.
      
      Arguments:
      @fontid (int): The id of the typeface as returned by :func:blf.load, for default font use 0.
      @text (string): the text to draw.

   '''

   pass

def enable(fontid, option):
   '''Enable option.
      
      Arguments:
      @fontid (int): The id of the typeface as returned by :func:blf.load, for default font use 0.
      @option (int): One of ROTATION, CLIPPING, SHADOW or KERNING_DEFAULT.

   '''

   pass

def load(filename):
   '''Load a new font.
      
      Arguments:
      @filename (string): the filename of the font.

      @returns (int): the new font's fontid or -1 if there was an error.
   '''

   return int

def position(fontid, x, y, z):
   '''Set the position for drawing text.
      
      Arguments:
      @fontid (int): The id of the typeface as returned by :func:blf.load, for default font use 0.
      @x (float): X axis position to draw the text.
      @y (float): Y axis position to draw the text.
      @z (float): Z axis position to draw the text.

   '''

   pass

def rotation(fontid, angle):
   '''Set the text rotation angle, enable/disable using ROTATION.
      
      Arguments:
      @fontid (int): The id of the typeface as returned by :func:blf.load, for default font use 0.
      @angle (float): The angle for text drawing to use.

   '''

   pass

def shadow(fontid, level, r, g, b, a):
   '''Shadow options, enable/disable using SHADOW .
      
      Arguments:
      @fontid (int): The id of the typeface as returned by :func:blf.load, for default font use 0.
      @level (int): The blur level, can be 3, 5 or 0.
      @r (float): Shadow color (red channel 0.0 - 1.0).
      @g (float): Shadow color (green channel 0.0 - 1.0).
      @b (float): Shadow color (blue channel 0.0 - 1.0).
      @a (float): Shadow color (alpha channel 0.0 - 1.0).

   '''

   pass

def shadow_offset(fontid, x, y):
   '''Set the offset for shadow text.
      
      Arguments:
      @fontid (int): The id of the typeface as returned by :func:blf.load, for default font use 0.
      @x (float): Vertical shadow offset value in pixels.
      @y (float): Horizontal shadow offset value in pixels.

   '''

   pass

def size(fontid, size, dpi):
   '''Set the size and dpi for drawing text.
      
      Arguments:
      @fontid (int): The id of the typeface as returned by :func:blf.load, for default font use 0.
      @size (int): Point size of the font.
      @dpi (int): dots per inch value to use for drawing.

   '''

   pass

def unload(filename):
   '''Unload an existing font.
      
      Arguments:
      @filename (string): the filename of the font.

   '''

   pass

def word_wrap(fontid, wrap_width):
   '''Set the wrap width, enable/disable using WORD_WRAP.
      
      Arguments:
      @fontid (int): The id of the typeface as returned by :func:blf.load, for default font use 0.
      @wrap_width (int): The width (in pixels) to wrap words at.

   '''

   pass

