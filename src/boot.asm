[bits 16]
[org 0x7c00]
KERNEL_SEG equ 0x1000
KERNEL_OFF equ 0x0000
start:
    jmp 0:init
init:
    cli
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7c00
    sti
    mov [boot_drive], dl
    mov word [spt], 18
    mov word [hpc], 2
    mov ax, 1
    mov cx, 32
    mov bx, KERNEL_SEG
    mov es, bx
    mov bx, KERNEL_OFF
    call load_sectors
    mov dl, [boot_drive]
    jmp KERNEL_SEG:KERNEL_OFF
print_string:
    pusha
    mov ah, 0x0E
.loop:
    lodsb
    test al, al
    jz .done
    int 0x10
    jmp .loop
.done:
    popa
    ret
load_sectors:
    pusha
.loop:
    push ax
    push cx
    xor dx, dx
    div word [spt]
    inc dx
    mov cl, dl
    xor dx, dx
    div word [hpc]
    mov ch, al
    mov dh, dl
    mov dl, [boot_drive]
    mov ax, 0x0201
    int 0x13
    mov al, 'L'
    mov ah, 0x0E
    int 0x10
    pop cx
    pop ax
    add ax, 1
    add bx, 512
    loop .loop
    popa
    ret
boot_drive db 0
spt dw 0
hpc dw 0
times 510-($-$$) db 0
dw 0xAA55
