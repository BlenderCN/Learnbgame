from .literal_semantic import NonTerminal, Define


class Lsystem:

    def __init__(self):
        self._non_terminals = dict()
        self._defines = dict()
        self.start = None

    def approx_steps(self, iteration):
        return self.start.result_len(iteration)

    def get_define(self, name, create=False):
        if name in self._defines:
            return self._defines[name]
        else:
            if not create:
                raise RuntimeError("Can't use a define before declaring it")
            self._defines[name] = Define()
            return self._defines[name]

    def get_non_terminal(self, name):
        if name in self._non_terminals:
            return self._non_terminals[name]
        else:
            self._non_terminals[name] = NonTerminal()
            return self._non_terminals[name]
