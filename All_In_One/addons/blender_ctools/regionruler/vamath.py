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


from mathutils import geometry as geom


def cross2d(v1, v2):
    return v1[0] * v2[1] - v1[1] * v2[0]


def dot2d(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1]


def intersect_line_quad_2d(line_p1, line_p2,
                           quad_p1, quad_p2, quad_p3, quad_p4, clip=False):
    """二次元の直線（線分）を凸包の四角形で切り取る。quad_p1~4は反時計回り
    :rtype: None | (Vector, Vector)
    """
    eps = 1e-8
    p1, p2 = line_p1.copy(), line_p2.copy()
    quad = [quad_p1, quad_p2, quad_p3, quad_p4]

    # lineが点の場合
    if p1 == p2:
        if geom.intersect_point_quad_2d(p1, *quad) == 1:
            return p1, p2
        else:
            return None
    # quadが点の場合
    if quad_p1 == quad_p2 == quad_p3 == quad_p4:
        line = p2 - p1
        f = cross2d(line, quad_p1 - p1)
        if f < eps:
            # p = (quad_p1 - p1).project(line) + p1
            d = dot2d(line, quad_p1 - p1)
            l = line.length
            f = d / l ** 2
            if clip and (f < 0 or f > 1):
                return None
            p = f * line + p1
            return p, p.copy()
        else:
            return None
    # lineがquadの内側に有る場合
    if clip:
        if geom.intersect_point_quad_2d(p1, *quad) == 1:
            if geom.intersect_point_quad_2d(p2, *quad) == 1:
                return p1, p2

    # quadの各辺との判定
    intersected = False
    for i in range(4):
        q1 = quad[i - 1]
        q2 = quad[i]
        if q1 == q2:
            # TODO: 何かしらの処理が要る？
            continue

        line = p2 - p1
        edge = q2 - q1

        # 平行
        if abs(cross2d(line, edge)) < eps:
            continue

        f1 = cross2d(edge, p1 - q1)
        f2 = cross2d(edge, p2 - q1)
        f3 = cross2d(line, q1 - p1)
        f4 = cross2d(line, q2 - p1)

        # 交点計算
        # if clip:
        #     # 線分が外側
        #     if f1 < 0 and f2 < 0:
        #         return None
        #     # NOTE:
        #     #     intersect_line_line_2d()は線分同士の判定を行う。
        #     #     平行でも線分同士が片方の頂点だけで重なるならその座標が返る
        #     #     (0, 0), (1, 0), (1, 0), (2, 0) -> (1, 0)
        #     p = geom.intersect_line_line_2d(p1, p2, q1, q2)
        # else:
        #     if f3 * f4 <= 0:  # edge上で交差
        #         d1 = cross2d(edge, q1 - p1)  # 省略 '/ edge.length'
        #         d2 = cross2d(edge, line)  # 省略 '/ edge.length'
        #         p = p1 + (d1 / d2) * line
        #     else:
        #         p = None
        if clip and f1 < 0 and f2 < 0:  # 線分が外側
            return None
        if (f1 * f2 <= 0 or not clip) and f3 * f4 <= 0:
            d1 = cross2d(edge, q1 - p1)  # 省略 '/ edge.length'
            d2 = cross2d(edge, line)  # 省略 '/ edge.length'
            p = p1 + (d1 / d2) * line
        else:
            p = None

        if p:
            if clip:
                if f1 < 0:  # p1が外側
                    p1 = p
                if f2 < 0:  # p2が外側
                    p2 = p.copy()
            else:
                if f1 < f2:
                    p1 = p
                else:
                    p2 = p
            if p1 == p2:
                return p1, p2
            intersected = True

    if intersected:
        return p1, p2
    else:
        return None
