import random
from collections import defaultdict

from log import VM_LOG, CPU_LOG

class CPU:
    def __init__(self, address, ip):
        self.address = address

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

        CPU_LOG.info(f"Made a CPU with address {self.address}")

    def receive_message(self, msg_atom, msg_content):
        print("you've got mail!")


class VirtualMachine:
    def __init__(self, code):
        VM_LOG.info("Made a virtual machine!")
        self.code = code

        self.cores = [CPU(random.getrandbits(64), 0)]

    def get_core_with_addr(self, addr, default_on_not_found=True):
        for core in self.cores:
            if core.address == addr:
                return core

        print(f"Tried to access CPU at address {hex(addr)}, but found nothing!")
        if default_on_not_found:
            return CPU(-1)

    def print_message(self, msg):
        print("[OUTPUT]:", msg)

    def new_actor(self, addr, ip):
        if self.get_core_with_addr(addr, default_on_not_found=False) is not None:
            print("[TRIED TO REGISTER A NEW ACTOR WITH AN ALREADY EXISTING ADDRESS")
            return

        self.cores.append(CPU(addr, ip))
