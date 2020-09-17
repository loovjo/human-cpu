from abc import ABC, abstractmethod
from compile_ctx import CompileCtx

class Instruction(ABC):
    @abstractmethod
    def compile_to_bytes(self, mutctx):
        pass

    @abstractmethod
    def __str__(self):
        pass

    def __repr__(self):
        return str(self)

class InstructionArgument(Instruction):
    pass


REGISTERS = {
    "ip": 0x40,
    "ra": 0x41,
    "rhen": 0x48,
    "rx": 0x78,
    "ry": 0x79,
    "rz": 0x7a,
    "brian": 0x58,
}

NUM_REGISTER_MARK = 0x4e

class RegisterArgument(InstructionArgument):
    def __init__(self, regname):
        assert(regname in REGISTERS.keys())
        self.regname = regname

    def compile_to_bytes(self, mutctx):
        mutctx.write_byte(REGISTERS[self.regname])

    def __str__(self):
        return f'RegisterArgument({self.regname})'

class ConstantArgument(InstructionArgument):
    def __init__(self, value):
        self.value = value

    def compile_to_bytes(self, mutctx):
        mutctx.write_byte(NUM_REGISTER_MARK)
        mutctx.write_u64(self.value)

    def __str__(self):
        return f'ConstantArgument({self.value})'

class PyExprArgument(InstructionArgument):
    def __init__(self, content):
        self.content = content

    def compile_to_bytes(self, mutctx):
        mutctx.write_byte(NUM_REGISTER_MARK)
        mutctx.write_expr(self.content)

    def __str__(self):
        return f'PyExprArgument({self.content})'

CPU_INSTRUCTIONS = {
             "Set": 0x53, # = 'S'
          "SetMem": 0x73, # = 's'
         "ReadMem": 0x52, # = 'R'

             "Add": 0x2b, # = '+'
             "Sub": 0x2d, # = '-'
             "Mul": 0x2a, # = "*"
             "Div": 0x2f, # = '/'

              "LT": 0x3c, # = '<'
              "LE": 0x5b, # = '['
              "EQ": 0x3d, # = '='
              "GT": 0x3e, # = '>'
              "GE": 0x5d, # = ']'

            "Idle": 0x49, # = 'I'
        "Send-msg": 0x5e, # = '^'
    "Make-handler": 0x21, # = '!'
       "Self-addr": 0x3f, # = '?'
    "Create-actor": 0x7d, # = '}'
           "Print": 0x23, # = '#'
}

class CpuInstruction(Instruction):
    def __init__(self, instruction, arguments):
        assert(instruction in CPU_INSTRUCTIONS.keys())
        self.instruction = instruction
        self.arguments = arguments

    def compile_to_bytes(self, mutctx):
        mutctx.write_byte(CPU_INSTRUCTIONS[self.instruction])
        for arg in self.arguments:
            arg.compile_to_bytes(mutctx)

    def __str__(self):
        return f'CpuInstruction({self.instruction}, {self.arguments})'


class LabelDef(Instruction):
    def __init__(self, name):
        self.name = name

    def compile_to_bytes(self, mutctx):
        mutctx.write_labelpos(self.name)

    def __str__(self):
        return f'LabelDef({self.name})'

def read_instlist(parsed_input):
    parsed_input.append(("", "instruction"))
    instlist = []

    at = 0

    # states:
    #   ("outside", None)
    #   ("parsing_args", (instname, [arglist])
    current_state = ("outside", None)

    while at < len(parsed_input):
        content, cat = parsed_input[at]

        if current_state[0] == "parsing_args" and cat in ["instruction", "labeldef"]:
            instlist.append(
                CpuInstruction(current_state[1][0], current_state[1][1])
            )
            current_state = ("outside", None)
            continue

        if cat == "instruction" and current_state[0] == "outside":
            current_state = ("parsing_args", (content, []))
            at += 1
            continue

        if cat == "labeldef" and current_state[0] == "outside":
            instlist.append(LabelDef(content))
            at += 1
            continue

        if cat == "constant" and current_state[0] == "parsing_args":
            current_state[1][1].append(ConstantArgument(content))
            at += 1
            continue

        if cat == "register" and current_state[0] == "parsing_args":
            current_state[1][1].append(RegisterArgument(content))
            at += 1
            continue

        if cat == "py-expr" and current_state[0] == "parsing_args":
            current_state[1][1].append(PyExprArgument(content))
            at += 1
            continue

        print("Reached invalid token: ...", parned_input[at-2:at], "<---")
        break

    return instlist


if __name__ == "__main__":
    import parser
    tklst = parser.cleanup(parser.tokenize("""
Set $ra $rx
Print `0x10`

"""))

    print("tklst", tklst)
    instlst = read_instlist(tklst)
    print(instlst)

    cctx = CompileCtx()
    for tk in instlst:
        tk.compile_to_bytes(cctx)

    print(cctx.postproc())
