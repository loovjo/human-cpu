import struct
import simpleeval


class CompileCtx:
    def __init__(self):
        self.output_bytes = b''

        self.exprs = {} # {byte_position: string expression}
        self.label_contents = {} # {label name: position}


    def write_byte(self, b):
        self.output_bytes = self.output_bytes + bytes([b])

    def write_u64(self, b):
        self.output_bytes = self.output_bytes + struct.pack("Q", b)

    def write_expr(self, expr):
        self.exprs[len(self.output_bytes)] = expr
        self.write_u64(0x4142434445464748)

    def new_inst(self):
        self.current_ip = len(self.output_bytes)

    def write_labelpos(self, label_name):
        self.label_contents[label_name] = len(self.output_bytes)

    def postproc(self):
        resulting_output = self.output_bytes
        for idx, expr in self.exprs.items():
            value = simpleeval.simple_eval(expr, names={"$": idx, **self.label_contents})
            assert(type(value) == int)
            enc = struct.pack("Q", value)

            resulting_output = resulting_output[:idx] + enc + resulting_output[idx+len(enc):]

        return resulting_output
