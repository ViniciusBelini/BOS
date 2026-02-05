syscall_handler:
    cmp ah, 0
    je .print_char
    cmp ah, 1
    je .print_string
    cmp ah, 2
    je .get_key
    iret
.print_char:
    call print_char_direct
    iret
.print_string:
    call print_string_direct
    iret
.get_key:
    call get_key
    iret
init_syscalls:
    push es
    xor ax, ax
    mov es, ax
    mov word [es:0x30*4], syscall_handler
    mov [es:0x30*4+2], cs
    pop es
    ret
