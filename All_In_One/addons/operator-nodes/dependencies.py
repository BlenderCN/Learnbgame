class Dependency:
    def __hash__(self):
        raise NotImplementedError()

    def evaluate(self):
        raise NotImplementedError()

class AttributeDependency:
    def __init__(self, owner, path):
        if owner is None:
            raise Exception("dependency owner must not be None")
        self.owner = owner
        self.path = path

    def __hash__(self):
        return hash((self.owner, self.path))

    def __eq__(self, other):
        return self.owner == other.owner and self.path == other.path

    def __repr__(self):
        return f"<Owner: {repr(self.owner)}, Path: {repr(self.path)}>"

    def evaluate(self):
        return self.owner.path_resolve(self.path)