import random

def getRandomString(length):
    random.seed()
    return ''.join(random.choice("abcdefghijklmnopqrstuvwxyz1234567890")
                   for _ in range(length))

def catch_registration_error(func):
    """
    Catch registration error for @classmethod registered Blender property groups
    :param func: registration/unregister function
    :return: decorated_function
    :rtype: function
    """
    def decorated_function(cls):
        """Run the decorated function and catch any raised errors"""
        try:
            func(cls)
        except (RuntimeError, AttributeError, ValueError, TypeError) as e:
            pass
    return decorated_function

def print_dict(rand_dict, indent=0):
    """
    Prints a dictionary in a 'pretty' manner.

    :param rand_dict: A dictionary with items in it.
    :type: dict

    :param indent: How much to indent when printing the dictionary.
    :type: int
    """
    for key, value in rand_dict.items():
        print ('  ' * indent + str(key))
        if isinstance(value, dict):
            print_dict(value, indent+2)
        else:
            print ('  ' * (indent+2) + str(value))

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- CLASSES --#

class IO(object):
    """
    This class handles the outputting of printed information.
    """
    @classmethod
    def warning(cls, message):
        """
        Prints a message with the warning label attached.

        :param message: The message to output.
        :type: str
        """
        print ("\n  WARNING: %s\n" % message)

    @classmethod
    def info(cls, message):
        """
        Prints a message.

        :param message: The message to output.
        :type: str
        """
        print ("\n  %s\n" % message)

    @classmethod
    def debug(cls, message):
        """
        Prints a message with the debug label attached.

        :param message: The message to output.
        :type: str
        """
        print ("  DEBUG: %s" % message)

    @classmethod
    def error(cls, message):
        """
        Prints a message with the error label attached.

        :param message: The message to output.
        :type: str
        """
        print ("\n  ERROR: %s\n" % message)

    @classmethod
    def block(cls, message):
        """
        Prints one line of a block of text.

        :param message: The message to output.
        :type: str
        """
        print ("  %s" % message)

    @classmethod
    def list(cls, input_list):
        """
        Prints a list in a readable manner.

        :param input_list: The dictionary to print.
        :type: list
        """
        print ("\n  LIST CONTENTS:")
        for item in input_list:
            print ("    %s" % item)

    @classmethod
    def dict(cls, input_dict):
        """
        Prints a dictionary in a readable manner.

        :param input_dict: The dictionary to print.
        :type: dict
        """
        print ("\n  DICTIONARY CONTENTS:")
        print_dict(input_dict)

class Autovivification(dict):
    """Python implementation of Perl's Autovivification data structure"""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value
