from typing import Union, BinaryIO


BLOCKSIZE = 256

def openDisk(filename: str, nBytes: int) -> Union[int, BinaryIO]:
    """
        Open or create a “disk”:
            - If nBytes > 0: create/overwrite the file to exactly nBytes (must be a multiple of BLOCKSIZE), filled with zero bytes, then reopen in "r+b" mode.
            - If nBytes == 0: just open an existing file in "r+b" mode (no resize). Returns a file object on success, or:
                -1 if invalid size
                -2 if I/O error
    """
    if nBytes < 0 or (nBytes > 0 and (nBytes % BLOCKSIZE) != 0):
        print("Error: Disk size must be non-negative and a multiple of BLOCKSIZE.")
        return -1

    try:
        if nBytes > 0:
            # Create or overwrite the file with exactly nBytes of zero bytes
            with open(filename, "wb") as file:
                file.write(b'\x00' * nBytes)

        # Just open existing file in read/write mode
        disk = open(filename, "r+b")
        return disk

    except Exception as error:
        print(f"Error opening disk '{filename}': {error}")
        return -2

def readBlock(disk: BinaryIO, bNum: int, buffer: bytearray) -> int:
    """
        Read exactly BLOCKSIZE bytes from block number bNum into the provided `buffer` (bytearray).
        Returns 0 on success, or:
            -1 on I/O exception
            -2 if we couldn’t read a full BLOCKSIZE bytes
    """
    try:
        disk.seek(bNum * BLOCKSIZE) # Move cursor to the specific byte offset
        data = disk.read(BLOCKSIZE)
        if len(data) != BLOCKSIZE:
            print(f"Error: Incomplete block read at block {bNum}.")
            return -2
        buffer[:] = data # Update original buffer passed in
        return 0

    except Exception as error:
        print(f"Error reading block {bNum}: {error}")
        return -1

def readBlockAsBytes(bNum: int, disk: BinaryIO) -> Union[int, bytearray]:
    """
        Read BLOCKSIZE bytes from block number bNum and return them as a bytearray.
        Returns bytearray of data, or:
            -1 on I/O exception
            -2 if we couldn't read a full BLOCKSIZE
    """
    try:
        disk.seek(bNum * BLOCKSIZE)
        data = disk.read(BLOCKSIZE)
        if len(data) != BLOCKSIZE:
            print(f"Error: Incomplete block read at block {bNum}.")
            return -2

        return bytearray(data)

    except Exception as error:
        print(f"Error reading block {bNum}: {error}")
        return -1

def writeBlock(disk: BinaryIO, bNum: int, buffer: bytearray) -> int:
    """
        Write exactly BLOCKSIZE bytes from `buffer` (bytes or bytearray) to block number bNum.
        Returns 0 on success, or:
            -1 on I/O exception
            -2 if buffer length ≠ BLOCKSIZE
            -3 if fewer than BLOCKSIZE bytes were written
    """
    try:
        if len(buffer) != BLOCKSIZE:
            print(f"Error: Buffer length {len(buffer)} != BLOCKSIZE.")
            return -2

        disk.seek(bNum * BLOCKSIZE)
        written = disk.write(buffer)

        # Check alignment
        if written != BLOCKSIZE:
            print(f"Error: Incomplete block write at block {bNum}.")
            return -3

        # force anything in buffer to disk
        disk.flush()
        return 0

    except Exception as error:
        print(f"Error writing block {bNum}: {error}")
        return -1

def closeDisk(disk: BinaryIO) -> int:
    """
        Close the disk (file object). Returns 0 on success, or -1 on failure.
    """
    try:
        disk.close()
        return 0
    except Exception as error:
        print(f"Error closing disk: {error}")
        return -1

