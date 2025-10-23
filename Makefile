ASM=nasm

SOURCE=src
BUILD=build

.PHONY: all image bootloader clean always run

#######################
# IMAGE
#######################
image: $(BUILD)/BOS.img

$(BUILD)/BOS.img: bootloader
	dd if=/dev/zero of=$(BUILD)/BOS.img bs=512 count=2880

	mkfs.fat -F 12 -n "MyOS FS" $(BUILD)/BOS.img
	dd if=$(BUILD)/boot.bin of=$(BUILD)/BOS.img conv=notrunc

#######################
# BOOTLOADER
#######################
bootloader: $(BUILD)/boot.bin

$(BUILD)/boot.bin: always
	$(ASM) $(SOURCE)/boot.asm -f bin -o $(BUILD)/boot.bin


#######################
# ALWAYS
#######################
always:
	mkdir -p $(BUILD)

#######################
# CLEAN
#######################
clean:
	rm -rf $(BUILD)/*
