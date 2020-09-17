import vm

def display_instinfo(code):
    virt = vm.VirtualMachine(code)

    instructions = virt.query_instructions()

    for inst in instructions:
        print("==")
        print("Instruction:", inst)
        print("Human description:", inst.get_desc())
        print("Wanted action:", inst.fake_action(virt.cores[0]))

# Add ra 0x1234 0x4321
display_instinfo(b"+AN\x12\x34\x00\x00\x00\x00\x00\x00N\x43\x21\x00\x00\x00\x00\x00\x00")

