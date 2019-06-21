class MapUVError(Exception):
    def __init__(self, layer, distance, data):
        self.layer = layer
        self.distance = distance
        self.data = data
        
    def __str__(self):
        return repr([self.layer, self.distance, self.data])