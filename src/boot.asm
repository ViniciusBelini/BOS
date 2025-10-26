; I DO NOT LIKE TO COMMENT IN EVERY PART OF THE CODE, BUT IN THIS PROJECT ILL DO IT
[BITS 16]
[ORG 0x7C00] ; here is where bios puts bootloader on memory

START:
    mov si, hello_world
    call PRINT
    jmp $

; PRINT ROUTINE
PRINT:
    pusha
    mov ah, 0xE
.looooooooooooop:
    lodsb

    cmp al, 0
    je .END

    int 10h

    jmp .looooooooooooop
.END:
    popa
    ret

loading_kernel db "Loading BOS Kernel..."

times 510-($-$$) db 0 ; fill everything with 0 - we do not use all 510 bytes of this sector
dw 0AA55h ; relax, its just boot signature!
