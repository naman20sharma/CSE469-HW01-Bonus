# CSE 469 Homework 1 Bonus: Disk Partition Analyzer with Enhanced Verbose Mode

**Name**: Naman Sharma  
**ASU ID**: 1230090591  
**Email**: nshar108@asu.edu  

---

## Overview

This project analyzes raw disk images to detect and display partition information using either the **MBR (Master Boot Record)** or **GPT (GUID Partition Table)** partitioning scheme. It also calculates and stores file hashes (**MD5**, **SHA-256**, and **SHA-512**) for verification. Additionally, the program extracts boot records for MBR partitions when offsets are provided.

An **enhanced verbose mode** has been implemented to provide detailed information about the program's execution, aiding in debugging and providing deeper insights into the analysis process.

---

## Files in the Submission

1. **hw_1_bonus.py**: Main Python script that contains all the functionality with the enhanced verbose mode.
2. **PartitionTypes.csv**: CSV file containing partition type mappings used by the program.
3. **Makefile**: Used to build the `boot_info` executable from `hw_1_bonus.py`.
4. **packages**: Lists dependencies required for the program to run.
5. **README.md**: This file, providing an overview and usage instructions for the assignment.

---

## Dependencies

This program requires **Python 3** and uses the following standard libraries:

- `argparse`: For parsing command-line arguments.
- `hashlib`: For calculating MD5, SHA-256, and SHA-512 hashes.
- `struct`: For unpacking binary data from raw disk images.
- `csv`: For reading the partition types from the CSV file.
- `os`: For interacting with the operating system (e.g., reading file size).
- `time`: For measuring execution time.

Since these libraries are part of the Python Standard Library, they do not need to be installed separately. However, the following must be available in the test environment:

**packages File Contents**:

```
python3
python3-pip
```

This ensures that Python 3 and Pip are installed on the system.

---

## How to Build and Run the Program

### 1. Build the Project

To compile the project and create the executable `boot_info`:

```bash
make
```

### 2. Run the Program for MBR Analysis

To analyze an MBR partition and extract the boot record:

```bash
./boot_info -f mbr_sample.raw -o 123 76 258 55
```

**Explanation**:

- `-f`: Specifies the input raw disk image (`mbr_sample.raw` in this case).
- `-o`: Specifies the offsets to extract boot records from the partitions.

### 3. Run the Program for GPT Analysis

To analyze a GPT partition:

```bash
./boot_info -f gpt_sample.raw
```

---

## Enhanced Verbose Mode

### Overview

An enhanced **verbose mode** has been implemented, activated using the `--verbose` flag. This mode provides detailed information about the program's execution, which can be invaluable for debugging and understanding the internal workings of the program.

### How to Use the Verbose Mode

To enable verbose output, include the `--verbose` flag when running the program:

#### MBR Analysis with Verbose Mode

```bash
./boot_info -f mbr_sample.raw -o 123 76 258 55 --verbose
```

#### GPT Analysis with Verbose Mode

```bash
./boot_info -f gpt_sample.raw --verbose
```

### Features of the Verbose Mode

#### 1. Detailed Execution Information

- **Section Headers**: Clear and bold headers are displayed for each major section of the program (e.g., hash calculations, partition scheme detection), making it easy to follow the program's flow.
- **Execution Timing**: The time taken for hash calculations and the total execution time of the program are displayed, helping identify performance bottlenecks.
- **File Size Information**: The size of the input file is shown in bytes and formatted into GB, MB, or KB as appropriate, providing immediate context about the file being analyzed.

#### 2. Dynamic Size Formatting

- **Adaptive Units**: Sizes are displayed in the most appropriate units based on their magnitude:
  - If size ≥ 1 GB, displayed in GB.
  - Else if size ≥ 1 MB, displayed in MB.
  - Else, displayed in KB.
- This makes the output more readable and easier to interpret at a glance.

#### 3. Partition Details

- **MBR Partitions**:
  - **Raw Partition Entry Data**: Displayed in hexadecimal for in-depth analysis.
  - **Boot Flag Status**: Indicated as bootable or non-bootable, providing critical information for boot sequence analysis.
  - **Partition Size**: Shown in appropriate units (GB, MB, or KB).
  - **Start LBA and Calculated Byte Offsets**: Provided for precise location mapping within the disk image.
- **GPT Partitions**:
  - **Partition Type GUID and Unique Partition GUID**: Displayed for identification of partition types and unique identifiers.
  - **Attributes Flags**: Shown for understanding partition properties and permissions.
  - **Partition Size**: Provided in appropriate units.
  - **Start and End LBAs with Calculated Byte Offsets**: Included for detailed mapping.

#### 4. Color-Coded Output

- **Section Headers**: Displayed in bold and underlined text to distinguish different parts of the output.
- **Success Messages**: Shown in green to indicate successful operations.
- **Warnings and Errors**: Displayed in red for clear visibility and immediate attention.
- **Status Indicators**:
  - **"Bootable"** status in green.
  - **"Non-bootable"** status in red.
  - **Unused Partitions**: Displayed in yellow to highlight their presence.
- **Data Values**:
  - **Partition GUIDs**: Displayed in cyan for emphasis and easy identification.

---

## Output

The script performs the following actions:

- **Detects the partitioning scheme** (MBR or GPT).
- **Calculates MD5, SHA-256, and SHA-512 hashes** of the input file and stores them in text files.
- **For MBR**:
  - Extracts partition information and displays partition type, start LBA, and size.
  - Provides detailed partition entry data and boot record extraction when offsets are provided.
- **For GPT**:
  - Extracts partition entries and displays partition type GUIDs, starting and ending LBAs, and partition names.
  - Provides detailed partition information, including attributes and size formatting.

---

## CSV File

The script uses a CSV file named **"PartitionTypes.csv"** to map partition type codes to their respective names. Ensure that the CSV file is in the same directory as the Python script.

---

## Warnings and Notes

- **Valid Offsets Required**: Ensure that valid offsets are provided for MBR partitions. If no offsets are given, boot record extraction will be skipped.
- **MBR Signature Check**: If the MBR signature (`0x55AA`) is not found, the program will print an error message and exit.
- **GPT Header Validation**: For GPT analysis, the program expects a valid GPT header. If the header is missing or incomplete, it will report an error.
- **Verbose Output Volume**: The verbose mode provides detailed output that can significantly increase the amount of information displayed. Use it when detailed analysis is required.
- **Terminal Compatibility**: The color-coded output in verbose mode uses ANSI escape codes, which are widely supported in Unix-based terminals. Ensure your terminal emulator supports ANSI codes to see the color formatting.

---

## How to Clean the Project

To remove the `boot_info` executable:

```bash
make clean
```

---

## Disclaimer

This script is intended for forensic analysis purposes and should only be used in compliance with applicable laws and ethical guidelines. The developer assumes no responsibility for misuse of the software.

---

## License

This script is provided under an open-source license. You are free to use, modify, and distribute it, provided that proper attribution is given to the original author.

---

## Author

This script was developed by **Naman Sharma**, as part of coursework for **Arizona State University**.

---

## Generative AI Acknowledgment

Portions of the code in this project were generated and updated with assistance from **ChatGPT**, an AI tool developed by **OpenAI**.

Reference: OpenAI. (2024). ChatGPT [Large language model]. [openai.com/chatgpt](https://openai.com/chatgpt)

---

If you have any questions or need further assistance, please feel free to contact me at **nshar108@asu.edu**.

---

*This README file provides an overview of the Disk Partition Analyzer project, including detailed information about the enhanced verbose mode and how it aids in debugging and forensic analysis.*

---

**Note**: The filenames and commands have been updated to reflect the correct usage:

- **Script Filename**: `hw_1_bonus.py` instead of `hw_1.py`.
- **Sample Disk Images**: `mbr_sample.raw` and `gpt_sample.raw` instead of `sample.raw`.
- **Makefile**: Updated to build from `hw_1_bonus.py`.

Please ensure that you replace any instances of `sample.raw` with `mbr_sample.raw` or `gpt_sample.raw` as appropriate when running the program.

