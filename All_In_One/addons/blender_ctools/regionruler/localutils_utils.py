# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


import collections
import collections.abc


def _list_or_tuple(x):
    return isinstance(x, (list, tuple))


def _is_iterable(x):
    """list_or_tuple()の代わり"""
    return (isinstance(x, collections.abc.Sequence) and
            not isinstance(x, (str, bytes, bytearray, memoryview)))


def flatten(sequence, to_expand=_is_iterable, dimension=0):
    """
    入れ子の要素を順に返すジェネレータ
    Python Cookbook 第二版 第四章第六節 入れ子になったシーケンスの平滑化
    :param sequence: 平坦化するシーケンス
    :type sequence: collections.abc.Iterable
    :param to_expand: 平坦化するオブジェクトか判定する
    :type to_expand: types.FunctionType -> bool
    :param dimension: sequenceの次元を指定して平坦化を制限する。
        [0, [1, [2, 3], 4], 5] ->
             0: (0, 1, 2, 3, 4, 5)  # 全て展開
             1: (0, [1, [2, 3], 4], 5)  # そのまま
             2: (0, 1, [2, 3], 4, 5)  # 二次元と見做し、一回だけ展開
    :type dimension: int
    :rtype: types.GeneratorType
    """
    for item in sequence:
        if dimension != 1 and to_expand(item):
            for sub_item in flatten(item, to_expand, dimension - 1):
                yield sub_item
        else:
            yield item


def find_brackets(text, brackets=(('(', ')'), ('[', ']'), ('{', '}')),
                  quotations=("'''", '"""', "'", '"'),
                  old_style=False):
    """文字列中のブラケット及びクォーテーションのペアを探す。
    対応するブラケットが見つけられないならインデックスはNoneになる。

    >> text = "print({'A': '''B\"C\"'''}['A'])"
    >> r = find_brackets(text)
    >> r
    ((5, '(', 28, ')'),
     (6, '{', 22, '}'),
     (7, "'", 9, "'"),
     (12, "'''", 19, "'''"),
     (23, '[', 27, ']'),
     (24, "'", 26, "'"))
    >> for i, t, j, u in r:
    >>     print(text[slice(i, j + len(u))])
    ({'A': '''B"C"'''}['A'])
    {'A': '''B"C"'''}
    'A'
    '''B"C"'''
    ['A']
    'A'

    >> find_brackets("eval(\'print(\\\'test\\\')\')")
    ((4, '(', 22, ')'), (5, "'", 21, "'"))

    >> find_brackets("({)'")
    ((0, '(', None, ')'),
     (1, '{', None, '}'),
     (None, '(', 2, ')'),
     (3, "'", None, "'"))

    >> find_brackets("<class> $$ABC¥¥", brackets=[['$$', '¥¥'], ['<', '>']])
    ((0, '<', 6, '>'), (8, '$$', 13, '¥¥'))

    :type text: str
    :param brackets: 対象を指定。先頭から順に処理するので順序には注意
    :type brackets: list | tuple
    :param quotations: 対象を指定。先頭から順に処理するので順序には注意
        例 ["'", "'''"] と ["'''", "'"] では結果が異なる
    :type quotations: list | tuple
    :param old_style: 互換性維持の為。
    :type old_style: bool
    :return: old_styleが偽の場合:
                 ((先頭インデックス, 先頭token,
                   末尾インデックス(末尾tokenの開始位置), 末尾token), ...)
             old_styleが真の場合:
                 ((先頭インデックス,
                   末尾インデックス(末尾tokenの開始位置 + len(末尾token)), ...)
    :rtype: tuple
    """

    match_tokens = {}  # {start index: [start token, end index, end token],...}
    tmp = []  # [[start index], ...]

    invalid = False
    i = 0
    length = len(text)
    while i < length:
        if tmp:
            j = tmp[-1]
            last_token = match_tokens[j][0]
        else:
            j = 0
            last_token = ''

        # ' " ''' """
        match = False
        for quot in quotations:
            if text[i: i + len(quot)] != quot:
                continue
            if i > 0 and text[i - 1] == '\\':
                continue
            if tmp and last_token in quotations and last_token != quot:
                # 文字列中では別の文字列を開始しない
                continue
            # close
            if tmp and last_token == quot:
                match_tokens[j][1] = i
                tmp.pop()
            # start
            else:
                match_tokens[i] = [quot, None, quot]
                tmp.append(i)
            match = True
            i += len(quot)
            break
        if match:
            continue

        if last_token in quotations:
            i += 1
            continue

        # ( ) [ ] { }
        match = False
        for token_start, token_end in brackets:
            # close
            if text[i: i + len(token_end)] == token_end:
                if invalid:
                    match_tokens[i] = [token_start, i, token_end]
                elif tmp and last_token == token_start:
                    match_tokens[j][1] = i
                    tmp.pop()
                else:
                    invalid = True
                    match_tokens[i] = [token_start, i, token_end]
                i += len(token_end)
                match = True
                break
            # start
            elif text[i: i + len(token_start)] == token_start:
                match_tokens[i] = [token_start, None, token_end]
                tmp.append(i)
                i += len(token_start)
                match = True
                break
        if not match:
            i += 1


    if old_style:
        retval = []
        for i, (t, j, u) in sorted(match_tokens.items()):
            if i == j:
                i = None
            if j:
                j += len(u)
            retval.append((i, j))
        retval = tuple(retval)
    else:
        retval = tuple(((i, t, j, u) if i != j else (None, t, j, u)
                       for i, (t, j, u) in sorted(match_tokens.items())))
    return retval
