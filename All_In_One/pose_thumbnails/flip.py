"""Pose flipping stuff."""

import typing

# We import 'bpy' to make 'import mathutils' work when running outside
# of Blender and using the built-as-Python-module version.
# noinspection PyUnresolvedReferences
import bpy
import mathutils


def name(to_flip: str, strip_number=False) -> str:
    """Flip left and right indicators in the name.

    Basically a Python implementation of BLI_string_flip_side_name.

    >>> name('bone_L.004')
    'bone_R.004'
    >>> name('bone_L.004', strip_number=True)
    'bone_R'
    >>> name('r_bone', strip_number=True)
    'l_bone'
    >>> name('left_bone')
    'right_bone'
    >>> name('Left_bone')
    'Right_bone'
    >>> name('LEFT_bone')
    'RIGHT_bone'
    >>> name('some.bone-RIGHT.004')
    'some.bone-LEFT.004'
    >>> name('some.bone-right.004')
    'some.bone-left.004'
    >>> name('some.bone-Right.004')
    'some.bone-Left.004'
    >>> name('some.bone-LEFT.004')
    'some.bone-RIGHT.004'
    >>> name('some.bone-left.004')
    'some.bone-right.004'
    >>> name('some.bone-Left.004')
    'some.bone-Right.004'
    """
    import string

    if len(to_flip) < 3:
        # we don't do names like .R or .L
        return to_flip

    # TODO: define once and reuse
    separators = set('. -_')
    replacements = {
        'l': 'r',
        'L': 'R',
        'r': 'l',
        'R': 'L',
    }

    prefix = suffix = number = ''
    is_set = False

    # We first check the case with a .### extension, let's find the last period
    replace = to_flip
    if to_flip[-1] in string.digits:
        try:
            index = to_flip.rindex('.')
        except ValueError:
            pass
        else:
            if to_flip[index + 1] in string.digits:
                # doesnt handle case bone.1abc2 correct..., whatever
                if not strip_number:
                    number = to_flip[index:]
                replace = to_flip[:index]

    # first case; separator . - _ with extensions r R l L
    if len(replace) > 1 and replace[-2] in separators:
        is_set = replace[-1] in replacements
        if is_set:
            replace = replace[:-1] + replacements[replace[-1]]

    # case; beginning with r R l L, with separator after it
    if not is_set and len(replace) > 1 and replace[1] in separators:
        is_set = replace[0] in replacements
        if is_set:
            replace = replacements[replace[0]] + replace[1:]

    if not is_set:
        lower = replace.lower()
        if lower.startswith('right'):
            bit = replace[0:2]
            if bit == 'Ri':
                prefix = 'Left'
            elif bit == 'RI':
                prefix = 'LEFT'
            else:
                prefix = 'left'
            replace = replace[5:]
        elif lower.startswith('left'):
            bit = replace[0:2]
            if bit == 'Le':
                prefix = 'Right'
            elif bit == 'LE':
                prefix = 'RIGHT'
            else:
                prefix = 'right'
            replace = replace[4:]
        elif lower.endswith('right'):
            bit = replace[-5:-3]
            if bit == 'Ri':
                suffix = 'Left'
            elif bit == 'RI':
                suffix = 'LEFT'
            else:
                suffix = 'left'
            replace = replace[:-5]
        elif lower.endswith('left'):
            bit = replace[-4:-2]
            if bit == 'Le':
                suffix = 'Right'
            elif bit == 'LE':
                suffix = 'RIGHT'
            else:
                suffix = 'right'
            replace = replace[:-4]

    return prefix + replace + suffix + number


def matrix(m44: mathutils.Matrix) -> mathutils.Matrix:
    """Flips the matrix around the X-axis.

    >>> _round(matrix(mathutils.Matrix.Identity(4)))
    Matrix(((1.0, 0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0, 0.0),
            (0.0, 0.0, 1.0, 0.0),
            (0.0, 0.0, 0.0, 1.0)))

    >>> import math
    >>> M = mathutils.Matrix

    >>> expect = M.Rotation(-math.pi/2, 4, 'Y')
    >>> _round(matrix(M.Rotation(math.pi/2, 4, 'Y')) - expect)
    Matrix(((0.0, 0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0, 0.0)))
    >>> expect = M.Rotation(-math.pi/3, 4, 'Z')
    >>> _round(matrix(M.Rotation(math.pi/3, 4, 'Z')) - expect)
    Matrix(((0.0, 0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0, 0.0)))
    >>> expect = M.Rotation(math.pi/2, 4, 'X')
    >>> _round(matrix(expect) - expect)
    Matrix(((0.0, 0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0, 0.0)))

    >>> expect = M.Rotation(-math.pi/2, 4, 'Y') * M.Translation((1, 2, 3))
    >>> _round(matrix(M.Rotation(math.pi/2, 4, 'Y') * M.Translation((-1, 2, 3))) - expect)
    Matrix(((0.0, 0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0, 0.0),
            (0.0, 0.0, 0.0, 0.0)))
    """

    flip_x = mathutils.Matrix((
        (-1, 0, 0, 0),
        (0, 1, 0, 0),
        (0, 0, 1, 0),
        (0, 0, 0, 1),
    ))
    return flip_x * m44 * flip_x


def _round(m44: mathutils.Matrix):
    """In-place round each element of the matrix to ndigits digits.

    Returns the same matrix for doctest purposes.
    """
    for vec in m44:
        for i in range(4):
            if abs(vec[i] - 0) < 0.00001:
                vec[i] = 0
            elif abs(vec[i] - 1) < 0.00001:
                vec[i] = 1
            elif abs(vec[i] + 1) < 0.00001:
                vec[i] = -1
    return m44


def pixels(values: typing.MutableSequence, width: int, height: int):
    """In-place flips the pixels of an image."""

    start = 0
    end = width
    for _ in range(height):
        values[start:end] = reversed(values[start:end])
        start = end
        end += width


if __name__ == '__main__':
    import doctest

    doctest.testmod()
