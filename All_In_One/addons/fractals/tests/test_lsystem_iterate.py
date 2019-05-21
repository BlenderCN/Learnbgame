import unittest
from lsystem.lsystem_class import Lsystem
from lsystem.lsystem_parse import parse as lparse
from lsystem.literal_semantic import (RotateTerminal,
                                      MoveTerminal, DrawTerminal,
                                      PushTerminal, PopTerminal)
import sys, os

import grammar_output


class TestLsystemIterate(unittest.TestCase):
    def test_iterate(self):
        for grammar_path, grammar_level, grammar_result in grammar_output.TEST_OUTPUTS:
            real_path = os.path.join("examples", "standard", grammar_path)
        with open(real_path) as grammar_file:
            my_lsystem = lparse(grammar_file.read())
            self.assertListEqual(
                [str(x) for x in my_lsystem.start.iterate(grammar_level)], grammar_result)
            # print([str(x) for x in my_lsystem.start.iterate(12)])
