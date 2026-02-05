all: build/wundusos.img
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
