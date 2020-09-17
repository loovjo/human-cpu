import vm

CODE = open("test-code.bin", "rb").read()

virt = vm.VirtualMachine(CODE)

instructions = virt.query_instructions()
print(instructions)
