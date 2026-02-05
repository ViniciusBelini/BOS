import sys
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
    with open(kernel_path, 'rb') as f: disk[KERNEL_START*512 : (KERNEL_START+KERNEL_COUNT)*512] = f.read().ljust(KERNEL_COUNT*512, b'\0')
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
