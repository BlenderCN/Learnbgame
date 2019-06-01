# Nikita Akimov
# interplanety@interplanety.org


class JsonEx:

    @staticmethod
    def vector2_to_json(vector):
        return [vector.x, vector.y]

    @staticmethod
    def vector2_from_json(vector, vector_in_json):
        vector.x = vector_in_json[0]
        vector.y = vector_in_json[1]

    @staticmethod
    def vector3_to_json(vector):
        return [vector.x, vector.y, vector.z]

    @staticmethod
    def vector3_from_json(vector, vector_in_json):
        vector.x = vector_in_json[0]
        vector.y = vector_in_json[1]
        vector.z = vector_in_json[2]

    @staticmethod
    def prop_array_to_json(prop_array):
        rez = []
        for prop in prop_array:
            rez.append(prop)
        return rez

    @staticmethod
    def prop_array_from_json(prop_array, prop_array_in_json):
        for i, prop in enumerate(prop_array_in_json):
            prop_array[i] = prop

    @staticmethod
    def color_to_json(color):
        return [color.r, color.g, color.b]

    @staticmethod
    def color_from_json(color, color_in_json):
        color.r = color_in_json[0]
        color.g = color_in_json[1]
        color.b = color_in_json[2]
