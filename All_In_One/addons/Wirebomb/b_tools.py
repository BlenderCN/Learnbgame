def layerlist_to_numberset(layer_list):
    """Converts a layer list to a number set.

    Converts a layer list consisting of booleans to a number set consisting of integers,
    representing the layers that are True in layer_list.

    Example:
        >>> print(layerlist_to_numberset([False, True, False, False, True]))
        {1, 4}

        This because layer 2 (index 1) and layer 3 (index 4) are both True.

    Args:
        layer_list: A list with booleans representing which layers are True and which are not.
            The first item represents the first layer and so on.

    Returns:
        A set consisting of integers representing the layers that are True in layer_list.
    """
    # TODO: Maybe put in the BlenderScene class as a @staticmethod?
    number_set = set()

    for i in range(0, 20):
        if layer_list[i]:
            number_set.add(i)

    return number_set


def manipulate_layerlists(mode, list1, list2):
    """Adds or subtracts two layer lists.

    Example:
        >>> print(manipulate_layerlists('add', [False, True, True, False], [True, True, False, False]))
        [True, True, True, False]
        >>> print(manipulate_layerlists('subtract', [False, True, True, False], [True, True, False, False]))
        [False, False, True, False]

    Args:
        mode: A string, either 'add' to add the lists or 'subtract' to subtract list2 from list1.
        list1: One of the layer lists.
        list2: The other one of the layer lists.

    Returns:
        The combined layer list.
    """
    layers = []

    if mode == 'add':
        for i in range(20):
            if list1[i] is True or list2[i] is True:
                layers.append(True)

            else:
                layers.append(False)

    elif mode == 'subtract':
        for i in range(20):
            if list1[i] is True and list2[i] is True:
                layers.append(False)

            else:
                layers.append(list1[i])

    return layers
