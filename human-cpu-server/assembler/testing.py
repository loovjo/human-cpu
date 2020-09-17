import unittest

from parser import *
from compile_ctx import CompileCtx

class TestTokenization(unittest.TestCase):
    def test_simple_with_whitespace(self):
        self.assertEqual(
            tokenize("Set $ra #100"),
            [ ("Set", "instruction")
            , ('', 'cat-break')
            , (" ", "whitespace")
            , ('', 'cat-break')
            , ("$ra", "register")
            , ('', 'cat-break')
            , (" ", "whitespace")
            , ('', 'cat-break')
            , ("#100", "constant")
            ]
        )

        self.assertEqual(
            tokenize("'hello Set $rip `hello`"),
            [ ("'hello", "labeldef")
            , ('', 'cat-break')
            , (" ", "whitespace")
            , ('', 'cat-break')
            , ("Set", "instruction")
            , ('', 'cat-break')
            , (" ", "whitespace")
            , ('', 'cat-break')
            , ("$rip", "register")
            , ('', 'cat-break')
            , (" ", "whitespace")
            , ('', 'cat-break')
            , ("`hello", "py-expr")
            , ("`", "py-expr-end")
            ]
        )

    def test_simple_without_whitespace(self):
        self.assertEqual(
            tokenize("Set$ra#100"),
            [ ("Set", "instruction")
            , ('', 'cat-break')
            , ("$ra", "register")
            , ('', 'cat-break')
            , ("#100", "constant")
            ]
        )

    def test_neighbouring_of_same_kind(self):
        self.assertEqual(
            tokenize("$ip$ra"),
            [ ("$ip", "register")
            , ('', 'cat-break')
            , ("$ra", "register")
            ]
        )

        self.assertEqual(
            tokenize("#1#2"),
            [ ("#1", "constant")
            , ('', 'cat-break')
            , ("#2", "constant")
            ]
        )

    def test_cleanup(self):
        self.assertEqual(
            cleanup(tokenize("'x Set $ra `2+2`")),
            [ ("x", "labeldef")
            , ("Set", "instruction")
            , ("ra", "register")
            , ("2+2", "py-expr")
            ]
        )


class TestCompiler(unittest.TestCase):
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

    def test_simple_labels(self):
        ctx = CompileCtx()
        ctx.write_expr('hello')
        ctx.write_byte(0x88)
        ctx.write_labelpos('world') # world = 9

        ctx.write_expr('world')
        ctx.write_u64(0xffffffffffffffff)
        ctx.write_labelpos('hello') # hello = 25

        self.assertEqual(
            ctx.postproc(),
            b'\x19\x00\x00\x00\x00\x00\x00\x00\x88\x09\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff',
        )

    def test_complex_labels(self):
        ctx = CompileCtx()
        ctx.write_expr('hello + world') # 34 = 0x22
        ctx.write_byte(0x88)
        ctx.write_labelpos('world') # world = 9

        ctx.write_expr('world * 10 - hello') # 65 = 0x41
        ctx.write_u64(0xffffffffffffffff)
        ctx.write_labelpos('hello') # hello = 25


        self.assertEqual(
            ctx.postproc(),
            b'\x22\x00\x00\x00\x00\x00\x00\x00\x88\x41\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff',
        )


if __name__ == '__main__':
    unittest.main()
