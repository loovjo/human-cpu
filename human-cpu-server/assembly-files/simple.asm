'start

    Make-handler `on_child_created` `1` `0x1000` `on_child_created`

    Create-actor `run_a` $ra

    Idle


'on_child_created

    ReadMem $ra `0x1000`

    SetMem `0x1008` `0x696a6b`

    Send-msg $ra `get_msg` `0x1` `0x1008`


'run_a
    Make-handler `get_msg` `2` `0x1000` `get_msg`

    Self-addr $rx
    SetMem `0x1000` $rx

    Send-msg $ra `on_child_created` `1` `0x1000`

    Idle


'get_msg

    Print `0x0` `0x1000`
