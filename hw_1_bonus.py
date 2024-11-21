#!/usr/bin/env python3
import argparse
import hashlib
import struct
import csv
import os
import time

# ANSI escape codes for colors and formatting
RESET = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
# Colors
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'

# Function to format size into GB, MB, or KB
def format_size(bytes_size):
    if bytes_size >= 1024 ** 3:  # 1 GB
        size_gb = bytes_size / (1024 ** 3)
        return f"{size_gb:.2f} GB"
    elif bytes_size >= 1024 ** 2:  # 1 MB
        size_mb = bytes_size / (1024 ** 2)
        return f"{size_mb:.2f} MB"
    else:
        size_kb = bytes_size / 1024
        return f"{size_kb:.2f} KB"

# Loads partition type mappings from the CSV file.
def load_partition_types(csv_file='PartitionTypes.csv'):
    partition_types = {}
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and len(row) >= 2:
                code = row[0].strip().lower()  # Always lowercase for consistency
                name = row[1].strip()
                try:
                    hex_value = int(code, 16)  # Convert code to integer
                    partition_types[hex_value] = name
                except ValueError:
                    print(f"Skipping invalid entry: {row}")
    return partition_types

# Calculates and saves hashes for the given file.
def calculate_hashes(file_path, verbose=False):
    if verbose:
        print(f"{BOLD}{UNDERLINE}Calculating hashes for {file_path}:{RESET}")
        file_size = os.path.getsize(file_path)
        formatted_size = format_size(file_size)
        print(f"File size: {formatted_size} ({file_size} bytes)")
    start_time = time.time()
    with open(file_path, 'rb') as f:
        data = f.read()
    save_hash(hashlib.md5(data).hexdigest(), file_path, "MD5", verbose=verbose)
    save_hash(hashlib.sha256(data).hexdigest(), file_path, "SHA-256", verbose=verbose)
    save_hash(hashlib.sha512(data).hexdigest(), file_path, "SHA-512", verbose=verbose)
    end_time = time.time()
    if verbose:
        print(f"Hash calculation completed in {end_time - start_time:.2f} seconds.\n")

# Saves the computed hash to a text file.
def save_hash(hash_value, file_path, hash_type, verbose=False):
    file_name = f"{hash_type}-{os.path.basename(file_path)}.txt"
    with open(file_name, 'w') as f:
        f.write(hash_value)
    if verbose:
        print(f"{GREEN}{hash_type} hash saved to {file_name}{RESET}")

# Detects the partition scheme (MBR or GPT).
def detect_partition_scheme(file_path, verbose=False):
    if verbose:
        print(f"{BOLD}{UNDERLINE}Detecting partition scheme for {file_path}:{RESET}")
    with open(file_path, 'rb') as f:
        mbr = f.read(512)
        if verbose:
            print(f"Read first 512 bytes (MBR): {len(mbr)} bytes")
        if mbr[510:512] != b'\x55\xAA':
            print(f"{RED}Invalid MBR signature. Cannot determine partition scheme.{RESET}")
            return None
        partition_entry = mbr[446:446+16]
        part_type = partition_entry[4]
        if verbose:
            print(f"First partition type code: 0x{part_type:02X}")
        if part_type == 0xEE:
            if verbose:
                print("Possible GPT protective MBR detected.")
            f.seek(512)
            header = f.read(8)
            if header[0:8] == b'EFI PART':
                if verbose:
                    print(f"{GREEN}GPT header signature found.{RESET}")
                return 'GPT'
            else:
                print(f"{RED}Invalid GPT header signature.{RESET}")
                return None
        else:
            if verbose:
                print(f"{GREEN}MBR partition scheme detected.{RESET}")
            return 'MBR'

# Formats a GUID to match little-endian formatting.
def format_guid(guid_bytes):
    # Split the GUID into parts
    part1 = guid_bytes[0:4][::-1]
    part2 = guid_bytes[4:6][::-1]
    part3 = guid_bytes[6:8][::-1]
    part4 = guid_bytes[8:10]
    part5 = guid_bytes[10:16]
    # Combine the parts
    guid = part1 + part2 + part3 + part4 + part5
    return guid.hex().upper()

# Reads and displays GPT partition entries from the raw disk image.
# This function was updated with assistance from ChatGPT, an AI tool developed by OpenAI.
# Reference: OpenAI. (2024). ChatGPT [Large language model]. openai.com/chatgpt
def read_gpt(file_path, verbose=False):
    sector_size = 512  # Default sector size
    if verbose:
        print(f"{BOLD}{UNDERLINE}Reading GPT from {file_path}:{RESET}")
    with open(file_path, 'rb') as f:
        f.seek(sector_size)  # GPT Header starts at LBA 1
        header = f.read(92)

    if len(header) < 92:
        print(f"{RED}GPT header is incomplete or file is too small.{RESET}")
        return

    header_fields = struct.unpack('<8sIIIIQQQQ16sQIII', header)
    signature = header_fields[0]
    if signature != b'EFI PART':
        print(f"{RED}Invalid GPT header signature.{RESET}")
        return

    partition_entry_lba = header_fields[10]
    num_partition_entries = header_fields[11]
    size_of_partition_entry = header_fields[12]

    if verbose:
        print(f"Partition entries start at LBA {partition_entry_lba}")
        print(f"Number of partition entries: {num_partition_entries}")
        print(f"Size of each partition entry: {size_of_partition_entry} bytes")

    partitions = []
    with open(file_path, 'rb') as f:
        for i in range(num_partition_entries):
            f.seek((partition_entry_lba * sector_size) + i * size_of_partition_entry)
            entry = f.read(size_of_partition_entry)
            if len(entry) < size_of_partition_entry:
                break

            partition_type_guid_bytes = entry[0:16]
            start_lba = struct.unpack('<Q', entry[32:40])[0]
            end_lba = struct.unpack('<Q', entry[40:48])[0]
            attributes = struct.unpack('<Q', entry[48:56])[0]

            # Check if the partition entry is unused (all zeros)
            if partition_type_guid_bytes == b'\x00' * 16:
                continue  # Skip unused entries

            partition_type_guid = format_guid(partition_type_guid_bytes)
            unique_partition_guid = format_guid(entry[16:32])
            name = entry[56:128].decode('utf-16le', errors='ignore').rstrip('\x00').strip()

            partition_size_sectors = end_lba - start_lba + 1
            partition_size_bytes = partition_size_sectors * sector_size
            formatted_size = format_size(partition_size_bytes)

            partitions.append({
                'number': len(partitions) + 1,
                'part_type_guid': partition_type_guid,
                'unique_guid': unique_partition_guid,
                'start_lba_hex': f"0x{start_lba:X}",
                'end_lba_hex': f"0x{end_lba:X}",
                'start_lba_dec': start_lba,
                'end_lba_dec': end_lba,
                'attributes': attributes,
                'name': name,
                'formatted_size': formatted_size
            })

            if verbose:
                print(f"\n{BOLD}Partition {len(partitions)}:{RESET}")
                print(f"  Partition Type GUID: {CYAN}{partition_type_guid}{RESET}")
                print(f"  Unique Partition GUID: {CYAN}{unique_partition_guid}{RESET}")
                print(f"  Start LBA: {start_lba} ({start_lba * sector_size} bytes)")
                print(f"  End LBA: {end_lba} ({end_lba * sector_size} bytes)")
                print(f"  Attributes Flags: 0x{attributes:X}")
                print(f"  Partition Size: {formatted_size}")
                print(f"  Partition Name: {name}")

    if partitions:
        for p in partitions:
            print(f"\nPartition number: {p['number']}")
            print(f"Partition Type GUID : {p['part_type_guid']}")
            print(f"Starting LBA in hex: {p['start_lba_hex']}")
            print(f"Ending LBA in hex: {p['end_lba_hex']}")
            print(f"Starting LBA in Decimal: {p['start_lba_dec']}")
            print(f"Ending LBA in Decimal: {p['end_lba_dec']}")
            print(f"Partition name: {p['name']}")
    else:
        print(f"{RED}No valid partitions found.{RESET}")

# Reads and displays MBR partition entries from the raw disk image.
def read_mbr(file_path, offsets, partition_types, verbose=False):
    sector_size = 512  # Default sector size
    if verbose:
        print(f"{BOLD}{UNDERLINE}Reading MBR from {file_path}:{RESET}")
        print(f"Sector size assumed: {sector_size} bytes")
    with open(file_path, 'rb') as f:
        mbr = f.read(sector_size)

    if mbr[510:512] != b'\x55\xAA':
        print(f"{RED}Invalid MBR signature.{RESET}")
        return

    partitions = []
    for i in range(4):
        entry_offset = 446 + i * 16
        entry = mbr[entry_offset: entry_offset + 16]
        if verbose:
            print(f"\n{BOLD}Partition Entry {i + 1} raw data:{RESET} {entry.hex().upper()}")
        boot_flag = entry[0]
        part_type = int(entry[4])

        # Skip if partition type is 0x00
        if part_type == 0x00:
            if verbose:
                print(f"{YELLOW}Partition {i + 1} is unused.{RESET}")
            continue  # Skip unused partition entries

        start_lba = struct.unpack('<I', entry[8:12])[0]
        size_in_sectors = struct.unpack('<I', entry[12:16])[0]
        size_in_bytes = size_in_sectors * sector_size
        formatted_size = format_size(size_in_bytes)

        type_name = partition_types.get(part_type, "Unknown")

        partitions.append({
            'number': i + 1,
            'boot_flag': boot_flag,
            'part_type': part_type,
            'type_name': type_name,
            'start_lba': start_lba,
            'size_in_sectors': size_in_sectors,
            'formatted_size': formatted_size
        })

        if verbose:
            boot_status = f"{GREEN}Bootable{RESET}" if boot_flag == 0x80 else f"{RED}Non-bootable{RESET}"
            print(f"{BOLD}Partition {i + 1}:{RESET}")
            print(f"  Boot Flag: 0x{boot_flag:02X} ({boot_status})")
            print(f"  Partition Type: 0x{part_type:02X} ({type_name})")
            print(f"  Start LBA: {start_lba} ({start_lba * sector_size} bytes)")
            print(f"  Size in sectors: {size_in_sectors}")
            print(f"  Partition Size: {formatted_size}")

    for p in partitions:
        print(f"({p['part_type']:02X}), {p['type_name']} , {p['start_lba']}, {p['size_in_sectors']}")

    if offsets:
        for i in range(min(len(offsets), len(partitions))):
            p = partitions[i]
            offset = offsets[i]
            print_partition_boot_record(file_path, p['start_lba'], offset, p['number'], verbose=verbose)

# Prints the 16-byte boot record from a given partition.
def print_partition_boot_record(file_path, start_lba, offset, partition_number, verbose=False):
    sector_size = 512
    if verbose:
        print(f"{BOLD}{UNDERLINE}Reading boot record from partition {partition_number} at offset {offset}:{RESET}")
        print(f"Start LBA: {start_lba}, Calculated byte offset: {(start_lba * sector_size) + offset}")
    with open(file_path, 'rb') as f:
        seek_position = (start_lba * sector_size) + offset
        f.seek(seek_position)
        boot_record = f.read(16)
        if len(boot_record) < 16:
            print(f"{RED}Could not read 16 bytes from offset {offset} in partition {partition_number}.{RESET}")
            return

    hex_values = ' '.join(f"{byte:02X}" for byte in boot_record)
    ascii_values = ''.join(chr(byte) if 32 <= byte <= 126 else '.' for byte in boot_record)

    print(f"\nPartition number: {partition_number}")
    print(f"16 bytes of boot record from offset {offset}: {hex_values}")
    print(f"ASCII:                                    {'  '.join(ascii_values)}")

# Main function to parse arguments and determine the partition scheme.
# This function was updated with assistance from ChatGPT, an AI tool developed by OpenAI.
# Reference: OpenAI. (2024). ChatGPT [Large language model]. openai.com/chatgpt
def main():
    parser = argparse.ArgumentParser(description="Analyze MBR and GPT of raw disk images.")
    parser.add_argument('-f', '--file', required=True, help="Path to the raw image")
    parser.add_argument('-o', '--offset', nargs='*', type=int, help="Offsets for MBR partitions")
    parser.add_argument('--verbose', action='store_true', help="Enable verbose output")

    args = parser.parse_args()
    verbose = args.verbose

    total_start_time = time.time()

    calculate_hashes(args.file, verbose=verbose)
    partition_types = load_partition_types()

    scheme = detect_partition_scheme(args.file, verbose=verbose)

    if scheme == 'MBR':
        if not args.offset:
            print("Offsets are required for MBR partitions.")
            return
        read_mbr(args.file, args.offset, partition_types, verbose=verbose)
    elif scheme == 'GPT':
        read_gpt(args.file, verbose=verbose)
    else:
        print("Unknown partitioning scheme.")

    total_end_time = time.time()
    if verbose:
        print(f"\n{BOLD}Total execution time: {total_end_time - total_start_time:.2f} seconds.{RESET}")

if __name__ == "__main__":
    main()
