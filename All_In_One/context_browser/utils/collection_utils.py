import bpy
from ..addon import ic


def sort_collection(collection, key, idx_data=None, idx_prop=None):
    if idx_data is not None and idx_prop is not None:
        cur_name = collection[getattr(idx_data, idx_prop)].name

    items = [item for item in collection]
    items.sort(key=key)
    items = [item.name for item in items]

    idx = len(items) - 1
    while idx > 0:
        name = items[idx]
        if collection[idx] != collection[name]:
            idx1 = collection.find(name)
            collection.move(idx1, idx)
        idx -= 1

    if idx_data is not None and idx_prop is not None:
        setattr(idx_data, idx_prop, collection.find(cur_name))


def move_item(collection, old_idx, new_idx):
    collection.move(old_idx, new_idx)


def remove_item(collection, idx, idx_data=None, idx_prop=None):
    collection.remove(idx)

    if idx_data is not None and idx_prop is not None:
        idx = getattr(idx_data, idx_prop)
        if idx >= len(collection) and idx > 0:
            setattr(idx_data, idx_prop, len(collection) - 1)
        else:
            setattr(idx_data, idx_prop, -1)
            setattr(idx_data, idx_prop, idx)


def remove_item_by(collection, key, value, idx_data=None, idx_prop=None):
    idx = find_by(collection, key, value)
    if idx == -1:
        return

    remove_item(collection, idx, idx_data, idx_prop)


def find_by(collection, key, value):
    for i, item in enumerate(collection):
        item_value = getattr(item, key, None)
        if item_value is not None and item_value == value:
            return i

    return -1


def find_item_by(collection, key, value):
    idx = find_by(collection, key, value)
    if idx == -1:
        return None

    return collection[idx]


class AddItemOperator:
    bl_label = "Add Item"
    bl_description = "Add an item"
    bl_options = {'INTERNAL'}

    idx = bpy.props.IntProperty(default=-1, options={'SKIP_SAVE'})

    def get_collection(self):
        return None

    def finish(self, item):
        pass

    def execute(self, context):
        collection = self.get_collection()
        item = collection.add()

        idx = len(collection) - 1
        if 0 <= self.idx < idx:
            collection.move(idx, self.idx)
            item = collection[self.idx]

        self.finish(item)
        return {'FINISHED'}


class MoveItemOperator:
    label_prop = "name"
    bl_idname = None
    bl_label = "Move Item"
    bl_description = "Move the item"
    bl_options = {'INTERNAL'}

    old_idx = bpy.props.IntProperty(default=-1, options={'SKIP_SAVE'})
    old_idx_last = bpy.props.IntProperty(default=-1, options={'SKIP_SAVE'})
    new_idx = bpy.props.IntProperty(default=-1, options={'SKIP_SAVE'})
    swap = bpy.props.BoolProperty(options={'SKIP_SAVE'})

    def get_collection(self):
        return None

    def get_icon(self, item, idx):
        return 'SPACE2' if idx == self.old_idx else 'SPACE3'

    def get_title(self):
        return "Swap Item" if self.swap else "Move Item"

    def get_title_icon(self):
        return 'ARROW_LEFTRIGHT' if self.swap else 'FORWARD'

    def draw_menu(self, menu, context):
        layout = menu.layout
        collection = self.get_collection()

        layout.label(text=self.get_title(), icon=ic(self.get_title_icon()))
        layout.separator()

        for i, item in enumerate(collection):
            name = getattr(item, self.label_prop, None) or "..."
            icon = self.get_icon(item, i)

            p = layout.operator(self.bl_idname, text=name, icon=ic(icon))
            p.old_idx = self.old_idx
            p.old_idx_last = self.old_idx_last
            p.new_idx = i
            p.swap = self.swap

    def finish(self):
        pass

    def execute(self, context):
        collection = self.get_collection()
        if self.old_idx < 0 or self.old_idx >= len(collection):
            return {'CANCELLED'}

        if self.old_idx_last >= 0 and (
                self.old_idx_last >= len(collection) or
                self.old_idx_last < self.old_idx):
            return {'CANCELLED'}

        if self.new_idx == -1:
            bpy.context.window_manager.popup_menu(self.draw_menu)
            return {'FINISHED'}

        if self.new_idx < 0 or self.new_idx >= len(collection):
            return {'CANCELLED'}

        if self.new_idx != self.old_idx:
            if self.old_idx_last < 0:
                collection.move(self.old_idx, self.new_idx)

                if self.swap:
                    swap_idx = self.new_idx - 1 \
                        if self.old_idx < self.new_idx \
                        else self.new_idx + 1
                    if swap_idx != self.old_idx:
                        collection.move(swap_idx, self.old_idx)

            else:
                if self.new_idx < self.old_idx:
                    for i in range(self.old_idx, self.old_idx_last + 1):
                        collection.move(self.old_idx_last, self.new_idx)
                else:
                    for i in range(0, self.old_idx_last - self.old_idx + 1):
                        collection.move(
                            self.old_idx_last - i, self.new_idx - i)

            self.finish()

        return {'FINISHED'}


class RemoveItemOperator:
    label_prop = "name"
    bl_label = "Remove Item(s)"
    bl_description = "Remove item(s)"
    bl_options = {'INTERNAL'}

    idx = bpy.props.IntProperty(default=-1, options={'SKIP_SAVE'})
    all = bpy.props.BoolProperty(options={'SKIP_SAVE'})

    def get_collection(self):
        return None

    def get_icon(self, item, idx):
        return 'SPACE3'

    def get_title(self):
        return "Remove Item"

    def get_title_icon(self):
        return 'X'

    def get_idx_data(self):
        return None

    def get_idx_prop(self):
        return None

    def draw_menu(self, menu, context):
        layout = menu.layout
        collection = self.get_collection()

        layout.label(text=self.get_title(), icon=ic(self.get_title_icon()))
        layout.separator()

        for i, item in enumerate(collection):
            name = getattr(item, self.label_prop, None) or "..."
            icon = self.get_icon(item, i)

            p = layout.operator(self.bl_idname, text=name, icon=ic(icon))
            p.idx = i

    def finish(self):
        pass

    def execute(self, context):
        if self.all:
            self.get_collection().clear()
            idx_data, idx_prop = self.get_idx_data(), self.get_idx_prop()
            if idx_data is not None and idx_prop is not None:
                setattr(idx_data, idx_prop, 0)

            self.finish()
            return {'FINISHED'}

        if self.idx == -1:
            bpy.context.window_manager.popup_menu(self.draw_menu)
            return {'FINISHED'}

        collection = self.get_collection()
        if self.idx < 0 or self.idx >= len(collection):
            return {'CANCELLED'}

        remove_item(
            collection, self.idx, self.get_idx_data(), self.get_idx_prop())

        self.finish()

        return {'FINISHED'}

    def invoke(self, context, event):
        if self.all:
            return context.window_manager.invoke_confirm(self, event)

        return self.execute(context)
