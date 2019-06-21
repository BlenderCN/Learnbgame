def listToTuple(lista):
    i = 0
    for index in lista:
        lista[i] = tuple(index)
        i = i + 1
    return lista
