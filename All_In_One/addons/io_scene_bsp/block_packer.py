import math

from collections import namedtuple

PackResult = namedtuple('PackResult', ['atlas_size', 'offsets'])


class Block:
    def __init__(self, size):
        self.size = size
        self._heights = [0 for _ in range(size[0])]

    def insert(self, element):
        block_width, block_height = self.size
        element_width, element_height = element.size

        best_height = block_height

        for i in range(0, (block_width - element_width) + 1):
            current_height = 0

            for j in range(0, element_width):
                if self._heights[i+j] >= best_height:
                    break

                if self._heights[i+j] > current_height:
                    current_height = self._heights[i+j]

            # Valid spot
            if j == element_width - 1:
                x = i
                y = best_height = current_height

        if best_height + element_height > block_height:
            return None

        for i in range(x, x + element_width):
            self._heights[i] = element_height + best_height

        #self._heights[x:element_width] = (element_height + best_height,) * element_width

        return x, y


def pack(regions, size=None):
    if not size:
        area = sum([r.size[0] * r.size[1] for r in regions])
        side = 1 << (int(math.sqrt(area)) - 1).bit_length()
        size = side, side

    # Sort using area weighted by shortest edge.
    es = enumerate(regions)
    sorted_es = sorted(es, key=lambda i: min(i[1].size) * i[1].size[0] * i[1].size[1], reverse=True)

    # Insert into tree
    tree = Block(size)
    offsets = []
    count = 0
    for index, image in enumerate(regions):#sorted_es:
        count += 1
        offset = tree.insert(image)
        offsets.append((index, offset))

    # Reorder offsets back to given image order
    unsorted_offsets = sorted(offsets, key=lambda i: i[0])
    offsets = [o[1] for o in unsorted_offsets]

    return PackResult(size, offsets)

if __name__ == '__main__':
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