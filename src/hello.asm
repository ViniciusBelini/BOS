[bits 16]
[org 0x0000]
start:
    mov ax, cs
    mov ds, ax
    mov si, msg_hello
    mov ah, 1
    int 0x30
.loop:
    mov si, msg_running
    mov ah, 1
    int 0x30
    mov cx, 0xFFFF
.delay:
    nop
    loop .delay
    jmp .loop
msg_hello db "Hello from Task 2!", 13, 10, 0
msg_running db ".", 0
