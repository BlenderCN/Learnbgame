class box():
    def __init__(self, index, area, x, y, w, h, left, right, layout):
        #if they share a horizontal edge 
        self.area = area
        self.index = index
        self.x = x
        self.y = y
        self.h = h
        self.w = w
        self.left = left
        self.right = right
        self.layout = layout
    def __repr__(self):
        return "box %d %d %d %d" % (self.x, self.y, self.w, self.h)


class ScreenLayoutPanel():
    bl_label = "Screen Layout"

    sd_operator = "sounddrivers.view_action" # an op that takes area_index
    sd_operator_text = "BGL" # an op that takes area_index

    def build_tree(self, context):
        window = context.window
        screen = window.screen
        areas = []

        for index, area in enumerate(screen.areas):
            areas.append(box(index,
                             area, 
                             area.x, 
                             window.height-(area.y + area.height), 
                             area.width,
                             area.height, None, None, 'BOX'))

        #areas = sorted(areas, key = lambda k:(k.y, k.x))

        #make a tree

        #searh for areas that share an edge
        while len(areas) > 1:
            #areas = sorted(areas, key = lambda k:(k.y , k.x))
            for area in areas:
                # share a vert edge
                se = [a for a in areas if a != area and a.y == area.y and a.h == area.h]
                if len(se):
                    a = se[0]
                    if a.x <= area.x:
                        left, right = a, area
                    else:
                        left, right = area, a
                    n = box(area.index, None, left.x, left.y,left.w + right.w + 1, left.h, left, right, 'COL')
                    areas.pop(areas.index(area))
                    areas.pop(areas.index(a))
                    areas.append(n)
            areas = sorted(areas, key = lambda k:(k.x , k.y))
            for area in areas:
                # share a horiz edge
                sh = [a for a in areas if a != area and a.x == area.x and a.w == area.w]
                if len(sh):
                    a = sh[0]
                    # left is top, right bottom
                    if a.y < area.y:
                        left, right = a, area
                    else:
                        left, right = area, a
                    n = box(0, None, left.x, left.y, area.w, area.h + a.h + 1, left, right, 'ROW')
                    areas.pop(areas.index(area))
                    areas.pop(areas.index(a))
                    areas.append(n)
        return areas[0]

    #traverse the tree
    def traverse_binary_tree(self, context, node, layout, scale_factor=0.8):
        window = context.window

        if node.layout == "ROW":
            col = box = layout.column()
            left = col.row()

            right = col.row()


        elif node.layout == "COL":
            m = max([node.left.w, node.right.w])
   
            right = layout.row()
                
            left = right.column()

        else:
            box = layout.box()
            box.scale_x = scale_factor * node.w / window.width
            box.scale_y = max([0.5, 7 * scale_factor * node.h / window.height])
            box.enabled = not (context.area == node.area)
            box.context_pointer_set("area", node.area)
            box.context_pointer_set("region", node.area.regions[-1])
            box.context_pointer_set("space_data", node.area.spaces.active)
            self.draw_area_operator(context, box, node.index)


            #op = box.operator("graph.clean", text=self.sd_operator_text)
            #op = box.operator(self.sd_operator, text=self.sd_operator_text)
            #op.area_index = node.index

        if node.left:
            self.traverse_binary_tree(context, node.left, left)

        if node.right:
            self.traverse_binary_tree(context, node.right, right)

    def draw_area_buttons(self, context):
        layout = self.layout       
        root = self.build_tree(context)
        layout.label(context.screen.name)
        self.traverse_binary_tree(context, root, layout)
