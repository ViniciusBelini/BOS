current_task db 0
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
