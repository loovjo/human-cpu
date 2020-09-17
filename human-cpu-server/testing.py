import unittest

from assembler import tokenize

class TestTokenization(unittest.TestCase):
    def test_simple_with_whitespace(self):
        self.assertEqual(
            tokenize("Set $ra #100"),
            [ ("Set", "instruction")
            , (" ", "whitespace")
            , ("$ra", "register")
            , (" ", "whitespace")
            , ("#100", "constant")
            ]
        )

        self.assertEqual(
            tokenize("'hello Set $rip `hello`"),
            [ ("'hello", "label")
            , (" ", "whitespace")
            , ("Set", "instruction")
            , (" ", "whitespace")
            , ("$rip", "register")
            , (" ", "whitespace")
            , ("`hello", "py-expr")
            , ("`", "py-expr-end")
            ]
        )

    def test_simple_without_whitespace(self):
        self.assertEqual(
            tokenize("Set$ra#100"),
            [ ("Set", "instruction")
            , ("$ra", "register")
            , ("#100", "constant")
            ]
        )

    def test_neighbouring_of_same_kind(self):
        self.assertEqual(
            tokenize("$ip$ra"),
            [ ("$ip", "register")
            , ("$ra", "register")
            ]
        )

        self.assertEqual(
            tokenize("#1#2"),
            [ ("#1", "constant")
            , ("#2", "constant")
            ]
        )


if __name__ == '__main__':
    unittest.main()
