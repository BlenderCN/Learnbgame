import math
from collections import namedtuple

__all__ = ['pack']


class Rect(object):
    __slots__ = (
        'top_left',
        '_size'
    )

    def __init__(self, top_left=(0, 0), size=(0, 0)):
        self.top_left = top_left
        self._size = size

    x = property(lambda self: self.top_left[0])
    y = property(lambda self: self.top_left[1])
    size = property(lambda self: self._size)
    width = property(lambda self: self._size[0])
    height = property(lambda self: self._size[1])
    top = property(lambda self: self.y)
    left = property(lambda self: self.x)
    right = property(lambda self: self.left + self.width)
    bottom = property(lambda self: self.top + self.height)
    area = property(lambda self: self.width * self.height)

    def contains(self, other):
        return other.width <= self.width and other.height <= self.height

    def __repr__(self):
        return '{}({}, {}, {}, {})'.format(self.__class__.__name__, self.left, self.top, self.width, self.height)


class Node(Rect):
    __slots__ = (
        'top_left',
        'size',
        'bucket',
        'left_child',
        'right_child',
        'full'
    )

    def __init__(self, top_left=(0, 0), size=(0,0)):
        super().__init__(top_left, size)
        self.bucket = None
        self.left_child = None
        self.right_child = None
        self.full = min(size) == 0

    def contains(self, other):
        if self.full:
            return False

        if self.left_child:
            self.full = self.left_child.full and self.right_child.full
            if self.full:
                return False

        return super().contains(other)

    def insert(self, node):
        if self.full:
            return None

        # Recursive case
        if self.bucket:
            result = self.left_child.insert(node) or self.right_child.insert(node)

            if not result:
                self.full = self.left_child.full and self.right_child.full

            return result

        # Is this node large enough to contain target node
        if not self.contains(node):
            return None

        self.bucket = node
        self.bucket.top_left = self.top_left

        # Partition space such that the right child's area is maximized
        child_0 = Node((self.left, node.bottom), (node.width, self.height - node.height))
        child_1 = Node((node.right, self.top), (self.width - node.width, self.height))
        child_2 = Node((node.right, self.top), (self.width - node.width, node.height))
        child_3 = Node((self.left, node.bottom), (self.width, self.height - node.height))

        if max(child_0.area, child_1.area) > max(child_2.area, child_3.area):
            self.left_child = child_0
            self.right_child = child_1

        else:
            self.left_child = child_2
            self.right_child = child_3

        return self.bucket.top_left


class KdRegionTreeError(Exception):
    pass


class KdRegionTree(object):
    """Class for densely packing areas

    Example:
        atlas = KdRegionTree((100, 100))
        atlas.insert(Rect(size=10, 10))
    """

    def __init__(self, size):
        self._root = Node(size=size)

    def insert(self, element):
        """Inserts the given element into the tree

        Args:
            element: An object that represents an area. Must have 'size'
            attribute.

        Returns:
             A two-tuple representing the top-left coordinate of the inserted
             element.
        """

        if not hasattr(element, 'size'):
            raise KdRegionTreeError("Inserted element must have 'size' attribute.")

        if min(element.size) <= 0:
            raise KdRegionTreeError('Inserted element must have non-zero area')

        rect = Rect(size=element.size)

        return self._root.insert(rect)


PackResult = namedtuple('PackResult', ['atlas_size', 'offsets'])


def pack(regions, size=None):
    if not size:
        area = sum([r.size[0] * r.size[1] for r in regions])
        side = 1 << (int(math.sqrt(area)) - 1).bit_length()
        size = side, side

    # Sort using area weighted by shortest edge.
    es = enumerate(regions)
    sorted_es = sorted(es, key=lambda i: min(i[1].size) * i[1].size[0] * i[1].size[1], reverse=True)

    # Insert into tree
    tree = KdRegionTree(size)
    offsets = []
    count = 0
    for index, image in sorted_es:
        count += 1
        offset = tree.insert(image)
        offsets.append((index, offset))

    # Reorder offsets back to given image order
    unsorted_offsets = sorted(offsets, key=lambda i: i[0])
    offsets = [o[1] for o in unsorted_offsets]

    return PackResult(size, offsets)


if __name__ == '__main__':
    """
    import timeit
    data = [Rect(size=(8,8)) for _ in range(20000)]

    def my_function():
        pack(data)

    print(timeit.timeit(my_function, number=1))
    quit()
    """

    from PIL import Image
    import glob
    import os

    glob_pattern = r'C:\Users\Joshua\Games\QUAKE\Id1\wads\id\*.png'
    images_paths = [g for g in glob.glob(glob_pattern)]
    images = [Image.open(file) for file in images_paths if os.path.getsize(file)]

    size, offsets = pack(images)

    total_images = len(images)
    packed_images = len([o for o in offsets if o])
    print('Successfully packed {} of {} images.'.format(packed_images, total_images))

    # Create atlas image
    sheet = Image.new('RGBA', size)
    fill_color = 0, 255, 255
    sheet.paste(fill_color, [0, 0, *size])

    # Composite image
    for image_index, image in enumerate(images):
        if not offsets[image_index]:
            continue

        offset = offsets[image_index]
        sheet.paste(image, offset)

    sheet.show()
