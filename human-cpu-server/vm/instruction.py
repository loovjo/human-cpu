import struct
from abc import ABC, abstractmethod
from enum import Enum

import action

class Argument(ABC):
    @abstractmethod
    def get_value(self, cpu):
        pass

    @abstractmethod
    def get_desc(self):
        pass

class Constant(Argument):
    def __init__(self, val):
        self.val = val

    def get_value(self, _cpu):
        return self.val

    def get_desc(self):
        return hex(self.val)

class Register(Argument):
    def __init__(self, reg):
        self.reg = reg

    def get_value(self, cpu):
        return cpu.registers[self.reg]

    def get_desc(self):
        return f"register ${self.reg}"

def parse_constant(bytestr):
    if len(bytestr) < 9:
        return None

    if bytestr[0] != 0x4e:
        return None

    return Constant(*struct.unpack("Q", bytestr[1:9])), 9

REGISTERS = {
    0x40: "ip",
    0x41: "ra",
    0x48: "rhen",
    0x78: "rx",
    0x79: "ry",
    0x7a: "rz",
    0x58: "brian",
}
def parse_register(bytestr):
    if len(bytestr) < 1:
        return None

    if bytestr[0] in REGISTERS:
        return Register(REGISTERS[bytestr[0]]), 1

    return None

def parser_any(*parsers):
    def parse(bytestr):
        for parser in parsers:
            res = parser(bytestr)
            if res is not None:
                return res
        return None

    return parse

parse_argument = parser_any(parse_register, parse_constant)


def make_instparser(cls, instruction_tag, n_args):
    def parse(bytestr):
        if len(bytestr) < 1:
            return None
        if bytestr[0] != instruction_tag:
            return None

        args = []
        at = 1
        for i in range(n_args):
            res = parse_argument(bytestr[at:])
            if res is None:
                return None
            arg, delta = res
            at += delta
            args.append(arg)

        def make_instance(req_addr):
            return cls(req_addr, *args)

        return make_instance

    return parse

class Instruction(ABC):
    def __init__(self, req_addr):
        self.req_addr = req_addr

    @abstractmethod
    def get_desc(self):
        pass

    # Make/fake an action appropriately performing this instruction
    @abstractmethod
    def fake_action(self, cpu):
        pass

    # Gives either:
    #   (Instruction, int) - The parsed instruction and how many bytes the instruction took
    #   None - The instruction could not be parsed
    @abstractmethod
    def parse(bytestr):
        pass

class Set(Instruction):
    def __init__(self, req_addr, reg, val):
        super().__init__(req_addr)

        assert(isinstance(reg, Register))
        self.reg = reg
        self.val = val

    def get_desc(self):
        return f"Set {self.reg.get_desc()} to {self.val.get_desc()}"

    def fake_action(self, cpu):
        val = self.val.get_value(cpu)
        return action.WriteToCPU(self.req_addr, new_ram={}, new_regs={self.reg.reg: val})

    parse = make_instparser(lambda *x: Set(*x), 0x53, 2)

class SetMem(Instruction):
    def __init__(self, req_addr, addr, val):
        super().__init__(req_addr)
        self.addr = addr
        self.val = val

    def get_desc(self):
        return f"Set the RAM at address {self.addr.get_desc()} to {self.val.get_desc()}"

    def fake_action(self, cpu):
        addr = self.addr.get_value(cpu)
        val = self.val.get_value(cpu)
        return action.WriteToCPU(self.req_addr, new_ram={addr: val}, new_regs={})

    parse = make_instparser(lambda *x: SetMem(*x), 0x73, 2)

class ReadMem(Instruction):
    def __init__(self, req_addr, reg_res, addr):
        super().__init__(req_addr)

        assert(isinstance(reg_res, Register))
        self.reg_res = reg_res
        self.addr = addr

    def get_desc(self):
        return f"Set {self.reg_res.get_desc()} to the value at RAM address {self.addr.get_desc()}"

    def fake_action(self, cpu):
        val = cpu.ram[self.val.get_value(cpu)]
        return action.WriteToCPU(self.req_addr, new_ram={}, new_regs={self.reg.reg: val})

    parse = make_instparser(lambda *x: ReadMem(*x), 0x52, 2)

class ArithmeticVariant(Enum):
    ADD = 0x2b
    SUB = 0x2d
    MUL = 0x2a
    DIV = 0x2f
    LT = 0x3c
    LE = 0x5b
    EQ = 0x3d
    GT = 0x3e
    GE = 0x5d

    def get_desc(self, a, b):
        if self == ArithmeticVariant.ADD: return f"{a} + {b}"
        if self == ArithmeticVariant.SUB: return f"{a} - {b}"
        if self == ArithmeticVariant.MUL: return f"{a} + {b}"
        if self == ArithmeticVariant.DIV: return f"{a} / {b} (integer division rounding down)"

        if self == ArithmeticVariant.LT: return f"1 if {a} < {b}, 0 otherwise"
        if self == ArithmeticVariant.LE: return f"1 if {a} &le; {b}, 0 otherwise"
        if self == ArithmeticVariant.EQ: return f"1 if {a} = {b}, 0 otherwise"
        if self == ArithmeticVariant.GT: return f"1 if {a} > {b}, 0 otherwise"
        if self == ArithmeticVariant.GE: return f"1 if {a} &ge; {b}, 0 otherwise"

    def perform(self, a, b):
        if self == ArithmeticVariant.ADD: return a + b
        if self == ArithmeticVariant.SUB: return a - b
        if self == ArithmeticVariant.MUL: return a + b
        if self == ArithmeticVariant.DIV: return a // b

        if self == ArithmeticVariant.LT: return a < b
        if self == ArithmeticVariant.LE: return a <= b
        if self == ArithmeticVariant.EQ: return a == b
        if self == ArithmeticVariant.GT: return a > b
        if self == ArithmeticVariant.GE: return a >= b


class Arithmetic(Instruction):
    def __init__(self, variant, req_addr, output, arg1, arg2):
        super().__init__(req_addr)

        assert(isinstance(output, Register))

        self.variant = variant
        self.output = output
        self.arg1 = arg1
        self.arg2 = arg2

    def get_desc(self):
        return f"Set {self.output.get_desc()} to {self.variant.get_desc(self.arg1.get_desc(), self.arg2.get_desc())}"

    def fake_action(self, cpu):
        v1 = self.arg1.get_value(cpu)
        v2 = self.arg2.get_value(cpu)
        res = self.variant.perform(v1, v2)

        return action.WriteToCPU(self.req_addr, new_ram={}, new_regs={self.output.reg: res})

    def make_parse(variant):
        return make_instparser(lambda *x: Arithmetic(variant, *x), variant.value, 3)

    parse_add = make_parse(ArithmeticVariant.ADD)
    parse_sub = make_parse(ArithmeticVariant.SUB)
    parse_mul = make_parse(ArithmeticVariant.MUL)
    parse_div = make_parse(ArithmeticVariant.DIV)
    parse_lt = make_parse(ArithmeticVariant.LT)
    parse_le = make_parse(ArithmeticVariant.LE)
    parse_eq = make_parse(ArithmeticVariant.EQ)
    parse_gt = make_parse(ArithmeticVariant.GT)
    parse_ge = make_parse(ArithmeticVariant.GE)

    parse = parser_any(parse_add, parse_sub, parse_mul, parse_div, parse_lt, parse_le, parse_eq, parse_gt, parse_ge)


class SendMessage(Instruction):
    def __init__(self, req_addr, receiver, atom, content_len, content_addr):
        super().__init__(req_addr)

        self.receiver = receiver
        self.atom = atom
        self.content_len = content_len
        self.content_addr = content_addr

    def get_desc(self):
        return f"Send a message to {self.receiver.get_desc()}, with the atom " + \
            f"{self.atom.get_desc()} and a content cosisting of {self.content_len.get_desc()} " + \
            f"bytes in ram, starting at {self.content_addr.get_desc()}"

    def fake_action(self, cpu):
        receiver = self.receiver.get_value(cpu)
        atom = self.atom.get_value(cpu)
        content_len = self.content_len.get_value(cpu)
        content_addr = self.content_addr.get_value(cpu)

        assert(content_len <= 0x8)
        content = [cpu.ram[i] for i in range(content_addr, content_addr + content_len)]

        return action.SendMessage(receiver, atom, content)

    parse = make_instparser(lambda *x: SendMessage(*x), 0x5e, 4)

class MakeHandler(Instruction):
    def __init__(self, req_addr, atom, expected_content_len, content_addr, run_ip):
        super().__init__(req_addr)

        self.atom = atom
        self.expected_content_len = expected_content_len
        self.content_addr = content_addr
        self.run_ip = run_ip

    def get_desc(self):
        return f"Create a message handler, handling atom {self.atom.get_desc()}, expecting " + \
            f"{self.expected_content_len.get_desc()} bytes of content. The content should end " + \
            f"address {self.content_addr.get_desc()} and should run at {self.run_ip.get_desc()}"

    def fake_action(self, cpu):
        atom = self.atom.get_value(cpu)
        expected_content_len = self.expected_content_len.get_value(cpu)
        content_addr = self.content_addr.get_value(cpu)
        run_ip = self.run_ip.get_value(cpu)

        return action.MakeNewHandler(self.req_addr, atom, expected_content_len, content_addr, run_ip)

    parse = make_instparser(lambda *x: MakeHandler(*x), 0x21, 4)

parse_instruction = parser_any(
    Set.parse,
    SetMem.parse,
    ReadMem.parse,
    Arithmetic.parse,
    SendMessage.parse,
    MakeHandler.parse,
)
