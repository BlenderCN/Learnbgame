def enumItemsFromList(itemData):
    """
    Create a Blender ENUM data structure from a provided list of elements
    :param itemData: elements
    :type itemData: list
    :return: items
    :rtype: list of tuple elements
    """
    items = []
    for _id, element in enumerate(itemData):
        items.append((element, element, "", "NONE", _id))
    if len(items) == 0:
        items = [("NONE", "NONE", "")]
    return items
