last_key db 0
key_pressed db 0
keyboard_handler:
    push ax
    in al, 0x60
    test al, 0x80
    jnz .done
    mov [last_key], al
    mov byte [key_pressed], 1
.done:
    mov al, 0x20
    out 0x20, al
    pop ax
    iret
scancode_to_ascii:
    push bx
    mov bx, .table
    xlatb
    pop bx
    ret
.table:
    db 0, 0, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 8, 9
    db 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', 13, 0, 'a', 's'
    db 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", '`', 0, '\\', 'z', 'x', 'c', 'v'
    db 'b', 'n', 'm', ',', '.', '/', 0, '*', 0, ' ', 0, 0, 0, 0, 0, 0
get_key:
.wait:
    hlt
    cmp byte [key_pressed], 0
    je .wait
    mov al, [last_key]
    mov byte [key_pressed], 0
    call scancode_to_ascii
    test al, al
    jz .wait
    ret
