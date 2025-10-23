; I DO NOT LIKE TO COMMENT IN EVERY PART OF THE CODE, BUT IN THIS PROJECT ALL DO IT
[BITS 16]
[ORG 0x7C00] ; here is where bios puts bootloader on memory

; maybe I do remember how to print using 10h int
START:
    mov si, hello_world
    mov ah, 0xE
.looooooooooooop:
    lodsb

    cmp al, 0
    je END

    int 10h

    jmp .looooooooooooop
END:
    jmp $

hello_world db "Hello, world!"

times 510-($-$$) db 0 ; fill everything with 0 - we do not use all 510 bytes of this sector
dw 0AA55h ; relax, its just boot signature!
