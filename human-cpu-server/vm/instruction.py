import struct
from abc import ABC, abstractmethod

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
        return "register {self.val}"

def parse_constant(bytestr):
    if len(bytestr) < 9:
        return None

    if bytestr[0] != 0x4e:
        return None

    return ConstantArgument(struct.unpack("Q", bytestr[1:9])), 9

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
        return Register(bytestr[0]), 1

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
            arg, at = res
            args.append(arg)

        return cls(*args)

    return parse

class Instruction(ABC):
    @abstractmethod
    def __init__(self, req_addr):
        self.req_addr

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
        super(Set).__init__(self, req_addr)

        assert(isinstance(reg, RegisterArgument))
        self.reg = reg
        self.val = val

    def get_desc(self):
        return f"Set {self.reg.get_desc()} to {self.val.get_desc()}"

    def fake_action(self, cpu):
        val = self.val.get_value(cpu)
        return action.WriteToCPU(self.req_addr, new_ram={}, new_regs={self.reg.reg: val})

    parse = make_instparser(Set, 0x53, 2)

class SetMem(Instruction):
    def __init__(self, req_addr, addr, val):
        super(SetMem).__init__(self, req_addr)
        self.addr = addr
        self.val = val

    def get_desc(self):
        return f"Set the RAM at address {self.addr.get_desc()} to {self.val.get_desc()}"

    def fake_action(self, cpu):
        addr = self.addr.get_value(cpu)
        val = self.val.get_value(cpu)
        return action.WriteToCPU(self.req_addr, new_ram={addr: val}, new_regs={})

    parse = make_instparser(SetMem, 0x73, 2)

class ReadMem(Instruction):
    def __init__(self, req_addr, reg_res, addr):
        super(ReadMem).__init__(self, req_addr)

        assert(isinstance(reg_res, RegisterArgument))
        self.reg_res = reg_res
        self.addr = addr

    def get_desc(self):
        return f"Set {self.reg_res.get_desc()} to the value at RAM address {self.addr.get_desc()}"

    def fake_action(self, cpu):
        val = cpu.ram[self.val.get_value(cpu)]
        return action.WriteToCPU(self.req_addr, new_ram={}, new_regs={self.reg.reg: val})

    parse = make_instparser(Set, 0x52, 2)
