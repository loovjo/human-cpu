import vm

def display_instinfo(code):
    print("\n"*3)
    virt = vm.VirtualMachine(code)

    instructions = virt.query_instructions()

    for inst in instructions:
        print("==")
        print("Instruction:", inst)
        print("Human description:", inst.get_desc())

        action = inst.fake_action(virt.cores[0])

        print("Wanted action:", inst.fake_action(virt.cores[0]))
        action.run(virt)
        print("Afterwards:", virt.cores[0])



# Add ra 0x1234 0x4321
display_instinfo(b"+AN\x12\x34\x00\x00\x00\x00\x00\x00N\x43\x21\x00\x00\x00\x00\x00\x00")

# Set ra 0x5577
display_instinfo(b"SAN\x12\x34\x00\x00\x00\x00\x00\x00")

