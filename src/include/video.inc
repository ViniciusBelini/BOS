VIDEO_MEM equ 0xB800
COLOR_YELLOW equ 0x0E
COLOR_LIGHT_CYAN equ 0x0B
COLOR_WHITE equ 0x0F
COLOR_LIGHT_GRAY equ 0x07
cursor_x db 0
cursor_y db 0
current_color db 0x07
clear_screen_direct:
    pusha
    push ds
    push es
    mov ax, VIDEO_MEM
    mov es, ax
    xor di, di
    mov ax, 0x0720
    mov cx, 80 * 25
    cld
    rep stosw
    mov byte [cursor_x], 0
    mov byte [cursor_y], 0
    call update_cursor
    pop es
    pop ds
    popa
    ret
print_char_direct:
    pusha
    push ds
    push es
    cmp al, 13
    je .handle_cr
    cmp al, 10
    je .handle_lf
    cmp al, 8
    je .handle_bs
    movzx bx, byte [cursor_y]
    imul bx, 80
    movzx dx, byte [cursor_x]
    add bx, dx
    shl bx, 1
    mov dx, VIDEO_MEM
    mov es, dx
    mov ah, [current_color]
    mov [es:bx], ax
    inc byte [cursor_x]
    cmp byte [cursor_x], 80
    jge .handle_lf
    jmp .done
.handle_cr:
    mov byte [cursor_x], 0
    jmp .done
.handle_lf:
    mov byte [cursor_x], 0
    inc byte [cursor_y]
    cmp byte [cursor_y], 25
    jl .done
    call scroll_screen
    mov byte [cursor_y], 24
    jmp .done
.handle_bs:
    cmp byte [cursor_x], 0
    je .done
    dec byte [cursor_x]
    movzx bx, byte [cursor_y]
    imul bx, 80
    movzx dx, byte [cursor_x]
    add bx, dx
    shl bx, 1
    mov dx, VIDEO_MEM
    mov es, dx
    mov ax, 0x0720
    mov [es:bx], ax
    jmp .done
.done:
    call update_cursor
.finish:
    pop es
    pop ds
    popa
    ret
scroll_screen:
    pusha
    push ds
    push es
    mov ax, VIDEO_MEM
    mov ds, ax
    mov es, ax
    mov si, 160
    xor di, di
    mov cx, 80 * 24
    cld
    rep movsw
    mov ax, 0x0720
    mov cx, 80
    cld
    rep stosw
    pop es
    pop ds
    popa
    ret
update_cursor:
    pusha
    push ds
    push es
    movzx bx, byte [cursor_y]
    imul bx, 80
    movzx dx, byte [cursor_x]
    add bx, dx
    mov dx, 0x3D4
    mov al, 0x0F
    out dx, al
    inc dx
    mov al, bl
    out dx, al
    dec dx
    mov al, 0x0E
    out dx, al
    inc dx
    mov al, bh
    out dx, al
    pop es
    pop ds
    popa
    ret
print_string_direct:
    pusha
    push ds
    push es
.loop:
    lodsb
    test al, al
    jz .done
    call print_char_direct
    jmp .loop
.done:
    pop es
    pop ds
    popa
    ret
set_color:
    mov [current_color], al
    ret
