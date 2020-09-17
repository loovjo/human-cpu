import random
from collections import defaultdict

from log import VM_LOG, CPU_LOG
from instruction import parse_instruction

class CPU:
    def __init__(self, address, ip, code_ref):
        self.address = address

        self.code_ref = code_ref

        self.registers = {
            "ip": ip,
            "ra": 0,
            "rx": 0,
            "ry": 0,
            "rz": 0,
            "brian": 0,
        }

        self.ram = defaultdict(int) # addr: value

        self.handlers = {} # atom: (expected-content-len, store-content-addr, run-ip)

        CPU_LOG.info(f"Made a CPU with address {hex(self.address)}")

    def receive_message(self, msg_atom, msg_content):
        CPU_LOG.info(f"{hex(self.address)} got a message: {msg_atom}/{msg_content}")

    def query_instructions(self):
        code_after_ip = self.code_ref[self.registers["ip"]:]
        CPU_LOG.debug(f"Parsing instruction {code_after_ip}")
        inst_init = parse_instruction(code_after_ip)
        if inst_init == None:
            return []
        inst = inst_init(self.address)
        return [inst]

    def __str__(self):
        return f"CPU(addr={hex(self.address)}, registers={self.registers}, ram={self.ram}, handlers={self.handlers})"

class VirtualMachine:
    def __init__(self, code):
        VM_LOG.info("Made a virtual machine!")
        self.code = code

        self.cores = [CPU(random.getrandbits(64), 0, self.code)]

    def query_instructions(self):
        VM_LOG.info("querying instructions")
        instructions = []
        for core in self.cores:
            instructions.extend(core.query_instructions())
        return instructions

    def get_core_with_addr(self, addr, default_on_not_found=True):
        for core in self.cores:
            if core.address == addr:
                return core

        if default_on_not_found:
            VM_LOG.warn(f"Tried to access CPU at address {hex(addr)}, but found nothing!")
            return CPU(-1, -1, self.code)

    def print_message(self, msg):
        print("[OUTPUT]:", msg)

    def new_actor(self, addr, ip):
        if self.get_core_with_addr(addr, default_on_not_found=False) is not None:
            print("[TRIED TO REGISTER A NEW ACTOR WITH AN ALREADY EXISTING ADDRESS")
            return

        self.cores.append(CPU(addr, ip, self.code))
