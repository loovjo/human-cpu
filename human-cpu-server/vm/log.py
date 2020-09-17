import logging


logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s")
VM_LOG = logging.getLogger("VM")

CPU_LOG = logging.getLogger("CPU")

ACTION_LOG = logging.getLogger("Action")
INSTRUCTION_LOG = logging.getLogger("Instruction")
