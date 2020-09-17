import vm

CODE = open("test-code.bin", "rb").read()

virt = vm.VirtualMachine(CODE)

instructions = virt.query_instructions()
print(len(instructions), "available")

for inst in instructions:
    print("==")
    print(inst)
    print(inst.get_desc())
    print(inst.fake_action(virt.cores[0]))
