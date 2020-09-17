'start
    Make-handler `on_child_created` `1` `0x100` `on_child_created`
    Create-actor `init_child`
    Idle

'on_child_created

    SetMem `0x1000` `0x68656c6c6f`

    ReadMem $ra `0x100`
    Send-msg $ra `print_msg` `0x1` `0x1000`

    SetMem `0x1000` `0x20776f726c64`
    Send-msg $ra `print_msg` `0x1` `0x1000`

    Idle


'init_child
    Make-handler `print_msg` `1` `0x1000` `print_msg`

    Self-addr $rx
    SetMem `0x100` $rx

    Send-msg $ra `on_child_created` `1` `0x100`

    Idle

'print_msg
    Print `0x5` `0x1000`
