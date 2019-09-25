# coding=utf-8

""" Copyright 2014 - 2018, Wybren van Keulen, The Grove """


class TwigInstance(object):
    
    __slots__ = ["matrix", "twig_type", "parent_branch", "position", "direction"]

    def __init__(self, matrix, twig_type, position, direction):
        self.matrix = matrix
        self.twig_type = twig_type  # 0 == Lateral, 1 == Apical
        self.position = position
        self.direction = direction
