from abc import ABC, abstractmethod

class Action(ABC):
    @abstractmethod
    def __str__(self):
        pass

    def __repr__(self):
        return str(self)

    # What are the addresses of the cores this action impacts?
    # 0 = affects all cores (printing and creating actors)
    @abstractmethod
    def affects(self):
        pass

    @abstractmethod
    def __eq__(self, other):
        pass

    @abstractmethod
    def run(self, vm):
        pass

class WriteToCPU(Action):
    def __init__(self, cpu_addr, new_ram, new_regs):
        self.cpu_addr = cpu_addr
        self.new_ram = new_ram
        self.new_regs = new_regs

    def affects(self):
        return [self.cpu_addr]

    def __eq__(self, other):
        if not isinstance(other, WriteToCPU):
            return False

        return self.cpu_addr == other.cpu_addr and self.new_ram == other.new_ram and self.new_regs == other.new_regs

    def __str__(self):
        return f"WriteToCPU(cpu_addr={hex(self.cpu_addr)}, new_ram={self.new_ram}, new_regs={self.new_regs})"

    def run(self, vm):
        core = vm.get_core_with_addr(self.cpu_addr)

        for addr, val in self.new_ram.items():
            core.ram[addr] = val

        for reg, val in self.new_regs.items():
            core.registers[reg] = val

class MakeNewHandler(Action):
    def __init__(self, cpu_addr, atom, n_args, write_args_to, run_ip):
        self.cpu_addr = cpu_addr
        self.atom = atom
        self.n_args = n_args
        self.write_args_to = write_args_to
        self.run_ip = run_ip

    def affects(self):
        return [self.cpu_addr]

    def __eq__(self, other):
        if not isinstance(other, MakeNewHandler):
            return False

        return self.cpu_addr == other.cpu_addr and self.atom == other.atom \
            and self.n_args == other.n_args and self.write_args_to == other.write_args_to \
            and self.run_ip == other.run_ip

    def __str__(self):
        args = []
        args.append(f"cpu_addr={hex(self.cpu_addr)}")
        args.append(f"atom={hex(self.atom)}")
        args.append(f"n_args={hex(self.n_args)}")
        args.append(f"write_args_to={hex(self.write_args_to)}")
        args.append(f"run_ip={hex(self.run_ip)}")
        return f"MakeNewHandler({', '.join(args)})"

    def run(self, vm):
        core = vm.get_core_with_addr(self.cpu_addr)

        core.handlers[self.atom] = (self.n_args, self.write_args_to, self.run_ip)

class SendMessage(Action):
    def __init__(self, receiver, atom, content):
        self.receiver = receiver
        self.atom = atom
        self.content = content

    def affects(self):
        return [self.receiver]

    def __eq__(self, other):
        if not isinstance(other, SendMessage):
            return False

        return self.receiver == other.receiver and self.atom == other.atom \
            and self.content == other.content

    def __str__(self):
        return f"SendMessage(receiver={hex(self.receiver)}, atom={hex(self.atom)}, content={self.content})"

    def run(self, vm):
        core = vm.get_core_with_addr(self.receiver)

        core.receive_message(self.atom, self.content)

class Print(Action):
    def __init__(self, msg):
        self.msg = msg

    def affects(self):
        return [0]

    def __eq__(self, other):
        if not isinstance(other, Print):
            return False

        return self.msg == other.msg

    def __str__(self):
        return f"Print(msg={self.msg})"

    def run(self, vm):
        vm.print_message(self.msg)

class CreateActor(Action):
    def __init__(self, new_actor_addr, run_ip, creator_addr):
        self.new_actor_addr = new_actor_addr
        self.run_ip = run_ip
        self.creator_addr = creator_addr

    def affects(self):
        return [0]

    def __eq__(self, other):
        if not isinstance(other, CreateActor):
            return False

        # Intentionally skip comparing new_actor_addr as it is arbitrary
        return self.run_ip == other.run_ip and self.creator_addr == other.creator_addr

    def __str__(self):
        return f"CreateActor(new_actor_addr={hex(self.new_actor_addr)}, run_ip={hex(self.run_ip)}, creator_addr={hex(self.creator_addr)})"

    def run(self, vm):
        vm.new_actor(self.new_actor_addr, self.run_ip)
