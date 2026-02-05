[bits 16]
[org 0x0000]

jmp start

%include "src/include/video.inc"
%include "src/include/keyboard.inc"
%include "src/include/multitasking.inc"
%include "src/include/fs_driver.inc"
%include "src/include/syscalls.inc"
%include "src/include/serial.inc"

start:
    cli
    cld
    mov ax, cs
    mov ds, ax
    mov es, ax
    ; Set kernel stack
    mov ax, 0x1000
    mov ss, ax
    mov sp, 0xFFF0
    sti
    
    mov [fs_boot_drive], dl
    
    call clear_screen_direct
    
    mov al, COLOR_YELLOW
    call set_color
    mov si, msg_kernel_start
    call print_string_direct
    
    call init_fs
    call init_syscalls
    call init_multitasking
    
    jmp kernel_task1

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
    cmp byte [last_key], 0x01 ; ESC
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
    
    mov word [es:di], 0      ; ES
    mov word [es:di+2], 0    ; DS
    mov word [es:di+4], 0    ; DI
    mov word [es:di+6], 0    ; SI
    mov word [es:di+8], 0    ; BP
    mov word [es:di+10], 0   ; SP
    mov word [es:di+12], 0   ; BX
    mov word [es:di+14], 0   ; DX
    mov word [es:di+16], 0   ; CX
    mov word [es:di+18], 0   ; AX
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
    popa
    ret

execute_command:
    pusha
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
    popa
    ret
.not_run:
    mov si, msg_unknown
    call print_string_direct
    popa
    ret
.do_help:
    mov si, msg_helptext
    call print_string_direct
    popa
    ret
.do_ls:
    call list_files
    popa
    ret
.do_cls:
    call clear_screen_direct
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
    popa
    ret

msg_newline db 13, 10, 0
