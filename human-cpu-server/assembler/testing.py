import unittest

from parser import tokenize
from compile_ctx import CompileCtx

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


class TestTokenization(unittest.TestCase):

    def test_write_bytes(self):
        ctx = CompileCtx()
        ctx.write_byte(5)
        ctx.write_byte(6)
        ctx.write_byte(7)
        self.assertEqual(
            ctx.postproc(),
            bytes([5, 6, 7]),
        )

    def test_write_u64s(self):
        ctx = CompileCtx()
        ctx.write_u64(5)
        ctx.write_u64(0xffffff)
        self.assertEqual(
            ctx.postproc(),
            b'\x05\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\x00\x00\x00\x00\x00',
        )

    def test_labels(self):
        ctx = CompileCtx()
        ctx.write_labelref('hello')
        ctx.write_byte(0x88)
        ctx.write_labelpos('world')

        ctx.write_labelref('world')
        ctx.write_u64(0xffffffffffffffff)
        ctx.write_labelpos('hello')


        self.assertEqual(
            ctx.postproc(),
            b'\x19\x00\x00\x00\x00\x00\x00\x00\x88\x09\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff',
        )


if __name__ == '__main__':
    unittest.main()
