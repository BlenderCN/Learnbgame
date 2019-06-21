#!BPY
# -*- coding: UTF-8 -*-
#
#
# 2018.05.20 Natukikazemizo

#﻿import bpy

import re

# emotions
emotions =  (
    ("expectation", "Expectation", ""),      # (識別子, UI表示名, 説明文)
    ("joy", "Joy", ""),
    ("reception", "Reception", ""),
    ("fear", "Fear", ""),
    ("surprise", "Surprise", ""),
    ("sorrow", "Sorrow", ""),
    ("hatred", "Hatred", ""),
    ("anger", "Anger", ""))

# characters
characters =  (
    ("dorothy", "Dorothy", "Dorothy"),      # (識別子, UI表示名, 説明文)
    ("loris", "Loris", "Loris"),
    ("maid_fox", "Maid Fox", "Maid Fox"),
    ("robot", "Robot", "Robot like motion"),
    ("real", "Real", "Real motion"),
    ("cartoon", "Cartoon", "Cartoon like motion"))

# twist dictionary
char_action = {
    "dorothy"   :"Dorothy.twist",
    "loris"     :"Loris.twist",
    "maid_fox"  :"MaidFox.twist",
    "robot"     :"Robot.twist",
    "real"      :"Real.twist",
    "cartoon"   :"Cartoon.twist"
}

# directions
directions = (
    ("l2r", "Left to Right", "Left to Right"),
    ("r2l", "Right to Left", "Right to Left"),
)

# Bone Position Max
BONE_POS_MAX = 0.01


def get_otherside_name(key, side, text):
    print("text:" + text)
    direction_pos = re.search(key, text).span(0)[0]
    other_side_name = text[:direction_pos + 1] + side + \
        text[direction_pos + 2:]
    return other_side_name
