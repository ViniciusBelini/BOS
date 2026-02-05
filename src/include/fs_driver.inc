%include "src/include/fs.inc"
fs_boot_drive db 0
fs_spt dw 18
fs_hpc dw 2
init_fs:
    mov [fs_boot_drive], dl
    ret
read_sector:
    pusha
    push ds
    push es
    xor dx, dx
    div word [fs_spt]
    inc dx
    mov cl, dl
    xor dx, dx
    div word [fs_hpc]
    mov ch, al
    mov dh, dl
    mov dl, [fs_boot_drive]
    mov ax, 0x0201
    int 0x13
    pop es
    pop ds
    popa
    ret
find_file:
    push si
    push di
    mov ax, ROOT_DIR_START_SECTOR
    mov cx, ROOT_DIR_SECTOR_COUNT
    mov bx, 0x7000
    mov es, bx
    xor bx, bx
.load_root:
    call read_sector
    inc ax
    add bx, 512
    loop .load_root
    mov cx, 96
    xor bx, bx
    mov ax, 0x7000
    mov es, ax
.search_loop:
    mov di, bx
    push si
    mov dx, 11
.compare:
    lodsb
    scasb
    jne .next_entry
    dec dx
    jnz .compare
    pop si
    mov ax, [es:bx + 22]
    mov dx, [es:bx + 24]
    mov cx, [es:bx + 26]
    mov bx, dx
    jmp .done
.next_entry:
    pop si
    add bx, 32
    loop .search_loop
    xor ax, ax
.done:
    pop di
    pop si
    ret
load_file:
    call find_file
    test ax, ax
    jz .not_found
.load_loop:
    push ax
    add ax, DATA_START_SECTOR
    call read_sector
    pop ax
    push es
    push bx
    mov dx, 0x8000
    mov es, dx
    xor bx, bx
    push ax
    mov ax, FAT_START_SECTOR
    mov cx, FAT_SECTOR_COUNT
.load_fat:
    call read_sector
    inc ax
    add bx, 512
    loop .load_fat
    pop ax
    mov bx, ax
    shl bx, 1
    mov ax, [es:bx]
    pop bx
    pop es
    cmp ax, 0xFFFF
    je .done
    add bx, 512
    jmp .load_loop
.not_found:
    stc
    ret
.done:
    clc
    ret
