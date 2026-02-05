import os

def write_file(path, content):
    if os.path.dirname(path): os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

write_file('src/include/fs.inc', """; WundusFS Specification
SECTOR_SIZE equ 512
KERNEL_START_SECTOR equ 1
KERNEL_SECTOR_COUNT equ 32
FAT_START_SECTOR equ 33
FAT_SECTOR_COUNT  equ 12
ROOT_DIR_START_SECTOR equ 45
ROOT_DIR_SECTOR_COUNT equ 6
DATA_START_SECTOR equ 51
""")

write_file('src/boot.asm', """[bits 16]
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
""")

write_file('src/include/video.inc', """VIDEO_MEM equ 0xB800
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
    rep movsw
    mov ax, 0x0720
    mov cx, 80
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
""")

write_file('src/include/keyboard.inc', """last_key db 0
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
    db 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", '`', 0, '\\\\', 'z', 'x', 'c', 'v'
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
""")

write_file('src/include/multitasking.inc', """current_task db 0
task1_sp dw 0
task1_ss dw 0
task2_sp dw 0
task2_ss dw 0
TASK2_STACK_TOP equ 0x3000
scheduler_handler:
    pusha
    push ds
    push es
    mov ax, ss
    mov bx, sp
    cmp byte [current_task], 0
    jne .save_task2
.save_task1:
    mov [task1_ss], ax
    mov [task1_sp], bx
    mov byte [current_task], 1
    mov ax, [task2_ss]
    mov bx, [task2_sp]
    jmp .load_context
.save_task2:
    mov [task2_ss], ax
    mov [task2_sp], bx
    mov byte [current_task], 0
    mov ax, [task1_ss]
    mov bx, [task1_sp]
.load_context:
    mov ss, ax
    mov sp, bx
    mov al, 0x20
    out 0x20, al
    pop es
    pop ds
    popa
    iret
init_multitasking:
    mov ax, 0
    mov [task2_ss], ax
    mov word [task2_sp], TASK2_STACK_TOP - 26
    push es
    push ds
    mov ax, 0
    mov es, ax
    mov di, TASK2_STACK_TOP - 26
    mov word [es:di], 0
    mov word [es:di+2], 0
    mov word [es:di+4], 0
    mov word [es:di+6], 0
    mov word [es:di+8], 0
    mov word [es:di+10], 0
    mov word [es:di+12], 0
    mov word [es:di+14], 0
    mov word [es:di+16], 0
    mov word [es:di+18], 0
    mov word [es:di+20], shell_start
    mov ax, cs
    mov word [es:di+22], ax
    mov word [es:di+24], 0x0202
    pop ds
    pop es
    cli
    xor ax, ax
    mov es, ax
    mov word [es:0x08*4], scheduler_handler
    mov [es:0x08*4+2], cs
    mov word [es:0x09*4], keyboard_handler
    mov [es:0x09*4+2], cs
    sti
    ret
""")

write_file('src/include/fs_driver.inc', """%include "src/include/fs.inc"
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
""")

write_file('src/include/syscalls.inc', """syscall_handler:
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
""")

write_file('src/include/serial.inc', """serial_init:
    mov dx, 0x3FB
    mov al, 0x80
    out dx, al
    mov dx, 0x3F8
    mov al, 0x01
    out dx, al
    mov al, 0x00
    inc dx
    out dx, al
    mov dx, 0x3FB
    mov al, 0x03
    out dx, al
    ret
serial_putc:
    push dx
    push ax
    mov dx, 0x3FD
.wait:
    in al, dx
    test al, 0x20
    jz .wait
    pop ax
    mov dx, 0x3F8
    out dx, al
    pop dx
    ret
serial_print:
    push si
.loop:
    lodsb
    test al, al
    jz .done
    call serial_putc
    jmp .loop
.done:
    pop si
    ret
""")

write_file('src/kernel.asm', """[bits 16]
[org 0x0000]
%include "src/include/video.inc"
%include "src/include/keyboard.inc"
%include "src/include/multitasking.inc"
%include "src/include/fs_driver.inc"
%include "src/include/syscalls.inc"
%include "src/include/serial.inc"
start:
    call serial_init
    mov si, msg_serial_hello
    call serial_print
    mov ax, cs
    mov ds, ax
    mov es, ax
    mov ax, 0x1000
    mov ss, ax
    mov sp, 0xFFF0
    mov [fs_boot_drive], dl
    call clear_screen_direct
    mov al, COLOR_YELLOW
    call set_color
    mov si, msg_kernel_start
    call print_string_direct
    mov al, COLOR_LIGHT_GRAY
    call set_color
    call init_fs
    call init_syscalls
    ; call init_multitasking
    jmp shell_start
msg_serial_hello db "Kernel Serial Init OK", 13, 10, 0
msg_kernel_start db "WundusOS Kernel Started.", 13, 10, 0
msg_task2_killed db 13, 10, "[Kernel] Task 2 terminated by user.", 13, 10, 0
kernel_task1:
.loop:
    pusha
    mov ax, VIDEO_MEM
    mov es, ax
    mov di, (80 * 0 + 79) * 2
    inc byte [indicator]
    mov al, [indicator]
    mov ah, 0x0E
    mov [es:di], ax
    popa
    hlt
    cmp byte [last_key], 0x01
    jne .loop
    mov byte [last_key], 0
    cli
    mov si, msg_task2_killed
    call print_string_direct
    call reset_task2_context
    sti
    jmp .loop
indicator db 0
reset_task2_context:
    mov word [task2_ss], 0
    mov word [task2_sp], TASK2_STACK_TOP - 26
    push es
    push di
    xor ax, ax
    mov es, ax
    mov di, TASK2_STACK_TOP - 26
    mov word [es:di], 0
    mov word [es:di+2], 0
    mov word [es:di+4], 0
    mov word [es:di+6], 0
    mov word [es:di+8], 0
    mov word [es:di+10], 0
    mov word [es:di+12], 0
    mov word [es:di+14], 0
    mov word [es:di+16], 0
    mov word [es:di+18], 0
    mov word [es:di+20], shell_start
    mov ax, cs
    mov word [es:di+22], ax
    mov word [es:di+24], 0x0202
    pop di
    pop es
    ret
shell_start:
    mov ax, cs
    mov ds, ax
    mov es, ax
    mov si, msg_shell_welcome
    call print_string_direct
.prompt:
    mov al, COLOR_LIGHT_CYAN
    call set_color
    mov si, msg_prompt
    call print_string_direct
    mov al, COLOR_WHITE
    call set_color
    mov di, shell_buffer
    call read_line
    mov si, shell_buffer
    call execute_command
    jmp .prompt
msg_shell_welcome db "WundusOS Shell. Type 'help' for commands.", 13, 10, 0
msg_prompt db "WundusOS> ", 0
shell_buffer times 64 db 0
read_line:
    pusha
    push ds
    push es
    xor cx, cx
.loop:
    call get_key
    cmp al, 13
    je .done
    cmp al, 8
    je .backspace
    cmp cx, 63
    jge .loop
    stosb
    inc cx
    call print_char_direct
    jmp .loop
.backspace:
    test cx, cx
    jz .loop
    dec cx
    dec di
    call print_char_direct
    jmp .loop
.done:
    mov al, 0
    stosb
    mov al, 13
    call print_char_direct
    mov al, 10
    call print_char_direct
    pop es
    pop ds
    popa
    ret
execute_command:
    pusha
    push ds
    push es
    mov si, shell_buffer
    mov di, cmd_help
    call strcmp
    jc .do_help
    mov di, cmd_ls
    call strcmp
    jc .do_ls
    mov di, cmd_cls
    call strcmp
    jc .do_cls
    mov si, shell_buffer
    mov di, cmd_run
    mov cx, 4
.check_run:
    lodsb
    scasb
    jne .not_run
    loop .check_run
    call do_run
    pop es
    pop ds
    popa
    ret
.not_run:
    mov si, msg_unknown
    call print_string_direct
    pop es
    pop ds
    popa
    ret
.do_help:
    mov si, msg_helptext
    call print_string_direct
    pop es
    pop ds
    popa
    ret
.do_ls:
    call list_files
    pop es
    pop ds
    popa
    ret
.do_cls:
    call clear_screen_direct
    pop es
    pop ds
    popa
    ret
cmd_help db "help", 0
cmd_ls   db "ls", 0
cmd_cls  db "clear", 0
cmd_run  db "run ", 0
msg_unknown db "Unknown command.", 13, 10, 0
msg_helptext db "Commands: help, ls, run [file], clear", 13, 10, 0
strcmp:
    pusha
.loop:
    lodsb
    mov bl, [es:di]
    cmp al, bl
    jne .not_equal
    test al, al
    jz .equal
    inc di
    jmp .loop
.not_equal:
    popa
    clc
    ret
.equal:
    popa
    stc
    ret
do_run:
    call prepare_filename
    mov si, filename_83
    mov ax, 0x4000
    mov es, ax
    xor bx, bx
    call load_file
    jc .error
    push ds
    push es
    mov ax, 0x4000
    mov ds, ax
    mov es, ax
    call 0x4000:0000
    pop es
    pop ds
    ret
.error:
    mov si, msg_load_error
    call print_string_direct
    ret
msg_load_error db "Error: File not found or load failed.", 13, 10, 0
filename_83 times 11 db ' '
prepare_filename:
    pusha
    mov di, filename_83
    mov al, ' '
    mov cx, 11
    rep stosb
    mov di, filename_83
    xor cx, cx
.copy_base:
    lodsb
    test al, al
    jz .done
    cmp al, '.'
    je .handle_ext
    cmp cx, 8
    jge .skip_base
    stosb
    inc cx
    jmp .copy_base
.skip_base:
    jmp .copy_base
.handle_ext:
    mov di, filename_83 + 8
    xor cx, cx
.copy_ext:
    lodsb
    test al, al
    jz .done
    cmp cx, 3
    jge .done
    stosb
    inc cx
    jmp .copy_ext
.done:
    popa
    ret
list_files:
    pusha
    push ds
    push es
    mov ax, ROOT_DIR_START_SECTOR
    mov cx, ROOT_DIR_SECTOR_COUNT
    mov bx, 0x7000
    mov es, bx
    xor bx, bx
.load:
    call read_sector
    inc ax
    add bx, 512
    loop .load
    mov cx, 96
    xor bx, bx
    mov ax, 0x7000
    mov es, ax
.loop:
    cmp byte [es:bx], 0
    je .next
    cmp byte [es:bx], 0xE5
    je .next
    push cx
    mov cx, 8
    mov di, bx
.pname:
    mov al, [es:di]
    call print_char_direct
    inc di
    loop .pname
    mov al, '.'
    call print_char_direct
    mov cx, 3
.pext:
    mov al, [es:di]
    call print_char_direct
    inc di
    loop .pext
    mov si, msg_newline
    call print_string_direct
    pop cx
.next:
    add bx, 32
    loop .loop
    pop es
    pop ds
    popa
    ret
msg_newline db 13, 10, 0
""")

write_file('src/hello.asm', """[bits 16]
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
""")

write_file('tools/mkwundusfs.py', """import sys
import struct
SECTOR_SIZE = 512
DISK_SECTORS = 2880
KERNEL_START = 1
KERNEL_COUNT = 32
FAT_START = 33
FAT_COUNT = 12
ROOT_DIR_START = 45
ROOT_DIR_COUNT = 6
DATA_START = 51
def main():
    output_path, boot_path, kernel_path = sys.argv[1:4]
    other_files = sys.argv[4:]
    disk = bytearray(DISK_SECTORS * SECTOR_SIZE)
    with open(boot_path, 'rb') as f: disk[0:512] = f.read()[:512]
    with open(kernel_path, 'rb') as f: disk[KERNEL_START*512 : (KERNEL_START+KERNEL_COUNT)*512] = f.read().ljust(KERNEL_COUNT*512, b'\\\\0')
    fat_offset = FAT_START * 512
    struct.pack_into('<H', disk, fat_offset, 0xFFF8)
    struct.pack_into('<H', disk, fat_offset + 2, 0xFFFF)
    current_data_sector = DATA_START
    root_dir_offset = ROOT_DIR_START * 512
    for i, file_path in enumerate(other_files):
        with open(file_path, 'rb') as f: data = f.read()
        name = os.path.basename(file_path).upper()
        base, ext = (name.split('.') + [''])[:2]
        base, ext = base[:8].ljust(8), ext[:3].ljust(3)
        file_size = len(data)
        sectors_needed = (file_size + 511) // 512
        first_cluster = current_data_sector - DATA_START
        entry_offset = root_dir_offset + i * 32
        disk[entry_offset:entry_offset+8] = base.encode('ascii')
        disk[entry_offset+8:entry_offset+11] = ext.encode('ascii')
        struct.pack_into('<H', disk, entry_offset + 22, first_cluster)
        struct.pack_into('<I', disk, entry_offset + 24, file_size)
        disk[current_data_sector*512 : current_data_sector*512 + len(data)] = data
        for s in range(sectors_needed):
            cluster = first_cluster + s
            next_cluster = cluster + 1 if s < sectors_needed - 1 else 0xFFFF
            struct.pack_into('<H', disk, fat_offset + cluster * 2, next_cluster)
        current_data_sector += sectors_needed
    with open(output_path, 'wb') as f: f.write(disk)
import os
if __name__ == "__main__": main()
""")

write_file('Makefile', """all: build/wundusos.img
build/boot.bin: src/boot.asm
	mkdir -p build
	nasm -f bin src/boot.asm -o build/boot.bin
build/kernel.bin: src/kernel.asm src/include/*.inc
	mkdir -p build
	nasm -f bin src/kernel.asm -o build/kernel.bin
build/hello.bin: src/hello.asm
	mkdir -p build
	nasm -f bin src/hello.asm -o build/hello.bin
build/wundusos.img: build/boot.bin build/kernel.bin build/hello.bin tools/mkwundusfs.py
	python3 tools/mkwundusfs.py build/wundusos.img build/boot.bin build/kernel.bin build/hello.bin
""")
